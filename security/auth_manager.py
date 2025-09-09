"""
Authentication Manager for Local and Cloud Deployments
"""

import bcrypt
import secrets
import datetime
from typing import Optional, Dict, Any
from config.database import db_manager

class AuthManager:
    """Manage user authentication and authorization"""
    
    def __init__(self):
        self.db = db_manager
        self._ensure_default_admin()
    
    def _ensure_default_admin(self):
        """Ensure default admin user exists"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            # Create default admin with known password
            default_password = "admin123"
            password_hash = self._hash_password(default_password)
            
            cursor.execute("""
                INSERT INTO users (username, password_hash, is_admin)
                VALUES (?, ?, ?)
            """, ('admin', password_hash, True))
            
            conn.commit()
            
            print("Default admin user created!")
            print("Username: admin")
            print("Password: admin123")
            print("IMPORTANT: Change this password after first login!")
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user
        
        Args:
            username: Username
            password: Password
            
        Returns:
            User info dict or None if authentication fails
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, password_hash, is_admin
                FROM users
                WHERE username = ?
            """, (username,))
            
            user = cursor.fetchone()
            if user and self._verify_password(password, user[2]):
                # Update last login
                cursor.execute("""
                    UPDATE users
                    SET last_login = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (user[0],))
                conn.commit()
                
                return {
                    'id': user[0],
                    'username': user[1],
                    'is_admin': bool(user[3])
                }
            
            return None
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None
    
    def create_user(self, username: str, password: str, is_admin: bool = False) -> Optional[int]:
        """
        Create a new user
        
        Args:
            username: Username
            password: Password
            is_admin: Whether user has admin privileges
            
        Returns:
            User ID or None if creation fails
        """
        try:
            password_hash = self._hash_password(password)
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO users (username, password_hash, is_admin)
                VALUES (?, ?, ?)
            """, (username, password_hash, is_admin))
            
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def update_user_password(self, user_id: int, new_password: str) -> bool:
        """
        Update a user's password
        
        Args:
            user_id: User ID
            new_password: New password
            
        Returns:
            True if successful, False otherwise
        """
        try:
            password_hash = self._hash_password(new_password)
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users
                SET password_hash = ?
                WHERE id = ?
            """, (password_hash, user_id))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating user password: {e}")
            return False
    
    def user_exists(self, username: str) -> bool:
        """
        Check if a user exists
        
        Args:
            username: Username to check
            
        Returns:
            True if user exists, False otherwise
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
            return cursor.fetchone()[0] > 0
        except Exception as e:
            print(f"Error checking user existence: {e}")
            return False

class APIKeyManager:
    """Manage API keys for programmatic access"""
    
    def __init__(self):
        self.db = db_manager
    
    def generate_api_key(self, user_id: int, name: str = "API Key", expires_days: int = 365) -> Optional[str]:
        """
        Generate a new API key
        
        Args:
            user_id: User ID
            name: Key name
            expires_days: Days until expiration (0 for no expiration)
            
        Returns:
            API key string or None if generation fails
        """
        try:
            api_key = secrets.token_urlsafe(32)
            
            # Calculate expiration
            expires_at = None
            if expires_days > 0:
                expires_at = datetime.datetime.now() + datetime.timedelta(days=expires_days)
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO api_keys (key, user_id, name, expires_at)
                VALUES (?, ?, ?, ?)
            """, (api_key, user_id, name, expires_at))
            
            conn.commit()
            return api_key
        except Exception as e:
            print(f"Error generating API key: {e}")
            return None
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Validate an API key
        
        Args:
            api_key: API key to validate
            
        Returns:
            User info dict or None if invalid
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT u.id, u.username, u.is_admin
                FROM api_keys ak
                JOIN users u ON ak.user_id = u.id
                WHERE ak.key = ? AND ak.is_active = 1
                AND (ak.expires_at IS NULL OR ak.expires_at > CURRENT_TIMESTAMP)
            """, (api_key,))
            
            user = cursor.fetchone()
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'is_admin': bool(user[2])
                }
            
            return None
        except Exception as e:
            print(f"Error validating API key: {e}")
            return None
    
    def revoke_api_key(self, key_id: int, user_id: int) -> bool:
        """
        Revoke an API key
        
        Args:
            key_id: Key ID
            user_id: User ID (for authorization)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE api_keys
                SET is_active = 0
                WHERE id = ? AND user_id = ?
            """, (key_id, user_id))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error revoking API key: {e}")
            return False

class SessionManager:
    """Manage user sessions"""
    
    def __init__(self):
        self.db = db_manager
    
    def create_session(self, user_id: int, ip_address: str = None, user_agent: str = None) -> Optional[str]:
        """
        Create a new user session
        
        Args:
            user_id: User ID
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Session token or None if creation fails
        """
        try:
            session_token = secrets.token_urlsafe(32)
            
            # Set expiration (24 hours)
            expires_at = datetime.datetime.now() + datetime.timedelta(hours=24)
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_sessions (session_token, user_id, ip_address, user_agent, expires_at)
                VALUES (?, ?, ?, ?, ?)
            """, (session_token, user_id, ip_address, user_agent, expires_at))
            
            conn.commit()
            return session_token
        except Exception as e:
            print(f"Error creating session: {e}")
            return None
    
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """
        Validate a user session
        
        Args:
            session_token: Session token to validate
            
        Returns:
            User info dict or None if invalid
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT u.id, u.username, u.is_admin
                FROM user_sessions us
                JOIN users u ON us.user_id = u.id
                WHERE us.session_token = ?
                AND us.expires_at > CURRENT_TIMESTAMP
            """, (session_token,))
            
            user = cursor.fetchone()
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'is_admin': bool(user[2])
                }
            
            return None
        except Exception as e:
            print(f"Error validating session: {e}")
            return None
    
    def destroy_session(self, session_token: str) -> bool:
        """
        Destroy a user session
        
        Args:
            session_token: Session token to destroy
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM user_sessions WHERE session_token = ?", (session_token,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error destroying session: {e}")
            return False

# Global instances
auth_manager = AuthManager()
api_key_manager = APIKeyManager()
session_manager = SessionManager()