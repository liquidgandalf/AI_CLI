#!/usr/bin/env python3
"""
Project Management Example - Python

This example shows how to create and manage projects via the API.
"""

import requests
import json
from datetime import datetime

# Configuration
API_KEY = 'YOUR_API_KEY_HERE'  # Replace with your actual API key
BASE_URL = 'http://localhost:5785'  # Update for your server

class ProjectManager:
    """Class to manage project operations."""
    
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def list_projects(self):
        """List all projects for the API key user."""
        url = f"{self.base_url}/api/v1/projects"
        
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
    
    def create_project(self, name, description=''):
        """Create a new project."""
        url = f"{self.base_url}/api/v1/projects"
        
        data = {
            'name': name,
            'description': description
        }
        
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
    
    def list_conversations(self):
        """List conversations to see project associations."""
        url = f"{self.base_url}/api/v1/conversations"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            else:
                return {'success': False, 'error': 'Failed to list conversations'}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Connection error: {str(e)}'}

def format_project_info(project):
    """Format project information for display."""
    created = datetime.fromisoformat(project['created_at'].replace('Z', '+00:00'))
    updated = datetime.fromisoformat(project['updated_at'].replace('Z', '+00:00'))
    
    status_flags = []
    if project.get('is_archived'):
        status_flags.append('📦 Archived')
    if project.get('is_hidden'):
        status_flags.append('👁️ Hidden')
    
    status = ' | '.join(status_flags) if status_flags else 'Active'
    
    return f"""  - ID: {project['id']}
    Name: {project['name']}
    Description: {project['description'] if project['description'] else 'No description'}
    Conversations: {project['conversation_count']}
    Status: {status}
    Created: {created.strftime('%Y-%m-%d %H:%M:%S')}
    Updated: {updated.strftime('%Y-%m-%d %H:%M:%S')}"""

def main():
    """Main function to demonstrate project management."""
    
    print("=== Project Management Example ===\n")
    
    # Initialize the project manager
    manager = ProjectManager(API_KEY, BASE_URL)
    
    # 1. List existing projects
    print("1. Listing existing projects...")
    result = manager.list_projects()
    
    if result['success']:
        projects = result['data']['projects']
        print(f"✅ Found {len(projects)} project(s):")
        
        if projects:
            for project in projects:
                print(format_project_info(project))
        else:
            print("  No projects found.")
        print()
    else:
        print(f"❌ Error listing projects: {result['error']}")
        return
    
    # 2. Create sample projects
    print("2. Creating sample projects...")
    
    sample_projects = [
        {
            'name': f'API Development Project - {datetime.now().strftime("%Y-%m-%d")}',
            'description': 'Project for testing API functionality, file uploads, and conversation management.'
        },
        {
            'name': f'Data Analysis Project - {datetime.now().strftime("%Y-%m-%d")}',
            'description': 'Project for analyzing uploaded files, processing transcripts, and generating insights.'
        },
        {
            'name': f'Documentation Project - {datetime.now().strftime("%Y-%m-%d")}',
            'description': 'Project for organizing documentation, examples, and user guides.'
        }
    ]
    
    created_projects = []
    
    for project_data in sample_projects:
        print(f"   Creating: {project_data['name']}")
        
        result = manager.create_project(project_data['name'], project_data['description'])
        
        if result['success']:
            new_project = result['data']
            created_projects.append(new_project)
            print(f"   ✅ Created project ID: {new_project['id']}")
        else:
            print(f"   ❌ Error creating project: {result['error']}")
    
    print()
    
    # 3. List projects again to see the new ones
    print("3. Listing updated project list...")
    result = manager.list_projects()
    
    if result['success']:
        projects = result['data']['projects']
        print(f"✅ Updated project list ({len(projects)} total):")
        
        for project in projects:
            if project['id'] in [p['id'] for p in created_projects]:
                print("  ➤ NEW PROJECT:")
                print(format_project_info(project))
            else:
                print(format_project_info(project))
        print()
    else:
        print(f"❌ Error listing updated projects: {result['error']}")
    
    # 4. Show conversation-project relationships
    print("4. Analyzing conversation-project relationships...")
    result = manager.list_conversations()
    
    if result['success']:
        conversations = result['data']['conversations']
        
        # Group conversations by project
        conversations_by_project = {}
        unassigned_conversations = []
        
        for conv in conversations:
            project_id = conv.get('project_id')
            if project_id:
                if project_id not in conversations_by_project:
                    conversations_by_project[project_id] = []
                conversations_by_project[project_id].append(conv)
            else:
                unassigned_conversations.append(conv)
        
        print(f"📊 Conversation-Project Analysis:")
        print(f"  - Total conversations: {len(conversations)}")
        print(f"  - Conversations in projects: {len(conversations) - len(unassigned_conversations)}")
        print(f"  - Unassigned conversations: {len(unassigned_conversations)}")
        print(f"  - Projects with conversations: {len(conversations_by_project)}")
        
        if conversations_by_project:
            print(f"\n📁 Project-Conversation Breakdown:")
            for project_id, convs in conversations_by_project.items():
                # Find project name
                project_name = "Unknown Project"
                if result['success']:
                    project_list = manager.list_projects()
                    if project_list['success']:
                        for proj in project_list['data']['projects']:
                            if proj['id'] == project_id:
                                project_name = proj['name']
                                break
                
                print(f"  - Project {project_id} ({project_name}): {len(convs)} conversation(s)")
                for conv in convs[:3]:  # Show first 3 conversations
                    print(f"    • {conv['title']} (ID: {conv['id']})")
                if len(convs) > 3:
                    print(f"    • ... and {len(convs) - 3} more")
        
        if unassigned_conversations:
            print(f"\n📝 Unassigned Conversations:")
            for conv in unassigned_conversations[:5]:  # Show first 5
                print(f"  - {conv['title']} (ID: {conv['id']})")
            if len(unassigned_conversations) > 5:
                print(f"  - ... and {len(unassigned_conversations) - 5} more")
        
    else:
        print(f"❌ Error analyzing conversations: {result['error']}")
    
    print("\n=== Project Management Complete ===")
    
    if created_projects:
        print(f"\n📁 Successfully created {len(created_projects)} project(s):")
        for project in created_projects:
            print(f"   - {project['name']} (ID: {project['id']})")
        
        print("\n🔄 Next steps you can try:")
        print("1. Use the web interface to move conversations into projects")
        print("2. Create conversations and assign them to projects")
        print("3. Upload files to conversations within projects")
        print("4. Use project organization to manage related conversations")
        print("5. Archive or hide projects when they're complete")
    else:
        print("\n❌ No projects were successfully created")

if __name__ == "__main__":
    main()
