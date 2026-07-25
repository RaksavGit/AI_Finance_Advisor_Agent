"""
Hooks and Plugin Integration Framework
Implements event-driven architecture with hook points.
"""

from enum import Enum
from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid


class HookType(Enum):
    """Types of hooks in the system."""
    # Lifecycle hooks
    BEFORE_SESSION_INIT = "before_session_init"
    AFTER_SESSION_INIT = "after_session_init"
    BEFORE_SESSION_END = "before_session_end"
    AFTER_SESSION_END = "after_session_end"

    # Analysis hooks
    BEFORE_ANALYSIS = "before_analysis"
    AFTER_ANALYSIS = "after_analysis"
    ON_HIGH_SPENDING_DETECTED = "on_high_spending_detected"

    # Recommendation hooks
    BEFORE_RECOMMENDATION = "before_recommendation"
    AFTER_RECOMMENDATION = "after_recommendation"
    ON_RECOMMENDATION_GENERATED = "on_recommendation_generated"

    # Chat hooks
    BEFORE_CHAT = "before_chat"
    AFTER_CHAT = "after_chat"
    ON_INTENT_DETECTED = "on_intent_detected"

    # Data hooks
    ON_DATA_VALIDATE = "on_data_validate"
    ON_DATA_MODIFIED = "on_data_modified"
    ON_ERROR = "on_error"


@dataclass
class HookContext:
    """Context passed to hook handlers."""
    hook_type: HookType
    hook_id: str
    timestamp: datetime
    session_id: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            'hook_type': self.hook_type.value,
            'hook_id': self.hook_id,
            'timestamp': self.timestamp.isoformat(),
            'session_id': self.session_id,
            'data': self.data,
            'metadata': self.metadata,
        }


class HookHandler:
    """Represents a hook handler."""

    def __init__(self, name: str, hook_type: HookType, callback: Callable, priority: int = 0):
        self.name = name
        self.hook_type = hook_type
        self.callback = callback
        self.priority = priority  # Higher priority runs first
        self.enabled = True
        self.execution_count = 0
        self.error_count = 0

    def execute(self, context: HookContext) -> bool:
        """Execute the hook handler."""
        if not self.enabled:
            return False

        try:
            self.callback(context)
            self.execution_count += 1
            return True
        except Exception as e:
            self.error_count += 1
            print(f"Error in hook handler {self.name}: {str(e)}")
            return False

    def get_metrics(self) -> Dict[str, Any]:
        """Get handler metrics."""
        return {
            'name': self.name,
            'hook_type': self.hook_type.value,
            'enabled': self.enabled,
            'execution_count': self.execution_count,
            'error_count': self.error_count,
            'success_rate': (self.execution_count - self.error_count) / self.execution_count * 100 if self.execution_count > 0 else 0,
        }


class HookManager:
    """Central manager for hook registration and execution."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.handlers: Dict[HookType, List[HookHandler]] = {ht: [] for ht in HookType}
            cls._instance.hook_history: List[HookContext] = []
            cls._instance.max_history = 1000
        return cls._instance

    @classmethod
    def get_instance(cls):
        """Get singleton instance."""
        return cls()

    def register(self, name: str, hook_type: HookType, callback: Callable, priority: int = 0) -> HookHandler:
        """Register a hook handler."""
        handler = HookHandler(name, hook_type, callback, priority)
        self.handlers[hook_type].append(handler)

        # Sort by priority (highest first)
        self.handlers[hook_type].sort(key=lambda h: h.priority, reverse=True)

        return handler

    def trigger(self, hook_type: HookType, session_id: str, data: Dict[str, Any], metadata: Dict[str, Any] = None) -> List[bool]:
        """Trigger all handlers for a hook type."""
        context = HookContext(
            hook_type=hook_type,
            hook_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            session_id=session_id,
            data=data,
            metadata=metadata or {}
        )

        results = []
        for handler in self.handlers[hook_type]:
            result = handler.execute(context)
            results.append(result)

        # Store in history
        self._add_to_history(context)

        return results

    def _add_to_history(self, context: HookContext):
        """Add hook execution to history."""
        self.hook_history.append(context)

        # Trim history if too large
        if len(self.hook_history) > self.max_history:
            self.hook_history = self.hook_history[-self.max_history:]

    def unregister(self, hook_type: HookType, handler_name: str) -> bool:
        """Unregister a hook handler."""
        handlers = self.handlers[hook_type]
        for i, handler in enumerate(handlers):
            if handler.name == handler_name:
                handlers.pop(i)
                return True
        return False

    def disable_handler(self, hook_type: HookType, handler_name: str) -> bool:
        """Disable a hook handler."""
        for handler in self.handlers[hook_type]:
            if handler.name == handler_name:
                handler.enabled = False
                return True
        return False

    def enable_handler(self, hook_type: HookType, handler_name: str) -> bool:
        """Enable a hook handler."""
        for handler in self.handlers[hook_type]:
            if handler.name == handler_name:
                handler.enabled = True
                return True
        return False

    def get_handlers(self, hook_type: HookType) -> List[HookHandler]:
        """Get all handlers for a hook type."""
        return self.handlers[hook_type]

    def get_handler_metrics(self, hook_type: Optional[HookType] = None) -> Dict[str, Any]:
        """Get metrics for all handlers or specific hook type."""
        if hook_type:
            return {
                handler.name: handler.get_metrics()
                for handler in self.handlers[hook_type]
            }
        else:
            return {
                ht.value: {
                    handler.name: handler.get_metrics()
                    for handler in self.handlers[ht]
                }
                for ht in HookType
            }

    def get_hook_history(self, hook_type: Optional[HookType] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get hook execution history."""
        history = self.hook_history

        if hook_type:
            history = [h for h in history if h.hook_type == hook_type]

        return [h.to_dict() for h in history[-limit:]]


# Pre-built Hook Handlers

def create_high_spending_alert_hook() -> Callable:
    """Create a hook for high spending alerts."""
    def handler(context: HookContext):
        data = context.data
        if data.get('high_spending_detected'):
            categories = data.get('high_spending_categories', [])
            print(f"🚨 Alert: High spending detected in {len(categories)} categories")

    return handler


def create_logging_hook() -> Callable:
    """Create a hook for logging events."""
    def handler(context: HookContext):
        print(f"[{context.hook_type.value}] Session: {context.session_id} | Data: {str(context.data)[:100]}")

    return handler


def create_validation_hook() -> Callable:
    """Create a hook for data validation."""
    def handler(context: HookContext):
        data = context.data
        # Validate data structure
        if 'income' in data and data['income'] < 0:
            raise ValueError("Income cannot be negative")
        if 'expenses' in data and isinstance(data['expenses'], dict):
            for cat, amount in data['expenses'].items():
                if amount < 0:
                    raise ValueError(f"Expense {cat} cannot be negative")

    return handler


def create_notification_hook() -> Callable:
    """Create a hook for sending notifications."""
    def handler(context: HookContext):
        if context.hook_type == HookType.ON_HIGH_SPENDING_DETECTED:
            print(f"📧 Notification: High spending alert sent to user")

    return handler


def create_analytics_hook() -> Callable:
    """Create a hook for analytics tracking."""
    def handler(context: HookContext):
        print(f"📊 Analytics: {context.hook_type.value} event tracked")

    return handler
