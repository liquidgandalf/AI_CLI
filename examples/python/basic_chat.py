#!/usr/bin/env python3
"""
Basic Chat Example - Python

This example shows how to send a simple question to the AI and get a response.
"""

import requests
import json

# Configuration
API_KEY = 'YOUR_API_KEY_HERE'  # Replace with your actual API key
BASE_URL = 'http://localhost:5785'  # Update for your server

def send_chat_message(question, dataset=''):
    """Send a chat message to the AI and return the response."""
    
    url = f"{BASE_URL}/api/v1/chat"
    
    headers = {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    data = {
        'question': question,
        'dataset': dataset
    }
    
    try:
        print(f"Sending question: {question}")
        print("Waiting for AI response...\n")
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            return {
                'success': True,
                'response': result['response'],
                'model': result['model'],
                'prompt_length': result['prompt_length']
            }
        else:
            error_data = response.json() if response.content else {'error': 'Unknown error'}
            return {
                'success': False,
                'error': error_data.get('error', 'Unknown error'),
                'status_code': response.status_code
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'Connection error: {str(e)}',
            'status_code': None
        }
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error': f'JSON decode error: {str(e)}',
            'status_code': response.status_code if 'response' in locals() else None
        }

def main():
    """Main function to demonstrate basic chat functionality."""
    
    # Example questions to ask
    questions = [
        "What is artificial intelligence?",
        "Explain the concept of machine learning in simple terms.",
        "What are the benefits of using APIs for software integration?"
    ]
    
    print("=== Basic Chat Example ===\n")
    
    for i, question in enumerate(questions, 1):
        print(f"--- Question {i} ---")
        
        result = send_chat_message(question)
        
        if result['success']:
            print("✅ AI Response:")
            print("=" * 50)
            print(result['response'])
            print("\n📊 Response Details:")
            print(f"Model: {result['model']}")
            print(f"Prompt Length: {result['prompt_length']} characters")
        else:
            print("❌ Error occurred:")
            print(f"Status Code: {result['status_code']}")
            print(f"Error: {result['error']}")
        
        print("\n" + "="*60 + "\n")
    
    # Example with context/dataset
    print("--- Question with Context ---")
    context = """
    The AI CLI system is a web-based chat interface that allows users to:
    - Have conversations with AI models
    - Upload and process various file types
    - Organize chats into projects
    - Use API keys for remote access
    """
    
    question_with_context = "Based on the provided information, what are the main features of the AI CLI system?"
    
    result = send_chat_message(question_with_context, context)
    
    if result['success']:
        print("✅ AI Response with Context:")
        print("=" * 50)
        print(result['response'])
        print(f"\n📊 Model: {result['model']}")
    else:
        print("❌ Error with context question:")
        print(f"Error: {result['error']}")
    
    print("\n=== Basic Chat Example Complete ===")

if __name__ == "__main__":
    main()
