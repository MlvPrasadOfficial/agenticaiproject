"""
Structured logging configuration for Enterprise Insights Copilot
Provides consistent, contextual logging across the application.
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional
import traceback
from functools import wraps
import uuid


class StructuredLogger:
    """Structured logger with context management and JSON formatting."""
    
    def __init__(self, name: str = "enterprise_insights"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create console handler with JSON formatter
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)
        
        # Context storage for request/session tracking
        self.context = {}
    
    def set_context(self, **kwargs):
        """Set context variables for all subsequent log entries."""
        self.context.update(kwargs)
    
    def clear_context(self):
        """Clear all context variables.""" 
        self.context.clear()
    
    def _format_message(self, level: str, message: str, **kwargs) -> Dict[str, Any]:
        """Format log message with context and metadata."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "message": message,
            "service": "enterprise-insights-backend",
            "version": "1.0.0",
            **self.context,
            **kwargs
        }
        
        # Add trace ID if not present
        if "trace_id" not in log_entry:
            log_entry["trace_id"] = str(uuid.uuid4())
            
        return log_entry
    
    def info(self, message: str, **kwargs):
        """Log info level message."""
        log_data = self._format_message("INFO", message, **kwargs)
        self.logger.info(json.dumps(log_data))
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log error level message with optional exception details."""
        error_data = {}
        if error:
            error_data = {
                "error_type": error.__class__.__name__,
                "error_message": str(error),
                "stack_trace": traceback.format_exc()
            }
        
        log_data = self._format_message("ERROR", message, **error_data, **kwargs)
        self.logger.error(json.dumps(log_data))
    
    def warning(self, message: str, **kwargs):
        """Log warning level message."""
        log_data = self._format_message("WARNING", message, **kwargs)
        self.logger.warning(json.dumps(log_data))
    
    def debug(self, message: str, **kwargs):
        """Log debug level message."""
        log_data = self._format_message("DEBUG", message, **kwargs)
        self.logger.debug(json.dumps(log_data))


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for log records."""
    
    def format(self, record):
        # If the message is already JSON, return it as-is
        try:
            json.loads(record.getMessage())
            return record.getMessage()
        except (json.JSONDecodeError, ValueError):
            # If not JSON, create a structured log entry
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": record.levelname,
                "message": record.getMessage(),
                "logger": record.name,
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
            
            if record.exc_info:
                log_entry["exception"] = self.formatException(record.exc_info)
                
            return json.dumps(log_entry)


def log_execution_time(logger: StructuredLogger):
    """Decorator to log function execution time."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            function_id = str(uuid.uuid4())
            
            logger.info(
                f"Starting execution of {func.__name__}",
                function_name=func.__name__,
                function_id=function_id,
                execution_phase="start"
            )
            
            try:
                result = await func(*args, **kwargs)
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                logger.info(
                    f"Completed execution of {func.__name__}",
                    function_name=func.__name__,
                    function_id=function_id,
                    execution_time_seconds=execution_time,
                    execution_phase="complete",
                    status="success"
                )
                
                return result
                
            except Exception as e:
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                logger.error(
                    f"Failed execution of {func.__name__}",
                    error=e,
                    function_name=func.__name__,
                    function_id=function_id,
                    execution_time_seconds=execution_time,
                    execution_phase="error",
                    status="failed"
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            function_id = str(uuid.uuid4())
            
            logger.info(
                f"Starting execution of {func.__name__}",
                function_name=func.__name__,
                function_id=function_id,
                execution_phase="start"
            )
            
            try:
                result = func(*args, **kwargs)
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                logger.info(
                    f"Completed execution of {func.__name__}",
                    function_name=func.__name__,
                    function_id=function_id,
                    execution_time_seconds=execution_time,
                    execution_phase="complete",
                    status="success"
                )
                
                return result
                
            except Exception as e:
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                logger.error(
                    f"Failed execution of {func.__name__}",
                    error=e,
                    function_name=func.__name__,
                    function_id=function_id,
                    execution_time_seconds=execution_time,
                    execution_phase="error",
                    status="failed"
                )
                raise
        
        return async_wrapper if 'async' in func.__code__.co_flags.__str__() else sync_wrapper
    return decorator


# Global logger instance
structured_logger = StructuredLogger()


def get_logger() -> StructuredLogger:
    """Get the global structured logger instance."""
    return structured_logger
