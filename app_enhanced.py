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

# Custom CSS - Enhanced UI Design
st.markdown("""
    <style>
    /* Main container styling */
    .main { padding-top: 0; }

    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    /* Metric cards with better styling */
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 25px;
        border-radius: 12px;
        margin: 15px 0;
        border: 1px solid rgba(0,0,0,0.05);
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }

    /* Success box with improved styling */
    .success-box {
        background-color: #f0fdf4;
        padding: 18px;
        border-radius: 10px;
        border-left: 5px solid #22c55e;
        border-right: 1px solid #dcfce7;
        margin: 15px 0;
    }

    /* Warning box */
    .warning-box {
        background-color: #fffbeb;
        padding: 18px;
        border-radius: 10px;
        border-left: 5px solid #f59e0b;
        border-right: 1px solid #fef3c7;
        margin: 15px 0;
    }

    /* Error box */
    .error-box {
        background-color: #fef2f2;
        padding: 18px;
        border-radius: 10px;
        border-left: 5px solid #ef4444;
        border-right: 1px solid #fee2e2;
        margin: 15px 0;
    }

    /* Info box */
    .info-box {
        background-color: #f0f9ff;
        padding: 18px;
        border-radius: 10px;
        border-left: 5px solid #0ea5e9;
        border-right: 1px solid #e0f2fe;
        margin: 15px 0;
    }

    /* Feature badges */
    .feature-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 14px;
        border-radius: 20px;
        font-size: 0.85em;
        margin-right: 8px;
        margin-bottom: 8px;
        font-weight: 500;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }

    /* Section styling */
    .section-title {
        font-size: 1.3em;
        font-weight: 600;
        margin-top: 25px;
        margin-bottom: 15px;
        color: #1f2937;
        border-bottom: 3px solid #667eea;
        padding-bottom: 10px;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f8fafc;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }

    /* Button styling */
    button {
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }

    /* Input styling */
    input { border-radius: 8px !important; }

    /* Divider styling */
    hr { margin: 25px 0; border: 1px solid #e5e7eb; }

    /* Chart container */
    .chart-container {
        background: white;
        border-radius: 12px;
        padding: 15px;
        margin: 15px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
        border-right: 2px solid #e2e8f0;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 20px !important;
    }

    /* Sidebar navigation styling */
    .sidebar-nav {
        padding: 10px 0;
    }

    /* Radio button styling for sidebar */
    .streamlit-expanderHeader {
        border-radius: 8px !important;
    }

    /* Improved radio button appearance */
    div[role="radiogroup"] {
        gap: 8px;
    }

    /* Navigation item styling */
    div[role="radio"] {
        padding: 12px 16px !important;
        margin: 6px 0 !important;
        border-radius: 8px !important;
        border: 2px solid transparent !important;
        transition: all 0.3s ease !important;
        background-color: transparent !important;
    }

    div[role="radio"]:hover {
        background-color: rgba(102, 126, 234, 0.05) !important;
        border-color: #667eea !important;
    }

    div[role="radio"][aria-checked="true"] {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%) !important;
        border-color: #667eea !important;
        font-weight: 500 !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15) !important;
    }

    /* Sidebar text styling */
    [data-testid="stSidebar"] label {
        font-size: 0.95em !important;
        font-weight: 500 !important;
        color: #1f2937 !important;
    }

    /* Sidebar section header */
    [data-testid="stSidebar"] h3 {
        color: #667eea !important;
        font-weight: 600 !important;
        margin-top: 20px !important;
        margin-bottom: 12px !important;
        font-size: 1.1em !important;
    }

    /* Divider in sidebar */
    [data-testid="stSidebar"] hr {
        margin: 15px 0 !important;
        border-color: #e2e8f0 !important;
    }
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

    # Initialize expense and income state
    if 'monthly_income' not in st.session_state:
        st.session_state.monthly_income = 100000

    if 'expenses' not in st.session_state:
        st.session_state.expenses = {
            'Rent': 28000,
            'Food': 12000,
            'Utilities': 3500,
            'Travel': 8000,
            'EMI': 15000,
            'Shopping': 12000,
            'Entertainment': 6000,
        }


def render_header():
    """Render optimized page header."""
    st.markdown("""
        <div class="header-container">
            <h1 style="margin: 0; text-align: center; font-size: 2.5em;">💰 Personal Finance Advisor</h1>
            <p style="text-align: center; font-size: 1.1em; margin: 10px 0; opacity: 0.95;">
                Enterprise-Grade AI Financial Analysis & Recommendation System
            </p>
        </div>
    """, unsafe_allow_html=True)


def render_dashboard(system: FinanceAdvisorSystem):
    """Render optimized main dashboard."""
    st.markdown("<h2 class='section-title'>📊 Dashboard</h2>", unsafe_allow_html=True)

    # Income section
    st.markdown("<h3 style='color: #667eea; margin-top: 20px;'>💵 Monthly Income</h3>", unsafe_allow_html=True)

    st.session_state.monthly_income = st.number_input(
        "Monthly Income (₹)",
        min_value=1000,
        max_value=10000000,
        value=st.session_state.monthly_income,
        step=5000,
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Expense inputs with better organization
    st.markdown("<h3 style='color: #667eea; margin-top: 20px;'>💸 Monthly Expenses</h3>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4, gap="medium")

    with col1:
        st.markdown("**Housing & Utilities**", help="Rent, Utilities")
        st.session_state.expenses['Rent'] = st.number_input(
            "Rent", min_value=0, value=st.session_state.expenses['Rent'], step=500,
            label_visibility="collapsed"
        )
        st.session_state.expenses['Utilities'] = st.number_input(
            "Utilities", min_value=0, value=st.session_state.expenses['Utilities'], step=100,
            label_visibility="collapsed"
        )

    with col2:
        st.markdown("**Food & Travel**", help="Food, Travel")
        st.session_state.expenses['Food'] = st.number_input(
            "Food", min_value=0, value=st.session_state.expenses['Food'], step=200,
            label_visibility="collapsed"
        )
        st.session_state.expenses['Travel'] = st.number_input(
            "Travel", min_value=0, value=st.session_state.expenses['Travel'], step=200,
            label_visibility="collapsed"
        )

    with col3:
        st.markdown("**Debt & Shopping**", help="EMI, Shopping")
        st.session_state.expenses['EMI'] = st.number_input(
            "EMI/Debt", min_value=0, value=st.session_state.expenses['EMI'], step=500,
            label_visibility="collapsed"
        )
        st.session_state.expenses['Shopping'] = st.number_input(
            "Shopping", min_value=0, value=st.session_state.expenses['Shopping'], step=200,
            label_visibility="collapsed"
        )

    with col4:
        st.markdown("**Entertainment**", help="Entertainment")
        st.session_state.expenses['Entertainment'] = st.number_input(
            "Entertainment", min_value=0, value=st.session_state.expenses['Entertainment'], step=100,
            label_visibility="collapsed"
        )
        st.empty()

    if st.button("🔍 Analyze Finances", use_container_width=True):
        try:
            # Analyze expenses
            analysis = system.analyze_expenses(
                st.session_state.session_id,
                st.session_state.monthly_income,
                st.session_state.expenses
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
        render_analysis_results(st.session_state.analysis_results, st.session_state.expenses, st.session_state.monthly_income)


def render_analysis_results(analysis, expenses, income):
    """Render optimized analysis results."""
    st.markdown("<h3 style='color: #667eea; margin-top: 25px;'>📈 Financial Summary</h3>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4, gap="medium")

    total_expenses = sum(expenses.values())
    net_savings = analysis['net_savings']
    savings_rate = analysis['savings_percentage']
    target_rate = 20

    # Color coding based on performance
    income_color = "#667eea"
    expense_color = "#f97316" if (total_expenses/income*100) > 80 else "#3b82f6"
    savings_color = "#22c55e" if savings_rate >= target_rate else "#ef4444"

    with col1:
        st.metric(
            "💰 Monthly Income",
            f"₹{income:,.0f}",
            help="Your total monthly income"
        )

    with col2:
        total_pct = (total_expenses/income*100)
        st.metric(
            "💸 Total Expenses",
            f"₹{total_expenses:,.0f}",
            delta=f"{total_pct:.1f}% of income",
            delta_color="inverse" if total_pct > 80 else "off"
        )

    with col3:
        st.metric(
            "🎯 Net Savings",
            f"₹{net_savings:,.0f}",
            delta=f"+{analysis['savings_percentage']:.1f}%",
            help="Amount left after expenses"
        )

    with col4:
        delta_rate = savings_rate - target_rate
        st.metric(
            "📊 Savings Rate",
            f"{savings_rate:.1f}%",
            delta=f"{delta_rate:+.1f}% vs target",
            delta_color="normal" if delta_rate >= 0 else "inverse"
        )

    # Charts with improved styling
    st.markdown("---")
    st.markdown("<h3 style='color: #667eea; margin-top: 25px;'>📊 Visual Analytics</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("**Expense Breakdown**")

        # Color palette for pie chart
        colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a']

        fig = go.Figure(data=[go.Pie(
            labels=list(expenses.keys()),
            values=list(expenses.values()),
            marker=dict(colors=colors[:len(expenses)])
        )])
        fig.update_layout(
            height=380,
            showlegend=True,
            font=dict(size=11),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("**Your Spending vs Benchmark**")

        benchmarks = {
            'Rent': 30, 'Food': 15, 'Utilities': 8, 'Travel': 10,
            'EMI': 15, 'Shopping': 10, 'Entertainment': 7
        }

        categories = list(expenses.keys())
        user_pct = [analysis['category_percentages'].get(cat, 0) for cat in categories]
        bench_pct = [benchmarks.get(cat, 10) for cat in categories]

        fig = go.Figure(data=[
            go.Bar(name='Your Spending', x=categories, y=user_pct, marker_color='#667eea'),
            go.Bar(name='Benchmark', x=categories, y=bench_pct, marker_color='#e5e7eb'),
        ])
        fig.update_layout(
            height=380,
            barmode='group',
            hovermode='x unified',
            font=dict(size=11),
            showlegend=True,
            margin=dict(l=0, r=0, t=0, b=40),
            xaxis=dict(tickangle=-45)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


def render_recommendations(system: FinanceAdvisorSystem):
    """Render recommendations tab."""
    st.subheader("💡 Recommendations")

    if not st.session_state.recommendations:
        st.info("Perform analysis first to see recommendations")
        return

    recommendations = st.session_state.recommendations.get('recommendations', [])

    if not recommendations:
        st.success("✅ Your spending is well-optimized!")
        return

    for i, rec in enumerate(recommendations, 1):
        # Safely get recommendation details with defaults
        title = rec.get('title', 'Recommendation')
        potential_savings = rec.get('potential_savings', 0)
        priority = rec.get('priority', 'MEDIUM')
        description = rec.get('description', 'Optimize your spending')
        action = rec.get('action', 'Review this recommendation')

        with st.expander(f"{i}. {title} - Save ₹{potential_savings:,.0f}/month"):
            col1, col2, col3 = st.columns(3)

            with col1:
                priority_emoji = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(priority, '⚪')
                st.metric("Priority", f"{priority_emoji} {priority}")

            with col2:
                st.metric("Monthly Savings", f"₹{potential_savings:,.0f}")

            with col3:
                st.metric("Annual Savings", f"₹{potential_savings*12:,.0f}")

            st.markdown(f"**Description**: {description}")
            st.markdown(f"**Action**: {action}")


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

    # Sidebar header
    with st.sidebar:
        st.markdown("""
            <div style='text-align: center; padding: 15px 0; margin-bottom: 10px;'>
                <h2 style='margin: 0; color: #667eea; font-size: 1.4em;'>💰 FinanceAI</h2>
                <p style='margin: 5px 0; color: #64748b; font-size: 0.85em;'>v2.0</p>
            </div>
            <hr style='margin: 15px 0;'>
        """, unsafe_allow_html=True)

        # Single unified navigation
        st.markdown("<h3 style='margin-top: 20px; margin-bottom: 12px;'>📱 Main Menu</h3>", unsafe_allow_html=True)

        # Single unified navigation - all options without empty spacers
        page = st.radio(
            "Navigation",
            [
                "📊 Dashboard",
                "💡 Recommendations",
                "💬 Chatbot",
                "📊 Observability",
                "🔌 Plugins",
                "⚖️ Governance",
                "ⓘ About",
            ],
            label_visibility="collapsed",
            key="unified_nav",
            index=0  # Default to Dashboard
        )

        st.markdown("<hr>", unsafe_allow_html=True)

        # System info
        st.markdown("""
            <div style='padding-top: 10px; border-top: 1px solid #e2e8f0;'>
                <p style='font-size: 0.8em; color: #94a3b8; margin: 5px 0;'>
                    <strong>System Status:</strong> ✅ Active
                </p>
                <p style='font-size: 0.8em; color: #94a3b8; margin: 5px 0;'>
                    <strong>Session:</strong> Ready
                </p>
            </div>
        """, unsafe_allow_html=True)

    # Add custom CSS for About icon styling
    st.markdown("""
        <style>
        /* Blue rounded info icon for About */
        .info-icon {
            display: inline-block;
            width: 24px;
            height: 24px;
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            border-radius: 50%;
            text-align: center;
            line-height: 24px;
            font-weight: bold;
            font-size: 14px;
            box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
        }
        </style>
    """, unsafe_allow_html=True)

    render_header()

    st.markdown("---")

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

    elif page == "ⓘ About":
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
    """Render about page with professional styling."""
    st.markdown("""
        <h2 style='display: flex; align-items: center; gap: 10px;'>
            <span class='info-icon'>ⓘ</span> About This Application
        </h2>
    """, unsafe_allow_html=True)

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
