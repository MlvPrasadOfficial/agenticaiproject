# LOGGING & DEBUGGING STRATEGY
# Enterprise Insights Copilot - Production-Grade Observability

## OVERVIEW

This document defines the comprehensive logging, debugging, and observability strategy for the Enterprise Insights Copilot. It follows industry best practices from MAANG companies and provides extensive visibility into system behavior, performance, and issues.

## LOGGING ARCHITECTURE

### Multi-Layer Logging Strategy
```python
# Logging Levels & Purpose
TRACE    = 5   # Detailed execution flow (development only)
DEBUG    = 10  # Detailed diagnostic information
INFO     = 20  # General information about system operation
WARNING  = 30  # Something unexpected happened but system continues
ERROR    = 40  # Error occurred but system can continue
CRITICAL = 50  # System cannot continue, immediate attention required
```

### Structured Logging Implementation
```python
# backend/app/core/logging_config.py
import structlog
import logging
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pythonjsonlogger import jsonlogger
import uuid
import asyncio
from contextvars import ContextVar

# Context variables for tracing
request_id: ContextVar[str] = ContextVar('request_id', default='')
user_id: ContextVar[str] = ContextVar('user_id', default='')
session_id: ContextVar[str] = ContextVar('session_id', default='')

class CustomJSONFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        
        # Add standard fields
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno
        
        # Add context from ContextVars
        log_record['request_id'] = request_id.get()
        log_record['user_id'] = user_id.get()
        log_record['session_id'] = session_id.get()
        
        # Add process info
        log_record['process_id'] = record.process
        log_record['thread_id'] = record.thread

def setup_logging(environment: str = "development"):
    """Setup comprehensive logging configuration"""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    formatter = CustomJSONFormatter(
        '%(timestamp)s %(level)s %(logger)s %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # File handlers
    info_handler = logging.FileHandler('logs/app.log')
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)
    
    error_handler = logging.FileHandler('logs/error.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # Debug handler (development only)
    if environment == "development":
        debug_handler = logging.FileHandler('logs/debug.log')
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)
        
        logging.getLogger().addHandler(debug_handler)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if environment == "development" else logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(info_handler)
    root_logger.addHandler(error_handler)
    
    # Configure specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)

class AgentLogger:
    """Specialized logger for agent operations"""
    
    def __init__(self, agent_name: str):
        self.logger = structlog.get_logger(f"agent.{agent_name}")
        self.agent_name = agent_name
    
    async def log_agent_start(self, input_data: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Log agent execution start"""
        await self.logger.ainfo(
            "agent_execution_started",
            agent=self.agent_name,
            input_data=self._sanitize_data(input_data),
            metadata=metadata or {}
        )
    
    async def log_agent_step(self, step: str, data: Dict[str, Any], duration: float = None):
        """Log individual agent steps"""
        await self.logger.ainfo(
            "agent_step_completed",
            agent=self.agent_name,
            step=step,
            data=self._sanitize_data(data),
            duration_ms=duration * 1000 if duration else None
        )
    
    async def log_agent_success(self, result: Dict[str, Any], metrics: Dict[str, Any]):
        """Log successful agent completion"""
        await self.logger.ainfo(
            "agent_execution_completed",
            agent=self.agent_name,
            status="success",
            result=self._sanitize_data(result),
            metrics=metrics
        )
    
    async def log_agent_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log agent errors with full context"""
        await self.logger.aerror(
            "agent_execution_failed",
            agent=self.agent_name,
            status="error",
            error_type=type(error).__name__,
            error_message=str(error),
            context=context or {},
            exc_info=True
        )
    
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from logs"""
        sensitive_keys = {'password', 'token', 'key', 'secret', 'api_key'}
        
        if isinstance(data, dict):
            return {
                k: "[REDACTED]" if any(sens in k.lower() for sens in sensitive_keys) else v
                for k, v in data.items()
            }
        return data

class WorkflowLogger:
    """Specialized logger for workflow operations"""
    
    def __init__(self):
        self.logger = structlog.get_logger("workflow")
    
    async def log_workflow_start(self, workflow_id: str, input_data: Dict[str, Any]):
        """Log workflow initiation"""
        await self.logger.ainfo(
            "workflow_started",
            workflow_id=workflow_id,
            input_data=self._sanitize_data(input_data),
            stage="initialization"
        )
    
    async def log_state_transition(self, workflow_id: str, from_state: str, to_state: str, metadata: Dict[str, Any] = None):
        """Log state transitions in workflow"""
        await self.logger.ainfo(
            "workflow_state_transition",
            workflow_id=workflow_id,
            from_state=from_state,
            to_state=to_state,
            metadata=metadata or {}
        )
    
    async def log_workflow_completion(self, workflow_id: str, final_state: Dict[str, Any], metrics: Dict[str, Any]):
        """Log workflow completion"""
        await self.logger.ainfo(
            "workflow_completed",
            workflow_id=workflow_id,
            final_state=final_state,
            metrics=metrics,
            stage="completion"
        )
```

