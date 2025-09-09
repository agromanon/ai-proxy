#!/usr/bin/env python3
"""
Script to initialize pre-configured providers in the database
"""

import sqlite3
import json

def initialize_providers():
    """Initialize pre-configured providers"""
    # Provider configurations
    providers = [
        {
            'name': 'Grok (Direct)',
            'api_endpoint': 'https://api.x.ai/v1',
            'api_key': '',
            'default_model': 'grok-4',
            'auth_method': 'bearer_token',
            'is_active': False
        },
        {
            'name': 'Grok (OpenAI)',
            'api_endpoint': 'https://api.x.ai/v1',
            'api_key': '',
            'default_model': 'grok-4',
            'auth_method': 'bearer_token',
            'is_active': False
        },
        {
            'name': 'OpenRouter',
            'api_endpoint': 'https://openrouter.ai/api/v1',
            'api_key': '',
            'default_model': 'openai/gpt-4o',
            'auth_method': 'bearer_token',
            'is_active': False
        },
        {
            'name': 'Chutes',
            'api_endpoint': 'http://llm.chutes.ai/api/v1',
            'api_key': '',
            'default_model': 'chutes/default-model',
            'auth_method': 'bearer_token',
            'is_active': False
        },
        {
            'name': 'Synthetic',
            'api_endpoint': 'https://api.synthetic.new/v1',
            'api_key': '',
            'default_model': 'synthetic/default-model',
            'auth_method': 'bearer_token',
            'is_active': False
        },
        {
            'name': 'AIML',
            'api_endpoint': 'https://api.aimlapi.com/v1',
            'api_key': '',
            'default_model': 'deepseek/deepseek-r1',
            'auth_method': 'bearer_token',
            'is_active': False
        }
    ]
    
    try:
        # Connect to database
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        
        # Insert providers if they don't already exist
        for provider in providers:
            cursor.execute("""
                SELECT COUNT(*) FROM providers WHERE name = ?
            """, (provider['name'],))
            
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO providers 
                    (name, api_endpoint, api_key, default_model, auth_method, is_active)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    provider['name'],
                    provider['api_endpoint'],
                    provider['api_key'],
                    provider['default_model'],
                    provider['auth_method'],
                    provider['is_active']
                ))
                print(f"✅ Added provider: {provider['name']}")
            else:
                print(f"ℹ️  Provider already exists: {provider['name']}")
        
        conn.commit()
        print(f"\n🎉 Successfully initialized {len(providers)} providers!")
        print("📝 To configure API keys:")
        print("   1. Access the web interface at http://localhost:8000")
        print("   2. Log in with admin/admin123")
        print("   3. Go to the 'Providers' section")
        print("   4. Edit each provider to add your API keys")
        print("   5. Activate one provider as your default")
        
    except Exception as e:
        print(f"❌ Error initializing providers: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()
    
    return True

if __name__ == "__main__":
    initialize_providers()