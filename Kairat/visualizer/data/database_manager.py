"""
Database manager component that handles all database operations.
"""

import sqlite3
import json
import os
from typing import Dict, List, Tuple, Optional


class DatabaseManager:
    """Handles all database operations for the visualizer."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_latest_state(self) -> Optional[Dict]:
        """Get the most recent game state from the database."""
        try:
            if not os.path.exists(self.db_path):
                return None
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if Areas table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Areas';")
            if not cursor.fetchone():
                conn.close()
                return None
                
            cursor.execute("""
                SELECT Date, Json 
                FROM Areas 
                ORDER BY Date DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
                
            datetime_str, json_str = row
            try:
                game_data = json.loads(json_str)
                return game_data
            except json.JSONDecodeError:
                return None
                
        except sqlite3.Error:
            return None
        except Exception:
            return None

    def get_all_states(self) -> List[Tuple[str, Dict]]:
        """Get all game states from the database for video mode."""
        try:
            if not os.path.exists(self.db_path):
                return []
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if Areas table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Areas';")
            if not cursor.fetchone():
                conn.close()
                return []
                
            cursor.execute("""
                SELECT Date, Json 
                FROM Areas 
                ORDER BY Date ASC
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return []
                
            all_states = []
            for datetime_str, json_str in rows:
                try:
                    game_data = json.loads(json_str)
                    all_states.append((datetime_str, game_data))
                except json.JSONDecodeError:
                    continue
            
            return all_states
                
        except sqlite3.Error:
            return []
        except Exception:
            return []

    def get_state_by_index(self, index: int) -> Optional[Tuple[str, Dict]]:
        """Get a specific state by index."""
        all_states = self.get_all_states()
        if 0 <= index < len(all_states):
            return all_states[index]
        return None

    def get_states_count(self) -> int:
        """Get the total number of states in the database."""
        try:
            if not os.path.exists(self.db_path):
                return 0
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM Areas")
            count = cursor.fetchone()[0]
            conn.close()
            
            return count
                
        except sqlite3.Error:
            return 0
        except Exception:
            return 0

    def validate_database(self) -> Tuple[bool, str]:
        """Validate the database structure and return status."""
        try:
            if not os.path.exists(self.db_path):
                return False, "Database file not found"
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if Areas table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Areas';")
            if not cursor.fetchone():
                conn.close()
                return False, "'Areas' table not found"
            
            # Check if table has required columns
            cursor.execute("PRAGMA table_info(Areas)")
            columns = [column[1] for column in cursor.fetchall()]
            
            required_columns = ["Date", "Json"]
            missing_columns = [col for col in required_columns if col not in columns]
            
            if missing_columns:
                conn.close()
                return False, f"Missing required columns: {', '.join(missing_columns)}"
            
            # Check if table has data
            cursor.execute("SELECT COUNT(*) FROM Areas")
            count = cursor.fetchone()[0]
            conn.close()
            
            if count == 0:
                return False, "No data in 'Areas' table"
            
            return True, f"Database valid with {count} records"
                
        except sqlite3.Error as e:
            return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}" 