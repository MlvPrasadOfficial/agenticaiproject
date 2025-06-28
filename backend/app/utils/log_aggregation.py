"""
Log aggregation and storage configuration
Provides centralized log collection, storage, and search capabilities.
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path
import aiofiles
import sqlite3
from app.utils.logging import structured_logger


@dataclass
class LogEntry:
    """Structured log entry data class."""
    timestamp: datetime
    level: str
    message: str
    service: str
    trace_id: str
    component: str
    metadata: Dict[str, Any]


class LogStorage:
    """Base interface for log storage backends."""
    
    async def store_log(self, log_entry: LogEntry) -> None:
        """Store a log entry."""
        raise NotImplementedError
    
    async def query_logs(self, query: Dict[str, Any]) -> List[LogEntry]:
        """Query logs based on criteria."""
        raise NotImplementedError
    
    async def get_logs_by_timerange(self, start_time: datetime, end_time: datetime) -> List[LogEntry]:
        """Get logs within a time range."""
        raise NotImplementedError


class FileLogStorage(LogStorage):
    """File-based log storage with rotation and compression."""
    
    def __init__(self, log_directory: str = "logs", max_file_size_mb: int = 100):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(exist_ok=True)
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.current_file_path = self.log_directory / f"app-{datetime.utcnow().strftime('%Y-%m-%d')}.jsonl"
    
    async def store_log(self, log_entry: LogEntry) -> None:
        """Store log entry in JSON Lines format."""
        log_data = {
            "timestamp": log_entry.timestamp.isoformat(),
            "level": log_entry.level,
            "message": log_entry.message,
            "service": log_entry.service,
            "trace_id": log_entry.trace_id,
            "component": log_entry.component,
            **log_entry.metadata
        }
        
        # Check if rotation is needed
        await self._rotate_if_needed()
        
        # Write log entry
        async with aiofiles.open(self.current_file_path, 'a') as f:
            await f.write(json.dumps(log_data) + '\n')
    
    async def _rotate_if_needed(self):
        """Rotate log file if it exceeds size limit."""
        if self.current_file_path.exists():
            file_size = self.current_file_path.stat().st_size
            if file_size > self.max_file_size_bytes:
                # Create rotated filename with timestamp
                timestamp = datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')
                rotated_path = self.log_directory / f"app-{timestamp}.jsonl"
                self.current_file_path.rename(rotated_path)
                
                # Compress old file (placeholder - would use gzip in production)
                # await self._compress_file(rotated_path)
    
    async def query_logs(self, query: Dict[str, Any]) -> List[LogEntry]:
        """Query logs from files (simplified implementation)."""
        logs = []
        
        # Get all log files
        log_files = list(self.log_directory.glob("*.jsonl"))
        log_files.sort(reverse=True)  # Most recent first
        
        for log_file in log_files:
            async with aiofiles.open(log_file, 'r') as f:
                async for line in f:
                    try:
                        log_data = json.loads(line.strip())
                        
                        # Simple filtering based on query parameters
                        matches = True
                        for key, value in query.items():
                            if key in log_data and log_data[key] != value:
                                matches = False
                                break
                        
                        if matches:
                            log_entry = LogEntry(
                                timestamp=datetime.fromisoformat(log_data['timestamp'].replace('Z', '+00:00')),
                                level=log_data['level'],
                                message=log_data['message'],
                                service=log_data['service'],
                                trace_id=log_data['trace_id'],
                                component=log_data['component'],
                                metadata={k: v for k, v in log_data.items() 
                                        if k not in ['timestamp', 'level', 'message', 'service', 'trace_id', 'component']}
                            )
                            logs.append(log_entry)
                    
                    except json.JSONDecodeError:
                        continue
        
        return logs


class SQLiteLogStorage(LogStorage):
    """SQLite-based log storage for structured queries."""
    
    def __init__(self, db_path: str = "logs/app_logs.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(exist_ok=True)
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize SQLite database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                service TEXT NOT NULL,
                trace_id TEXT,
                component TEXT,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for common queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_level ON logs(level)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_service ON logs(service)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trace_id ON logs(trace_id)')
        
        conn.commit()
        conn.close()
    
    async def store_log(self, log_entry: LogEntry) -> None:
        """Store log entry in SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO logs (timestamp, level, message, service, trace_id, component, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            log_entry.timestamp.isoformat(),
            log_entry.level,
            log_entry.message,
            log_entry.service,
            log_entry.trace_id,
            log_entry.component,
            json.dumps(log_entry.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    async def query_logs(self, query: Dict[str, Any]) -> List[LogEntry]:
        """Query logs from SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build WHERE clause from query parameters
        where_conditions = []
        params = []
        
        for key, value in query.items():
            if key in ['level', 'service', 'trace_id', 'component']:
                where_conditions.append(f"{key} = ?")
                params.append(value)
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        cursor.execute(f'''
            SELECT timestamp, level, message, service, trace_id, component, metadata
            FROM logs
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT 1000
        ''', params)
        
        logs = []
        for row in cursor.fetchall():
            log_entry = LogEntry(
                timestamp=datetime.fromisoformat(row[0]),
                level=row[1],
                message=row[2],
                service=row[3],
                trace_id=row[4],
                component=row[5],
                metadata=json.loads(row[6]) if row[6] else {}
            )
            logs.append(log_entry)
        
        conn.close()
        return logs
    
    async def get_logs_by_timerange(self, start_time: datetime, end_time: datetime) -> List[LogEntry]:
        """Get logs within a specific time range."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, level, message, service, trace_id, component, metadata
            FROM logs
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp DESC
        ''', (start_time.isoformat(), end_time.isoformat()))
        
        logs = []
        for row in cursor.fetchall():
            log_entry = LogEntry(
                timestamp=datetime.fromisoformat(row[0]),
                level=row[1],
                message=row[2],
                service=row[3],
                trace_id=row[4],
                component=row[5],
                metadata=json.loads(row[6]) if row[6] else {}
            )
            logs.append(log_entry)
        
        conn.close()
        return logs


class LogAggregator:
    """Log aggregation service that collects and stores logs."""
    
    def __init__(self, storage_backends: List[LogStorage]):
        self.storage_backends = storage_backends
        self.log_queue = asyncio.Queue()
        self.running = False
    
    async def start(self):
        """Start the log aggregation service."""
        self.running = True
        await self._process_logs()
    
    async def stop(self):
        """Stop the log aggregation service."""
        self.running = False
    
    async def add_log(self, log_entry: LogEntry):
        """Add a log entry to the aggregation queue."""
        await self.log_queue.put(log_entry)
    
    async def _process_logs(self):
        """Process logs from the queue and store them."""
        while self.running:
            try:
                # Wait for log entry with timeout
                log_entry = await asyncio.wait_for(self.log_queue.get(), timeout=1.0)
                
                # Store in all backends
                for backend in self.storage_backends:
                    try:
                        await backend.store_log(log_entry)
                    except Exception as e:
                        # Log storage error (to console to avoid recursion)
                        print(f"Failed to store log in backend {backend.__class__.__name__}: {e}")
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Error processing logs: {e}")


class LogAnalytics:
    """Log analytics and reporting functionality."""
    
    def __init__(self, storage: LogStorage):
        self.storage = storage
    
    async def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for the last N hours."""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        logs = await self.storage.get_logs_by_timerange(start_time, end_time)
        
        error_logs = [log for log in logs if log.level == "ERROR"]
        
        # Group errors by component
        error_by_component = {}
        for log in error_logs:
            component = log.component
            if component not in error_by_component:
                error_by_component[component] = []
            error_by_component[component].append(log)
        
        return {
            "total_errors": len(error_logs),
            "error_by_component": {k: len(v) for k, v in error_by_component.items()},
            "time_range_hours": hours,
            "most_common_errors": self._get_most_common_errors(error_logs),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _get_most_common_errors(self, error_logs: List[LogEntry]) -> List[Dict[str, Any]]:
        """Get most common error messages."""
        error_counts = {}
        
        for log in error_logs:
            message = log.message
            if message in error_counts:
                error_counts[message] += 1
            else:
                error_counts[message] = 1
        
        # Sort by count and return top 10
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"message": msg, "count": count} for msg, count in sorted_errors[:10]]
    
    async def get_performance_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance metrics from logs."""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        logs = await self.storage.get_logs_by_timerange(start_time, end_time)
        
        # Analyze performance-related logs
        performance_logs = [log for log in logs if 'execution_time' in log.metadata]
        
        if not performance_logs:
            return {"message": "No performance data available"}
        
        execution_times = [float(log.metadata['execution_time']) for log in performance_logs if 'execution_time' in log.metadata]
        
        return {
            "average_execution_time": sum(execution_times) / len(execution_times),
            "max_execution_time": max(execution_times),
            "min_execution_time": min(execution_times),
            "total_operations": len(performance_logs),
            "time_range_hours": hours,
            "generated_at": datetime.utcnow().isoformat()
        }


# Global log aggregation system
file_storage = FileLogStorage()
sqlite_storage = SQLiteLogStorage()
log_aggregator = LogAggregator([file_storage, sqlite_storage])
log_analytics = LogAnalytics(sqlite_storage)


async def initialize_log_aggregation():
    """Initialize the log aggregation system."""
    await log_aggregator.start()


def get_log_aggregator() -> LogAggregator:
    """Get the global log aggregator."""
    return log_aggregator


def get_log_analytics() -> LogAnalytics:
    """Get the log analytics service."""
    return log_analytics
