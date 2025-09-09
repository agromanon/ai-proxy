"""
Input validation for API requests and configuration
"""

import re
from typing import Any, Dict, List, Optional, Union
from errors.handlers import ValidationError

class Validator:
    """Base validator class"""
    
    @staticmethod
    def validate_string(value: Any, field_name: str, min_length: int = 0, max_length: int = None, 
                       pattern: str = None, required: bool = True) -> str:
        """
        Validate a string field
        
        Args:
            value: Value to validate
            field_name: Name of the field
            min_length: Minimum length
            max_length: Maximum length
            pattern: Regex pattern to match
            required: Whether the field is required
            
        Returns:
            Validated string
            
        Raises:
            ValidationError: If validation fails
        """
        # Check if required
        if required and (value is None or value == ""):
            raise ValidationError(f"{field_name} is required")
        
        # If not required and value is None or empty, return empty string
        if not required and (value is None or value == ""):
            return ""
        
        # Convert to string
        if not isinstance(value, str):
            value = str(value)
        
        # Check length
        if len(value) < min_length:
            raise ValidationError(f"{field_name} must be at least {min_length} characters long")
        
        if max_length and len(value) > max_length:
            raise ValidationError(f"{field_name} must be no more than {max_length} characters long")
        
        # Check pattern
        if pattern:
            if not re.match(pattern, value):
                raise ValidationError(f"{field_name} format is invalid")
        
        return value
    
    @staticmethod
    def validate_url(value: Any, field_name: str, required: bool = True) -> str:
        """
        Validate a URL field
        
        Args:
            value: Value to validate
            field_name: Name of the field
            required: Whether the field is required
            
        Returns:
            Validated URL
            
        Raises:
            ValidationError: If validation fails
        """
        url = Validator.validate_string(value, field_name, min_length=1, required=required)
        
        if url:
            # Basic URL validation
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            
            if not url_pattern.match(url):
                raise ValidationError(f"{field_name} must be a valid URL")
        
        return url
    
    @staticmethod
    def validate_api_key(value: Any, field_name: str, required: bool = True) -> str:
        """
        Validate an API key field
        
        Args:
            value: Value to validate
            field_name: Name of the field
            required: Whether the field is required
            
        Returns:
            Validated API key
            
        Raises:
            ValidationError: If validation fails
        """
        api_key = Validator.validate_string(value, field_name, min_length=16, required=required)
        return api_key
    
    @staticmethod
    def validate_integer(value: Any, field_name: str, min_value: int = None, 
                        max_value: int = None, required: bool = True) -> int:
        """
        Validate an integer field
        
        Args:
            value: Value to validate
            field_name: Name of the field
            min_value: Minimum value
            max_value: Maximum value
            required: Whether the field is required
            
        Returns:
            Validated integer
            
        Raises:
            ValidationError: If validation fails
        """
        # Check if required
        if required and value is None:
            raise ValidationError(f"{field_name} is required")
        
        # If not required and value is None, return None
        if not required and value is None:
            return None
        
        # Convert to integer
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be an integer")
        
        # Check range
        if min_value is not None and int_value < min_value:
            raise ValidationError(f"{field_name} must be at least {min_value}")
        
        if max_value is not None and int_value > max_value:
            raise ValidationError(f"{field_name} must be no more than {max_value}")
        
        return int_value
    
    @staticmethod
    def validate_boolean(value: Any, field_name: str, required: bool = False) -> bool:
        """
        Validate a boolean field
        
        Args:
            value: Value to validate
            field_name: Name of the field
            required: Whether the field is required
            
        Returns:
            Validated boolean
            
        Raises:
            ValidationError: If validation fails
        """
        if required and value is None:
            raise ValidationError(f"{field_name} is required")
        
        if value is None:
            return False
        
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes', 'on']
        
        if isinstance(value, (int, float)):
            return bool(value)
        
        raise ValidationError(f"{field_name} must be a boolean value")
    
    @staticmethod
    def validate_enum(value: Any, field_name: str, valid_values: List[str], 
                     required: bool = True) -> str:
        """
        Validate an enum field
        
        Args:
            value: Value to validate
            field_name: Name of the field
            valid_values: List of valid values
            required: Whether the field is required
            
        Returns:
            Validated enum value
            
        Raises:
            ValidationError: If validation fails
        """
        # Check if required
        if required and value is None:
            raise ValidationError(f"{field_name} is required")
        
        # If not required and value is None, return None
        if not required and value is None:
            return None
        
        # Convert to string
        if not isinstance(value, str):
            value = str(value)
        
        # Check if value is valid
        if value not in valid_values:
            raise ValidationError(f"{field_name} must be one of: {', '.join(valid_values)}")
        
        return value

