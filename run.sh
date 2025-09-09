#!/bin/bash

# AI Proxy Runner Script
# This script handles starting the AI Proxy with the correct environment

set -e

echo "🚀 Starting AI Proxy..."

# Check if we're on macOS with Homebrew
if [[ "$OSTYPE" == "darwin"* ]] && command -v brew &> /dev/null; then
    echo "🍎 Detected macOS with Homebrew"
    
    # Check if we're in a virtual environment
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        echo "🔄 Checking for virtual environment..."
        
        # Check if venv exists
        if [ -d "venv" ]; then
            echo "✅ Found virtual environment, activating..."
            source venv/bin/activate
        else
            echo "🔧 Creating virtual environment..."
            python3 -m venv venv
            source venv/bin/activate
            echo "📥 Installing dependencies..."
            pip install -e .
        fi
    else
        echo "✅ Already in virtual environment"
    fi
else
    # For other systems, check if we're in a virtual environment
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        echo "⚠️  Warning: Not in a virtual environment"
        echo "💡 Consider using a virtual environment for isolation"
    fi
fi

# Start the proxy
echo "🏃 Running AI Proxy..."
python app.py