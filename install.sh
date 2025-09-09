#!/bin/bash

# AI Proxy Installation Script
# This script installs and configures the AI Proxy with minimal user interaction

set -e  # Exit on any error

echo "AI Proxy Installation Script"
echo "=========================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher and add it to your PATH"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if (( $(echo "$PYTHON_VERSION < 3.8" | bc -l) )); then
    echo "Error: Python 3.8 or higher is required"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

echo "Python version: $PYTHON_VERSION - OK"

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    
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

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    # Create requirements.txt if it doesn't exist
    cat > requirements.txt << 'EOF'
flask==3.1.1
requests==2.32.4
bcrypt==4.1.2
EOF
    pip install -r requirements.txt
fi

# Create default configuration files
echo "Creating default configuration..."
touch .env

# Create logs directory
mkdir -p logs

# Create database directory
mkdir -p data

# Create default database if it doesn't exist
if [ ! -f "data/app.db" ]; then
    echo "Creating default database..."
    python3 -c "
import sqlite3
conn = sqlite3.connect('data/app.db')
conn.execute('''
    CREATE TABLE IF NOT EXISTS app_settings (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        server_port INTEGER DEFAULT 8000,
        server_host TEXT DEFAULT '127.0.0.1',
        enable_full_logging BOOLEAN DEFAULT TRUE,
        log_directory TEXT DEFAULT 'logs',
        enable_streaming BOOLEAN DEFAULT TRUE,
        request_timeout INTEGER DEFAULT 300,
        require_auth BOOLEAN DEFAULT TRUE,
        secret_key TEXT,
        session_cookie_secure BOOLEAN DEFAULT FALSE,
        rate_limit_enabled BOOLEAN DEFAULT TRUE,
        rate_limit_requests INTEGER DEFAULT 100,
        rate_limit_window INTEGER DEFAULT 3600,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.execute('''
    INSERT OR IGNORE INTO app_settings 
    (server_port, server_host, enable_full_logging, log_directory, 
     enable_streaming, request_timeout, require_auth, secret_key,
     rate_limit_enabled, rate_limit_requests, rate_limit_window)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (8000, '127.0.0.1', True, 'logs', True, 300, True, 'dev-secret-key', True, 100, 3600))
conn.commit()
conn.close()
"

echo "Installation completed successfully!"
echo ""
echo "To start the AI Proxy:"
echo "  ./start.sh"
echo ""
echo "Access the web interface at: http://localhost:8000"
echo "Default login: admin / admin123"
echo "IMPORTANT: Change the default password after first login!"