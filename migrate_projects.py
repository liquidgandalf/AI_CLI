#!/usr/bin/env python3
"""
Migration script to add projects table and project_id to conversations
"""

from database import get_db, init_db
from sqlalchemy import text

def migrate_projects():
    """Add projects table and project_id column to conversations"""
    db = get_db()
    try:
        # Check if projects table exists
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'"))
        projects_table_exists = result.fetchone() is not None
        
        if not projects_table_exists:
            print("Creating projects table...")
            db.execute(text("""
                CREATE TABLE projects (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """))
            db.commit()
            print("✓ Projects table created")
        else:
            print("Projects table already exists")
        
        # Check if project_id column exists in conversations table
        result = db.execute(text("PRAGMA table_info(conversations)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'project_id' not in columns:
            print("Adding project_id column to conversations...")
            db.execute(text("ALTER TABLE conversations ADD COLUMN project_id INTEGER"))
            db.commit()
            print("✓ project_id column added to conversations")
        else:
            print("project_id column already exists in conversations")
            
        print("✓ Projects migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting projects migration...")
    migrate_projects()
    print("Migration completed!")
