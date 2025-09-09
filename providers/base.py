"""
Base provider class for all AI providers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseProvider(ABC):
    """Abstract base class for all AI providers"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize provider with configuration
        
        Args:
            config: Provider configuration dictionary
        """
        self.name = config['name']
        self.api_endpoint = config['api_endpoint']
        self.api_key = config['api_key']
        self.default_model = config.get('default_model')
        self.auth_method = config.get('auth_method', 'bearer_token')
        self.headers = config.get('headers', {})
        self.is_active = config.get('is_active', False)
    
    @abstractmethod
    def prepare_request(self, anthropic_request: Dict[str, Any], 
                       custom_prompt_template: Optional[str] = None,
                       prompt_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Convert Anthropic request format to provider format
        
        Args:
            anthropic_request: Anthropic format request
            custom_prompt_template: Custom prompt template
            prompt_config: Prompt configuration
            
        Returns:
            Provider format request
        """
        pass
    
    @abstractmethod
    def send_request(self, provider_request: Dict[str, Any], stream: bool = False) -> Any:
        """
        Send request to provider API
        
        Args:
            provider_request: Provider format request
            stream: Whether to stream the response
            
        Returns:
            Provider response
        """
        pass
    
    @abstractmethod
    def process_response(self, provider_response: Any) -> Dict[str, Any]:
        """
        Convert provider response to Anthropic format
        
        Args:
            provider_response: Provider format response
            
        Returns:
            Anthropic format response
        """
        pass
    
    @abstractmethod
    def process_stream_response(self, response: Any) -> Any:
        """
        Process streaming response from provider
        
        Args:
            response: Streaming response from provider
            
        Returns:
            Processed streaming response
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test connection to provider API
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers based on auth method
        
        Returns:
            Dictionary of authentication headers
        """
        headers = {}
        
        if self.auth_method == 'bearer_token':
            headers['Authorization'] = f'Bearer {self.api_key}'
        elif self.auth_method == 'basic_auth':
            import base64
            credentials = base64.b64encode(f'{self.api_key}'.encode()).decode()
            headers['Authorization'] = f'Basic {credentials}'
        elif self.auth_method == 'custom_header':
            # Custom header should be in headers config
            pass
        
        return headers
    
    def get_provider_format(self) -> str:
        """
        Get the API format for this provider
        
        Returns:
            Format type (openai, anthropic, etc.)
        """
        # Most providers use OpenAI format
        openai_providers = ['openrouter', 'aiml', 'synthetic', 'chutes']
        if any(provider in self.name.lower() for provider in openai_providers):
            return 'openai'
        else:
            return 'anthropic'