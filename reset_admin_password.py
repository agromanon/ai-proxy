#!/usr/bin/env python3
"""
Script to reset admin password
"""

import sys
import os
import sqlite3
import bcrypt

def reset_admin_password(new_password="admin123"):
    """Reset admin password"""
    try:
        # Connect to database
        conn = sqlite3.connect('app.db')
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
            print(f"✅ Admin password reset successfully!")
            print(f"📝 New credentials:")
            print(f"   Username: admin")
            print(f"   Password: {new_password}")
            print(f"⚠️  IMPORTANT: Change this password immediately after logging in!")
            return True
        else:
            print("❌ Failed to reset admin password")
            return False
            
    except Exception as e:
        print(f"❌ Error resetting admin password: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # Default password
    new_password = "admin123"
    
    # Check if password was provided as argument
    if len(sys.argv) > 1:
        new_password = sys.argv[1]
    
    reset_admin_password(new_password)