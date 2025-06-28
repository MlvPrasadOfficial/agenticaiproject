"""
Performance monitoring decorators and utilities
Provides comprehensive performance tracking for the application.
"""

import time
import psutil
import asyncio
import functools
from typing import Dict, Any, Callable, Optional, List
from datetime import datetime
import threading
from contextlib import contextmanager
from app.utils.logging import get_logger
from app.utils.metrics import metrics
from app.utils.business_metrics import business_metrics


class PerformanceMonitor:
    """Performance monitoring and tracking utilities."""
    
    def __init__(self):
        self.logger = get_logger()
        self.active_operations = {}
        self.performance_history = []
        self.lock = threading.Lock()
    
    def start_operation(self, operation_id: str, operation_name: str, metadata: Dict[str, Any] = None):
        """Start tracking a performance operation."""
        with self.lock:
            self.active_operations[operation_id] = {
                "name": operation_name,
                "start_time": time.time(),
                "start_memory": psutil.Process().memory_info().rss,
                "metadata": metadata or {}
            }
    
    def end_operation(self, operation_id: str, result_metadata: Dict[str, Any] = None):
        """End tracking a performance operation."""
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        with self.lock:
            if operation_id not in self.active_operations:
                return None
            
            operation = self.active_operations.pop(operation_id)
            
            performance_data = {
                "operation_id": operation_id,
                "operation_name": operation["name"],
                "duration_seconds": end_time - operation["start_time"],
                "memory_delta_bytes": end_memory - operation["start_memory"],
                "start_time": operation["start_time"],
                "end_time": end_time,
                "metadata": operation["metadata"],
                "result_metadata": result_metadata or {}
            }
            
            # Store in history (keep last 1000 operations)
            self.performance_history.append(performance_data)
            if len(self.performance_history) > 1000:
                self.performance_history.pop(0)
            
            return performance_data
    
    def get_performance_summary(self, operation_name: Optional[str] = None, last_n: int = 100) -> Dict[str, Any]:
        """Get performance summary for operations."""
        with self.lock:
            history = self.performance_history.copy()
        
        if operation_name:
            history = [op for op in history if op["operation_name"] == operation_name]
        
        # Get last N operations
        history = history[-last_n:]
        
        if not history:
            return {"message": "No performance data available"}
        
        durations = [op["duration_seconds"] for op in history]
        memory_deltas = [op["memory_delta_bytes"] for op in history]
        
        return {
            "operation_count": len(history),
            "average_duration_seconds": sum(durations) / len(durations),
            "max_duration_seconds": max(durations),
            "min_duration_seconds": min(durations),
            "average_memory_delta_bytes": sum(memory_deltas) / len(memory_deltas),
            "max_memory_delta_bytes": max(memory_deltas),
            "operation_name": operation_name,
            "generated_at": datetime.utcnow().isoformat()
        }


# Global performance monitor
performance_monitor = PerformanceMonitor()


def monitor_performance(operation_name: str = None, track_memory: bool = True, track_cpu: bool = False):
    """Decorator to monitor function performance."""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            operation_id = f"{func.__name__}_{int(time.time() * 1000000)}"
            actual_operation_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            # Get initial system metrics
            start_metrics = {}
            if track_memory:
                start_metrics["memory_rss"] = psutil.Process().memory_info().rss
                start_metrics["memory_vms"] = psutil.Process().memory_info().vms
            
            if track_cpu:
                start_metrics["cpu_percent"] = psutil.Process().cpu_percent()
            
            # Start performance tracking
            performance_monitor.start_operation(
                operation_id, 
                actual_operation_name, 
                {"function_args_count": len(args), "function_kwargs_count": len(kwargs)}
            )
            
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Calculate final metrics
                end_time = time.time()
                duration = end_time - start_time
                
                end_metrics = {}
                if track_memory:
                    end_memory = psutil.Process().memory_info()
                    end_metrics["memory_rss"] = end_memory.rss
                    end_metrics["memory_vms"] = end_memory.vms
                    end_metrics["memory_delta_rss"] = end_memory.rss - start_metrics["memory_rss"]
                
                if track_cpu:
                    end_metrics["cpu_percent"] = psutil.Process().cpu_percent()
                
                # Record metrics
                metrics.record_data_processing(actual_operation_name, duration)
                
                # Log performance data
                performance_monitor.logger.info(
                    f"Performance monitoring: {actual_operation_name}",
                    operation_name=actual_operation_name,
                    duration_seconds=duration,
                    start_metrics=start_metrics,
                    end_metrics=end_metrics,
                    performance_category="function_execution"
                )
                
                # End performance tracking
                performance_monitor.end_operation(operation_id, {
                    "status": "success",
                    "result_type": type(result).__name__,
                    **end_metrics
                })
                
                return result
                
            except Exception as e:
                # Calculate error metrics
                end_time = time.time()
                duration = end_time - start_time
                
                # Record error metrics
                metrics.record_error(e.__class__.__name__, actual_operation_name)
                
                # Log error with performance context
                performance_monitor.logger.error(
                    f"Performance monitoring error: {actual_operation_name}",
                    error=e,
                    operation_name=actual_operation_name,
                    duration_seconds=duration,
                    performance_category="function_error"
                )
                
                # End performance tracking with error
                performance_monitor.end_operation(operation_id, {
                    "status": "error",
                    "error_type": e.__class__.__name__,
                    "error_message": str(e)
                })
                
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            operation_id = f"{func.__name__}_{int(time.time() * 1000000)}"
            actual_operation_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            # Get initial system metrics
            start_metrics = {}
            if track_memory:
                start_metrics["memory_rss"] = psutil.Process().memory_info().rss
                start_metrics["memory_vms"] = psutil.Process().memory_info().vms
            
            if track_cpu:
                start_metrics["cpu_percent"] = psutil.Process().cpu_percent()
            
            # Start performance tracking
            performance_monitor.start_operation(
                operation_id, 
                actual_operation_name, 
                {"function_args_count": len(args), "function_kwargs_count": len(kwargs)}
            )
            
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # Calculate final metrics
                end_time = time.time()
                duration = end_time - start_time
                
                end_metrics = {}
                if track_memory:
                    end_memory = psutil.Process().memory_info()
                    end_metrics["memory_rss"] = end_memory.rss
                    end_metrics["memory_vms"] = end_memory.vms
                    end_metrics["memory_delta_rss"] = end_memory.rss - start_metrics["memory_rss"]
                
                if track_cpu:
                    end_metrics["cpu_percent"] = psutil.Process().cpu_percent()
                
                # Record metrics
                metrics.record_data_processing(actual_operation_name, duration)
                
                # Log performance data
                performance_monitor.logger.info(
                    f"Performance monitoring: {actual_operation_name}",
                    operation_name=actual_operation_name,
                    duration_seconds=duration,
                    start_metrics=start_metrics,
                    end_metrics=end_metrics,
                    performance_category="function_execution"
                )
                
                # End performance tracking
                performance_monitor.end_operation(operation_id, {
                    "status": "success",
                    "result_type": type(result).__name__,
                    **end_metrics
                })
                
                return result
                
            except Exception as e:
                # Calculate error metrics
                end_time = time.time()
                duration = end_time - start_time
                
                # Record error metrics
                metrics.record_error(e.__class__.__name__, actual_operation_name)
                
                # Log error with performance context
                performance_monitor.logger.error(
                    f"Performance monitoring error: {actual_operation_name}",
                    error=e,
                    operation_name=actual_operation_name,
                    duration_seconds=duration,
                    performance_category="function_error"
                )
                
                # End performance tracking with error
                performance_monitor.end_operation(operation_id, {
                    "status": "error",
                    "error_type": e.__class__.__name__,
                    "error_message": str(e)
                })
                
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


