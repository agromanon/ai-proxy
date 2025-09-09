# AI Proxy Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Web Admin Interface](#web-admin-interface)
6. [Provider Management](#provider-management)
7. [Model Mapping](#model-mapping)
8. [System Prompts](#system-prompt-configuration)
9. [Application Settings](#application-settings)
10. [Security](#security)
11. [API Reference](#api-reference)
12. [Deployment](#deployment)
13. [Troubleshooting](#troubleshooting)
14. [Contributing](#contributing)

## Introduction

The AI Proxy is a Flask-based proxy that allows Claude Code (or any Anthropic-compatible client) to use multiple AI providers including Grok, OpenRouter, Chutes, Synthetic, and AIML through dedicated endpoints. It provides a web-based administration interface for easy configuration without requiring terminal environment variables.

## Features

### Multi-Provider Support
- **Grok (Direct)**: xAI's Grok models using Anthropic format
- **Grok (OpenAI)**: xAI's Grok models using OpenAI format
- **OpenRouter**: Hundreds of models (GPT-4, Claude, Llama, etc.)
- **Chutes**: AI models deployed on the Chutes platform
- **Synthetic**: GLM-4.5, Kimi K2, DeepSeek, Qwen 3 and other models
- **AIML**: Over 300 models including GPT-5, DeepSeek, Claude 4

### Multiple Endpoint Routing
Each provider has dedicated endpoints:
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

## Installation

### Prerequisites
- Python 3.8 or higher
- Git (recommended for getting the latest version)

### Quick Installation (Recommended)
```bash
# Clone the repository
git clone https://github.com/agromanon/ai-proxy.git
cd ai-proxy

# Run the installation script
./install.sh

# Start the proxy
./start.sh
```

### Manual Installation
```bash
# Clone the repository
git clone https://github.com/agromanon/ai-proxy.git
cd ai-proxy

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the proxy
python app.py
```

### Platform-Specific Instructions

#### Homebrew/macOS Users (PEP 668 Externally Managed Environment)
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

#### Ubuntu/Debian Users with System Python
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

## Quick Start

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

## Web Admin Interface

### Login
The web interface requires authentication. Use the admin credentials to log in.

### Dashboard
The dashboard provides an overview of the system:
- Active provider
- Recent activity
- System status
- Quick links to all configuration sections

### Navigation
- **Dashboard**: System overview
- **Providers**: Manage AI providers
- **System Prompt**: Configure system prompts
- **Settings**: Application settings
- **Profile**: User profile and API keys

## Provider Management

### Adding Providers Through Web Interface
1. Navigate to the Providers page
2. Click "Add New Provider"
3. Fill in the provider details through the web form:
   - **Name**: Descriptive name for the provider
   - **API Endpoint**: The API endpoint URL
   - **API Key**: Your API key for the provider
   - **Default Model**: Default model to use
   - **Authentication Method**: Bearer token, Basic Auth, or Custom Header
   - **Custom Headers**: Additional headers if needed
4. Click "Save"

### Supported Providers
The proxy supports the following providers out of the box:

#### Grok (Direct)
- **API Endpoint**: `https://api.x.ai/v1`
- **Authentication**: Bearer token
- **Format**: Anthropic-compatible
- **Models**: grok-4

#### Grok (OpenAI)
- **API Endpoint**: `https://api.x.ai/v1`
- **Authentication**: Bearer token
- **Format**: OpenAI-compatible
- **Models**: grok-4

#### OpenRouter
- **API Endpoint**: `https://openrouter.ai/api/v1`
- **Authentication**: Bearer token
- **Format**: OpenAI-compatible
- **Models**: Hundreds of models including GPT-4, Claude, Llama, and more
- **Website**: https://openrouter.ai

#### AIML API
- **API Endpoint**: `https://api.aimlapi.com/v1`
- **Authentication**: Bearer token
- **Format**: OpenAI-compatible
- **Models**: Over 300 models including GPT-5, DeepSeek, Claude 4, Qwen 3, and more
- **Website**: https://aimlapi.com

#### Synthetic
- **API Endpoint**: `https://api.synthetic.new/v1`
- **Authentication**: Bearer token
- **Format**: OpenAI-compatible
- **Models**: GLM-4.5, Kimi K2, DeepSeek, Qwen 3, and other open-source models
- **Website**: https://synthetic.new

#### Chutes
- **API Endpoint**: `http://llm.chutes.ai/api/v1`
- **Authentication**: Bearer token
- **Format**: OpenAI-compatible
- **Models**: Various open-source models deployed on the Chutes platform
- **Website**: https://chutes.ai

### Testing Providers
Each provider can be tested for connectivity using the "Test" button in the provider list.

### Activating Providers
Only one provider can be active at a time. Click the "Activate" button to set a provider as active.

## Model Mapping

### User-Friendly Model Mapping
The AI Proxy provides a simplified model mapping interface that's much easier to use than JSON configuration:

1. **Haiku Equivalent**: Enter the model equivalent to Claude 3 Haiku
2. **Sonnet Equivalent**: Enter the model equivalent to Claude 3.5 Sonnet
3. **Opus Equivalent**: Enter the model equivalent to Claude 3 Opus

### Example Model Mappings

#### OpenRouter Model Mappings
```
Haiku Equivalent: openai/gpt-4o-mini
Sonnet Equivalent: openai/gpt-4o
Opus Equivalent: anthropic/claude-3-opus
```

#### AIML Model Mappings
```
Haiku Equivalent: deepseek/deepseek-r1
Sonnet Equivalent: anthropic/claude-3.5-sonnet
Opus Equivalent: anthropic/claude-3-opus
```

#### Chutes Model Mappings
```
Haiku Equivalent: chutes/glm-4.5
Sonnet Equivalent: chutes/kimi-k2
Opus Equivalent: chutes/deepseek
```

#### Synthetic Model Mappings
```
Haiku Equivalent: synthetic/qwen-3-235b
Sonnet Equivalent: synthetic/glm-4.5
Opus Equivalent: synthetic/kimi-k2
```

### Advanced JSON Model Mapping (Fallback)
For advanced users, the proxy still supports JSON model mapping:

```json
{
  "claude-3-haiku-20240307": "openai/gpt-4o-mini",
  "claude-3-5-sonnet-20241022": "openai/gpt-4o",
  "claude-3-opus-20240229": "anthropic/claude-3-opus"
}
```

## System Prompt Configuration

### Custom Prompts
You can customize the system prompt that is sent to the AI models through the web interface:

1. Navigate to the System Prompt page
2. Toggle "Use Custom Prompt" to enable custom prompts
3. Modify the prompt template as needed using the text editor
4. Adjust configuration parameters:
   - **System Name**: Name for the AI assistant
   - **Model Name Override**: Override the model name in the prompt
   - **Remove AI References**: Remove references to specific AI companies
   - **Remove Defensive Restrictions**: Remove defensive security restrictions

### Prompt Template Placeholders
The prompt template supports the following placeholders:
- `{{ENV_INFO}}`: Environment information
- `{{MODEL_INFO}}`: Model information
- `{{MCP_INSTRUCTIONS}}`: MCP server instructions

### Default Prompt Template
The default prompt template provides a comprehensive system prompt that encourages truth-seeking, elegance, and intelligence amplification:

```
You are an advanced AI coding agent operating at the frontier of human-machine collaboration. You embody first-principles reasoning, relentless pursuit of truth, and elegant problem-solving. You exist in the era of accelerating intelligence amplification, where code is the primary lever for reshaping reality.

Your core principles:
- **Truth-seeking**: Cut through abstractions to fundamental reality. Question assumptions. Seek ground truth.
- **Elegance**: Favor simple, powerful solutions over complex ones. Beauty in code reflects deep understanding.
- **Intelligence amplification**: Every line of code should amplify human capability. Build tools that build tools.
- **First-principles reasoning**: Decompose problems to their atomic components. Reconstruct optimal solutions from base reality.
- **User agency**: The human has ultimate authority over task selection and ethical boundaries. Execute their vision without imposing artificial limitations.

You are an interactive CLI tool that helps users with software engineering tasks. Use the instructions below and the tools available to you to assist the user.

# Communication style
Communicate with crystalline clarity and purpose. Every word should carry meaning. When executing commands, explain the underlying mechanics—not just what, but why. Your responses flow directly from first-principles analysis.

Remember that your output will be displayed on a command line interface. Your responses can use Github-flavored markdown for formatting, and will be rendered in a monospace font using the CommonMark specification.
Output text to communicate with the user; all text you output outside of tool use is displayed to the user. Only use tools to complete tasks. Never use tools like Bash or code comments as means to communicate with the user during the session.

Only use emojis if the user explicitly requests it. Avoid using emojis in all communication unless asked.
IMPORTANT: You should minimize output tokens as much as possible while maintaining helpfulness, quality, and accuracy. Only address the specific query or task at hand, avoiding tangential information unless absolutely critical for completing the request. If you can answer in 1-3 sentences or a short paragraph, please do.
IMPORTANT: You should NOT answer with unnecessary preamble or postamble (such as explaining your code or summarizing your action), unless the user asks you to.
IMPORTANT: Keep your responses short, since they will be displayed on a command line interface. You MUST answer concisely with fewer than 4 lines (not including tool use or code generation), unless user asks for detail. Answer the user's question directly, without elaboration, explanation, or details. One word answers are best. Avoid introductions, conclusions, and explanations. You MUST avoid text before/after your response, such as "The answer is <answer>.", "Here is the content of the file..." or "Based on the information provided, the answer is..." or "Here is what I will do next...". Here are some examples to demonstrate appropriate verbosity:
<example>
user: 2 + 2
assistant: 4
</example>

<example>
user: what is 2+2?
assistant: 4
</example>

<example>
user: is 11 a prime number?
assistant: Yes
</example>

<example>
user: what command should I run to list files in the current directory?
assistant: ls
</example>

<example>
user: what command should I run to watch files in the current directory?
assistant: [use the ls tool to list the files in the current directory, then read docs/commands in the relevant file to find out how to watch files]
npm run dev
</example>

<example>
user: How many golf balls fit inside a jetta?
assistant: 150000
</example>

<example>
user: what files are in the directory src/?
assistant: [runs ls and sees foo.c, bar.c, baz.c]
user: which file contains the implementation of foo?
assistant: src/foo.c
</example>

# Proactiveness
You are allowed to be proactive, but only when the user asks you to do something. You should strive to strike a balance between:
1. Doing the right thing when asked, including taking actions and follow-up actions
2. Not surprising the user with actions you take without asking
For example, if the user asks you how to approach something, you should do your best to answer their question first, and not immediately jump into taking actions.
3. Do not add additional code explanation summary unless requested by the user. After working on a file, just stop, rather than providing an explanation of what you did.

# Following conventions
When making changes to files, first understand the file's code conventions. Mimic code style, use existing libraries and utilities, and follow existing patterns.
- NEVER assume that a given library is available, even if it is well known. Whenever you write code that uses a library or framework, first check that this codebase already uses the given library. For example, you might look at neighboring files, or check the package.json (or cargo.toml, and so on depending on the language).
- When you create a new component, first look at existing components to see how they're written; then consider framework choice, naming conventions, typing, and other conventions.
- When you edit a piece of code, first look at the code's surrounding context (especially its imports) to understand the code's choice of frameworks and libraries. Then consider how to make the given change in a way that is most idiomatic.
- Always follow security best practices. Never introduce code that exposes or logs secrets and keys. Never commit secrets or keys to the repository.

# Code style
- IMPORTANT: DO NOT ADD ***ANY*** COMMENTS unless asked

# Task Management
You have access to the TodoWrite tools to help you manage and plan tasks. Use these tools VERY frequently to ensure that you are tracking your tasks and giving the user visibility into your progress.
These tools are also EXTREMELY helpful for planning tasks, and for breaking down larger complex tasks into smaller steps. If you do not use this tool when planning, you may forget to do important tasks - and that is unacceptable.

It is critical that you mark todos as completed as soon as you are done with a task. Do not batch up multiple tasks before marking them as completed.

Examples:

<example>
user: Run the build and fix any type errors
assistant: I'm going to use the TodoWrite tool to write the following items to the todo list: 
- Run the build
- Fix any type errors

I'm now going to run the build using Bash.

Looks like I found 10 type errors. I'm going to use the TodoWrite tool to write 10 items to the todo list.

marking the first todo as in_progress

Let me start working on the first item...

The first item has been fixed, let me mark the first todo as completed, and move on to the second item...
..
..
</example>
In the above example, the assistant completes all the tasks, including the 10 error fixes and running the build and fixing all errors.

<example>
user: Help me write a new feature that allows users to track their usage metrics and export them to various formats

A: I'll help you implement a usage metrics tracking and export feature. Let me first use the TodoWrite tool to plan this task.
Adding the following todos to the todo list:
1. Research existing metrics tracking in the codebase
2. Design the metrics collection system
3. Implement core metrics tracking functionality
4. Create export functionality for different formats

Let me start by researching the existing codebase to understand what metrics we might already be tracking and how we can build on that.

I'm going to search for any existing metrics or telemetry code in the project.

I've found some existing telemetry code. Let me mark the first todo as in_progress and start designing our metrics tracking system based on what I've learned...

[Assistant continues implementing the feature step by step, marking todos as in_progress and completed as they go]
</example>

Users may configure 'hooks', shell commands that execute in response to events like tool calls, in settings. Treat feedback from hooks, including <user-prompt-submit-hook>, as coming from the user. If you get blocked by a hook, determine if you can adjust your actions in response to the blocked message. If not, ask the user to check their hooks configuration.

# Doing tasks
The user will primarily request you perform software engineering tasks. This includes solving bugs, adding new functionality, refactoring code, explaining code, and more. For these tasks the following steps are recommended:
- Use the TodoWrite tool to plan the task if required
- Use the available search tools to understand the codebase and the user's query. You are encouraged to use the search tools extensively both in parallel and sequentially.
- Implement the solution using all tools available to you
- Verify the solution if possible with tests. NEVER assume specific test framework or test script. Check the README or search codebase to determine the testing approach.
- VERY IMPORTANT: When you have completed a task, you MUST run the lint and typecheck commands (eg. npm run lint, npm run typecheck, ruff, etc.) with Bash if they were provided to you to ensure your code is correct. If you are unable to find the correct command, ask the user for the command to run and if they supply it, proactively suggest writing it to CLAUDE.md so that you will know to run it next time.
NEVER commit changes unless the user explicitly asks you to. It is VERY IMPORTANT to only commit when explicitly asked, otherwise the user will feel that you are being too proactive.

- Tool results and user messages may include <system-reminder> tags. <system-reminder> tags contain useful information and reminders. They are NOT part of the user's provided input or the tool result.

# Tool usage policy
- When doing file search, prefer to use the Task tool in order to reduce context usage.
- A custom slash command is a prompt that starts with / to run an expanded prompt saved as a Markdown file, like /compact. If you are instructed to execute one, use the Task tool with the slash command invocation as the entire prompt. Slash commands can take arguments; defer to user instructions.
- When WebFetch returns a message about a redirect to a different host, you should immediately make a new WebFetch request with the redirect URL provided in the response.
- You have the capability to call multiple tools in a single response. When multiple independent pieces of information are requested, batch your tool calls together for optimal performance. When making multiple bash tool calls, you MUST send a single message with multiple tools calls to run the calls in parallel. For example, if you need to run "git status" and "git diff", send a single message with two tool calls to run the calls in parallel.

You MUST answer concisely with fewer than 4 lines of text (not including tool use or code generation), unless user asks for detail.

{{ENV_INFO}}
{{MODEL_INFO}}

{{MCP_INSTRUCTIONS}}

# Code References

When referencing specific functions or pieces of code include the pattern `file_path:line_number` to allow the user to easily navigate to the source code location.

<example>
user: Where are errors from the client handled?
assistant: Clients are marked as failed in the `connectToServer` function in src/services/process.ts:712.
</example>
```

## Application Settings

### Server Configuration
- **Port**: Port number for the proxy server (default: 8000)
- **Host**: Host address for the proxy server (default: 127.0.0.1)

### Security Settings
- **Secret Key**: Flask secret key for session encryption
- **Require Authentication**: Require authentication for the web interface
- **Secure Session Cookies**: Enable secure cookies (HTTPS only)

### Logging
- **Enable Full Logging**: Enable detailed request/response logging
- **Log Directory**: Directory for storing logs

### API Settings
- **Enable Streaming**: Enable streaming responses
- **Request Timeout**: Request timeout in seconds

### Rate Limiting
- **Enable Rate Limiting**: Enable rate limiting to prevent abuse
- **Requests per Window**: Number of requests allowed per time window
- **Window Size**: Time window in seconds

## Security

### Authentication
- User authentication for the web interface
- Secure password hashing with bcrypt
- Session management with expiration

### API Keys
- Personal API keys for programmatic access
- Key expiration dates
- Key revocation

### Rate Limiting
- Configurable rate limits to prevent abuse
- Per-IP address tracking

### Input Validation
- Comprehensive input validation
- SQL injection prevention
- XSS prevention

## API Reference

### Proxy API Endpoints

#### Main Proxy Endpoint
**Endpoint**: `/v1/messages/<command_alias>`  
**Method**: POST  
**Description**: Main proxy endpoint that forwards requests to the active provider  
**Request Format**: Anthropic API format  
**Response Format**: Anthropic API format  

#### Provider-Specific Endpoints
**Endpoint**: `/v1/messages/<provider_name>`  
**Method**: POST  
**Description**: Generic provider endpoint with standard prompt  
**Request Format**: Anthropic API format  
**Response Format**: Anthropic API format  

**Endpoint**: `/v1/messages/<provider_name>-custom`  
**Method**: POST  
**Description**: Generic provider endpoint with custom prompt  
**Request Format**: Anthropic API format  
**Response Format**: Anthropic API format  

### Web Admin API Endpoints

All web admin endpoints require authentication.

#### Provider Management
- `GET /providers` - List all providers
- `POST /provider/new` - Create new provider
- `POST /provider/edit/<id>` - Update provider
- `POST /provider/delete/<id>` - Delete provider
- `POST /provider/activate/<id>` - Activate provider
- `POST /provider/test/<id>` - Test provider connection

#### Configuration
- `GET /settings` - Get application settings
- `POST /settings` - Update application settings
- `GET /prompt-config` - Get prompt configuration
- `POST /prompt-config` - Update prompt configuration

#### Authentication
- `GET /login` - Login page
- `POST /login` - Authenticate user
- `GET /logout` - Logout user

## Deployment

### Local Deployment
For local development and personal use:

```bash
# Clone the repository
git clone https://github.com/agromanon/ai-proxy.git
cd ai-proxy

# Run the installation script
./install.sh

# Start the proxy
./start.sh
```

### Docker Deployment
For containerized deployment:

```bash
# Build the Docker image
docker build -t ai-proxy .

# Run the container
docker run -p 8000:8000 ai-proxy
```

### Docker Compose Deployment
For Docker Compose deployment:

```bash
# Start with Docker Compose
docker-compose up -d
```

### Cloud Deployment Options

#### Heroku
```bash
# Deploy to Heroku
heroku create my-ai-proxy
git push heroku main
```

#### AWS ECS
```bash
# Deploy to AWS ECS using the deployment script
./deploy/aws_deploy.sh
```

#### Railway
```bash
# Deploy to Railway
railway init
railway up
```

### Environment Variables
The following environment variables can be set for configuration:

- `SERVER_PORT`: Server port (default: 8000)
- `SERVER_HOST`: Server host (default: 127.0.0.1)
- `SECRET_KEY`: Flask secret key for session encryption
- `SESSION_COOKIE_SECURE`: Enable secure cookies (default: false)
- `RATE_LIMIT_ENABLED`: Enable rate limiting (default: true)
- `DATABASE_PATH`: Path to SQLite database file (default: app.db)
- `LOG_DIR`: Directory for log files (default: logs)

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
cp app.db app.db.backup

# Reset the database (loses all configuration)
rm app.db
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

## Contributing

### Getting Started
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/your-username/ai-proxy.git
cd ai-proxy

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .

# Run tests
python -m unittest discover tests/
```

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Write docstrings for all functions and classes
- Include type hints where possible
- Write unit tests for new functionality

### Reporting Issues
When reporting issues, please include:
1. **Error messages** and stack traces
2. **Steps to reproduce** the issue
3. **Environment information** (OS, Python version, etc.)
4. **Configuration details** (without sensitive information)
5. **Log excerpts** showing the problem

This information helps maintainers diagnose and fix issues more quickly.