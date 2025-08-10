#!/usr/bin/env python3
"""
Migration script to add is_starred field to conversations table
"""

import sqlite3
import os

def migrate_starred_chats():
    """Add is_starred field to conversations table"""
    db_path = 'ai_chat.db'
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found. No migration needed.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if is_starred column already exists
        cursor.execute("PRAGMA table_info(conversations)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_starred' not in columns:
            print("Adding is_starred column to conversations table...")
            
            # Add is_starred column with default value False
            cursor.execute("""
                ALTER TABLE conversations 
                ADD COLUMN is_starred BOOLEAN DEFAULT 0 NOT NULL
            """)
            
            conn.commit()
            print("✅ Successfully added is_starred column to conversations table")
        else:
            print("✅ is_starred column already exists in conversations table")
            
    except sqlite3.Error as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_starred_chats()
