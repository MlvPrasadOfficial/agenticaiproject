"""
Error tracking and alerting system for Enterprise Insights Copilot
Provides comprehensive error monitoring, tracking, and alerting capabilities.
"""

import asyncio
import json
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import traceback
import os

from app.utils.logging import get_logger
from app.utils.metrics import metrics


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertChannel(Enum):
    """Alert delivery channels."""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    LOG = "log"


@dataclass
class ErrorEvent:
    """Error event data structure."""
    error_id: str
    timestamp: datetime
    error_type: str
    error_message: str
    component: str
    trace_id: Optional[str]
    stack_trace: Optional[str]
    context: Dict[str, Any]
    severity: AlertSeverity
    resolved: bool = False
    resolution_time: Optional[datetime] = None


@dataclass
class AlertRule:
    """Alert rule configuration."""
    rule_id: str
    name: str
    description: str
    condition: str  # Expression to evaluate
    severity: AlertSeverity
    channels: List[AlertChannel]
    throttle_minutes: int = 5
    enabled: bool = True


class ErrorTracker:
    """Error tracking and management system."""
    
    def __init__(self):
        self.logger = get_logger()
        self.error_history: List[ErrorEvent] = []
        self.alert_rules: List[AlertRule] = []
        self.last_alert_times: Dict[str, datetime] = {}
        self.error_patterns: Dict[str, int] = {}
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Setup default alert rules."""
        default_rules = [
            AlertRule(
                rule_id="high_error_rate",
                name="High Error Rate",
                description="Alert when error rate exceeds threshold",
                condition="error_count_per_minute > 10",
                severity=AlertSeverity.HIGH,
                channels=[AlertChannel.EMAIL, AlertChannel.LOG],
                throttle_minutes=10
            ),
            AlertRule(
                rule_id="critical_error",
                name="Critical Error",
                description="Alert on critical errors",
                condition="severity == 'critical'",
                severity=AlertSeverity.CRITICAL,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.LOG],
                throttle_minutes=0  # No throttling for critical errors
            ),
            AlertRule(
                rule_id="repeated_error",
                name="Repeated Error Pattern",
                description="Alert when same error occurs repeatedly",
                condition="error_pattern_count > 5",
                severity=AlertSeverity.MEDIUM,
                channels=[AlertChannel.EMAIL, AlertChannel.LOG],
                throttle_minutes=15
            )
        ]
        
        self.alert_rules.extend(default_rules)
    
    async def track_error(self, 
                         error: Exception, 
                         component: str,
                         context: Dict[str, Any] = None,
                         trace_id: str = None,
                         severity: AlertSeverity = AlertSeverity.MEDIUM) -> ErrorEvent:
        """Track an error event."""
        error_id = f"{component}_{int(datetime.utcnow().timestamp() * 1000000)}"
        
        error_event = ErrorEvent(
            error_id=error_id,
            timestamp=datetime.utcnow(),
            error_type=error.__class__.__name__,
            error_message=str(error),
            component=component,
            trace_id=trace_id,
            stack_trace=traceback.format_exc(),
            context=context or {},
            severity=severity
        )
        
        # Store error
        self.error_history.append(error_event)
        
        # Update error patterns
        pattern_key = f"{error_event.error_type}:{error_event.component}"
        self.error_patterns[pattern_key] = self.error_patterns.get(pattern_key, 0) + 1
        
        # Record metrics
        metrics.record_error(error_event.error_type, component)
        
        # Log error
        self.logger.error(
            f"Error tracked: {error_event.error_message}",
            error_id=error_id,
            error_type=error_event.error_type,
            component=component,
            severity=severity.value,
            error=error
        )
        
        # Check alert rules
        await self._evaluate_alert_rules(error_event)
        
        # Cleanup old errors (keep last 1000)
        if len(self.error_history) > 1000:
            self.error_history = self.error_history[-1000:]
        
        return error_event
    
    async def _evaluate_alert_rules(self, error_event: ErrorEvent):
        """Evaluate alert rules against the error event."""
        current_time = datetime.utcnow()
        
        for rule in self.alert_rules:
            if not rule.enabled:
                continue
            
            # Check throttling
            last_alert_key = f"{rule.rule_id}:{error_event.component}"
            last_alert_time = self.last_alert_times.get(last_alert_key)
            
            if (last_alert_time and 
                (current_time - last_alert_time).total_seconds() < rule.throttle_minutes * 60):
                continue
            
            # Evaluate rule condition
            should_alert = await self._evaluate_condition(rule.condition, error_event)
            
            if should_alert:
                await self._send_alert(rule, error_event)
                self.last_alert_times[last_alert_key] = current_time
    
    async def _evaluate_condition(self, condition: str, error_event: ErrorEvent) -> bool:
        """Evaluate alert condition."""
        try:
            # Simple condition evaluation (in production, use a proper expression evaluator)
            context = {
                "error_count_per_minute": self._get_error_count_per_minute(),
                "severity": error_event.severity.value,
                "error_type": error_event.error_type,
                "component": error_event.component,
                "error_pattern_count": self._get_pattern_count(error_event)
            }
            
            # Basic condition parsing
            if "error_count_per_minute > 10" in condition:
                return context["error_count_per_minute"] > 10
            elif "severity == 'critical'" in condition:
                return context["severity"] == "critical"
            elif "error_pattern_count > 5" in condition:
                return context["error_pattern_count"] > 5
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to evaluate alert condition: {condition}", error=e)
            return False
    
    def _get_error_count_per_minute(self) -> int:
        """Get error count in the last minute."""
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        recent_errors = [e for e in self.error_history if e.timestamp > one_minute_ago]
        return len(recent_errors)
    
    def _get_pattern_count(self, error_event: ErrorEvent) -> int:
        """Get count for this error pattern."""
        pattern_key = f"{error_event.error_type}:{error_event.component}"
        return self.error_patterns.get(pattern_key, 0)
    
    async def _send_alert(self, rule: AlertRule, error_event: ErrorEvent):
        """Send alert through configured channels."""
        alert_data = {
            "rule": rule.name,
            "severity": rule.severity.value,
            "error_event": asdict(error_event),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for channel in rule.channels:
            try:
                if channel == AlertChannel.LOG:
                    await self._send_log_alert(alert_data)
                elif channel == AlertChannel.EMAIL:
                    await self._send_email_alert(alert_data)
                elif channel == AlertChannel.WEBHOOK:
                    await self._send_webhook_alert(alert_data)
                elif channel == AlertChannel.SLACK:
                    await self._send_slack_alert(alert_data)
                    
            except Exception as e:
                self.logger.error(f"Failed to send alert via {channel.value}", error=e)
    
    async def _send_log_alert(self, alert_data: Dict[str, Any]):
        """Send alert via logging."""
        self.logger.warning(
            f"ALERT: {alert_data['rule']} - {alert_data['error_event']['error_message']}",
            alert_rule=alert_data['rule'],
            severity=alert_data['severity'],
            error_id=alert_data['error_event']['error_id'],
            component=alert_data['error_event']['component']
        )
    
    async def _send_email_alert(self, alert_data: Dict[str, Any]):
        """Send alert via email."""
        try:
            # Email configuration from environment
            smtp_server = os.getenv("SMTP_SERVER", "localhost")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_username = os.getenv("SMTP_USERNAME")
            smtp_password = os.getenv("SMTP_PASSWORD")
            alert_email_to = os.getenv("ALERT_EMAIL_TO", "admin@example.com")
            alert_email_from = os.getenv("ALERT_EMAIL_FROM", "alerts@enterpriseinsights.com")
            
            if not smtp_username or not smtp_password:
                self.logger.warning("Email alert skipped: SMTP credentials not configured")
                return
            
            # Create email message
            msg = MimeMultipart()
            msg['From'] = alert_email_from
            msg['To'] = alert_email_to
            msg['Subject'] = f"Enterprise Insights Alert: {alert_data['rule']}"
            
            # Email body
            body = f"""
            Alert: {alert_data['rule']}
            Severity: {alert_data['severity']}
            Time: {alert_data['timestamp']}
            
            Error Details:
            - Error ID: {alert_data['error_event']['error_id']}
            - Type: {alert_data['error_event']['error_type']}
            - Message: {alert_data['error_event']['error_message']}
            - Component: {alert_data['error_event']['component']}
            - Trace ID: {alert_data['error_event']['trace_id']}
            
            Stack Trace:
            {alert_data['error_event']['stack_trace']}
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Email alert sent for rule: {alert_data['rule']}")
            
        except Exception as e:
            self.logger.error("Failed to send email alert", error=e)
    
    async def _send_webhook_alert(self, alert_data: Dict[str, Any]):
        """Send alert via webhook."""
        try:
            webhook_url = os.getenv("ALERT_WEBHOOK_URL")
            if not webhook_url:
                self.logger.warning("Webhook alert skipped: ALERT_WEBHOOK_URL not configured")
                return
            
            # In a real implementation, this would use aiohttp or similar
            self.logger.info(f"Webhook alert would be sent to: {webhook_url}")
            
        except Exception as e:
            self.logger.error("Failed to send webhook alert", error=e)
    
    async def _send_slack_alert(self, alert_data: Dict[str, Any]):
        """Send alert via Slack."""
        try:
            slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
            if not slack_webhook_url:
                self.logger.warning("Slack alert skipped: SLACK_WEBHOOK_URL not configured")
                return
            
            # In a real implementation, this would send to Slack
            self.logger.info(f"Slack alert would be sent for rule: {alert_data['rule']}")
            
        except Exception as e:
            self.logger.error("Failed to send Slack alert", error=e)
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for the specified time period."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_errors = [e for e in self.error_history if e.timestamp > cutoff_time]
        
        # Group by component
        errors_by_component = {}
        for error in recent_errors:
            component = error.component
            if component not in errors_by_component:
                errors_by_component[component] = []
            errors_by_component[component].append(error)
        
        # Group by severity
        errors_by_severity = {}
        for error in recent_errors:
            severity = error.severity.value
            errors_by_severity[severity] = errors_by_severity.get(severity, 0) + 1
        
        return {
            "total_errors": len(recent_errors),
            "errors_by_component": {k: len(v) for k, v in errors_by_component.items()},
            "errors_by_severity": errors_by_severity,
            "time_period_hours": hours,
            "most_common_patterns": self._get_top_error_patterns(recent_errors),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _get_top_error_patterns(self, errors: List[ErrorEvent]) -> List[Dict[str, Any]]:
        """Get the most common error patterns."""
        pattern_counts = {}
        
        for error in errors:
            pattern = f"{error.error_type} in {error.component}"
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        # Sort by count and return top 10
        sorted_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"pattern": pattern, "count": count} for pattern, count in sorted_patterns[:10]]
    
    def add_alert_rule(self, rule: AlertRule):
        """Add a new alert rule."""
        self.alert_rules.append(rule)
        self.logger.info(f"Added alert rule: {rule.name}")
    
    def remove_alert_rule(self, rule_id: str):
        """Remove an alert rule."""
        self.alert_rules = [r for r in self.alert_rules if r.rule_id != rule_id]
        self.logger.info(f"Removed alert rule: {rule_id}")
    
    def resolve_error(self, error_id: str, resolution_notes: str = None):
        """Mark an error as resolved."""
        for error in self.error_history:
            if error.error_id == error_id:
                error.resolved = True
                error.resolution_time = datetime.utcnow()
                
                self.logger.info(
                    f"Error resolved: {error_id}",
                    error_id=error_id,
                    resolution_notes=resolution_notes
                )
                break


