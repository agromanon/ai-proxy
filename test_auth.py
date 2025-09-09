#!/usr/bin/env python3
"""
Test authentication script
"""

import sys
import os

# Add the current directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from security.auth_manager import auth_manager

def test_authentication(username: str, password: str) -> bool:
    """
    Test user authentication
    
    Args:
        username: Username to test
        password: Password to test
        
    Returns:
        True if authentication successful, False otherwise
    """
    try:
        user = auth_manager.authenticate_user(username, password)
        if user:
            print(f"✅ Authentication successful!")
            print(f"   User ID: {user['id']}")
            print(f"   Username: {user['username']}")
            print(f"   Is Admin: {user['is_admin']}")
            return True
        else:
            print("❌ Authentication failed!")
            return False
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
        return False

if __name__ == "__main__":
    # Test default admin credentials
    print("Testing default admin credentials...")
    test_authentication("admin", "admin123")
    
    print("\nTesting invalid credentials...")
    test_authentication("admin", "wrongpassword")