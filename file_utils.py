#!/usr/bin/env python3
"""
File utilities for handling uploads, type detection, and storage management
"""

import os
import uuid
import mimetypes
from datetime import datetime
from werkzeug.utils import secure_filename

# Storage configuration
STORAGE_BASE = os.path.join(os.path.dirname(__file__), 'storage')
UPLOADS_DIR = os.path.join(STORAGE_BASE, 'uploads')

# File type mappings
FILE_TYPE_MAPPINGS = {
    # Audio files
    'audio/mpeg': 'audio',
    'audio/mp3': 'audio',
    'audio/wav': 'audio',
    'audio/ogg': 'audio',
    'audio/m4a': 'audio',
    'audio/aac': 'audio',
    'audio/flac': 'audio',
    
    # Image files
    'image/jpeg': 'image',
    'image/jpg': 'image',
    'image/png': 'image',
    'image/gif': 'image',
    'image/webp': 'image',
    'image/svg+xml': 'image',
    'image/bmp': 'image',
    
    # Text files
    'text/plain': 'text',
    'text/markdown': 'text',
    'text/html': 'text',
    'text/css': 'text',
    'text/javascript': 'text',
    'application/json': 'text',
    'application/xml': 'text',
    'text/tab-separated-values': 'text',
    
    # Document files
    'application/pdf': 'document',
    'application/msword': 'document',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'document',
    'application/vnd.ms-excel': 'document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'document',
    'application/vnd.ms-powerpoint': 'document',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'document',
    'text/csv': 'document',
    'application/vnd.oasis.opendocument.spreadsheet': 'document',
    'application/vnd.oasis.opendocument.text': 'document',
    'application/vnd.oasis.opendocument.presentation': 'document',
    'application/rtf': 'document',
    'application/x-rtf': 'document',
    
    # Archive files
    'application/zip': 'archive',
    'application/x-tar': 'archive',
    'application/gzip': 'archive',
    'application/x-rar-compressed': 'archive',
    
    # Additional images for OCR
    'image/tiff': 'image',
}

# File size limits (in bytes)
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {
    'audio': {'mp3', 'wav', 'ogg', 'm4a', 'aac', 'flac', 'mpga'},
    'image': {'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'tif', 'tiff'},
    'text': {'txt', 'md', 'html', 'css', 'js', 'json', 'xml', 'py', 'sql', 'tsv'},
    'document': {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'csv', 'ods', 'odt', 'odp', 'rtf'},
    'archive': {'zip', 'tar', 'gz', 'rar'},
}

def ensure_storage_dirs():
    """Ensure storage directories exist"""
    os.makedirs(UPLOADS_DIR, exist_ok=True)

def get_file_type_from_mime(mime_type):
    """Determine file type category from MIME type"""
    if not mime_type:
        return 'other'
    
    return FILE_TYPE_MAPPINGS.get(mime_type.lower(), 'other')

def get_file_type_from_extension(filename):
    """Determine file type category from file extension"""
    if not filename:
        return 'other'
    
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return file_type
    
    return 'other'

def generate_system_filename(original_filename):
    """Generate a unique system filename while preserving extension"""
    if not original_filename:
        return str(uuid.uuid4())
    
    # Get file extension
    parts = original_filename.rsplit('.', 1)
    if len(parts) == 2:
        extension = parts[1].lower()
        return f"{uuid.uuid4()}.{extension}"
    else:
        return str(uuid.uuid4())

def get_date_path():
    """Generate date-based path (year/month/day)"""
    now = datetime.now()
    return os.path.join(
        str(now.year),
        f"{now.month:02d}",
        f"{now.day:02d}"
    )

def get_full_storage_path(date_path, system_filename):
    """Get full storage path for a file"""
    full_dir = os.path.join(UPLOADS_DIR, date_path)
    os.makedirs(full_dir, exist_ok=True)
    return os.path.join(full_dir, system_filename)

def get_relative_path(date_path, system_filename):
    """Get relative path from storage root"""
    return os.path.join(date_path, system_filename)

def validate_file(file):
    """Validate uploaded file"""
    if not file or not file.filename:
        return False, "No file selected"
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    if file_size > MAX_FILE_SIZE:
        return False, f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
    
    if file_size == 0:
        return False, "File is empty"
    
    # Check file extension
    filename = secure_filename(file.filename)
    if '.' not in filename:
        return False, "File must have an extension"
    
    ext = filename.rsplit('.', 1)[1].lower()
    all_allowed_extensions = set()
    for extensions in ALLOWED_EXTENSIONS.values():
        all_allowed_extensions.update(extensions)
    
    if ext not in all_allowed_extensions:
        return False, f"File type '{ext}' not allowed"
    
    return True, "File is valid"

def save_uploaded_file(file, conversation_id, user_id):
    """Save uploaded file and return file metadata"""
    # Validate file
    is_valid, message = validate_file(file)
    if not is_valid:
        raise ValueError(message)
    
    # Generate filenames and paths
    original_filename = secure_filename(file.filename)
    system_filename = generate_system_filename(original_filename)
    date_path = get_date_path()
    relative_path = get_relative_path(date_path, system_filename)
    full_path = get_full_storage_path(date_path, system_filename)
    
    # Determine file type and MIME type
    mime_type, _ = mimetypes.guess_type(original_filename)
    file_type = get_file_type_from_mime(mime_type) or get_file_type_from_extension(original_filename)
    
    # Get file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    # Save file to disk
    ensure_storage_dirs()
    file.save(full_path)
    
    return {
        'original_filename': original_filename,
        'system_filename': system_filename,
        'file_path': relative_path,
        'file_type': file_type,
        'mime_type': mime_type,
        'file_size': file_size,
        'conversation_id': conversation_id,
        'uploaded_by': user_id
    }

def get_file_full_path(relative_path):
    """Get full filesystem path from relative path"""
    return os.path.join(UPLOADS_DIR, relative_path)

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"
