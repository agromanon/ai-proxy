#!/usr/bin/env python3
"""
Test script to verify AI Proxy installation
"""

import sys
import os
import subprocess
import tempfile
import shutil

def test_import():
    """Test if the package can be imported"""
    try:
        import app
        print("✅ Package can be imported")
        return True
    except ImportError as e:
        print(f"❌ Failed to import package: {e}")
        return False

def test_dependencies():
    """Test if dependencies are installed"""
    try:
        import flask
        import requests
        import bcrypt
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def test_database_creation():
    """Test if database can be created"""
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        
        # Set environment variable for database path
        os.environ["DATABASE_PATH"] = db_path
        
        # Import and initialize database
        from config.database import db_manager
        
        # Get connection
        conn = db_manager.get_connection()
        
        # Test basic operations
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        cursor.execute("INSERT INTO test (name) VALUES (?)", ("test",))
        conn.commit()
        
        # Clean up
        shutil.rmtree(temp_dir)
        print("✅ Database creation and operations work")
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_provider_discovery():
    """Test if providers can be discovered"""
    try:
        from provider_registry import ProviderRegistry
        registry = ProviderRegistry()
        
        providers = registry.get_provider_info()
        if len(providers) > 0:
            print(f"✅ Provider discovery works ({len(providers)} providers found)")
            return True
        else:
            print("❌ No providers found")
            return False
    except Exception as e:
        print(f"❌ Provider discovery failed: {e}")
        return False

def main():
    """Run all tests"""
    print("AI Proxy Installation Test")
    print("=" * 40)
    
    tests = [
        test_import,
        test_dependencies,
        test_database_creation,
        test_provider_discovery
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 40)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Installation is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)