"""
Debugging dashboard endpoints for Enterprise Insights Copilot
Provides real-time debugging and monitoring capabilities via REST API.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import HTMLResponse
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import asyncio

from app.utils.logging import get_logger
from app.utils.metrics import metrics, check_metrics_health
from app.utils.business_metrics import get_business_analyzer
from app.utils.log_aggregation import get_log_analytics
from app.utils.performance_monitoring import get_performance_monitor, get_system_performance_snapshot
from app.utils.tracing import get_tracer


router = APIRouter(prefix="/debug", tags=["debugging"])
logger = get_logger()


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Comprehensive health check endpoint."""
    try:
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "enterprise-insights-backend",
            "version": "1.0.0",
            "components": {
                "metrics": check_metrics_health(),
                "logging": await check_logging_health(),
                "performance_monitor": await check_performance_health(),
                "system": await get_system_performance_snapshot()
            }
        }
        
        # Check if any component is unhealthy
        for component, status in health_data["components"].items():
            if isinstance(status, dict) and status.get("status") == "unhealthy":
                health_data["status"] = "degraded"
                break
        
        logger.info("Health check completed", health_status=health_data["status"])
        return health_data
        
    except Exception as e:
        logger.error("Health check failed", error=e)
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/metrics/summary", response_model=Dict[str, Any])
async def metrics_summary():
    """Get metrics summary for debugging."""
    try:
        business_analyzer = get_business_analyzer()
        
        summary = {
            "business_metrics": business_analyzer.generate_business_health_report(),
            "system_metrics": await get_system_performance_snapshot(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info("Metrics summary generated")
        return summary
        
    except Exception as e:
        logger.error("Failed to generate metrics summary", error=e)
        raise HTTPException(status_code=500, detail=f"Metrics summary failed: {str(e)}")


@router.get("/logs/recent", response_model=List[Dict[str, Any]])
async def recent_logs(
    level: Optional[str] = Query(None, description="Log level filter"),
    component: Optional[str] = Query(None, description="Component filter"),
    limit: int = Query(100, description="Number of logs to return", le=1000)
):
    """Get recent logs for debugging."""
    try:
        log_analytics = get_log_analytics()
        
        # Build query filters
        query_filters = {}
        if level:
            query_filters["level"] = level.upper()
        if component:
            query_filters["component"] = component
        
        # Get logs (this would typically query the storage backend)
        logs = await log_analytics.storage.query_logs(query_filters)
        
        # Convert to dict format and limit results
        log_data = []
        for log in logs[:limit]:
            log_dict = {
                "timestamp": log.timestamp.isoformat(),
                "level": log.level,
                "message": log.message,
                "service": log.service,
                "trace_id": log.trace_id,
                "component": log.component,
                "metadata": log.metadata
            }
            log_data.append(log_dict)
        
        logger.info(f"Retrieved {len(log_data)} recent logs", 
                   level_filter=level, component_filter=component)
        return log_data
        
    except Exception as e:
        logger.error("Failed to retrieve recent logs", error=e)
        raise HTTPException(status_code=500, detail=f"Log retrieval failed: {str(e)}")


@router.get("/logs/errors", response_model=Dict[str, Any])
async def error_logs_summary(hours: int = Query(24, description="Hours to look back", le=168)):
    """Get error logs summary for debugging."""
    try:
        log_analytics = get_log_analytics()
        error_summary = await log_analytics.get_error_summary(hours)
        
        logger.info(f"Error summary generated for last {hours} hours")
        return error_summary
        
    except Exception as e:
        logger.error("Failed to generate error summary", error=e)
        raise HTTPException(status_code=500, detail=f"Error summary failed: {str(e)}")


@router.get("/performance/summary", response_model=Dict[str, Any])
async def performance_summary(
    operation: Optional[str] = Query(None, description="Operation name filter"),
    last_n: int = Query(100, description="Number of recent operations", le=1000)
):
    """Get performance summary for debugging."""
    try:
        performance_monitor = get_performance_monitor()
        
        summary = performance_monitor.get_performance_summary(operation, last_n)
        
        # Add current system snapshot
        summary["current_system"] = await get_system_performance_snapshot()
        
        logger.info(f"Performance summary generated for operation: {operation}")
        return summary
        
    except Exception as e:
        logger.error("Failed to generate performance summary", error=e)
        raise HTTPException(status_code=500, detail=f"Performance summary failed: {str(e)}")


@router.get("/tracing/active", response_model=Dict[str, Any])
async def active_traces():
    """Get information about active traces."""
    try:
        # This would typically query the tracing backend
        # For now, returning a placeholder structure
        
        traces_info = {
            "active_traces_count": 12,
            "sampling_rate": 0.1,
            "exporters": ["jaeger", "otlp", "console"],
            "instrumented_libraries": [
                "fastapi",
                "requests", 
                "sqlalchemy"
            ],
            "recent_spans": [
                {
                    "trace_id": "abc123",
                    "span_id": "def456", 
                    "operation_name": "agent.data_analyst.execute",
                    "duration_ms": 250,
                    "status": "ok"
                }
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info("Active traces info retrieved")
        return traces_info
        
    except Exception as e:
        logger.error("Failed to get active traces", error=e)
        raise HTTPException(status_code=500, detail=f"Tracing info failed: {str(e)}")


@router.get("/environment", response_model=Dict[str, Any])
async def environment_info():
    """Get environment and configuration information."""
    try:
        import os
        import sys
        import platform
        
        env_info = {
            "python_version": sys.version,
            "platform": platform.platform(),
            "environment_variables": {
                key: "***" if any(secret in key.lower() for secret in ["key", "secret", "password", "token"]) 
                      else value
                for key, value in os.environ.items()
                if key.startswith(("APP_", "ENVIRONMENT", "DEBUG", "ALLOWED_ORIGINS"))
            },
            "system_info": {
                "cpu_count": os.cpu_count(),
                "python_path": sys.executable,
                "working_directory": os.getcwd()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info("Environment info retrieved")
        return env_info
        
    except Exception as e:
        logger.error("Failed to get environment info", error=e)
        raise HTTPException(status_code=500, detail=f"Environment info failed: {str(e)}")


@router.get("/config/validate", response_model=Dict[str, Any])
async def validate_configuration():
    """Validate application configuration."""
    try:
        import os
        
        config_checks = {
            "environment_variables": {
                "ENVIRONMENT": os.getenv("ENVIRONMENT", "NOT_SET"),
                "DEBUG": os.getenv("DEBUG", "NOT_SET"),
                "ALLOWED_ORIGINS": "SET" if os.getenv("ALLOWED_ORIGINS") else "NOT_SET"
            },
            "dependencies": await check_dependencies(),
            "services": await check_external_services(),
            "validation_timestamp": datetime.utcnow().isoformat()
        }
        
        # Determine overall status
        issues = []
        if config_checks["environment_variables"]["ENVIRONMENT"] == "NOT_SET":
            issues.append("ENVIRONMENT variable not set")
        
        config_checks["status"] = "valid" if not issues else "issues_found"
        config_checks["issues"] = issues
        
        logger.info("Configuration validation completed", 
                   status=config_checks["status"], issues_count=len(issues))
        return config_checks
        
    except Exception as e:
        logger.error("Configuration validation failed", error=e)
        raise HTTPException(status_code=500, detail=f"Config validation failed: {str(e)}")


@router.get("/dashboard", response_class=HTMLResponse)
async def debugging_dashboard():
    """Simple HTML debugging dashboard."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Enterprise Insights - Debug Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 1200px; margin: 0 auto; }
            .section { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 5px; }
            .metric { display: inline-block; margin: 10px; padding: 10px; background: white; border-radius: 3px; }
            .error { color: red; }
            .success { color: green; }
            .warning { color: orange; }
            button { padding: 10px 20px; margin: 5px; cursor: pointer; }
            pre { background: #f0f0f0; padding: 10px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Enterprise Insights - Debug Dashboard</h1>
            
            <div class="section">
                <h2>System Health</h2>
                <button onclick="loadHealth()">Refresh Health</button>
                <div id="health-status"></div>
            </div>
            
            <div class="section">
                <h2>Recent Logs</h2>
                <button onclick="loadLogs()">Load Recent Logs</button>
                <button onclick="loadErrors()">Load Error Summary</button>
                <div id="logs-container"></div>
            </div>
            
            <div class="section">
                <h2>Performance Metrics</h2>
                <button onclick="loadPerformance()">Refresh Performance</button>
                <div id="performance-container"></div>
            </div>
            
            <div class="section">
                <h2>Environment Info</h2>
                <button onclick="loadEnvironment()">Load Environment</button>
                <div id="environment-container"></div>
            </div>
        </div>
        
        <script>
            async function loadHealth() {
                try {
                    const response = await fetch('/debug/health');
                    const data = await response.json();
                    document.getElementById('health-status').innerHTML = 
                        '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    document.getElementById('health-status').innerHTML = 
                        '<span class="error">Failed to load health data: ' + error.message + '</span>';
                }
            }
            
            async function loadLogs() {
                try {
                    const response = await fetch('/debug/logs/recent?limit=50');
                    const data = await response.json();
                    document.getElementById('logs-container').innerHTML = 
                        '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    document.getElementById('logs-container').innerHTML = 
                        '<span class="error">Failed to load logs: ' + error.message + '</span>';
                }
            }
            
            async function loadErrors() {
                try {
                    const response = await fetch('/debug/logs/errors');
                    const data = await response.json();
                    document.getElementById('logs-container').innerHTML = 
                        '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    document.getElementById('logs-container').innerHTML = 
                        '<span class="error">Failed to load error summary: ' + error.message + '</span>';
                }
            }
            
            async function loadPerformance() {
                try {
                    const response = await fetch('/debug/performance/summary');
                    const data = await response.json();
                    document.getElementById('performance-container').innerHTML = 
                        '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    document.getElementById('performance-container').innerHTML = 
                        '<span class="error">Failed to load performance data: ' + error.message + '</span>';
                }
            }
            
            async function loadEnvironment() {
                try {
                    const response = await fetch('/debug/environment');
                    const data = await response.json();
                    document.getElementById('environment-container').innerHTML = 
                        '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    document.getElementById('environment-container').innerHTML = 
                        '<span class="error">Failed to load environment info: ' + error.message + '</span>';
                }
            }
            
            // Auto-load health on page load
            window.onload = function() {
                loadHealth();
            };
        </script>
    </body>
    </html>
    """
    
    logger.info("Debug dashboard accessed")
    return HTMLResponse(content=html_content)


# Helper functions
async def check_logging_health() -> Dict[str, Any]:
    """Check if logging system is healthy."""
    try:
        logger.info("Logging health check test")
        return {
            "status": "healthy",
            "logger_name": logger.logger.name,
            "log_level": logger.logger.level,
            "handlers_count": len(logger.logger.handlers)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


async def check_performance_health() -> Dict[str, Any]:
    """Check if performance monitoring is healthy."""
    try:
        performance_monitor = get_performance_monitor()
        active_ops = len(performance_monitor.active_operations)
        history_size = len(performance_monitor.performance_history)
        
        return {
            "status": "healthy",
            "active_operations": active_ops,
            "history_size": history_size,
            "max_history_size": 1000
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e)
        }


async def check_dependencies() -> Dict[str, str]:
    """Check if required dependencies are available."""
    dependencies = {}
    
    try:
        import fastapi
        dependencies["fastapi"] = fastapi.__version__
    except ImportError:
        dependencies["fastapi"] = "NOT_INSTALLED"
    
    try:
        import prometheus_client
        dependencies["prometheus_client"] = "INSTALLED"
    except ImportError:
        dependencies["prometheus_client"] = "NOT_INSTALLED"
    
    try:
        import opentelemetry
        dependencies["opentelemetry"] = "INSTALLED"
    except ImportError:
        dependencies["opentelemetry"] = "NOT_INSTALLED"
    
    return dependencies


async def check_external_services() -> Dict[str, str]:
    """Check connectivity to external services."""
    services = {
        "jaeger": "UNKNOWN",
        "prometheus": "UNKNOWN",
        "otlp_collector": "UNKNOWN"
    }
    
    # In a real implementation, this would actually check connectivity
    # For now, just return placeholder status
    return services
