#!/usr/bin/env python3
"""
Demo script showing how to use the AI Proxy package
"""

import subprocess
import sys
import os
import time

def check_prerequisites():
    """Check if prerequisites are met"""
    print("Checking prerequisites...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print("✅ Python version OK")
    
    # Check if pip is available
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✅ pip is available")
    except subprocess.CalledProcessError:
        print("❌ pip is not available")
        return False
    
    return True

def install_package():
    """Install the AI Proxy package"""
    print("\nInstalling AI Proxy package...")
    
    try:
        # Install in development mode
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], 
                      check=True, capture_output=True)
        print("✅ AI Proxy package installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install package: {e}")
        return False

def start_proxy():
    """Start the AI Proxy server"""
    print("\nStarting AI Proxy server...")
    
    try:
        # Start the proxy in the background
        process = subprocess.Popen([sys.executable, "-m", "app"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        print("✅ AI Proxy server started")
        print("📝 Access the web interface at: http://localhost:8000")
        print("📝 Default login credentials will be displayed in the console")
        print("⚠️  Remember to change the default password after first login!")
        
        return process
    except Exception as e:
        print(f"❌ Failed to start proxy: {e}")
        return None

def main():
    """Main demo function"""
    print("AI Proxy Demo")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\nPlease install the required prerequisites and try again.")
        return
    
    # Install package
    if not install_package():
        print("\nFailed to install the package. Please check the error above.")
        return
    
    # Start proxy
    process = start_proxy()
    if not process:
        print("\nFailed to start the proxy server.")
        return
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Open your web browser and go to http://localhost:8000")
    print("2. Log in with the default credentials")
    print("3. Configure your AI providers through the web interface")
    print("4. Add API keys for the providers you want to use")
    print("5. Start using Claude Code with multiple providers!")
    
    print("\nPress Ctrl+C to stop the server")
    
    try:
        # Wait for the process to complete or be interrupted
        process.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping AI Proxy server...")
        process.terminate()
        process.wait()
        print("✅ Server stopped")

if __name__ == "__main__":
    main()