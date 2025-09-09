#!/usr/bin/env python3
"""
Reset admin password script
"""

import sys
import os
import bcrypt
import secrets

# Add the current directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import db_manager

def reset_admin_password(new_password: str = "admin123") -> bool:
    """
    Reset the admin password
    
    Args:
        new_password: New password for the admin user
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Connect to database
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Hash the new password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)
        
        # Update admin password
        cursor.execute("""
            UPDATE users 
            SET password_hash = ? 
            WHERE username = 'admin'
        """, (hashed_password.decode('utf-8'),))
        
        # Check if update was successful
        if cursor.rowcount > 0:
            conn.commit()
            print("✅ Admin password reset successfully!")
            print(f"📝 New credentials:")
            print(f"   Username: admin")
            print(f"   Password: {new_password}")
            print("⚠️  IMPORTANT: Change this password immediately after logging in!")
            return True
        else:
            print("❌ Admin user not found")
            return False
            
    except Exception as e:
        print(f"❌ Error resetting admin password: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def generate_secure_admin_password() -> str:
    """
    Generate a secure admin password
    
    Returns:
        Secure password string
    """
    return secrets.token_urlsafe(16)

if __name__ == "__main__":
    # Default password
    new_password = "admin123"
    
    # Check if password was provided as argument
    if len(sys.argv) > 1:
        new_password = sys.argv[1]
    
    # Reset admin password
    success = reset_admin_password(new_password)
    
    if not success:
        sys.exit(1)