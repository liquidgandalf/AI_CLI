#!/usr/bin/env python3
"""
Conversation Management Example - Python

This example shows how to create conversations, list them, and manage conversation data.
"""

import requests
import json
from datetime import datetime

# Configuration
API_KEY = 'YOUR_API_KEY_HERE'  # Replace with your actual API key
BASE_URL = 'http://localhost:5785'  # Update for your server

class ConversationManager:
    """Class to manage conversation operations."""
    
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def list_conversations(self):
        """List all conversations for the API key user."""
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
    
    def create_conversation(self, title):
        """Create a new conversation."""
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
    
    def send_chat_message(self, question, dataset=''):
        """Send a chat message (this will be associated with conversations automatically)."""
        url = f"{self.base_url}/api/v1/chat"
        
        data = {
            'question': question,
            'dataset': dataset
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=60)
            
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

def format_conversation_info(conv):
    """Format conversation information for display."""
    created = datetime.fromisoformat(conv['created_at'].replace('Z', '+00:00'))
    updated = datetime.fromisoformat(conv['updated_at'].replace('Z', '+00:00'))
    
    status_flags = []
    if conv.get('is_starred'):
        status_flags.append('⭐ Starred')
    if conv.get('is_archived'):
        status_flags.append('📦 Archived')
    if conv.get('is_hidden'):
        status_flags.append('👁️ Hidden')
    
    status = ' | '.join(status_flags) if status_flags else 'Active'
    
    return f"""  - ID: {conv['id']}
    Title: {conv['title']}
    Messages: {conv['message_count']} | Files: {conv['file_count']}
    Status: {status}
    Created: {created.strftime('%Y-%m-%d %H:%M:%S')}
    Updated: {updated.strftime('%Y-%m-%d %H:%M:%S')}
    Project: {conv['project_id'] if conv['project_id'] else 'None'}"""

def main():
    """Main function to demonstrate conversation management."""
    
    print("=== Conversation Management Example ===\n")
    
    # Initialize the conversation manager
    manager = ConversationManager(API_KEY, BASE_URL)
    
    # 1. List existing conversations
    print("1. Listing existing conversations...")
    result = manager.list_conversations()
    
    if result['success']:
        conversations = result['data']['conversations']
        print(f"✅ Found {len(conversations)} conversation(s):")
        
        if conversations:
            for conv in conversations:
                print(format_conversation_info(conv))
        else:
            print("  No conversations found.")
        print()
    else:
        print(f"❌ Error listing conversations: {result['error']}")
        return
    
    # 2. Create a new conversation
    print("2. Creating a new conversation...")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_title = f"API Test Conversation - {timestamp}"
    
    result = manager.create_conversation(new_title)
    
    if result['success']:
        new_conv = result['data']
        print("✅ Created new conversation:")
        print(f"  - ID: {new_conv['id']}")
        print(f"  - Title: {new_conv['title']}")
        print(f"  - Created: {new_conv['created_at']}")
        print(f"  - User ID: {new_conv['user_id']}")
        print()
        
        conversation_id = new_conv['id']
    else:
        print(f"❌ Error creating conversation: {result['error']}")
        return
    
    # 3. Send a message to test the conversation system
    print("3. Sending a test message...")
    test_message = "Hello! This is a test message sent via the Python API. Can you confirm you received this and tell me what capabilities you have?"
    
    result = manager.send_chat_message(test_message)
    
    if result['success']:
        response_data = result['data']
        print("✅ AI Response received:")
        print("=" * 50)
        print(response_data['response'][:200] + "..." if len(response_data['response']) > 200 else response_data['response'])
        print("=" * 50)
        print(f"Model: {response_data['model']}")
        print(f"Prompt Length: {response_data['prompt_length']} characters")
        print()
    else:
        print(f"❌ Error sending message: {result['error']}")
    
    # 4. List conversations again to see the updated count
    print("4. Listing conversations again to see updates...")
    result = manager.list_conversations()
    
    if result['success']:
        conversations = result['data']['conversations']
        print(f"✅ Updated conversation list ({len(conversations)} total):")
        
        for conv in conversations:
            if conv['id'] == conversation_id:
                print("  ➤ NEW CONVERSATION:")
                print(format_conversation_info(conv))
            else:
                print(format_conversation_info(conv))
        print()
    else:
        print(f"❌ Error listing updated conversations: {result['error']}")
    
    # 5. Demonstrate conversation filtering
    print("5. Analyzing conversation data...")
    if result['success']:
        conversations = result['data']['conversations']
        
        # Count different types
        active_count = len([c for c in conversations if not c.get('is_archived') and not c.get('is_hidden')])
        starred_count = len([c for c in conversations if c.get('is_starred')])
        with_files_count = len([c for c in conversations if c['file_count'] > 0])
        in_projects_count = len([c for c in conversations if c['project_id']])
        
        print(f"📊 Conversation Statistics:")
        print(f"  - Total conversations: {len(conversations)}")
        print(f"  - Active conversations: {active_count}")
        print(f"  - Starred conversations: {starred_count}")
        print(f"  - Conversations with files: {with_files_count}")
        print(f"  - Conversations in projects: {in_projects_count}")
    
    print("\n=== Conversation Management Complete ===")
    print("\nNext steps you can try:")
    print("- Run file_upload.py to add files to conversations")
    print("- Run project_management.py to organize conversations into projects")
    print("- Use the web interface to star, hide, or archive conversations")

if __name__ == "__main__":
    main()
