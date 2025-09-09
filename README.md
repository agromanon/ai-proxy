# AI Proxy - Multi-Provider Claude Code Proxy

A Flask-based proxy that allows Claude Code (or any Anthropic-compatible client) to use multiple AI providers including Grok, OpenRouter, Chutes, Synthetic, and AIML through dedicated endpoints.

## 🚀 Key Features

### Multi-Provider Support
- **Grok (Direct)**: xAI's Grok models using Anthropic format
- **Grok (OpenAI)**: xAI's Grok models using OpenAI format
- **OpenRouter**: Hundreds of models (GPT-4, Claude, Llama, etc.)
- **Chutes**: AI models deployed on the Chutes platform
- **Synthetic**: GLM-4.5, Kimi K2, DeepSeek, Qwen 3 and other models
- **AIML**: Over 300 models including GPT-5, DeepSeek, Claude 4

### Multiple Endpoint Routing
Each provider has two dedicated endpoints:
- **Standard**: Default system prompt (`/v1/messages/openrouter`)
- **Custom**: Configurable system prompt (`/v1/messages/openrouter-custom`)

### Web Administration Interface
- **Easy Provider Configuration**: Add API keys and settings through web forms
- **Custom Provider Wizard**: Add new providers with guided setup
- **Command Alias Management**: Define custom command names for each provider
- **System Prompt Customization**: Configure prompts through the web UI
- **User Management**: Create users and API keys visually
- **Request Logging**: Monitor usage and performance
- **All Settings in UI**: No terminal environment variables needed

### Zero External Dependencies
- Embedded SQLite database
- Single Python runtime requirement
- No external services needed

## 🎯 Use Cases

### Developer Productivity
Use different providers for different tasks simultaneously:

```bash
# Terminal 1: OpenRouter for creative tasks
export ANTHROPIC_BASE_URL=http://localhost:8000/v1/messages/openrouter
claude

# Terminal 2: Chutes for technical tasks
export ANTHROPIC_BASE_URL=http://localhost:8000/v1/messages/chutes
claude

# Terminal 3: AIML for latest models with custom prompt
export ANTHROPIC_BASE_URL=http://localhost:8000/v1/messages/aiml-custom
claude
```

### Model Comparison
Compare different models side-by-side with the same prompt or different configurations.

### Team Collaboration
Deploy once, allow multiple developers to use different providers simultaneously.

## 🛠️ Quick Start

### One-Command Installation (Linux/macOS)
```bash
curl -sSL https://raw.githubusercontent.com/agromanon/ai-proxy/master/install.sh | bash
```

### Manual Installation
```bash
# Clone repository
git clone https://github.com/agromanon/ai-proxy.git
cd ai-proxy

# Run installation script
./install.sh

# Start the proxy
./start.sh
```

### Homebrew/macOS Users (PEP 668 Externally Managed Environment)
If you're using Homebrew on macOS, you may encounter this error:
```
error: externally-managed-environment
× This environment is externally managed
```

**Solution**: Use the included installation script which automatically handles virtual environments:

```bash
# Clone repository
git clone https://github.com/agromanon/ai-proxy.git
cd ai-proxy

# Run the smart installation script
./install.sh

# Start the proxy
./start.sh
```

The installation script will:
1. Automatically create and activate a virtual environment
2. Install all dependencies in the virtual environment
3. Configure the application with sensible defaults
4. Create necessary directories and files
5. Start the proxy server

### First-Time Setup
1. **Access the Web Interface**: Open http://localhost:8000 in your browser
2. **Login**: Use default credentials (admin/admin123) 
3. **Change Password**: Immediately change the default password
4. **Add Providers**: Configure your AI provider API keys through the web interface
5. **Configure Prompts**: Set up custom prompts if desired
6. **Define Commands**: Create custom command aliases for your providers

### Claude Code Usage
After configuration through the web interface, use providers with simple commands:

```bash
# Use any configured provider
export ANTHROPIC_BASE_URL=http://localhost:8000/v1/messages/openrouter
claude

# Or use custom command aliases defined in the web interface
export ANTHROPIC_BASE_URL=http://localhost:8000/v1/messages/my-custom-command
claude
```

## 🎛️ Provider Endpoints

| Provider | Standard Endpoint | Custom Endpoint |
|----------|-------------------|-----------------|
| Grok (Direct) | `/v1/messages/grok-direct` | `/v1/messages/grok-direct-custom` |
| Grok (OpenAI) | `/v1/messages/grok-openai` | `/v1/messages/grok-openai-custom` |
| OpenRouter | `/v1/messages/openrouter` | `/v1/messages/openrouter-custom` |
| Chutes | `/v1/messages/chutes` | `/v1/messages/chutes-custom` |
| Synthetic | `/v1/messages/synthetic` | `/v1/messages/synthetic-custom` |
| AIML | `/v1/messages/aiml` | `/v1/messages/aiml-custom` |

## 🎨 Custom Provider Wizard

Add new providers through the intuitive web wizard:
1. **Provider Info**: Name and API endpoint
2. **Authentication**: Bearer token, Basic Auth, or Custom Header
3. **API Format**: OpenAI, Anthropic, or Grok compatible
4. **Custom Commands**: Define your own command aliases
5. **Test & Save**: Verify connection before saving

## 🔧 Web-Based Configuration

**All configuration is managed through the web interface:**

### Provider Management
- Add, edit, delete providers through forms
- Test connections before saving
- Set active providers
- Define custom command aliases

### System Prompts
- Enable/disable custom prompts
- Modify prompt templates visually
- Configure prompt modifications (remove restrictions, etc.)

### Application Settings
- Server configuration (port, host)
- Security settings (secret key, authentication)
- Logging options
- Rate limiting
- API settings

### User Management
- Create multiple user accounts
- Generate API keys for programmatic access
- Manage sessions

## ☁️ Cloud Deployment

Deploy to popular cloud platforms:
- **Heroku**: `./deploy/heroku_deploy.sh`
- **Railway**: `./deploy/railway_deploy.sh`
- **AWS ECS**: `./deploy/aws_deploy.sh`
- **Docker**: `docker-compose up -d`

## 📚 Documentation

- [User Guide](docs/user_guide.md) - Complete usage instructions
- [Installation Guide](INSTALL.md) - Installation instructions
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Common issues and solutions
- [Deployment Guide](docs/deployment.md) - Local and cloud deployment
- [Client Usage](docs/client_usage.md) - Claude Code configuration
- [Developer Guide](docs/developer_guide.md) - Extending the proxy
- [API Reference](docs/api_reference.md) - Endpoint documentation

## 🔒 Security

- Built-in authentication and authorization
- Rate limiting to prevent abuse
- Secure password hashing
- API key management
- Input validation and sanitization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.