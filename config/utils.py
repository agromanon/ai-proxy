"""
Database utilities and helpers
"""

import sqlite3
import os
import json
from typing import List, Dict, Any, Optional
from config.database import db_manager

class DatabaseUtils:
    """Utility functions for database operations"""
    
    @staticmethod
    def get_all_providers() -> List[Dict[str, Any]]:
        """Get all providers with their headers"""
        conn = db_manager.get_connection()
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
            if row[12] if len(row) > 12 else row[9]:  # headers column
                headers_list = (row[12] if len(row) > 12 else row[9]).split(',')
                for header_pair in headers_list:
                    if ':' in header_pair:
                        key, value = header_pair.split(':', 1)
                        provider_config['headers'][key] = value
            
            providers.append(provider_config)
        
        return providers
    
    @staticmethod
    def get_provider_by_id(provider_id: int) -> Optional[Dict[str, Any]]:
        """Get provider by ID"""
        conn = db_manager.get_connection()
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
            if row[12] if len(row) > 12 else row[9]:  # headers column
                headers_list = (row[12] if len(row) > 12 else row[9]).split(',')
                for header_pair in headers_list:
                    if ':' in header_pair:
                        key, value = header_pair.split(':', 1)
                        provider_config['headers'][key] = value
            
            return provider_config
        
        return None
    
    @staticmethod
    def get_provider_by_name(provider_name: str) -> Optional[Dict[str, Any]]:
        """Get provider by name"""
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.*, 
                   GROUP_CONCAT(ph.header_key || ':' || ph.header_value) as headers
            FROM providers p
            LEFT JOIN provider_headers ph ON p.id = ph.provider_id
            WHERE p.name = ?
            GROUP BY p.id
        """, (provider_name,))
        
        row = cursor.fetchone()
        if row:
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
            if row[12] if len(row) > 12 else row[9]:  # headers column
                headers_list = (row[12] if len(row) > 12 else row[9]).split(',')
                for header_pair in headers_list:
                    if ':' in header_pair:
                        key, value = header_pair.split(':', 1)
                        provider_config['headers'][key] = value
            
            return provider_config
        
        return None
    
    @staticmethod
    def get_app_settings() -> Dict[str, Any]:
        """Get application settings"""
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM app_settings WHERE id = 1")
        row = cursor.fetchone()
        
        if row:
            return {
                'id': row[0],
                'server_port': row[1],
                'server_host': row[2],
                'enable_full_logging': bool(row[3]),
                'log_directory': row[4],
                'enable_streaming': bool(row[5]),
                'request_timeout': row[6],
                'require_auth': bool(row[7]),
                'secret_key': row[8],
                'session_cookie_secure': bool(row[9]),
                'rate_limit_enabled': bool(row[10]),
                'rate_limit_requests': row[11],
                'rate_limit_window': row[12],
                'created_at': row[13],
                'updated_at': row[14]
            }
        
        # Return defaults if no settings found
        return {
            'server_port': 8000,
            'server_host': '127.0.0.1',
            'enable_full_logging': True,
            'log_directory': 'logs',
            'enable_streaming': True,
            'request_timeout': 300,
            'require_auth': True,
            'secret_key': 'dev-secret-key',
            'session_cookie_secure': False,
            'rate_limit_enabled': True,
            'rate_limit_requests': 100,
            'rate_limit_window': 3600
        }
    
    @staticmethod
    def update_app_settings(settings: Dict[str, Any]) -> bool:
        """Update application settings"""
        try:
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            
            # Build update query
            update_fields = []
            update_values = []
            
            for key, value in settings.items():
                if key in ['server_port', 'server_host', 'enable_full_logging', 
                          'log_directory', 'enable_streaming', 'request_timeout',
                          'require_auth', 'secret_key', 'session_cookie_secure',
                          'rate_limit_enabled', 'rate_limit_requests', 'rate_limit_window']:
                    update_fields.append(f"{key} = ?")
                    update_values.append(value)
            
            if update_fields:
                query = f"UPDATE app_settings SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = 1"
                cursor.execute(query, update_values)
                conn.commit()
                return True
            
            return False
        except Exception as e:
            print(f"Error updating app settings: {e}")
            return False
    
    @staticmethod
    def get_prompt_config() -> Dict[str, Any]:
        """Get prompt configuration"""
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM prompt_config WHERE id = 1")
        row = cursor.fetchone()
        
        if row:
            return {
                'id': row[0],
                'use_custom_prompt': bool(row[1]),
                'prompt_template': row[2],
                'system_name': row[3],
                'model_name_override': row[4],
                'remove_ai_references': bool(row[5]),
                'remove_defensive_restrictions': bool(row[6]),
                'created_at': row[7],
                'updated_at': row[8]
            }
        
        # Return defaults if no config found
        return {
            'use_custom_prompt': False,
            'prompt_template': None,
            'system_name': 'AI Assistant',
            'model_name_override': None,
            'remove_ai_references': False,
            'remove_defensive_restrictions': False
        }
    
    @staticmethod
    def update_prompt_config(config: Dict[str, Any]) -> bool:
        """Update prompt configuration"""
        try:
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            
            # Build update query
            update_fields = []
            update_values = []
            
            for key, value in config.items():
                if key in ['use_custom_prompt', 'prompt_template', 'system_name',
                          'model_name_override', 'remove_ai_references', 
                          'remove_defensive_restrictions']:
                    update_fields.append(f"{key} = ?")
                    update_values.append(value)
            
            if update_fields:
                query = f"UPDATE prompt_config SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = 1"
                cursor.execute(query, update_values)
                conn.commit()
                return True
            
            return False
        except Exception as e:
            print(f"Error updating prompt config: {e}")
            return False
    
    @staticmethod
    def log_request(request_data: Dict[str, Any]) -> Optional[int]:
        """Log a request to the database"""
        try:
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO request_logs 
                (request_id, provider_name, model_used, request_data, response_data, 
                 status_code, duration_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                request_data['request_id'],
                request_data.get('provider_name'),
                request_data.get('model_used'),
                request_data.get('request_data'),
                request_data.get('response_data'),
                request_data.get('status_code'),
                request_data.get('duration_ms')
            ))
            
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error logging request: {str(e)}")
            return None

# Global instance
db_utils = DatabaseUtils()