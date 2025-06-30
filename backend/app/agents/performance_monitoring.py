"""
Agent Performance Monitoring
Task 104: Implement agent performance monitoring
"""

import asyncio
import logging
import time
import psutil
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime, timezone, timedelta
from enum import Enum
from dataclasses import dataclass, field
from collections import deque, defaultdict
import statistics
import json
import threading

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of performance metrics"""
    COUNTER = "counter"         # Monotonically increasing
    GAUGE = "gauge"            # Current value
    HISTOGRAM = "histogram"     # Distribution of values
    TIMER = "timer"            # Duration measurements
    RATE = "rate"              # Rate of events


class MetricUnit(str, Enum):
    """Units for metrics"""
    SECONDS = "seconds"
    MILLISECONDS = "milliseconds"
    BYTES = "bytes"
    KILOBYTES = "kilobytes"
    MEGABYTES = "megabytes"
    COUNT = "count"
    PERCENT = "percent"
    REQUESTS_PER_SECOND = "requests_per_second"


@dataclass
class MetricValue:
    """Individual metric value with timestamp"""
    value: Union[int, float]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    labels: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "labels": self.labels
        }


@dataclass
class PerformanceSnapshot:
    """Performance snapshot at a point in time"""
    agent_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Execution metrics
    active_executions: int = 0
    completed_executions: int = 0
    failed_executions: int = 0
    average_response_time: float = 0.0
    
    # Resource metrics
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    memory_peak: float = 0.0
    
    # LLM metrics
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    token_rate: float = 0.0
    
    # Error metrics
    error_rate: float = 0.0
    timeout_count: int = 0
    retry_count: int = 0
    
    # Quality metrics
    average_confidence: float = 0.0
    user_satisfaction: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "timestamp": self.timestamp.isoformat(),
            "active_executions": self.active_executions,
            "completed_executions": self.completed_executions,
            "failed_executions": self.failed_executions,
            "average_response_time": self.average_response_time,
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "memory_peak": self.memory_peak,
            "total_tokens": self.total_tokens,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "token_rate": self.token_rate,
            "error_rate": self.error_rate,
            "timeout_count": self.timeout_count,
            "retry_count": self.retry_count,
            "average_confidence": self.average_confidence,
            "user_satisfaction": self.user_satisfaction
        }


class Metric:
    """Base class for performance metrics"""
    
    def __init__(
        self, 
        name: str, 
        metric_type: MetricType, 
        unit: MetricUnit = MetricUnit.COUNT,
        description: str = "",
        max_samples: int = 1000
    ):
        self.name = name
        self.type = metric_type
        self.unit = unit
        self.description = description
        self.max_samples = max_samples
        self.values: deque = deque(maxlen=max_samples)
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        self._lock = threading.Lock()
    
    def add_value(self, value: Union[int, float], labels: Optional[Dict[str, str]] = None):
        """Add a value to the metric"""
        with self._lock:
            metric_value = MetricValue(value, labels=labels or {})
            self.values.append(metric_value)
            self.updated_at = datetime.now(timezone.utc)
    
    def get_current_value(self) -> Optional[float]:
        """Get the most recent value"""
        with self._lock:
            if self.values:
                return self.values[-1].value
            return None
    
    def get_statistics(self, window_minutes: int = 60) -> Dict[str, float]:
        """Get statistics for a time window"""
        with self._lock:
            if not self.values:
                return {}
            
            # Filter values within time window
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
            recent_values = [
                v.value for v in self.values 
                if v.timestamp >= cutoff_time
            ]
            
            if not recent_values:
                return {}
            
            stats = {
                "count": len(recent_values),
                "latest": recent_values[-1],
                "min": min(recent_values),
                "max": max(recent_values),
                "mean": statistics.mean(recent_values)
            }
            
            if len(recent_values) > 1:
                stats["stddev"] = statistics.stdev(recent_values)
                stats["median"] = statistics.median(recent_values)
            
            # Add percentiles for larger datasets
            if len(recent_values) >= 10:
                sorted_values = sorted(recent_values)
                stats["p50"] = statistics.median(sorted_values)
                stats["p95"] = sorted_values[int(0.95 * len(sorted_values))]
                stats["p99"] = sorted_values[int(0.99 * len(sorted_values))]
            
            return stats
    
    def get_time_series(self, window_minutes: int = 60) -> List[Dict[str, Any]]:
        """Get time series data"""
        with self._lock:
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
            return [
                v.to_dict() for v in self.values 
                if v.timestamp >= cutoff_time
            ]


class Timer:
    """Timer for measuring durations"""
    
    def __init__(self, metric: Metric):
        self.metric = metric
        self.start_time: Optional[float] = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.metric.add_value(duration)


class PerformanceMonitor:
    """Main performance monitoring system"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.metrics: Dict[str, Metric] = {}
        self.snapshots: deque = deque(maxlen=100)  # Keep last 100 snapshots
        self.start_time = datetime.now(timezone.utc)
        
        # Resource monitoring
        self.process = psutil.Process()
        self.baseline_memory = self.process.memory_info().rss
        
        # Execution tracking
        self.active_executions = set()
        self.execution_history: deque = deque(maxlen=1000)
        
        # Initialize default metrics
        self._initialize_default_metrics()
        
        # Start background monitoring
        self._monitoring_task: Optional[asyncio.Task] = None
        self._should_monitor = False
    
    def _initialize_default_metrics(self):
        """Initialize default performance metrics"""
        metrics = [
            ("execution_count", MetricType.COUNTER, MetricUnit.COUNT, "Total executions"),
            ("execution_duration", MetricType.TIMER, MetricUnit.SECONDS, "Execution duration"),
            ("memory_usage", MetricType.GAUGE, MetricUnit.MEGABYTES, "Memory usage"),
            ("cpu_usage", MetricType.GAUGE, MetricUnit.PERCENT, "CPU usage"),
            ("token_count", MetricType.COUNTER, MetricUnit.COUNT, "Total tokens processed"),
            ("error_count", MetricType.COUNTER, MetricUnit.COUNT, "Total errors"),
            ("timeout_count", MetricType.COUNTER, MetricUnit.COUNT, "Total timeouts"),
            ("retry_count", MetricType.COUNTER, MetricUnit.COUNT, "Total retries"),
            ("confidence_score", MetricType.GAUGE, MetricUnit.PERCENT, "Confidence score"),
            ("response_time", MetricType.TIMER, MetricUnit.MILLISECONDS, "Response time")
        ]
        
        for name, metric_type, unit, description in metrics:
            self.metrics[name] = Metric(name, metric_type, unit, description)
    
    def get_metric(self, name: str) -> Optional[Metric]:
        """Get a metric by name"""
        return self.metrics.get(name)
    
    def create_metric(
        self, 
        name: str, 
        metric_type: MetricType, 
        unit: MetricUnit = MetricUnit.COUNT,
        description: str = ""
    ) -> Metric:
        """Create a new metric"""
        metric = Metric(name, metric_type, unit, description)
        self.metrics[name] = metric
        return metric
    
    def record_value(self, metric_name: str, value: Union[int, float], labels: Optional[Dict[str, str]] = None):
        """Record a value for a metric"""
        metric = self.metrics.get(metric_name)
        if metric:
            metric.add_value(value, labels)
        else:
            logger.warning(f"Metric {metric_name} not found")
    
    def increment_counter(self, metric_name: str, amount: Union[int, float] = 1, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        metric = self.metrics.get(metric_name)
        if metric and metric.type == MetricType.COUNTER:
            current = metric.get_current_value() or 0
            metric.add_value(current + amount, labels)
        else:
            logger.warning(f"Counter metric {metric_name} not found")
    
    def set_gauge(self, metric_name: str, value: Union[int, float], labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric value"""
        metric = self.metrics.get(metric_name)
        if metric and metric.type == MetricType.GAUGE:
            metric.add_value(value, labels)
        else:
            logger.warning(f"Gauge metric {metric_name} not found")
    
    def start_timer(self, metric_name: str) -> Optional[Timer]:
        """Start a timer for a metric"""
        metric = self.metrics.get(metric_name)
        if metric and metric.type == MetricType.TIMER:
            return Timer(metric)
        else:
            logger.warning(f"Timer metric {metric_name} not found")
            return None
    
    def record_execution_start(self, execution_id: str):
        """Record the start of an execution"""
        self.active_executions.add(execution_id)
        self.increment_counter("execution_count")
    
    def record_execution_end(
        self, 
        execution_id: str, 
        duration: float, 
        success: bool, 
        token_count: int = 0,
        confidence: Optional[float] = None
    ):
        """Record the end of an execution"""
        self.active_executions.discard(execution_id)
        
        # Record metrics
        self.record_value("execution_duration", duration)
        self.record_value("response_time", duration * 1000)  # Convert to milliseconds
        
        if token_count > 0:
            self.increment_counter("token_count", token_count)
        
        if confidence is not None:
            self.set_gauge("confidence_score", confidence * 100)  # Convert to percentage
        
        if not success:
            self.increment_counter("error_count")
        
        # Store execution history
        execution_record = {
            "execution_id": execution_id,
            "duration": duration,
            "success": success,
            "token_count": token_count,
            "confidence": confidence,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.execution_history.append(execution_record)
    
    def record_timeout(self, execution_id: str):
        """Record a timeout"""
        self.increment_counter("timeout_count")
        self.increment_counter("error_count")
    
    def record_retry(self, execution_id: str):
        """Record a retry"""
        self.increment_counter("retry_count")
    
    def get_current_performance(self) -> PerformanceSnapshot:
        """Get current performance snapshot"""
        # Resource usage
        cpu_percent = self.process.cpu_percent()
        memory_info = self.process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        # Update resource metrics
        self.set_gauge("cpu_usage", cpu_percent)
        self.set_gauge("memory_usage", memory_mb)
        
        # Calculate derived metrics
        execution_count = self.metrics["execution_count"].get_current_value() or 0
        error_count = self.metrics["error_count"].get_current_value() or 0
        error_rate = (error_count / execution_count * 100) if execution_count > 0 else 0.0
        
        # Get average response time
        response_time_stats = self.metrics["response_time"].get_statistics(window_minutes=60)
        avg_response_time = response_time_stats.get("mean", 0.0) / 1000  # Convert to seconds
        
        # Get token metrics
        total_tokens = self.metrics["token_count"].get_current_value() or 0
        
        # Calculate token rate (tokens per minute)
        uptime_minutes = (datetime.now(timezone.utc) - self.start_time).total_seconds() / 60
        token_rate = total_tokens / uptime_minutes if uptime_minutes > 0 else 0.0
        
        # Get confidence score
        confidence = self.metrics["confidence_score"].get_current_value() or 0.0
        
        snapshot = PerformanceSnapshot(
            agent_id=self.agent_id,
            active_executions=len(self.active_executions),
            completed_executions=int(execution_count),
            failed_executions=int(error_count),
            average_response_time=avg_response_time,
            cpu_usage=cpu_percent,
            memory_usage=memory_mb,
            memory_peak=memory_mb,  # Would track peak separately in production
            total_tokens=int(total_tokens),
            token_rate=token_rate,
            error_rate=error_rate,
            timeout_count=int(self.metrics["timeout_count"].get_current_value() or 0),
            retry_count=int(self.metrics["retry_count"].get_current_value() or 0),
            average_confidence=confidence / 100  # Convert back to 0-1 range
        )
        
        self.snapshots.append(snapshot)
        return snapshot
    
    def get_metric_statistics(self, metric_name: str, window_minutes: int = 60) -> Dict[str, Any]:
        """Get statistics for a specific metric"""
        metric = self.metrics.get(metric_name)
        if metric:
            return {
                "name": metric_name,
                "type": metric.type.value,
                "unit": metric.unit.value,
                "description": metric.description,
                "statistics": metric.get_statistics(window_minutes),
                "sample_count": len(metric.values)
            }
        return {}
    
    def get_all_metrics_summary(self, window_minutes: int = 60) -> Dict[str, Any]:
        """Get summary of all metrics"""
        summary = {}
        for name, metric in self.metrics.items():
            summary[name] = self.get_metric_statistics(name, window_minutes)
        return summary
    
    def get_performance_trend(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get performance trend over time"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        return [
            snapshot.to_dict() for snapshot in self.snapshots 
            if snapshot.timestamp >= cutoff_time
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        snapshot = self.get_current_performance()
        
        # Define health thresholds
        health_score = 100.0
        issues = []
        
        # Check CPU usage
        if snapshot.cpu_usage > 80:
            health_score -= 20
            issues.append(f"High CPU usage: {snapshot.cpu_usage:.1f}%")
        
        # Check memory usage
        if snapshot.memory_usage > 1000:  # 1GB
            health_score -= 15
            issues.append(f"High memory usage: {snapshot.memory_usage:.1f}MB")
        
        # Check error rate
        if snapshot.error_rate > 10:  # 10% error rate
            health_score -= 25
            issues.append(f"High error rate: {snapshot.error_rate:.1f}%")
        
        # Check response time
        if snapshot.average_response_time > 10:  # 10 seconds
            health_score -= 20
            issues.append(f"Slow response time: {snapshot.average_response_time:.1f}s")
        
        # Determine status
        if health_score >= 80:
            status = "healthy"
        elif health_score >= 60:
            status = "degraded"
        else:
            status = "unhealthy"
        
        return {
            "status": status,
            "health_score": max(0, health_score),
            "issues": issues,
            "snapshot": snapshot.to_dict(),
            "uptime_seconds": (datetime.now(timezone.utc) - self.start_time).total_seconds()
        }
    
    async def start_monitoring(self, interval_seconds: int = 30):
        """Start background monitoring"""
        if self._monitoring_task:
            return
        
        self._should_monitor = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop(interval_seconds))
    
    async def stop_monitoring(self):
        """Stop background monitoring"""
        self._should_monitor = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            self._monitoring_task = None
    
    async def _monitoring_loop(self, interval_seconds: int):
        """Background monitoring loop"""
        while self._should_monitor:
            try:
                # Take performance snapshot
                self.get_current_performance()
                
                # Log health status periodically
                if len(self.snapshots) % 10 == 0:  # Every 10 snapshots
                    health = self.get_health_status()
                    logger.info(f"Agent {self.agent_id} health: {health['status']} (score: {health['health_score']:.1f})")
                
                await asyncio.sleep(interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(interval_seconds)
    
    def export_metrics(self, format_type: str = "json") -> str:
        """Export metrics in specified format"""
        data = {
            "agent_id": self.agent_id,
            "export_time": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": (datetime.now(timezone.utc) - self.start_time).total_seconds(),
            "metrics": self.get_all_metrics_summary(),
            "current_performance": self.get_current_performance().to_dict(),
            "health_status": self.get_health_status()
        }
        
        if format_type.lower() == "json":
            return json.dumps(data, indent=2)
        else:
            return str(data)


# Global performance monitors by agent ID
_performance_monitors: Dict[str, PerformanceMonitor] = {}


def get_performance_monitor(agent_id: str) -> PerformanceMonitor:
    """Get or create performance monitor for an agent"""
    if agent_id not in _performance_monitors:
        _performance_monitors[agent_id] = PerformanceMonitor(agent_id)
    return _performance_monitors[agent_id]


async def start_all_monitoring():
    """Start monitoring for all agents"""
    for monitor in _performance_monitors.values():
        await monitor.start_monitoring()


async def stop_all_monitoring():
    """Stop monitoring for all agents"""
    for monitor in _performance_monitors.values():
        await monitor.stop_monitoring()


def get_system_performance() -> Dict[str, Any]:
    """Get system-wide performance summary"""
    return {
        "total_agents": len(_performance_monitors),
        "agents": {
            agent_id: monitor.get_health_status()
            for agent_id, monitor in _performance_monitors.items()
        },
        "system_resources": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
    }


# Decorators for automatic performance monitoring


def monitor_performance(agent_id: str, metric_name: str = "execution_duration"):
    """Decorator to automatically monitor function performance"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            monitor = get_performance_monitor(agent_id)
            execution_id = kwargs.get('execution_id', 'unknown')
            
            # Record execution start
            monitor.record_execution_start(execution_id)
            
            start_time = time.time()
            success = False
            token_count = 0
            confidence = None
            
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                success = True
                
                # Extract metrics from result if available
                if hasattr(result, 'token_usage'):
                    token_count = sum(result.token_usage.values())
                if hasattr(result, 'confidence'):
                    confidence = result.confidence
                
                return result
                
            except Exception as e:
                success = False
                raise
            
            finally:
                duration = time.time() - start_time
                monitor.record_execution_end(execution_id, duration, success, token_count, confidence)
        
        return wrapper
    return decorator
