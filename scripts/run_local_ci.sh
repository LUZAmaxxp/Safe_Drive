#!/bin/bash
# Local CI Runner Script
# Run this script to perform CI checks locally before pushing

set -e

echo "================================================"
echo "Safe_Drive Local CI Check"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo "Checking Python syntax..."
if python3 --version 2>/dev/null; then
    PYTHON_CMD="python3"
elif python --version 2>/dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}✗ Python not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Found Python: $($PYTHON_CMD --version)${NC}"

# Check Python syntax
echo ""
echo "Checking Python syntax in all .py files..."
for file in *.py; do
    if [ -f "$file" ]; then
        if $PYTHON_CMD -m py_compile "$file" 2>/dev/null; then
            echo -e "${GREEN}✓ $file${NC}"
        else
            echo -e "${RED}✗ $file has syntax errors${NC}"
        fi
    fi
done

# Check if requirements.txt exists
if [ -f requirements.txt ]; then
    echo ""
    echo "Requirements.txt found:"
    echo "  - To install: pip install -r requirements.txt"
else
    echo -e "${YELLOW}⚠ requirements.txt not found${NC}"
fi

# Check Node.js and frontend
echo ""
echo "Checking frontend..."
if command -v node &> /dev/null; then
    echo -e "${GREEN}✓ Node.js version: $(node --version)${NC}"
    
    if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
        echo ""
        echo "Frontend directory found"
        echo "  - To install: cd frontend && npm install"
        echo "  - To build: cd frontend && npm run build"
    else
        echo -e "${RED}✗ Frontend directory or package.json not found${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Node.js not found (frontend checks skipped)${NC}"
fi

# Check for tests
echo ""
echo "Checking tests..."
if [ -f "tests/test_app.py" ]; then
    echo -e "${GREEN}✓ Test file found: tests/test_app.py${NC}"
    echo "  - To run tests: $PYTHON_CMD -m unittest tests.test_app -v"
else
    echo -e "${YELLOW}⚠ Test file not found${NC}"
fi

# Summary
echo ""
echo "================================================"
echo "Local CI Check Complete"
echo "================================================"
echo ""
echo "To run full tests:"
echo "  1. Install Python dependencies: pip install -r requirements.txt"
echo "  2. Run tests: python -m unittest tests.test_app -v"
echo ""
echo "To build frontend:"
echo "  1. cd frontend"
echo "  2. npm install"
echo "  3. npm run build"
echo ""

