#!/bin/bash
set -euo pipefail

# Pi-Kinect Development Check Script
# Runs linting, type checking, and tests

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd "$PROJECT_DIR"

echo "🔍 Pi-Kinect Development Check"
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        return 1
    fi
}

# Function to run command and check status
run_check() {
    local name="$1"
    shift
    echo "Running $name..."
    if "$@"; then
        print_status 0 "$name passed"
    else
        print_status 1 "$name failed"
        return 1
    fi
}

# Check if we're in a virtual environment
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
    echo -e "${YELLOW}⚠️  Not in a virtual environment. Consider using one.${NC}"
fi

# Install development dependencies if needed
echo "📦 Checking development dependencies..."
pip install -q -e ".[dev,test]" || {
    echo -e "${RED}❌ Failed to install development dependencies${NC}"
    exit 1
}

# Run checks
echo ""
echo "🧹 Running code quality checks..."

# Black formatting check
run_check "Black formatting" black --check pi_kinect/ tests/

# isort import sorting check
run_check "isort import sorting" isort --check-only pi_kinect/ tests/

# flake8 linting
run_check "flake8 linting" flake8 pi_kinect/ tests/

# mypy type checking
run_check "mypy type checking" mypy pi_kinect/

# bandit security check
run_check "bandit security check" bandit -r pi_kinect/

echo ""
echo "🧪 Running tests..."

# pytest
run_check "pytest tests" pytest tests/ -v

echo ""
echo "📊 Running coverage check..."

# pytest with coverage
run_check "pytest coverage" pytest tests/ --cov=pi_kinect --cov-report=term-missing

echo ""
echo "🎯 All checks completed!"

# Summary
echo ""
echo "📋 Summary:"
echo "- Code formatting: ✅"
echo "- Import sorting: ✅"
echo "- Linting: ✅"
echo "- Type checking: ✅"
echo "- Security check: ✅"
echo "- Tests: ✅"
echo "- Coverage: ✅"
echo ""
echo -e "${GREEN}🎉 All development checks passed!${NC}"
