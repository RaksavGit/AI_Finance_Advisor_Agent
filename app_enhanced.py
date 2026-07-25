"""
Personal Finance Advisor AI Agent - Enhanced with Enterprise Features
Version 2.0 - Production Ready with Skills, Hooks, Plugins, Governance, Observability, Deployment
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json

# Import enterprise features
from features.skills import (
    SkillRegistry, ExpenseAnalyzerSkill, RecommendationGeneratorSkill,
    ChatResponderSkill, GoalTrackerSkill, BudgetPlannerSkill
)
from features.hooks import HookManager, HookType, create_logging_hook, create_validation_hook
from features.plugins import PluginManager, PluginConfig, PluginType
from features.governance import setup_governance_engine, ComplianceChecker
from features.observability import TraceLogger, MetricsCollector, PerformanceMonitor, EventType
from features.deployment import DeploymentConfig, DeploymentEnvironment, DeploymentPlatform
from features.integration_example import FinanceAdvisorSystem

# Page configuration
st.set_page_config(
    page_title="Finance Advisor AI Agent v2.0",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card { background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin: 10px 0; }
    .success-box { background-color: #d4edda; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745; }
    .warning-box { background-color: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107; }
    .error-box { background-color: #f8d7da; padding: 15px; border-radius: 5px; border-left: 4px solid #dc3545; }
    .feature-badge { display: inline-block; background-color: #007bff; color: white; padding: 5px 10px;
                     border-radius: 20px; font-size: 0.8em; margin-right: 5px; }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state with enterprise features."""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = f"session_{datetime.now().timestamp()}"

    if 'finance_system' not in st.session_state:
        config = DeploymentConfig(
            environment=DeploymentEnvironment.PRODUCTION,
            platform=DeploymentPlatform.STREAMLIT_CLOUD,
            app_name="Finance Advisor AI Agent",
            version="2.0",
            config_data={
                'enable_banking': True,
                'enable_notifications': False,
                'enable_analytics': True,
                'enable_investments': True,
            }
        )
        st.session_state.finance_system = FinanceAdvisorSystem(config)

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None

    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = None


def render_header():
    """Render page header with feature badges."""
    col1, col2 = st.columns([3, 1])

    with col1:
        st.title("💰 Personal Finance Advisor Agent v2.0")
        st.markdown("""
        **Enterprise-Grade AI Financial Analysis & Recommendation System**

        Powered by **Skills**, **Hooks**, **Plugins**, **Governance**, and **Observability**
        """)

    with col2:
        st.subheader("Features")
        st.markdown("""
        <span class="feature-badge">Skills ✓</span>
        <span class="feature-badge">Hooks ✓</span>
        <span class="feature-badge">Plugins ✓</span>
        <span class="feature-badge">Governance ✓</span>
        <span class="feature-badge">Observability ✓</span>
        """, unsafe_allow_html=True)


def render_dashboard(system: FinanceAdvisorSystem):
    """Render main dashboard."""
    st.subheader("📊 Dashboard")

    col1, col2 = st.columns([1, 1])

    with col1:
        income = st.number_input(
            "Monthly Income ($)",
            min_value=1000,
            max_value=1000000,
            value=100000,
            step=1000
        )

    with col2:
        st.info("💡 Enter your income to get started with financial analysis")

    # Expense inputs
    st.subheader("Monthly Expenses")

    expenses = {}
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        expenses['Rent'] = st.number_input("Rent", min_value=0, value=28000, step=100)
        expenses['Food'] = st.number_input("Food", min_value=0, value=12000, step=100)

    with col2:
        expenses['Utilities'] = st.number_input("Utilities", min_value=0, value=3500, step=100)
        expenses['Travel'] = st.number_input("Travel", min_value=0, value=8000, step=100)

    with col3:
        expenses['EMI'] = st.number_input("EMI/Debt", min_value=0, value=15000, step=100)
        expenses['Shopping'] = st.number_input("Shopping", min_value=0, value=12000, step=100)

    with col4:
        expenses['Entertainment'] = st.number_input("Entertainment", min_value=0, value=6000, step=100)
        st.empty()

    if st.button("🔍 Analyze Finances", use_container_width=True):
        try:
            # Analyze expenses
            analysis = system.analyze_expenses(
                st.session_state.session_id,
                income,
                expenses
            )
            st.session_state.analysis_results = analysis

            # Generate recommendations
            recommendations = system.generate_recommendations(
                st.session_state.session_id,
                analysis
            )
            st.session_state.recommendations = recommendations

            st.success("✅ Analysis Complete!")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    # Display results if available
    if st.session_state.analysis_results:
        st.markdown("---")
        render_analysis_results(st.session_state.analysis_results, expenses, income)


