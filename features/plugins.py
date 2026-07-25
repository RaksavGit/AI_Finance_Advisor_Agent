"""
Plugin and MCP Integration Framework
Enables extensibility through plugins and Model Context Protocol.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Type
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json


class PluginType(Enum):
    """Types of plugins."""
    DATA_SOURCE = "data_source"  # Banking APIs, data imports
    NOTIFICATION = "notification"  # SMS, Email, Push
    ANALYTICS = "analytics"  # Data warehouse, BI tools
    ADVISOR = "advisor"  # Investment, tax, insurance
    INTEGRATION = "integration"  # Third-party services


@dataclass
class PluginConfig:
    """Configuration for a plugin."""
    name: str
    type: PluginType
    version: str
    enabled: bool = True
    config_data: Dict[str, Any] = None

    def __post_init__(self):
        if self.config_data is None:
            self.config_data = {}


class PluginInterface(ABC):
    """Base interface for all plugins."""

    def __init__(self, config: PluginConfig):
        self.config = config
        self.is_initialized = False
        self.last_execution: Optional[datetime] = None
        self.execution_count = 0
        self.error_count = 0

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the plugin."""
        pass

    @abstractmethod
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the plugin."""
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate plugin configuration."""
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """Get plugin metadata."""
        return {
            'name': self.config.name,
            'type': self.config.type.value,
            'version': self.config.version,
            'enabled': self.config.enabled,
            'is_initialized': self.is_initialized,
            'execution_count': self.execution_count,
            'error_count': self.error_count,
            'last_execution': self.last_execution.isoformat() if self.last_execution else None,
        }

    def on_error(self, error: Exception):
        """Handle plugin errors."""
        self.error_count += 1
        print(f"Error in plugin {self.config.name}: {str(error)}")


