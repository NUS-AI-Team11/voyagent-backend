#!/bin/bash
# VoyageAgent project initialization script

set -euo pipefail

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

PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info[0])')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info[1])')
if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 13 ]; then
    echo "Warning: Python $PYTHON_VERSION detected."
    echo "This project is best tested on Python 3.11-3.12 for maximum dependency compatibility."
fi

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
pip install --upgrade pip
echo "pip upgraded."

# Install dependencies
echo ""
echo "Installing project dependencies..."
pip install -r requirements.txt
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

# Run tests
echo ""
echo "Running test suite..."
pytest tests/ -q

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
echo "   - Quick start: docs/QUICK_START.md"
echo ""
echo "Happy coding!"
