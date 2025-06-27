"""
Enterprise Insights Copilot - Comprehensive Logging System
MAANG-level structured JSON logging with correlation IDs and observability
"""

import sys
import logging
import structlog
from pathlib import Path
from typing import Any, Dict, Optional
from contextvars import ContextVar
from datetime import datetime
import json
import traceback
import uuid

from app.core.config import settings

# Context variables for request correlation
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)


class CorrelationIDProcessor:
    """Add correlation IDs to log records"""
    
    def __call__(self, logger, method_name, event_dict):
        request_id = request_id_var.get()
        user_id = user_id_var.get()
        
        if request_id:
            event_dict["request_id"] = request_id
        if user_id:
            event_dict["user_id"] = user_id
            
        return event_dict


class TimestampProcessor:
    """Add ISO timestamp to log records"""
    
    def __call__(self, logger, method_name, event_dict):
        event_dict["timestamp"] = datetime.utcnow().isoformat() + "Z"
        return event_dict


class ServiceInfoProcessor:
    """Add service information to log records"""
    
    def __call__(self, logger, method_name, event_dict):
        event_dict.update({
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "level": method_name.upper()
        })
        return event_dict


class ExceptionProcessor:
    """Process exceptions for better logging"""
    
    def __call__(self, logger, method_name, event_dict):
        exc_info = event_dict.pop("exc_info", None)
        if exc_info:
            if exc_info is True:
                exc_info = sys.exc_info()
            
            if exc_info and exc_info[0] is not None:
                event_dict["exception"] = {
                    "type": exc_info[0].__name__,
                    "message": str(exc_info[1]),
                    "traceback": traceback.format_exception(*exc_info)
                }
        
        return event_dict


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for standard library logging"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add correlation IDs if available
        request_id = request_id_var.get()
        user_id = user_id_var.get()
        
        if request_id:
            log_entry["request_id"] = request_id
        if user_id:
            log_entry["user_id"] = user_id
        
        # Add exception information
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "message"
            }:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


def setup_logging():
    """Set up comprehensive logging configuration"""
    
    # Ensure log directory exists
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        TimestampProcessor(),
        ServiceInfoProcessor(),
        CorrelationIDProcessor(),
        ExceptionProcessor(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if settings.LOG_FORMAT == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.extend([
            structlog.dev.ConsoleRenderer(colors=True),
        ])
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(settings.LOG_FILE),
        ],
        format="%(message)s" if settings.LOG_FORMAT == "json" else 
               "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Apply JSON formatter if needed
    if settings.LOG_FORMAT == "json":
        json_formatter = JSONFormatter()
        for handler in logging.root.handlers:
            handler.setFormatter(json_formatter)
    
    # Set specific logger levels
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    # Suppress noisy third-party loggers in production
    if settings.is_production:
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get a configured logger instance"""
    return structlog.get_logger(name)


def set_request_id(request_id: str = None) -> str:
    """Set request ID in context"""
    if request_id is None:
        request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    return request_id


def set_user_id(user_id: str) -> None:
    """Set user ID in context"""
    user_id_var.set(user_id)


def get_request_id() -> Optional[str]:
    """Get current request ID from context"""
    return request_id_var.get()


def get_user_id() -> Optional[str]:
    """Get current user ID from context"""
    return user_id_var.get()


def log_performance(func_name: str, duration: float, **kwargs) -> None:
    """Log performance metrics"""
    logger = get_logger("performance")
    logger.info(
        "Performance metric",
        function=func_name,
        duration_ms=round(duration * 1000, 2),
        **kwargs
    )


def log_business_event(event_type: str, **kwargs) -> None:
    """Log business events for analytics"""
    logger = get_logger("business")
    logger.info(
        "Business event",
        event_type=event_type,
        **kwargs
    )


def log_security_event(event_type: str, severity: str = "info", **kwargs) -> None:
    """Log security-related events"""
    logger = get_logger("security")
    log_func = getattr(logger, severity.lower(), logger.info)
    log_func(
        "Security event",
        event_type=event_type,
        severity=severity,
        **kwargs
    )


def log_agent_activity(agent_name: str, activity: str, **kwargs) -> None:
    """Log AI agent activities"""
    logger = get_logger("agents")
    logger.info(
        "Agent activity",
        agent_name=agent_name,
        activity=activity,
        **kwargs
    )


# Create global logger instance
logger = get_logger(__name__)