def validate_provider_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate provider configuration
    
    Args:
        config: Provider configuration dictionary
        
    Returns:
        Validated configuration
        
    Raises:
        ValidationError: If validation fails
    """
    validated_config = {}
    
    # Validate name
    validated_config['name'] = Validator.validate_string(
        config.get('name'), 'Provider name', min_length=1, max_length=100
    )
    
    # Validate API endpoint
    validated_config['api_endpoint'] = Validator.validate_url(
        config.get('api_endpoint'), 'API endpoint'
    )
    
    # Validate API key
    validated_config['api_key'] = Validator.validate_api_key(
        config.get('api_key'), 'API key'
    )
    
    # Validate default model (optional)
    if config.get('default_model'):
        validated_config['default_model'] = Validator.validate_string(
            config.get('default_model'), 'Default model', max_length=100, required=False
        )
    else:
        validated_config['default_model'] = None
    
    # Validate auth method
    validated_config['auth_method'] = Validator.validate_enum(
        config.get('auth_method', 'bearer_token'), 
        'Authentication method',
        ['bearer_token', 'basic_auth', 'custom_header']
    )
    
    # Validate is_active (optional, default False)
    validated_config['is_active'] = Validator.validate_boolean(
        config.get('is_active', False), 'Active status', required=False
    )
    
    # Validate headers (optional)
    headers = config.get('headers', {})
    if headers:
        if not isinstance(headers, dict):
            raise ValidationError("Headers must be a dictionary")
        validated_config['headers'] = headers
    else:
        validated_config['headers'] = {}
    
    return validated_config

def validate_app_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate application settings
    
    Args:
        settings: Application settings dictionary
        
    Returns:
        Validated settings
        
    Raises:
        ValidationError: If validation fails
    """
    validated_settings = {}
    
    # Validate server port
    validated_settings['server_port'] = Validator.validate_integer(
        settings.get('server_port', 8000), 'Server port', min_value=1, max_value=65535
    )
    
    # Validate server host
    validated_settings['server_host'] = Validator.validate_string(
        settings.get('server_host', '127.0.0.1'), 'Server host', max_length=100
    )
    
    # Validate enable_full_logging
    validated_settings['enable_full_logging'] = Validator.validate_boolean(
        settings.get('enable_full_logging', True), 'Enable full logging', required=False
    )
    
    # Validate log_directory
    validated_settings['log_directory'] = Validator.validate_string(
        settings.get('log_directory', 'logs'), 'Log directory', max_length=255, required=False
    )
    
    # Validate enable_streaming
    validated_settings['enable_streaming'] = Validator.validate_boolean(
        settings.get('enable_streaming', True), 'Enable streaming', required=False
    )
    
    # Validate request_timeout
    validated_settings['request_timeout'] = Validator.validate_integer(
        settings.get('request_timeout', 300), 'Request timeout', min_value=1, max_value=3600
    )
    
    # Validate require_auth
    validated_settings['require_auth'] = Validator.validate_boolean(
        settings.get('require_auth', True), 'Require authentication', required=False
    )
    
    # Validate secret_key (optional)
    if settings.get('secret_key'):
        validated_settings['secret_key'] = Validator.validate_string(
            settings.get('secret_key'), 'Secret key', max_length=255, required=False
        )
    else:
        validated_settings['secret_key'] = None
    
    # Validate session_cookie_secure (optional)
    validated_settings['session_cookie_secure'] = Validator.validate_boolean(
        settings.get('session_cookie_secure', False), 'Session cookie secure', required=False
    )
    
    # Validate rate_limit_enabled (optional)
    validated_settings['rate_limit_enabled'] = Validator.validate_boolean(
        settings.get('rate_limit_enabled', True), 'Rate limit enabled', required=False
    )
    
    # Validate rate_limit_requests (optional)
    validated_settings['rate_limit_requests'] = Validator.validate_integer(
        settings.get('rate_limit_requests', 100), 'Rate limit requests', min_value=1, max_value=10000
    )
    
    # Validate rate_limit_window (optional)
    validated_settings['rate_limit_window'] = Validator.validate_integer(
        settings.get('rate_limit_window', 3600), 'Rate limit window', min_value=60, max_value=86400
    )
    
    return validated_settings

