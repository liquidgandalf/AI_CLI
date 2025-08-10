#!/usr/bin/env python3
"""
Migration script to add chat_files table for file attachments
"""

import sqlite3
import os

def migrate_chat_files():
    """Add chat_files table for file attachments"""
    db_path = 'ai_chat.db'
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found. No migration needed.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if chat_files table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_files'")
        if cursor.fetchone():
            print("✅ chat_files table already exists")
            return
        
        print("Creating chat_files table...")
        
        # Create chat_files table
        cursor.execute("""
            CREATE TABLE chat_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                original_filename VARCHAR(255) NOT NULL,
                system_filename VARCHAR(255) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                file_type VARCHAR(50) NOT NULL,
                mime_type VARCHAR(100),
                file_size INTEGER NOT NULL,
                upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                uploaded_by INTEGER NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id),
                FOREIGN KEY (uploaded_by) REFERENCES users(id)
            )
        """)
        
        conn.commit()
        print("✅ Successfully created chat_files table")
        
    except sqlite3.Error as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_chat_files()
