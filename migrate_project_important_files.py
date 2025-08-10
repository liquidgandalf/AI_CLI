#!/usr/bin/env python3
"""
Migration script to add is_project_important column to chat_files table
"""

import sqlite3
import os

def migrate_project_important_files():
    # Database file path
    db_path = 'ai_chat.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Please run the main application first to create the database.")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(chat_files)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_project_important' in columns:
            print("✅ is_project_important column already exists")
            return
        
        # Add the new column
        cursor.execute("""
            ALTER TABLE chat_files 
            ADD COLUMN is_project_important BOOLEAN DEFAULT 0 NOT NULL
        """)
        
        # Commit changes
        conn.commit()
        print("✅ Successfully added is_project_important column to chat_files table")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_project_important_files()
