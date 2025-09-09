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
        print("Virtual environment created successfully")
        return True
    except Exception as e:
        print(f"Error creating virtual environment: {e}")
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
        print("Dependencies installed successfully")
        return True
    except Exception as e:
        print(f"Error installing dependencies: {e}")
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
    
    print("Default configuration created")

def create_startup_script():
    """Create platform-specific startup scripts"""
    print("Creating startup scripts...")
    
    if platform.system() == "Windows":
        # Create Windows batch file
        startup_content = """@echo off
echo Starting AI Proxy...
call venv\\Scripts\\activate
python app.py
pause
"""
        with open("start.bat", "w") as f:
            f.write(startup_content)
            
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
    
    print("Startup scripts created")

def main():
    """Main installation function"""
    print("AI Proxy Installation Script")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create default configuration
    create_default_config()
    
    # Create startup scripts
    create_startup_script()
    
    print("\nInstallation completed successfully!")
    print("\nNext steps:")
    print("1. Edit the configuration through the web interface after starting the proxy")
    print("2. Run the proxy using:")
    if platform.system() == "Windows":
        print("   start.bat")
    else:
        print("   ./start.sh")
    print("\nAccess the web interface at: http://localhost:8000")
    print("Default login: admin / admin123")
    print("IMPORTANT: Change the default password after first login!")

if __name__ == "__main__":
    main()