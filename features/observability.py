"""
Observability and Traceability Framework
Implements comprehensive logging, metrics, and tracing.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import time


class LogLevel(Enum):
    """Log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class EventType(Enum):
    """Types of events to trace."""
    SESSION_INIT = "session_initialized"
    SESSION_END = "session_ended"
    ANALYSIS_START = "analysis_started"
    ANALYSIS_COMPLETE = "analysis_completed"
    RECOMMENDATION_START = "recommendation_started"
    RECOMMENDATION_COMPLETE = "recommendation_completed"
    CHAT_QUERY = "chat_query"
    CHAT_RESPONSE = "chat_response"
    ERROR_OCCURRED = "error_occurred"
    VALIDATION_FAILED = "validation_failed"
    RULE_VIOLATION = "rule_violation"
    HIGH_SPENDING_DETECTED = "high_spending_detected"
    PLUGIN_EXECUTED = "plugin_executed"
    HOOK_TRIGGERED = "hook_triggered"


@dataclass
class LogEntry:
    """Represents a single log entry."""
    timestamp: datetime
    level: LogLevel
    message: str
    component: str
    session_id: str
    user_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level.value,
            'message': self.message,
            'component': self.component,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'data': self.data,
            'trace_id': self.trace_id,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)


@dataclass
class TraceEvent:
    """Represents a traced event."""
    event_type: EventType
    event_id: str
    session_id: str
    timestamp: datetime
    duration_ms: float = 0.0
    status: str = "completed"  # completed, failed, pending
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': self.event_type.value,
            'event_id': self.event_id,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat(),
            'duration_ms': self.duration_ms,
            'status': self.status,
            'data': self.data,
            'error': self.error,
        }


@dataclass
class Metric:
    """Represents a system metric."""
    name: str
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat(),
            'tags': self.tags,
        }


