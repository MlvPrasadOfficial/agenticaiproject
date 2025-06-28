"""
Prometheus metrics collection for Enterprise Insights Copilot
Provides business and technical metrics for monitoring and observability.
"""

import time
from functools import wraps
from typing import Dict, Any, Optional
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Info,
    generate_latest,
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    REGISTRY
)
from fastapi import Request, Response
from fastapi.responses import PlainTextResponse


class MetricsCollector:
    """Centralized metrics collection for the application."""
    
    def __init__(self):
        # HTTP request metrics
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code']
        )
        
        self.http_request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint']
        )
        
        # Business logic metrics
        self.agent_executions_total = Counter(
            'agent_executions_total',
            'Total agent executions',
            ['agent_type', 'status']
        )
        
        self.agent_execution_duration = Histogram(
            'agent_execution_duration_seconds',
            'Agent execution duration in seconds',
            ['agent_type']
        )
        
        self.data_uploads_total = Counter(
            'data_uploads_total',
            'Total data uploads',
            ['file_type', 'status']
        )
        
        self.data_processing_duration = Histogram(
            'data_processing_duration_seconds',
            'Data processing duration in seconds',
            ['processing_type']
        )
        
        # System metrics
        self.active_sessions = Gauge(
            'active_sessions_total',
            'Number of active user sessions'
        )
        
        self.memory_usage_bytes = Gauge(
            'memory_usage_bytes',
            'Memory usage in bytes',
            ['type']
        )
        
        self.database_connections = Gauge(
            'database_connections_active',
            'Active database connections'
        )
        
        # Error metrics
        self.errors_total = Counter(
            'errors_total',
            'Total errors',
            ['error_type', 'component']
        )
        
        # Application info
        self.app_info = Info(
            'app_info',
            'Application information'
        )
        self.app_info.info({
            'version': '1.0.0',
            'service': 'enterprise-insights-backend',
            'environment': 'production'
        })
    
    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics."""
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        
        self.http_request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def record_agent_execution(self, agent_type: str, status: str, duration: float):
        """Record agent execution metrics."""
        self.agent_executions_total.labels(
            agent_type=agent_type,
            status=status
        ).inc()
        
        self.agent_execution_duration.labels(
            agent_type=agent_type
        ).observe(duration)
    
    def record_data_upload(self, file_type: str, status: str):
        """Record data upload metrics."""
        self.data_uploads_total.labels(
            file_type=file_type,
            status=status
        ).inc()
    
    def record_data_processing(self, processing_type: str, duration: float):
        """Record data processing metrics."""
        self.data_processing_duration.labels(
            processing_type=processing_type
        ).observe(duration)
    
    def record_error(self, error_type: str, component: str):
        """Record error metrics."""
        self.errors_total.labels(
            error_type=error_type,
            component=component
        ).inc()
    
    def update_active_sessions(self, count: int):
        """Update active sessions count."""
        self.active_sessions.set(count)
    
    def update_memory_usage(self, memory_type: str, bytes_used: int):
        """Update memory usage metrics."""
        self.memory_usage_bytes.labels(type=memory_type).set(bytes_used)
    
    def update_database_connections(self, count: int):
        """Update database connections count."""
        self.database_connections.set(count)


# Global metrics collector instance
metrics = MetricsCollector()


def track_execution_time(metric_name: str, labels: Optional[Dict[str, str]] = None):
    """Decorator to track function execution time."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record success metrics
                if metric_name == "agent_execution":
                    agent_type = labels.get('agent_type', 'unknown') if labels else 'unknown'
                    metrics.record_agent_execution(agent_type, 'success', duration)
                elif metric_name == "data_processing":
                    processing_type = labels.get('processing_type', 'unknown') if labels else 'unknown'
                    metrics.record_data_processing(processing_type, duration)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Record error metrics
                if metric_name == "agent_execution":
                    agent_type = labels.get('agent_type', 'unknown') if labels else 'unknown'
                    metrics.record_agent_execution(agent_type, 'error', duration)
                    metrics.record_error(e.__class__.__name__, 'agent')
                elif metric_name == "data_processing":
                    processing_type = labels.get('processing_type', 'unknown') if labels else 'unknown'
                    metrics.record_data_processing(processing_type, duration)
                    metrics.record_error(e.__class__.__name__, 'data_processing')
                
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record success metrics
                if metric_name == "agent_execution":
                    agent_type = labels.get('agent_type', 'unknown') if labels else 'unknown'
                    metrics.record_agent_execution(agent_type, 'success', duration)
                elif metric_name == "data_processing":
                    processing_type = labels.get('processing_type', 'unknown') if labels else 'unknown'
                    metrics.record_data_processing(processing_type, duration)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Record error metrics
                if metric_name == "agent_execution":
                    agent_type = labels.get('agent_type', 'unknown') if labels else 'unknown'
                    metrics.record_agent_execution(agent_type, 'error', duration)
                    metrics.record_error(e.__class__.__name__, 'agent')
                elif metric_name == "data_processing":
                    processing_type = labels.get('processing_type', 'unknown') if labels else 'unknown'
                    metrics.record_data_processing(processing_type, duration)
                    metrics.record_error(e.__class__.__name__, 'data_processing')
                
                raise
        
        return async_wrapper if 'async' in func.__code__.co_flags.__str__() else sync_wrapper
    return decorator


async def metrics_middleware(request: Request, call_next):
    """FastAPI middleware to collect HTTP metrics."""
    start_time = time.time()
    
    # Extract endpoint pattern
    endpoint = request.url.path
    if hasattr(request.state, 'route'):
        endpoint = request.state.route.path
    
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Record metrics
    metrics.record_http_request(
        method=request.method,
        endpoint=endpoint,
        status_code=response.status_code,
        duration=duration
    )
    
    return response


def get_metrics_endpoint():
    """Get Prometheus metrics endpoint handler."""
    async def metrics_handler():
        """Return Prometheus metrics in text format."""
        return PlainTextResponse(
            generate_latest(REGISTRY),
            media_type=CONTENT_TYPE_LATEST
        )
    
    return metrics_handler


# Health check function for metrics
def check_metrics_health() -> Dict[str, Any]:
    """Check if metrics collection is healthy."""
    try:
        # Test metric recording
        test_start = time.time()
        metrics.record_http_request("GET", "/health", 200, 0.001)
        metrics_time = time.time() - test_start
        
        return {
            "status": "healthy",
            "metrics_recording_time_ms": round(metrics_time * 1000, 2),
            "registry_collectors": len(REGISTRY._collector_to_names),
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }
