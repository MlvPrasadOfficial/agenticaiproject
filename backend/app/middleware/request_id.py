"""
Enterprise Insights Copilot - Request ID Middleware
MAANG-level distributed tracing and correlation ID management
"""

import uuid
import time
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import (
    get_logger,
    set_request_id,
    set_user_id,
    get_request_id,
    log_performance
)

logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request IDs and correlation tracking"""
    
    def __init__(
        self,
        app,
        header_name: str = "X-Request-ID",
        correlation_header: str = "X-Correlation-ID",
        user_header: str = "X-User-ID",
        generate_if_missing: bool = True,
    ):
        super().__init__(app)
        self.header_name = header_name
        self.correlation_header = correlation_header
        self.user_header = user_header
        self.generate_if_missing = generate_if_missing
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with ID tracking"""
        
        start_time = time.time()
        
        # Get or generate request ID
        request_id = request.headers.get(self.header_name)
        if not request_id and self.generate_if_missing:
            request_id = str(uuid.uuid4())
        
        # Get correlation ID (for distributed tracing)
        correlation_id = request.headers.get(self.correlation_header)
        if not correlation_id:
            correlation_id = request_id
        
        # Get user ID if available
        user_id = request.headers.get(self.user_header)
        
        # Set context variables for logging
        if request_id:
            set_request_id(request_id)
        if user_id:
            set_user_id(user_id)
        
        # Add IDs to request state for access in route handlers
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id
        request.state.user_id = user_id
        request.state.start_time = start_time
        
        # Log request start
        logger.info(
            "Request started",
            method=request.method,
            url=str(request.url),
            path=request.url.path,
            query_params=str(request.query_params) if request.query_params else None,
            user_agent=request.headers.get("user-agent"),
            client_ip=self._get_client_ip(request),
            request_id=request_id,
            correlation_id=correlation_id,
            user_id=user_id
        )
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate request duration
            duration = time.time() - start_time
            
            # Add headers to response
            if request_id:
                response.headers[self.header_name] = request_id
            if correlation_id:
                response.headers[self.correlation_header] = correlation_id
            
            # Log request completion
            logger.info(
                "Request completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
                request_id=request_id,
                correlation_id=correlation_id,
                user_id=user_id
            )
            
            # Log performance metrics
            log_performance(
                func_name=f"{request.method} {request.url.path}",
                duration=duration,
                status_code=response.status_code,
                request_id=request_id
            )
            
            return response
            
        except Exception as e:
            # Calculate request duration for failed requests
            duration = time.time() - start_time
            
            # Log request error
            logger.error(
                "Request failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
                duration_ms=round(duration * 1000, 2),
                request_id=request_id,
                correlation_id=correlation_id,
                user_id=user_id,
                exc_info=True
            )
            
            # Re-raise the exception
            raise
    
    def _get_client_ip(self, request: Request) -> Optional[str]:
        """Extract client IP address from request"""
        
        # Check for forwarded headers (load balancers, proxies)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        if hasattr(request.client, "host"):
            return request.client.host
        
        return None


class DistributedTracingMiddleware(BaseHTTPMiddleware):
    """Enhanced middleware for distributed tracing with OpenTelemetry integration"""
    
    def __init__(self, app, service_name: str = "enterprise-insights-api"):
        super().__init__(app)
        self.service_name = service_name
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with distributed tracing"""
        
        # Get trace context from headers
        trace_id = request.headers.get("x-trace-id")
        span_id = request.headers.get("x-span-id")
        parent_span_id = request.headers.get("x-parent-span-id")
        
        # Generate trace ID if not present
        if not trace_id:
            trace_id = str(uuid.uuid4().hex)
        
        # Generate span ID
        if not span_id:
            span_id = str(uuid.uuid4().hex[:16])
        
        # Add trace context to request state
        request.state.trace_id = trace_id
        request.state.span_id = span_id
        request.state.parent_span_id = parent_span_id
        
        # Create span context for logging
        span_context = {
            "trace_id": trace_id,
            "span_id": span_id,
            "parent_span_id": parent_span_id,
            "service": self.service_name,
            "operation": f"{request.method} {request.url.path}"
        }
        
        start_time = time.time()
        
        try:
            # Process the request
            response = await call_next(request)
            
            duration = time.time() - start_time
            
            # Add trace headers to response
            response.headers["x-trace-id"] = trace_id
            response.headers["x-span-id"] = span_id
            
            # Log span completion
            logger.info(
                "Span completed",
                **span_context,
                duration_ms=round(duration * 1000, 2),
                status_code=response.status_code,
                success=True
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Log span error
            logger.error(
                "Span failed",
                **span_context,
                duration_ms=round(duration * 1000, 2),
                error=str(e),
                success=False,
                exc_info=True
            )
            
            raise


def get_request_context(request: Request) -> dict:
    """Get request context information"""
    return {
        "request_id": getattr(request.state, "request_id", None),
        "correlation_id": getattr(request.state, "correlation_id", None),
        "user_id": getattr(request.state, "user_id", None),
        "trace_id": getattr(request.state, "trace_id", None),
        "span_id": getattr(request.state, "span_id", None),
    }


def setup_request_middleware(app):
    """Set up request ID and tracing middleware"""
    
    # Add distributed tracing middleware
    app.add_middleware(
        DistributedTracingMiddleware,
        service_name="enterprise-insights-copilot"
    )
    
    # Add request ID middleware
    app.add_middleware(
        RequestIDMiddleware,
        header_name="X-Request-ID",
        correlation_header="X-Correlation-ID",
        user_header="X-User-ID",
        generate_if_missing=True
    )
    
    logger.info("Request tracking middleware configured")
