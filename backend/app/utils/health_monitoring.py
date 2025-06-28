"""
Health check monitoring system for Enterprise Insights Copilot
Provides comprehensive health monitoring for all system components.
"""

import asyncio
import time
import psutil
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import sqlite3
from pathlib import Path

from app.utils.logging import get_logger
from app.utils.metrics import metrics


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Health check configuration."""
    name: str
    description: str
    check_function: Callable
    timeout_seconds: int = 10
    critical: bool = True
    enabled: bool = True
    interval_seconds: int = 60


@dataclass
class HealthResult:
    """Health check result."""
    check_name: str
    status: HealthStatus
    message: str
    response_time_ms: float
    timestamp: datetime
    metadata: Dict[str, Any]


class HealthMonitor:
    """Health monitoring and checking system."""
    
    def __init__(self):
        self.logger = get_logger()
        self.health_checks: List[HealthCheck] = []
        self.health_history: List[HealthResult] = []
        self.running = False
        self.check_tasks: List[asyncio.Task] = []
        self._setup_default_checks()
    
    def _setup_default_checks(self):
        """Setup default health checks."""
        default_checks = [
            HealthCheck(
                name="system_memory",
                description="Check system memory usage",
                check_function=self._check_system_memory,
                timeout_seconds=5,
                critical=True,
                interval_seconds=30
            ),
            HealthCheck(
                name="system_cpu",
                description="Check system CPU usage",
                check_function=self._check_system_cpu,
                timeout_seconds=5,
                critical=False,
                interval_seconds=30
            ),
            HealthCheck(
                name="disk_space",
                description="Check available disk space",
                check_function=self._check_disk_space,
                timeout_seconds=5,
                critical=True,
                interval_seconds=60
            ),
            HealthCheck(
                name="database_connection",
                description="Check database connectivity",
                check_function=self._check_database,
                timeout_seconds=10,
                critical=True,
                interval_seconds=30
            ),
            HealthCheck(
                name="log_system",
                description="Check logging system health",
                check_function=self._check_logging_system,
                timeout_seconds=5,
                critical=False,
                interval_seconds=60
            ),
            HealthCheck(
                name="metrics_system",
                description="Check metrics collection system",
                check_function=self._check_metrics_system,
                timeout_seconds=5,
                critical=False,
                interval_seconds=60
            )
        ]
        
        self.health_checks.extend(default_checks)
    
    async def start_monitoring(self):
        """Start health monitoring background tasks."""
        if self.running:
            return
        
        self.running = True
        
        # Start individual check tasks
        for check in self.health_checks:
            if check.enabled:
                task = asyncio.create_task(self._run_periodic_check(check))
                self.check_tasks.append(task)
        
        self.logger.info(f"Health monitoring started with {len(self.check_tasks)} checks")
    
    async def stop_monitoring(self):
        """Stop health monitoring."""
        self.running = False
        
        # Cancel all check tasks
        for task in self.check_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.check_tasks, return_exceptions=True)
        self.check_tasks.clear()
        
        self.logger.info("Health monitoring stopped")
    
    async def _run_periodic_check(self, check: HealthCheck):
        """Run a health check periodically."""
        while self.running:
            try:
                await self._execute_health_check(check)
                await asyncio.sleep(check.interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in periodic health check {check.name}", error=e)
                await asyncio.sleep(check.interval_seconds)
    
    async def _execute_health_check(self, check: HealthCheck) -> HealthResult:
        """Execute a single health check."""
        start_time = time.time()
        
        try:
            # Execute check with timeout
            result = await asyncio.wait_for(
                check.check_function(),
                timeout=check.timeout_seconds
            )
            
            response_time = (time.time() - start_time) * 1000
            
            health_result = HealthResult(
                check_name=check.name,
                status=result.get("status", HealthStatus.UNKNOWN),
                message=result.get("message", "Health check completed"),
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                metadata=result.get("metadata", {})
            )
            
        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            health_result = HealthResult(
                check_name=check.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check timed out after {check.timeout_seconds}s",
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                metadata={"timeout": True}
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            health_result = HealthResult(
                check_name=check.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                metadata={"error": str(e)}
            )
        
        # Store result
        self.health_history.append(health_result)
        
        # Keep only last 1000 results
        if len(self.health_history) > 1000:
            self.health_history = self.health_history[-1000:]
        
        # Record metrics
        status_value = 1 if health_result.status == HealthStatus.HEALTHY else 0
        metrics.update_active_sessions(status_value)  # Reusing existing gauge
        
        # Log significant status changes
        if health_result.status != HealthStatus.HEALTHY:
            self.logger.warning(
                f"Health check {check.name} failed",
                check_name=check.name,
                status=health_result.status.value,
                message=health_result.message,
                response_time_ms=health_result.response_time_ms
            )
        
        return health_result
    
    async def run_all_checks(self) -> List[HealthResult]:
        """Run all health checks immediately."""
        results = []
        
        for check in self.health_checks:
            if check.enabled:
                result = await self._execute_health_check(check)
                results.append(result)
        
        return results
    
    async def run_single_check(self, check_name: str) -> Optional[HealthResult]:
        """Run a single health check by name."""
        check = next((c for c in self.health_checks if c.name == check_name), None)
        
        if not check:
            return None
        
        return await self._execute_health_check(check)
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        if not self.health_history:
            return {
                "status": HealthStatus.UNKNOWN.value,
                "message": "No health data available",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Get latest results for each check
        latest_results = {}
        for result in reversed(self.health_history):
            if result.check_name not in latest_results:
                latest_results[result.check_name] = result
        
        # Determine overall status
        critical_checks = [c for c in self.health_checks if c.critical and c.enabled]
        critical_check_names = {c.name for c in critical_checks}
        
        overall_status = HealthStatus.HEALTHY
        unhealthy_critical = 0
        unhealthy_non_critical = 0
        
        for check_name, result in latest_results.items():
            if result.status == HealthStatus.UNHEALTHY:
                if check_name in critical_check_names:
                    unhealthy_critical += 1
                else:
                    unhealthy_non_critical += 1
            elif result.status == HealthStatus.DEGRADED:
                if overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
        
        # Determine final status
        if unhealthy_critical > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif unhealthy_non_critical > 0 and overall_status == HealthStatus.HEALTHY:
            overall_status = HealthStatus.DEGRADED
        
        return {
            "status": overall_status.value,
            "critical_checks_unhealthy": unhealthy_critical,
            "non_critical_checks_unhealthy": unhealthy_non_critical,
            "total_checks": len(latest_results),
            "checks": {name: {
                "status": result.status.value,
                "message": result.message,
                "response_time_ms": result.response_time_ms,
                "timestamp": result.timestamp.isoformat()
            } for name, result in latest_results.items()},
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_health_history(self, check_name: Optional[str] = None, hours: int = 24) -> List[Dict[str, Any]]:
        """Get health check history."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        filtered_history = [
            result for result in self.health_history
            if result.timestamp > cutoff_time and (
                check_name is None or result.check_name == check_name
            )
        ]
        
        return [
            {
                "check_name": result.check_name,
                "status": result.status.value,
                "message": result.message,
                "response_time_ms": result.response_time_ms,
                "timestamp": result.timestamp.isoformat(),
                "metadata": result.metadata
            }
            for result in filtered_history
        ]
    
    def add_health_check(self, check: HealthCheck):
        """Add a custom health check."""
        self.health_checks.append(check)
        
        # If monitoring is running, start the new check
        if self.running and check.enabled:
            task = asyncio.create_task(self._run_periodic_check(check))
            self.check_tasks.append(task)
        
        self.logger.info(f"Added health check: {check.name}")
    
    def remove_health_check(self, check_name: str):
        """Remove a health check."""
        self.health_checks = [c for c in self.health_checks if c.name != check_name]
        self.logger.info(f"Removed health check: {check_name}")
    
    # Default health check implementations
    async def _check_system_memory(self) -> Dict[str, Any]:
        """Check system memory usage."""
        memory = psutil.virtual_memory()
        
        if memory.percent > 90:
            status = HealthStatus.UNHEALTHY
            message = f"Critical memory usage: {memory.percent:.1f}%"
        elif memory.percent > 80:
            status = HealthStatus.DEGRADED
            message = f"High memory usage: {memory.percent:.1f}%"
        else:
            status = HealthStatus.HEALTHY
            message = f"Memory usage normal: {memory.percent:.1f}%"
        
        return {
            "status": status,
            "message": message,
            "metadata": {
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "memory_total_gb": memory.total / (1024**3)
            }
        }
    
    async def _check_system_cpu(self) -> Dict[str, Any]:
        """Check system CPU usage."""
        cpu_percent = psutil.cpu_percent(interval=1)
        
        if cpu_percent > 95:
            status = HealthStatus.UNHEALTHY
            message = f"Critical CPU usage: {cpu_percent:.1f}%"
        elif cpu_percent > 80:
            status = HealthStatus.DEGRADED
            message = f"High CPU usage: {cpu_percent:.1f}%"
        else:
            status = HealthStatus.HEALTHY
            message = f"CPU usage normal: {cpu_percent:.1f}%"
        
        return {
            "status": status,
            "message": message,
            "metadata": {
                "cpu_percent": cpu_percent,
                "cpu_count": psutil.cpu_count()
            }
        }
    
    async def _check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space."""
        disk = psutil.disk_usage('/')
        
        if disk.percent > 95:
            status = HealthStatus.UNHEALTHY
            message = f"Critical disk usage: {disk.percent:.1f}%"
        elif disk.percent > 85:
            status = HealthStatus.DEGRADED
            message = f"High disk usage: {disk.percent:.1f}%"
        else:
            status = HealthStatus.HEALTHY
            message = f"Disk usage normal: {disk.percent:.1f}%"
        
        return {
            "status": status,
            "message": message,
            "metadata": {
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3),
                "disk_total_gb": disk.total / (1024**3)
            }
        }
    
    async def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity."""
        try:
            # Simple SQLite connection test
            db_path = "logs/app_logs.db"
            if not Path(db_path).parent.exists():
                Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(db_path, timeout=5)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    "status": HealthStatus.HEALTHY,
                    "message": "Database connection successful",
                    "metadata": {"database_type": "sqlite", "response_ok": True}
                }
            else:
                return {
                    "status": HealthStatus.UNHEALTHY,
                    "message": "Database query failed",
                    "metadata": {"database_type": "sqlite", "response_ok": False}
                }
                
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Database connection failed: {str(e)}",
                "metadata": {"database_type": "sqlite", "error": str(e)}
            }
    
    async def _check_logging_system(self) -> Dict[str, Any]:
        """Check logging system health."""
        try:
            # Test logging functionality
            self.logger.debug("Health check test log message")
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Logging system operational",
                "metadata": {
                    "logger_name": self.logger.logger.name,
                    "handler_count": len(self.logger.logger.handlers)
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Logging system failed: {str(e)}",
                "metadata": {"error": str(e)}
            }
    
    async def _check_metrics_system(self) -> Dict[str, Any]:
        """Check metrics collection system."""
        try:
            # Test metrics recording
            metrics.record_http_request("GET", "/health", 200, 0.001)
            
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Metrics system operational",
                "metadata": {"metrics_recorded": True}
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Metrics system failed: {str(e)}",
                "metadata": {"error": str(e)}
            }


# Global health monitor instance
health_monitor = HealthMonitor()


def get_health_monitor() -> HealthMonitor:
    """Get the global health monitor instance."""
    return health_monitor


async def initialize_health_monitoring():
    """Initialize health monitoring system."""
    await health_monitor.start_monitoring()


async def shutdown_health_monitoring():
    """Shutdown health monitoring system."""
    await health_monitor.stop_monitoring()
