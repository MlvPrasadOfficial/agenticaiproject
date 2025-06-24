# Health Check API Routes

from fastapi import APIRouter
import time
import os
import httpx

from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.APP_VERSION,
        "environment": "development" if settings.DEBUG else "production"
    }


@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with system metrics"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.APP_VERSION,
        "components": {
            "ollama": await check_ollama_connection(),
            "pinecone": check_pinecone_configuration()
        },
        "config": {
            "max_file_size": settings.MAX_FILE_SIZE,
            "upload_directory": settings.UPLOAD_DIRECTORY,
            "allowed_file_types": settings.ALLOWED_FILE_TYPES
        }
    }


async def check_ollama_connection():
    """Check if Ollama service is available"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5.0)
            if response.status_code == 200:
                return "connected"
            else:
                return f"error: HTTP {response.status_code}"
    except Exception as e:
        return f"error: {str(e)}"


def check_pinecone_configuration():
    """Check if Pinecone is configured"""
    if not settings.PINECONE_API_KEY:
        return "not_configured"
    return "configured"
