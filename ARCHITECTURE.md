# Personal Finance Advisor Agent - Technical Architecture

## System Overview

The Personal Finance Advisor Agent is built using a modular, skill-based architecture where specialized components handle distinct responsibilities. The system follows the producer-consumer pattern with clear data flows.

## Component Breakdown

### 1. Data Layer: ExpenseDataManager

**Purpose**: Manages sample expense data and provides data access abstractions

**Class Definition**:
```python
class ExpenseDataManager:
    BENCHMARKS: Dict[str, float]          # Industry standards
    HIGH_SPENDING_THRESHOLD: float = 0.30 # 30% of income
    TARGET_SAVINGS_PERCENTAGE: float = 0.20 # 20% target
    
    @staticmethod
    get_sample_customer_data() -> Dict
    
    @staticmethod
    get_multiple_months_data() -> pd.DataFrame
```

**Methods**:

| Method | Input | Output | Purpose |
|--------|-------|--------|---------|
| `get_sample_customer_data()` | None | `{customer_id, name, monthly_income, expenses: {category: amount}}` | Returns sample customer profile with realistic expenses |
| `get_multiple_months_data()` | None | `DataFrame[Month, Total_Expenses, Savings, Savings_Percentage]` | Generates 12-month trend data for visualization |

**Key Benchmarks**:
```python
Rent: 30%        # Housing cost cap
Food: 15%        # Daily necessities target
Utilities: 8%    # Basic utilities
Transportation: 10%  # Travel & vehicles
Entertainment: 7%    # Discretionary spending
Shopping: 10%    # Non-essential purchases
EMI: 15%         # Debt service ratio
```

**Data Format**:
```python
{
    'customer_id': 'CUST_001',
    'name': 'John Doe',
    'monthly_income': 100000,
    'expenses': {
        'Rent': 28000,
        'Food': 12000,
        'Utilities': 3500,
        'Travel': 8000,
        'EMI': 15000,
        'Shopping': 12000,
        'Entertainment': 6000,
    },
    'tracking_period': 'July 2024 - July 2025'
}
```

---

### 2. Analysis Engine: ExpenseAnalysisEngine

**Purpose**: Analyzes expense patterns and calculates key financial metrics

**Class Definition**:
```python
class ExpenseAnalysisEngine:
    monthly_income: float
    expenses: Dict[str, float]
    total_expenses: float
    net_savings: float
    savings_percentage: float
```

**Constructor**:
```python
def __init__(self, monthly_income: float, expenses: Dict[str, float])
```

**Public Methods**:

#### `get_dashboard_metrics() -> Dict[str, float]`
Returns four key metrics for dashboard display.

**Contract**:
```python
Input: None (uses self.* attributes)
Output: {
    'monthly_income': float,
    'total_expenses': float,
    'net_savings': float,
    'savings_percentage': float,
}
Example Output:
{
    'monthly_income': 100000,
    'total_expenses': 84000,
    'net_savings': 16000,
    'savings_percentage': 16.0,
}
```

#### `get_category_percentages() -> Dict[str, float]`
Calculates each category as percentage of income.

**Contract**:
```python
Input: None
Output: {category: percentage_of_income}
Example Output:
{
    'Rent': 28.0,        # $28k / $100k = 28%
    'Food': 12.0,        # $12k / $100k = 12%
    'EMI': 15.0,
    ...
}
```

#### `get_top_spending_categories(top_n: int = 3) -> List[Tuple[str, float]]`
Returns highest spending categories ranked.

**Contract**:
```python
Input: top_n = 3 (default)
Output: [(category, amount), ...] sorted descending by amount
Example Output:
[
    ('Rent', 28000),
    ('EMI', 15000),
    ('Shopping', 12000),
]
```

#### `identify_high_spending_categories() -> List[Tuple[str, float, float]]`
Flags categories exceeding 30% of income.

