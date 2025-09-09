#!/usr/bin/env python3
"""
AI Proxy - Main Application with Command Alias Routing
"""

import os
import json
import logging
import traceback
from datetime import datetime
from flask import Flask, request, Response, jsonify
from config.database import db_manager
from config.utils import db_utils
from config.command_alias_manager import command_alias_manager
from security.auth_manager import auth_manager, session_manager
from security.utils import configure_session
from provider_registry import ProviderRegistry
from dynamic_provider_loader import DynamicProviderLoader
from errors.handlers import handle_api_errors, create_error_response
from validation.validators import validate_anthropic_request
from security.rate_limiter import check_rate_limit

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('proxy.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize components
provider_registry = ProviderRegistry()
provider_loader = DynamicProviderLoader(db_manager, provider_registry)

# Create Flask app
app = Flask(__name__)

# Configure session
configure_session(app)

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# Dynamic routing based on command aliases
@app.route('/v1/messages/<command_alias>', methods=['POST'])
@handle_api_errors
def alias_based_proxy(command_alias):
    """
    Dynamic endpoint that routes based on command alias
    
    Args:
        command_alias: The command alias to route to
        
    Returns:
        Flask Response
    """
    # Look up provider by command alias
    provider_info = command_alias_manager.get_provider_by_alias(command_alias)
    
    if not provider_info:
        # Try default routing based on provider name
        return proxy_request(provider_name=command_alias, custom_prompt='custom' in command_alias)
    
    # Determine if custom prompt should be used
    custom_prompt = provider_info.get('alias_type') == 'custom'
    
    # Get actual provider name
    provider_name = provider_info['name']
    
    return proxy_request(provider_name=provider_name, custom_prompt=custom_prompt)

# Fallback to provider name-based routing for backward compatibility
@app.route('/v1/messages/<provider_name>', methods=['POST'])
@handle_api_errors
def provider_standard(provider_name):
    """Generic provider endpoint with standard prompt"""
    return proxy_request(provider_name=provider_name, custom_prompt=False)

@app.route('/v1/messages/<provider_name>-custom', methods=['POST'])
@handle_api_errors
def provider_custom(provider_name):
    """Generic provider endpoint with custom prompt"""
    return proxy_request(provider_name=provider_name, custom_prompt=True)

def proxy_request(provider_name: str, custom_prompt: bool = False):
    """
    Main proxy request handler
    
    Args:
        provider_name: Name of the provider to use
        custom_prompt: Whether to use custom prompt configuration
        
    Returns:
        Flask Response
    """
    start_time = datetime.now()
    request_id = f"req_{datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]}"
    
    try:
        # Rate limiting
        app_settings = db_utils.get_app_settings()
        if app_settings.get('rate_limit_enabled', True):
            client_ip = request.remote_addr
            check_rate_limit(client_ip)
        
        # Parse request data
        if not request.is_json:
            return create_error_response("Request must be JSON", "INVALID_REQUEST", 400), 400
        
        data = request.json
        if not data:
            return create_error_response("Request body is empty", "EMPTY_REQUEST", 400), 400
        
        # Validate request format
        try:
            data = validate_anthropic_request(data)
        except Exception as e:
            return create_error_response(str(e), "VALIDATION_ERROR", 400), 400
        
        # Log request details
        logger.info("="*80)
        logger.info(f"NEW REQUEST {request_id}")
        logger.info("="*80)
        logger.info(f"Provider: {provider_name}")
        logger.info(f"Custom Prompt: {custom_prompt}")
        logger.info(f"Model: {data.get('model', 'not specified')}")
        logger.info(f"Messages: {len(data.get('messages', []))}")
        
        # Get provider configuration
        provider_config = provider_loader.get_provider_by_name(provider_name)
        if not provider_config:
            return create_error_response(f"Provider '{provider_name}' not found", "PROVIDER_NOT_FOUND", 404), 404
        
        # Create provider instance
        provider_instance = provider_loader.create_provider_instance(provider_config)
        if not provider_instance:
            return create_error_response(f"Failed to create provider instance for '{provider_name}'", "PROVIDER_ERROR", 500), 500
        
        # Get prompt configuration if needed
        prompt_config = None
        if custom_prompt:
            prompt_config = db_utils.get_prompt_config()
        
        # Prepare request for provider
        try:
            if custom_prompt and prompt_config and prompt_config.get('use_custom_prompt'):
                provider_request = provider_instance.prepare_request(
                    data, 
                    prompt_config.get('prompt_template'),
                    prompt_config
                )
            else:
                provider_request = provider_instance.prepare_request(data)
        except Exception as e:
            logger.error(f"Error preparing request for provider '{provider_name}': {str(e)}")
            return create_error_response(f"Error preparing request: {str(e)}", "REQUEST_PREP_ERROR", 500), 500
        
        # Send request to provider
        stream = data.get('stream', False)
        try:
            response = provider_instance.send_request(provider_request, stream=stream)
        except Exception as e:
            logger.error(f"Error sending request to provider '{provider_name}': {str(e)}")
            return create_error_response(f"Provider error: {str(e)}", "PROVIDER_ERROR", 500), 500
        
        # Handle response
        if response.status_code != 200:
            logger.error(f"Provider '{provider_name}' returned error: {response.status_code} - {response.text}")
            return Response(response.content, content_type=response.headers.get('Content-Type'), status=response.status_code)
        
        # Handle streaming response
        if stream:
            def generate():
                try:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            yield chunk
                except Exception as e:
                    logger.error(f"Error during streaming from '{provider_name}': {str(e)}")
                    yield json.dumps(create_error_response(f"Streaming error: {str(e)}", "STREAMING_ERROR", 500))
            
            return Response(
                generate(),
                content_type=response.headers.get('Content-Type'),
                status=response.status_code
            )
        
        # Handle non-streaming response
        try:
            provider_response = response.json()
        except Exception as e:
            logger.error(f"Error parsing response from '{provider_name}': {str(e)}")
            return create_error_response(f"Error parsing response: {str(e)}", "RESPONSE_PARSE_ERROR", 500), 500
        
        # Convert response back to Anthropic format
        try:
            anthropic_response = provider_instance.process_response(provider_response)
        except Exception as e:
            logger.error(f"Error processing response from '{provider_name}': {str(e)}")
            return create_error_response(f"Error processing response: {str(e)}", "RESPONSE_PROCESS_ERROR", 500), 500
        
        # Calculate duration
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        # Log successful request
        logger.info(f"Request {request_id} to '{provider_name}' completed successfully in {duration_ms:.2f}ms")
        
        # Log to database if enabled
        if app_settings.get('enable_full_logging', True):
            try:
                db_utils.log_request({
                    'request_id': request_id,
                    'provider_name': provider_name,
                    'model_used': data.get('model'),
                    'request_data': json.dumps(data),
                    'response_data': json.dumps(anthropic_response),
                    'status_code': 200,
                    'duration_ms': int(duration_ms)
                })
            except Exception as e:
                logger.warning(f"Failed to log request: {str(e)}")
        
        return Response(
            json.dumps(anthropic_response),
            content_type='application/json',
            status=200
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in proxy_request: {str(e)}")
        logger.error(traceback.format_exc())
        return create_error_response(f"Internal server error: {str(e)}", "INTERNAL_ERROR", 500), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return create_error_response("Endpoint not found", "NOT_FOUND", 404), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return create_error_response("Internal server error", "INTERNAL_ERROR", 500), 500

if __name__ == '__main__':
    # Get settings from database
    app_settings = db_utils.get_app_settings()
    
    # Run the app
    app.run(
        host=app_settings.get('server_host', '127.0.0.1'),
        port=app_settings.get('server_port', 8000),
        debug=False  # Set to False in production
    )