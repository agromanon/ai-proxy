"""
Provider registry with endpoint mapping
"""

import os
import importlib
import inspect
from typing import Dict, List, Any, Optional
from providers.base import BaseProvider

class ProviderRegistry:
    """Registry for discovering and managing providers"""
    
    def __init__(self, providers_dir: str = "providers"):
        self.providers_dir = providers_dir
        self.providers: Dict[str, Dict[str, Any]] = {}
        self.endpoint_mapping: Dict[str, str] = {}
        self.discover_providers()
    
    def discover_providers(self):
        """Dynamically discover and load all provider implementations"""
        # Clear existing providers
        self.providers = {}
        self.endpoint_mapping = {}
        
        # Check if providers directory exists
        if not os.path.exists(self.providers_dir):
            print(f"Providers directory {self.providers_dir} not found")
            return
        
        # Iterate through provider files
        for filename in os.listdir(self.providers_dir):
            if filename.endswith('.py') and filename != '__init__.py' and filename != 'base.py':
                module_name = filename[:-3]  # Remove .py extension
                try:
                    # Import the module
                    module = importlib.import_module(f"providers.{module_name}")
                    
                    # Find provider classes
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, BaseProvider) and 
                            obj != BaseProvider):
                            # Register the provider
                            provider_key = module_name.replace('_', '-')
                            display_name = self._get_provider_display_name(module_name)
                            
                            self.providers[provider_key] = {
                                'class': obj,
                                'module': module_name,
                                'name': display_name,
                                'endpoints': {
                                    'standard': f'/v1/messages/{provider_key}',
                                    'custom': f'/v1/messages/{provider_key}-custom'
                                }
                            }
                            
                            # Map endpoints to provider keys
                            self.endpoint_mapping[f'/v1/messages/{provider_key}'] = provider_key
                            self.endpoint_mapping[f'/v1/messages/{provider_key}-custom'] = provider_key
                            
                            print(f"Registered provider: {provider_key} -> {display_name}")
                            
                except Exception as e:
                    print(f"Error loading provider {module_name}: {str(e)}")
    
    def _get_provider_display_name(self, module_name: str) -> str:
        """Convert module name to display name"""
        # Special handling for Grok providers
        if module_name == 'grok_direct':
            return 'Grok (Direct)'
        elif module_name == 'grok_openai':
            return 'Grok (OpenAI)'
        else:
            return module_name.replace('_', ' ').title()
    
    def get_provider_classes(self) -> Dict[str, Any]:
        """Get all registered provider classes"""
        return {key: provider['class'] for key, provider in self.providers.items()}
    
    def get_provider_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered providers"""
        return self.providers
    
    def get_provider_class(self, provider_key: str) -> Any:
        """Get a specific provider class by key"""
        if provider_key in self.providers:
            return self.providers[provider_key]['class']
        return None
    
    def get_endpoints(self) -> Dict[str, str]:
        """Get endpoint to provider mapping"""
        return self.endpoint_mapping
    
    def get_provider_endpoints(self, provider_key: str) -> Dict[str, str]:
        """Get endpoints for a specific provider"""
        if provider_key in self.providers:
            return self.providers[provider_key]['endpoints']
        return {}
    
    def get_all_endpoints(self) -> List[Dict[str, str]]:
        """Get all available endpoints with their descriptions"""
        endpoints = []
        for provider_key, provider_info in self.providers.items():
            endpoints.append({
                'endpoint': provider_info['endpoints']['standard'],
                'description': f"{provider_info['name']} with standard prompt",
                'provider': provider_info['name'],
                'custom_prompt': False
            })
            endpoints.append({
                'endpoint': provider_info['endpoints']['custom'],
                'description': f"{provider_info['name']} with custom prompt",
                'provider': provider_info['name'],
                'custom_prompt': True
            })
        return endpoints
    
    def is_valid_provider(self, provider_name: str) -> bool:
        """Check if a provider name is valid"""
        return provider_name.lower() in [key.lower() for key in self.providers.keys()]
    
    def normalize_provider_name(self, provider_name: str) -> str:
        """Normalize provider name to match registry key"""
        provider_name_lower = provider_name.lower().replace(' ', '_').replace('-', '_')
        for key in self.providers.keys():
            if key.lower() == provider_name_lower:
                return key
        return provider_name

# Global instance
provider_registry = ProviderRegistry()