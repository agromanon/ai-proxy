# Troubleshooting Guide

## Common Installation Issues

### Homebrew/macOS Users (PEP 668 Externally Managed Environment)

If you're using Homebrew on macOS, you may encounter this error:
```
error: externally-managed-environment
× This environment is externally managed
```

**Solution**: Use a virtual environment instead of installing globally.

#### Option 1: Using Python's built-in venv (Recommended)
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

#### Option 2: Using pipx (Alternative)
```bash
# Install pipx if you don't have it
brew install pipx

# Install the package using pipx
pipx install .

# Run the proxy
pipx run ai-proxy
```

#### Option 3: Using conda (If you have Anaconda/Miniconda)
```bash
# Create conda environment
conda create -n ai-proxy python=3.11
conda activate ai-proxy

# Install the package
pip install -e .

# Run the proxy
python app.py
```

### Ubuntu/Debian Users with System Python

If you encounter the externally managed environment error on Ubuntu/Debian:

#### Solution 1: Use virtual environment (Recommended)
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

#### Solution 2: Use --user flag (Alternative)
```bash
# Install with --user flag
pip install --user -e .

# Run the proxy
python app.py
```

## Running the Application

### Starting the Proxy
After successful installation, you can start the proxy in several ways:

#### Method 1: Direct Python execution
```bash
# Activate virtual environment (if using one)
source venv/bin/activate

# Run the application
python app.py
```

#### Method 2: Using the installed package
```bash
# Activate virtual environment (if using one)
source venv/bin/activate

# Run using the installed package
ai-proxy
```

#### Method 3: Using startup scripts
```bash
# On Linux/macOS
./start.sh

# On Windows
start.bat
```

### Default Configuration
The proxy will start with these default settings:
- **Host**: 127.0.0.1 (localhost)
- **Port**: 8000
- **Database**: app.db (SQLite file in the project directory)
- **Log Directory**: logs/ (created automatically)

## Web Interface Access

After starting the proxy, access the web interface at:
**http://localhost:8000**

### Default Login Credentials
- **Username**: admin
- **Password**: Check the console output when you first start the application for the generated password

**Important**: Change the default password immediately after first login!

## Provider Configuration

### Adding Providers Through Web Interface
1. Navigate to the "Providers" section in the web interface
2. Click "Add New Provider"
3. Fill in the provider details:
   - **Name**: Descriptive name for the provider
   - **API Endpoint**: The API endpoint URL
   - **API Key**: Your API key for the provider
   - **Default Model**: Default model to use
   - **Authentication Method**: Bearer token (default), Basic Auth, or Custom Header
   - **Custom Headers**: Additional headers if needed
4. Click "Save"

### Supported Providers
The proxy supports the following providers out of the box:

#### Grok (Direct)
- **API Endpoint**: `https://api.x.ai/v1`
- **Authentication**: Bearer token
- **Format**: Anthropic-compatible

#### Grok (OpenAI)
- **API Endpoint**: `https://api.x.ai/v1`
- **Authentication**: Bearer token
- **Format**: OpenAI-compatible

#### OpenRouter
- **API Endpoint**: `https://openrouter.ai/api/v1`
- **Authentication**: Bearer token
- **Format**: OpenAI-compatible

#### AIML API
- **API Endpoint**: `https://api.aimlapi.com/v1`
- **Authentication**: Bearer token
- **Format**: OpenAI-compatible

#### Synthetic
- **API Endpoint**: `https://api.synthetic.new/v1`
- **Authentication**: Bearer token
- **Format**: OpenAI-compatible

#### Chutes
- **API Endpoint**: `http://llm.chutes.ai/api/v1`
- **Authentication**: Bearer token
- **Format**: OpenAI-compatible

### Testing Providers
Each provider can be tested for connectivity using the "Test" button in the provider list.

### Activating Providers
Only one provider can be active at a time. Click the "Activate" button to set a provider as active.

## Claude Code Usage

### Setting the Base URL
After configuring providers through the web interface, use them with Claude Code:

```bash
# For OpenRouter with standard prompt
export ANTHROPIC_BASE_URL=http://localhost:8000/v1/messages/openrouter
claude

# For Chutes with custom prompt
export ANTHROPIC_BASE_URL=http://localhost:8000/v1/messages/chutes-custom
claude

# For AIML with standard prompt
export ANTHROPIC_BASE_URL=http://localhost:8000/v1/messages/aiml
claude
```

