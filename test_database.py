#!/usr/bin/env python3
"""
Test database initialization
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import db_manager
from initialize_database import initialize_database

def test_database_initialization():
    """Test database initialization"""
    print("Testing database initialization...")
    
    try:
        # Initialize database
        success = initialize_database()
        
        if success:
            print("✅ Database initialization test passed")
            
            # Test that providers were created
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM providers")
            provider_count = cursor.fetchone()[0]
            print(f"✅ Found {provider_count} providers in database")
            
            cursor.execute("SELECT name FROM providers ORDER BY name")
            providers = cursor.fetchall()
            print("✅ Providers in database:")
            for provider in providers:
                print(f"   • {provider[0]}")
            
            return True
        else:
            print("❌ Database initialization test failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing database initialization: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database_initialization()
    sys.exit(0 if success else 1)