**Contract**:
```python
Input: None
Output: [(category, amount, percentage), ...] sorted by percentage descending
Example Output:
[]  # Empty if no categories > 30%

Or (if rent was $35k):
[
    ('Rent', 35000, 35.0),
]
```

#### `get_benchmark_comparison() -> Dict[str, Dict[str, float]]`
Compares user spending against industry benchmarks.

**Contract**:
```python
Input: None
Output: {
    category: {
        'user_spending': float,      # % of income
        'benchmark': float,           # % of income
        'difference': float,           # user - benchmark
        'status': 'OVER' | 'UNDER'
    },
    ...
}
Example Output:
{
    'Rent': {
        'user_spending': 28.0,
        'benchmark': 30.0,
        'difference': -2.0,
        'status': 'UNDER'
    },
    'Food': {
        'user_spending': 12.0,
        'benchmark': 15.0,
        'difference': -3.0,
        'status': 'UNDER'
    },
}
```

#### `calculate_potential_savings() -> Dict[str, float]`
Estimates 10% reduction from high-spending categories.

**Contract**:
```python
Input: None
Output: {category: savings_amount}
Example Output:
{
    'Rent': 2800,        # $28k * 0.10
    'EMI': 1500,         # $15k * 0.10
}
```

---

### 3. Recommendation Engine: RecommendationEngine

**Purpose**: Generates prioritized, actionable recommendations

**Class Definition**:
```python
class RecommendationEngine:
    engine: ExpenseAnalysisEngine           # Reference to analysis engine
    recommendations: List[Dict[str, str]]   # Cache of generated recommendations
```

**Constructor**:
```python
def __init__(self, analysis_engine: ExpenseAnalysisEngine)
    # Stores reference, initializes empty recommendations
```

**Public Methods**:

#### `generate_recommendations() -> List[Dict]`
Main method to generate all prioritized recommendations.

**Business Logic**:
1. **High-Spending Detection**: Categories > 30% of income
   - Priority: HIGH
   - Action: Reduce by 10%
   - Savings: Category_Amount * 0.10

2. **Benchmark Alignment**: Categories > benchmark + 2%
   - Priority: MEDIUM
   - Action: Align to benchmark
   - Savings: Category_Amount - (Benchmark_% × Income)

3. **Savings Target Gap**: Current rate < 20%
   - Priority: MEDIUM
   - Action: Reduce expenses
   - Savings: (20% × Income) - Current_Savings

**Output Contract**:
```python
Output: [
    {
        'priority': 'HIGH' | 'MEDIUM' | 'LOW',
        'category': str,
        'type': 'reduce_high_spending' | 'align_to_benchmark' | 'increase_savings_target',
        'title': str,
        'description': str,
        'potential_savings': float,
        'action': str,
    },
    ...
]
# Sorted by potential_savings descending
```

**Example Output**:
```python
[
    {
        'priority': 'MEDIUM',
        'category': 'Overall_Savings',
        'type': 'increase_savings_target',
        'title': 'Increase Savings Target to 20%',
        'description': 'Current savings rate is 16.0%. Target 20% savings...',
        'potential_savings': 4000.0,
        'action': 'Implement cost reduction across multiple categories',
    },
    {
        'priority': 'MEDIUM',
        'category': 'Rent',
        'type': 'align_to_benchmark',
        'title': 'Align Rent to Industry Benchmark',
        'description': 'Industry benchmark suggests 30.0% of income for Rent...',
        'potential_savings': 0.0,  # Already aligned
        'action': 'Monitor Rent spending',
    },
]
```

---

### 4. Chatbot Interface: ChatbotResponder

**Purpose**: Process natural language queries and generate contextual responses

**Class Definition**:
```python
class ChatbotResponder:
    engine: ExpenseAnalysisEngine
    recommendations: List[Dict]
    
    def respond_to_query(query: str) -> str
```

**Constructor**:
```python
def __init__(self, analysis_engine: ExpenseAnalysisEngine, recommendations: List[Dict])
```

**Intent Classification**:

