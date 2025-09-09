#!/usr/bin/env python3
"""
Database Initialization Script
Initializes the database with default providers and settings
"""

import sys
import os
import json
import sqlite3

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import db_manager

def initialize_database():
    """Initialize database with default providers and settings"""
    print("Initializing database with default providers and settings...")
    
    try:
        # Get database connection
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Create default providers if they don't exist
        default_providers = [
            {
                'name': 'OpenRouter',
                'api_endpoint': 'https://openrouter.ai/api/v1',
                'api_key': '',
                'default_model': 'openai/gpt-3.5-turbo',
                'auth_method': 'bearer_token',
                'is_active': False,
                'api_standard': 'openai',
                'supported_models': '{}',
                'model_mapping': json.dumps({
                    'claude-3-haiku-20240307': 'openai/gpt-4o-mini',
                    'claude-3-5-sonnet-20241022': 'openai/gpt-4o',
                    'claude-3-opus-20240229': 'anthropic/claude-3-opus'
                })
            },
            {
                'name': 'Chutes',
                'api_endpoint': 'http://llm.chutes.ai/api/v1',  # Corrected endpoint
                'api_key': '',
                'default_model': 'chutes/default-model',
                'auth_method': 'bearer_token',
                'is_active': False,
                'api_standard': 'openai',
                'supported_models': '{}',
                'model_mapping': json.dumps({
                    'claude-3-haiku-20240307': 'chutes/glm-4.5',
                    'claude-3-5-sonnet-20241022': 'chutes/kimi-k2',
                    'claude-3-opus-20240229': 'chutes/deepseek'
                })
            },
            {
                'name': 'Synthetic',
                'api_endpoint': 'https://api.synthetic.new/v1',
                'api_key': '',
                'default_model': 'synthetic/default-model',
                'auth_method': 'bearer_token',
                'is_active': False,
                'api_standard': 'openai',
                'supported_models': '{}',
                'model_mapping': json.dumps({
                    'claude-3-haiku-20240307': 'synthetic/qwen-3-235b',
                    'claude-3-5-sonnet-20241022': 'synthetic/glm-4.5',
                    'claude-3-opus-20240229': 'synthetic/kimi-k2'
                })
            },
            {
                'name': 'AIML',
                'api_endpoint': 'https://api.aimlapi.com/v1',
                'api_key': '',
                'default_model': 'deepseek/deepseek-r1',
                'auth_method': 'bearer_token',
                'is_active': False,
                'api_standard': 'openai',
                'supported_models': '{}',
                'model_mapping': json.dumps({
                    'claude-3-haiku-20240307': 'deepseek/deepseek-r1',
                    'claude-3-5-sonnet-20241022': 'anthropic/claude-4-sonnet',
                    'claude-3-opus-20240229': 'google/gemini-2.5-pro'
                })
            },
            {
                'name': 'Grok (Direct)',
                'api_endpoint': 'https://api.x.ai/v1',
                'api_key': '',
                'default_model': 'grok-4',
                'auth_method': 'bearer_token',
                'is_active': False,
                'api_standard': 'anthropic',  # Grok Direct uses Anthropic format
                'supported_models': '{}',
                'model_mapping': json.dumps({
                    'claude-3-haiku-20240307': 'grok-4',
                    'claude-3-5-sonnet-20241022': 'grok-4',
                    'claude-3-opus-20240229': 'grok-4'
                })
            },
            {
                'name': 'Grok (OpenAI)',
                'api_endpoint': 'https://api.x.ai/v1',
                'api_key': '',
                'default_model': 'grok-4',
                'auth_method': 'bearer_token',
                'is_active': False,
                'api_standard': 'openai',  # Grok OpenAI uses OpenAI format
                'supported_models': '{}',
                'model_mapping': json.dumps({
                    'claude-3-haiku-20240307': 'grok-4',
                    'claude-3-5-sonnet-20241022': 'grok-4',
                    'claude-3-opus-20240229': 'grok-4'
                })
            }
        ]
        
        # Insert default providers
        for provider in default_providers:
            cursor.execute("SELECT COUNT(*) FROM providers WHERE name = ?", (provider['name'],))
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO providers 
                    (name, api_endpoint, api_key, default_model, auth_method, is_active,
                     api_standard, supported_models, model_mapping)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    provider['name'],
                    provider['api_endpoint'],
                    provider['api_key'],
                    provider['default_model'],
                    provider['auth_method'],
                    provider['is_active'],
                    provider['api_standard'],
                    provider['supported_models'],
                    provider['model_mapping']
                ))
                print(f"✅ Added default provider: {provider['name']}")
        
        # Ensure default app settings exist
        cursor.execute("SELECT COUNT(*) FROM app_settings WHERE id = 1")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO app_settings 
                (server_port, server_host, enable_full_logging, log_directory, 
                 enable_streaming, request_timeout, require_auth, secret_key,
                 rate_limit_enabled, rate_limit_requests, rate_limit_window)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (8000, '127.0.0.1', True, 'logs', True, 300, True, 'dev-secret-key', True, 100, 3600))
            print("✅ Created default app settings")
        
        # Ensure default prompt config exists
        cursor.execute("SELECT COUNT(*) FROM prompt_config WHERE id = 1")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO prompt_config 
                (use_custom_prompt, system_name, remove_ai_references, 
                 remove_defensive_restrictions)
                VALUES (?, ?, ?, ?)
            """, (False, 'AI Assistant', False, False))
            print("✅ Created default prompt configuration")
        
        # Ensure default admin user exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            # Import auth manager to create default admin
            from security.auth_manager import auth_manager
            print("✅ Created default admin user")
        
        conn.commit()
        print("\n🎉 Database initialization completed successfully!")
        print("📝 Default providers added:")
        for provider in default_providers:
            print(f"   • {provider['name']}")
        print("\n🔐 Default admin user created (username: admin, password: admin123)")
        print("⚠️  IMPORTANT: Change the default admin password after first login!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = initialize_database()
    if not success:
        sys.exit(1)