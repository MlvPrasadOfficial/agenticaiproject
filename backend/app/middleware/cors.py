"""
Enterprise Insights Copilot - CORS Middleware
MAANG-level CORS configuration with security best practices
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Union
import re
from urllib.parse import urlparse

from app.core.config import settings
from app.core.logging import get_logger, log_security_event
from app.core.environment import env_config

logger = get_logger(__name__)


class SecurityCORSMiddleware:
    """Enhanced CORS middleware with security features"""
    
    def __init__(
        self,
        app: FastAPI,
        allow_origins: List[str] = None,
        allow_origin_regex: str = None,
        allow_methods: List[str] = None,
        allow_headers: List[str] = None,
        allow_credentials: bool = False,
        expose_headers: List[str] = None,
        max_age: int = 600,
    ):
        self.app = app
        self.allow_origins = allow_origins or []
        self.allow_origin_regex = allow_origin_regex
        self.allow_methods = allow_methods or ["GET"]
        self.allow_headers = allow_headers or []
        self.allow_credentials = allow_credentials
        self.expose_headers = expose_headers or []
        self.max_age = max_age
        
        # Compile regex pattern if provided
        self.origin_regex = None
        if allow_origin_regex:
            self.origin_regex = re.compile(allow_origin_regex)
    
    def is_allowed_origin(self, origin: str) -> bool:
        """Check if origin is allowed"""
        
        # Check exact matches
        if origin in self.allow_origins:
            return True
        
        # Check wildcard
        if "*" in self.allow_origins:
            return True
        
        # Check regex pattern
        if self.origin_regex and self.origin_regex.match(origin):
            return True
        
        return False
    
    def validate_origin_security(self, origin: str) -> bool:
        """Validate origin for security issues"""
        
        # Parse the origin URL
        try:
            parsed = urlparse(origin)
        except Exception:
            return False
        
        # Check for HTTPS in production
        if settings.is_production and parsed.scheme != "https":
            log_security_event(
                "cors_insecure_origin",
                severity="warning",
                origin=origin,
                reason="Non-HTTPS origin in production"
            )
            return False
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r".*\.ngrok\.io$",  # Tunneling services
            r".*\.localtunnel\.me$",
            r".*localhost.*",  # Localhost in production
            r".*127\.0\.0\.1.*",
        ]
        
        if settings.is_production:
            for pattern in suspicious_patterns:
                if re.match(pattern, parsed.netloc, re.IGNORECASE):
                    log_security_event(
                        "cors_suspicious_origin",
                        severity="warning",
                        origin=origin,
                        pattern=pattern
                    )
                    return False
        
        return True
    
    async def __call__(self, request: Request, call_next):
        """Process CORS for incoming requests"""
        
        origin = request.headers.get("origin")
        method = request.method
        
        # Handle preflight requests
        if method == "OPTIONS":
            return await self.handle_preflight(request, origin)
        
        # Process actual request
        response = await call_next(request)
        
        # Add CORS headers to response
        if origin:
            self.add_cors_headers(response, origin, method)
        
        return response
    
    async def handle_preflight(self, request: Request, origin: str) -> Response:
        """Handle CORS preflight requests"""
        
        requested_method = request.headers.get("access-control-request-method")
        requested_headers = request.headers.get("access-control-request-headers")
        
        # Log preflight request
        logger.debug(
            "CORS preflight request",
            origin=origin,
            method=requested_method,
            headers=requested_headers
        )
        
        # Check if origin is allowed
        if not origin or not self.is_allowed_origin(origin):
            log_security_event(
                "cors_origin_denied",
                severity="warning",
                origin=origin,
                requested_method=requested_method
            )
            return Response(status_code=403)
        
        # Validate origin security
        if not self.validate_origin_security(origin):
            return Response(status_code=403)
        
        # Check if method is allowed
        if requested_method and requested_method not in self.allow_methods:
            log_security_event(
                "cors_method_denied",
                severity="info",
                origin=origin,
                method=requested_method
            )
            return Response(status_code=405)
        
        # Create preflight response
        headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": ", ".join(self.allow_methods),
            "Access-Control-Max-Age": str(self.max_age),
        }
        
        if self.allow_credentials:
            headers["Access-Control-Allow-Credentials"] = "true"
        
        if self.allow_headers:
            headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)
        
        if requested_headers:
            # Allow requested headers if they're in our allowed list
            requested_headers_list = [h.strip() for h in requested_headers.split(",")]
            allowed_requested_headers = [
                h for h in requested_headers_list 
                if h.lower() in [ah.lower() for ah in self.allow_headers]
            ]
            if allowed_requested_headers:
                headers["Access-Control-Allow-Headers"] = ", ".join(allowed_requested_headers)
        
        return Response(status_code=200, headers=headers)
    
    def add_cors_headers(self, response: Response, origin: str, method: str):
        """Add CORS headers to response"""
        
        if not self.is_allowed_origin(origin):
            return
        
        if not self.validate_origin_security(origin):
            return
        
        response.headers["Access-Control-Allow-Origin"] = origin
        
        if self.allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        if self.expose_headers:
            response.headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)


def setup_cors(app: FastAPI) -> None:
    """Set up CORS middleware for the application"""
    
    # Get environment-specific CORS configuration
    cors_config = env_config.get_security_config()
    
    # Determine allowed origins
    allowed_origins = settings.ALLOWED_HOSTS.copy()
    
    # Add environment-specific origins
    env_origins = cors_config.get("cors_origins", [])
    if env_origins:
        allowed_origins.extend(env_origins)
    
    # Remove duplicates
    allowed_origins = list(set(allowed_origins))
    
    # Development mode - allow all localhost origins
    if settings.is_development:
        dev_origins = [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:8080",
        ]
        allowed_origins.extend(dev_origins)
        allowed_origins = list(set(allowed_origins))
    
    # Configure allowed methods
    allowed_methods = [
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "OPTIONS",
        "HEAD",
    ]
    
    # Configure allowed headers
    allowed_headers = [
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-Request-ID",
        "X-Correlation-ID",
        "Cache-Control",
        "Pragma",
    ]
    
    # Configure exposed headers
    exposed_headers = [
        "X-Request-ID",
        "X-Correlation-ID",
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
    ]
    
    # Add standard CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=allowed_methods,
        allow_headers=allowed_headers,
        expose_headers=exposed_headers,
        max_age=600,  # 10 minutes
    )
    
    # Log CORS configuration
    logger.info(
        "CORS middleware configured",
        allowed_origins=allowed_origins if not settings.is_production else "[REDACTED]",
        allow_credentials=True,
        environment=settings.ENVIRONMENT
    )
    
    # Log security warning for wildcard origins in production
    if "*" in allowed_origins and settings.is_production:
        log_security_event(
            "cors_wildcard_production",
            severity="error",
            message="Wildcard CORS origin detected in production - security risk!"
        )