class TraceLogger:
    """Central logger for tracing application execution."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logs: List[LogEntry] = []
            cls._instance.events: List[TraceEvent] = []
            cls._instance.max_logs = 10000
            cls._instance.max_events = 5000
        return cls._instance

    @classmethod
    def get_instance(cls):
        """Get singleton instance."""
        return cls()

    def log(self, level: LogLevel, message: str, component: str, session_id: str,
            user_id: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> LogEntry:
        """Log a message."""
        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            message=message,
            component=component,
            session_id=session_id,
            user_id=user_id,
            data=data or {}
        )

        self.logs.append(entry)

        # Trim logs if too many
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]

        return entry

    def debug(self, message: str, component: str, session_id: str, **kwargs):
        return self.log(LogLevel.DEBUG, message, component, session_id, **kwargs)

    def info(self, message: str, component: str, session_id: str, **kwargs):
        return self.log(LogLevel.INFO, message, component, session_id, **kwargs)

    def warning(self, message: str, component: str, session_id: str, **kwargs):
        return self.log(LogLevel.WARNING, message, component, session_id, **kwargs)

    def error(self, message: str, component: str, session_id: str, **kwargs):
        return self.log(LogLevel.ERROR, message, component, session_id, **kwargs)

    def critical(self, message: str, component: str, session_id: str, **kwargs):
        return self.log(LogLevel.CRITICAL, message, component, session_id, **kwargs)

    def trace_event(self, event_type: EventType, session_id: str,
                   data: Optional[Dict[str, Any]] = None,
                   duration_ms: float = 0.0,
                   status: str = "completed",
                   error: Optional[str] = None) -> TraceEvent:
        """Record a trace event."""
        event = TraceEvent(
            event_type=event_type,
            event_id=str(uuid.uuid4()),
            session_id=session_id,
            timestamp=datetime.now(),
            duration_ms=duration_ms,
            status=status,
            data=data or {},
            error=error
        )

        self.events.append(event)

        # Trim events if too many
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]

        return event

    def get_logs(self, session_id: Optional[str] = None, level: Optional[LogLevel] = None,
                limit: int = 100) -> List[Dict[str, Any]]:
        """Get logs, optionally filtered."""
        logs = self.logs

        if session_id:
            logs = [l for l in logs if l.session_id == session_id]

        if level:
            logs = [l for l in logs if l.level == level]

        return [l.to_dict() for l in logs[-limit:]]

    def get_events(self, session_id: Optional[str] = None,
                  event_type: Optional[EventType] = None,
                  limit: int = 100) -> List[Dict[str, Any]]:
        """Get events, optionally filtered."""
        events = self.events

        if session_id:
            events = [e for e in events if e.session_id == session_id]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return [e.to_dict() for e in events[-limit:]]

    def get_session_trace(self, session_id: str) -> Dict[str, Any]:
        """Get complete trace for a session."""
        session_logs = [l for l in self.logs if l.session_id == session_id]
        session_events = [e for e in self.events if e.session_id == session_id]

        return {
            'session_id': session_id,
            'log_count': len(session_logs),
            'event_count': len(session_events),
            'logs': [l.to_dict() for l in session_logs[-50:]],
            'events': [e.to_dict() for e in session_events[-50:]],
            'start_time': session_events[0].timestamp.isoformat() if session_events else None,
            'end_time': session_events[-1].timestamp.isoformat() if session_events else None,
        }

    def export_logs(self, session_id: Optional[str] = None) -> str:
        """Export logs as JSON."""
        logs = self.get_logs(session_id=session_id, limit=10000)
        return json.dumps(logs, indent=2, default=str)

    def export_events(self, session_id: Optional[str] = None) -> str:
        """Export events as JSON."""
        events = self.get_events(session_id=session_id, limit=10000)
        return json.dumps(events, indent=2, default=str)


class MetricsCollector:
    """Collects and aggregates system metrics."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.metrics: List[Metric] = []
            cls._instance.max_metrics = 10000
            cls._instance.aggregated: Dict[str, Dict[str, Any]] = {}
        return cls._instance

    @classmethod
    def get_instance(cls):
        """Get singleton instance."""
        return cls()

    def record_metric(self, name: str, value: float, unit: str = "",
                     tags: Optional[Dict[str, str]] = None) -> Metric:
        """Record a metric."""
        metric = Metric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            tags=tags or {}
        )

        self.metrics.append(metric)

        # Trim metrics if too many
        if len(self.metrics) > self.max_metrics:
            self.metrics = self.metrics[-self.max_metrics:]

        self._update_aggregated(name, value)

        return metric

    def _update_aggregated(self, name: str, value: float):
        """Update aggregated statistics."""
        if name not in self.aggregated:
            self.aggregated[name] = {
                'count': 0,
                'sum': 0,
                'min': float('inf'),
                'max': float('-inf'),
                'average': 0,
            }

        stats = self.aggregated[name]
        stats['count'] += 1
        stats['sum'] += value
        stats['min'] = min(stats['min'], value)
        stats['max'] = max(stats['max'], value)
        stats['average'] = stats['sum'] / stats['count']

    def get_metrics(self, name: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get metrics."""
        metrics = self.metrics

        if name:
            metrics = [m for m in metrics if m.name == name]

        return [m.to_dict() for m in metrics[-limit:]]

    def get_aggregated_stats(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Get aggregated statistics."""
        if name:
            return self.aggregated.get(name, {})
        return self.aggregated

    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get metrics for dashboard display."""
        return {
            'total_metrics_recorded': len(self.metrics),
            'unique_metrics': len(self.aggregated),
            'recent_metrics': [m.to_dict() for m in self.metrics[-10:]],
            'aggregated_stats': {
                name: {
                    'count': stats['count'],
                    'average': round(stats['average'], 2),
                    'min': stats['min'],
                    'max': stats['max'],
                }
                for name, stats in self.aggregated.items()
            }
        }


class PerformanceMonitor:
    """Monitors application performance."""

    def __init__(self):
        self.timers: Dict[str, float] = {}
        self.metrics = MetricsCollector.get_instance()

    def start_timer(self, name: str):
        """Start a performance timer."""
        self.timers[name] = time.time()

    def end_timer(self, name: str, tags: Optional[Dict[str, str]] = None) -> float:
        """End a performance timer and record metric."""
        if name not in self.timers:
            return 0

        elapsed_ms = (time.time() - self.timers[name]) * 1000
        self.metrics.record_metric(f'performance_{name}', elapsed_ms, 'ms', tags)

        del self.timers[name]
        return elapsed_ms

    def time_block(self, name: str, func, *args, **kwargs):
        """Time a function execution."""
        self.start_timer(name)
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            self.end_timer(name)


class HealthCheck:
    """Health check for system monitoring."""

    @staticmethod
    def check_health() -> Dict[str, Any]:
        """Perform system health check."""
        logger = TraceLogger.get_instance()
        metrics = MetricsCollector.get_instance()

        # Check for recent errors
        recent_errors = logger.get_logs(level=LogLevel.ERROR, limit=100)
        error_rate = len(recent_errors) / max(len(logger.logs), 1)

        # Check metrics
        perf_stats = metrics.get_aggregated_stats()

        return {
            'status': 'healthy' if error_rate < 0.05 else 'degraded' if error_rate < 0.1 else 'unhealthy',
            'error_rate': error_rate,
            'total_logs': len(logger.logs),
            'total_events': len(logger.events),
            'total_metrics': len(metrics.metrics),
            'recent_errors': len(recent_errors),
            'performance': {
                name: stats.get('average', 0)
                for name, stats in perf_stats.items()
            }
        }
