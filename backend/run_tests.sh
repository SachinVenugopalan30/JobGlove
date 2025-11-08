#!/bin/bash

# JobGlove Backend Test Runner
# Provides easy access to different test modes

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}   JobGlove Backend Test Runner${NC}"
echo -e "${BLUE}============================================${NC}\n"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}pytest not found. Installing test dependencies...${NC}"
    pip install -r requirements.txt
fi

# Parse command line arguments
MODE="${1:-all}"

case "$MODE" in
    quick|simple)
        echo -e "${GREEN}Running quick tests (no pytest)...${NC}\n"
        python tests/simple_test.py
        ;;

    unit)
        echo -e "${GREEN}Running unit tests only...${NC}\n"
        pytest -m unit -v
        ;;

    integration)
        echo -e "${GREEN}Running integration tests only...${NC}\n"
        pytest -m integration -v
        ;;

    coverage)
        echo -e "${GREEN}Running tests with coverage report...${NC}\n"
        pytest --cov=. --cov-report=html --cov-report=term
        echo -e "\n${BLUE}Coverage report generated in htmlcov/index.html${NC}"
        ;;

    verbose)
        echo -e "${GREEN}Running all tests with verbose output...${NC}\n"
        pytest -v -s
        ;;

    watch)
        echo -e "${GREEN}Running tests in watch mode...${NC}\n"
        echo -e "${YELLOW}Watching for file changes... (Press Ctrl+C to stop)${NC}\n"
        pytest-watch
        ;;

    all|*)
        echo -e "${GREEN}Running full test suite...${NC}\n"
        pytest -v
        ;;
esac

EXIT_CODE=$?

echo -e "\n${BLUE}============================================${NC}"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Tests completed successfully${NC}"
else
    echo -e "${RED}✗ Tests failed (exit code: $EXIT_CODE)${NC}"
fi
echo -e "${BLUE}============================================${NC}\n"

exit $EXIT_CODE