class ErrorTrackingMiddleware:
    """Middleware for automatic error tracking."""
    
    def __init__(self, error_tracker: ErrorTracker):
        self.error_tracker = error_tracker
    
    async def __call__(self, request, call_next):
        """Middleware function for FastAPI."""
        try:
            response = await call_next(request)
            return response
            
        except Exception as e:
            # Track the error
            await self.error_tracker.track_error(
                error=e,
                component="http_middleware",
                context={
                    "method": request.method,
                    "url": str(request.url),
                    "headers": dict(request.headers)
                },
                severity=AlertSeverity.HIGH
            )
            
            # Re-raise the exception
            raise


# Global error tracker instance
error_tracker = ErrorTracker()


def get_error_tracker() -> ErrorTracker:
    """Get the global error tracker instance."""
    return error_tracker


# Convenience decorators
def track_errors(component: str, severity: AlertSeverity = AlertSeverity.MEDIUM):
    """Decorator to automatically track errors in functions."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                await error_tracker.track_error(
                    error=e,
                    component=component,
                    context={"function": func.__name__},
                    severity=severity
                )
                raise
        
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                asyncio.create_task(error_tracker.track_error(
                    error=e,
                    component=component,
                    context={"function": func.__name__},
                    severity=severity
                ))
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator
