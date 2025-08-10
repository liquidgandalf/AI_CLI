#!/usr/bin/env python3
"""
Database models and setup for AI Chat Interface
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, create_engine, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
import secrets

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    allowedaccess = Column(String(10), default='no', nullable=False)  # 'yes' or 'no'
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversations = relationship("Conversation", back_populates="user")
    projects = relationship("Project", back_populates="user")
    uploaded_files = relationship("ChatFile", back_populates="uploader")

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)  # Optional project description
    is_archived = Column(Boolean, default=False, nullable=False)  # Archive flag for unused projects
    is_hidden = Column(Boolean, default=False, nullable=False)  # Hidden from front page but accessible via user page
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="projects")
    conversations = relationship("Conversation", back_populates="project")

class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)  # Optional project assignment
    title = Column(String(255), nullable=False)
    dataset = Column(Text)  # Store the dataset for this conversation
    is_starred = Column(Boolean, default=False, nullable=False)  # Priority chat flag
    is_archived = Column(Boolean, default=False, nullable=False)  # Archive flag for empty/unused chats
    is_hidden = Column(Boolean, default=False, nullable=False)  # Hidden from front page but accessible via user page
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="conversations")
    project = relationship("Project", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")
    files = relationship("ChatFile", back_populates="conversation")

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)
    message_type = Column(String(10), nullable=False)  # 'user' or 'ai'
    question = Column(Text)  # For user messages
    response = Column(Text)  # For AI messages
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="messages")

class ChatFile(Base):
    __tablename__ = 'chat_files'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)
    original_filename = Column(String(255), nullable=False)  # User's original filename
    system_filename = Column(String(255), nullable=False)    # Our generated filename
    file_path = Column(String(500), nullable=False)          # Relative path from storage root
    file_type = Column(String(50), nullable=False)           # 'audio', 'image', 'text', 'document', 'other'
    mime_type = Column(String(100), nullable=True)           # MIME type for proper serving
    file_size = Column(Integer, nullable=False)              # Size in bytes
    upload_date = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    is_project_important = Column(Boolean, default=False, nullable=False)  # Flag for project-important files
    file_hash = Column(String(32), nullable=True)            # MD5 hash for duplicate detection
    
    # File processing fields
    has_been_processed = Column(Integer, default=0, nullable=False)  # 0=unprocessed, 1=being processed, 2=processed
    transcoded_raw_file = Column(Text, nullable=True)        # Raw response from processing (can be very long)
    summary_raw_file = Column(Text, nullable=True)           # Summary of processed file (can be long)
    human_notes = Column(Text, nullable=True)                # Human notes about the file
    date_processed = Column(DateTime, nullable=True)         # When processing was completed
    time_to_process = Column(Float, nullable=True)           # Time taken to process in seconds
    
    # Relationships
    conversation = relationship("Conversation", back_populates="files")
    uploader = relationship("User", back_populates="uploaded_files")

class ApiKey(Base):
    __tablename__ = 'api_keys'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    key_name = Column(String(255), nullable=False)  # Human-readable name
    key_hash = Column(String(255), nullable=False, unique=True)  # Hashed API key
    key_prefix = Column(String(10), nullable=False)  # First few chars for display
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    
    user = relationship("User")
    
    @staticmethod
    def generate_key():
        """Generate a new API key"""
        return f"sk-{secrets.token_urlsafe(32)}"
    
    @staticmethod
    def hash_key(key):
        """Hash an API key for storage"""
        import hashlib
        return hashlib.sha256(key.encode()).hexdigest()

# Database setup
DATABASE_URL = "sqlite:///ai_chat.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here, let the caller handle it

if __name__ == "__main__":
    init_db()
    print("Database initialized!")