| Intent | Keywords | Handler Method | Example Query |
|--------|----------|-----------------|----------------|
| **GREETING** | hello, hi, hey | `_handle_greeting()` | "Hi there!" |
| **SAVINGS_HOW** | save, how, can | `_handle_how_to_save()` | "How can I save more?" |
| **SAVINGS_PCT** | savings, percentage, rate | `_handle_savings_percentage()` | "What is my saving percentage?" |
| **HIGH_SPENDING** | spending, where, which | `_handle_high_spending()` | "Where am I spending too much?" |
| **CATEGORY_SPECIFIC** | [category name] | `_handle_category_query()` | "How can I reduce my rent?" |
| **INCOME** | income | `_handle_income_query()` | "What is my income?" |
| **RECOMMENDATIONS** | recommend, suggestion | `_handle_recommendations_query()` | "What should I do?" |

**Response Contract**:
```python
Input: user_query: str (any natural language)
Output: response: str (formatted markdown with metrics and suggestions)
Behavior:
    1. Classify intent using keyword matching
    2. Retrieve relevant data from analysis_engine
    3. Format response with specific numbers and actions
    4. Return markdown-formatted string for Streamlit rendering
```

**Example Interactions**:

**Query 1**: "How can I save more?"
```
Response:
"**Top Opportunities to Save More:**

1. **Increase Savings Target to 20%**
   Potential monthly savings: $4,000.00
   Action: Implement cost reduction across multiple categories

2. **Optimize Entertainment Spending**
   Potential monthly savings: $600.00
   Action: Reduce discretionary entertainment expenses"
```

**Query 2**: "What is my saving percentage?"
```
Response:
"Your current savings rate is 16.0%. 
The recommended target is 20.0%.

To reach your target:
- Increase monthly savings by: $4,000.00
- Reduce monthly expenses by: $4,000.00

This is achievable through strategic spending reductions across high-spending categories."
```

---

### 5. UI Layer: Streamlit Components

**Purpose**: Render data visualizations and handle user interactions

**Key Functions**:

#### `initialize_session_state()`
Initializes Streamlit session state for data persistence across reruns.

```python
Initializes:
  st.session_state.chat_history = []
  st.session_state.analysis_engine = ExpenseAnalysisEngine(...)
  st.session_state.recommendation_engine = RecommendationEngine(...)
```

#### `render_metrics_dashboard()`
Displays four key metrics in cards.

```python
Renders:
  - Monthly Income: $100,000
  - Total Expenses: $84,000 (84.0% of income)
  - Net Savings: $16,000 (+16.0%)
  - Savings Rate: 16.0% (Target: 20%)
```

#### `render_expense_pie_chart()`
Visualization: Pie chart of expense breakdown.

```python
Chart Type: Plotly Pie Chart
Data: {category: amount}
Colors: Default Plotly palette
Interaction: Hover shows amount and percentage
```

#### `render_spending_bar_chart()`
Visualization: Bar chart comparing user spending vs benchmarks.

```python
Chart Type: Plotly Grouped Bar Chart
Data: 
  - Your Spending (by category)
  - Industry Benchmark (by category)
Grouping: side-by-side comparison
Colors: steelblue (user), lightgray (benchmark)
```

#### `render_savings_trend_chart()`
Visualization: Line chart of 12-month savings trend.

```python
Chart Type: Plotly Line + Markers
Data: Savings percentage by month
Reference Lines: 20% target (dashed orange)
Interaction: Hover shows month and percentage
```

#### `render_high_spending_analysis()`
Conditional display of high-spending alerts.

```python
Logic:
  If categories > 30% threshold:
    - Display warning box
    - List categories with amounts and percentages
    - Show potential savings by category
  Else:
    - Display success message
```

#### `render_recommendations()`
Display prioritized recommendations in expandable sections.

```python
Structure:
  For each recommendation:
    - Expandable section with priority color indicator
    - Title + monthly savings amount
    - Full details on expand:
      - Priority level
      - Category
      - Description
      - Annual savings potential
      - Recommended action
```

