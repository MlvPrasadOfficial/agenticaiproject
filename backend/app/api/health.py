# Health Check API Routes

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import time
import psutil
import os

from app.core.database import get_db
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
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with system metrics"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # System metrics
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.APP_VERSION,
        "components": {
            "database": db_status,
            "ollama": await check_ollama_connection(),
            "pinecone": await check_pinecone_connection()
        },
        "system": {
            "memory_usage": f"{memory.percent}%",
            "disk_usage": f"{disk.percent}%",
            "cpu_count": psutil.cpu_count()
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
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5.0)
            if response.status_code == 200:
                return "connected"
            else:
                return f"error: HTTP {response.status_code}"
    except Exception as e:
        return f"error: {str(e)}"


async def check_pinecone_connection():
    """Check if Pinecone is configured and accessible"""
    try:
        if not settings.PINECONE_API_KEY:
            return "not_configured"
        
        # Add Pinecone connection test here
        return "configured"
    except Exception as e:
        return f"error: {str(e)}"
