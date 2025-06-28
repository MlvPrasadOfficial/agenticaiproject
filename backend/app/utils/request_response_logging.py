"""
Request/Response logging middleware for Enterprise Insights Copilot
Provides comprehensive logging of HTTP requests and responses for debugging and monitoring.
"""

import time
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
from contextlib import asynccontextmanager

from fastapi import Request, Response
from fastapi.responses import StreamingResponse
import starlette.status as status

from app.utils.logging import get_logger
from app.utils.metrics import metrics
from app.utils.tracing import get_tracer


class RequestResponseLogger:
    """Request and response logging system."""
    
    def __init__(self):
        self.logger = get_logger()
        self.tracer = get_tracer()
        self.excluded_paths = {"/health", "/metrics", "/docs", "/redoc", "/openapi.json"}
        self.log_request_body = True
        self.log_response_body = True
        self.max_body_size = 10000  # Max body size to log (bytes)
        self.request_logs: List[Dict[str, Any]] = []
        self.max_log_history = 1000
    
    async def log_request_response(self, request: Request, call_next):
        """Main middleware function for logging requests and responses."""
        # Generate request ID for tracking
        request_id = str(uuid.uuid4())
        
        # Skip logging for excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)
        
        # Start timing
        start_time = time.time()
        
        # Log request
        request_data = await self._log_request(request, request_id)
        
        # Set request context
        self.logger.set_context(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            user_agent=request.headers.get("user-agent", "unknown")
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Log response
            response_data = await self._log_response(response, request_id, response_time, request_data)
            
            # Record metrics
            metrics.record_http_request(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                duration=response_time
            )
            
            # Log combined request/response data
            self._log_request_response_summary(request_data, response_data)
            
            return response
            
        except Exception as e:
            # Calculate error response time
            response_time = time.time() - start_time
            
            # Log error
            error_data = self._log_error_response(request_id, e, response_time)
            
            # Record error metrics
            metrics.record_error(e.__class__.__name__, "http_request")
            
            # Log error summary
            self._log_error_summary(request_data, error_data)
            
            # Re-raise exception
            raise
        
        finally:
            # Clear request context
            self.logger.clear_context()
    
    async def _log_request(self, request: Request, request_id: str) -> Dict[str, Any]:
        """Log incoming request details."""
        # Extract request body if needed
        body_content = None
        if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                if len(body_bytes) <= self.max_body_size:
                    body_content = body_bytes.decode('utf-8')
                else:
                    body_content = f"<Body too large: {len(body_bytes)} bytes>"
            except Exception as e:
                body_content = f"<Failed to read body: {str(e)}>"
        
        # Parse query parameters
        query_params = dict(request.query_params)
        
        # Extract headers (excluding sensitive ones)
        headers = {
            key: value for key, value in request.headers.items()
            if not any(sensitive in key.lower() for sensitive in ['authorization', 'cookie', 'token', 'key'])
        }
        
        request_data = {
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": query_params,
            "headers": headers,
            "body": body_content,
            "client_ip": self._get_client_ip(request),
            "user_agent": headers.get("user-agent", "unknown"),
            "content_type": headers.get("content-type"),
            "content_length": headers.get("content-length")
        }
        
        # Log request
        self.logger.info(
            f"HTTP Request: {request.method} {request.url.path}",
            **request_data,
            log_type="http_request"
        )
        
        return request_data
    
    async def _log_response(self, response: Response, request_id: str, response_time: float, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log outgoing response details."""
        # Extract response headers
        response_headers = dict(response.headers)
        
        # Try to get response body for logging
        response_body = None
        if self.log_response_body and hasattr(response, 'body'):
            try:
                if isinstance(response, StreamingResponse):
                    response_body = "<Streaming Response>"
                else:
                    body = getattr(response, 'body', None)
                    if body and len(body) <= self.max_body_size:
                        response_body = body.decode('utf-8') if isinstance(body, bytes) else str(body)
                    elif body:
                        response_body = f"<Response body too large: {len(body)} bytes>"
            except Exception:
                response_body = "<Failed to read response body>"
        
        response_data = {
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status_code": response.status_code,
            "status_text": self._get_status_text(response.status_code),
            "headers": response_headers,
            "body": response_body,
            "response_time_ms": round(response_time * 1000, 2),
            "content_type": response_headers.get("content-type"),
            "content_length": response_headers.get("content-length")
        }
        
        # Determine log level based on status code
        if response.status_code >= 500:
            log_level = "error"
        elif response.status_code >= 400:
            log_level = "warning"
        else:
            log_level = "info"
        
        # Log response
        log_message = f"HTTP Response: {response.status_code} for {request_data['method']} {request_data['path']}"
        
        if log_level == "error":
            self.logger.error(log_message, **response_data, log_type="http_response")
        elif log_level == "warning":
            self.logger.warning(log_message, **response_data, log_type="http_response")
        else:
            self.logger.info(log_message, **response_data, log_type="http_response")
        
        return response_data
    
    def _log_error_response(self, request_id: str, error: Exception, response_time: float) -> Dict[str, Any]:
        """Log error response details."""
        error_data = {
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": error.__class__.__name__,
            "error_message": str(error),
            "response_time_ms": round(response_time * 1000, 2),
            "status_code": 500
        }
        
        self.logger.error(
            f"HTTP Request Error: {error.__class__.__name__}",
            error=error,
            **error_data,
            log_type="http_error"
        )
        
        return error_data
    
    def _log_request_response_summary(self, request_data: Dict[str, Any], response_data: Dict[str, Any]):
        """Log combined request/response summary."""
        summary = {
            "request_id": request_data["request_id"],
            "method": request_data["method"],
            "path": request_data["path"],
            "status_code": response_data["status_code"],
            "response_time_ms": response_data["response_time_ms"],
            "client_ip": request_data["client_ip"],
            "user_agent": request_data["user_agent"],
            "timestamp": response_data["timestamp"]
        }
        
        # Store in memory for quick access
        self.request_logs.append(summary)
        if len(self.request_logs) > self.max_log_history:
            self.request_logs = self.request_logs[-self.max_log_history:]
        
        # Log summary
        self.logger.info(
            f"Request completed: {summary['method']} {summary['path']} -> {summary['status_code']} ({summary['response_time_ms']}ms)",
            **summary,
            log_type="http_summary"
        )
    
    def _log_error_summary(self, request_data: Dict[str, Any], error_data: Dict[str, Any]):
        """Log error summary."""
        summary = {
            "request_id": request_data["request_id"],
            "method": request_data["method"],
            "path": request_data["path"],
            "error_type": error_data["error_type"],
            "error_message": error_data["error_message"],
            "response_time_ms": error_data["response_time_ms"],
            "client_ip": request_data["client_ip"],
            "timestamp": error_data["timestamp"]
        }
        
        # Store error in memory
        self.request_logs.append(summary)
        if len(self.request_logs) > self.max_log_history:
            self.request_logs = self.request_logs[-self.max_log_history:]
        
        # Log error summary
        self.logger.error(
            f"Request failed: {summary['method']} {summary['path']} -> {summary['error_type']}",
            **summary,
            log_type="http_error_summary"
        )
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        return getattr(request.client, "host", "unknown") if request.client else "unknown"
    
    def _get_status_text(self, status_code: int) -> str:
        """Get status text for HTTP status code."""
        status_texts = {
            200: "OK",
            201: "Created",
            202: "Accepted",
            204: "No Content",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            422: "Unprocessable Entity",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable",
            504: "Gateway Timeout"
        }
        return status_texts.get(status_code, "Unknown")
    
    def get_recent_requests(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent request logs."""
        return self.request_logs[-limit:]
    
    def get_request_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get request statistics for the specified time period."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_requests = [
            req for req in self.request_logs
            if datetime.fromisoformat(req["timestamp"].replace('Z', '+00:00')) > cutoff_time
        ]
        
        if not recent_requests:
            return {"message": "No request data available"}
        
        # Calculate statistics
        status_codes = {}
        methods = {}
        paths = {}
        response_times = []
        
        for req in recent_requests:
            # Status codes
            status = req.get("status_code", "unknown")
            status_codes[status] = status_codes.get(status, 0) + 1
            
            # Methods
            method = req.get("method", "unknown")
            methods[method] = methods.get(method, 0) + 1
            
            # Paths
            path = req.get("path", "unknown")
            paths[path] = paths.get(path, 0) + 1
            
            # Response times
            if "response_time_ms" in req:
                response_times.append(req["response_time_ms"])
        
        # Calculate response time statistics
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        
        return {
            "total_requests": len(recent_requests),
            "time_period_hours": hours,
            "status_codes": status_codes,
            "methods": methods,
            "top_paths": dict(sorted(paths.items(), key=lambda x: x[1], reverse=True)[:10]),
            "response_time_stats": {
                "average_ms": round(avg_response_time, 2),
                "max_ms": max_response_time,
                "min_ms": min_response_time
            },
            "error_rate": (status_codes.get(500, 0) + status_codes.get(400, 0)) / len(recent_requests) * 100,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def configure_logging(self, 
                         log_request_body: bool = True,
                         log_response_body: bool = True,
                         max_body_size: int = 10000,
                         excluded_paths: Optional[List[str]] = None):
        """Configure logging behavior."""
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.max_body_size = max_body_size
        
        if excluded_paths:
            self.excluded_paths.update(excluded_paths)
        
        self.logger.info(
            "Request/Response logging configured",
            log_request_body=log_request_body,
            log_response_body=log_response_body,
            max_body_size=max_body_size,
            excluded_paths=list(self.excluded_paths)
        )


# Global request/response logger instance
request_response_logger = RequestResponseLogger()


def get_request_response_logger() -> RequestResponseLogger:
    """Get the global request/response logger instance."""
    return request_response_logger


async def request_response_middleware(request: Request, call_next):
    """FastAPI middleware for request/response logging."""
    return await request_response_logger.log_request_response(request, call_next)


@asynccontextmanager
async def request_context(request_id: Optional[str] = None):
    """Context manager for request-scoped logging."""
    if not request_id:
        request_id = str(uuid.uuid4())
    
    logger = get_logger()
    
    # Set request context
    logger.set_context(request_id=request_id)
    
    try:
        yield request_id
    finally:
        # Clear request context
        logger.clear_context()


# Convenience function for manual request logging
async def log_external_request(method: str, url: str, status_code: int, response_time: float, **kwargs):
    """Log external API requests manually."""
    logger = get_logger()
    
    log_data = {
        "method": method,
        "url": url,
        "status_code": status_code,
        "response_time_ms": round(response_time * 1000, 2),
        "log_type": "external_request",
        **kwargs
    }
    
    if status_code >= 400:
        logger.warning(f"External request failed: {method} {url} -> {status_code}", **log_data)
    else:
        logger.info(f"External request: {method} {url} -> {status_code}", **log_data)
