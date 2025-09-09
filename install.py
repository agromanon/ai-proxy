#!/usr/bin/env python3
"""
AI Proxy Installation Script
"""

import os
import sys
import subprocess
import platform
import venv
from pathlib import Path

def check_python_version():
    """Check if Python 3.8+ is installed"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    return True

def create_virtual_environment():
    """Create virtual environment"""
    print("Creating virtual environment...")
    try:
        venv.create("venv", with_pip=True)
        print("✅ Virtual environment created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating virtual environment: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        # Determine the path to pip in the virtual environment
        if platform.system() == "Windows":
            pip_path = os.path.join("venv", "Scripts", "pip.exe")
        else:
            pip_path = os.path.join("venv", "bin", "pip")
        
        # Install requirements
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_default_config():
    """Create default configuration files"""
    print("Creating default configuration...")
    
    # Create .env file
    env_content = """# AI Proxy Configuration

# Server Settings
SERVER_PORT=8000
SERVER_HOST=127.0.0.1

# Security Settings
SECRET_KEY=your-secret-key-change-in-production
SESSION_COOKIE_SECURE=false
RATE_LIMIT_ENABLED=true

# Database Settings
DATABASE_PATH=app.db

# Default Admin User
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# Logging
ENABLE_FULL_LOGGING=true
LOG_DIRECTORY=logs
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    print("✅ Default configuration created")

def create_startup_script():
    """Create platform-specific startup scripts"""
    print("Creating startup scripts...")
    
    if platform.system() == "Windows":
        # Create Windows batch file
        startup_content = """@echo off
echo Starting AI Proxy...
call venv\Scripts\activate
python app.py
pause
"""
        with open("start.bat", "w") as f:
            f.write(startup_content)
        
        # Create Windows service installation (optional)
        service_content = """@echo off
echo Installing AI Proxy as Windows service...
echo This requires additional setup with NSSM or similar tool
pause
"""
        with open("install-service.bat", "w") as f:
            f.write(service_content)
            
    else:
        # Create Unix shell script
        startup_content = """#!/bin/bash
echo "Starting AI Proxy..."
source venv/bin/activate
python app.py
"""
        with open("start.sh", "w") as f:
            f.write(startup_content)
        os.chmod("start.sh", 0o755)
        
        # Create service file for systemd (Linux)
        service_content = """#!/bin/bash
# AI Proxy Service Installation Script

echo "This script helps you install AI Proxy as a systemd service"
echo "Note: You may need to modify paths in the service file"

cat > ai-proxy.service << 'EOF'
[Unit]
Description=AI Proxy Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/path/to/ai-proxy
ExecStart=/path/to/ai-proxy/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "Service file created. To install:"
echo "1. Edit ai-proxy.service to set correct paths"
echo "2. sudo cp ai-proxy.service /etc/systemd/system/"
echo "3. sudo systemctl daemon-reload"
echo "4. sudo systemctl enable ai-proxy"
echo "5. sudo systemctl start ai-proxy"
"""
        with open("install-service.sh", "w") as f:
            f.write(service_content)
        os.chmod("install-service.sh", 0o755)
    
    print("✅ Startup scripts created")

def initialize_database():
    """Initialize database with default providers and settings"""
    print("Initializing database with default providers and settings...")
    
    try:
        # Activate virtual environment
        if platform.system() == "Windows":
            python_path = os.path.join("venv", "Scripts", "python.exe")
        else:
            python_path = os.path.join("venv", "bin", "python")
        
        # Run database initialization script
        subprocess.run([python_path, "initialize_database.py"], check=True)
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

def create_requirements_file():
    """Create requirements.txt file"""
    print("Creating requirements file...")
    
    requirements = """flask==3.1.1
requests==2.32.4
bcrypt==4.1.2
sqlite3
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements)
    
    print("✅ Requirements file created")

def main():
    """Main installation function"""
    print("AI Proxy Installation Script")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create requirements.txt if it doesn't exist
    if not os.path.exists("requirements.txt"):
        create_requirements_file()
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create default configuration
    create_default_config()
    
    # Initialize database
    if not initialize_database():
        sys.exit(1)
    
    # Create startup scripts
    create_startup_script()
    
    print("\n🎉 Installation completed successfully!")
    print("\n🚀 Next steps:")
    print("1. Edit the configuration through the web interface after starting the proxy")
    print("2. Run the proxy using:")
    if platform.system() == "Windows":
        print("   start.bat")
    else:
        print("   ./start.sh")
    print("\n🌐 Access the web interface at: http://localhost:8000")
    print("🔐 Default login: admin / admin123")
    print("⚠️  IMPORTANT: Change the default password after first login!")
    print("\n📋 Default providers included:")
    print("   • OpenRouter")
    print("   • Chutes (corrected endpoint)")
    print("   • Synthetic")
    print("   • AIML")
    print("   • Grok (Direct)")
    print("   • Grok (OpenAI)")

if __name__ == "__main__":
    main()