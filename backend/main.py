"""
Enterprise Insights Copilot - Main FastAPI Application
MAANG-level backend with multi-agent AI capabilities
"""

from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.security import setup_security_middleware
from app.api.v1.api import api_router
from app.middleware.cors import setup_cors
from app.middleware.request_id import setup_request_middleware
from app.middleware.error_handler import setup_error_handling

# Set up logging
setup_logging()

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise-grade AI-powered business insights platform",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# Set up middleware (order matters!)
setup_error_handling(app)      # Must be first to catch all errors
setup_request_middleware(app)  # Request tracking and correlation
setup_security_middleware(app) # Security headers, rate limiting, CORS
setup_cors(app)               # CORS handling

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Application startup event handler"""
    print(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION} starting up...")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 Debug mode: {settings.DEBUG}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event handler"""
    print(f"🛑 {settings.PROJECT_NAME} shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )
