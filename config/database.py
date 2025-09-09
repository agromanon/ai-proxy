"""
Embedded Database Manager using SQLite
"""

import sqlite3
import os
import threading
from pathlib import Path
from typing import Optional, Dict, Any

class DatabaseManager:
    """Thread-safe SQLite database manager"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, db_path: str = "app.db"):
        """Singleton pattern for database connection"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_path: str = "app.db"):
        """Initialize database manager"""
        if not self._initialized:
            self.db_path = db_path
            self.connection = None
            self._initialized = True
            self._local = threading.local()
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get thread-local database connection
        Creates connection if it doesn't exist
        """
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            # Create database directory if it doesn't exist
            db_dir = Path(self.db_path).parent
            if db_dir and not db_dir.exists():
                db_dir.mkdir(parents=True, exist_ok=True)
            
            # Create connection
            self._local.connection = sqlite3.connect(
                self.db_path, 
                check_same_thread=False,  # Allow sharing across threads with proper locking
                timeout=30.0  # 30 second timeout
            )
            self._local.connection.row_factory = sqlite3.Row
            self._local.connection.execute("PRAGMA foreign_keys = ON")
            
            # Initialize tables
            self._create_tables()
        
        return self._local.connection
    
    def _create_tables(self):
        """Create all required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Providers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS providers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                api_endpoint TEXT NOT NULL,
                api_key TEXT NOT NULL,
                default_model TEXT,
                auth_method TEXT DEFAULT 'bearer_token',
                is_active BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Provider headers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS provider_headers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider_id INTEGER NOT NULL,
                header_key TEXT NOT NULL,
                header_value TEXT NOT NULL,
                FOREIGN KEY (provider_id) REFERENCES providers (id) ON DELETE CASCADE
            )
        """)
        
        # Application settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                server_port INTEGER DEFAULT 8000,
                server_host TEXT DEFAULT '127.0.0.1',
                enable_full_logging BOOLEAN DEFAULT TRUE,
                log_directory TEXT DEFAULT 'logs',
                enable_streaming BOOLEAN DEFAULT TRUE,
                request_timeout INTEGER DEFAULT 300,
                require_auth BOOLEAN DEFAULT TRUE,
                secret_key TEXT,
                session_cookie_secure BOOLEAN DEFAULT FALSE,
                rate_limit_enabled BOOLEAN DEFAULT TRUE,
                rate_limit_requests INTEGER DEFAULT 100,
                rate_limit_window INTEGER DEFAULT 3600,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Prompt configuration table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompt_config (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                use_custom_prompt BOOLEAN DEFAULT FALSE,
                prompt_template TEXT,
                system_name TEXT,
                model_name_override TEXT,
                remove_ai_references BOOLEAN DEFAULT FALSE,
                remove_defensive_restrictions BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
        # API keys table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                user_id INTEGER,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_token TEXT UNIQUE NOT NULL,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Request logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS request_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT NOT NULL,
                provider_name TEXT,
                model_used TEXT,
                request_data TEXT,
                response_data TEXT,
                status_code INTEGER,
                duration_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Command aliases table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_aliases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider_id INTEGER NOT NULL,
                alias_type TEXT NOT NULL, -- 'standard' or 'custom'
                command_alias TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (provider_id) REFERENCES providers (id) ON DELETE CASCADE,
                UNIQUE(provider_id, alias_type)
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_command_aliases_provider 
            ON command_aliases(provider_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_command_aliases_alias 
            ON command_aliases(command_alias)
        """)
        
        # Create default records if they don't exist
        self._create_defaults(cursor)
        
        conn.commit()
    
    def _create_defaults(self, cursor):
        """Create default records"""
        # Default app settings
        cursor.execute("SELECT COUNT(*) FROM app_settings WHERE id = 1")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO app_settings 
                (server_port, server_host, enable_full_logging, log_directory, 
                 enable_streaming, request_timeout, require_auth, secret_key,
                 rate_limit_requests, rate_limit_window)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (8000, '127.0.0.1', True, 'logs', True, 300, True, 'dev-secret-key', 100, 3600))
        
        # Default prompt config
        cursor.execute("SELECT COUNT(*) FROM prompt_config WHERE id = 1")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO prompt_config 
                (use_custom_prompt, system_name, remove_ai_references, 
                 remove_defensive_restrictions)
                VALUES (?, ?, ?, ?)
            """, (False, 'AI Assistant', False, False))
        
        # Default admin user
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            # We'll create the admin user with a default password in the auth manager
            pass
    
    def close_connection(self):
        """Close database connection"""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
    
    def backup(self, backup_path: Optional[str] = None) -> str:
        """
        Create a backup of the database
        
        Args:
            backup_path: Path for backup file (optional)
            
        Returns:
            Path to backup file
        """
        if not backup_path:
            backup_path = f"{self.db_path}.backup.{int(datetime.now().timestamp())}"
        
        conn = self.get_connection()
        backup_conn = sqlite3.connect(backup_path)
        conn.backup(backup_conn)
        backup_conn.close()
        
        return backup_path
    
    def reset(self):
        """Reset database (for development/testing)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Drop all tables
        tables = [
            'request_logs', 'user_sessions', 'api_keys', 'users', 
            'prompt_config', 'app_settings', 'provider_headers', 'providers',
            'command_aliases'
        ]
        
        for table in tables:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
            except:
                pass
        
        conn.commit()
        self._create_tables()

# Global database manager instance
db_manager = DatabaseManager()