### Custom Command Aliases
You can define custom command aliases through the web interface:

```bash
# Using custom command alias
export ANTHROPIC_BASE_URL=http://localhost:8000/v1/messages/my-custom-command
claude
```

## Common Issues and Solutions

### Port Already in Use
If you get an error that port 8000 is already in use:

```bash
# Change the port in the web interface under Settings
# Or temporarily kill the process using the port:
lsof -i :8000
kill -9 PID
```

### Database Lock Issues
If you encounter database lock errors:

```bash
# Stop the application
# Remove the lock file if it exists
rm app.db.lock
# Restart the application
```

### Permission Denied Errors
If you get permission denied errors:

```bash
# Make sure you have write permissions in the project directory
chmod -R 755 .
# Or run with appropriate permissions
sudo chown -R $USER:$USER .
```

### Missing Dependencies
If you get import errors for missing dependencies:

```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### SSL/HTTPS Issues
If you're running behind a reverse proxy with HTTPS:

1. Update the application settings in the web interface:
   - Enable "Secure Session Cookies"
   - Update the server host if needed

### Rate Limiting
If you hit rate limits:

1. Check the rate limiting settings in the web interface
2. Increase the limit or window size
3. Or implement proper retry logic in your client

## Logging and Monitoring

### Log Files
Logs are stored in the configured log directory (default: `logs/`):

- **proxy.log**: Main application logs
- **request logs**: Detailed request/response logs (if enabled)

### Log Levels
The application uses these log levels:
- **DEBUG**: Detailed debugging information
- **INFO**: General information about application operation
- **WARNING**: Potentially harmful situations
- **ERROR**: Error events that might still allow the application to continue
- **CRITICAL**: Critical events that will likely lead to application termination

### Monitoring
Monitor the application health:
```bash
# Check if the application is running
curl http://localhost:8000/health

# Check logs
tail -f logs/proxy.log
```

## Performance Tuning

### Database Performance
For high-traffic deployments:
1. Consider using PostgreSQL instead of SQLite
2. Increase database connection pool size
3. Optimize database indexes

### Memory Usage
Monitor memory usage:
```bash
# Check memory usage
ps aux | grep python
```

### Connection Handling
For high-concurrency scenarios:
1. Adjust request timeout settings
2. Tune rate limiting parameters
3. Consider load balancing for multiple instances

## Security Considerations

### API Keys
- Never commit API keys to version control
- Use environment variables or the web interface for configuration
- Rotate keys regularly

### Authentication
- Always change the default admin password
- Use strong, unique passwords
- Enable two-factor authentication if available

### Network Security
- Restrict access to the proxy server
- Use HTTPS in production environments
- Implement proper firewall rules

### Input Validation
- The application includes built-in input validation
- Keep dependencies updated
- Regularly review security advisories

## Updates and Maintenance

### Updating the Application
To update to the latest version:

```bash
# Pull the latest changes
git pull

# If using virtual environment, reactivate it
source venv/bin/activate

# Reinstall the package
pip install -e .

# Restart the application
```

### Backing Up Data
Regularly back up your configuration:

```bash
# Backup the database
cp app.db app.db.backup.$(date +%Y%m%d)

# Or use the built-in backup feature in the web interface
```

### Database Migration
If you encounter database schema issues:

```bash
# Check the database schema
sqlite3 app.db .schema

# The application should handle migrations automatically
# If issues persist, consult the GitHub issues or create a new one
```

## Getting Help

### Documentation
- [README.md](README.md): Main project documentation
- [INSTALL.md](INSTALL.md): Installation guide
- [USER_GUIDE.md](docs/USER_GUIDE.md): Complete user guide

### Community Support
- GitHub Issues: https://github.com/agromanon/ai-proxy/issues
- Discussions: https://github.com/agromanon/ai-proxy/discussions

### Professional Support
For enterprise support options, contact the maintainers.

## Reporting Issues

When reporting issues, please include:
1. **Error messages** and stack traces
2. **Steps to reproduce** the issue
3. **Environment information** (OS, Python version, etc.)
4. **Configuration details** (without sensitive information)
5. **Log excerpts** showing the problem

This information helps maintainers diagnose and fix issues more quickly.