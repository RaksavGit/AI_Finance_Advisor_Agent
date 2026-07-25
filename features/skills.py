"""
Skills and Subagents Framework
Implements modular skill-based architecture with subagent support.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
import uuid
import time


class SkillType(Enum):
    """Types of skills in the system."""
    ANALYZER = "analyzer"
    CALCULATOR = "calculator"
    GENERATOR = "generator"
    RESPONDER = "responder"
    ADVISOR = "advisor"
    TRACKER = "tracker"


@dataclass
class SkillMetadata:
    """Metadata for a skill."""
    name: str
    type: SkillType
    version: str
    dependencies: List[str] = field(default_factory=list)
    description: str = ""
    author: str = ""
    enabled: bool = True


@dataclass
class SkillExecutionContext:
    """Context for skill execution."""
    skill_id: str
    session_id: str
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    error: Optional[str] = None
    status: str = "pending"  # pending, executing, completed, failed

    def to_dict(self) -> Dict[str, Any]:
        return {
            'skill_id': self.skill_id,
            'session_id': self.session_id,
            'execution_id': self.execution_id,
            'timestamp': self.timestamp.isoformat(),
            'input_data': self.input_data,
            'output_data': self.output_data,
            'execution_time_ms': self.execution_time_ms,
            'error': self.error,
            'status': self.status,
        }


class BaseSkill(ABC):
    """Base class for all skills."""

    def __init__(self, metadata: SkillMetadata):
        self.metadata = metadata
        self.execution_history: List[SkillExecutionContext] = []
        self._pre_hooks: List[Callable] = []
        self._post_hooks: List[Callable] = []

    @abstractmethod
    def execute(self, context: SkillExecutionContext) -> Dict[str, Any]:
        """Execute the skill. Must be implemented by subclasses."""
        pass

    def run(self, input_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Run the skill with execution tracking."""
        context = SkillExecutionContext(
            skill_id=self.metadata.name,
            session_id=session_id,
            input_data=input_data,
            status="executing"
        )

        start_time = time.time()

        try:
            # Execute pre-hooks
            for hook in self._pre_hooks:
                hook(context)

            # Execute skill
            output = self.execute(context)
            context.output_data = output
            context.status = "completed"

            # Execute post-hooks
            for hook in self._post_hooks:
                hook(context)

        except Exception as e:
            context.error = str(e)
            context.status = "failed"
            raise

        finally:
            context.execution_time_ms = (time.time() - start_time) * 1000
            self.execution_history.append(context)

        return context.output_data

    def add_pre_hook(self, hook: Callable):
        """Add a pre-execution hook."""
        self._pre_hooks.append(hook)

    def add_post_hook(self, hook: Callable):
        """Add a post-execution hook."""
        self._post_hooks.append(hook)

    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get execution history."""
        return [ctx.to_dict() for ctx in self.execution_history]

    def get_metrics(self) -> Dict[str, Any]:
        """Get skill metrics."""
        if not self.execution_history:
            return {
                'total_executions': 0,
                'successful': 0,
                'failed': 0,
                'average_time_ms': 0,
            }

        successful = sum(1 for ctx in self.execution_history if ctx.status == 'completed')
        failed = sum(1 for ctx in self.execution_history if ctx.status == 'failed')
        avg_time = sum(ctx.execution_time_ms for ctx in self.execution_history) / len(self.execution_history)

        return {
            'total_executions': len(self.execution_history),
            'successful': successful,
            'failed': failed,
            'success_rate': successful / len(self.execution_history) * 100 if self.execution_history else 0,
            'average_time_ms': avg_time,
        }


class Subagent:
    """Represents a specialized subagent composed of multiple skills."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.skills: Dict[str, BaseSkill] = {}
        self.execution_sequence: List[str] = []

    def add_skill(self, skill: BaseSkill):
        """Add a skill to the subagent."""
        self.skills[skill.metadata.name] = skill

    def set_execution_sequence(self, sequence: List[str]):
        """Set the order in which skills should execute."""
        self.execution_sequence = sequence

    def execute(self, input_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Execute subagent by running all skills in sequence."""
        result = input_data.copy()

        skills_to_run = self.execution_sequence or list(self.skills.keys())

        for skill_name in skills_to_run:
            if skill_name not in self.skills:
                raise ValueError(f"Skill {skill_name} not found in subagent")

            skill = self.skills[skill_name]
            result = skill.run(result, session_id)

        return result

    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics for all skills in subagent."""
        return {
            skill_name: skill.get_metrics()
            for skill_name, skill in self.skills.items()
        }


class SkillRegistry:
    """Central registry for managing all skills and subagents."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.skills: Dict[str, BaseSkill] = {}
            cls._instance.subagents: Dict[str, Subagent] = {}
            cls._instance.skill_chain: List[str] = []
        return cls._instance

    @classmethod
    def get_instance(cls):
        """Get singleton instance."""
        return cls()

    def register_skill(self, skill: BaseSkill) -> None:
        """Register a skill."""
        if not skill.metadata.enabled:
            return

        self.skills[skill.metadata.name] = skill

    def register_subagent(self, subagent: Subagent) -> None:
        """Register a subagent."""
        self.subagents[subagent.name] = subagent

    def get_skill(self, name: str) -> Optional[BaseSkill]:
        """Get a skill by name."""
        return self.skills.get(name)

    def get_subagent(self, name: str) -> Optional[Subagent]:
        """Get a subagent by name."""
        return self.subagents.get(name)

    def execute_skill(self, skill_name: str, input_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Execute a single skill."""
        skill = self.get_skill(skill_name)
        if not skill:
            raise ValueError(f"Skill {skill_name} not found")
        return skill.run(input_data, session_id)

    def execute_subagent(self, subagent_name: str, input_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Execute a subagent."""
        subagent = self.get_subagent(subagent_name)
        if not subagent:
            raise ValueError(f"Subagent {subagent_name} not found")
        return subagent.execute(input_data, session_id)

    def list_skills(self) -> List[str]:
        """List all registered skills."""
        return list(self.skills.keys())

    def list_subagents(self) -> List[str]:
        """List all registered subagents."""
        return list(self.subagents.keys())

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics."""
        return {
            'total_skills': len(self.skills),
            'total_subagents': len(self.subagents),
            'skills': {
                name: skill.get_metrics()
                for name, skill in self.skills.items()
            },
            'subagents': {
                name: subagent.get_metrics()
                for name, subagent in self.subagents.items()
            }
        }


# Concrete Skill Implementations

class ExpenseAnalyzerSkill(BaseSkill):
    """Skill for analyzing expenses."""

    def __init__(self):
        metadata = SkillMetadata(
            name="expense_analyzer",
            type=SkillType.ANALYZER,
            version="1.0",
            description="Analyzes customer expenses and identifies patterns",
            dependencies=[]
        )
        super().__init__(metadata)

    def execute(self, context: SkillExecutionContext) -> Dict[str, Any]:
        """Execute expense analysis."""
        income = context.input_data.get('income', 0)
        expenses = context.input_data.get('expenses', {})

        total_expenses = sum(expenses.values())
        net_savings = income - total_expenses
        savings_percentage = (net_savings / income * 100) if income > 0 else 0

        category_percentages = {
            cat: (amt / income * 100) if income > 0 else 0
            for cat, amt in expenses.items()
        }

        return {
            'total_expenses': total_expenses,
            'net_savings': net_savings,
            'savings_percentage': savings_percentage,
            'category_percentages': category_percentages,
            'expenses': expenses,
            'income': income,
        }


class RecommendationGeneratorSkill(BaseSkill):
    """Skill for generating recommendations."""

    def __init__(self):
        metadata = SkillMetadata(
            name="recommendation_generator",
            type=SkillType.GENERATOR,
            version="1.0",
            description="Generates prioritized savings recommendations",
            dependencies=["expense_analyzer"]
        )
        super().__init__(metadata)

    def execute(self, context: SkillExecutionContext) -> Dict[str, Any]:
        """Execute recommendation generation."""
        analysis = context.input_data.get('analysis', {})
        benchmarks = context.input_data.get('benchmarks', {})

        recommendations = []

        # High spending recommendations
        for category, percentage in analysis.get('category_percentages', {}).items():
            if percentage > 30:  # 30% threshold
                savings = analysis['expenses'][category] * 0.10
                recommendations.append({
                    'priority': 'HIGH',
                    'category': category,
                    'title': f'Reduce {category} Spending',
                    'potential_savings': savings,
                    'description': f'{category} spending at {percentage:.1f}% exceeds recommended levels.'
                })

        # Sort by savings potential
        recommendations.sort(key=lambda x: x['potential_savings'], reverse=True)

        return {
            'recommendations': recommendations,
            'total_potential_savings': sum(r['potential_savings'] for r in recommendations),
            'recommendation_count': len(recommendations),
        }


class ChatResponderSkill(BaseSkill):
    """Skill for responding to chat queries."""

    def __init__(self):
        metadata = SkillMetadata(
            name="chat_responder",
            type=SkillType.RESPONDER,
            version="1.0",
            description="Responds to user queries using financial data",
            dependencies=["expense_analyzer", "recommendation_generator"]
        )
        super().__init__(metadata)

    def execute(self, context: SkillExecutionContext) -> Dict[str, Any]:
        """Execute chat response generation with enhanced question handling."""
        query = context.input_data.get('query', '')
        analysis = context.input_data.get('analysis', {})
        recommendations = context.input_data.get('recommendations', {})

        query_lower = query.lower()
        response = ""

        # Validate we have actual data
        if not analysis or analysis == {}:
            return {
                'response': "Please run the **Analyze Finances** button on the Dashboard first to get financial insights. I need your income and expense data to help you!",
                'query': query,
                'intent': 'financial_query',
            }

        # 1. How to save more / Savings opportunities
        if ('save' in query_lower or 'savings' in query_lower) and ('how' in query_lower or 'more' in query_lower):
            recs = recommendations.get('recommendations', []) if isinstance(recommendations, dict) else recommendations
            savings_rate = analysis.get('savings_percentage', 0)
            monthly_income = analysis.get('monthly_income', 1)  # Default to 1 to avoid division by zero
            current_savings = analysis.get('net_savings', 0)

            # Calculate target: 20% of monthly income
            target_savings = monthly_income * 0.20

            # Calculate gap: how much more needs to be saved to reach 20% target
            gap_to_target = target_savings - current_savings

            # Ensure gap is never negative (use absolute value for display, but logic handles direction)
            if gap_to_target < 0:
                gap_to_target = 0  # Already exceeding target

            if recs:
                total_potential = sum(rec.get('potential_savings', 0) for rec in recs if isinstance(rec, dict))
                response = f"**Top Opportunities to Save More:**\n\n📊 **Total Potential Savings: ₹{total_potential:,.0f}/month**\n\n"

                for i, rec in enumerate(recs[:5], 1):
                    title = rec.get('title', 'Recommendation') if isinstance(rec, dict) else str(rec)
                    savings = rec.get('potential_savings', 0) if isinstance(rec, dict) else 0
                    action = rec.get('action', '') if isinstance(rec, dict) else ''
                    priority = rec.get('priority', 'MEDIUM') if isinstance(rec, dict) else 'MEDIUM'
                    description = rec.get('description', '') if isinstance(rec, dict) else ''

                    # Add priority emoji
                    priority_emoji = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(priority, '⚪')

                    response += f"{i}. {priority_emoji} **{title}**\n"
                    response += f"   💰 Save: ₹{savings:,.0f}/month\n"
                    if description:
                        response += f"   📝 {description}\n"
                    if action:
                        response += f"   🎯 {action}\n\n"
            else:
                # Evaluate if savings rate is actually good
                if savings_rate >= 20:
                    excess = current_savings - target_savings
                    response = f"🎉 **Excellent Savings Rate!**\n\nYour current savings rate is {savings_rate:.1f}%, which exceeds the recommended 20% target by ₹{max(0, excess):,.0f}/month. Keep up this excellent work!"
                elif savings_rate >= 15:
                    response = f"✅ **Good Savings Rate**\n\nYour current savings rate is {savings_rate:.1f}%. While close to the 20% target, there's room for improvement. You need to increase savings by ₹{gap_to_target:,.0f}/month to reach your goal."
                elif savings_rate >= 10:
                    response = f"⚠️ **Below Target Savings Rate**\n\nYour current savings rate is {savings_rate:.1f}%. Target is 20%. You need to reduce expenses by approximately ₹{gap_to_target:,.0f}/month to reach your goal."
                else:
                    # For savings rate < 10% - Show action plan with specific methods
                    response = f"🚨 **Critical: Low Savings Rate**\n\nYour current savings rate is only {savings_rate:.1f}%. This is concerning. Target is 20%.\n\n**Action Plan to Increase Savings by ₹{max(gap_to_target, 0):,.0f}/month:**\n\n**1. Immediate Actions (Quick Wins):**\n   • 🍚 **Food & Dining**: Reduce restaurant expenses, cook at home\n   • 🛍️ **Shopping**: Stop impulse purchases, plan ahead\n   • 🎬 **Entertainment**: Cut subscriptions you don't use regularly\n\n**2. Medium-term (1-3 months):**\n   • 📱 **Utilities**: Compare providers, optimize usage\n   • 🚗 **Travel**: Use public transport, carpool\n   • 🎫 **Entertainment**: Find free/low-cost options\n\n**3. Long-term Adjustments:**\n   • 🏠 **Housing**: Negotiate rent or find cheaper accommodation\n   • 💳 **Debt**: Consider refinancing high-interest loans\n   • 💼 **Income**: Look for better job opportunities\n\n**4. Automation:**\n   • Set up auto-transfer to savings account on payday\n   • Use budgeting apps to track spending\n   • Review monthly progress\n\nStart with 1-2 quick wins and build from there!"

        # 2. General savings inquiry
        elif 'save' in query_lower or 'savings' in query_lower:
            savings_rate = analysis.get('savings_percentage', 0)
            monthly_savings = analysis.get('net_savings', 0)
            monthly_income = analysis.get('monthly_income', 0)
            target_savings = monthly_income * 0.20
            recs = recommendations.get('recommendations', []) if isinstance(recommendations, dict) else []

            response = f"**Your Savings Overview:**\n\n💰 Current savings rate: {savings_rate:.1f}%\n💵 Monthly savings: ₹{monthly_savings:,.0f}\n📊 Annual savings potential: ₹{monthly_savings * 12:,.0f}\n\n**Target vs Actual:**\n🎯 Target savings (20%): ₹{target_savings:,.0f}/month\n"

            if monthly_savings >= target_savings:
                gap = monthly_savings - target_savings
                response += f"✅ You're exceeding your target by ₹{gap:,.0f}/month! Excellent work!"
            else:
                gap = target_savings - monthly_savings
                response += f"⚠️ Gap to reach target: ₹{gap:,.0f}/month\n\n"

                # Show recommendations if available
                if recs:
                    total_potential = sum(rec.get('potential_savings', 0) for rec in recs if isinstance(rec, dict))
                    response += f"**Recommended Actions (Total potential: ₹{total_potential:,.0f}/month):**\n\n"
                    for i, rec in enumerate(recs[:3], 1):
                        title = rec.get('title', 'Recommendation') if isinstance(rec, dict) else str(rec)
                        savings = rec.get('potential_savings', 0) if isinstance(rec, dict) else 0
                        action = rec.get('action', '') if isinstance(rec, dict) else ''
                        response += f"{i}. **{title}** - Save ₹{savings:,.0f}/month\n   {action}\n\n"
                else:
                    response += "💡 Focus on reducing discretionary expenses to close this gap."

        # 3. High spending categories / Where am I spending too much
        elif any(word in query_lower for word in ['spend', 'spending', 'expensive', 'where', 'most']):
            total_exp = analysis.get('total_expenses', 0)
            if total_exp > 0:
                exp_pct = (total_exp / analysis.get('monthly_income', 1)) * 100
                response = f"**Your Spending Analysis:**\n\n💸 Total monthly expenses: ₹{total_exp:,.0f}\n📈 Percentage of income: {exp_pct:.1f}%\n\n**Top expense categories:**"
                # Get category percentages if available
                cat_pcts = analysis.get('category_percentages', {})
                if cat_pcts:
                    sorted_cats = sorted(cat_pcts.items(), key=lambda x: x[1], reverse=True)
                    for i, (cat, pct) in enumerate(sorted_cats[:3], 1):
                        response += f"\n{i}. **{cat}**: {pct:.1f}% of income"
            else:
                response = "**Your Spending Analysis:**\n\nNo spending data available yet. Please enter your expenses."

        # 4. Income related questions
        elif 'income' in query_lower:
            response = f"**Your Income Information:**\n\n💰 Monthly income: ₹{analysis.get('monthly_income', 0):,.0f}\n📅 Annual income: ₹{analysis.get('monthly_income', 0) * 12:,.0f}\n\n**Income allocation:**\n- Spending: {(analysis.get('total_expenses', 0) / analysis.get('monthly_income', 1) * 100):.1f}%\n- Savings: {analysis.get('savings_percentage', 0):.1f}%"

        # 5. Budget related questions
        elif any(word in query_lower for word in ['budget', 'plan', 'allocate']):
            response = f"**Budget Planning:**\n\n📋 Recommended budget allocation:\n- Rent/Housing: 30% (₹{analysis.get('monthly_income', 0) * 0.30:,.0f})\n- Food: 15% (₹{analysis.get('monthly_income', 0) * 0.15:,.0f})\n- Utilities: 8% (₹{analysis.get('monthly_income', 0) * 0.08:,.0f})\n- Transportation: 10% (₹{analysis.get('monthly_income', 0) * 0.10:,.0f})\n- Entertainment: 7% (₹{analysis.get('monthly_income', 0) * 0.07:,.0f})\n- Savings: 20% (₹{analysis.get('monthly_income', 0) * 0.20:,.0f})\n\nAdjust based on your priorities and lifestyle!"

        # 6. Goals / Targets related
        elif any(word in query_lower for word in ['goal', 'target', 'achieve', 'reach']):
            target_savings = analysis.get('monthly_income', 0) * 0.20
            current_savings = analysis.get('net_savings', 0)
            gap = target_savings - current_savings
            response = f"**Financial Goals & Targets:**\n\n🎯 Recommended savings target: ₹{target_savings:,.0f}/month (20% of income)\n✅ Your current savings: ₹{current_savings:,.0f}/month\n\n"
            if gap > 0:
                response += f"📈 To reach your target, increase monthly savings by: ₹{gap:,.0f}\n💡 This could be achieved by reducing discretionary spending or increasing income."
            else:
                response += f"🎉 Excellent! You're already saving ₹{abs(gap):,.0f} more than the 20% target!"

        # 7. Debt / EMI related
        elif any(word in query_lower for word in ['debt', 'emi', 'loan', 'obligation']):
            response = "**Debt Management Tips:**\n\n📌 Best practices:\n1. **Priority**: Pay high-interest debt first\n2. **Allocation**: Keep debt payments to 15% of income max\n3. **Timeline**: Try to eliminate non-essential debt in 3-5 years\n4. **Strategy**: Build emergency fund (3-6 months expenses) alongside debt repayment\n\nEnter your EMI details in the dashboard for personalized analysis!"

        # 8. Category specific questions (Rent, Food, etc.)
        elif any(cat in query_lower for cat in ['rent', 'food', 'utilities', 'travel', 'shopping', 'entertainment']):
            for cat in ['Rent', 'Food', 'Utilities', 'Travel', 'Shopping', 'Entertainment']:
                if cat.lower() in query_lower:
                    cat_pct = analysis.get('category_percentages', {}).get(cat, 0)
                    response = f"**{cat} Spending Analysis:**\n\n💰 Your {cat.lower()} spending: {cat_pct:.1f}% of income\n\n**Recommendations:**\n"
                    if cat.lower() == 'rent':
                        response += "- Keep housing costs ≤ 30% of income\n- Consider shared living to reduce costs"
                    elif cat.lower() == 'food':
                        response += "- Target: 12-15% of income\n- Try meal planning and cooking at home"
                    elif cat.lower() == 'utilities':
                        response += "- Target: 6-8% of income\n- Optimize usage to reduce costs"
                    elif cat.lower() == 'travel':
                        response += "- Target: 8-10% of income\n- Use public transport when possible"
                    elif cat.lower() == 'shopping':
                        response += "- Target: 10% of income\n- Plan purchases and avoid impulse buying"
                    elif cat.lower() == 'entertainment':
                        response += "- Target: 5-7% of income\n- Look for free/low-cost entertainment options"
                    break

        # 9. Help / Tips / Advice
        elif any(word in query_lower for word in ['help', 'advice', 'tips', 'how', 'what']):
            response = "**Financial Advice & Tips:**\n\n💡 Here's how I can help:\n1. **Save More**: Get personalized savings recommendations\n2. **Spending Tips**: Analyze where you're overspending\n3. **Income Info**: View your income allocation\n4. **Budget Plans**: Get recommended budget breakdown\n5. **Goal Setting**: Set and track financial targets\n6. **Debt Management**: Get debt reduction strategies\n7. **Category Analysis**: Deep dive into specific spending categories\n\nJust ask me about any of these topics!"

        # 10. Default/Fallback response
        if not response:
            response = "**How can I help with your finances?**\n\nYou can ask me about:\n💰 How to save more money\n📊 Your spending breakdown\n💵 Income and budget\n🎯 Financial goals and targets\n💳 Debt management\n🛒 Specific spending categories\n\nSimply ask your question!"

        return {
            'response': response,
            'query': query,
            'intent': 'financial_query',
        }


class GoalTrackerSkill(BaseSkill):
    """Skill for tracking financial goals."""

    def __init__(self):
        metadata = SkillMetadata(
            name="goal_tracker",
            type=SkillType.TRACKER,
            version="1.0",
            description="Tracks and monitors financial goals",
            dependencies=["expense_analyzer"]
        )
        super().__init__(metadata)

    def execute(self, context: SkillExecutionContext) -> Dict[str, Any]:
        """Execute goal tracking."""
        goals = context.input_data.get('goals', [])
        savings_rate = context.input_data.get('savings_percentage', 0)

        goal_status = []
        for goal in goals:
            progress = min(goal.get('current_amount', 0) / goal.get('target_amount', 1) * 100, 100)
            goal_status.append({
                'name': goal.get('name', 'Unknown'),
                'target': goal.get('target_amount', 0),
                'current': goal.get('current_amount', 0),
                'progress_pct': progress,
            })

        return {
            'goals': goal_status,
            'total_goals': len(goals),
            'on_track_count': sum(1 for g in goal_status if g['progress_pct'] >= 50),
        }


class BudgetPlannerSkill(BaseSkill):
    """Skill for budget planning."""

    def __init__(self):
        metadata = SkillMetadata(
            name="budget_planner",
            type=SkillType.ADVISOR,
            version="1.0",
            description="Creates and analyzes budgets",
            dependencies=["expense_analyzer"]
        )
        super().__init__(metadata)

    def execute(self, context: SkillExecutionContext) -> Dict[str, Any]:
        """Execute budget planning."""
        income = context.input_data.get('income', 0)
        current_spending = context.input_data.get('total_expenses', 0)
        target_savings_rate = context.input_data.get('target_savings_rate', 0.20)

        recommended_budget = income * (1 - target_savings_rate)
        budget_variance = current_spending - recommended_budget

        return {
            'recommended_budget': recommended_budget,
            'current_spending': current_spending,
            'variance': budget_variance,
            'status': 'under_budget' if budget_variance <= 0 else 'over_budget',
        }
