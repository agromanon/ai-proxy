#!/bin/bash

# AI Proxy Start Script
# This script starts the AI Proxy with proper configuration

set -e  # Exit on any error

echo "Starting AI Proxy..."

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Activating virtual environment..."
    
    # Check if venv exists
    if [ ! -d "venv" ]; then
        echo "Error: Virtual environment not found"
        echo "Please run install.sh first"
        exit 1
    fi
    
    # Activate virtual environment
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        # Windows
        source venv/Scripts/activate
    else
        # Unix/Linux/macOS
        source venv/bin/activate
    fi
else
    echo "Already in virtual environment"
fi

# Check if dependencies are installed
if ! python3 -c "import flask" &> /dev/null; then
    echo "Error: Dependencies not installed"
    echo "Please run install.sh first"
    exit 1
fi

# Start the proxy
echo "Starting AI Proxy server..."
echo "Access the web interface at: http://localhost:8000"
echo "Default login: admin / admin123"
echo "IMPORTANT: Change the default password after first login!"

python3 app.py