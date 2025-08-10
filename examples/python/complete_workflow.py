#!/usr/bin/env python3
"""
Complete Workflow Example - Python

This example demonstrates a full workflow using the AI CLI API:
1. Create a project
2. Create conversations within the project
3. Upload files to conversations
4. Fetch URL content and ask questions about it
5. Retrieve processed file content
6. Demonstrate the complete API ecosystem
"""

import requests
import json
import tempfile
import os
from datetime import datetime
import time

# Configuration
API_KEY = 'YOUR_API_KEY_HERE'  # Replace with your actual API key
BASE_URL = 'http://localhost:5785'  # Update for your server

class AICliWorkflow:
    """Complete workflow manager for AI CLI API operations."""
    
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
        self.project_id = None
        self.conversation_ids = []
        self.uploaded_files = []
    
    def make_request(self, endpoint, method='GET', data=None, files=None):
        """Make a request to the API with proper error handling."""
        url = f"{self.base_url}{endpoint}"
        
        headers = self.headers.copy()
        if files:
            # Remove Content-Type for file uploads
            headers = {'X-API-Key': self.api_key}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                if files:
                    response = requests.post(url, headers=headers, files=files, timeout=60)
                else:
                    response = requests.post(url, headers=headers, json=data, timeout=60)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return {'success': False, 'error': f'Unsupported method: {method}'}
            
            if response.status_code in [200, 201]:
                return {'success': True, 'data': response.json() if response.content else {}}
            else:
                error_data = response.json() if response.content else {'error': 'Unknown error'}
                return {
                    'success': False,
                    'error': error_data.get('error', 'Unknown error'),
                    'status_code': response.status_code
                }
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Connection error: {str(e)}'}
    
    def step_1_create_project(self):
        """Step 1: Create a project for organizing our work."""
        print("=== Step 1: Creating Project ===")
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        project_data = {
            'name': f'Complete Workflow Demo - {timestamp}',
            'description': 'Demonstration project showing full AI CLI API workflow including conversations, file uploads, URL fetching, and content processing.'
        }
        
        result = self.make_request('/api/v1/projects', 'POST', project_data)
        
        if result['success']:
            project = result['data']
            self.project_id = project['id']
            print(f"✅ Created project: {project['name']}")
            print(f"   Project ID: {project['id']}")
            print(f"   Description: {project['description']}")
            return True
        else:
            print(f"❌ Failed to create project: {result['error']}")
            return False
    
    def step_2_create_conversations(self):
        """Step 2: Create multiple conversations for different purposes."""
        print("\n=== Step 2: Creating Conversations ===")
        
        conversations = [
            {
                'title': 'File Processing Conversation',
                'purpose': 'For uploading and processing various file types'
            },
            {
                'title': 'Web Content Analysis',
                'purpose': 'For fetching and analyzing web content'
            },
            {
                'title': 'General AI Chat',
                'purpose': 'For general questions and AI interactions'
            }
        ]
        
        for conv_data in conversations:
            result = self.make_request('/api/v1/conversations', 'POST', {'title': conv_data['title']})
            
            if result['success']:
                conversation = result['data']
                self.conversation_ids.append(conversation['id'])
                print(f"✅ Created conversation: {conversation['title']}")
                print(f"   Conversation ID: {conversation['id']}")
                print(f"   Purpose: {conv_data['purpose']}")
            else:
                print(f"❌ Failed to create conversation '{conv_data['title']}': {result['error']}")
        
        return len(self.conversation_ids) > 0
    
    def step_3_upload_files(self):
        """Step 3: Upload various types of files for processing."""
        print("\n=== Step 3: Uploading Files ===")
        
        if not self.conversation_ids:
            print("❌ No conversations available for file upload")
            return False
        
        # Use the first conversation for file uploads
        conversation_id = self.conversation_ids[0]
        print(f"Using conversation ID: {conversation_id}")
        
        # Create sample files
        sample_files = self._create_sample_files()
        
        for file_path, filename, description in sample_files:
            print(f"\nUploading: {filename}")
            print(f"Description: {description}")
            
            try:
                with open(file_path, 'rb') as file:
                    files = {'file': (filename, file)}
                    result = self.make_request(f'/api/v1/conversations/{conversation_id}/upload', 'POST', files=files)
                    
                    if result['success']:
                        file_data = result['data']
                        self.uploaded_files.append(file_data)
                        print(f"✅ Upload successful:")
                        print(f"   File ID: {file_data['id']}")
                        print(f"   Type: {file_data['file_type']}")
                        print(f"   Size: {file_data['file_size']} bytes")
                    else:
                        print(f"❌ Upload failed: {result['error']}")
                
                # Clean up temporary file
                os.unlink(file_path)
                
            except Exception as e:
                print(f"❌ Error uploading {filename}: {str(e)}")
        
        return len(self.uploaded_files) > 0
    
    def step_4_fetch_and_analyze_urls(self):
        """Step 4: Fetch web content and analyze it."""
        print("\n=== Step 4: Fetching and Analyzing Web Content ===")
        
        test_urls = [
            {
                'url': 'https://jsonplaceholder.typicode.com/posts/1',
                'question': 'What is the main topic and content of this post?'
            },
            {
                'url': 'https://httpbin.org/json',
                'question': 'What data structure is shown in this JSON response?'
            }
        ]
        
        for url_data in test_urls:
            print(f"\nFetching: {url_data['url']}")
            
            # Fetch URL content
            result = self.make_request('/api/v1/fetch-url', 'POST', {'url': url_data['url']})
            
            if result['success']:
                content_data = result['data']
                content = content_data['content']
                print(f"✅ Fetched {len(content)} characters")
                
                # Ask question about the content
                print(f"Question: {url_data['question']}")
                
                chat_result = self.make_request('/api/v1/chat', 'POST', {
                    'question': url_data['question'],
                    'dataset': content
                })
                
                if chat_result['success']:
                    response = chat_result['data']['response']
                    print(f"✅ AI Response: {response[:200]}..." if len(response) > 200 else f"✅ AI Response: {response}")
                else:
                    print(f"❌ Failed to get AI response: {chat_result['error']}")
            else:
                print(f"❌ Failed to fetch URL: {result['error']}")
        
        return True
    
    def step_5_chat_interactions(self):
        """Step 5: Demonstrate various chat interactions."""
        print("\n=== Step 5: AI Chat Interactions ===")
        
        questions = [
            "What are the key benefits of using APIs for software integration?",
            "Explain the concept of file processing in AI systems.",
            "How can web scraping and content analysis be useful for businesses?"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\nQuestion {i}: {question}")
            
            result = self.make_request('/api/v1/chat', 'POST', {
                'question': question,
                'dataset': ''
            })
            
            if result['success']:
                response = result['data']['response']
                model = result['data']['model']
                print(f"✅ AI Response ({model}):")
                print(f"   {response[:300]}..." if len(response) > 300 else f"   {response}")
            else:
                print(f"❌ Chat failed: {result['error']}")
        
        return True
    
    def step_6_retrieve_processed_content(self):
        """Step 6: Retrieve and display processed file content."""
        print("\n=== Step 6: Retrieving Processed Content ===")
        
        if not self.uploaded_files:
            print("❌ No uploaded files to check")
            return False
        
        for file_data in self.uploaded_files:
            file_id = file_data['id']
            filename = file_data['filename']
            
            print(f"\nChecking file: {filename} (ID: {file_id})")
            
            # Get file details
            result = self.make_request(f'/api/files/{file_id}/details')
            
            if result['success']:
                details = result['data']
                status = self._get_processing_status_text(details['has_been_processed'])
                print(f"   Processing Status: {status}")
                
                if details.get('processed_content'):
                    content = details['processed_content']
                    print(f"   ✅ Processed content available ({len(content)} chars)")
                    print(f"   Preview: {content[:150]}..." if len(content) > 150 else f"   Content: {content}")
                else:
                    print(f"   ⏳ No processed content yet")
                    if details['has_been_processed'] == 0:
                        print(f"   💡 Tip: Start the background worker to process files")
            else:
                print(f"   ❌ Error getting file details: {result['error']}")
        
        return True
    
    def step_7_summary_and_cleanup(self):
        """Step 7: Provide summary and show how to clean up."""
        print("\n=== Step 7: Workflow Summary ===")
        
        # Get final project and conversation counts
        projects_result = self.make_request('/api/v1/projects')
        conversations_result = self.make_request('/api/v1/conversations')
        
        if projects_result['success'] and conversations_result['success']:
            projects = projects_result['data']['projects']
            conversations = conversations_result['data']['conversations']
            
            print(f"📊 Workflow Results:")
            print(f"   - Total projects: {len(projects)}")
            print(f"   - Total conversations: {len(conversations)}")
            print(f"   - Files uploaded: {len(self.uploaded_files)}")
            print(f"   - Created project ID: {self.project_id}")
            print(f"   - Created conversation IDs: {', '.join(map(str, self.conversation_ids))}")
            
            # Show conversations with file counts
            conversations_with_files = [c for c in conversations if c['file_count'] > 0]
            print(f"   - Conversations with files: {len(conversations_with_files)}")
        
        print(f"\n✅ Complete workflow demonstration finished!")
        print(f"\n🔄 Next steps:")
        print(f"   1. Check the web interface to see your created projects and conversations")
        print(f"   2. Start the background worker to process uploaded files:")
        print(f"      cd /home/derek/AI_CLI")
        print(f"      source venv/bin/activate")
        print(f"      python process_unprocessed_files.py --loop")
        print(f"   3. Run individual example scripts to explore specific features")
        print(f"   4. Use the API in your own applications")
        
        return True
    
    def _create_sample_files(self):
        """Create sample files for upload testing."""
        files_created = []
        
        # Text file
        text_content = f"""Complete Workflow Demo File
==========================

Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This file demonstrates the complete AI CLI API workflow including:

1. Project Creation
   - Organize related conversations and files
   - Provide structure for complex tasks

2. Conversation Management
   - Create multiple conversations for different purposes
   - Track messages and file attachments

3. File Upload and Processing
   - Support for multiple file types
   - Automatic content extraction and indexing
   - Background processing for scalability

4. Web Content Fetching
   - Retrieve content from any URL
   - Ask questions about fetched content
   - Combine web data with AI analysis

5. AI Chat Interactions
   - Natural language processing
   - Context-aware responses
   - Integration with uploaded content

This workflow demonstrates the full capabilities of the AI CLI system
for building intelligent applications that can process files, analyze
web content, and provide AI-powered insights.
"""
        
        text_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        text_file.write(text_content)
        text_file.close()
        files_created.append((text_file.name, 'workflow-demo.txt', 'Complete workflow demonstration file'))
        
        # JSON configuration file
        json_content = {
            "workflow_demo": {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "components": {
                    "project_management": {
                        "enabled": True,
                        "features": ["create", "list", "organize"]
                    },
                    "conversation_management": {
                        "enabled": True,
                        "features": ["create", "list", "message_tracking"]
                    },
                    "file_processing": {
                        "enabled": True,
                        "supported_types": ["text", "documents", "images", "audio", "archives"],
                        "max_size_mb": 100
                    },
                    "web_content_fetching": {
                        "enabled": True,
                        "features": ["url_fetch", "content_analysis"]
                    },
                    "ai_chat": {
                        "enabled": True,
                        "features": ["natural_language", "context_aware", "content_integration"]
                    }
                },
                "api_endpoints": {
                    "projects": ["/api/v1/projects"],
                    "conversations": ["/api/v1/conversations"],
                    "file_upload": ["/api/v1/conversations/{id}/upload"],
                    "url_fetch": ["/api/v1/fetch-url"],
                    "chat": ["/api/v1/chat"]
                }
            }
        }
        
        json_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(json_content, json_file, indent=2)
        json_file.close()
        files_created.append((json_file.name, 'workflow-config.json', 'Workflow configuration and metadata'))
        
        return files_created
    
    def _get_processing_status_text(self, status):
        """Convert processing status number to text."""
        status_map = {
            0: 'Unprocessed',
            1: 'Processing',
            2: 'Processed',
            4: 'Do Not Process'
        }
        return status_map.get(status, 'Unknown')
    
    def run_complete_workflow(self):
        """Run the complete workflow demonstration."""
        print("🚀 Starting Complete AI CLI API Workflow Demonstration")
        print("=" * 60)
        
        steps = [
            self.step_1_create_project,
            self.step_2_create_conversations,
            self.step_3_upload_files,
            self.step_4_fetch_and_analyze_urls,
            self.step_5_chat_interactions,
            self.step_6_retrieve_processed_content,
            self.step_7_summary_and_cleanup
        ]
        
        for i, step in enumerate(steps, 1):
            try:
                success = step()
                if not success:
                    print(f"\n⚠️  Step {i} encountered issues but continuing...")
                
                # Small delay between steps for readability
                time.sleep(1)
                
            except Exception as e:
                print(f"\n❌ Step {i} failed with error: {str(e)}")
                print("Continuing with remaining steps...")
        
        print("\n" + "=" * 60)
        print("🎉 Complete workflow demonstration finished!")

def main():
    """Main function to run the complete workflow."""
    print("Complete Workflow Example - AI CLI API")
    print("This script demonstrates all major API features in a single workflow.\n")
    
    # Check if API key is configured
    if API_KEY == 'YOUR_API_KEY_HERE':
        print("❌ Please configure your API key in the script before running!")
        print("   1. Get your API key from the AI CLI admin interface")
        print("   2. Replace 'YOUR_API_KEY_HERE' with your actual API key")
        print("   3. Update BASE_URL if needed")
        return
    
    # Initialize and run workflow
    workflow = AICliWorkflow(API_KEY, BASE_URL)
    workflow.run_complete_workflow()

if __name__ == "__main__":
    main()
