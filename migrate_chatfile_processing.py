#!/usr/bin/env python3
"""
Database migration to add file processing fields to ChatFile table.

This migration adds the following fields:
- has_been_processed (INTEGER, default 0): 0=unprocessed, 1=being processed, 2=processed
- transcoded_raw_file (TEXT): Raw response from processing
- summary_raw_file (TEXT): Summary of processed file
- human_notes (TEXT): Human notes about the file
- date_processed (DATETIME): When processing was completed
- time_to_process (REAL): Time taken to process in seconds

Usage: python migrate_chatfile_processing.py
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add the current directory to Python path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def migrate_database():
    """Add file processing fields to ChatFile table"""
    
    # Database file path
    db_path = 'ai_chat.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False
    
    print("🔄 Starting ChatFile table migration...")
    print("Adding file processing fields to chat_files table")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_files'")
        if not cursor.fetchone():
            print("❌ chat_files table not found!")
            return False
        
        # Check if columns already exist (in case migration was run before)
        cursor.execute("PRAGMA table_info(chat_files)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        migrations_needed = []
        new_columns = {
            'has_been_processed': 'INTEGER DEFAULT 0 NOT NULL',
            'transcoded_raw_file': 'TEXT',
            'summary_raw_file': 'TEXT', 
            'human_notes': 'TEXT',
            'date_processed': 'DATETIME',
            'time_to_process': 'REAL'
        }
        
        for column_name, column_def in new_columns.items():
            if column_name not in existing_columns:
                migrations_needed.append((column_name, column_def))
        
        if not migrations_needed:
            print("✅ All file processing columns already exist. No migration needed.")
            return True
        
        print(f"📝 Adding {len(migrations_needed)} new columns:")
        
        # Add each missing column
        for column_name, column_def in migrations_needed:
            print(f"  - Adding {column_name}...")
            cursor.execute(f"ALTER TABLE chat_files ADD COLUMN {column_name} {column_def}")
        
        # Commit the changes
        conn.commit()
        
        print("✅ Migration completed successfully!")
        print("\nNew ChatFile processing fields:")
        print("  - has_been_processed: 0=unprocessed, 1=being processed, 2=processed")
        print("  - transcoded_raw_file: Raw response from processing")
        print("  - summary_raw_file: Summary of processed file")
        print("  - human_notes: Human notes about the file")
        print("  - date_processed: When processing was completed")
        print("  - time_to_process: Time taken to process in seconds")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error during migration: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during migration: {e}")
        return False
    finally:
        if conn:
            conn.close()

def main():
    print("🗄️  ChatFile Processing Fields Migration")
    print("=" * 50)
    print("This migration will add file processing fields to the ChatFile table.")
    print()
    
    success = migrate_database()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("💡 The ChatFile model now supports file processing workflows.")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
