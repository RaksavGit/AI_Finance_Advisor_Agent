#!/bin/bash

echo "========================================"
echo "Personal Finance Advisor - Setup Verification"
echo "========================================"
echo ""

# Check Python version
echo "✓ Checking Python version..."
python --version || echo "✗ Python not found"

# Check if in correct directory
echo "✓ Checking directory structure..."
if [ -f "app.py" ] && [ -f "requirements.txt" ]; then
    echo "  Found: app.py, requirements.txt"
else
    echo "✗ Missing required files"
    exit 1
fi

# List all files
echo ""
echo "✓ Project files:"
ls -1 *.py *.txt *.md 2>/dev/null | sed 's/^/  /'

# Check dependencies
echo ""
echo "✓ Checking Python packages..."
python -c "import streamlit; print('  ✓ streamlit')" 2>/dev/null || echo "  ✗ streamlit not installed"
python -c "import pandas; print('  ✓ pandas')" 2>/dev/null || echo "  ✗ pandas not installed"
python -c "import numpy; print('  ✓ numpy')" 2>/dev/null || echo "  ✗ numpy not installed"
python -c "import plotly; print('  ✓ plotly')" 2>/dev/null || echo "  ✗ plotly not installed"
python -c "import matplotlib; print('  ✓ matplotlib')" 2>/dev/null || echo "  ✗ matplotlib not installed"

# Check syntax
echo ""
echo "✓ Checking Python syntax..."
python -m py_compile app.py && echo "  ✓ app.py syntax valid" || echo "  ✗ Syntax error in app.py"

# Count lines
echo ""
echo "✓ Project statistics:"
wc -l app.py | awk '{print "  app.py: " $1 " lines"}'
wc -l README.md | awk '{print "  README.md: " $1 " lines"}'
wc -l ARCHITECTURE.md 2>/dev/null | awk '{print "  ARCHITECTURE.md: " $1 " lines"}'

echo ""
echo "========================================"
echo "✓ Setup verification complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Install dependencies: pip install -r requirements.txt"
echo "2. Run the app: streamlit run app.py"
echo "3. Open: http://localhost:8501"
echo ""
