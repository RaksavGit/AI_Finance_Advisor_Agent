"""
Personal Finance Advisor AI Agent - Streamlit Application
Production-grade financial analysis and recommendation system.

Architecture:
- Data Layer: Sample customer expense data with multiple categories
- Analysis Engine: Rule-based expense analysis and pattern detection
- Recommendation Engine: Intelligent savings suggestions based on benchmarks
- Chatbot Interface: Natural language interaction with context awareness
- Visualization Layer: Interactive charts and metrics display
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
from typing import Dict, List, Tuple, Any

# ============================================================================
# DATA LAYER - Sample Customer Expense Data
# ============================================================================

class ExpenseDataManager:
    """Manages customer expense data and provides data access layer."""

    # Industry benchmark thresholds (as % of income)
    BENCHMARKS = {
        'Rent': 0.30,           # Should not exceed 30% of income
        'Food': 0.15,           # Target around 15% of income
        'Utilities': 0.08,      # Around 8% of income
        'Transportation': 0.10, # Around 10% of income
        'Entertainment': 0.07,  # Around 7% of income
        'Shopping': 0.10,       # Around 10% of income
        'EMI': 0.15,            # Maximum 15% for debt obligations
    }

    # High spending threshold
    HIGH_SPENDING_THRESHOLD = 0.30  # Categories exceeding 30% of income

    # Recommended savings target
    TARGET_SAVINGS_PERCENTAGE = 0.20  # Aim for 20% savings

    @staticmethod
    def get_sample_customer_data() -> Dict[str, Any]:
        """
        Generate realistic sample customer expense data.
        Returns a dictionary with customer profile and monthly expenses.
        """
        customer_data = {
            'customer_id': 'CUST_001',
            'name': 'John Doe',
            'monthly_income': 100000,  # in currency units
            'email': 'john@example.com',
            'expenses': {
                'Rent': 28000,         # 28% of income
                'Food': 12000,         # 12% of income
                'Utilities': 3500,     # 3.5% of income
                'Travel': 8000,        # 8% of income
                'EMI': 15000,          # 15% of income
                'Shopping': 12000,     # 12% of income
                'Entertainment': 6000, # 6% of income
            },
            'tracking_period': 'July 2024 - July 2025'
        }
        return customer_data

    @staticmethod
    def get_multiple_months_data() -> pd.DataFrame:
        """
        Generate expense data for trend analysis across multiple months.
        Used for savings trend visualization.
        """
        months = pd.date_range(start='2024-08-01', end='2025-07-01', freq='MS')
        data = []

        # Base expenses with slight monthly variations
        base_expenses = {
            'Rent': 28000,
            'Food': 12000,
            'Utilities': 3500,
            'Travel': 8000,
            'EMI': 15000,
            'Shopping': 12000,
            'Entertainment': 6000,
        }

        for month in months:
            # Add seasonal variations (±5% random variation)
            variation_factor = np.random.uniform(0.95, 1.05)
            total_expense = sum(base_expenses.values()) * variation_factor
            savings = 100000 - total_expense
            savings_percentage = (savings / 100000) * 100

            data.append({
                'Month': month,
                'Total_Expenses': total_expense,
                'Savings': savings,
                'Savings_Percentage': savings_percentage
            })

        return pd.DataFrame(data)


# ============================================================================
# ANALYSIS ENGINE - Expense Analysis and Pattern Detection
# ============================================================================

class ExpenseAnalysisEngine:
    """Analyzes expenses and identifies spending patterns."""

    def __init__(self, monthly_income: float, expenses: Dict[str, float]):
        self.monthly_income = monthly_income
        self.expenses = expenses
        self.total_expenses = sum(expenses.values())
        self.net_savings = monthly_income - self.total_expenses
        self.savings_percentage = (self.net_savings / monthly_income * 100) if monthly_income > 0 else 0

    def get_dashboard_metrics(self) -> Dict[str, float]:
        """Calculate key metrics for dashboard display."""
        return {
            'monthly_income': self.monthly_income,
            'total_expenses': self.total_expenses,
            'net_savings': self.net_savings,
            'savings_percentage': self.savings_percentage,
        }

    def get_category_percentages(self) -> Dict[str, float]:
        """Calculate percentage of income spent in each category."""
        return {
            category: (amount / self.monthly_income * 100) if self.monthly_income > 0 else 0
            for category, amount in self.expenses.items()
        }

    def get_top_spending_categories(self, top_n: int = 3) -> List[Tuple[str, float]]:
        """Identify top N highest spending categories."""
        sorted_expenses = sorted(self.expenses.items(), key=lambda x: x[1], reverse=True)
        return sorted_expenses[:top_n]

    def identify_high_spending_categories(self) -> List[Tuple[str, float, float]]:
        """
        Identify categories exceeding 30% of income.
        Returns list of (category, amount, percentage) tuples.
        """
        category_percentages = self.get_category_percentages()
        high_spending = []

        for category, percentage in category_percentages.items():
            if percentage > ExpenseDataManager.HIGH_SPENDING_THRESHOLD * 100:
                high_spending.append((
                    category,
                    self.expenses[category],
                    percentage
                ))

        return sorted(high_spending, key=lambda x: x[2], reverse=True)

    def get_benchmark_comparison(self) -> Dict[str, Dict[str, float]]:
        """
        Compare user spending against industry benchmarks.
        Returns comparison data for each category.
        """
        category_percentages = self.get_category_percentages()
        comparison = {}

        for category in self.expenses.keys():
            user_spending_pct = category_percentages.get(category, 0)
            benchmark_pct = ExpenseDataManager.BENCHMARKS.get(category, 0) * 100

            comparison[category] = {
                'user_spending': user_spending_pct,
                'benchmark': benchmark_pct,
                'difference': user_spending_pct - benchmark_pct,
                'status': 'OVER' if user_spending_pct > benchmark_pct else 'UNDER'
            }

        return comparison

    def calculate_potential_savings(self) -> Dict[str, float]:
        """
        Calculate potential savings if user reduces high-spending categories by 10%.
        """
        potential_savings = {}
        high_spending = self.identify_high_spending_categories()

        for category, amount, percentage in high_spending:
            # Suggest 10% reduction from current spending
            reduction_amount = amount * 0.10
            potential_savings[category] = reduction_amount

        return potential_savings


# ============================================================================
# RECOMMENDATION ENGINE - Intelligent Savings Suggestions
# ============================================================================

class RecommendationEngine:
    """Generates actionable savings recommendations based on spending patterns."""

    def __init__(self, analysis_engine: ExpenseAnalysisEngine):
        self.engine = analysis_engine
        self.recommendations = []

    def generate_recommendations(self) -> List[Dict[str, str]]:
        """
        Generate prioritized recommendations based on spending analysis.
        Returns list of recommendation dictionaries with priority and impact.
        """
        self.recommendations = []

        # 1. High spending category recommendations
        high_spending = self.engine.identify_high_spending_categories()
        for category, amount, percentage in high_spending:
            potential_reduction = amount * 0.10  # 10% reduction target
            rec = {
                'priority': 'HIGH',
                'category': category,
                'type': 'reduce_high_spending',
                'title': f'Reduce {category} Spending',
                'description': f'Your {category} spending ({percentage:.1f}% of income) exceeds recommended levels. '
                              f'Consider reducing by 10% (save ${potential_reduction:,.0f}/month).',
                'potential_savings': potential_reduction,
                'action': f'Review and optimize {category.lower()} expenses'
            }
            self.recommendations.append(rec)

        # 2. Benchmark-based recommendations
        benchmark_comparison = self.engine.get_benchmark_comparison()
        benchmark_opportunities = []

        for category, comparison in benchmark_comparison.items():
            if comparison['status'] == 'OVER' and comparison['difference'] > 2:  # Over by more than 2%
                current_amount = self.engine.expenses[category]
                benchmark_amount = current_amount * (comparison['benchmark'] / comparison['user_spending'])
                potential_savings = current_amount - benchmark_amount

                benchmark_opportunities.append({
                    'priority': 'MEDIUM',
                    'category': category,
                    'type': 'align_to_benchmark',
                    'title': f'Align {category} to Industry Benchmark',
                    'description': f'Industry benchmark suggests {comparison["benchmark"]:.1f}% of income for {category}. '
                                  f'Align to benchmark to save ${potential_savings:,.0f}/month.',
                    'potential_savings': potential_savings,
                    'action': f'Optimize {category.lower()} to {comparison["benchmark"]:.1f}% of income'
                })

        self.recommendations.extend(benchmark_opportunities)

        # 3. Savings target recommendation
        if self.engine.savings_percentage < ExpenseDataManager.TARGET_SAVINGS_PERCENTAGE * 100:
            target_savings = self.engine.monthly_income * ExpenseDataManager.TARGET_SAVINGS_PERCENTAGE
            additional_savings_needed = target_savings - self.engine.net_savings

            rec = {
                'priority': 'MEDIUM',
                'category': 'Overall_Savings',
                'type': 'increase_savings_target',
                'title': 'Increase Savings Target to 20%',
                'description': f'Current savings rate is {self.engine.savings_percentage:.1f}%. '
                              f'Target 20% savings rate by reducing overall expenses by ${additional_savings_needed:,.0f}/month.',
                'potential_savings': additional_savings_needed,
                'action': 'Implement cost reduction across multiple categories'
            }
            self.recommendations.append(rec)

        # Sort by potential savings (highest first)
        self.recommendations = sorted(
            self.recommendations,
            key=lambda x: x['potential_savings'],
            reverse=True
        )

        return self.recommendations


# ============================================================================
# CHATBOT RESPONDER - Natural Language Interaction
# ============================================================================

class ChatbotResponder:
    """Handles natural language queries about finances and recommendations."""

    def __init__(self, analysis_engine: ExpenseAnalysisEngine, recommendations: List[Dict]):
        self.engine = analysis_engine
        self.recommendations = recommendations

    def respond_to_query(self, user_query: str) -> str:
        """
        Process user query and return contextual response.
        Uses rule-based matching to identify query intent and generate response.
        """
        query_lower = user_query.lower().strip()

        # Greeting queries
        if any(word in query_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return self._handle_greeting()

        # Savings-related queries
        if any(word in query_lower for word in ['save', 'savings', 'saving']):
            if 'how' in query_lower or 'can' in query_lower:
                return self._handle_how_to_save()
            elif 'percentage' in query_lower or 'rate' in query_lower:
                return self._handle_savings_percentage()
            else:
                return self._handle_savings_general()

        # High spending queries
        if any(word in query_lower for word in ['spending', 'spend', 'expensive']):
            if 'where' in query_lower or 'which' in query_lower:
                return self._handle_high_spending()
            else:
                return self._handle_spending_analysis()

        # Category-specific queries
        for category in self.engine.expenses.keys():
            if category.lower() in query_lower:
                return self._handle_category_query(category, query_lower)

        # Income/expenses queries
        if 'income' in query_lower:
            return self._handle_income_query()

        if 'expense' in query_lower or 'expenses' in query_lower:
            return self._handle_expense_query()

        # Recommendation queries
        if 'recommend' in query_lower or 'suggestion' in query_lower:
            return self._handle_recommendations_query()

        # Default fallback
        return self._handle_fallback()

    def _handle_greeting(self) -> str:
        """Greeting response."""
        metrics = self.engine.get_dashboard_metrics()
        return (
            f"Hello! 👋 Welcome to your Personal Finance Advisor. "
            f"I'm here to help you optimize your finances.\n\n"
            f"**Your Current Status:**\n"
            f"- Monthly Income: ${metrics['monthly_income']:,.0f}\n"
            f"- Monthly Expenses: ${metrics['total_expenses']:,.0f}\n"
            f"- Net Savings: ${metrics['net_savings']:,.0f}\n"
            f"- Savings Rate: {metrics['savings_percentage']:.1f}%\n\n"
            f"Feel free to ask me about your spending, savings opportunities, or specific categories!"
        )

    def _handle_how_to_save(self) -> str:
        """Response to 'How can I save more?' type queries."""
        high_rec = [r for r in self.recommendations if r['priority'] == 'HIGH']

        if not high_rec:
            return (
                f"Great news! Your spending is already well-optimized. "
                f"You're currently saving ${self.engine.net_savings:,.0f}/month ({self.engine.savings_percentage:.1f}%).\n\n"
                f"To save more, consider:\n"
                f"1. Reducing discretionary spending (Entertainment, Shopping)\n"
                f"2. Negotiating fixed costs (Rent, Utilities)\n"
                f"3. Automating savings to ensure consistency"
            )

        response = "**Top Opportunities to Save More:**\n\n"
        for i, rec in enumerate(high_rec[:3], 1):
            response += f"{i}. **{rec['title']}**\n"
            response += f"   Potential monthly savings: ${rec['potential_savings']:,.0f}\n"
            response += f"   Action: {rec['action']}\n\n"

        return response

    def _handle_high_spending(self) -> str:
        """Response to 'Where am I spending too much?' type queries."""
        high_spending = self.engine.identify_high_spending_categories()

        if not high_spending:
            return (
                "Excellent! Your spending across all categories is within recommended benchmarks. "
                "You're managing your finances efficiently."
            )

        response = "**Your High Spending Categories:**\n\n"
        for i, (category, amount, percentage) in enumerate(high_spending, 1):
            response += f"{i}. **{category}**: ${amount:,.0f} ({percentage:.1f}% of income)\n"

        response += "\nThese categories exceed 30% of your income. Consider optimization strategies for each."
        return response

    def _handle_savings_percentage(self) -> str:
        """Response to savings percentage queries."""
        target = ExpenseDataManager.TARGET_SAVINGS_PERCENTAGE * 100
        current = self.engine.savings_percentage
        gap = target - current

        if gap <= 0:
            return (
                f"Excellent! Your current savings rate is {current:.1f}%, "
                f"which exceeds the recommended target of {target:.1f}%. "
                f"You're on track for financial health!"
            )
        else:
            monthly_gap = self.engine.monthly_income * (gap / 100)
            return (
                f"Your current savings rate is {current:.1f}%. "
                f"The recommended target is {target:.1f}%.\n\n"
                f"To reach your target:\n"
                f"- Increase monthly savings by: ${monthly_gap:,.0f}\n"
                f"- Reduce monthly expenses by: ${monthly_gap:,.0f}\n\n"
                f"This is achievable through strategic spending reductions across high-spending categories."
            )

    def _handle_savings_general(self) -> str:
        """General savings information."""
        metrics = self.engine.get_dashboard_metrics()
        return (
            f"**Your Savings Overview:**\n\n"
            f"- Current Monthly Savings: ${metrics['net_savings']:,.0f}\n"
            f"- Savings Rate: {metrics['savings_percentage']:.1f}%\n"
            f"- Annual Savings Potential: ${metrics['net_savings'] * 12:,.0f}\n\n"
            f"Industry Target: 20% of income\n"
            f"Your Target Monthly Savings: ${self.engine.monthly_income * 0.20:,.0f}\n\n"
            f"You're currently " +
            ("ahead of target! Keep it up! 🎯" if self.engine.savings_percentage >= 20 else
             f"${(self.engine.monthly_income * 0.20 - metrics['net_savings']):,.0f}/month away from target.")
        )

    def _handle_spending_analysis(self) -> str:
        """General spending analysis."""
        top_categories = self.engine.get_top_spending_categories(3)
        response = "**Your Top Spending Categories:**\n\n"

        for i, (category, amount) in enumerate(top_categories, 1):
            pct = (amount / self.engine.monthly_income) * 100
            response += f"{i}. {category}: ${amount:,.0f} ({pct:.1f}%)\n"

        response += f"\nTotal Monthly Expenses: ${self.engine.total_expenses:,.0f}"
        return response

    def _handle_category_query(self, category: str, query_lower: str) -> str:
        """Response to category-specific queries."""
        amount = self.engine.expenses.get(category, 0)
        percentage = (amount / self.engine.monthly_income) * 100 if self.engine.monthly_income > 0 else 0
        benchmark = ExpenseDataManager.BENCHMARKS.get(category, 0) * 100

        response = f"**{category} Spending Analysis:**\n\n"
        response += f"Current Spending: ${amount:,.0f} ({percentage:.1f}% of income)\n"
        response += f"Industry Benchmark: {benchmark:.1f}% of income\n\n"

        if 'reduce' in query_lower or 'cut' in query_lower:
            reduction = amount * 0.10
            response += f"**Reduction Strategy:**\n"
            response += f"A 10% reduction would save: ${reduction:,.0f}/month\n"
            response += f"New spending level: ${amount - reduction:,.0f}"
        elif 'how' in query_lower:
            response += f"**Optimization Suggestions:**\n"
            if percentage > benchmark + 5:
                response += f"1. Your {category} spending is {percentage - benchmark:.1f}% above benchmark\n"
                response += f"2. Target reduction: {percentage - benchmark:.1f}% of income\n"
                response += f"3. Monthly savings potential: ${amount - (self.engine.monthly_income * benchmark / 100):,.0f}\n"
            else:
                response += f"Your {category} spending is well-managed relative to benchmarks."

        return response

    def _handle_income_query(self) -> str:
        """Response to income-related queries."""
        return (
            f"**Your Income Information:**\n\n"
            f"Monthly Income: ${self.engine.monthly_income:,.0f}\n"
            f"Annual Income: ${self.engine.monthly_income * 12:,.0f}\n\n"
            f"**Income Allocation:**\n"
            f"- Current Spending: {(self.engine.total_expenses / self.engine.monthly_income * 100):.1f}%\n"
            f"- Current Savings: {self.engine.savings_percentage:.1f}%"
        )

    def _handle_expense_query(self) -> str:
        """Response to general expense queries."""
        metrics = self.engine.get_dashboard_metrics()
        return (
            f"**Your Expense Summary:**\n\n"
            f"Total Monthly Expenses: ${metrics['total_expenses']:,.0f}\n"
            f"As % of Income: {(metrics['total_expenses'] / metrics['monthly_income'] * 100):.1f}%\n\n"
            f"**Top 3 Spending Categories:**\n" +
            "\n".join([
                f"{i}. {cat}: ${amt:,.0f}"
                for i, (cat, amt) in enumerate(self.engine.get_top_spending_categories(3), 1)
            ])
        )

    def _handle_recommendations_query(self) -> str:
        """Response to recommendation queries."""
        if not self.recommendations:
            return "No specific recommendations at this time. Your spending is well-optimized!"

        response = "**Recommended Actions (by Impact):**\n\n"
        for i, rec in enumerate(self.recommendations[:5], 1):
            response += f"{i}. {rec['title']}\n"
            response += f"   💰 Save: ${rec['potential_savings']:,.0f}/month\n"
            response += f"   📋 {rec['action']}\n\n"

        return response

    def _handle_fallback(self) -> str:
        """Fallback response for unrecognized queries."""
        return (
            "I'm here to help with your finances! 💰\n\n"
            "You can ask me about:\n"
            "- How to save more on your spending\n"
            "- Where you're spending too much\n"
            "- Your savings percentage and goals\n"
            "- Specific spending categories\n"
            "- Recommendations for optimization\n\n"
            "What would you like to know?"
        )


# ============================================================================
# STREAMLIT UI - Dashboard and Visualization
# ============================================================================

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'analysis_engine' not in st.session_state:
        customer_data = ExpenseDataManager.get_sample_customer_data()
        st.session_state.analysis_engine = ExpenseAnalysisEngine(
            customer_data['monthly_income'],
            customer_data['expenses']
        )
    if 'recommendation_engine' not in st.session_state:
        st.session_state.recommendation_engine = RecommendationEngine(
            st.session_state.analysis_engine
        )


def render_metrics_dashboard():
    """Render key metrics on dashboard."""
    metrics = st.session_state.analysis_engine.get_dashboard_metrics()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Monthly Income",
            value=f"${metrics['monthly_income']:,.0f}",
            delta=None
        )

    with col2:
        st.metric(
            label="Total Expenses",
            value=f"${metrics['total_expenses']:,.0f}",
            delta=f"{(metrics['total_expenses']/metrics['monthly_income']*100):.1f}% of income"
        )

    with col3:
        st.metric(
            label="Net Savings",
            value=f"${metrics['net_savings']:,.0f}",
            delta=f"+{metrics['savings_percentage']:.1f}%",
            delta_color="normal" if metrics['savings_percentage'] >= 20 else "off"
        )

    with col4:
        st.metric(
            label="Savings Rate",
            value=f"{metrics['savings_percentage']:.1f}%",
            delta="Target: 20%",
            delta_color="normal" if metrics['savings_percentage'] >= 20 else "inverse"
        )


def render_expense_pie_chart():
    """Render expense breakdown pie chart."""
    engine = st.session_state.analysis_engine

    fig = go.Figure(data=[go.Pie(
        labels=list(engine.expenses.keys()),
        values=list(engine.expenses.values()),
        hovertemplate='<b>%{label}</b><br>Amount: $%{value:,.0f}<br>Percentage: %{percent}<extra></extra>',
    )])

    fig.update_layout(
        title="Expense Breakdown by Category",
        height=400,
        showlegend=True,
    )

    st.plotly_chart(fig, use_container_width=True)


def render_spending_bar_chart():
    """Render monthly spending by category bar chart."""
    engine = st.session_state.analysis_engine
    percentages = engine.get_category_percentages()

    categories = list(percentages.keys())
    values = list(percentages.values())
    benchmark_values = [
        ExpenseDataManager.BENCHMARKS.get(cat, 0) * 100 for cat in categories
    ]

    fig = go.Figure(data=[
        go.Bar(
            name='Your Spending',
            x=categories,
            y=values,
            marker_color='steelblue',
            hovertemplate='%{x}<br>Your Spending: %{y:.1f}%<extra></extra>',
        ),
        go.Bar(
            name='Industry Benchmark',
            x=categories,
            y=benchmark_values,
            marker_color='lightgray',
            hovertemplate='%{x}<br>Benchmark: %{y:.1f}%<extra></extra>',
        )
    ])

    fig.update_layout(
        title="Spending by Category vs Industry Benchmark",
        xaxis_title="Category",
        yaxis_title="% of Income",
        height=400,
        barmode='group',
        hovermode='x unified',
    )

    st.plotly_chart(fig, use_container_width=True)


def render_savings_trend_chart():
    """Render savings trend over multiple months."""
    df = ExpenseDataManager.get_multiple_months_data()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['Month'],
        y=df['Savings_Percentage'],
        mode='lines+markers',
        name='Savings %',
        line=dict(color='green', width=2),
        marker=dict(size=6),
        hovertemplate='<b>%{x|%B %Y}</b><br>Savings Rate: %{y:.1f}%<extra></extra>',
    ))

    # Add benchmark line
    target_line = ExpenseDataManager.TARGET_SAVINGS_PERCENTAGE * 100
    fig.add_hline(
        y=target_line,
        line_dash="dash",
        line_color="orange",
        annotation_text=f"Target ({target_line:.0f}%)",
        annotation_position="right"
    )

    fig.update_layout(
        title="Savings Rate Trend (12 Months)",
        xaxis_title="Month",
        yaxis_title="Savings Rate (%)",
        height=400,
        hovermode='x unified',
    )

    st.plotly_chart(fig, use_container_width=True)


def render_high_spending_analysis():
    """Render analysis of high spending categories."""
    engine = st.session_state.analysis_engine
    high_spending = engine.identify_high_spending_categories()

    st.subheader("🚨 High Spending Alert")

    if high_spending:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.warning(
                f"**You have {len(high_spending)} category(ies) exceeding 30% of income threshold**"
            )

            for category, amount, percentage in high_spending:
                st.markdown(f"**{category}**: ${amount:,.0f} ({percentage:.1f}%)")

        with col2:
            potential_savings = engine.calculate_potential_savings()
            total_potential = sum(potential_savings.values())
            st.info(f"**Potential Monthly Savings**\n\n${total_potential:,.0f}")
    else:
        st.success("✅ No categories exceed 30% threshold. Well done!")


def render_recommendations():
    """Render actionable savings recommendations."""
    recommendations = st.session_state.recommendation_engine.generate_recommendations()

    st.subheader("💡 Savings Recommendations")

    if not recommendations:
        st.info("Your spending is well-optimized. No specific recommendations at this time.")
        return

    # Create tabs for recommendation priority levels
    priority_map = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    sorted_recs = sorted(recommendations, key=lambda x: priority_map.get(x['priority'], 3))

    for i, rec in enumerate(sorted_recs, 1):
        priority_color = {
            'HIGH': '🔴',
            'MEDIUM': '🟡',
            'LOW': '🟢'
        }.get(rec['priority'], '⚪')

        with st.expander(f"{priority_color} {rec['title']} - Save ${rec['potential_savings']:,.0f}/month"):
            st.markdown(f"**Priority:** {rec['priority']}")
            st.markdown(f"**Category:** {rec['category']}")
            st.markdown(f"**Description:** {rec['description']}")
            st.markdown(f"**Monthly Savings Potential:** ${rec['potential_savings']:,.0f}")
            st.markdown(f"**Annual Savings:** ${rec['potential_savings'] * 12:,.0f}")
            st.markdown(f"**Action:** {rec['action']}")


def render_chatbot():
    """Render interactive chatbot interface."""
    st.subheader("💬 Finance Advisor Chatbot")

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    # Chat input
    user_input = st.chat_input("Ask me anything about your finances...")

    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input
        })

        # Generate bot response
        responder = ChatbotResponder(
            st.session_state.analysis_engine,
            st.session_state.recommendation_engine.generate_recommendations()
        )
        bot_response = responder.respond_to_query(user_input)

        # Add bot response to history
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': bot_response
        })

        # Rerun to display new message
        st.rerun()


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Personal Finance Advisor",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for better appearance
    st.markdown("""
        <style>
        .metric-card {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 5px;
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    initialize_session_state()

    # Header
    st.title("💰 Personal Finance Advisor Agent")
    st.markdown(
        "Intelligent expense analysis and savings recommendations powered by AI"
    )

    # Sidebar navigation
    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Analysis", "Chatbot"],
        icons=["📊", "📈", "💬"]
    )

    # Dashboard tab content
    if page == "Dashboard":
        st.markdown("---")
        render_metrics_dashboard()
        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            render_expense_pie_chart()
        with col2:
            render_spending_bar_chart()

        render_high_spending_analysis()

        st.markdown("---")
        render_savings_trend_chart()

    # Analysis tab content
    elif page == "Analysis":
        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Spending Summary")
            engine = st.session_state.analysis_engine

            st.markdown("**By Category:**")
            for category, amount in sorted(engine.expenses.items(), key=lambda x: x[1], reverse=True):
                pct = (amount / engine.monthly_income) * 100
                st.markdown(f"- {category}: ${amount:,.0f} ({pct:.1f}%)")

        with col2:
            st.subheader("📈 Benchmark Comparison")
            comparison = engine.get_benchmark_comparison()

            for category, data in comparison.items():
                status_icon = "✅" if data['status'] == 'UNDER' else "⚠️"
                st.markdown(
                    f"{status_icon} **{category}**\n"
                    f"- Your: {data['user_spending']:.1f}% | Benchmark: {data['benchmark']:.1f}% | "
                    f"Diff: {data['difference']:+.1f}%"
                )

        st.markdown("---")
        render_recommendations()

    # Chatbot tab content
    elif page == "Chatbot":
        st.markdown("---")
        render_chatbot()

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #888; font-size: 0.9em;'>
        Personal Finance Advisor Agent v1.0 | Built with Streamlit<br>
        Data-driven insights for smarter financial decisions
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
