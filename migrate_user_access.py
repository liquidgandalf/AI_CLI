#!/usr/bin/env python3
"""
Migration script to add allowedaccess and is_admin fields to existing users
"""

from database import get_db, User, init_db
from sqlalchemy import text

def migrate_user_access():
    """Add allowedaccess and is_admin columns and set existing users to allowed access"""
    db = get_db()
    try:
        # First, let's check if the columns already exist
        result = db.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result.fetchall()]
        
        # Add allowedaccess column if it doesn't exist
        if 'allowedaccess' not in columns:
            print("Adding allowedaccess column...")
            db.execute(text("ALTER TABLE users ADD COLUMN allowedaccess VARCHAR(10) DEFAULT 'no' NOT NULL"))
            db.commit()
            print("✓ allowedaccess column added")
        else:
            print("allowedaccess column already exists")
            
        # Add is_admin column if it doesn't exist
        if 'is_admin' not in columns:
            print("Adding is_admin column...")
            db.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0 NOT NULL"))
            db.commit()
            print("✓ is_admin column added")
        else:
            print("is_admin column already exists")
        
        # Set all existing users to have allowed access to prevent lockout
        existing_users = db.query(User).all()
        if existing_users:
            print(f"Found {len(existing_users)} existing users")
            for user in existing_users:
                user.allowedaccess = 'yes'
                print(f"✓ Set allowedaccess=yes for user: {user.username}")
            
            # Make the first user an admin to ensure admin access
            first_user = existing_users[0]
            first_user.is_admin = True
            print(f"✓ Set is_admin=True for first user: {first_user.username}")
            
            db.commit()
            print("✓ All existing users updated with allowed access")
        else:
            print("No existing users found")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting user access migration...")
    migrate_user_access()
    print("Migration completed successfully!")