def validate_prompt_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate prompt configuration
    
    Args:
        config: Prompt configuration dictionary
        
    Returns:
        Validated configuration
        
    Raises:
        ValidationError: If validation fails
    """
    validated_config = {}
    
    # Validate use_custom_prompt
    validated_config['use_custom_prompt'] = Validator.validate_boolean(
        config.get('use_custom_prompt', False), 'Use custom prompt', required=False
    )
    
    # Validate prompt_template (optional)
    if config.get('prompt_template'):
        validated_config['prompt_template'] = Validator.validate_string(
            config.get('prompt_template'), 'Prompt template', required=False
        )
    else:
        validated_config['prompt_template'] = None
    
    # Validate system_name (optional)
    if config.get('system_name'):
        validated_config['system_name'] = Validator.validate_string(
            config.get('system_name'), 'System name', max_length=100, required=False
        )
    else:
        validated_config['system_name'] = None
    
    # Validate model_name_override (optional)
    if config.get('model_name_override'):
        validated_config['model_name_override'] = Validator.validate_string(
            config.get('model_name_override'), 'Model name override', max_length=100, required=False
        )
    else:
        validated_config['model_name_override'] = None
    
    # Validate remove_ai_references
    validated_config['remove_ai_references'] = Validator.validate_boolean(
        config.get('remove_ai_references', False), 'Remove AI references', required=False
    )
    
    # Validate remove_defensive_restrictions
    validated_config['remove_defensive_restrictions'] = Validator.validate_boolean(
        config.get('remove_defensive_restrictions', False), 'Remove defensive restrictions', required=False
    )
    
    return validated_config

def validate_anthropic_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate Anthropic API request format
    
    Args:
        request_data: Anthropic request data
        
    Returns:
        Validated request data
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(request_data, dict):
        raise ValidationError("Request data must be a JSON object")
    
    validated_request = {}
    
    # Validate model (required)
    if 'model' not in request_data:
        raise ValidationError("Model is required")
    
    validated_request['model'] = Validator.validate_string(
        request_data['model'], 'Model', min_length=1, max_length=100
    )
    
    # Validate messages (required)
    if 'messages' not in request_data:
        raise ValidationError("Messages are required")
    
    if not isinstance(request_data['messages'], list):
        raise ValidationError("Messages must be an array")
    
    validated_request['messages'] = request_data['messages']
    
    # Validate max_tokens (optional)
    if 'max_tokens' in request_data:
        validated_request['max_tokens'] = Validator.validate_integer(
            request_data['max_tokens'], 'Max tokens', min_value=1, max_value=4096
        )
    
    # Validate temperature (optional)
    if 'temperature' in request_data:
        temp = request_data['temperature']
        if not isinstance(temp, (int, float)) or temp < 0 or temp > 1:
            raise ValidationError("Temperature must be a number between 0 and 1")
        validated_request['temperature'] = temp
    
    # Validate system (optional)
    if 'system' in request_data:
        validated_request['system'] = request_data['system']
    
    # Validate tools (optional)
    if 'tools' in request_data:
        if not isinstance(request_data['tools'], list):
            raise ValidationError("Tools must be an array")
        validated_request['tools'] = request_data['tools']
    
    # Validate tool_choice (optional)
    if 'tool_choice' in request_data:
        validated_request['tool_choice'] = request_data['tool_choice']
    
    return validated_request