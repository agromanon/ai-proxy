# Installation Guide

## Prerequisites
- Python 3.8 or higher
- Git (recommended for getting the latest version)

## Installation Methods

### Method 1: Install from Source with Virtual Environment (Recommended)
```bash
# Clone the repository
git clone https://github.com/agromanon/ai-proxy.git
cd ai-proxy

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in development mode
pip install -e .

# Run the proxy
python app.py
```

### Method 2: Install from PyPI (When available)
```bash
# Install the package
pip install ai-proxy

# Run the proxy
ai-proxy
```

### Method 3: Run without installation using virtual environment
```bash
# Clone the repository
git clone https://github.com/agromanon/ai-proxy.git
cd ai-proxy

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the proxy
python app.py
```

## Platform-Specific Instructions

### Homebrew/macOS Users (PEP 668 Externally Managed Environment)
If you're using Homebrew on macOS, you may encounter this error:
```
error: externally-managed-environment
× This environment is externally managed
```

**Solution**: Use a virtual environment instead of installing globally.

```bash
# Clone the repository
git clone https://github.com/agromanon/ai-proxy.git
cd ai-proxy

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install the package
pip install -e .

# Run the proxy
python app.py
```

### Ubuntu/Debian Users with System Python
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

## First-Time Setup

1. After starting the proxy, access the web interface at `http://localhost:8000`
2. Log in with the default credentials:
   - Username: `admin`
   - Password: Check console output for the generated password
3. Change the default password immediately
4. Configure your AI providers through the web interface
5. Add API keys for the providers you want to use

## Usage

After configuration, you can use the proxy with Claude Code or any Anthropic-compatible client:

```bash
# Use any configured provider
export ANTHROPIC_BASE_URL=http://localhost:8000/v1/messages/openrouter
claude

# Or use custom command aliases defined in the web interface
export ANTHROPIC_BASE_URL=http://localhost:8000/v1/messages/my-custom-command
claude
```

## Updating

To update to the latest version:

```bash
# If installed from source
cd ai-proxy
git pull
source venv/bin/activate  # If using virtual environment
pip install -e .

# If installed from PyPI
pip install --upgrade ai-proxy
```

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.