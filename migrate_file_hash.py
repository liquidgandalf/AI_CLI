#!/usr/bin/env python3
"""
Migration script to add file_hash column to chat_files table for duplicate detection.
This script adds an MD5 hash field to prevent duplicate file uploads.
"""

import sqlite3
import os
import sys

def migrate_database():
    """Add file_hash column to chat_files table"""
    db_path = 'ai_chat.db'
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(chat_files)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'file_hash' in columns:
            print("file_hash column already exists in chat_files table")
            conn.close()
            return True
        
        # Add the file_hash column
        print("Adding file_hash column to chat_files table...")
        cursor.execute("""
            ALTER TABLE chat_files 
            ADD COLUMN file_hash TEXT
        """)
        
        # Commit changes
        conn.commit()
        print("Successfully added file_hash column to chat_files table")
        
        # Close connection
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Running migration to add file_hash column...")
    success = migrate_database()
    
    if success:
        print("Migration completed successfully!")
        sys.exit(0)
    else:
        print("Migration failed!")
        sys.exit(1)
