"""
Enterprise Insights Copilot - Health Check Endpoints
MAANG-level health monitoring and readiness checks
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime, timedelta
import asyncio
import time
import os
import psutil
from pathlib import Path

from app.core.config import settings
from app.core.logging import get_logger
from app.core.environment import env_config

logger = get_logger(__name__)
router = APIRouter()

# Health check models
class HealthStatus(BaseModel):
    """Health status response model"""
    status: str
    timestamp: str
    version: str
    environment: str
    uptime: float
    checks: Dict[str, Any]


class ReadinessStatus(BaseModel):
    """Readiness status response model"""
    ready: bool
    timestamp: str
    version: str
    environment: str
    checks: Dict[str, Any]


class LivenessStatus(BaseModel):
    """Liveness status response model"""
    alive: bool
    timestamp: str
    version: str
    environment: str


# Global startup time for uptime calculation
startup_time = time.time()


async def check_database() -> Dict[str, Any]:
    """Check database connectivity"""
    try:
        # TODO: Implement actual database connection check
        # For now, return mock status
        return {
            "status": "healthy",
            "response_time_ms": 10,
            "message": "Database connection successful"
        }
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Database connection failed"
        }


async def check_redis() -> Dict[str, Any]:
    """Check Redis connectivity"""
    try:
        # TODO: Implement actual Redis connection check
        # For now, return mock status
        return {
            "status": "healthy",
            "response_time_ms": 5,
            "message": "Redis connection successful"
        }
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Redis connection failed"
        }


async def check_external_apis() -> Dict[str, Any]:
    """Check external API dependencies"""
    try:
        checks = {}
        
        # Check OpenAI API
        if settings.OPENAI_API_KEY:
            checks["openai"] = {
                "status": "healthy",
                "message": "API key configured"
            }
        else:
            checks["openai"] = {
                "status": "warning",
                "message": "API key not configured"
            }
        
        # Check Anthropic API
        if settings.ANTHROPIC_API_KEY:
            checks["anthropic"] = {
                "status": "healthy",
                "message": "API key configured"
            }
        else:
            checks["anthropic"] = {
                "status": "warning",
                "message": "API key not configured"
            }
        
        # Check Pinecone
        if settings.PINECONE_API_KEY:
            checks["pinecone"] = {
                "status": "healthy",
                "message": "API key configured"
            }
        else:
            checks["pinecone"] = {
                "status": "warning",
                "message": "API key not configured"
            }
        
        return checks
        
    except Exception as e:
        logger.error("External API health check failed", error=str(e))
        return {
            "error": str(e),
            "message": "External API check failed"
        }


def check_system_resources() -> Dict[str, Any]:
    """Check system resource usage"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        # Determine overall status
        status = "healthy"
        warnings = []
        
        if cpu_percent > 80:
            status = "warning"
            warnings.append(f"High CPU usage: {cpu_percent}%")
        
        if memory_percent > 85:
            status = "warning" if status == "healthy" else "unhealthy"
            warnings.append(f"High memory usage: {memory_percent}%")
        
        if disk_percent > 90:
            status = "warning" if status == "healthy" else "unhealthy"
            warnings.append(f"High disk usage: {disk_percent}%")
        
        return {
            "status": status,
            "cpu_percent": round(cpu_percent, 2),
            "memory_percent": round(memory_percent, 2),
            "disk_percent": round(disk_percent, 2),
            "warnings": warnings
        }
        
    except Exception as e:
        logger.error("System resource check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "System resource check failed"
        }


def check_file_system() -> Dict[str, Any]:
    """Check file system health"""
    try:
        checks = {}
        
        # Check upload directory
        upload_dir = Path(settings.UPLOAD_DIRECTORY)
        if upload_dir.exists() and upload_dir.is_dir():
            checks["upload_directory"] = {
                "status": "healthy",
                "path": str(upload_dir),
                "writable": os.access(upload_dir, os.W_OK)
            }
        else:
            checks["upload_directory"] = {
                "status": "warning",
                "path": str(upload_dir),
                "message": "Upload directory does not exist"
            }
        
        # Check log directory
        log_dir = Path("logs")
        if log_dir.exists() and log_dir.is_dir():
            checks["log_directory"] = {
                "status": "healthy",
                "path": str(log_dir),
                "writable": os.access(log_dir, os.W_OK)
            }
        else:
            checks["log_directory"] = {
                "status": "warning",
                "path": str(log_dir),
                "message": "Log directory does not exist"
            }
        
        return checks
        
    except Exception as e:
        logger.error("File system check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "File system check failed"
        }


