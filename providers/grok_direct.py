"""
Grok Direct provider implementation (Anthropic format)
"""

import requests
import json
from typing import Dict, Any, Optional
from providers.base import BaseProvider

class GrokDirectProvider(BaseProvider):
    """Grok Direct provider implementation using Anthropic format"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Ensure correct endpoint
        if 'api.x.ai' not in self.api_endpoint:
            self.api_endpoint = 'https://api.x.ai/v1'
    
    def prepare_request(self, anthropic_request: Dict[str, Any], 
                       custom_prompt_template: Optional[str] = None,
                       prompt_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Convert Anthropic request to Anthropic format for Grok Direct"""
        # For direct Grok, we mostly pass through but may modify some fields
        request_data = anthropic_request.copy()
        
        # Map model to grok-4 if needed
        if 'claude' in request_data.get('model', '').lower():
            request_data['model'] = 'grok-4'
        
        # Apply custom prompt if needed
        if custom_prompt_template and prompt_config:
            # This would use the existing system prompt parsing logic
            pass
            
        return request_data
    
    def send_request(self, provider_request: Dict[str, Any], stream: bool = False) -> requests.Response:
        """Send request to Grok Direct API (Anthropic format)"""
        headers = {
            'Content-Type': 'application/json',
            **self.get_auth_headers()
        }
        
        # Add custom headers
        headers.update(self.headers)
        
        url = f"{self.api_endpoint}/messages"
        
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
            raise Exception(f"Error sending request to Grok Direct: {str(e)}")
    
    def process_response(self, provider_response: Dict[str, Any]) -> Dict[str, Any]:
        """Convert response to Anthropic format (mostly pass-through)"""
        if isinstance(provider_response, str):
            provider_response = json.loads(provider_response)
        
        # Grok Direct already returns Anthropic format, so minimal processing
        return provider_response
    
    def process_stream_response(self, response: requests.Response) -> Any:
        """Process streaming response from Grok Direct"""
        return response
    
    def test_connection(self) -> bool:
        """Test connection to Grok Direct API"""
        try:
            headers = {
                'Content-Type': 'application/json',
                **self.get_auth_headers()
            }
            
            test_request = {
                "model": "grok-4",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            
            response = requests.post(
                f"{self.api_endpoint}/messages",
                json=test_request,
                headers=headers,
                timeout=30
            )
            
            return response.status_code == 200
        except Exception as e:
            print(f"Error testing Grok Direct connection: {str(e)}")
            return False