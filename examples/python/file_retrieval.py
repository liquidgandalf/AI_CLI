#!/usr/bin/env python3
"""
File Retrieval Example - Python

This example shows how to retrieve processed file transcripts and raw content.
"""

import requests
import json
from datetime import datetime

# Configuration
API_KEY = 'YOUR_API_KEY_HERE'  # Replace with your actual API key
BASE_URL = 'http://localhost:5785'  # Update for your server

class FileRetrievalManager:
    """Class to manage file retrieval operations."""
    
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def list_conversations(self):
        """List all conversations to find ones with files."""
        url = f"{self.base_url}/api/v1/conversations"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
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
    
    def get_conversation_files(self, conversation_id):
        """Get files for a specific conversation."""
        url = f"{self.base_url}/api/conversations/{conversation_id}/files"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
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
    
    def get_file_details(self, file_id):
        """Get detailed information about a file including processed content."""
        url = f"{self.base_url}/api/files/{file_id}/details"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
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
    
    def download_file(self, file_id):
        """Download the raw file content."""
        url = f"{self.base_url}/api/files/{file_id}/download"
        
        # Headers for file download
        download_headers = {
            'X-API-Key': self.api_key
        }
        
        try:
            response = requests.get(url, headers=download_headers, timeout=30)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'content': response.content,
                    'content_type': response.headers.get('Content-Type', 'unknown'),
                    'content_length': len(response.content)
                }
            else:
                error_data = response.json() if response.content else {'error': 'Unknown error'}
                return {
                    'success': False,
                    'error': error_data.get('error', 'Unknown error'),
                    'status_code': response.status_code
                }
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Connection error: {str(e)}'}

def get_processing_status_text(status):
    """Convert processing status number to human-readable text."""
    status_map = {
        0: 'Unprocessed',
        1: 'Processing',
        2: 'Processed',
        4: 'Do Not Process'
    }
    return status_map.get(status, 'Unknown')

def format_file_info(file_data):
    """Format file information for display."""
    upload_date = datetime.fromisoformat(file_data['upload_date'].replace('Z', '+00:00'))
    status = get_processing_status_text(file_data['has_been_processed'])
    
    return f"""  - ID: {file_data['id']}
    Name: {file_data['original_filename']}
    Type: {file_data['file_type']}
    Size: {file_data['file_size']} bytes
    Status: {status}
    Uploaded: {upload_date.strftime('%Y-%m-%d %H:%M:%S')}
    MIME: {file_data.get('mime_type', 'unknown')}"""