### Performance Logging
```python
# backend/app/core/performance_logging.py
import time
import psutil
import asyncio
from typing import Dict, Any, Optional
from functools import wraps
from dataclasses import dataclass
import structlog

@dataclass
class PerformanceMetrics:
    duration: float
    memory_usage: float
    cpu_usage: float
    db_queries: int
    api_calls: int
    cache_hits: int
    cache_misses: int

class PerformanceLogger:
    def __init__(self):
        self.logger = structlog.get_logger("performance")
        self.metrics_history = []
    
    def track_performance(self, operation_name: str):
        """Decorator to track performance of operations"""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                start_cpu = psutil.cpu_percent()
                
                try:
                    result = await func(*args, **kwargs)
                    
                    end_time = time.time()
                    end_memory = psutil.Process().memory_info().rss / 1024 / 1024
                    end_cpu = psutil.cpu_percent()
                    
                    metrics = PerformanceMetrics(
                        duration=end_time - start_time,
                        memory_usage=end_memory - start_memory,
                        cpu_usage=end_cpu - start_cpu,
                        db_queries=0,  # To be implemented with DB interceptor
                        api_calls=0,   # To be implemented with HTTP interceptor
                        cache_hits=0,  # To be implemented with cache interceptor
                        cache_misses=0
                    )
                    
                    await self.log_performance(operation_name, metrics, success=True)
                    return result
                    
                except Exception as e:
                    end_time = time.time()
                    await self.log_performance(
                        operation_name, 
                        PerformanceMetrics(
                            duration=end_time - start_time,
                            memory_usage=0,
                            cpu_usage=0,
                            db_queries=0,
                            api_calls=0,
                            cache_hits=0,
                            cache_misses=0
                        ), 
                        success=False,
                        error=str(e)
                    )
                    raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Similar implementation for sync functions
                pass
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    async def log_performance(self, operation: str, metrics: PerformanceMetrics, success: bool, error: str = None):
        """Log performance metrics"""
        await self.logger.ainfo(
            "performance_metrics",
            operation=operation,
            duration_ms=metrics.duration * 1000,
            memory_delta_mb=metrics.memory_usage,
            cpu_delta_percent=metrics.cpu_usage,
            db_queries=metrics.db_queries,
            api_calls=metrics.api_calls,
            cache_efficiency=metrics.cache_hits / (metrics.cache_hits + metrics.cache_misses) if (metrics.cache_hits + metrics.cache_misses) > 0 else 0,
            success=success,
            error=error
        )
        
        self.metrics_history.append(metrics)
        
        # Alert on performance degradation
        if metrics.duration > 30:  # 30 seconds threshold
            await self.logger.awarning(
                "performance_alert",
                operation=operation,
                issue="slow_execution",
                duration_ms=metrics.duration * 1000,
                threshold_ms=30000
            )
```

## DEBUGGING STRATEGY