class PluginManager:
    """Manages plugin lifecycle and execution."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.plugins: Dict[str, PluginInterface] = {}
            cls._instance.plugin_registry: Dict[str, Type[PluginInterface]] = {}
        return cls._instance

    @classmethod
    def get_instance(cls):
        """Get singleton instance."""
        return cls()

    def register_plugin_class(self, name: str, plugin_class: Type[PluginInterface]):
        """Register a plugin class."""
        self.plugin_registry[name] = plugin_class

    def load_plugin(self, config: PluginConfig) -> bool:
        """Load and initialize a plugin."""
        if config.name in self.plugins:
            print(f"Plugin {config.name} already loaded")
            return False

        if config.name not in self.plugin_registry:
            print(f"Plugin class {config.name} not registered")
            return False

        plugin_class = self.plugin_registry[config.name]
        plugin = plugin_class(config)

        if not plugin.validate_config():
            print(f"Plugin {config.name} configuration is invalid")
            return False

        if not plugin.initialize():
            print(f"Failed to initialize plugin {config.name}")
            return False

        self.plugins[config.name] = plugin
        return True

    def unload_plugin(self, name: str) -> bool:
        """Unload a plugin."""
        if name in self.plugins:
            del self.plugins[name]
            return True
        return False

    def execute_plugin(self, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a plugin."""
        plugin = self.plugins.get(name)
        if not plugin:
            raise ValueError(f"Plugin {name} not loaded")

        if not plugin.config.enabled:
            raise ValueError(f"Plugin {name} is disabled")

        try:
            result = plugin.execute(data)
            plugin.execution_count += 1
            plugin.last_execution = datetime.now()
            return result
        except Exception as e:
            plugin.on_error(e)
            raise

    def get_plugin(self, name: str) -> Optional[PluginInterface]:
        """Get a plugin by name."""
        return self.plugins.get(name)

    def list_plugins(self) -> List[str]:
        """List all loaded plugins."""
        return list(self.plugins.keys())

    def get_plugins_by_type(self, plugin_type: PluginType) -> List[PluginInterface]:
        """Get all plugins of a specific type."""
        return [p for p in self.plugins.values() if p.config.type == plugin_type]

    def get_plugin_metrics(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Get metrics for plugins."""
        if name:
            plugin = self.plugins.get(name)
            return plugin.get_metadata() if plugin else {}
        else:
            return {
                name: plugin.get_metadata()
                for name, plugin in self.plugins.items()
            }


# Concrete Plugin Implementations

class BankingDataPlugin(PluginInterface):
    """Plugin for banking data integration."""

    def initialize(self) -> bool:
        self.is_initialized = True
        return True

    def validate_config(self) -> bool:
        return 'api_key' in self.config.config_data or 'mock_mode' in self.config.config_data

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Import banking data."""
        if self.config.config_data.get('mock_mode'):
            # Mock banking data
            return {
                'status': 'success',
                'transactions': [
                    {'date': '2024-07-01', 'category': 'Rent', 'amount': 28000},
                    {'date': '2024-07-05', 'category': 'Food', 'amount': 3000},
                ],
                'account_balance': 50000,
            }
        else:
            # Real API call would go here
            return {'status': 'success', 'transactions': []}


class NotificationPlugin(PluginInterface):
    """Plugin for sending notifications."""

    def initialize(self) -> bool:
        self.is_initialized = True
        return True

    def validate_config(self) -> bool:
        return 'notification_type' in self.config.config_data

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification."""
        notification_type = self.config.config_data.get('notification_type')
        message = data.get('message', '')

        print(f"📨 Sending {notification_type} notification: {message}")

        return {
            'status': 'sent',
            'type': notification_type,
            'message': message,
            'timestamp': datetime.now().isoformat(),
        }


class AnalyticsPlugin(PluginInterface):
    """Plugin for analytics and reporting."""

    def initialize(self) -> bool:
        self.is_initialized = True
        return True

    def validate_config(self) -> bool:
        return 'warehouse_type' in self.config.config_data

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send analytics data."""
        warehouse_type = self.config.config_data.get('warehouse_type')
        event_name = data.get('event_name', 'unknown_event')

        print(f"📊 Analytics event [{warehouse_type}]: {event_name}")

        return {
            'status': 'logged',
            'warehouse': warehouse_type,
            'event': event_name,
            'timestamp': datetime.now().isoformat(),
        }


class InvestmentAdvisorPlugin(PluginInterface):
    """Plugin for investment recommendations."""

    def initialize(self) -> bool:
        self.is_initialized = True
        return True

    def validate_config(self) -> bool:
        return 'advisor_type' in self.config.config_data

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate investment recommendations."""
        savings = data.get('monthly_savings', 0)
        risk_profile = data.get('risk_profile', 'moderate')

        allocations = {
            'stocks': 0.60,
            'bonds': 0.30,
            'cash': 0.10,
        } if risk_profile == 'moderate' else {
            'stocks': 0.80,
            'bonds': 0.15,
            'cash': 0.05,
        }

        return {
            'status': 'success',
            'recommended_allocation': allocations,
            'monthly_investment': savings,
            'expected_annual_return': savings * 12 * 0.07,  # 7% average
        }


class DataExportPlugin(PluginInterface):
    """Plugin for exporting financial data to various formats."""

    def initialize(self) -> bool:
        self.is_initialized = True
        return True

    def validate_config(self) -> bool:
        return 'export_formats' in self.config.config_data

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Export financial data to specified format."""
        export_format = data.get('format', 'csv')
        expenses = data.get('expenses', {})
        income = data.get('monthly_income', 0)

        export_data = {
            'monthly_income': income,
            'total_expenses': sum(expenses.values()),
            'expenses_breakdown': expenses,
            'export_date': datetime.now().isoformat(),
        }

        if export_format == 'csv':
            csv_content = "Category,Amount\n"
            for category, amount in expenses.items():
                csv_content += f"{category},₹{amount:,.0f}\n"
            csv_content += f"TOTAL_EXPENSES,₹{sum(expenses.values()):,.0f}\n"
            csv_content += f"MONTHLY_INCOME,₹{income:,.0f}\n"
            return {
                'status': 'success',
                'format': 'csv',
                'data': csv_content,
                'filename': f'financial_data_{datetime.now().strftime("%Y%m%d")}.csv'
            }

        elif export_format == 'json':
            return {
                'status': 'success',
                'format': 'json',
                'data': json.dumps(export_data, indent=2),
                'filename': f'financial_data_{datetime.now().strftime("%Y%m%d")}.json'
            }

        else:
            return {
                'status': 'error',
                'message': f'Unsupported export format: {export_format}',
                'supported_formats': ['csv', 'json']
            }


class MCPServer:
    """Model Context Protocol Server for tool/resource exposure."""

    def __init__(self):
        self.resources: Dict[str, Dict[str, Any]] = {}
        self.tools: Dict[str, Dict[str, Any]] = {}

    def register_resource(self, name: str, resource_schema: Dict[str, Any]):
        """Register a resource for MCP."""
        self.resources[name] = resource_schema

    def register_tool(self, name: str, tool_schema: Dict[str, Any]):
        """Register a tool for MCP."""
        self.tools[name] = tool_schema

    def get_resources_schema(self) -> Dict[str, Any]:
        """Get all resources schema for MCP."""
        return {
            'resources': list(self.resources.keys()),
            'schemas': self.resources,
        }

    def get_tools_schema(self) -> Dict[str, Any]:
        """Get all tools schema for MCP."""
        return {
            'tools': list(self.tools.keys()),
            'schemas': self.tools,
        }

    def get_mcp_schema(self) -> Dict[str, Any]:
        """Get complete MCP schema."""
        return {
            'resources': self.get_resources_schema(),
            'tools': self.get_tools_schema(),
        }


def setup_mcp_server() -> MCPServer:
    """Setup MCP server with standard resources and tools."""
    mcp = MCPServer()

    # Register Resources
    mcp.register_resource('expense_data', {
        'name': 'expense_data',
        'description': 'Get customer expense data',
        'schema': {
            'type': 'object',
            'properties': {
                'monthly_income': {'type': 'number'},
                'expenses': {'type': 'object'},
            }
        }
    })

    mcp.register_resource('recommendations', {
        'name': 'recommendations',
        'description': 'Get prioritized recommendations',
        'schema': {
            'type': 'array',
            'items': {'type': 'object'}
        }
    })

    mcp.register_resource('chat_history', {
        'name': 'chat_history',
        'description': 'Access conversation history',
        'schema': {'type': 'array'}
    })

    # Register Tools
    mcp.register_tool('analyze_expenses', {
        'name': 'analyze_expenses',
        'description': 'Run expense analysis',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'income': {'type': 'number'},
                'expenses': {'type': 'object'},
            },
            'required': ['income', 'expenses']
        }
    })

    mcp.register_tool('generate_recommendations', {
        'name': 'generate_recommendations',
        'description': 'Create savings suggestions',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'analysis_data': {'type': 'object'},
            }
        }
    })

    mcp.register_tool('chat', {
        'name': 'chat',
        'description': 'Process natural language queries',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'query': {'type': 'string'},
            },
            'required': ['query']
        }
    })

    return mcp
