#!/usr/bin/env python3
"""
Script to update database schema with model mapping and API standard fields
"""

import sqlite3

def update_database_schema():
    """Update database schema with new fields"""
    try:
        # Connect to database
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        
        # Add model_mapping column to providers table (if it doesn't exist)
        try:
            cursor.execute("ALTER TABLE providers ADD COLUMN model_mapping TEXT")
            print("✅ Added model_mapping column to providers table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️  model_mapping column already exists")
            else:
                print(f"ℹ️  Column may already exist: {e}")
        
        # Add api_standard column to providers table (if it doesn't exist)
        try:
            cursor.execute("ALTER TABLE providers ADD COLUMN api_standard TEXT DEFAULT 'openai'")
            print("✅ Added api_standard column to providers table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️  api_standard column already exists")
            else:
                print(f"ℹ️  Column may already exist: {e}")
        
        # Add supported_models column to providers table (if it doesn't exist)
        try:
            cursor.execute("ALTER TABLE providers ADD COLUMN supported_models TEXT")
            print("✅ Added supported_models column to providers table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️  supported_models column already exists")
            else:
                print(f"ℹ️  Column may already exist: {e}")
        
        # Update existing providers with default API standards
        api_standards = {
            'Grok (Direct)': 'anthropic',
            'Grok (OpenAI)': 'openai',
            'OpenRouter': 'openai',
            'Chutes': 'openai',
            'Synthetic': 'openai',
            'AIML': 'openai'
        }
        
        for provider_name, api_standard in api_standards.items():
            cursor.execute("""
                UPDATE providers 
                SET api_standard = ?
                WHERE name = ?
            """, (api_standard, provider_name))
            if cursor.rowcount > 0:
                print(f"✅ Updated {provider_name} API standard to {api_standard}")
        
        conn.commit()
        print("\n🎉 Database schema updated successfully!")
        
    except Exception as e:
        print(f"❌ Error updating database schema: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()
    
    return True

if __name__ == "__main__":
    update_database_schema()