"""
Enterprise Insights Copilot - Error Handling Middleware
MAANG-level error handling with proper HTTP status codes and security
"""

import traceback
from typing import Callable, Dict, Any, Optional
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError
import asyncio

from app.core.config import settings
from app.core.logging import get_logger, log_security_event, get_request_id
from app.middleware.request_id import get_request_context

logger = get_logger(__name__)


class CustomHTTPException(HTTPException):
    """Custom HTTP exception with additional context"""
    
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
        error_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code, detail, headers)
        self.error_code = error_code
        self.error_type = error_type
        self.context = context or {}


class ErrorResponse:
    """Standardized error response structure"""
    
    def __init__(
        self,
        status_code: int,
        error_code: str,
        error_type: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        timestamp: Optional[str] = None
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.error_type = error_type
        self.message = message
        self.details = details or {}
        self.request_id = request_id
        self.timestamp = timestamp
    
    def to_dict(self, include_debug: bool = False) -> Dict[str, Any]:
        """Convert to dictionary for JSON response"""
        
        response = {
            "error": {
                "code": self.error_code,
                "type": self.error_type,
                "message": self.message,
            },
            "request_id": self.request_id,
            "timestamp": self.timestamp
        }
        
        if self.details:
            response["error"]["details"] = self.details
        
        if include_debug and not settings.is_production:
            response["debug"] = self.details.get("debug", {})
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Comprehensive error handling middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        self.error_handlers = {
            ValidationError: self._handle_validation_error,
            RequestValidationError: self._handle_request_validation_error,
            HTTPException: self._handle_http_exception,
            CustomHTTPException: self._handle_custom_http_exception,
            asyncio.TimeoutError: self._handle_timeout_error,
            ConnectionError: self._handle_connection_error,
            PermissionError: self._handle_permission_error,
            ValueError: self._handle_value_error,
            TypeError: self._handle_type_error,
            KeyError: self._handle_key_error,
            FileNotFoundError: self._handle_file_not_found_error,
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with error handling"""
        
        try:
            response = await call_next(request)
            return response
            
        except Exception as e:
            return await self._handle_exception(request, e)
    
    async def _handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle any exception and return appropriate response"""
        
        # Get request context
        context = get_request_context(request)
        request_id = context.get("request_id")
        
        # Find appropriate handler
        handler = None
        for exc_type, exc_handler in self.error_handlers.items():
            if isinstance(exc, exc_type):
                handler = exc_handler
                break
        
        # Use default handler if no specific handler found
        if handler is None:
            handler = self._handle_generic_error
        
        # Handle the exception
        error_response = await handler(request, exc)
        
        # Log the error
        self._log_error(request, exc, error_response, context)
        
        # Log security events for suspicious errors
        await self._check_security_events(request, exc, context)
        
        return JSONResponse(
            status_code=error_response.status_code,
            content=error_response.to_dict(include_debug=settings.is_development)
        )
    
    async def _handle_validation_error(self, request: Request, exc: ValidationError) -> ErrorResponse:
        """Handle Pydantic validation errors"""
        
        return ErrorResponse(
            status_code=422,
            error_code="VALIDATION_ERROR",
            error_type="validation",
            message="Request validation failed",
            details={
                "validation_errors": exc.errors(),
                "invalid_fields": [error["loc"] for error in exc.errors()]
            },
            request_id=get_request_id(),
            timestamp=self._get_timestamp()
        )
    
    async def _handle_request_validation_error(self, request: Request, exc: RequestValidationError) -> ErrorResponse:
        """Handle FastAPI request validation errors"""
        
        return ErrorResponse(
            status_code=422,
            error_code="REQUEST_VALIDATION_ERROR",
            error_type="validation",
            message="Request validation failed",
            details={
                "validation_errors": exc.errors(),
                "body": exc.body if hasattr(exc, 'body') else None
            },
            request_id=get_request_id(),
            timestamp=self._get_timestamp()
        )
    
    async def _handle_http_exception(self, request: Request, exc: HTTPException) -> ErrorResponse:
        """Handle standard HTTP exceptions"""
        
        error_codes = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            409: "CONFLICT",
            429: "TOO_MANY_REQUESTS",
            500: "INTERNAL_SERVER_ERROR",
            502: "BAD_GATEWAY",
            503: "SERVICE_UNAVAILABLE",
            504: "GATEWAY_TIMEOUT"
        }
        
        return ErrorResponse(
            status_code=exc.status_code,
            error_code=error_codes.get(exc.status_code, "HTTP_ERROR"),
            error_type="http",
            message=str(exc.detail),
            details={"headers": exc.headers} if exc.headers else None,
            request_id=get_request_id(),
            timestamp=self._get_timestamp()
        )
    
    async def _handle_custom_http_exception(self, request: Request, exc: CustomHTTPException) -> ErrorResponse:
        """Handle custom HTTP exceptions"""
        
        return ErrorResponse(
            status_code=exc.status_code,
            error_code=exc.error_code or "CUSTOM_ERROR",
            error_type=exc.error_type or "application",
            message=str(exc.detail),
            details=exc.context,
            request_id=get_request_id(),
            timestamp=self._get_timestamp()
        )
    
    async def _handle_timeout_error(self, request: Request, exc: asyncio.TimeoutError) -> ErrorResponse:
        """Handle timeout errors"""
        
        return ErrorResponse(
            status_code=504,
            error_code="TIMEOUT_ERROR",
            error_type="timeout",
            message="Request timed out",
            details={"timeout_type": "asyncio_timeout"},
            request_id=get_request_id(),
            timestamp=self._get_timestamp()
        )
    
    async def _handle_connection_error(self, request: Request, exc: ConnectionError) -> ErrorResponse:
        """Handle connection errors"""
        
        return ErrorResponse(
            status_code=503,
            error_code="CONNECTION_ERROR",
            error_type="connection",
            message="Service temporarily unavailable",
            details={"connection_error": str(exc) if settings.is_development else None},
            request_id=get_request_id(),
            timestamp=self._get_timestamp()
        )
    
    async def _handle_permission_error(self, request: Request, exc: PermissionError) -> ErrorResponse:
        """Handle permission errors"""
        
        return ErrorResponse(
            status_code=403,
            error_code="PERMISSION_ERROR",
            error_type="permission",
            message="Insufficient permissions",
            details={"permission_error": str(exc) if settings.is_development else None},
            request_id=get_request_id(),
            timestamp=self._get_timestamp()
        )
    
    async def _handle_value_error(self, request: Request, exc: ValueError) -> ErrorResponse:
        """Handle value errors"""
        
        return ErrorResponse(
            status_code=400,
            error_code="VALUE_ERROR",
            error_type="validation",
            message="Invalid value provided",
            details={"value_error": str(exc) if settings.is_development else None},
            request_id=get_request_id(),
            timestamp=self._get_timestamp()
        )
    
    async def _handle_type_error(self, request: Request, exc: TypeError) -> ErrorResponse:
        """Handle type errors"""
        
        return ErrorResponse(
            status_code=400,
            error_code="TYPE_ERROR",
            error_type="validation",
            message="Invalid data type provided",
            details={"type_error": str(exc) if settings.is_development else None},
            request_id=get_request_id(),
            timestamp=self._get_timestamp()
        )
    
    async def _handle_key_error(self, request: Request, exc: KeyError) -> ErrorResponse:
        """Handle key errors"""
        
        return ErrorResponse(
            status_code=400,
            error_code="KEY_ERROR",
            error_type="validation",
            message="Required field missing",
            details={"missing_key": str(exc) if settings.is_development else None},
            request_id=get_request_id(),
            timestamp=self._get_timestamp()
        )
    
    async def _handle_file_not_found_error(self, request: Request, exc: FileNotFoundError) -> ErrorResponse:
        """Handle file not found errors"""
        
        return ErrorResponse(
            status_code=404,
            error_code="FILE_NOT_FOUND",
            error_type="resource",
            message="Requested file not found",
            details={"file_error": str(exc) if settings.is_development else None},
            request_id=get_request_id(),
            timestamp=self._get_timestamp()
        )
    
    async def _handle_generic_error(self, request: Request, exc: Exception) -> ErrorResponse:
        """Handle generic/unknown errors"""
        
        # Log the full exception for debugging
        logger.error(
            "Unhandled exception",
            exception_type=type(exc).__name__,
            exception_message=str(exc),
            traceback=traceback.format_exc() if settings.is_development else None,
            exc_info=True
        )
        
        return ErrorResponse(
            status_code=500,
            error_code="INTERNAL_ERROR",
            error_type="server",
            message="An internal server error occurred",
            details={
                "exception_type": type(exc).__name__,
                "traceback": traceback.format_exc() if settings.is_development else None
            },
            request_id=get_request_id(),
            timestamp=self._get_timestamp()
        )
    
    def _log_error(
        self, 
        request: Request, 
        exc: Exception, 
        error_response: ErrorResponse,
        context: Dict[str, Any]
    ):
        """Log error with full context"""
        
        log_data = {
            "error_code": error_response.error_code,
            "error_type": error_response.error_type,
            "status_code": error_response.status_code,
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params) if request.query_params else None,
            "user_agent": request.headers.get("user-agent"),
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            **context
        }
        
        # Use appropriate log level based on status code
        if error_response.status_code >= 500:
            logger.error("Server error occurred", **log_data, exc_info=True)
        elif error_response.status_code >= 400:
            logger.warning("Client error occurred", **log_data)
        else:
            logger.info("Error handled", **log_data)
    
    async def _check_security_events(
        self, 
        request: Request, 
        exc: Exception, 
        context: Dict[str, Any]
    ):
        """Check for security-related events"""
        
        # Log suspicious 403/401 errors
        if isinstance(exc, HTTPException) and exc.status_code in [401, 403]:
            log_security_event(
                "authentication_failure",
                severity="warning",
                path=request.url.path,
                method=request.method,
                user_agent=request.headers.get("user-agent"),
                **context
            )
        
        # Log potential brute force attempts
        if isinstance(exc, HTTPException) and exc.status_code == 429:
            log_security_event(
                "rate_limit_exceeded",
                severity="warning",
                path=request.url.path,
                method=request.method,
                **context
            )
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"


def setup_error_handling(app):
    """Set up error handling middleware"""
    
    app.add_middleware(ErrorHandlingMiddleware)
    
    logger.info("Error handling middleware configured")
