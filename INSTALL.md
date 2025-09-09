# AI Proxy Installation Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Installation](#quick-installation)
3. [Manual Installation](#manual-installation)
4. [Homebrew/macOS Installation](#homebrewmacos-installation)
5. [Platform-Specific Instructions](#platform-specific-instructions)
6. [First-Time Setup](#first-time-setup)
7. [Usage](#usage)
8. [Updating](#updating)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

- **Python 3.8 or higher** (Python 3.10+ recommended)
- **Git** (recommended for getting the latest version)
- **At least 50MB free disk space**

## Quick Installation

For most users, the one-command installation is the simplest approach:

```bash
curl -sSL https://raw.githubusercontent.com/agromanon/ai-proxy/master/install.sh | bash
```

This will:
1. Clone the repository
2. Create a virtual environment
3. Install all dependencies
4. Create default configuration files
5. Start the proxy server

## Manual Installation

If you prefer to install manually:

```bash
# Clone the repository
git clone https://github.com/agromanon/ai-proxy.git
cd ai-proxy

# Run the installation script
./install.sh

# Start the proxy
./start.sh
```

## Homebrew/macOS Installation

### PEP 668 Externally Managed Environment Issue

If you're using Homebrew on macOS, you may encounter this error:
```
error: externally-managed-environment
× This environment is externally managed
```

This occurs because Homebrew manages Python packages globally and prevents global installations to avoid conflicts.

### Solution: Use the Smart Installation Script

The AI Proxy includes a smart installation script that automatically handles virtual environments for Homebrew/macOS users:

```bash
# Clone the repository
git clone https://github.com/agromanon/ai-proxy.git
cd ai-proxy

# Run the smart installation script
./install.sh

# Start the proxy
./start.sh
```

### What the Smart Installation Script Does

1. **Automatically Creates Virtual Environment**:
   - Creates a Python virtual environment in the `venv` directory
   - Activates the virtual environment automatically
   - Installs all dependencies in the virtual environment

2. **Handles Dependencies Properly**:
   - Installs Flask, Requests, Bcrypt, and other dependencies in the virtual environment
   - Avoids conflicts with Homebrew-managed packages
   - Ensures consistent versions across all installations

3. **Creates Default Configuration**:
   - Generates `.env` file with default settings
   - Creates necessary directories (logs, data, templates)
   - Sets up database with default schema

4. **Provides Startup Scripts**:
   - Creates platform-specific startup scripts (`start.sh` for Unix/macOS, `start.bat` for Windows)
   - Makes scripts executable automatically

### Manual Virtual Environment Setup (Alternative)

If you prefer to set up the virtual environment manually:

```bash
# Clone the repository
git clone https://github.com/agromanon/ai-proxy.git
cd ai-proxy

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create default configuration
touch .env

# Create directories
mkdir -p logs data templates

# Start the proxy
python app.py
```

### Platform-Specific Considerations

#### macOS with Homebrew
- The installation script automatically detects Homebrew and creates a virtual environment
- No need to modify system Python or Homebrew installation
- All dependencies are isolated in the virtual environment

#### Ubuntu/Debian with System Python
If you encounter the externally managed environment error on Ubuntu/Debian:

```bash
# Install python3-venv if not already installed
sudo apt update
sudo apt install python3-venv

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the package
pip install -e .

# Run the proxy
python app.py
```

## Platform-Specific Instructions

### Windows Users
Windows users can use the `start.bat` script:

```bash
# Clone the repository
git clone https://github.com/agromanon/ai-proxy.git
cd ai-proxy

# Run the installation script
install.bat

# Start the proxy
start.bat
```

### Linux Users
Linux users can use the `start.sh` script:

```bash
# Clone the repository
git clone https://github.com/agromanon/ai-proxy.git
cd ai-proxy

# Make scripts executable
chmod +x install.sh start.sh

# Run the installation script
./install.sh

# Start the proxy
./start.sh
```

### macOS Users
macOS users can use the `start.sh` script:

```bash
# Clone the repository
git clone https://github.com/agromanon/ai-proxy.git
cd ai-proxy

# Make scripts executable
chmod +x install.sh start.sh

# Run the installation script
./install.sh

# Start the proxy
./start.sh
```

## First-Time Setup

### Access the Web Interface
After starting the proxy, access the web interface at:
**http://localhost:8000**

### Default Login Credentials
- **Username**: `admin`
- **Password**: Check console output for the generated password

**Important**: Change the default password immediately after first login!

### Configure Providers
1. Navigate to the **Providers** section in the web interface
2. Click **Add New Provider**
3. Fill in the provider details through the web form:
   - **Name**: Descriptive name for the provider
   - **API Endpoint**: The API endpoint URL
   - **API Key**: Your API key for the provider
   - **Default Model**: Default model to use
   - **Authentication Method**: Bearer token (default), Basic Auth, or Custom Header
   - **Custom Headers**: Additional headers if needed
4. Click **Save**

### Configure System Prompts
1. Navigate to the **System Prompt** section in the web interface
2. Toggle **Use Custom Prompt** to enable custom prompts
3. Modify the prompt template as needed using the text editor
4. Adjust configuration parameters:
   - **System Name**: Name for the AI assistant
   - **Model Name Override**: Override model references in prompts
   - **Remove AI References**: Remove company-specific references
   - **Remove Defensive Restrictions**: Remove security restrictions

### Configure Application Settings
1. Navigate to the **Settings** section in the web interface
2. Adjust server configuration:
   - **Port**: Port number for the proxy server (default: 8000)
   - **Host**: Host address for the proxy server (default: 127.0.0.1)
3. Configure security settings:
   - **Secret Key**: Flask secret key for session encryption
   - **Require Authentication**: Require authentication for the web interface
   - **Secure Session Cookies**: Enable secure cookies (HTTPS only)
4. Adjust logging options:
   - **Enable Full Logging**: Enable detailed request/response logging
   - **Log Directory**: Directory for storing logs
5. Configure API settings:
   - **Enable Streaming**: Enable streaming responses
   - **Request Timeout**: Request timeout in seconds
6. Set rate limiting:
   - **Enable Rate Limiting**: Enable rate limiting to prevent abuse
   - **Requests per Window**: Number of requests allowed per time window
   - **Window Size**: Time window in seconds

## Usage

### Claude Code Integration
After configuration through the web interface, use providers with simple commands:

```bash
# Use any configured provider
export ANTHROPIC_BASE_URL=http://localhost:8000/v1/messages/openrouter
claude

# Or use custom command aliases defined in the web interface
export ANTHROPIC_BASE_URL=http://localhost:8000/v1/messages/my-custom-command
claude
```

### Provider Endpoints
Each provider has two dedicated endpoints:
- **Standard**: Default system prompt (`/v1/messages/openrouter`)
- **Custom**: Configurable system prompt (`/v1/messages/openrouter-custom`)

### Multiple Provider Usage
You can use different providers simultaneously in different terminal sessions:

```bash
# Terminal 1: OpenRouter with standard prompt
export ANTHROPIC_BASE_URL=http://localhost:8000/v1/messages/openrouter
claude

# Terminal 2: Chutes with custom prompt
export ANTHROPIC_BASE_URL=http://localhost:8000/v1/messages/chutes-custom
claude

# Terminal 3: AIML with standard prompt
export ANTHROPIC_BASE_URL=http://localhost:8000/v1/messages/aiml
claude
```

## Updating

To update to the latest version:

```bash
# Pull the latest changes
git pull

# Run the installation script to update dependencies
./install.sh

# Restart the proxy
./start.sh
```

## Troubleshooting

### Common Issues

#### Port Already in Use
If you get an error that port 8000 is already in use:

```bash
# Change the port in the web interface under Settings
# Or temporarily kill the process using the port:
lsof -i :8000
kill -9 PID
```

#### Database Issues
If you encounter database errors:

```bash
# Backup the database
cp data/app.db data/app.db.backup

# Reset the database (loses all configuration)
rm data/app.db
# Restart the application to recreate database
```

#### Provider Connection Failures
1. Verify API key is correct through the web interface
2. Check API endpoint URL
3. Test connectivity using the "Test" button
4. Check provider status pages

#### Authentication Issues
1. Verify username and password
2. Reset password if needed
3. Check if account is locked

#### Performance Issues
1. Check network connectivity
2. Verify provider status
3. Review logs in the web interface

### Logs
Logs are stored in the configured log directory and provide detailed information about requests and errors. Access logs through the web interface.

### Support
For issues not covered in this guide, please check the project GitHub repository or contact support.