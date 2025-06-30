"""
Terminal Monitoring and Status Utility for Enterprise Insights Copilot
Provides comprehensive monitoring of backend terminal status, process health, and logging.
"""

import os
import sys
import time
import psutil
import asyncio
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json

from app.core.logging import get_logger

logger = get_logger("terminal_monitor")


class TerminalStatus(Enum):
    """Terminal/Process status enumeration"""
    STARTING = "starting"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class ProcessInfo:
    """Process information data class"""
    pid: int
    name: str
    status: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    create_time: datetime
    cmdline: List[str]
    cwd: str
    port: Optional[int] = None


@dataclass
class TerminalMonitorData:
    """Terminal monitor data structure"""
    timestamp: datetime
    backend_status: TerminalStatus
    backend_process: Optional[ProcessInfo]
    system_info: Dict[str, Any]
    ports_status: Dict[int, bool]
    log_summary: Dict[str, Any]


class TerminalMonitor:
    """
    Comprehensive terminal and process monitoring system.
    Monitors backend status, system resources, and maintains logs.
    """
    
    def __init__(self):
        self.backend_port = 8000
        self.frontend_port = 3000
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        self.monitor_log_file = self.log_dir / f"terminal_monitor_{datetime.now().strftime('%Y%m%d')}.log"
        self.status_file = self.log_dir / "terminal_status.json"
        
        # Initialize logging
        self._setup_monitor_logging()
        
    def _setup_monitor_logging(self):
        """Setup dedicated logging for terminal monitoring"""
        import logging
        
        # Create dedicated logger for terminal monitoring
        self.monitor_logger = logging.getLogger("terminal_monitor")
        self.monitor_logger.setLevel(logging.INFO)
        
        # File handler for monitor logs
        file_handler = logging.FileHandler(self.monitor_log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        if not self.monitor_logger.handlers:
            self.monitor_logger.addHandler(file_handler)
            self.monitor_logger.addHandler(console_handler)
    
    def get_process_by_port(self, port: int) -> Optional[ProcessInfo]:
        """Find process using specific port"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status', 'create_time', 'cwd']):
                try:
                    connections = proc.connections(kind='inet')
                    for conn in connections:
                        if conn.laddr.port == port:
                            return ProcessInfo(
                                pid=proc.pid,
                                name=proc.info['name'],
                                status=proc.info['status'],
                                cpu_percent=proc.cpu_percent(),
                                memory_percent=proc.memory_percent(),
                                memory_mb=proc.memory_info().rss / 1024 / 1024,
                                create_time=datetime.fromtimestamp(proc.info['create_time'], tz=timezone.utc),
                                cmdline=proc.info['cmdline'] or [],
                                cwd=proc.info['cwd'] or "",
                                port=port
                            )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.error(f"Error finding process by port {port}: {e}")
        return None
    
    def get_backend_status(self) -> tuple[TerminalStatus, Optional[ProcessInfo]]:
        """Get current backend terminal/process status"""
        try:
            # Check if backend process is running on expected port
            backend_process = self.get_process_by_port(self.backend_port)
            
            if backend_process:
                # Process found, check if it's our FastAPI app
                cmdline_str = " ".join(backend_process.cmdline).lower()
                if any(keyword in cmdline_str for keyword in ['uvicorn', 'fastapi', 'main:app']):
                    return TerminalStatus.RUNNING, backend_process
                else:
                    return TerminalStatus.ERROR, backend_process
            
            # Check if there's a Python process that might be our backend
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline'] or []
                    cmdline_str = " ".join(cmdline).lower()
                    
                    if proc.info['name'] == 'python.exe' and any(
                        keyword in cmdline_str 
                        for keyword in ['main.py', 'uvicorn', 'fastapi']
                    ):
                        # Found potential backend process
                        proc_info = ProcessInfo(
                            pid=proc.pid,
                            name=proc.info['name'],
                            status=proc.status(),
                            cpu_percent=proc.cpu_percent(),
                            memory_percent=proc.memory_percent(),
                            memory_mb=proc.memory_info().rss / 1024 / 1024,
                            create_time=datetime.fromtimestamp(proc.create_time(), tz=timezone.utc),
                            cmdline=cmdline,
                            cwd=proc.cwd()
                        )
                        return TerminalStatus.RUNNING, proc_info
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return TerminalStatus.STOPPED, None
            
        except Exception as e:
            logger.error(f"Error checking backend status: {e}")
            return TerminalStatus.ERROR, None
    
    def check_port_status(self, port: int) -> bool:
        """Check if port is in use"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                return result == 0
        except Exception:
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get current system information"""
        try:
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_count": cpu_count,
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_total_gb": round(memory.total / 1024 / 1024 / 1024, 2),
                "memory_available_gb": round(memory.available / 1024 / 1024 / 1024, 2),
                "memory_percent": memory.percent,
                "disk_total_gb": round(disk.total / 1024 / 1024 / 1024, 2),
                "disk_free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
                "disk_percent": round((disk.used / disk.total) * 100, 2)
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {}
    
    def get_log_summary(self) -> Dict[str, Any]:
        """Get summary of recent logs"""
        try:
            log_files = list(self.log_dir.glob("*.log"))
            
            summary = {
                "total_log_files": len(log_files),
                "recent_logs": [],
                "total_size_mb": 0
            }
            
            for log_file in sorted(log_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                stat = log_file.stat()
                size_mb = stat.st_size / 1024 / 1024
                summary["total_size_mb"] += size_mb
                
                summary["recent_logs"].append({
                    "file": log_file.name,
                    "size_mb": round(size_mb, 2),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "lines": self._count_lines_safely(log_file)
                })
            
            summary["total_size_mb"] = round(summary["total_size_mb"], 2)
            return summary
            
        except Exception as e:
            logger.error(f"Error getting log summary: {e}")
            return {"error": str(e)}
    
    def _count_lines_safely(self, file_path: Path) -> int:
        """Safely count lines in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except Exception:
            return 0
    
    def collect_terminal_status(self) -> TerminalMonitorData:
        """Collect comprehensive terminal status"""
        timestamp = datetime.now(timezone.utc)
        
        # Get backend status
        backend_status, backend_process = self.get_backend_status()
        
        # Get system info
        system_info = self.get_system_info()
        
        # Check port status
        ports_status = {
            self.backend_port: self.check_port_status(self.backend_port),
            self.frontend_port: self.check_port_status(self.frontend_port)
        }
        
        # Get log summary
        log_summary = self.get_log_summary()
        
        return TerminalMonitorData(
            timestamp=timestamp,
            backend_status=backend_status,
            backend_process=backend_process,
            system_info=system_info,
            ports_status=ports_status,
            log_summary=log_summary
        )
    
    def log_terminal_status(self) -> TerminalMonitorData:
        """Collect and log terminal status"""
        status_data = self.collect_terminal_status()
        
        # Log to monitor logger
        self.monitor_logger.info(
            f"Terminal Status Check - Backend: {status_data.backend_status.value}, "
            f"Port {self.backend_port}: {'UP' if status_data.ports_status[self.backend_port] else 'DOWN'}, "
            f"CPU: {status_data.system_info.get('cpu_percent', 'N/A')}%, "
            f"Memory: {status_data.system_info.get('memory_percent', 'N/A')}%"
        )
        
        # Log detailed process info if available
        if status_data.backend_process:
            proc = status_data.backend_process
            self.monitor_logger.info(
                f"Backend Process - PID: {proc.pid}, "
                f"CPU: {proc.cpu_percent}%, "
                f"Memory: {proc.memory_mb:.1f}MB, "
                f"Status: {proc.status}"
            )
        
        # Save status to file
        self._save_status_to_file(status_data)
        
        # Log to main application logger
        logger.info(
            "Terminal status collected",
            extra={
                "backend_status": status_data.backend_status.value,
                "backend_port_active": status_data.ports_status[self.backend_port],
                "system_cpu_percent": status_data.system_info.get('cpu_percent'),
                "system_memory_percent": status_data.system_info.get('memory_percent'),
                "log_files_count": status_data.log_summary.get('total_log_files', 0)
            }
        )
        
        return status_data
    
    def _save_status_to_file(self, status_data: TerminalMonitorData):
        """Save status data to JSON file"""
        try:
            # Convert to serializable format
            data_dict = asdict(status_data)
            data_dict['timestamp'] = status_data.timestamp.isoformat()
            data_dict['backend_status'] = status_data.backend_status.value
            
            if status_data.backend_process:
                data_dict['backend_process']['create_time'] = status_data.backend_process.create_time.isoformat()
            
            with open(self.status_file, 'w') as f:
                json.dump(data_dict, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving status to file: {e}")
    
    def start_monitoring(self, interval: int = 30):
        """Start continuous monitoring"""
        self.monitor_logger.info(f"Starting terminal monitoring with {interval}s interval")
        
        try:
            while True:
                self.log_terminal_status()
                time.sleep(interval)
        except KeyboardInterrupt:
            self.monitor_logger.info("Terminal monitoring stopped by user")
        except Exception as e:
            self.monitor_logger.error(f"Error in monitoring loop: {e}")
    
    async def async_monitoring(self, interval: int = 30):
        """Asynchronous monitoring for integration with FastAPI"""
        self.monitor_logger.info(f"Starting async terminal monitoring with {interval}s interval")
        
        try:
            while True:
                self.log_terminal_status()
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            self.monitor_logger.info("Async terminal monitoring cancelled")
            raise  # Re-raise CancelledError
        except Exception as e:
            self.monitor_logger.error(f"Error in async monitoring: {e}")
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get formatted status report"""
        status_data = self.collect_terminal_status()
        
        # Convert process info to dict and handle datetime serialization
        process_info = None
        if status_data.backend_process:
            process_info = asdict(status_data.backend_process)
            process_info['create_time'] = status_data.backend_process.create_time.isoformat()
        
        report = {
            "timestamp": status_data.timestamp.isoformat(),
            "backend": {
                "status": status_data.backend_status.value,
                "port_active": status_data.ports_status[self.backend_port],
                "process_info": process_info
            },
            "system": status_data.system_info,
            "ports": status_data.ports_status,
            "logs": status_data.log_summary
        }
        
        return report


# Global monitor instance
terminal_monitor = TerminalMonitor()


def get_terminal_status() -> Dict[str, Any]:
    """Get current terminal status (convenience function)"""
    return terminal_monitor.get_status_report()


def log_terminal_status() -> TerminalMonitorData:
    """Log current terminal status (convenience function)"""
    return terminal_monitor.log_terminal_status()


if __name__ == "__main__":
    """Run monitoring as standalone script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Terminal Monitor for Enterprise Insights Copilot")
    parser.add_argument("--interval", type=int, default=30, help="Monitoring interval in seconds")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    
    args = parser.parse_args()
    
    monitor = TerminalMonitor()
    
    if args.once:
        status = monitor.log_terminal_status()
        print(json.dumps(monitor.get_status_report(), indent=2))
    else:
        monitor.start_monitoring(args.interval)
