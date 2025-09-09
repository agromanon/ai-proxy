"""
Dynamic provider loader with endpoint support
"""

import json
import sqlite3
from typing import Dict, List, Any, Optional
from provider_registry import ProviderRegistry
from config.database import db_manager

class DynamicProviderLoader:
    """Load and manage provider configurations dynamically"""
    
    def __init__(self, db_manager, provider_registry: ProviderRegistry):
        self.db = db_manager
        self.provider_registry = provider_registry
    
    def load_all_providers(self) -> List[Dict[str, Any]]:
        """Load all provider configurations from database"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT p.*, 
                       GROUP_CONCAT(ph.header_key || ':' || ph.header_value) as headers
                FROM providers p
                LEFT JOIN provider_headers ph ON p.id = ph.provider_id
                GROUP BY p.id
                ORDER BY p.name
            """)
            
            providers = []
            for row in cursor.fetchall():
                provider_config = self._parse_provider_row(row)
                providers.append(provider_config)
            
            return providers
        except Exception as e:
            print(f"Error loading providers: {str(e)}")
            return []
    
    def get_provider_by_id(self, provider_id: int) -> Optional[Dict[str, Any]]:
        """Get provider configuration by ID"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT p.*, 
                       GROUP_CONCAT(ph.header_key || ':' || ph.header_value) as headers
                FROM providers p
                LEFT JOIN provider_headers ph ON p.id = ph.provider_id
                WHERE p.id = ?
                GROUP BY p.id
            """, (provider_id,))
            
            row = cursor.fetchone()
            if row:
                return self._parse_provider_row(row)
            
            return None
        except Exception as e:
            print(f"Error getting provider by ID: {str(e)}")
            return None
    
    def get_provider_by_name(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """Get provider configuration by name"""
        try:
            # Normalize provider name
            normalized_name = self.provider_registry.normalize_provider_name(provider_name)
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT p.*, 
                       GROUP_CONCAT(ph.header_key || ':' || ph.header_value) as headers
                FROM providers p
                LEFT JOIN provider_headers ph ON p.id = ph.provider_id
                WHERE LOWER(p.name) = LOWER(?)
                GROUP BY p.id
            """, (normalized_name,))
            
            row = cursor.fetchone()
            if row:
                return self._parse_provider_row(row)
            
            return None
        except Exception as e:
            print(f"Error getting provider by name: {str(e)}")
            return None
    
    def _parse_provider_row(self, row) -> Dict[str, Any]:
        """Parse database row into provider configuration"""
        provider_config = {
            'id': row[0],
            'name': row[1],
            'api_endpoint': row[2],
            'api_key': row[3],
            'default_model': row[4],
            'auth_method': row[5],
            'is_active': bool(row[6]),
            'created_at': row[7],
            'updated_at': row[8],
            'api_standard': row[9] if len(row) > 9 else 'openai',
            'supported_models': row[10] if len(row) > 10 else '{}',
            'model_mapping': row[11] if len(row) > 11 else '{}',
            'headers': {}
        }
        
        # Parse headers
        if len(row) > 12 and row[12]:  # headers column
            headers_list = row[12].split(',')
            for header_pair in headers_list:
                if ':' in header_pair:
                    key, value = header_pair.split(':', 1)
                    provider_config['headers'][key] = value
        
        # Parse model mapping
        try:
            if provider_config['model_mapping']:
                provider_config['model_mapping'] = json.loads(provider_config['model_mapping'])
            else:
                provider_config['model_mapping'] = {}
        except json.JSONDecodeError:
            provider_config['model_mapping'] = {}
        
        # Parse supported models
        try:
            if provider_config['supported_models']:
                provider_config['supported_models'] = json.loads(provider_config['supported_models'])
            else:
                provider_config['supported_models'] = {}
        except json.JSONDecodeError:
            provider_config['supported_models'] = {}
        
        return provider_config
    
    def create_provider_instance(self, provider_config: Dict[str, Any]):
        """Create a provider instance from configuration"""
        try:
            # Get provider key from name
            provider_key = self.provider_registry.normalize_provider_name(provider_config['name'])
            
            # Get provider class
            provider_class = self.provider_registry.get_provider_class(provider_key)
            if not provider_class:
                raise Exception(f"Provider {provider_key} not found in registry")
            
            # Create instance
            provider_instance = provider_class(provider_config)
            return provider_instance
            
        except Exception as e:
            print(f"Error creating provider instance: {str(e)}")
            return None
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get information about all available providers"""
        providers = self.load_all_providers()
        provider_info = self.provider_registry.get_provider_info()
        
        result = []
        for provider in providers:
            provider_key = self.provider_registry.normalize_provider_name(provider['name'])
            if provider_key in provider_info:
                provider_with_endpoints = provider.copy()
                provider_with_endpoints['endpoints'] = provider_info[provider_key]['endpoints']
                result.append(provider_with_endpoints)
        
        return result
    
    def get_provider_endpoints(self, provider_name: str) -> Dict[str, str]:
        """Get endpoints for a specific provider"""
        provider_key = self.provider_registry.normalize_provider_name(provider_name)
        return self.provider_registry.get_provider_endpoints(provider_key)
    
    def get_all_endpoints(self) -> List[Dict[str, str]]:
        """Get all available endpoints with their descriptions"""
        providers = self.load_all_providers()
        endpoints = []
        
        for provider in providers:
            provider_key = self.provider_registry.normalize_provider_name(provider['name'])
            provider_endpoints = self.provider_registry.get_provider_endpoints(provider_key)
            
            # Standard endpoint
            endpoints.append({
                'endpoint': provider_endpoints.get('standard', f'/v1/messages/{provider_key}'),
                'description': f"{provider['name']} with standard prompt",
                'provider': provider['name'],
                'custom_prompt': False
            })
            
            # Custom endpoint
            endpoints.append({
                'endpoint': provider_endpoints.get('custom', f'/v1/messages/{provider_key}-custom'),
                'description': f"{provider['name']} with custom prompt",
                'provider': provider['name'],
                'custom_prompt': True
            })
        
        return endpoints
    
    def is_valid_provider(self, provider_name: str) -> bool:
        """Check if a provider name is valid"""
        return self.provider_registry.is_valid_provider(provider_name)
    
    def normalize_provider_name(self, provider_name: str) -> str:
        """Normalize provider name to match registry key"""
        return self.provider_registry.normalize_provider_name(provider_name)
    
    def get_model_mapping(self, provider_name: str, model_name: str) -> Optional[str]:
        """
        Get mapped model name for a provider
        
        Args:
            provider_name: Name of the provider
            model_name: Original model name (e.g., claude-3-5-sonnet-20241022)
            
        Returns:
            Mapped model name or None if not found
        """
        provider = self.get_provider_by_name(provider_name)
        if not provider:
            return None
            
        model_mapping = provider.get('model_mapping', {})
        if not model_mapping:
            return None
            
        # Try exact match first
        if model_name in model_mapping:
            return model_mapping[model_name]
            
        # Try normalized model name
        normalized_model = model_name.lower().replace(' ', '-').replace('_', '-')
        if normalized_model in model_mapping:
            return model_mapping[normalized_model]
            
        # Try simplified model name
        if '-' in normalized_model:
            simplified_model = normalized_model.split('-')[0]
            if simplified_model in model_mapping:
                return model_mapping[simplified_model]
                
        return None
    
    def get_predefined_headers(self, provider_name: str) -> Dict[str, str]:
        """
        Get predefined headers for a provider based on its API standard
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Dictionary of predefined headers
        """
        provider = self.get_provider_by_name(provider_name)
        if not provider:
            return {}
            
        api_standard = provider.get('api_standard', 'openai').lower()
        
        # Predefined headers for different API standards
        predefined_headers = {
            'anthropic': {
                'anthropic-version': '2023-06-01',
                'anthropic-dangerous-direct-browser-access': 'true'
            },
            'openai': {
                'OpenAI-Organization': '',
                'OpenAI-Project': ''
            },
            'grok': {
                'X-API-Key': ''
            }
        }
        
        return predefined_headers.get(api_standard, {})

# Global instance
provider_loader = DynamicProviderLoader(db_manager, ProviderRegistry())