### Advanced Debugging Tools
```python
# backend/app/core/debugging.py
import pdb
import traceback
import inspect
import sys
from typing import Any, Dict, List, Optional
from functools import wraps
import structlog

class AdvancedDebugger:
    def __init__(self, environment: str):
        self.environment = environment
        self.logger = structlog.get_logger("debugger")
        self.debug_sessions = {}
        self.breakpoints = set()
        
    def debug_on_error(self, func):
        """Decorator that triggers debugger on exceptions"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if self.environment == "development":
                    await self.logger.aerror(
                        "exception_triggered_debug",
                        function=func.__name__,
                        exception=str(e),
                        traceback=traceback.format_exc()
                    )
                    
                    # Start interactive debugging session
                    pdb.post_mortem()
                raise
        return wrapper
    
    async def capture_execution_context(self, 
                                       function_name: str, 
                                       local_vars: Dict[str, Any], 
                                       call_stack: List[str]):
        """Capture detailed execution context for debugging"""
        context = {
            "function": function_name,
            "local_variables": self._serialize_variables(local_vars),
            "call_stack": call_stack,
            "system_state": {
                "memory_usage": psutil.Process().memory_info().rss / 1024 / 1024,
                "cpu_percent": psutil.cpu_percent(),
                "thread_count": psutil.Process().num_threads()
            }
        }
        
        await self.logger.adebug(
            "execution_context_captured",
            context=context
        )
        
        return context
    
    def _serialize_variables(self, variables: Dict[str, Any]) -> Dict[str, str]:
        """Safely serialize variables for logging"""
        serialized = {}
        for name, value in variables.items():
            try:
                if callable(value):
                    serialized[name] = f"<function {value.__name__}>"
                elif hasattr(value, '__dict__'):
                    serialized[name] = f"<object {type(value).__name__}>"
                else:
                    serialized[name] = str(value)[:200]  # Limit length
            except Exception:
                serialized[name] = "<unserializable>"
        
        return serialized

class ErrorAnalyzer:
    """Analyze and categorize errors for better debugging"""
    
    def __init__(self):
        self.logger = structlog.get_logger("error_analyzer")
        self.error_patterns = {
            "api_timeout": ["timeout", "connection timeout", "read timeout"],
            "rate_limit": ["rate limit", "quota exceeded", "too many requests"],
            "authentication": ["unauthorized", "invalid token", "authentication failed"],
            "data_validation": ["validation error", "invalid data", "schema error"],
            "resource_exhaustion": ["out of memory", "disk full", "connection pool exhausted"]
        }
    
    async def analyze_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze error and provide debugging insights"""
        error_msg = str(error).lower()
        error_type = type(error).__name__
        
        # Categorize error
        category = "unknown"
        for pattern_name, patterns in self.error_patterns.items():
            if any(pattern in error_msg for pattern in patterns):
                category = pattern_name
                break
        
        # Generate debugging suggestions
        suggestions = self._generate_debugging_suggestions(category, error_type, error_msg)
        
        analysis = {
            "error_type": error_type,
            "error_message": str(error),
            "category": category,
            "severity": self._assess_severity(category, error_type),
            "debugging_suggestions": suggestions,
            "context": context or {},
            "traceback": traceback.format_exc()
        }
        
        await self.logger.aerror(
            "error_analysis_completed",
            analysis=analysis
        )
        
        return analysis
    
    def _generate_debugging_suggestions(self, category: str, error_type: str, error_msg: str) -> List[str]:
        """Generate contextual debugging suggestions"""
        suggestions = []
        
        if category == "api_timeout":
            suggestions.extend([
                "Check network connectivity",
                "Verify API endpoint status",
                "Consider increasing timeout values",
                "Implement retry logic with exponential backoff"
            ])
        elif category == "rate_limit":
            suggestions.extend([
                "Implement request throttling",
                "Check API quota usage",
                "Consider using multiple API keys",
                "Add caching to reduce API calls"
            ])
        elif category == "data_validation":
            suggestions.extend([
                "Validate input data before processing",
                "Check data schema compatibility",
                "Implement data cleaning pipeline",
                "Add comprehensive input sanitization"
            ])
        
        return suggestions
    
    def _assess_severity(self, category: str, error_type: str) -> str:
        """Assess error severity"""
        critical_categories = ["resource_exhaustion", "authentication"]
        critical_types = ["SystemExit", "MemoryError", "KeyboardInterrupt"]
        
        if category in critical_categories or error_type in critical_types:
            return "critical"
        elif category in ["api_timeout", "rate_limit"]:
            return "high"
        else:
            return "medium"
```

