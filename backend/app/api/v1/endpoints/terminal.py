"""
Terminal Status API endpoints for Enterprise Insights Copilot
Provides REST API access to terminal monitoring and status information
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import asyncio
from datetime import datetime, timezone

from app.utils.terminal_monitor import terminal_monitor, get_terminal_status
from app.core.logging import get_logger

logger = get_logger("terminal_api")

router = APIRouter()


@router.get("/status", summary="Get Terminal Status")
async def get_current_terminal_status() -> Dict[str, Any]:
    """
    Get comprehensive terminal and system status information.
    
    Returns:
        Dict containing backend status, system info, ports, and logs
    """
    try:
        status = get_terminal_status()
        logger.info("Terminal status requested via API")
        return {
            "success": True,
            "data": status,
            "message": "Terminal status retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting terminal status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get terminal status: {str(e)}")


@router.get("/status/backend", summary="Get Backend Status")
async def get_backend_status() -> Dict[str, Any]:
    """
    Get specific backend process status information.
    
    Returns:
        Dict containing backend process details
    """
    try:
        status_data = terminal_monitor.collect_terminal_status()
        
        backend_info = {
            "status": status_data.backend_status.value,
            "port_active": status_data.ports_status.get(8000, False),
            "process": None
        }
        
        if status_data.backend_process:
            backend_info["process"] = {
                "pid": status_data.backend_process.pid,
                "name": status_data.backend_process.name,
                "status": status_data.backend_process.status,
                "cpu_percent": status_data.backend_process.cpu_percent,
                "memory_mb": status_data.backend_process.memory_mb,
                "memory_percent": status_data.backend_process.memory_percent,
                "create_time": status_data.backend_process.create_time.isoformat(),
                "port": status_data.backend_process.port
            }
        
        logger.info(f"Backend status requested - Status: {backend_info['status']}")
        
        return {
            "success": True,
            "data": backend_info,
            "timestamp": status_data.timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting backend status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get backend status: {str(e)}")


@router.get("/status/system", summary="Get System Status")
async def get_system_status() -> Dict[str, Any]:
    """
    Get system resource information.
    
    Returns:
        Dict containing CPU, memory, and disk usage
    """
    try:
        system_info = terminal_monitor.get_system_info()
        
        logger.info("System status requested via API")
        
        return {
            "success": True,
            "data": system_info,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")


@router.get("/status/logs", summary="Get Logs Summary")
async def get_logs_summary() -> Dict[str, Any]:
    """
    Get summary of recent log files.
    
    Returns:
        Dict containing log file information
    """
    try:
        log_summary = terminal_monitor.get_log_summary()
        
        logger.info("Logs summary requested via API")
        
        return {
            "success": True,
            "data": log_summary,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting logs summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get logs summary: {str(e)}")


@router.post("/monitor/start", summary="Start Terminal Monitoring")
async def start_terminal_monitoring(
    background_tasks: BackgroundTasks,
    interval: int = 30
) -> Dict[str, Any]:
    """
    Start background terminal monitoring.
    
    Args:
        interval: Monitoring interval in seconds (default: 30)
    
    Returns:
        Success message
    """
    try:
        # Add background task for monitoring
        background_tasks.add_task(terminal_monitor.async_monitoring, interval)
        
        logger.info(f"Terminal monitoring started with {interval}s interval")
        
        return {
            "success": True,
            "message": f"Terminal monitoring started with {interval}s interval",
            "interval": interval
        }
        
    except Exception as e:
        logger.error(f"Error starting terminal monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")


@router.post("/status/refresh", summary="Refresh Status")
async def refresh_terminal_status() -> Dict[str, Any]:
    """
    Force refresh of terminal status information.
    
    Returns:
        Updated status information
    """
    try:
        status_data = terminal_monitor.log_terminal_status()
        
        logger.info("Terminal status manually refreshed")
        
        return {
            "success": True,
            "message": "Status refreshed successfully",
            "data": terminal_monitor.get_status_report(),
            "timestamp": status_data.timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error refreshing terminal status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to refresh status: {str(e)}")


@router.get("/health", summary="Health Check")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint for terminal monitoring system.
    
    Returns:
        Health status
    """
    try:
        # Quick status check
        status_data = terminal_monitor.collect_terminal_status()
        
        is_healthy = (
            status_data.backend_status.value in ["running", "starting"] and
            status_data.ports_status.get(8000, False)
        )
        
        return {
            "success": True,
            "healthy": is_healthy,
            "backend_status": status_data.backend_status.value,
            "backend_port_active": status_data.ports_status.get(8000, False),
            "timestamp": status_data.timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return {
            "success": False,
            "healthy": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