@contextmanager
def performance_context(operation_name: str, metadata: Dict[str, Any] = None):
    """Context manager for performance monitoring."""
    operation_id = f"{operation_name}_{int(time.time() * 1000000)}"
    
    # Start monitoring
    performance_monitor.start_operation(operation_id, operation_name, metadata)
    start_time = time.time()
    
    try:
        yield operation_id
        
        # Success case
        duration = time.time() - start_time
        metrics.record_data_processing(operation_name, duration)
        
        performance_monitor.end_operation(operation_id, {"status": "success"})
        
    except Exception as e:
        # Error case
        duration = time.time() - start_time
        metrics.record_error(e.__class__.__name__, operation_name)
        
        performance_monitor.end_operation(operation_id, {
            "status": "error",
            "error_type": e.__class__.__name__
        })
        
        raise


class PerformanceBenchmark:
    """Performance benchmarking utilities."""
    
    @staticmethod
    async def benchmark_function(func: Callable, iterations: int = 100, *args, **kwargs) -> Dict[str, Any]:
        """Benchmark a function over multiple iterations."""
        durations = []
        memory_usage = []
        
        for i in range(iterations):
            start_memory = psutil.Process().memory_info().rss
            start_time = time.time()
            
            try:
                if asyncio.iscoroutinefunction(func):
                    await func(*args, **kwargs)
                else:
                    func(*args, **kwargs)
                    
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss
                
                durations.append(end_time - start_time)
                memory_usage.append(end_memory - start_memory)
                
            except Exception as e:
                # Still record the duration/memory for failed attempts
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss
                
                durations.append(end_time - start_time)
                memory_usage.append(end_memory - start_memory)
        
        return {
            "function_name": func.__name__,
            "iterations": iterations,
            "average_duration_seconds": sum(durations) / len(durations),
            "max_duration_seconds": max(durations),
            "min_duration_seconds": min(durations),
            "average_memory_delta_bytes": sum(memory_usage) / len(memory_usage),
            "max_memory_delta_bytes": max(memory_usage),
            "total_duration_seconds": sum(durations),
            "benchmark_timestamp": datetime.utcnow().isoformat()
        }


# Convenience functions
def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor."""
    return performance_monitor


async def get_system_performance_snapshot() -> Dict[str, Any]:
    """Get current system performance snapshot."""
    process = psutil.Process()
    
    return {
        "cpu_percent": process.cpu_percent(),
        "memory_info": {
            "rss": process.memory_info().rss,
            "vms": process.memory_info().vms,
            "percent": process.memory_percent()
        },
        "system_cpu_percent": psutil.cpu_percent(),
        "system_memory": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "percent": psutil.virtual_memory().percent
        },
        "disk_usage": {
            "total": psutil.disk_usage('/').total,
            "used": psutil.disk_usage('/').used,
            "free": psutil.disk_usage('/').free,
            "percent": psutil.disk_usage('/').percent
        },
        "timestamp": datetime.utcnow().isoformat()
    }
