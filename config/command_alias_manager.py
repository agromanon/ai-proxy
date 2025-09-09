"""
Command Alias Manager for Custom Provider Commands
"""

from config.database import db_manager
from typing import Dict, List, Optional

class CommandAliasManager:
    """Manage custom command aliases for providers"""
    
    def __init__(self):
        self.db = db_manager
        self._create_table()
    
    def _create_table(self):
        """Create command aliases table if it doesn't exist"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
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
            
            conn.commit()
        except Exception as e:
            print(f"Error creating command aliases table: {str(e)}")
    
    def set_alias(self, provider_id: int, alias_type: str, command_alias: str) -> bool:
        """
        Set a command alias for a provider
        
        Args:
            provider_id: Provider ID
            alias_type: Type of alias ('standard' or 'custom')
            command_alias: The command alias to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Insert or update alias
            cursor.execute("""
                INSERT OR REPLACE INTO command_aliases 
                (provider_id, alias_type, command_alias, is_active, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (provider_id, alias_type, command_alias, True))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error setting command alias: {str(e)}")
            return False
    
    def get_alias(self, provider_id: int, alias_type: str) -> Optional[str]:
        """
        Get a command alias for a provider
        
        Args:
            provider_id: Provider ID
            alias_type: Type of alias ('standard' or 'custom')
            
        Returns:
            Command alias or None if not found
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT command_alias FROM command_aliases
                WHERE provider_id = ? AND alias_type = ? AND is_active = 1
            """, (provider_id, alias_type))
            
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            print(f"Error getting command alias: {str(e)}")
            return None
    
    def get_provider_by_alias(self, command_alias: str) -> Optional[Dict[str, any]]:
        """
        Get provider information by command alias
        
        Args:
            command_alias: Command alias to look up
            
        Returns:
            Provider information or None if not found
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT p.*, ca.alias_type FROM command_aliases ca
                JOIN providers p ON ca.provider_id = p.id
                WHERE ca.command_alias = ? AND ca.is_active = 1
            """, (command_alias,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'api_endpoint': row[2],
                    'api_key': row[3],
                    'default_model': row[4],
                    'auth_method': row[5],
                    'is_active': bool(row[6]),
                    'alias_type': row[8]  # alias_type from join
                }
            return None
        except Exception as e:
            print(f"Error getting provider by alias: {str(e)}")
            return None
    
    def get_all_aliases(self, provider_id: int = None) -> List[Dict[str, any]]:
        """
        Get all command aliases, optionally filtered by provider
        
        Args:
            provider_id: Optional provider ID to filter by
            
        Returns:
            List of command aliases
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            if provider_id:
                cursor.execute("""
                    SELECT ca.*, p.name as provider_name FROM command_aliases ca
                    JOIN providers p ON ca.provider_id = p.id
                    WHERE ca.provider_id = ? AND ca.is_active = 1
                    ORDER BY ca.alias_type
                """, (provider_id,))
            else:
                cursor.execute("""
                    SELECT ca.*, p.name as provider_name FROM command_aliases ca
                    JOIN providers p ON ca.provider_id = p.id
                    WHERE ca.is_active = 1
                    ORDER BY p.name, ca.alias_type
                """)
            
            aliases = []
            for row in cursor.fetchall():
                aliases.append({
                    'id': row[0],
                    'provider_id': row[1],
                    'alias_type': row[2],
                    'command_alias': row[3],
                    'is_active': bool(row[4]),
                    'created_at': row[5],
                    'updated_at': row[6],
                    'provider_name': row[7]
                })
            
            return aliases
        except Exception as e:
            print(f"Error getting command aliases: {str(e)}")
            return []
    
    def remove_alias(self, provider_id: int, alias_type: str) -> bool:
        """
        Remove a command alias
        
        Args:
            provider_id: Provider ID
            alias_type: Type of alias to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM command_aliases
                WHERE provider_id = ? AND alias_type = ?
            """, (provider_id, alias_type))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error removing command alias: {str(e)}")
            return False
    
    def generate_default_alias(self, provider_name: str, alias_type: str) -> str:
        """
        Generate a default command alias for a provider
        
        Args:
            provider_name: Name of the provider
            alias_type: Type of alias ('standard' or 'custom')
            
        Returns:
            Generated command alias
        """
        # Normalize provider name
        normalized_name = provider_name.lower().replace(' ', '-').replace('_', '-')
        
        if alias_type == 'standard':
            return f"claude-{normalized_name}"
        elif alias_type == 'custom':
            return f"claude-{normalized_name}-custom"
        else:
            return f"claude-{normalized_name}"

# Global instance
command_alias_manager = CommandAliasManager()