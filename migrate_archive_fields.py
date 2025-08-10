#!/usr/bin/env python3
"""
Migration script to add is_archived fields to conversations and projects tables.
This enables archiving functionality for unused chats and projects.
"""

import sqlite3
import os
import sys

def migrate_database():
    """Add is_archived columns to conversations and projects tables"""
    db_path = 'ai_chat.db'
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check and add is_archived to conversations table
        cursor.execute("PRAGMA table_info(conversations)")
        conv_columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_archived' not in conv_columns:
            print("Adding is_archived column to conversations table...")
            cursor.execute("""
                ALTER TABLE conversations 
                ADD COLUMN is_archived BOOLEAN DEFAULT 0 NOT NULL
            """)
        else:
            print("is_archived column already exists in conversations table")
        
        # Check and add is_archived to projects table
        cursor.execute("PRAGMA table_info(projects)")
        proj_columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_archived' not in proj_columns:
            print("Adding is_archived column to projects table...")
            cursor.execute("""
                ALTER TABLE projects 
                ADD COLUMN is_archived BOOLEAN DEFAULT 0 NOT NULL
            """)
        else:
            print("is_archived column already exists in projects table")
        
        # Commit changes
        conn.commit()
        print("Successfully added is_archived columns to both tables")
        
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
    print("Running migration to add is_archived columns...")
    success = migrate_database()
    
    if success:
        print("Migration completed successfully!")
        sys.exit(0)
    else:
        print("Migration failed!")
        sys.exit(1)