def render_analysis_results(analysis, expenses, income):
    """Render analysis results."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Monthly Income",
            f"${income:,.0f}",
            delta=None
        )

    with col2:
        total_expenses = sum(expenses.values())
        st.metric(
            "Total Expenses",
            f"${total_expenses:,.0f}",
            delta=f"{(total_expenses/income*100):.1f}% of income"
        )

    with col3:
        net_savings = analysis['net_savings']
        st.metric(
            "Net Savings",
            f"${net_savings:,.0f}",
            delta=f"+{analysis['savings_percentage']:.1f}%"
        )

    with col4:
        savings_rate = analysis['savings_percentage']
        target_rate = 20
        delta_rate = savings_rate - target_rate
        st.metric(
            "Savings Rate",
            f"{savings_rate:.1f}%",
            delta=f"{delta_rate:+.1f}% vs 20% target"
        )

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Expense Breakdown")
        fig = go.Figure(data=[go.Pie(labels=list(expenses.keys()), values=list(expenses.values()))])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Category vs Benchmark")
        benchmarks = {
            'Rent': 30, 'Food': 15, 'Utilities': 8, 'Travel': 10,
            'EMI': 15, 'Shopping': 10, 'Entertainment': 7
        }

        categories = list(expenses.keys())
        user_pct = [analysis['category_percentages'].get(cat, 0) for cat in categories]
        bench_pct = [benchmarks.get(cat, 10) for cat in categories]

        fig = go.Figure(data=[
            go.Bar(name='Your Spending', x=categories, y=user_pct, marker_color='steelblue'),
            go.Bar(name='Benchmark', x=categories, y=bench_pct, marker_color='lightgray'),
        ])
        fig.update_layout(height=400, barmode='group')
        st.plotly_chart(fig, use_container_width=True)


def render_recommendations(system: FinanceAdvisorSystem):
    """Render recommendations tab."""
    st.subheader("💡 Recommendations")

    if not st.session_state.recommendations:
        st.info("Perform analysis first to see recommendations")
        return

    recommendations = st.session_state.recommendations['recommendations']

    if not recommendations:
        st.success("✅ Your spending is well-optimized!")
        return

    for i, rec in enumerate(recommendations, 1):
        with st.expander(f"{i}. {rec['title']} - Save ${rec['potential_savings']:,.0f}/month"):
            col1, col2, col3 = st.columns(3)

            with col1:
                priority_emoji = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(rec['priority'], '⚪')
                st.metric("Priority", f"{priority_emoji} {rec['priority']}")

            with col2:
                st.metric("Monthly Savings", f"${rec['potential_savings']:,.0f}")

            with col3:
                st.metric("Annual Savings", f"${rec['potential_savings']*12:,.0f}")

            st.markdown(f"**Description**: {rec['description']}")
            st.markdown(f"**Action**: {rec['action']}")


def render_chatbot(system: FinanceAdvisorSystem):
    """Render chatbot interface."""
    st.subheader("💬 Finance Advisor Chatbot")

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    # Chat input
    user_input = st.chat_input("Ask me about your finances...")

    if user_input:
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input
        })

        with st.chat_message("user"):
            st.markdown(user_input)

        try:
            # Generate response
            response = system.respond_to_chat(
                st.session_state.session_id,
                user_input,
                st.session_state.analysis_results or {},
                st.session_state.recommendations or {}
            )

            # Check compliance
            is_compliant, warnings = ComplianceChecker.check_compliance(response['response'])

            if not is_compliant:
                response_text = response['response'] + "\n\n⚠️ **Compliance Note**: " + ", ".join(warnings)
            else:
                response_text = response['response']

            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response_text
            })

            with st.chat_message("assistant"):
                st.markdown(response_text)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


def render_observability(system: FinanceAdvisorSystem):
    """Render observability dashboard."""
    st.subheader("📊 Observability & Monitoring")

    tab1, tab2, tab3 = st.tabs(["Metrics", "Logs", "Health"])

    with tab1:
        st.subheader("System Metrics")
        metrics = system.get_system_metrics()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Skills", metrics['skills']['total_skills'])
        with col2:
            st.metric("Total Subagents", len(metrics['skills']['subagents']))
        with col3:
            st.metric("Active Plugins", len(metrics['plugins']))
        with col4:
            st.metric("Governance Rules", metrics['governance']['total_rules'])

        st.subheader("Performance Metrics")
        dashboard = metrics['observability']['dashboard']
        st.json(dashboard['aggregated_stats'])

    with tab2:
        st.subheader("Event Logs")
        logger = TraceLogger.get_instance()
        logs = logger.get_logs(session_id=st.session_state.session_id, limit=20)

        if logs:
            for log in reversed(logs):
                level = log['level']
                level_colors = {
                    'DEBUG': '🔵',
                    'INFO': '🟢',
                    'WARNING': '🟡',
                    'ERROR': '🔴',
                    'CRITICAL': '⚫'
                }
                emoji = level_colors.get(level, '⚪')
                st.markdown(f"{emoji} **{log['level']}** | {log['timestamp']}")
                st.markdown(f"_{log['message']}_")
                if log.get('data'):
                    st.json(log['data'])
        else:
            st.info("No logs yet")

    with tab3:
        st.subheader("System Health")
        health = system.get_health_status()

        health_colors = {
            'healthy': '🟢',
            'degraded': '🟡',
            'unhealthy': '🔴'
        }

        status_emoji = health_colors.get(health['status'], '⚪')
        st.markdown(f"## {status_emoji} Status: {health['status'].upper()}")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Error Rate", f"{health['error_rate']*100:.2f}%")
        with col2:
            st.metric("Total Logs", health['total_logs'])
        with col3:
            st.metric("Total Events", health['total_events'])
        with col4:
            st.metric("Recent Errors", health['recent_errors'])


def render_plugins(system: FinanceAdvisorSystem):
    """Render plugins management."""
    st.subheader("🔌 Plugins Management")

    plugin_manager = system.plugin_manager
    plugins = plugin_manager.list_plugins()

    if not plugins:
        st.info("No plugins loaded. Configure plugins in your deployment settings.")
        return

    for plugin_name in plugins:
        plugin = plugin_manager.get_plugin(plugin_name)
        metadata = plugin.get_metadata()

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.subheader(f"🔌 {metadata['name']} v{metadata['version']}")
        with col2:
            status = "✅ Active" if metadata['enabled'] else "❌ Inactive"
            st.markdown(f"**Status**: {status}")
        with col3:
            st.markdown(f"**Type**: {metadata['type']}")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Executions", metadata['execution_count'])
        with col2:
            st.metric("Errors", metadata['error_count'])
        with col3:
            if metadata['execution_count'] > 0:
                success_rate = ((metadata['execution_count'] - metadata['error_count']) /
                               metadata['execution_count'] * 100)
                st.metric("Success Rate", f"{success_rate:.1f}%")

        st.divider()


def render_governance(system: FinanceAdvisorSystem):
    """Render governance & compliance."""
    st.subheader("⚖️ Governance & Compliance")

    governance = system.governance_engine
    metrics = governance.get_metrics()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rules", metrics['total_rules'])
    with col2:
        st.metric("Enabled Rules", metrics['enabled_rules'])
    with col3:
        st.metric("Violations Log", len(governance.violation_log))

    st.subheader("Active Rules")
    for rule_name, rule_info in metrics['rules'].items():
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(f"**{rule_name}**")
        with col2:
            status = "✅" if rule_info['enabled'] else "❌"
            st.markdown(f"{status} {rule_info['type']}")
        with col3:
            st.markdown(f"Priority: {rule_info['priority']}")

    if governance.violation_log:
        st.subheader("Recent Violations")
        violations_df = pd.DataFrame(governance.violation_log[-10:])
        st.dataframe(violations_df, use_container_width=True)


def main():
    """Main application."""
    initialize_session_state()

    system = st.session_state.finance_system

    render_header()

    st.markdown("---")

    # Sidebar navigation
    page = st.sidebar.radio(
        "📋 Navigation",
        [
            "📊 Dashboard",
            "💡 Recommendations",
            "💬 Chatbot",
            "📊 Observability",
            "🔌 Plugins",
            "⚖️ Governance",
            "ℹ️ About"
        ]
    )

    if page == "📊 Dashboard":
        render_dashboard(system)

    elif page == "💡 Recommendations":
        render_recommendations(system)

    elif page == "💬 Chatbot":
        render_chatbot(system)

    elif page == "📊 Observability":
        render_observability(system)

    elif page == "🔌 Plugins":
        render_plugins(system)

    elif page == "⚖️ Governance":
        render_governance(system)

    elif page == "ℹ️ About":
        render_about()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888; font-size: 0.9em;'>
    <p><b>Personal Finance Advisor AI Agent v2.0</b></p>
    <p>Enterprise Features: Skills • Hooks • Plugins • Governance • Observability • Deployment</p>
    <p>🚀 Deployed on Streamlit Cloud | Built with Python & Streamlit</p>
    </div>
    """, unsafe_allow_html=True)


