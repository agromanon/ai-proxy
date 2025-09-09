# Installation Guide

## Prerequisites
- Python 3.8 or higher
- Git (recommended for getting the latest version)

## Installation Methods

### Method 1: Install from Source (Recommended)
```bash
# Clone the repository
git clone https://github.com/agromanon/ai-proxy.git
cd ai-proxy

# Install in development mode
pip install -e .

# Run the proxy
ai-proxy
```

### Method 2: Install from PyPI (When available)
```bash
# Install the package
pip install ai-proxy

# Run the proxy
ai-proxy
```

### Method 3: Run without installation
```bash
# Clone the repository
git clone https://github.com/agromanon/ai-proxy.git
cd ai-proxy

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

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
pip install -e .

# If installed from PyPI
pip install --upgrade ai-proxy
```