#### `render_chatbot()`
Interactive chat interface.

```python
Components:
  - Chat history display (alternating user/assistant)
  - Text input field at bottom
  - Auto-scroll to latest message
  - Session state persistence
```

## Data Flow Diagram

```
User Input (Dashboard View)
    ↓
[Streamlit UI] → Calls render_metrics_dashboard()
    ↓
Queries st.session_state.analysis_engine
    ↓
ExpenseAnalysisEngine.get_dashboard_metrics()
    ↓
Returns {income, expenses, savings, rate}
    ↓
[UI Renders] Metric cards
    ↓
User navigates to Analysis tab
    ↓
[Streamlit UI] → Calls render_high_spending_analysis()
    ↓
Queries ExpenseAnalysisEngine.identify_high_spending_categories()
    ↓
Queries RecommendationEngine.generate_recommendations()
    ↓
[UI Renders] Alerts + Recommendations
    ↓
User types chat query
    ↓
[Streamlit UI] → Calls ChatbotResponder.respond_to_query()
    ↓
Intent classification + data retrieval
    ↓
[UI Renders] Chat response
```

## State Management

### Session State

```python
st.session_state:
  - chat_history: List[{role: str, content: str}]
    Stores all chat messages for history display
    Persisted across reruns
    Cleared on session reset
    
  - analysis_engine: ExpenseAnalysisEngine
    Stores computed analysis for current session
    Persisted across reruns
    Recreated only if data changes
    
  - recommendation_engine: RecommendationEngine
    Stores recommendation logic & cache
    Persisted across reruns
    Regenerated on each tab access (stateless)
```

### Process Flow

```
Session Start
    ↓
initialize_session_state()
    ↓
Load sample data: ExpenseDataManager.get_sample_customer_data()
    ↓
Create analysis_engine: ExpenseAnalysisEngine(income, expenses)
    ↓
Store in session_state
    ↓
Streamlit renders UI based on selected tab
    ↓
On user interaction:
    - Dashboard: Render metrics + charts
    - Analysis: Render high-spending + recommendations
    - Chatbot: Process message → respond → st.rerun()
    ↓
On st.rerun():
    - Check session_state for existing objects
    - Reuse if available (skip re-initialization)
    - Update only affected components
```

## Scalability Considerations

### Current Limitations (Single Streamlit Instance)

```
Maximum concurrent users: 10-20
Session state memory: ~2MB per user
Bottleneck: Server-side session storage
Solution: Implement caching layer for production
```

### Recommended Production Architecture

```
For 1,000+ concurrent users:
  1. Deploy on container orchestration (K8s)
  2. Multiple Streamlit instances behind load balancer
  3. Shared Redis cache for analysis results
  4. Stateless design (session data in cache, not memory)
  5. Database for long-term data storage
```

## API Contract Examples

### Expense Analysis

```
POST /api/analyze
{
  "income": 100000,
  "expenses": {
    "Rent": 28000,
    "Food": 12000,
    ...
  }
}

Response 200:
{
  "metrics": {
    "monthly_income": 100000,
    "total_expenses": 84000,
    "net_savings": 16000,
    "savings_percentage": 16.0
  },
  "high_spending": [],
  "top_categories": [...]
}
```

### Generate Recommendations

```
POST /api/recommendations
{
  "analysis": {...metrics from above...}
}

Response 200:
{
  "recommendations": [
    {
      "priority": "MEDIUM",
      "title": "Increase Savings Target to 20%",
      "potential_savings": 4000,
      "action": "Reduce expenses across categories"
    },
    ...
  ]
}
```

### Chat Query

```
POST /api/chat
{
  "query": "How can I save more?",
  "context": {
    "income": 100000,
    "expenses": {...}
  }
}

Response 200:
{
  "intent": "savings_improvement",
  "response": "**Top Opportunities to Save More:**\n1. ...",
  "confidence": 0.95
}
```

## Error Handling

