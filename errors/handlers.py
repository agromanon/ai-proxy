"""
Comprehensive error handling and validation framework
"""

import logging
import traceback
from typing import Any, Dict, Optional, Union
from functools import wraps
import json

# Set up logging
logger = logging.getLogger(__name__)

class ProxyError(Exception):
    """Base exception class for proxy errors"""
    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR", status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)

class ConfigurationError(ProxyError):
    """Exception for configuration-related errors"""
    def __init__(self, message: str):
        super().__init__(message, "CONFIGURATION_ERROR", 500)

class ProviderError(ProxyError):
    """Exception for provider-related errors"""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message, "PROVIDER_ERROR", status_code)

class AuthenticationError(ProxyError):
    """Exception for authentication-related errors"""
    def __init__(self, message: str):
        super().__init__(message, "AUTHENTICATION_ERROR", 401)

class ValidationError(ProxyError):
    """Exception for validation-related errors"""
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR", 400)

class RateLimitError(ProxyError):
    """Exception for rate limit errors"""
    def __init__(self, message: str):
        super().__init__(message, "RATE_LIMIT_ERROR", 429)

def handle_errors(func):
    """
    Decorator to handle errors in functions
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ProxyError:
            # Re-raise proxy errors as-is
            raise
        except Exception as e:
            # Log the full traceback
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Return a generic error
            raise ProxyError(f"Internal server error: {str(e)}", "INTERNAL_ERROR", 500)
    
    return wrapper

def handle_api_errors(func):
    """
    Decorator to handle API errors and return proper JSON responses
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ProxyError as e:
            logger.error(f"Proxy error: {e.message}")
            return create_error_response(e.message, e.error_code, e.status_code), e.status_code
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            logger.error(traceback.format_exc())
            return create_error_response(f"Internal server error: {str(e)}", "INTERNAL_ERROR", 500), 500
    
    return wrapper

def create_error_response(message: str, error_code: str, status_code: int) -> Dict[str, Any]:
    """
    Create a standardized error response
    
    Args:
        message: Error message
        error_code: Error code
        status_code: HTTP status code
        
    Returns:
        Error response dictionary
    """
    return {
        "error": {
            "message": message,
            "code": error_code,
            "status": status_code
        }
    }

def log_error(error: Exception, context: str = ""):
    """
    Log an error with context
    
    Args:
        error: The exception
        context: Additional context information
    """
    logger.error(f"Error {context}: {str(error)}")
    logger.error(traceback.format_exc())

def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """
    Safely parse JSON with error handling
    
    Args:
        json_string: JSON string to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to parse JSON: {str(e)}")
        return default

def safe_json_dumps(obj: Any, **kwargs) -> str:
    """
    Safely serialize JSON with error handling
    
    Args:
        obj: Object to serialize
        **kwargs: Additional arguments for json.dumps
        
    Returns:
        JSON string or empty string if serialization fails
    """
    try:
        return json.dumps(obj, **kwargs)
    except (TypeError, ValueError) as e:
        logger.warning(f"Failed to serialize to JSON: {str(e)}")
        return "{}"