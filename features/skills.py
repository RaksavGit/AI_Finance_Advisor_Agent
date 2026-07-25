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
        """Execute chat response generation."""
        query = context.input_data.get('query', '')
        analysis = context.input_data.get('analysis', {})
        recommendations = context.input_data.get('recommendations', {})

        # Simple intent detection
        if 'save' in query.lower() or 'savings' in query.lower():
            response = f"Your current savings rate is {analysis.get('savings_percentage', 0):.1f}%"
        elif 'spend' in query.lower():
            response = f"Your total monthly expenses are ${analysis.get('total_expenses', 0):,.0f}"
        else:
            response = "How can I help you with your finances?"

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
