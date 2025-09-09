"""
OpenRouter provider implementation
"""

import requests
import json
from typing import Dict, Any, Optional
from providers.base import BaseProvider
from converter.enhanced_converter import convert_anthropic_to_provider, convert_provider_to_anthropic

class OpenRouterProvider(BaseProvider):
    """OpenRouter provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Ensure correct endpoint
        if 'openrouter.ai' not in self.api_endpoint:
            self.api_endpoint = 'https://openrouter.ai/api/v1'
    
    def prepare_request(self, anthropic_request: Dict[str, Any], 
                       custom_prompt_template: Optional[str] = None,
                       prompt_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Convert Anthropic request to OpenAI format for OpenRouter"""
        return convert_anthropic_to_provider(
            anthropic_request, 
            provider_type='openai',
            custom_prompt_template=custom_prompt_template,
            config_file=None if not prompt_config else 'prompt_config.json'
        )
    
    def send_request(self, provider_request: Dict[str, Any], stream: bool = False) -> requests.Response:
        """Send request to OpenRouter API"""
        headers = {
            'Content-Type': 'application/json',
            **self.get_auth_headers()
        }
        
        # Add custom headers
        headers.update(self.headers)
        
        url = f"{self.api_endpoint}/chat/completions"
        
        try:
            response = requests.post(
                url,
                json=provider_request,
                headers=headers,
                stream=stream,
                timeout=300
            )
            return response
        except Exception as e:
            raise Exception(f"Error sending request to OpenRouter: {str(e)}")
    
    def process_response(self, provider_response: Dict[str, Any]) -> Dict[str, Any]:
        """Convert OpenAI response to Anthropic format"""
        if isinstance(provider_response, str):
            provider_response = json.loads(provider_response)
        
        return convert_provider_to_anthropic(provider_response, provider_type='openai')
    
    def process_stream_response(self, response: requests.Response) -> Any:
        """Process streaming response from OpenRouter"""
        # Streaming is handled by the main proxy
        return response
    
    def test_connection(self) -> bool:
        """Test connection to OpenRouter API"""
        try:
            headers = {
                'Content-Type': 'application/json',
                **self.get_auth_headers()
            }
            
            test_request = {
                "model": self.default_model or "openai/gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            
            response = requests.post(
                f"{self.api_endpoint}/chat/completions",
                json=test_request,
                headers=headers,
                timeout=30
            )
            
            return response.status_code == 200
        except Exception as e:
            print(f"Error testing OpenRouter connection: {str(e)}")
            return False