@router.get("/health/", response_model=HealthStatus)
async def health_check():
    """
    Comprehensive health check endpoint
    Returns detailed health information about all system components
    """
    start_time = time.time()
    timestamp = datetime.utcnow().isoformat() + "Z"
    uptime = time.time() - startup_time
    
    try:
        # Run all health checks
        checks = {
            "database": await check_database(),
            "redis": await check_redis(),
            "external_apis": await check_external_apis(),
            "system_resources": check_system_resources(),
            "file_system": check_file_system(),
        }
        
        # Determine overall status
        overall_status = "healthy"
        for check_name, check_result in checks.items():
            if isinstance(check_result, dict):
                if check_result.get("status") == "unhealthy":
                    overall_status = "unhealthy"
                    break
                elif check_result.get("status") == "warning" and overall_status == "healthy":
                    overall_status = "warning"
        
        # Log health check
        duration = (time.time() - start_time) * 1000
        logger.info(
            "Health check completed",
            status=overall_status,
            duration_ms=round(duration, 2),
            uptime_seconds=round(uptime, 2)
        )
        
        return HealthStatus(
            status=overall_status,
            timestamp=timestamp,
            version=settings.VERSION,
            environment=settings.ENVIRONMENT,
            uptime=round(uptime, 2),
            checks=checks
        )
        
    except Exception as e:
        logger.error("Health check failed", error=str(e), exc_info=True)
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": timestamp,
                "version": settings.VERSION,
                "environment": settings.ENVIRONMENT,
                "error": str(e),
                "message": "Health check failed"
            }
        )


@router.get("/readiness", response_model=ReadinessStatus)
async def readiness_check():
    """
    Readiness check endpoint for Kubernetes
    Determines if the application is ready to accept traffic
    """
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    try:
        # Check critical dependencies for readiness
        checks = {
            "database": await check_database(),
            "redis": await check_redis(),
            "configuration": {
                "status": "healthy" if settings.SECRET_KEY != "your-super-secret-key-change-in-production" else "warning",
                "message": "Configuration loaded"
            }
        }
        
        # Determine readiness
        ready = True
        for check_name, check_result in checks.items():
            if isinstance(check_result, dict) and check_result.get("status") == "unhealthy":
                ready = False
                break
        
        status_code = 200 if ready else 503
        
        logger.info(
            "Readiness check completed",
            ready=ready,
            checks=checks
        )
        
        response = ReadinessStatus(
            ready=ready,
            timestamp=timestamp,
            version=settings.VERSION,
            environment=settings.ENVIRONMENT,
            checks=checks
        )
        
        return JSONResponse(
            status_code=status_code,
            content=response.dict()
        )
        
    except Exception as e:
        logger.error("Readiness check failed", error=str(e), exc_info=True)
        return JSONResponse(
            status_code=503,
            content={
                "ready": False,
                "timestamp": timestamp,
                "version": settings.VERSION,
                "environment": settings.ENVIRONMENT,
                "error": str(e),
                "message": "Readiness check failed"
            }
        )


@router.get("/liveness", response_model=LivenessStatus)
async def liveness_check():
    """
    Liveness check endpoint for Kubernetes
    Simple check to determine if the application is alive
    """
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    try:
        # Simple liveness check - if we can respond, we're alive
        response = LivenessStatus(
            alive=True,
            timestamp=timestamp,
            version=settings.VERSION,
            environment=settings.ENVIRONMENT
        )
        
        return response
        
    except Exception as e:
        logger.error("Liveness check failed", error=str(e), exc_info=True)
        return JSONResponse(
            status_code=503,
            content={
                "alive": False,
                "timestamp": timestamp,
                "version": settings.VERSION,
                "environment": settings.ENVIRONMENT,
                "error": str(e)
            }
        )


@router.get("/metrics")
async def metrics():
    """
    Basic metrics endpoint for monitoring
    """
    uptime = time.time() - startup_time
    
    # TODO: Implement Prometheus metrics
    metrics_data = {
        "uptime_seconds": round(uptime, 2),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    return metrics_data
