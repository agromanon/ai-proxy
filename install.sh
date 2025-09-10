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

# Check Python version using pure Python (more reliable)
echo "Checking Python version..."
PYTHON_VERSION_OUTPUT=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")' 2>/dev/null)
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)' 2>/dev/null)
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)' 2>/dev/null)

# Check if version is 3.8 or higher
if [[ $PYTHON_MAJOR -lt 3 ]] || [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -lt 8 ]]; then
    echo "Error: Python 3.8 or higher is required"
    echo "Current version: $PYTHON_VERSION_OUTPUT"
    exit 1
fi

echo "Python version: $PYTHON_VERSION_OUTPUT - OK"

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

# Create data directory
mkdir -p data

# Create default database if it doesn't exist
if [ ! -f "data/app.db" ]; then
    echo "Creating default database..."
    python3 -c "
import sqlite3
import json

# Create database connection
conn = sqlite3.connect('data/app.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
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

cursor.execute('''
    CREATE TABLE IF NOT EXISTS providers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        api_endpoint TEXT NOT NULL,
        api_key TEXT NOT NULL,
        default_model TEXT,
        auth_method TEXT DEFAULT 'bearer_token',
        is_active BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        api_standard TEXT DEFAULT 'openai',
        supported_models TEXT,
        model_mapping TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS provider_headers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider_id INTEGER NOT NULL,
        header_key TEXT NOT NULL,
        header_value TEXT NOT NULL,
        FOREIGN KEY (provider_id) REFERENCES providers (id) ON DELETE CASCADE
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS prompt_config (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        use_custom_prompt BOOLEAN DEFAULT FALSE,
        prompt_template TEXT,
        system_name TEXT,
        model_name_override TEXT,
        remove_ai_references BOOLEAN DEFAULT FALSE,
        remove_defensive_restrictions BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_admin BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS api_keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        user_id INTEGER,
        name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_token TEXT UNIQUE NOT NULL,
        user_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        ip_address TEXT,
        user_agent TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS request_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id TEXT NOT NULL,
        provider_name TEXT,
        model_used TEXT,
        request_data TEXT,
        response_data TEXT,
        status_code INTEGER,
        duration_ms INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Create default records
# Default app settings
cursor.execute('SELECT COUNT(*) FROM app_settings WHERE id = 1')
if cursor.fetchone()[0] == 0:
    cursor.execute('''
        INSERT INTO app_settings 
        (server_port, server_host, enable_full_logging, log_directory, 
         enable_streaming, request_timeout, require_auth, secret_key,
         rate_limit_enabled, rate_limit_requests, rate_limit_window)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (8000, '127.0.0.1', True, 'logs', True, 300, True, 'dev-secret-key', True, 100, 3600))

# Default prompt config
cursor.execute('SELECT COUNT(*) FROM prompt_config WHERE id = 1')
if cursor.fetchone()[0] == 0:
    cursor.execute('''
        INSERT INTO prompt_config 
        (use_custom_prompt, system_name, remove_ai_references, 
         remove_defensive_restrictions)
        VALUES (?, ?, ?, ?)
    ''', (False, 'AI Assistant', False, False))

conn.commit()
conn.close()
"
fi

# Initialize database with default providers
echo "Initializing database with default providers..."
python3 initialize_database.py

echo "Installation completed successfully!"
echo ""
echo "To start the AI Proxy:"
echo "  ./start.sh"
echo ""
echo "Access the web interface at: http://localhost:8000"
echo "Default login: admin / admin123"
echo "IMPORTANT: Change the default password after first login!"