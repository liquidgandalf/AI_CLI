#!/usr/bin/env python3
"""
File Upload Example - Python

This example shows how to upload files to conversations for processing.
"""

import requests
import json
import tempfile
import os
from datetime import datetime

# Configuration
API_KEY = 'YOUR_API_KEY_HERE'  # Replace with your actual API key
BASE_URL = 'http://localhost:5785'  # Update for your server

class FileUploadManager:
    """Class to manage file upload operations."""
    
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def create_conversation(self, title):
        """Create a new conversation for file uploads."""
        url = f"{self.base_url}/api/v1/conversations"
        data = {'title': title}
        
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            
            if response.status_code == 201:
                return {'success': True, 'data': response.json()}
            else:
                error_data = response.json() if response.content else {'error': 'Unknown error'}
                return {
                    'success': False,
                    'error': error_data.get('error', 'Unknown error'),
                    'status_code': response.status_code
                }
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Connection error: {str(e)}'}
    
    def upload_file(self, conversation_id, file_path, filename=None):
        """Upload a file to a conversation."""
        url = f"{self.base_url}/api/v1/conversations/{conversation_id}/upload"
        
        # Headers for file upload (don't include Content-Type, let requests handle it)
        upload_headers = {
            'X-API-Key': self.api_key
        }
        
        try:
            with open(file_path, 'rb') as file:
                files = {
                    'file': (filename or os.path.basename(file_path), file)
                }
                
                response = requests.post(
                    url, 
                    headers=upload_headers, 
                    files=files, 
                    timeout=60
                )
                
                if response.status_code == 201:
                    return {'success': True, 'data': response.json()}
                else:
                    error_data = response.json() if response.content else {'error': 'Unknown error'}
                    return {
                        'success': False,
                        'error': error_data.get('error', 'Unknown error'),
                        'status_code': response.status_code
                    }
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Connection error: {str(e)}'}
        except FileNotFoundError:
            return {'success': False, 'error': f'File not found: {file_path}'}
        except Exception as e:
            return {'success': False, 'error': f'Unexpected error: {str(e)}'}
    
    def list_conversations(self):
        """List conversations to verify file attachment."""
        url = f"{self.base_url}/api/v1/conversations"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            else:
                return {'success': False, 'error': 'Failed to list conversations'}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Connection error: {str(e)}'}

def create_sample_files():
    """Create sample files for upload testing."""
    files_created = []
    
    # Create a text file
    text_content = f"""Sample Text File for API Testing
=====================================

This file was created on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This demonstrates the file upload functionality of the AI CLI API.

Supported File Types:
- Text files: .txt, .md, .html, .css, .js, .json, .xml, .py, .sql
- Documents: .pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx  
- Images: .jpg, .jpeg, .png, .gif, .webp, .svg, .bmp
- Audio: .mp3, .wav, .ogg, .m4a, .aac, .flac, .mpga
- Archives: .zip, .tar, .gz, .rar

File Processing:
- Files are automatically processed by background workers
- Text files are extracted and indexed
- Audio files are transcribed
- Documents are parsed for content
- Images are analyzed for content

Maximum file size: 100MB per file

This sample file can be used to test the upload and processing pipeline.
"""
    
    # Create temporary text file
    text_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    text_file.write(text_content)
    text_file.close()
    files_created.append((text_file.name, 'sample-text-file.txt', 'text'))
    
    # Create a JSON file
    json_content = {
        "api_test": True,
        "created_at": datetime.now().isoformat(),
        "file_type": "json",
        "description": "Sample JSON file for API upload testing",
        "features": [
            "File upload via API",
            "Automatic processing",
            "Content extraction",
            "Searchable content"
        ],
        "supported_formats": {
            "text": ["txt", "md", "html", "css", "js", "json", "xml", "py", "sql"],
            "documents": ["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx"],
            "images": ["jpg", "jpeg", "png", "gif", "webp", "svg", "bmp"],
            "audio": ["mp3", "wav", "ogg", "m4a", "aac", "flac", "mpga"],
            "archives": ["zip", "tar", "gz", "rar"]
        },
        "max_file_size": "100MB"
    }
    
    json_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(json_content, json_file, indent=2)
    json_file.close()
    files_created.append((json_file.name, 'sample-data.json', 'text'))
    
    # Create a Python script file
    python_content = f'''#!/usr/bin/env python3
"""
Sample Python Script - API Upload Test
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

def hello_world():
    """Simple function to demonstrate Python file upload."""
    print("Hello from uploaded Python file!")
    return "File upload successful"

def process_data(data):
    """Example function that processes data."""
    if isinstance(data, list):
        return [item.upper() if isinstance(item, str) else item for item in data]
    elif isinstance(data, str):
        return data.upper()
    else:
        return str(data)

class APITestClass:
    """Example class for testing file processing."""
    
    def __init__(self, name):
        self.name = name
        self.created_at = "{datetime.now().isoformat()}"
    
    def get_info(self):
        return f"API Test Class: {{self.name}}, Created: {{self.created_at}}"

if __name__ == "__main__":
    print("This Python file was uploaded via the AI CLI API")
    test_obj = APITestClass("Upload Test")
    print(test_obj.get_info())
    hello_world()
'''
    
    python_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
    python_file.write(python_content)
    python_file.close()
    files_created.append((python_file.name, 'sample-script.py', 'text'))
    
    return files_created