def main():
    """Main function to demonstrate file retrieval functionality."""
    
    print("=== File Retrieval Example ===\n")
    
    # Initialize the file retrieval manager
    manager = FileRetrievalManager(API_KEY, BASE_URL)
    
    # 1. Find conversations with files
    print("1. Finding conversations with files...")
    result = manager.list_conversations()
    
    if not result['success']:
        print(f"❌ Error listing conversations: {result['error']}")
        return
    
    conversations = result['data']['conversations']
    conversations_with_files = [c for c in conversations if c['file_count'] > 0]
    
    if not conversations_with_files:
        print("❌ No conversations with files found.")
        print("   Please run file_upload.py first to upload some files.")
        return
    
    print(f"✅ Found {len(conversations_with_files)} conversation(s) with files:")
    for conv in conversations_with_files:
        created = datetime.fromisoformat(conv['created_at'].replace('Z', '+00:00'))
        print(f"  - ID: {conv['id']}, Title: {conv['title']}")
        print(f"    Files: {conv['file_count']}, Messages: {conv['message_count']}")
        print(f"    Created: {created.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Use the first conversation with files
    selected_conv = conversations_with_files[0]
    conversation_id = selected_conv['id']
    print(f"Using conversation ID: {conversation_id} - '{selected_conv['title']}'")
    print()
    
    # 2. Get files for the selected conversation
    print("2. Getting files for the selected conversation...")
    result = manager.get_conversation_files(conversation_id)
    
    if not result['success']:
        print(f"❌ Error getting files: {result['error']}")
        return
    
    files = result['data']['files']
    print(f"✅ Found {len(files)} file(s):")
    
    for file_data in files:
        print(format_file_info(file_data))
    print()
    
    if not files:
        print("❌ No files found in conversation.")
        return
    
    # 3. Process each file to show details and content
    for i, file_data in enumerate(files, 1):
        file_id = file_data['id']
        filename = file_data['original_filename']
        
        print(f"--- File {i}: {filename} (ID: {file_id}) ---")
        
        # Get detailed file information
        print("Getting detailed file information...")
        result = manager.get_file_details(file_id)
        
        if result['success']:
            details = result['data']
            
            print("✅ File Details:")
            print(f"  - Original Name: {details['original_filename']}")
            print(f"  - File Type: {details['file_type']}")
            print(f"  - MIME Type: {details['mime_type']}")
            print(f"  - File Size: {details['file_size']} bytes")
            print(f"  - Processing Status: {get_processing_status_text(details['has_been_processed'])}")
            
            upload_date = datetime.fromisoformat(details['upload_date'].replace('Z', '+00:00'))
            print(f"  - Upload Date: {upload_date.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Show processed content if available
            if details.get('processed_content') and details['processed_content'].strip():
                print("\n📄 PROCESSED TRANSCRIPT:")
                print("=" * 50)
                print(details['processed_content'])
                print("=" * 50)
            else:
                print("  - No processed content available yet")
                if details['has_been_processed'] == 0:
                    print("    (File is unprocessed - start the background worker)")
                elif details['has_been_processed'] == 1:
                    print("    (File is currently being processed)")
                elif details['has_been_processed'] == 4:
                    print("    (File is marked as 'Do Not Process')")
            
        else:
            print(f"❌ Error getting file details: {result['error']}")
        
        # Download raw file content
        print("\nDownloading raw file content...")
        result = manager.download_file(file_id)
        
        if result['success']:
            content_type = result['content_type']
            content_length = result['content_length']
            raw_content = result['content']
            
            print(f"✅ Raw file downloaded successfully")
            print(f"  - Content Type: {content_type}")
            print(f"  - Content Length: {content_length} bytes")
            
            # If it's a text file, show a preview
            if content_type.startswith('text/') or 'json' in content_type:
                try:
                    text_content = raw_content.decode('utf-8')
                    print("\n📄 RAW CONTENT PREVIEW (first 500 chars):")
                    print("=" * 50)
                    preview = text_content[:500]
                    print(preview)
                    if len(text_content) > 500:
                        print("\n... (content truncated)")
                    print("=" * 50)
                except UnicodeDecodeError:
                    print("  - Content is not valid UTF-8 text")
            else:
                print("  - Binary file content not displayed")
        else:
            print(f"❌ Error downloading file: {result['error']}")
        
        print("\n" + "="*60 + "\n")
    
    # 4. Summary and next steps
    print("=== File Retrieval Complete ===")
    
    processed_files = [f for f in files if f['has_been_processed'] == 2]
    unprocessed_files = [f for f in files if f['has_been_processed'] == 0]
    processing_files = [f for f in files if f['has_been_processed'] == 1]
    
    print(f"\n📊 File Processing Summary:")
    print(f"  - Total files: {len(files)}")
    print(f"  - Processed: {len(processed_files)}")
    print(f"  - Processing: {len(processing_files)}")
    print(f"  - Unprocessed: {len(unprocessed_files)}")
    
    if unprocessed_files:
        print(f"\n🔄 To process {len(unprocessed_files)} unprocessed file(s):")
        print("1. Start the background worker:")
        print("   cd /home/derek/AI_CLI")
        print("   source venv/bin/activate")
        print("   python process_unprocessed_files.py --loop")
        print("2. Wait for processing to complete")
        print("3. Run this script again to see processed content")
    
    if processed_files:
        print(f"\n✅ {len(processed_files)} file(s) have been processed and transcripts are available")

if __name__ == "__main__":
    main()
