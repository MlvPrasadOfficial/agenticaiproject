"""
Enterprise Insights Copilot - API v1 Router
MAANG-level API routing and organization
"""

from fastapi import APIRouter
from app.api.v1 import health

# Create main API router
api_router = APIRouter()

# Include health check routes
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"],
    responses={
        200: {"description": "Healthy"},
        503: {"description": "Service Unavailable"}
    }
)

# Root endpoint
@api_router.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Enterprise Insights Copilot API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/api/v1/health/health"
    }
