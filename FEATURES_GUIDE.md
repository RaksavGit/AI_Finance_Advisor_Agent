# AI Finance Advisor - Features Guide

**Version**: 2.0 with Enterprise Features  
**Date**: July 25, 2026

---

## Table of Contents

1. [Skills & Subagents](#1-skills--subagents)
2. [Hooks Framework](#2-hooks-framework)
3. [MCP & Plugin Integration](#3-mcp--plugin-integration)
4. [Governance Framework](#4-governance-framework)
5. [Observability & Traceability](#5-observability--traceability)
6. [Deployment Architecture](#6-deployment-architecture)
7. [Integration Guide](#7-integration-guide)

---

## 1. Skills & Subagents

### Overview

Skills are modular, reusable components that perform specific tasks. Subagents compose multiple skills into specialized agents.

### Core Skills

#### ExpenseAnalyzerSkill
**Purpose**: Analyzes customer expenses and calculates financial metrics

```python
from features.skills import ExpenseAnalyzerSkill, SkillRegistry

registry = SkillRegistry.get_instance()
skill = ExpenseAnalyzerSkill()
registry.register_skill(skill)

# Execute
result = registry.execute_skill('expense_analyzer', {
    'income': 100000,
    'expenses': {'Rent': 28000, 'Food': 12000, ...}
}, session_id='user_123')

# Result includes:
# - total_expenses
# - net_savings
# - savings_percentage
# - category_percentages
```

#### RecommendationGeneratorSkill
**Purpose**: Generates prioritized savings recommendations

```python
result = registry.execute_skill('recommendation_generator', {
    'analysis': analysis_results,
    'benchmarks': {}
}, session_id='user_123')

# Result includes:
# - recommendations[]
# - total_potential_savings
# - recommendation_count
```

#### ChatResponderSkill
**Purpose**: Responds to user queries using financial data

```python
result = registry.execute_skill('chat_responder', {
    'query': 'How can I save more?',
    'analysis': analysis_data,
    'recommendations': recommendations_data
}, session_id='user_123')

# Result includes:
# - response
# - query
# - intent
```

#### GoalTrackerSkill
**Purpose**: Tracks and monitors financial goals

```python
result = registry.execute_skill('goal_tracker', {
    'goals': [
        {'name': 'Emergency Fund', 'target_amount': 10000, 'current_amount': 3000},
        {'name': 'Vacation', 'target_amount': 5000, 'current_amount': 2000}
    ],
    'savings_percentage': 16.0
}, session_id='user_123')
```

#### BudgetPlannerSkill
**Purpose**: Creates and analyzes budgets

```python
result = registry.execute_skill('budget_planner', {
    'income': 100000,
    'total_expenses': 84000,
    'target_savings_rate': 0.20
}, session_id='user_123')

# Result includes:
# - recommended_budget
# - current_spending
# - variance
# - status (under_budget or over_budget)
```

### Creating Custom Skills

```python
from features.skills import BaseSkill, SkillMetadata, SkillType, SkillExecutionContext
from typing import Dict, Any

class CustomSkill(BaseSkill):
    def __init__(self):
        metadata = SkillMetadata(
            name="custom_skill",
            type=SkillType.ADVISOR,
            version="1.0",
            description="Custom financial analysis skill",
            dependencies=[]
        )
        super().__init__(metadata)
    
    def execute(self, context: SkillExecutionContext) -> Dict[str, Any]:
        # Your custom logic here
        return {'result': 'success'}

# Register and use
skill = CustomSkill()
registry.register_skill(skill)
```

### Subagents

Subagents compose multiple skills into domain-specific agents:

```python
from features.skills import Subagent

# Create analysis subagent
analysis_subagent = Subagent("analysis_subagent", "Comprehensive expense analysis")
analysis_subagent.add_skill(registry.get_skill("expense_analyzer"))
analysis_subagent.add_skill(registry.get_skill("budget_planner"))
analysis_subagent.set_execution_sequence(["expense_analyzer", "budget_planner"])
registry.register_subagent(analysis_subagent)

# Execute subagent
result = registry.execute_subagent('analysis_subagent', input_data, session_id)
```

### Skill Metrics

```python
# Get individual skill metrics
metrics = registry.get_skill('expense_analyzer').get_metrics()
# Returns: total_executions, successful, failed, success_rate, average_time_ms

# Get all system metrics
system_metrics = registry.get_system_metrics()
# Returns: total_skills, subagents, metrics for each
```

---

## 2. Hooks Framework

### Overview

Hooks are event-driven callbacks that execute at specific points in the application lifecycle.

### Hook Types

| Hook | Purpose | When Triggered |
|------|---------|----------------|
| `BEFORE_SESSION_INIT` | Pre-session initialization | Before user session starts |
| `AFTER_SESSION_INIT` | Post-session setup | After session initialized |
| `BEFORE_ANALYSIS` | Pre-analysis setup | Before expense analysis |
| `AFTER_ANALYSIS` | Post-analysis cleanup | After analysis completes |
| `ON_HIGH_SPENDING_DETECTED` | Alert generation | When category exceeds threshold |
| `BEFORE_RECOMMENDATION` | Pre-recommendation setup | Before generating recommendations |
| `AFTER_RECOMMENDATION` | Post-recommendation processing | After recommendations generated |
| `BEFORE_CHAT` | Pre-chat setup | Before chat response |
| `AFTER_CHAT` | Post-chat cleanup | After chat response |
| `ON_DATA_VALIDATE` | Data validation | During input validation |
| `ON_DATA_MODIFIED` | Data change handling | When user data changes |
| `ON_ERROR` | Error handling | When error occurs |

### Registering Hooks

```python
from features.hooks import HookManager, HookType

hook_manager = HookManager.get_instance()

# Simple hook
def my_hook(context):
    print(f"Event: {context.hook_type.value}")
    print(f"Session: {context.session_id}")
    print(f"Data: {context.data}")

hook_manager.register(
    name="my_hook",
    hook_type=HookType.AFTER_ANALYSIS,
    callback=my_hook,
    priority=100  # Higher priority runs first
)
```

### Triggering Hooks

```python
# Trigger hooks
hook_manager.trigger(
    HookType.AFTER_ANALYSIS,
    session_id='user_123',
    data={'results': analysis_results},
    metadata={'duration_ms': 150}
)
```

### Pre-built Hooks

```python
from features.hooks import (
    create_logging_hook,
    create_validation_hook,
    create_high_spending_alert_hook,
    create_notification_hook,
    create_analytics_hook
)

# Register pre-built hooks
hook_manager.register("logger", HookType.BEFORE_ANALYSIS, create_logging_hook())
hook_manager.register("validator", HookType.ON_DATA_VALIDATE, create_validation_hook())
hook_manager.register("alerter", HookType.ON_HIGH_SPENDING_DETECTED, create_high_spending_alert_hook())
```

---

## 3. MCP & Plugin Integration

### Overview

Plugins provide extensibility for integrations with third-party services. MCP (Model Context Protocol) exposes resources and tools.

### Plugin Types

| Type | Purpose | Examples |
|------|---------|----------|
| `DATA_SOURCE` | Import external data | Plaid banking, CSV uploads |
| `NOTIFICATION` | Send alerts | Email, SMS, Push |
| `ANALYTICS` | Track events | BigQuery, Mixpanel |
| `ADVISOR` | Generate advice | Investment, Tax, Insurance |
| `INTEGRATION` | Third-party services | Google Sheets, Slack |

### Using Plugins

```python
from features.plugins import (
    PluginManager, PluginConfig, PluginType,
    BankingDataPlugin, NotificationPlugin
)

plugin_manager = PluginManager.get_instance()

# Register plugin class
plugin_manager.register_plugin_class("banking_data", BankingDataPlugin)

# Load plugin
config = PluginConfig(
    name="banking_data",
    type=PluginType.DATA_SOURCE,
    version="1.0",
    enabled=True,
    config_data={'api_key': 'xxx', 'mock_mode': False}
)

plugin_manager.load_plugin(config)

# Execute plugin
result = plugin_manager.execute_plugin('banking_data', {
    'account_id': 'ACC_123'
})
```

### Creating Custom Plugins

```python
from features.plugins import PluginInterface, PluginConfig, PluginType

class MyCustomPlugin(PluginInterface):
    def initialize(self) -> bool:
        # Setup plugin
        self.is_initialized = True
        return True
    
    def validate_config(self) -> bool:
        # Validate configuration
        return 'required_field' in self.config.config_data
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Execute plugin logic
        return {'status': 'success', 'data': data}

# Register and use
plugin_manager.register_plugin_class("my_plugin", MyCustomPlugin)
```

### Built-in Plugins

#### BankingDataPlugin
Imports transaction data from banking APIs

```python
# Use with Plaid API
result = plugin_manager.execute_plugin('banking_data', {
    'plaid_token': 'public-xxx',
    'institution_id': 'ins_123'
})
```

#### NotificationPlugin
Sends notifications via multiple channels

```python
result = plugin_manager.execute_plugin('notifications', {
    'recipient': 'user@example.com',
    'message': 'Your spending alert: $500 on Shopping'
})
```

#### AnalyticsPlugin
Tracks events to analytics warehouse

```python
result = plugin_manager.execute_plugin('analytics', {
    'event_name': 'high_spending_detected',
    'category': 'Rent',
    'amount': 28000
})
```

#### InvestmentAdvisorPlugin
Recommends investment allocations

```python
result = plugin_manager.execute_plugin('investment_advisor', {
    'monthly_savings': 4000,
    'risk_profile': 'moderate'
})
# Returns: recommended_allocation, expected_return
```

### MCP Server Setup

```python
from features.plugins import setup_mcp_server

mcp = setup_mcp_server()

# Get MCP schema for Claude/LLM integration
schema = mcp.get_mcp_schema()

# Available Resources:
# - expense_data: Get customer expenses
# - recommendations: Get prioritized suggestions
# - chat_history: Access conversation history

# Available Tools:
# - analyze_expenses: Run expense analysis
# - generate_recommendations: Create suggestions
# - chat: Process natural language queries
```

---

## 4. Governance Framework

### Overview

Governance enforces business rules, validates data, and ensures compliance.

### Business Rules

Rules are registered and enforced automatically:

```python
from features.governance import GovernanceEngine, BusinessRule, RuleType

engine = GovernanceEngine.get_instance()

# Example: Validate income range
rule = BusinessRule(
    name='validate_income_range',
    rule_type=RuleType.INCOME_VALIDATION,
    description='Income must be between 1 and 1B',
    validator=lambda data: 1 <= data.get('income', 0) <= 1_000_000_000,
    error_message='Invalid income value',
    priority=100
)

engine.register_rule(rule)

# Validate data
is_valid, error = engine.validate('validate_income_range', {'income': 100000})
```

### Default Rules

| Rule | Type | Threshold |
|------|------|-----------|
| `validate_income_range` | Income Validation | 1 - 1,000,000,000 |
| `validate_expenses_format` | Expense Validation | Must be dict with positive values |
| `validate_income_expense_ratio` | Spending | Expenses ≤ 2x income |
| `validate_category_threshold` | Spending | Category ≤ 50% income |
| `validate_recommendations_accuracy` | Recommendation | Savings 0 - 1,000,000 |
| `validate_chat_compliance` | Compliance | No guaranteed returns |

### Spending Benchmarks

```python
from features.governance import BusinessRulesValidator

benchmarks = BusinessRulesValidator.SPENDING_THRESHOLDS
# {
#     'Rent': 0.30,           # 30% of income
#     'Food': 0.15,           # 15% of income
#     'Utilities': 0.08,      # 8% of income
#     'Transportation': 0.10, # 10% of income
#     'Entertainment': 0.07,  # 7% of income
#     'Shopping': 0.10,       # 10% of income
#     'EMI': 0.15,            # 15% of income
# }
```

### Compliance Checking

```python
from features.governance import ComplianceChecker

response = "Your portfolio could return 10% annually..."

is_compliant, warnings = ComplianceChecker.check_compliance(response)
# warnings: ['❌ Avoid guaranteeing returns']

# Add disclaimer
compliant_response = ComplianceChecker.add_disclaimer(response)
```

---

## 5. Observability & Traceability

### Overview

Complete visibility into application execution with logging, tracing, and metrics.

### Logging

```python
from features.observability import TraceLogger, LogLevel

logger = TraceLogger.get_instance()

# Log messages
logger.debug("Debug message", component="analyzer", session_id="user_123")
logger.info("Info message", component="analyzer", session_id="user_123")
logger.warning("Warning message", component="analyzer", session_id="user_123")
logger.error("Error message", component="analyzer", session_id="user_123", data={'error_code': 500})
logger.critical("Critical message", component="analyzer", session_id="user_123")

# Get logs
logs = logger.get_logs(session_id="user_123", limit=50)
logs_json = logger.export_logs(session_id="user_123")
```

### Event Tracing

```python
from features.observability import EventType

# Trace events
logger.trace_event(
    event_type=EventType.ANALYSIS_COMPLETE,
    session_id="user_123",
    data={'duration_ms': 150, 'expenses_analyzed': 7},
    duration_ms=150,
    status="completed"
)

# Get events
events = logger.get_events(session_id="user_123", limit=50)
events_json = logger.export_events(session_id="user_123")

# Get full session trace
trace = logger.get_session_trace(session_id="user_123")
```

### Metrics Collection

```python
from features.observability import MetricsCollector, PerformanceMonitor

metrics = MetricsCollector.get_instance()

# Record metric
metrics.record_metric("analysis_duration", 150, "ms", tags={'user': 'user_123'})
metrics.record_metric("savings_rate", 16.0, "percent")
metrics.record_metric("recommendations_count", 3, "count")

# Get metrics
all_metrics = metrics.get_metrics(name="analysis_duration", limit=100)
stats = metrics.get_aggregated_stats()
dashboard = metrics.get_dashboard_metrics()
```

### Performance Monitoring

```python
monitor = PerformanceMonitor()

# Time a block of code
monitor.start_timer("analysis")
# ... do analysis ...
elapsed = monitor.end_timer("analysis")

# Or use context manager pattern
monitor.time_block("recommendation", generate_recommendations, input_data)
```

### Health Checks

```python
from features.observability import HealthCheck

health = HealthCheck.check_health()
# Returns:
# {
#     'status': 'healthy' | 'degraded' | 'unhealthy',
#     'error_rate': 0.01,
#     'total_logs': 1000,
#     'total_events': 500,
#     'recent_errors': 10,
#     'performance': { timing metrics }
# }
```

---

## 6. Deployment Architecture

### Overview

Ready-to-deploy configurations for multiple platforms.

### Supported Platforms

| Platform | Use Case | Effort |
|----------|----------|--------|
| `STREAMLIT_CLOUD` | MVP, low cost | Easy |
| `HEROKU` | Production, managed | Medium |
| `AWS_ECS` | Enterprise, scalable | Hard |
| `DOCKER_LOCAL` | Development, testing | Easy |
| `KUBERNETES` | Distributed, multi-region | Hard |

### Configuration

```python
from features.deployment import DeploymentConfig, DeploymentEnvironment, DeploymentPlatform

# Production ECS deployment
config = DeploymentConfig(
    environment=DeploymentEnvironment.PRODUCTION,
    platform=DeploymentPlatform.AWS_ECS,
    app_name="Finance Advisor",
    version="2.0",
    region="us-east-1",
    replicas=3,
    max_replicas=10,
    memory_mb=2048,
    cpu_cores=1.0,
    enable_ssl=True,
    enable_logging=True,
    enable_monitoring=True
)
```

### Generation Tools

```python
from features.deployment import (
    DockerfileGenerator,
    ProcfileGenerator,
    KubernetesManifestGenerator,
    EnvironmentConfigurator,
    CI_CDConfiguration
)

# Generate Dockerfile
dockerfile = DockerfileGenerator.generate_dockerfile()
docker_compose = DockerfileGenerator.generate_docker_compose()

# Generate Procfile for Heroku
procfile = ProcfileGenerator.generate_procfile()

# Generate Kubernetes manifests
deployment = KubernetesManifestGenerator.generate_deployment()
service = KubernetesManifestGenerator.generate_service()  # Implied

# Generate environment variables
env_vars = EnvironmentConfigurator.get_environment_vars(DeploymentEnvironment.PRODUCTION)
env_file = EnvironmentConfigurator.generate_env_file(DeploymentEnvironment.PRODUCTION)

# Generate CI/CD configuration
github_actions = CI_CDConfiguration.generate_github_actions()
gitlab_ci = CI_CDConfiguration.generate_gitlab_ci()
```

### Deployment Strategies

```python
from features.deployment import RollbackStrategy

# Blue-green deployment
strategy = RollbackStrategy.get_blue_green_deployment()
# Deployment with zero downtime, instant rollback

# Canary deployment
strategy = RollbackStrategy.get_canary_deployment()
# Gradual traffic shift, 50-minute rollout with 5-minute rollback

# Get rollback plan
rollback = RollbackStrategy.get_rollback_plan(current_version="2.0", previous_version="1.9")
```

---

## 7. Integration Guide

### Complete System Setup

```python
from features.integration_example import FinanceAdvisorSystem
from features.deployment import DeploymentConfig, DeploymentEnvironment, DeploymentPlatform

# Create configuration
config = DeploymentConfig(
    environment=DeploymentEnvironment.PRODUCTION,
    platform=DeploymentPlatform.AWS_ECS,
    app_name="Finance Advisor",
    version="2.0",
    config_data={
        'enable_banking': True,
        'enable_notifications': True,
        'enable_analytics': True,
        'enable_investments': True,
    }
)

# Initialize system (auto-setup all features)
system = FinanceAdvisorSystem(config)

# Use the system
analysis = system.analyze_expenses(session_id, income, expenses)
recommendations = system.generate_recommendations(session_id, analysis)
chat_response = system.respond_to_chat(session_id, query, analysis, recommendations)

# Get comprehensive metrics
metrics = system.get_system_metrics()
health = system.get_health_status()
```

### Streamlit Integration

```python
import streamlit as st
from features.integration_example import FinanceAdvisorSystem
from features.deployment import DeploymentConfig, DeploymentEnvironment, DeploymentPlatform

# Initialize system in session state
if 'finance_system' not in st.session_state:
    config = DeploymentConfig(
        environment=DeploymentEnvironment.PRODUCTION,
        platform=DeploymentPlatform.STREAMLIT_CLOUD,
        app_name="Finance Advisor",
        version="2.0"
    )
    st.session_state.finance_system = FinanceAdvisorSystem(config)

system = st.session_state.finance_system

# Use in Streamlit app
with st.container():
    income = st.number_input("Monthly Income", min_value=1000)
    expenses = {}
    for category in ['Rent', 'Food', 'Utilities', 'Entertainment']:
        expenses[category] = st.number_input(f"{category} Expense")
    
    if st.button("Analyze"):
        analysis = system.analyze_expenses(st.session_state.session_id, income, expenses)
        st.write(f"Savings Rate: {analysis['savings_percentage']:.1f}%")
```

---

## Key Features Summary

| Feature | Component | Benefit |
|---------|-----------|---------|
| **Skills** | `features/skills.py` | Modular, reusable analysis components |
| **Subagents** | `features/skills.py` | Automated multi-step workflows |
| **Hooks** | `features/hooks.py` | Event-driven extensibility |
| **Plugins** | `features/plugins.py` | Third-party integrations |
| **MCP** | `features/plugins.py` | LLM/AI integration |
| **Governance** | `features/governance.py` | Business rule enforcement |
| **Compliance** | `features/governance.py` | Regulatory compliance checks |
| **Logging** | `features/observability.py` | Full execution visibility |
| **Tracing** | `features/observability.py` | Request-level diagnostics |
| **Metrics** | `features/observability.py` | Performance monitoring |
| **Deployment** | `features/deployment.py` | Multi-platform readiness |
| **Rollback** | `features/deployment.py` | Safe deployment strategies |

---

## Next Steps

1. **Read** integration_example.py for complete working example
2. **Explore** each feature module for detailed documentation
3. **Test** with example_workflow() to see all features in action
4. **Integrate** with your Streamlit app using the integration guide
5. **Deploy** using the deployment configuration tools

For questions or issues, see the individual module docstrings.
