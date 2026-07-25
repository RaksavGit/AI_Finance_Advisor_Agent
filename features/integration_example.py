"""
Integration Example - Shows how to use all features together
"""

from features.skills import (
    SkillRegistry, ExpenseAnalyzerSkill, RecommendationGeneratorSkill,
    ChatResponderSkill, GoalTrackerSkill, BudgetPlannerSkill, Subagent
)
from features.hooks import HookManager, HookType, create_logging_hook, create_validation_hook
from features.plugins import PluginManager, PluginConfig, PluginType, setup_mcp_server
from features.plugins import BankingDataPlugin, NotificationPlugin, AnalyticsPlugin, InvestmentAdvisorPlugin, DataExportPlugin
from features.governance import setup_governance_engine
from features.observability import TraceLogger, MetricsCollector, PerformanceMonitor, HealthCheck
from features.deployment import DeploymentConfig, DeploymentEnvironment, DeploymentPlatform
from typing import Dict, Any


class FinanceAdvisorSystem:
    """Integrated Finance Advisor System with all features."""

    def __init__(self, config: DeploymentConfig):
        self.config = config

        # Initialize frameworks
        self.skill_registry = SkillRegistry.get_instance()
        self.hook_manager = HookManager.get_instance()
        self.plugin_manager = PluginManager.get_instance()
        self.governance_engine = setup_governance_engine()
        self.trace_logger = TraceLogger.get_instance()
        self.metrics_collector = MetricsCollector.get_instance()
        self.perf_monitor = PerformanceMonitor()
        self.mcp_server = setup_mcp_server()

        # Setup system
        self._setup_skills()
        self._setup_hooks()
        self._setup_plugins()

    def _setup_skills(self):
        """Register all skills."""
        # Register individual skills
        self.skill_registry.register_skill(ExpenseAnalyzerSkill())
        self.skill_registry.register_skill(RecommendationGeneratorSkill())
        self.skill_registry.register_skill(ChatResponderSkill())
        self.skill_registry.register_skill(GoalTrackerSkill())
        self.skill_registry.register_skill(BudgetPlannerSkill())

        # Setup analysis subagent
        analysis_subagent = Subagent("analysis_subagent", "Performs expense analysis")
        analysis_subagent.add_skill(self.skill_registry.get_skill("expense_analyzer"))
        analysis_subagent.add_skill(self.skill_registry.get_skill("budget_planner"))
        analysis_subagent.set_execution_sequence(["expense_analyzer", "budget_planner"])
        self.skill_registry.register_subagent(analysis_subagent)

        # Setup recommendation subagent
        recommendation_subagent = Subagent("recommendation_subagent", "Generates recommendations")
        recommendation_subagent.add_skill(self.skill_registry.get_skill("recommendation_generator"))
        recommendation_subagent.add_skill(self.skill_registry.get_skill("goal_tracker"))
        self.skill_registry.register_subagent(recommendation_subagent)

    def _setup_hooks(self):
        """Register all hooks."""
        # Register logging hook
        self.hook_manager.register(
            "main_logger",
            HookType.BEFORE_ANALYSIS,
            create_logging_hook(),
            priority=100
        )

        # Register validation hook
        self.hook_manager.register(
            "input_validator",
            HookType.ON_DATA_VALIDATE,
            create_validation_hook(),
            priority=100
        )

        # Register custom hooks
        def high_spending_alert(context):
            if context.data.get('high_spending_detected'):
                self.trace_logger.warning(
                    f"High spending detected: {context.data.get('categories')}",
                    component="high_spending_detector",
                    session_id=context.session_id
                )

        self.hook_manager.register(
            "high_spending_alert",
            HookType.ON_HIGH_SPENDING_DETECTED,
            high_spending_alert,
            priority=90
        )

    def _setup_plugins(self):
        """Setup and load plugins."""
        # Register plugin classes
        self.plugin_manager.register_plugin_class("banking_data", BankingDataPlugin)
        self.plugin_manager.register_plugin_class("notifications", NotificationPlugin)
        self.plugin_manager.register_plugin_class("analytics", AnalyticsPlugin)
        self.plugin_manager.register_plugin_class("investment_advisor", InvestmentAdvisorPlugin)
        self.plugin_manager.register_plugin_class("data_export", DataExportPlugin)

        # Load plugins based on configuration
        if self.config.config_data.get('enable_banking'):
            banking_config = PluginConfig(
                name="banking_data",
                type=PluginType.DATA_SOURCE,
                version="1.0",
                enabled=True,
                config_data={'mock_mode': True}
            )
            self.plugin_manager.load_plugin(banking_config)

        if self.config.config_data.get('enable_notifications'):
            notify_config = PluginConfig(
                name="notifications",
                type=PluginType.NOTIFICATION,
                version="1.0",
                enabled=True,
                config_data={'notification_type': 'email'}
            )
            self.plugin_manager.load_plugin(notify_config)

        if self.config.config_data.get('enable_analytics'):
            analytics_config = PluginConfig(
                name="analytics",
                type=PluginType.ANALYTICS,
                version="1.0",
                enabled=True,
                config_data={'warehouse_type': 'bigquery'}
            )
            self.plugin_manager.load_plugin(analytics_config)

        if self.config.config_data.get('enable_investments'):
            investment_config = PluginConfig(
                name="investment_advisor",
                type=PluginType.ADVISOR,
                version="1.0",
                enabled=True,
                config_data={'advisor_type': 'robo_advisor'}
            )
            self.plugin_manager.load_plugin(investment_config)

        if self.config.config_data.get('enable_data_export'):
            export_config = PluginConfig(
                name="data_export",
                type=PluginType.INTEGRATION,
                version="1.0",
                enabled=True,
                config_data={'export_formats': ['csv', 'json']}
            )
            self.plugin_manager.load_plugin(export_config)

    def analyze_expenses(self, session_id: str, income: float, expenses: Dict[str, float]) -> Dict[str, Any]:
        """Analyze expenses using skill system."""
        self.perf_monitor.start_timer("analyze_expenses")
        self.trace_logger.info(
            f"Starting expense analysis for session {session_id}",
            component="analyzer",
            session_id=session_id
        )

        try:
            # Validate input data
            is_valid, errors = self.governance_engine.validate_all({
                'income': income,
                'expenses': expenses
            })

            if not is_valid:
                self.trace_logger.error(
                    f"Validation failed: {errors}",
                    component="analyzer",
                    session_id=session_id
                )
                raise ValueError(f"Validation errors: {errors}")

            # Trigger hook
            self.hook_manager.trigger(
                HookType.ON_DATA_VALIDATE,
                session_id,
                {'income': income, 'expenses': expenses}
            )

            # Execute analysis
            input_data = {
                'income': income,
                'expenses': expenses
            }

            analysis_result = self.skill_registry.execute_skill(
                'expense_analyzer',
                input_data,
                session_id
            )

            # Record metrics
            self.metrics_collector.record_metric(
                "analysis_total_expenses",
                analysis_result['total_expenses'],
                "currency"
            )
            self.metrics_collector.record_metric(
                "analysis_savings_rate",
                analysis_result['savings_percentage'],
                "percent"
            )

            # Track trace event
            self.trace_logger.trace_event(
                event_type=__import__('features.observability', fromlist=['EventType']).EventType.ANALYSIS_COMPLETE,
                session_id=session_id,
                data=analysis_result
            )

            return analysis_result

        finally:
            self.perf_monitor.end_timer("analyze_expenses")

    def generate_recommendations(self, session_id: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendations using skill system."""
        self.perf_monitor.start_timer("generate_recommendations")

        try:
            # Execute recommendation generation
            input_data = {
                'analysis': analysis_data,
                'benchmarks': {}
            }

            recommendations = self.skill_registry.execute_skill(
                'recommendation_generator',
                input_data,
                session_id
            )

            # Validate recommendations
            is_valid, error = self.governance_engine.validate(
                'validate_recommendations_accuracy',
                recommendations
            )

            if not is_valid:
                self.trace_logger.warning(
                    f"Recommendation validation warning: {error}",
                    component="recommendation_generator",
                    session_id=session_id
                )

            # Check for high spending and trigger hook
            if recommendations['recommendation_count'] > 0:
                self.hook_manager.trigger(
                    HookType.ON_RECOMMENDATION_GENERATED,
                    session_id,
                    recommendations
                )

            # Send notifications if enabled
            if self.plugin_manager.get_plugin("notifications"):
                self.plugin_manager.execute_plugin(
                    "notifications",
                    {
                        'message': f"Generated {recommendations['recommendation_count']} recommendations"
                    }
                )

            # Track analytics
            if self.plugin_manager.get_plugin("analytics"):
                self.plugin_manager.execute_plugin(
                    "analytics",
                    {
                        'event_name': 'recommendation_generated',
                        'count': recommendations['recommendation_count']
                    }
                )

            return recommendations

        finally:
            self.perf_monitor.end_timer("generate_recommendations")

    def respond_to_chat(self, session_id: str, query: str,
                       analysis_data: Dict[str, Any],
                       recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """Respond to chat query using skill system."""
        self.perf_monitor.start_timer("chat_response")

        try:
            input_data = {
                'query': query,
                'analysis': analysis_data,
                'recommendations': recommendations
            }

            response = self.skill_registry.execute_skill(
                'chat_responder',
                input_data,
                session_id
            )

            # Compliance check
            from features.governance import ComplianceChecker
            is_compliant, warnings = ComplianceChecker.check_compliance(response['response'])

            if not is_compliant:
                response['compliance_warnings'] = warnings
                self.trace_logger.warning(
                    f"Chat response has compliance warnings: {warnings}",
                    component="chat_responder",
                    session_id=session_id
                )

            return response

        finally:
            self.perf_monitor.end_timer("chat_response")

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics."""
        return {
            'configuration': self.config.to_dict(),
            'skills': self.skill_registry.get_system_metrics(),
            'governance': self.governance_engine.get_metrics(),
            'hooks': self.hook_manager.get_handler_metrics(),
            'plugins': self.plugin_manager.get_plugin_metrics(),
            'observability': {
                'logs': len(self.trace_logger.logs),
                'events': len(self.trace_logger.events),
                'metrics': len(self.metrics_collector.metrics),
                'dashboard': self.metrics_collector.get_dashboard_metrics(),
            },
            'health': HealthCheck.check_health(),
        }

    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status."""
        return HealthCheck.check_health()


# Example usage
def example_workflow():
    """Example workflow showing full system integration."""

    # Setup system with production configuration
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

    system = FinanceAdvisorSystem(config)

    # Simulate user session
    session_id = "session_12345"

    # User input
    income = 100000
    expenses = {
        'Rent': 28000,
        'Food': 12000,
        'Utilities': 3500,
        'Travel': 8000,
        'EMI': 15000,
        'Shopping': 12000,
        'Entertainment': 6000,
    }

    try:
        # Step 1: Analyze expenses
        print("📊 Step 1: Analyzing expenses...")
        analysis = system.analyze_expenses(session_id, income, expenses)
        print(f"   Savings Rate: {analysis['savings_percentage']:.1f}%")

        # Step 2: Generate recommendations
        print("💡 Step 2: Generating recommendations...")
        recommendations = system.generate_recommendations(session_id, analysis)
        print(f"   Recommendations: {recommendations['recommendation_count']}")

        # Step 3: Chat query
        print("💬 Step 3: Processing chat query...")
        chat_response = system.respond_to_chat(
            session_id,
            "How can I save more?",
            analysis,
            recommendations
        )
        print(f"   Response: {chat_response['response'][:100]}...")

        # Show metrics
        print("\n📈 System Metrics:")
        metrics = system.get_system_metrics()
        print(f"   Skills: {metrics['skills']['total_skills']}")
        print(f"   Plugins: {len(metrics['plugins'])}")
        print(f"   Health: {metrics['health']['status']}")

    except Exception as e:
        print(f"❌ Error: {e}")

        # Show error metrics
        trace_logger = TraceLogger.get_instance()
        print(f"\n📋 Recent Logs:")
        logs = trace_logger.get_logs(session_id=session_id, limit=5)
        for log in logs:
            print(f"   {log['level']}: {log['message']}")


if __name__ == "__main__":
    example_workflow()
