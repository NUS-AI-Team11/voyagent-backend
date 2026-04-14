#!/bin/bash
# VoyageAgent project initialization script

echo "============================================================"
echo "      VoyageAgent - Intelligent Travel Planning System      "
echo "============================================================"
echo ""

# Check Python version
echo "Checking Python environment..."
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Found Python $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists, skipping."
else
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "Virtual environment activated."

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "pip upgraded."

# Install dependencies
echo ""
echo "Installing project dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo "Dependencies installed."

# Configure environment variables
echo ""
echo "Configuring environment variables..."
if [ -f ".env" ]; then
    echo ".env file already exists, skipping."
else
    cp .env.example .env
    echo ".env file created."
    echo "   Please edit .env and add your API keys."
fi

# Run framework tests
echo ""
echo "Running framework integrity tests..."
python test_framework.py

echo ""
echo "============================================================"
echo "                   Initialization complete!                 "
echo "============================================================"
echo ""
echo "Next steps:"
echo "   1. Edit .env and configure your API keys"
echo "   2. Run tests: pytest tests/ -v"
echo "   3. Start the app: python main.py"
echo ""
echo "Learn more:"
echo "   - Architecture: docs/architecture.md"
echo "   - Project docs: README.md"
echo "   - Framework report: FRAMEWORK_REPORT.md"
echo ""
echo "Happy coding!"
