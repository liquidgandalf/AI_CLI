#!/usr/bin/env python3
"""
URL Fetching Example - Python

This example shows how to fetch web content and ask questions about it.
"""

import requests
import json

# Configuration
API_KEY = 'YOUR_API_KEY_HERE'  # Replace with your actual API key
BASE_URL = 'http://localhost:5785'  # Update for your server

class URLFetcher:
    """Class to manage URL fetching operations."""
    
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def fetch_url(self, url):
        """Fetch content from a URL."""
        api_url = f"{self.base_url}/api/v1/fetch-url"
        
        data = {'url': url}
        
        try:
            response = requests.post(api_url, headers=self.headers, json=data, timeout=60)
            
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
    
    def ask_about_content(self, question, content):
        """Ask a question about fetched content."""
        api_url = f"{self.base_url}/api/v1/chat"
        
        data = {
            'question': question,
            'dataset': content
        }
        
        try:
            response = requests.post(api_url, headers=self.headers, json=data, timeout=60)
            
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

def main():
    """Main function to demonstrate URL fetching functionality."""
    
    print("=== URL Fetching Example ===\n")
    
    # Initialize the URL fetcher
    fetcher = URLFetcher(API_KEY, BASE_URL)
    
    # Example URLs to fetch and analyze
    test_urls = [
        {
            'url': 'https://httpbin.org/json',
            'description': 'JSON test endpoint',
            'questions': [
                'What data is contained in this JSON response?',
                'What is the slideshow title mentioned in this data?'
            ]
        },
        {
            'url': 'https://jsonplaceholder.typicode.com/posts/1',
            'description': 'Sample blog post data',
            'questions': [
                'What is the title and content of this post?',
                'Who is the author of this post (user ID)?'
            ]
        },
        {
            'url': 'https://api.github.com/repos/microsoft/vscode/readme',
            'description': 'VS Code repository README',
            'questions': [
                'What is this repository about?',
                'What programming language is primarily used?'
            ]
        }
    ]
    
    for i, url_data in enumerate(test_urls, 1):
        print(f"--- Example {i}: {url_data['description']} ---")
        print(f"URL: {url_data['url']}")
        
        # 1. Fetch the URL content
        print("Fetching URL content...")
        result = fetcher.fetch_url(url_data['url'])
        
        if result['success']:
            content_data = result['data']
            content = content_data['content']
            
            print("✅ URL fetched successfully!")
            print(f"  - Content length: {len(content)} characters")
            print(f"  - Content type: {content_data.get('content_type', 'unknown')}")
            print(f"  - Status code: {content_data.get('status_code', 'unknown')}")
            
            # Show a preview of the content
            print(f"\n📄 Content Preview (first 300 chars):")
            print("-" * 50)
            print(content[:300] + ("..." if len(content) > 300 else ""))
            print("-" * 50)
            
            # 2. Ask questions about the content
            print(f"\n🤔 Asking questions about the content:")
            
            for j, question in enumerate(url_data['questions'], 1):
                print(f"\n  Question {j}: {question}")
                
                result = fetcher.ask_about_content(question, content)
                
                if result['success']:
                    response_data = result['data']
                    print(f"  ✅ AI Answer:")
                    print(f"  {response_data['response']}")
                    print(f"  (Model: {response_data['model']})")
                else:
                    print(f"  ❌ Error asking question: {result['error']}")
        
        else:
            print(f"❌ Error fetching URL: {result['error']}")
            
            # Try to provide helpful error information
            if 'status_code' in result:
                print(f"   HTTP Status: {result['status_code']}")
            
            print("   This might be due to:")
            print("   - Network connectivity issues")
            print("   - URL not accessible")
            print("   - Server blocking requests")
            print("   - Invalid URL format")
        
        print("\n" + "="*60 + "\n")
    
    # Demonstrate custom URL fetching
    print("--- Custom URL Example ---")
    print("You can also fetch any URL of your choice:")
    
    # Example with a custom URL (you can modify this)
    custom_url = "https://httpbin.org/user-agent"
    custom_question = "What user agent information is shown in this response?"
    
    print(f"Custom URL: {custom_url}")
    print(f"Custom Question: {custom_question}")
    
    result = fetcher.fetch_url(custom_url)
    
    if result['success']:
        content = result['data']['content']
        print(f"✅ Custom URL fetched successfully!")
        print(f"Content: {content}")
        
        # Ask the custom question
        result = fetcher.ask_about_content(custom_question, content)
        
        if result['success']:
            print(f"\n✅ AI Answer to custom question:")
            print(f"{result['data']['response']}")
        else:
            print(f"❌ Error with custom question: {result['error']}")
    else:
        print(f"❌ Error fetching custom URL: {result['error']}")
    
    print("\n=== URL Fetching Complete ===")
    print("\n🔄 Next steps you can try:")
    print("1. Modify the test_urls list to fetch different websites")
    print("2. Change the questions to ask different things about the content")
    print("3. Combine URL fetching with conversation management")
    print("4. Use fetched content as context for further AI conversations")
    print("5. Save interesting fetched content as files for processing")
    
    print("\n💡 Use cases for URL fetching:")
    print("- Analyze news articles or blog posts")
    print("- Extract data from API endpoints")
    print("- Research topics by fetching relevant web pages")
    print("- Monitor website changes")
    print("- Gather information for reports or summaries")

if __name__ == "__main__":
    main()