## OBSERVABILITY & MONITORING

### Distributed Tracing
```python
# backend/app/core/tracing.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

def setup_tracing(service_name: str = "enterprise-insights-copilot"):
    """Setup distributed tracing"""
    
    # Configure tracer provider
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)
    
    # Configure Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name="localhost",
        agent_port=6831,
    )
    
    # Add span processor
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    # Instrument libraries
    FastAPIInstrumentor.instrument()
    RequestsInstrumentor.instrument()
    SQLAlchemyInstrumentor.instrument()
    
    return tracer

class WorkflowTracer:
    """Custom tracer for workflow operations"""
    
    def __init__(self, tracer):
        self.tracer = tracer
    
    async def trace_agent_execution(self, agent_name: str, input_data: Dict[str, Any]):
        """Trace agent execution with custom spans"""
        with self.tracer.start_as_current_span(f"agent.{agent_name}.execute") as span:
            span.set_attribute("agent.name", agent_name)
            span.set_attribute("agent.input.query", input_data.get("user_query", ""))
            span.set_attribute("agent.input.has_file_data", bool(input_data.get("file_data")))
            
            try:
                # Agent execution logic here
                yield span
                span.set_attribute("agent.status", "success")
            except Exception as e:
                span.set_attribute("agent.status", "error")
                span.set_attribute("agent.error", str(e))
                raise
```

### Metrics Collection
```python
# backend/app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Define metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

AGENT_EXECUTION_COUNT = Counter(
    'agent_executions_total',
    'Total agent executions',
    ['agent_name', 'status']
)

AGENT_EXECUTION_DURATION = Histogram(
    'agent_execution_duration_seconds',
    'Agent execution duration',
    ['agent_name']
)

WORKFLOW_STATE_GAUGE = Gauge(
    'workflow_active_count',
    'Number of active workflows',
    ['state']
)

LLM_TOKEN_USAGE = Counter(
    'llm_tokens_total',
    'Total LLM tokens used',
    ['provider', 'model', 'type']
)

class MetricsCollector:
    """Centralized metrics collection"""
    
    def __init__(self):
        # Start Prometheus metrics server
        start_http_server(8000)
    
    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record HTTP request metrics"""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_agent_execution(self, agent_name: str, status: str, duration: float):
        """Record agent execution metrics"""
        AGENT_EXECUTION_COUNT.labels(agent_name=agent_name, status=status).inc()
        AGENT_EXECUTION_DURATION.labels(agent_name=agent_name).observe(duration)
    
    def record_llm_usage(self, provider: str, model: str, token_type: str, count: int):
        """Record LLM token usage"""
        LLM_TOKEN_USAGE.labels(provider=provider, model=model, type=token_type).inc(count)
```

## DEVELOPMENT DEBUGGING TOOLS

### Interactive Debugging Dashboard
```python
# backend/app/debug/dashboard.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import json

debug_app = FastAPI()
templates = Jinja2Templates(directory="templates")

@debug_app.get("/debug", response_class=HTMLResponse)
async def debug_dashboard(request: Request):
    """Interactive debugging dashboard"""
    return templates.TemplateResponse("debug_dashboard.html", {
        "request": request,
        "active_sessions": get_active_sessions(),
        "recent_errors": get_recent_errors(),
        "performance_metrics": get_performance_summary()
    })

@debug_app.get("/debug/logs/{level}")
async def get_logs(level: str, limit: int = 100):
    """Get logs by level"""
    # Implementation to retrieve logs
    pass

@debug_app.get("/debug/trace/{trace_id}")
async def get_trace(trace_id: str):
    """Get distributed trace by ID"""
    # Implementation to retrieve trace data
    pass
```

This comprehensive logging and debugging strategy provides:

1. **Structured Logging**: JSON-formatted logs with context
2. **Performance Monitoring**: Detailed metrics and alerting
3. **Error Analysis**: Intelligent error categorization and suggestions
4. **Distributed Tracing**: Full request flow visibility
5. **Interactive Debugging**: Development-time debugging tools
6. **Production Observability**: Prometheus metrics and monitoring

The strategy enables rapid issue identification, performance optimization, and comprehensive system visibility essential for enterprise-grade applications.
