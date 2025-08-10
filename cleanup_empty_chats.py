#!/usr/bin/env python3
"""
One-off cleanup script to delete all conversations with zero messages.
This will clean up the accumulated empty chats from the previous bug.

Usage: python cleanup_empty_chats.py
"""

import sys
import os
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker

# Add the current directory to Python path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Conversation, Message, ChatFile, get_db

def cleanup_empty_conversations():
    """Delete all conversations that have zero messages"""
    
    # Get database session
    db = get_db()
    
    try:
        # Find all conversations with zero messages using a simpler approach
        all_conversations = db.query(Conversation).all()
        empty_conversations = []
        
        for conv in all_conversations:
            message_count = db.query(Message).filter(Message.conversation_id == conv.id).count()
            if message_count == 0:
                empty_conversations.append(conv)
        
        if not empty_conversations:
            print("✅ No empty conversations found. Database is clean!")
            return
        
        print(f"🔍 Found {len(empty_conversations)} empty conversations to delete:")
        
        # Show details of what will be deleted
        for conv in empty_conversations:
            print(f"  - ID: {conv.id}, Title: '{conv.title}', User: {conv.user_id}, Created: {conv.created_at}")
        
        # Ask for confirmation
        response = input(f"\n⚠️  Are you sure you want to delete these {len(empty_conversations)} empty conversations? (y/N): ")
        
        if response.lower() != 'y':
            print("❌ Cleanup cancelled.")
            return
        
        # Delete the empty conversations
        deleted_count = 0
        for conv in empty_conversations:
            try:
                # Double-check that this conversation has no messages
                message_count = db.query(Message).filter(Message.conversation_id == conv.id).count()
                if message_count == 0:
                    # First, delete any associated chat files
                    chat_files = db.query(ChatFile).filter(ChatFile.conversation_id == conv.id).all()
                    files_deleted = 0
                    for chat_file in chat_files:
                        db.delete(chat_file)
                        files_deleted += 1
                    
                    # Then delete the conversation
                    db.delete(conv)
                    deleted_count += 1
                    
                    if files_deleted > 0:
                        print(f"  ✅ Deleted conversation ID {conv.id}: '{conv.title}' (and {files_deleted} associated files)")
                    else:
                        print(f"  ✅ Deleted conversation ID {conv.id}: '{conv.title}'")
                else:
                    print(f"  ⚠️  Skipped conversation ID {conv.id}: '{conv.title}' (has {message_count} messages)")
            except Exception as e:
                print(f"  ❌ Error deleting conversation ID {conv.id}: {e}")
                db.rollback()  # Rollback this specific conversation's deletion
                continue
        
        # Commit all deletions
        db.commit()
        
        print(f"\n🎉 Cleanup completed! Deleted {deleted_count} empty conversations.")
        print("💡 The system will now reuse existing unused chats instead of creating new ones.")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    print("🧹 Empty Chat Cleanup Script")
    print("=" * 40)
    print("This script will delete all conversations with zero messages.")
    print("This is a one-time cleanup to fix the accumulated empty chats.")
    print()
    
    try:
        cleanup_empty_conversations()
    except KeyboardInterrupt:
        print("\n❌ Cleanup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
