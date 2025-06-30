"""
Agent Error Handling and Retry Logic
Task 103: Add agent error handling and retry logic
"""

import asyncio
import logging
import traceback
from typing import Dict, List, Any, Optional, Callable, Type, Union
from datetime import datetime, timezone, timedelta
from enum import Enum
from dataclasses import dataclass, field
import random
import uuid

logger = logging.getLogger(__name__)


class ErrorSeverity(str, Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    """Error categories for classification"""
    NETWORK = "network"
    TIMEOUT = "timeout"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RATE_LIMIT = "rate_limit"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DATA_PROCESSING = "data_processing"
    LLM_ERROR = "llm_error"
    SYSTEM_ERROR = "system_error"
    USER_ERROR = "user_error"
    CONFIGURATION = "configuration"


class RetryStrategy(str, Enum):
    """Retry strategies"""
    NONE = "none"               # No retry
    IMMEDIATE = "immediate"     # Retry immediately
    LINEAR = "linear"           # Linear backoff
    EXPONENTIAL = "exponential" # Exponential backoff
    JITTER = "jitter"          # Exponential with jitter
    CUSTOM = "custom"          # Custom retry logic


@dataclass
class ErrorContext:
    """Context information for errors"""
    agent_id: str
    execution_id: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    task_name: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_multiplier: float = 2.0
    jitter: bool = True
    retry_on_exceptions: List[Type[Exception]] = field(default_factory=list)
    stop_on_exceptions: List[Type[Exception]] = field(default_factory=list)
    custom_retry_condition: Optional[Callable[[Exception, int], bool]] = None


class AgentError(Exception):
    """Base exception for agent errors"""
    
    def __init__(
        self, 
        message: str, 
        category: ErrorCategory = ErrorCategory.SYSTEM_ERROR,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[ErrorContext] = None,
        original_exception: Optional[Exception] = None,
        retry_after: Optional[float] = None
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.context = context
        self.original_exception = original_exception
        self.retry_after = retry_after
        self.error_id = str(uuid.uuid4())
        self.timestamp = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary"""
        return {
            "error_id": self.error_id,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "timestamp": self.timestamp.isoformat(),
            "retry_after": self.retry_after,
            "original_exception": str(self.original_exception) if self.original_exception else None,
            "context": self.context.__dict__ if self.context else None
        }


class ValidationError(AgentError):
    """Error for input validation failures"""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None, **kwargs):
        super().__init__(message, ErrorCategory.VALIDATION, ErrorSeverity.LOW, **kwargs)
        self.field = field
        self.value = value


class TimeoutError(AgentError):
    """Error for timeout situations"""
    
    def __init__(self, message: str, timeout_duration: Optional[float] = None, **kwargs):
        super().__init__(message, ErrorCategory.TIMEOUT, ErrorSeverity.MEDIUM, **kwargs)
        self.timeout_duration = timeout_duration


class RateLimitError(AgentError):
    """Error for rate limiting"""
    
    def __init__(self, message: str, retry_after: float = 60.0, **kwargs):
        super().__init__(message, ErrorCategory.RATE_LIMIT, ErrorSeverity.MEDIUM, 
                        retry_after=retry_after, **kwargs)


class ResourceExhaustionError(AgentError):
    """Error for resource exhaustion"""
    
    def __init__(self, message: str, resource_type: Optional[str] = None, **kwargs):
        super().__init__(message, ErrorCategory.RESOURCE_EXHAUSTION, ErrorSeverity.HIGH, **kwargs)
        self.resource_type = resource_type


class LLMError(AgentError):
    """Error for LLM-related issues"""
    
    def __init__(self, message: str, model_name: Optional[str] = None, **kwargs):
        super().__init__(message, ErrorCategory.LLM_ERROR, ErrorSeverity.MEDIUM, **kwargs)
        self.model_name = model_name


class RetryAttempt:
    """Information about a retry attempt"""
    
    def __init__(self, attempt_number: int, delay: float, error: Exception):
        self.attempt_number = attempt_number
        self.delay = delay
        self.error = error
        self.timestamp = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "attempt_number": self.attempt_number,
            "delay": self.delay,
            "error": str(self.error),
            "timestamp": self.timestamp.isoformat()
        }


class ErrorHandler:
    """Handles error classification, logging, and recovery"""
    
    def __init__(self):
        self.error_handlers: Dict[ErrorCategory, Callable] = {}
        self.error_statistics: Dict[str, int] = {}
        self.recent_errors: List[AgentError] = []
        self.max_recent_errors = 100
        self.circuit_breakers: Dict[str, 'CircuitBreaker'] = {}
    
    def register_handler(self, category: ErrorCategory, handler: Callable):
        """Register error handler for specific category"""
        self.error_handlers[category] = handler
    
    async def handle_error(self, error: Exception, context: ErrorContext) -> Optional[Any]:
        """Handle an error with appropriate strategy"""
        # Convert to AgentError if needed
        if not isinstance(error, AgentError):
            agent_error = self._classify_error(error, context)
        else:
            agent_error = error
            if agent_error.context is None:
                agent_error.context = context
        
        # Log the error
        self._log_error(agent_error)
        
        # Update statistics
        self._update_statistics(agent_error)
        
        # Store recent error
        self._store_recent_error(agent_error)
        
        # Run category-specific handler
        handler = self.error_handlers.get(agent_error.category)
        if handler:
            try:
                return await handler(agent_error)
            except Exception as e:
                logger.error(f"Error handler failed: {e}")
        
        return None
    
    def _classify_error(self, error: Exception, context: ErrorContext) -> AgentError:
        """Classify error into appropriate category"""
        error_msg = str(error)
        
        # Classification rules
        if isinstance(error, asyncio.TimeoutError):
            return TimeoutError(f"Operation timed out: {error_msg}", context=context)
        
        elif "rate limit" in error_msg.lower():
            return RateLimitError(f"Rate limit exceeded: {error_msg}", context=context)
        
        elif "network" in error_msg.lower() or "connection" in error_msg.lower():
            return AgentError(error_msg, ErrorCategory.NETWORK, ErrorSeverity.MEDIUM, context=context)
        
        elif "memory" in error_msg.lower() or "resource" in error_msg.lower():
            return ResourceExhaustionError(f"Resource exhausted: {error_msg}", context=context)
        
        elif "validation" in error_msg.lower() or "invalid" in error_msg.lower():
            return ValidationError(f"Validation failed: {error_msg}", context=context)
        
        elif "auth" in error_msg.lower():
            return AgentError(error_msg, ErrorCategory.AUTHENTICATION, ErrorSeverity.HIGH, context=context)
        
        else:
            return AgentError(error_msg, ErrorCategory.SYSTEM_ERROR, ErrorSeverity.MEDIUM, 
                            context=context, original_exception=error)
    
    def _log_error(self, error: AgentError):
        """Log error with appropriate level"""
        log_data = {
            "error_id": error.error_id,
            "category": error.category.value,
            "severity": error.severity.value,
            "agent_id": error.context.agent_id if error.context else "unknown",
            "execution_id": error.context.execution_id if error.context else "unknown"
        }
        
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(f"Critical error: {error.message}", extra=log_data)
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(f"High severity error: {error.message}", extra=log_data)
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"Medium severity error: {error.message}", extra=log_data)
        else:
            logger.info(f"Low severity error: {error.message}", extra=log_data)
    
    def _update_statistics(self, error: AgentError):
        """Update error statistics"""
        key = f"{error.category.value}:{error.severity.value}"
        self.error_statistics[key] = self.error_statistics.get(key, 0) + 1
    
    def _store_recent_error(self, error: AgentError):
        """Store error in recent errors list"""
        self.recent_errors.append(error)
        if len(self.recent_errors) > self.max_recent_errors:
            self.recent_errors.pop(0)
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        total_errors = sum(self.error_statistics.values())
        return {
            "total_errors": total_errors,
            "error_breakdown": self.error_statistics.copy(),
            "recent_error_count": len(self.recent_errors),
            "circuit_breaker_count": len(self.circuit_breakers)
        }
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent errors"""
        return [error.to_dict() for error in self.recent_errors[-limit:]]


class RetryManager:
    """Manages retry logic for failed operations"""
    
    def __init__(self, default_config: Optional[RetryConfig] = None):
        self.default_config = default_config or RetryConfig()
        self.retry_histories: Dict[str, List[RetryAttempt]] = {}
    
    async def execute_with_retry(
        self, 
        operation: Callable,
        context: ErrorContext,
        config: Optional[RetryConfig] = None,
        *args,
        **kwargs
    ) -> Any:
        """Execute operation with retry logic"""
        retry_config = config or self.default_config
        
        if retry_config.strategy == RetryStrategy.NONE:
            return await self._execute_operation(operation, *args, **kwargs)
        
        last_exception = None
        retry_history = []
        
        for attempt in range(retry_config.max_attempts):
            try:
                if attempt > 0:
                    delay = self._calculate_delay(attempt, retry_config)
                    logger.info(f"Retrying operation after {delay:.2f}s (attempt {attempt + 1}/{retry_config.max_attempts})")
                    await asyncio.sleep(delay)
                
                result = await self._execute_operation(operation, *args, **kwargs)
                
                # Success - log retry history if there were previous failures
                if retry_history:
                    self.retry_histories[context.execution_id] = retry_history
                    logger.info(f"Operation succeeded after {attempt + 1} attempts")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # Record retry attempt
                delay = self._calculate_delay(attempt + 1, retry_config) if attempt < retry_config.max_attempts - 1 else 0
                retry_attempt = RetryAttempt(attempt + 1, delay, e)
                retry_history.append(retry_attempt)
                
                # Check if we should stop retrying
                if not self._should_retry(e, attempt + 1, retry_config):
                    break
                
                # Log retry attempt
                logger.warning(f"Operation failed (attempt {attempt + 1}/{retry_config.max_attempts}): {e}")
        
        # All retries exhausted
        self.retry_histories[context.execution_id] = retry_history
        logger.error(f"Operation failed after {retry_config.max_attempts} attempts")
        
        # Raise the last exception
        if isinstance(last_exception, AgentError):
            raise last_exception
        else:
            raise AgentError(
                f"Operation failed after {retry_config.max_attempts} attempts: {last_exception}",
                context=context,
                original_exception=last_exception
            )
    
    async def _execute_operation(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute the operation (async or sync)"""
        if asyncio.iscoroutinefunction(operation):
            return await operation(*args, **kwargs)
        else:
            return operation(*args, **kwargs)
    
    def _calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """Calculate delay for retry attempt"""
        if config.strategy == RetryStrategy.IMMEDIATE:
            delay = 0
        elif config.strategy == RetryStrategy.LINEAR:
            delay = config.base_delay * attempt
        elif config.strategy == RetryStrategy.EXPONENTIAL:
            delay = config.base_delay * (config.backoff_multiplier ** (attempt - 1))
        elif config.strategy == RetryStrategy.JITTER:
            exponential_delay = config.base_delay * (config.backoff_multiplier ** (attempt - 1))
            jitter_range = exponential_delay * 0.1  # 10% jitter
            delay = exponential_delay + random.uniform(-jitter_range, jitter_range)
        else:
            delay = config.base_delay
        
        # Apply max delay limit
        delay = min(delay, config.max_delay)
        
        # Add small random jitter if enabled
        if config.jitter and config.strategy != RetryStrategy.JITTER:
            jitter = delay * 0.05 * random.random()  # 5% jitter
            delay += jitter
        
        return max(0, delay)
    
    def _should_retry(self, exception: Exception, attempt: int, config: RetryConfig) -> bool:
        """Determine if we should retry after this exception"""
        # Check if we've exceeded max attempts
        if attempt >= config.max_attempts:
            return False
        
        # Check stop conditions
        if config.stop_on_exceptions:
            for stop_exception in config.stop_on_exceptions:
                if isinstance(exception, stop_exception):
                    return False
        
        # Check retry conditions
        if config.retry_on_exceptions:
            for retry_exception in config.retry_on_exceptions:
                if isinstance(exception, retry_exception):
                    return True
            return False  # If specific exceptions are listed, only retry on those
        
        # Check custom retry condition
        if config.custom_retry_condition:
            return config.custom_retry_condition(exception, attempt)
        
        # Default behavior - retry on most exceptions except validation errors
        if isinstance(exception, ValidationError):
            return False
        
        return True
    
    def get_retry_history(self, execution_id: str) -> List[Dict[str, Any]]:
        """Get retry history for an execution"""
        history = self.retry_histories.get(execution_id, [])
        return [attempt.to_dict() for attempt in history]


class CircuitBreaker:
    """Circuit breaker pattern for preventing cascading failures"""
    
    def __init__(
        self, 
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half-open
    
    async def call(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute operation through circuit breaker"""
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half-open"
            else:
                raise AgentError(
                    f"Circuit breaker is open. Recovery timeout: {self.recovery_timeout}s",
                    ErrorCategory.SYSTEM_ERROR,
                    ErrorSeverity.HIGH
                )
        
        try:
            result = await self._execute_operation(operation, *args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    async def _execute_operation(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute the operation"""
        if asyncio.iscoroutinefunction(operation):
            return await operation(*args, **kwargs)
        else:
            return operation(*args, **kwargs)
    
    def _on_success(self):
        """Handle successful operation"""
        self.failure_count = 0
        self.state = "closed"
    
    def _on_failure(self):
        """Handle failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.now(timezone.utc)
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit breaker"""
        if self.last_failure_time is None:
            return True
        
        elapsed = (datetime.now(timezone.utc) - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout
    
    def get_state(self) -> Dict[str, Any]:
        """Get circuit breaker state"""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "recovery_timeout": self.recovery_timeout
        }


# Global instances
_error_handler = ErrorHandler()
_retry_manager = RetryManager()


def get_error_handler() -> ErrorHandler:
    """Get global error handler"""
    return _error_handler


def get_retry_manager() -> RetryManager:
    """Get global retry manager"""
    return _retry_manager


# Decorators for easy use


def with_retry(config: Optional[RetryConfig] = None):
    """Decorator for adding retry logic to functions"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            context = ErrorContext(
                agent_id=kwargs.get('agent_id', 'unknown'),
                execution_id=kwargs.get('execution_id', str(uuid.uuid4()))
            )
            
            retry_manager = get_retry_manager()
            return await retry_manager.execute_with_retry(func, context, config, *args, **kwargs)
        
        return wrapper
    return decorator


def with_circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    expected_exception: Type[Exception] = Exception
):
    """Decorator for adding circuit breaker to functions"""
    circuit_breaker = CircuitBreaker(failure_threshold, recovery_timeout, expected_exception)
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await circuit_breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator


def handle_errors(func):
    """Decorator for automatic error handling"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            context = ErrorContext(
                agent_id=kwargs.get('agent_id', 'unknown'),
                execution_id=kwargs.get('execution_id', str(uuid.uuid4()))
            )
            
            error_handler = get_error_handler()
            await error_handler.handle_error(e, context)
            raise
    
    return wrapper