def main():
    """Main function to demonstrate file upload functionality."""
    
    print("=== File Upload Example ===\n")
    
    # Initialize the file upload manager
    manager = FileUploadManager(API_KEY, BASE_URL)
    
    # 1. Create a conversation for file uploads
    print("1. Creating a conversation for file uploads...")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conv_title = f"File Upload Test - {timestamp}"
    
    result = manager.create_conversation(conv_title)
    
    if result['success']:
        conversation = result['data']
        conversation_id = conversation['id']
        print(f"✅ Created conversation ID: {conversation_id}")
        print(f"   Title: {conversation['title']}")
        print()
    else:
        print(f"❌ Error creating conversation: {result['error']}")
        return
    
    # 2. Create sample files
    print("2. Creating sample files for upload...")
    sample_files = create_sample_files()
    print(f"✅ Created {len(sample_files)} sample files:")
    for file_path, filename, file_type in sample_files:
        file_size = os.path.getsize(file_path)
        print(f"   - {filename} ({file_type}, {file_size} bytes)")
    print()
    
    # 3. Upload each file
    print("3. Uploading files to conversation...")
    uploaded_files = []
    
    for file_path, filename, expected_type in sample_files:
        print(f"   Uploading {filename}...")
        
        result = manager.upload_file(conversation_id, file_path, filename)
        
        if result['success']:
            file_data = result['data']
            uploaded_files.append(file_data)
            print(f"   ✅ Upload successful:")
            print(f"      - File ID: {file_data['id']}")
            print(f"      - Filename: {file_data['filename']}")
            print(f"      - Type: {file_data['file_type']}")
            print(f"      - Size: {file_data['file_size']} bytes")
            print(f"      - Upload Date: {file_data['upload_date']}")
        else:
            print(f"   ❌ Upload failed: {result['error']}")
        
        print()
    
    # 4. Clean up temporary files
    print("4. Cleaning up temporary files...")
    for file_path, filename, _ in sample_files:
        try:
            os.unlink(file_path)
            print(f"   ✅ Deleted {filename}")
        except Exception as e:
            print(f"   ⚠️  Could not delete {filename}: {e}")
    print()
    
    # 5. Verify files are attached to conversation
    print("5. Verifying file attachment to conversation...")
    result = manager.list_conversations()
    
    if result['success']:
        conversations = result['data']['conversations']
        target_conv = next((c for c in conversations if c['id'] == conversation_id), None)
        
        if target_conv:
            print(f"✅ Conversation now has {target_conv['file_count']} file(s) attached")
            print(f"   Message count: {target_conv['message_count']}")
        else:
            print("❌ Could not find the conversation")
    else:
        print(f"❌ Error verifying conversation: {result['error']}")
    
    print("\n=== File Upload Complete ===")
    
    if uploaded_files:
        print(f"\n📁 Successfully uploaded {len(uploaded_files)} file(s):")
        for file_data in uploaded_files:
            print(f"   - {file_data['filename']} (ID: {file_data['id']})")
        
        print("\n🔄 Next steps:")
        print("1. Files will be processed by the background worker")
        print("2. Start worker: python process_unprocessed_files.py --loop")
        print("3. Use file_retrieval.py to get processed transcripts")
        print("4. Check the web interface to see processing status")
        print("5. Files can be downloaded via the API or web interface")
    else:
        print("\n❌ No files were successfully uploaded")

if __name__ == "__main__":
    main()
