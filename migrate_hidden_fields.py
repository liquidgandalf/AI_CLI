#!/usr/bin/env python3
"""
Migration script to add is_hidden field to conversations and projects tables
for three-level archiving system (Active, Hidden, Archived)
"""

import sqlite3
import os

def migrate_hidden_fields():
    """Add is_hidden field to conversations and projects tables"""
    
    db_path = "ai_chat.db"
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if is_hidden already exists in conversations table
        cursor.execute("PRAGMA table_info(conversations)")
        conversations_columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_hidden' not in conversations_columns:
            print("Adding is_hidden field to conversations table...")
            cursor.execute("""
                ALTER TABLE conversations 
                ADD COLUMN is_hidden BOOLEAN DEFAULT FALSE NOT NULL
            """)
            print("✓ Added is_hidden to conversations table")
        else:
            print("✓ is_hidden field already exists in conversations table")
        
        # Check if is_hidden already exists in projects table
        cursor.execute("PRAGMA table_info(projects)")
        projects_columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_hidden' not in projects_columns:
            print("Adding is_hidden field to projects table...")
            cursor.execute("""
                ALTER TABLE projects 
                ADD COLUMN is_hidden BOOLEAN DEFAULT FALSE NOT NULL
            """)
            print("✓ Added is_hidden to projects table")
        else:
            print("✓ is_hidden field already exists in projects table")
        
        # Commit changes
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
        # Show current table structures
        print("\n📋 Updated table structures:")
        
        print("\nConversations table:")
        cursor.execute("PRAGMA table_info(conversations)")
        for column in cursor.fetchall():
            print(f"  - {column[1]} ({column[2]})")
        
        print("\nProjects table:")
        cursor.execute("PRAGMA table_info(projects)")
        for column in cursor.fetchall():
            print(f"  - {column[1]} ({column[2]})")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔄 Starting migration to add is_hidden fields...")
    success = migrate_hidden_fields()
    
    if success:
        print("\n🎉 Migration completed! The three-level archiving system is now ready:")
        print("  📌 Level 1 (Active): is_archived=False, is_hidden=False")
        print("  👁️  Level 2 (Hidden): is_archived=False, is_hidden=True") 
        print("  📦 Level 3 (Archived): is_archived=True")
    else:
        print("\n💥 Migration failed! Please check the errors above.")
