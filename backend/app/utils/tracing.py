"""
OpenTelemetry configuration for distributed tracing
Provides end-to-end request tracing across the application.
"""

import os
import time
from typing import Dict, Any, Optional
from functools import wraps

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION


class TracingConfig:
    """Configuration for OpenTelemetry tracing."""
    
    def __init__(self):
        self.service_name = "enterprise-insights-backend"
        self.service_version = "1.0.0"
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.jaeger_endpoint = os.getenv("JAEGER_ENDPOINT", "http://localhost:14268/api/traces")
        self.otlp_endpoint = os.getenv("OTLP_ENDPOINT", "http://localhost:4317")
        self.enable_console_export = os.getenv("TRACE_CONSOLE_EXPORT", "false").lower() == "true"
        
    def setup_tracing(self):
        """Initialize OpenTelemetry tracing."""
        # Create resource with service information
        resource = Resource.create({
            SERVICE_NAME: self.service_name,
            SERVICE_VERSION: self.service_version,
            "environment": self.environment,
            "component": "backend"
        })
        
        # Create tracer provider
        tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(tracer_provider)
        
        # Configure exporters
        self._setup_exporters(tracer_provider)
        
        # Setup auto-instrumentation
        self._setup_instrumentation()
        
        return trace.get_tracer(self.service_name)
    
    def _setup_exporters(self, tracer_provider: TracerProvider):
        """Setup trace exporters."""
        # Console exporter for development
        if self.enable_console_export:
            console_exporter = ConsoleSpanExporter()
            console_processor = BatchSpanProcessor(console_exporter)
            tracer_provider.add_span_processor(console_processor)
        
        # Jaeger exporter
        try:
            jaeger_exporter = JaegerExporter(
                agent_host_name="localhost",
                agent_port=6831,
                collector_endpoint=self.jaeger_endpoint,
            )
            jaeger_processor = BatchSpanProcessor(jaeger_exporter)
            tracer_provider.add_span_processor(jaeger_processor)
        except Exception as e:
            print(f"Failed to setup Jaeger exporter: {e}")
        
        # OTLP exporter (for other observability platforms)
        try:
            otlp_exporter = OTLPSpanExporter(endpoint=self.otlp_endpoint)
            otlp_processor = BatchSpanProcessor(otlp_exporter)
            tracer_provider.add_span_processor(otlp_processor)
        except Exception as e:
            print(f"Failed to setup OTLP exporter: {e}")
    
    def _setup_instrumentation(self):
        """Setup automatic instrumentation for common libraries."""
        # FastAPI instrumentation
        FastAPIInstrumentor().instrument()
        
        # HTTP requests instrumentation
        RequestsInstrumentor().instrument()
        
        # Database instrumentation
        try:
            SQLAlchemyInstrumentor().instrument()
        except Exception as e:
            print(f"Failed to setup SQLAlchemy instrumentation: {e}")
        
        # Redis instrumentation
        try:
            RedisInstrumentor().instrument()
        except Exception as e:
            print(f"Failed to setup Redis instrumentation: {e}")


class CustomTracer:
    """Custom tracer with convenience methods."""
    
    def __init__(self, tracer_name: str = "enterprise-insights"):
        self.tracer = trace.get_tracer(tracer_name)
    
    def start_span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Start a new span with optional attributes."""
        span = self.tracer.start_span(name)
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, str(value))
        return span
    
    def add_event(self, span, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Add an event to a span."""
        if attributes:
            span.add_event(name, attributes)
        else:
            span.add_event(name)
    
    def set_error(self, span, error: Exception):
        """Mark a span as having an error."""
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(error)))
        span.set_attribute("error.type", error.__class__.__name__)
        span.set_attribute("error.message", str(error))
    
    def trace_function(self, span_name: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None):
        """Decorator to trace function execution."""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                name = span_name or f"{func.__module__}.{func.__name__}"
                
                with self.tracer.start_as_current_span(name) as span:
                    # Add function attributes
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)
                    
                    # Add custom attributes
                    if attributes:
                        for key, value in attributes.items():
                            span.set_attribute(key, str(value))
                    
                    try:
                        result = await func(*args, **kwargs)
                        span.set_status(trace.Status(trace.StatusCode.OK))
                        return result
                    except Exception as e:
                        self.set_error(span, e)
                        raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                name = span_name or f"{func.__module__}.{func.__name__}"
                
                with self.tracer.start_as_current_span(name) as span:
                    # Add function attributes
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)
                    
                    # Add custom attributes
                    if attributes:
                        for key, value in attributes.items():
                            span.set_attribute(key, str(value))
                    
                    try:
                        result = func(*args, **kwargs)
                        span.set_status(trace.Status(trace.StatusCode.OK))
                        return result
                    except Exception as e:
                        self.set_error(span, e)
                        raise
            
            return async_wrapper if 'async' in func.__code__.co_flags.__str__() else sync_wrapper
        return decorator


# Global tracing configuration
tracing_config = TracingConfig()
tracer = None


def initialize_tracing():
    """Initialize the tracing system."""
    global tracer
    tracer = tracing_config.setup_tracing()
    return CustomTracer()


def get_tracer() -> CustomTracer:
    """Get the global tracer instance."""
    if tracer is None:
        return initialize_tracing()
    return CustomTracer()


# Convenience decorators
def trace_agent_execution(agent_type: str):
    """Decorator specifically for tracing agent executions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            custom_tracer = get_tracer()
            
            with custom_tracer.tracer.start_as_current_span(f"agent.{agent_type}.execute") as span:
                span.set_attribute("agent.type", agent_type)
                span.set_attribute("agent.function", func.__name__)
                
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    
                    execution_time = time.time() - start_time
                    span.set_attribute("agent.execution_time", execution_time)
                    span.set_attribute("agent.status", "success")
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    
                    return result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    span.set_attribute("agent.execution_time", execution_time)
                    span.set_attribute("agent.status", "error")
                    custom_tracer.set_error(span, e)
                    raise
        
        return wrapper
    return decorator


def trace_data_processing(processing_type: str):
    """Decorator specifically for tracing data processing operations."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            custom_tracer = get_tracer()
            
            with custom_tracer.tracer.start_as_current_span(f"data.{processing_type}.process") as span:
                span.set_attribute("data.processing_type", processing_type)
                span.set_attribute("data.function", func.__name__)
                
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    
                    processing_time = time.time() - start_time
                    span.set_attribute("data.processing_time", processing_time)
                    span.set_attribute("data.status", "success")
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    
                    return result
                    
                except Exception as e:
                    processing_time = time.time() - start_time
                    span.set_attribute("data.processing_time", processing_time)
                    span.set_attribute("data.status", "error")
                    custom_tracer.set_error(span, e)
                    raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            custom_tracer = get_tracer()
            
            with custom_tracer.tracer.start_as_current_span(f"data.{processing_type}.process") as span:
                span.set_attribute("data.processing_type", processing_type)
                span.set_attribute("data.function", func.__name__)
                
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    
                    processing_time = time.time() - start_time
                    span.set_attribute("data.processing_time", processing_time)
                    span.set_attribute("data.status", "success")
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    
                    return result
                    
                except Exception as e:
                    processing_time = time.time() - start_time
                    span.set_attribute("data.processing_time", processing_time)
                    span.set_attribute("data.status", "error")
                    custom_tracer.set_error(span, e)
                    raise
        
        return async_wrapper if 'async' in func.__code__.co_flags.__str__() else sync_wrapper
    return decorator
