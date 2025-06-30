"""
Enterprise Insights Copilot - API v1 Router
MAANG-level API routing and organization
"""

from fastapi import APIRouter
from app.api.v1 import health, upload, data, agents, rag

# Create main API router
api_router = APIRouter()

# Include health check routes
api_router.include_router(
    health.router,
    tags=["health"],
    responses={
        200: {"description": "Healthy"},
        503: {"description": "Service Unavailable"}
    }
)

# Include file upload routes
api_router.include_router(
    upload.router,
    tags=["File Management"],
    responses={
        413: {"description": "File too large"},
        415: {"description": "Unsupported file type"},
        422: {"description": "Validation error"}
    }
)

# Include data processing routes
api_router.include_router(
    data.router,
    tags=["Data Processing"],
    responses={
        404: {"description": "Data not found"},
        422: {"description": "Validation error"}
    }
)

# Include agent system routes
api_router.include_router(
    agents.router,
    tags=["Agent System"],
    responses={
        404: {"description": "Resource not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)

# Include RAG system routes
api_router.include_router(
    rag.router,
    tags=["rag"],
    responses={
        200: {"description": "Success"},
        500: {"description": "Internal server error"}
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