def render_about():
    """Render about page."""
    st.subheader("ℹ️ About This Application")

    st.markdown("""
    ## Personal Finance Advisor AI Agent v2.0

    ### What is This?
    A production-ready financial analysis system powered by:
    - **Skills Framework**: Modular, reusable analysis components
    - **Subagents**: Multi-step automated workflows
    - **Hooks**: Event-driven extensibility points
    - **Plugins**: Third-party integration capabilities
    - **MCP Protocol**: LLM/AI integration support
    - **Governance**: Business rule enforcement & compliance
    - **Observability**: Comprehensive logging & monitoring
    - **Deployment**: Multi-platform deployment strategies

    ### Key Features
    ✅ **Expense Analysis** - Deep financial pattern detection
    ✅ **Smart Recommendations** - AI-powered savings suggestions
    ✅ **Interactive Chatbot** - 24/7 financial Q&A
    ✅ **Goal Tracking** - Monitor financial milestones
    ✅ **Budget Planning** - Automatic budget optimization
    ✅ **Compliance Checks** - Regulatory compliance validation
    ✅ **Full Observability** - Logging, tracing, metrics
    ✅ **Enterprise Ready** - Production deployment strategies

    ### Technology Stack
    - **Frontend**: Streamlit (Python)
    - **Backend**: Python with Enterprise Features
    - **Visualizations**: Plotly
    - **Deployment**: Streamlit Cloud (also supports Heroku, AWS ECS, Kubernetes)
    - **Monitoring**: Built-in observability framework

    ### Architecture Highlights
    - **Microservices Ready**: Skills can be deployed independently
    - **Highly Observable**: Full execution tracing and metrics
    - **Compliant**: Built-in regulatory compliance checks
    - **Scalable**: From MVP to enterprise deployment
    - **Extensible**: Plugin system for easy integration

    ### Getting Started
    1. Enter your **monthly income** on the Dashboard
    2. Input your **monthly expenses** by category
    3. Click **"Analyze Finances"** to get insights
    4. View **Recommendations** for savings opportunities
    5. Chat with the **Chatbot** for personalized advice
    6. Monitor **Observability** metrics for system health
    7. Manage **Plugins** for additional capabilities
    8. Review **Governance** rules for compliance

    ### Contact & Support
    For questions, issues, or feature requests, visit the GitHub repository.
    """)

    st.subheader("📊 System Information")

    system = st.session_state.finance_system

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Deployment Configuration**")
        config = system.config.to_dict()
        for key, value in config.items():
            if key != 'config_data':
                st.markdown(f"- **{key}**: {value}")

    with col2:
        st.markdown("**System Status**")
        health = system.get_health_status()
        st.markdown(f"- **Status**: {health['status'].upper()}")
        st.markdown(f"- **Error Rate**: {health['error_rate']*100:.2f}%")
        st.markdown(f"- **Logs**: {health['total_logs']}")
        st.markdown(f"- **Events**: {health['total_events']}")


if __name__ == "__main__":
    main()