### Input Validation

```python
Errors caught:
  - Negative income/expenses
  - Extremely large numbers (>$100M)
  - Missing required categories
  - Non-numeric values
  - Empty input

Response: ValueError with descriptive message
Display: st.error() in UI
```

### Graceful Degradation

```python
If analysis fails:
  - Return cached results (if available)
  - Display warning to user
  - Fall back to defaults
  - Log error for debugging

If recommendation generation fails:
  - Return generic recommendations
  - Display info message
  - Do not crash app
```

---

## Testing Guide

### Unit Tests (Manual)

```python
# Test 1: Metric Calculation
income = 100000
expenses = {'Rent': 28000, 'Food': 12000, 'EMI': 15000}
engine = ExpenseAnalysisEngine(income, {**expenses, **{'others': 29000}})
assert engine.net_savings == 16000
assert engine.savings_percentage == 16.0

# Test 2: High Spending Detection
# Rent > 30% should be flagged
expenses['Rent'] = 35000
engine = ExpenseAnalysisEngine(income, expenses)
high_spending = engine.identify_high_spending_categories()
assert len(high_spending) == 1
assert high_spending[0][0] == 'Rent'

# Test 3: Recommendation Generation
recommender = RecommendationEngine(engine)
recs = recommender.generate_recommendations()
assert len(recs) > 0
assert all('potential_savings' in r for r in recs)
```

### Integration Tests

```python
# Test full flow: Data → Analysis → Recommendations → Chat

# 1. Load data
data = ExpenseDataManager.get_sample_customer_data()

# 2. Create analysis
engine = ExpenseAnalysisEngine(data['monthly_income'], data['expenses'])
metrics = engine.get_dashboard_metrics()
assert metrics['monthly_income'] == 100000

# 3. Generate recommendations
recommender = RecommendationEngine(engine)
recs = recommender.generate_recommendations()
assert len(recs) >= 1

# 4. Chat interaction
responder = ChatbotResponder(engine, recs)
response = responder.respond_to_query("How can I save more?")
assert len(response) > 0
assert "$" in response  # Should contain monetary amounts
```

---

## Configuration & Customization

### Benchmark Customization

Edit `ExpenseDataManager.BENCHMARKS`:
```python
BENCHMARKS = {
    'Rent': 0.30,           # Change to 0.25 for stricter requirement
    'Food': 0.15,           # Adjust based on region/income level
    # ...
}
```

### Recommendation Thresholds

Edit `ExpenseAnalysisEngine`:
```python
HIGH_SPENDING_THRESHOLD = 0.30      # Change high-spending flag
REDUCTION_TARGET = 0.10             # Change reduction percentage (currently 10%)
TARGET_SAVINGS_PERCENTAGE = 0.20    # Change savings goal (currently 20%)
```

### Sample Data

Edit `ExpenseDataManager.get_sample_customer_data()`:
```python
# Modify to test different scenarios
# Example 1: High income, low savings
# Example 2: High expenses, all categories
# Move to database for multi-user support
```

---

## Deployment Checklist

- [ ] Python 3.9+ environment configured
- [ ] All dependencies installed via `pip install -r requirements.txt`
- [ ] `streamlit run app.py` executes without errors
- [ ] All three tabs (Dashboard, Analysis, Chatbot) render correctly
- [ ] Sample data loads on first run
- [ ] Chat history persists across tab switches
- [ ] Recommendations generate within 100ms
- [ ] No console errors or warnings
- [ ] Metrics calculations validated for accuracy
- [ ] UI responsive on mobile/tablet devices

---

## Future Enhancements

```
Phase 1 (Current): Rule-based recommendations
Phase 2: Real banking data integration (Plaid API)
Phase 3: Investment recommendations engine
Phase 4: Machine learning personalization
Phase 5: Multi-user support with persistent data
Phase 6: Mobile app release
Phase 7: Regional expansion with localization
```

---

**Version**: 1.0.0  
**Last Updated**: July 2024
