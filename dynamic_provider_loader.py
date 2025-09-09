"""
Dynamic provider loader with endpoint support
"""

from typing import Dict, Any, Optional, List
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
            'headers': {}
        }
        
        # Parse headers
        if row[9]:  # headers column
            headers_list = row[9].split(',')
            for header_pair in headers_list:
                if ':' in header_pair:
                    key, value = header_pair.split(':', 1)
                    provider_config['headers'][key] = value
        
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
        """Get list of available providers with their endpoints"""
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

# Global instance is created in app.py