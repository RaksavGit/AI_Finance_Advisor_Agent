"""
Governance Framework
Implements business rules, validation, and compliance checks.
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class RuleType(Enum):
    """Types of business rules."""
    SPENDING_THRESHOLD = "spending_threshold"
    INCOME_VALIDATION = "income_validation"
    EXPENSE_VALIDATION = "expense_validation"
    SAVINGS_TARGET = "savings_target"
    RECOMMENDATION_VALIDATION = "recommendation_validation"
    COMPLIANCE_CHECK = "compliance_check"


@dataclass
class BusinessRule:
    """Represents a business rule."""
    name: str
    rule_type: RuleType
    description: str
    validator: Callable[[Dict[str, Any]], bool]
    error_message: str
    enabled: bool = True
    priority: int = 0  # Higher = more important


class GovernanceEngine:
    """Central engine for enforcing business rules and policies."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.rules: Dict[str, BusinessRule] = {}
            cls._instance.violation_log: List[Dict[str, Any]] = []
        return cls._instance

    @classmethod
    def get_instance(cls):
        """Get singleton instance."""
        return cls()

    def register_rule(self, rule: BusinessRule) -> None:
        """Register a business rule."""
        self.rules[rule.name] = rule

    def validate(self, rule_name: str, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate data against a specific rule."""
        rule = self.rules.get(rule_name)
        if not rule:
            return True, None

        if not rule.enabled:
            return True, None

        try:
            is_valid = rule.validator(data)
            if not is_valid:
                self._log_violation(rule_name, data, rule.error_message)
                return False, rule.error_message
            return True, None
        except Exception as e:
            self._log_violation(rule_name, data, str(e))
            return False, str(e)

    def validate_all(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate data against all enabled rules."""
        errors = []

        for rule_name, rule in sorted(self.rules.items(), key=lambda x: x[1].priority, reverse=True):
            is_valid, error = self.validate(rule_name, data)
            if not is_valid:
                errors.append(error)

        return len(errors) == 0, errors

    def _log_violation(self, rule_name: str, data: Dict[str, Any], error: str):
        """Log rule violation."""
        self.violation_log.append({
            'rule': rule_name,
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'data_keys': list(data.keys()),
            'error': error,
        })

        # Keep only recent violations
        if len(self.violation_log) > 1000:
            self.violation_log = self.violation_log[-500:]

    def disable_rule(self, rule_name: str) -> bool:
        """Disable a rule."""
        if rule_name in self.rules:
            self.rules[rule_name].enabled = False
            return True
        return False

    def enable_rule(self, rule_name: str) -> bool:
        """Enable a rule."""
        if rule_name in self.rules:
            self.rules[rule_name].enabled = True
            return True
        return False

    def get_violation_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent violations."""
        return self.violation_log[-limit:]

    def get_metrics(self) -> Dict[str, Any]:
        """Get governance metrics."""
        return {
            'total_rules': len(self.rules),
            'enabled_rules': sum(1 for r in self.rules.values() if r.enabled),
            'total_violations': len(self.violation_log),
            'rules': {
                name: {
                    'enabled': rule.enabled,
                    'type': rule.rule_type.value,
                    'priority': rule.priority,
                }
                for name, rule in self.rules.items()
            }
        }


class BusinessRulesValidator:
    """Validates business rules for finance advisor."""

    # Spending thresholds
    SPENDING_THRESHOLDS = {
        'Rent': 0.30,           # 30% of income
        'Food': 0.15,           # 15% of income
        'Utilities': 0.08,      # 8% of income
        'Transportation': 0.10, # 10% of income
        'Entertainment': 0.07,  # 7% of income
        'Shopping': 0.10,       # 10% of income
        'EMI': 0.15,            # 15% of income
    }

    HIGH_SPENDING_THRESHOLD = 0.30  # 30% alert threshold
    TARGET_SAVINGS_RATE = 0.20      # 20% target
    MIN_INCOME = 1
    MAX_INCOME = 1_000_000_000

    @staticmethod
    def validate_income(data: Dict[str, Any]) -> bool:
        """Validate income is within acceptable ranges."""
        income = data.get('income', 0)
        return BusinessRulesValidator.MIN_INCOME <= income <= BusinessRulesValidator.MAX_INCOME

    @staticmethod
    def validate_expenses(data: Dict[str, Any]) -> bool:
        """Validate expenses are valid."""
        expenses = data.get('expenses', {})

        if not isinstance(expenses, dict) or len(expenses) == 0:
            return False

        for category, amount in expenses.items():
            if not isinstance(amount, (int, float)) or amount < 0:
                return False

        return True

    @staticmethod
    def validate_income_expense_ratio(data: Dict[str, Any]) -> bool:
        """Validate expenses don't exceed 2x income."""
        income = data.get('income', 0)
        expenses = data.get('expenses', {})

        if income == 0:
            return False

        total_expenses = sum(expenses.values()) if expenses else 0
        return total_expenses <= income * 2

    @staticmethod
    def validate_category_threshold(data: Dict[str, Any]) -> bool:
        """Validate individual category spending doesn't exceed 50% of income."""
        income = data.get('income', 0)
        expenses = data.get('expenses', {})

        for category, amount in expenses.items():
            if income > 0 and (amount / income) > 0.50:
                return False

        return True

    @staticmethod
    def validate_recommendations_accuracy(data: Dict[str, Any]) -> bool:
        """Validate recommendations are reasonable."""
        recommendations = data.get('recommendations', [])

        for rec in recommendations:
            savings = rec.get('potential_savings', 0)

            # Savings can't be negative
            if savings < 0:
                return False

            # Savings can't exceed 1M
            if savings > 1_000_000:
                return False

        return True

    @staticmethod
    def validate_recommendation_integrity(data: Dict[str, Any]) -> bool:
        """Validate recommendation data integrity."""
        recommendations = data.get('recommendations', [])

        required_fields = ['title', 'priority', 'potential_savings']

        for rec in recommendations:
            if not all(field in rec for field in required_fields):
                return False

            if rec['priority'] not in ['HIGH', 'MEDIUM', 'LOW']:
                return False

        return True

    @staticmethod
    def validate_chat_compliance(data: Dict[str, Any]) -> bool:
        """Validate chat responses include proper disclaimers."""
        response = data.get('response', '')

        # Check for dangerous statements
        dangerous_phrases = [
            'guaranteed return',
            'guaranteed profit',
            'won\'t lose money',
            'sure thing',
        ]

        response_lower = response.lower()
        for phrase in dangerous_phrases:
            if phrase in response_lower:
                return False

        return True


def setup_governance_engine() -> GovernanceEngine:
    """Setup governance engine with default business rules."""
    engine = GovernanceEngine.get_instance()

    # Income Validation Rules
    engine.register_rule(BusinessRule(
        name='validate_income_range',
        rule_type=RuleType.INCOME_VALIDATION,
        description='Income must be within acceptable range',
        validator=BusinessRulesValidator.validate_income,
        error_message='Income must be between 1 and 1,000,000,000',
        priority=100
    ))

    # Expense Validation Rules
    engine.register_rule(BusinessRule(
        name='validate_expenses_format',
        rule_type=RuleType.EXPENSE_VALIDATION,
        description='Expenses must be valid dictionary with positive values',
        validator=BusinessRulesValidator.validate_expenses,
        error_message='Invalid expense data format',
        priority=100
    ))

    engine.register_rule(BusinessRule(
        name='validate_income_expense_ratio',
        rule_type=RuleType.SPENDING_THRESHOLD,
        description='Total expenses should not exceed 2x monthly income',
        validator=BusinessRulesValidator.validate_income_expense_ratio,
        error_message='Total expenses exceed 2x monthly income',
        priority=90
    ))

    engine.register_rule(BusinessRule(
        name='validate_category_threshold',
        rule_type=RuleType.SPENDING_THRESHOLD,
        description='No single category should exceed 50% of income',
        validator=BusinessRulesValidator.validate_category_threshold,
        error_message='Single expense category exceeds 50% threshold',
        priority=85
    ))

    # Recommendation Validation Rules
    engine.register_rule(BusinessRule(
        name='validate_recommendations_accuracy',
        rule_type=RuleType.RECOMMENDATION_VALIDATION,
        description='Recommendations should have reasonable savings amounts',
        validator=BusinessRulesValidator.validate_recommendations_accuracy,
        error_message='Recommendation savings amounts are unrealistic',
        priority=80
    ))

    engine.register_rule(BusinessRule(
        name='validate_recommendation_integrity',
        rule_type=RuleType.RECOMMENDATION_VALIDATION,
        description='Recommendations should have all required fields',
        validator=BusinessRulesValidator.validate_recommendation_integrity,
        error_message='Recommendation data integrity check failed',
        priority=80
    ))

    # Compliance Rules
    engine.register_rule(BusinessRule(
        name='validate_chat_compliance',
        rule_type=RuleType.COMPLIANCE_CHECK,
        description='Chat responses must comply with financial advisory standards',
        validator=BusinessRulesValidator.validate_chat_compliance,
        error_message='Response contains possibly non-compliant financial statements',
        priority=95
    ))

    return engine


class ComplianceChecker:
    """Checks financial advice for regulatory compliance."""

    COMPLIANCE_RULES = {
        'no_guaranteed_returns': {
            'pattern': 'guaranteed',
            'message': 'Never guarantee investment returns',
        },
        'include_disclaimer': {
            'pattern': 'investment advice',
            'requires': 'not investment advice',
            'message': 'Include appropriate disclaimers',
        },
        'no_false_claims': {
            'patterns': ['guaranteed', 'never lose', 'sure profit'],
            'message': 'Avoid false or misleading claims',
        },
    }

    @staticmethod
    def check_compliance(response: str) -> tuple[bool, List[str]]:
        """Check if response is compliant."""
        warnings = []
        response_lower = response.lower()

        # Check for guaranteed returns
        if 'guaranteed' in response_lower and 'return' in response_lower:
            warnings.append("❌ Avoid guaranteeing returns")

        # Check for false claims
        dangerous_phrases = ['never lose', 'sure profit', 'certain gain']
        for phrase in dangerous_phrases:
            if phrase in response_lower:
                warnings.append(f"❌ Remove phrase: '{phrase}'")

        # Check for investment advice disclaimer
        if 'investment' in response_lower and 'disclose' not in response_lower:
            warnings.append("⚠️ Consider adding investment advice disclaimer")

        return len(warnings) == 0, warnings

    @staticmethod
    def add_disclaimer(response: str) -> str:
        """Add compliance disclaimer to response."""
        if 'investment' in response.lower():
            disclaimer = "\n\n*Disclaimer: This is not investment advice. Please consult with a certified financial advisor.*"
            return response + disclaimer

        return response
