#!/usr/bin/env python3
"""
AI Chat Interface with Google Authentication and Conversation History
Connects to local Ollama service for AI responses
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import os
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_db, get_db, User, Conversation, Message, ApiKey, Project, ChatFile
from file_utils import save_uploaded_file, get_file_full_path, format_file_size
from datetime import datetime
import os
import asyncio
import hashlib
from playwright.async_api import async_playwright
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize database
init_db()

class FlaskUser(UserMixin):
    def __init__(self, user_id, username, email, name, allowedaccess='no', is_admin=False, created_at=None):
        self.id = user_id
        self.username = username
        self.email = email
        self.name = name
        self.allowedaccess = allowedaccess
        self.is_admin = is_admin
        self.created_at = created_at

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    try:
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user:
            return FlaskUser(user.id, user.username, user.email, user.name, user.allowedaccess, user.is_admin, user.created_at)
    finally:
        db.close()
    return None

# Access Control
def access_required(f):
    """Decorator to require user to have allowed access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        
        db = get_db()
        try:
            user = db.query(User).filter(User.id == current_user.id).first()
            if not user or user.allowedaccess != 'yes':
                flash('Access denied. Your account does not have permission to use this system.', 'error')
                return redirect(url_for('logout'))
        finally:
            db.close()
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        
        db = get_db()
        try:
            user = db.query(User).filter(User.id == current_user.id).first()
            if not user or not user.is_admin or user.allowedaccess != 'yes':
                flash('Admin access required.', 'error')
                return redirect(url_for('chat'))
        finally:
            db.close()
        
        return f(*args, **kwargs)
    return decorated_function

# API Key Authentication
def api_key_required(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for API key in headers
        api_key = request.headers.get('X-API-Key') or request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # Hash the provided key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Look up the API key in database
        db = get_db()
        try:
            api_key_record = db.query(ApiKey).filter(
                ApiKey.key_hash == key_hash,
                ApiKey.is_active == True
            ).first()
            
            if not api_key_record:
                return jsonify({'error': 'Invalid API key'}), 401
            
            # Update last used timestamp
            api_key_record.last_used = datetime.utcnow()
            db.commit()
            
            # Get the user for this API key
            user = db.query(User).filter(User.id == api_key_record.user_id).first()
            if not user:
                return jsonify({'error': 'User not found'}), 401
            
            # Store user info in request context
            request.api_user = user
            
        finally:
            db.close()
        
        return f(*args, **kwargs)
    return decorated_function

# Configuration
OLLAMA_URL = os.environ.get('OLLAMA_URL', "http://localhost:11434/api/generate")
DEFAULT_MODEL = "gpt-oss:20b"  # OpenAI's open-weight model - 20B parameters, ~3.6B active per token
MAX_PROMPT_LENGTH = 4000  # Conservative limit for context window
AI_TIMEOUT_SECONDS = 600  # 10 minutes - perfect for complex analysis on dedicated AI server

def build_conversation_prompt(dataset, question, history):
    """
    Build a conversation prompt with history management for token limits.
    
    Strategy: Put the most important parts (current dataset + question) at the end
    so they survive if the model truncates from the beginning.
    If the model truncates from the end, we'll reverse the order.
    
    For now, assuming truncation from beginning (most common).
    """
    
    # Current dataset and question (most important - goes at end)
    # Make it clear to the AI that it has access to the provided data
    if dataset.strip():
        if "Source URL:" in dataset:
            current_context = f"You have been provided with content from a web page. Here is the data:\n\n{dataset}\n\nBased on this provided data, please answer the following question:\n{question}"
        else:
            current_context = f"You have been provided with the following dataset:\n\n{dataset}\n\nBased on this provided data, please answer the following question:\n{question}"
    else:
        current_context = f"Question: {question}"
    
    # If no history, just return current context
    if not history:
        return current_context
    
    # Build history string
    history_parts = []
    for item in history[:-1]:  # Exclude the current message we just added
        if item['type'] == 'user':
            history_parts.append(f"Previous Dataset: {item.get('dataset', '')}")
            history_parts.append(f"Previous Question: {item.get('question', '')}")
        elif item['type'] == 'ai':
            history_parts.append(f"Previous Response: {item.get('response', '')}")
    
    history_text = "\n\n".join(history_parts)
    
    # Combine history with current context
    if history_text:
        full_prompt = f"Conversation History:\n{history_text}\n\n---\n\nCurrent Context:\n{current_context}"
    else:
        full_prompt = current_context
    
    # If prompt is too long, truncate history but keep current context
    if len(full_prompt) > MAX_PROMPT_LENGTH:
        # Calculate how much space we have for history
        current_context_length = len(current_context) + 50  # +50 for formatting
        available_for_history = MAX_PROMPT_LENGTH - current_context_length
        
        if available_for_history > 100:  # Only include history if we have reasonable space
            truncated_history = history_text[:available_for_history] + "..."
            full_prompt = f"Conversation History (truncated):\n{truncated_history}\n\n---\n\nCurrent Context:\n{current_context}"
        else:
            # Not enough space for history, just use current context
            full_prompt = current_context
    
    return full_prompt

@app.route('/')
def index():
    """Redirect to login or chat based on authentication"""
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password')
            return render_template('login.html')
        
        db = get_db()
        try:
            user = db.query(User).filter(User.username == username).first()
            
            if user and check_password_hash(user.password_hash, password):
                flask_user = FlaskUser(user.id, user.username, user.email, user.name, user.allowedaccess, user.is_admin, user.created_at)
                login_user(flask_user)
                return redirect(url_for('chat'))
            else:
                flash('Invalid username or password')
        finally:
            db.close()
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register new user"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        
        if not username or not email or not password or not name:
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        db = get_db()
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                flash('Username or email already exists', 'error')
                return render_template('register.html')
            
            # Check if this is the first user
            user_count = db.query(User).count()
            is_first_user = user_count == 0
            
            # Create new user
            password_hash = generate_password_hash(password)
            new_user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                name=name,
                allowedaccess='yes' if is_first_user else 'no',
                is_admin=is_first_user
            )
            
            db.add(new_user)
            db.commit()
            
            if is_first_user:
                flash('Registration successful! You are the first user and have been granted admin access.', 'success')
            else:
                flash('Registration successful! Please wait for admin approval to access the system.', 'info')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.rollback()
            flash('Registration failed. Please try again.', 'error')
            print(f"Registration error: {e}")
            
        finally:
            db.close()
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    return redirect(url_for('login'))

@app.route('/chat')
@login_required
@access_required
def chat():
    """Main chat interface"""
    return render_template('chat.html')

@app.route('/api/user-info')
@login_required
@access_required
def get_user_info():
    """Get current user information"""
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'name': current_user.name
    })

@app.route('/api/chat', methods=['POST'])
@login_required
@access_required
def api_chat():
    """Handle chat requests to AI with dataset/question format and conversation history"""
    try:
        data = request.get_json()
        dataset = data.get('dataset', '')
        question = data.get('question', '')
        history = data.get('history', [])
        conversation_id = data.get('conversation_id')
        selected_model = data.get('model', DEFAULT_MODEL)
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Build the full prompt with conversation history
        prompt = build_conversation_prompt(dataset, question, history)
        
        # Debug: Log the prompt being sent to AI (first 500 chars)
        print(f"\n=== AI PROMPT DEBUG ===")
        print(f"Dataset length: {len(dataset)} characters")
        print(f"Question: {question}")
        print(f"Prompt preview (first 500 chars): {prompt[:500]}...")
        print(f"=== END DEBUG ===")
        
        # Send request to Ollama
        ollama_payload = {
            "model": selected_model,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(OLLAMA_URL, json=ollama_payload, timeout=AI_TIMEOUT_SECONDS)
        response.raise_for_status()
        
        ai_response = response.json()
        ai_text = ai_response.get('response', 'No response received')
        
        # Save to database
        db = get_db()
        try:
            # Create or get conversation
            if conversation_id:
                conversation = db.query(Conversation).filter(
                    Conversation.id == conversation_id,
                    Conversation.user_id == current_user.id
                ).first()
            else:
                conversation = None
            
            if not conversation:
                # Create new conversation with auto-generated title
                title = question[:50] + "..." if len(question) > 50 else question
                conversation = Conversation(
                    user_id=current_user.id,
                    title=title,
                    dataset=dataset
                )
                db.add(conversation)
                db.commit()
                db.refresh(conversation)
            
            # Save user message
            user_message = Message(
                conversation_id=conversation.id,
                message_type='user',
                question=question
            )
            db.add(user_message)
            
            # Save AI response
            ai_message = Message(
                conversation_id=conversation.id,
                message_type='ai',
                response=ai_text
            )
            db.add(ai_message)
            
            # Update conversation timestamp
            conversation.updated_at = datetime.utcnow()
            db.commit()
            
            return jsonify({
                'response': ai_text,
                'model': ai_response.get('model', DEFAULT_MODEL),
                'prompt_length': len(prompt),
                'conversation_id': conversation.id
            })
            
        finally:
            db.close()
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'AI service error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/models', methods=['GET'])
@login_required
@access_required
def get_models():
    """Get available models from Ollama"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': f'Could not fetch models: {str(e)}'}), 500

@app.route('/api/conversations', methods=['GET'])
@login_required
@access_required
def get_conversations():
    """Get user's active conversations (Level 1: front page, excluding those assigned to projects)"""
    db = get_db()
    try:
        # Only get conversations that are NOT assigned to any project AND are active (not hidden or archived)
        # Sort by starred status first (starred=True first), then by updated_at desc
        conversations = db.query(Conversation).filter(
            Conversation.user_id == current_user.id,
            Conversation.project_id.is_(None),
            Conversation.is_archived == False,
            Conversation.is_hidden == False
        ).order_by(Conversation.is_starred.desc(), Conversation.updated_at.desc()).all()
        
        conversations_data = []
        for conv in conversations:
            conversations_data.append({
                'id': conv.id,
                'title': conv.title,
                'dataset': conv.dataset,
                'is_starred': conv.is_starred,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat(),
                'project_id': conv.project_id
            })
        
        return jsonify(conversations_data)
    finally:
        db.close()

@app.route('/api/conversations', methods=['POST'])
@login_required
@access_required
def create_conversation():
    """Create a new conversation"""
    data = request.get_json()
    title = data.get('title', 'New Chat')
    dataset = data.get('dataset', '')
    
    db = get_db()
    try:
        # Cleanup: remove other empty "New Chat" conversations for this user
        # Only delete conversations that still have the default title and no messages
        old_new_chats = db.query(Conversation).filter(
            Conversation.user_id == current_user.id,
            Conversation.title == 'New Chat'
        ).all()
        for old_conv in old_new_chats:
            # Skip deletion if this conversation has any messages
            msg_count = db.query(Message).filter(Message.conversation_id == old_conv.id).count()
            if msg_count == 0:
                # Delete associated files from disk and database
                files = db.query(ChatFile).filter(ChatFile.conversation_id == old_conv.id).all()
                for chat_file in files:
                    file_path = get_file_full_path(chat_file.file_path)
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except OSError as e:
                            print(f"Warning: Could not delete file {file_path}: {e}")
                    db.delete(chat_file)
                # Delete messages (none expected) and the conversation
                db.query(Message).filter(Message.conversation_id == old_conv.id).delete()
                db.delete(old_conv)
        
        # Create new conversation
        conversation = Conversation(
            user_id=current_user.id,
            title=title,
            dataset=dataset,
            is_starred=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(conversation)
        db.commit()
        
        return jsonify({
            'success': True,
            'conversation_id': conversation.id,
            'id': conversation.id,
            'title': conversation.title,
            'dataset': conversation.dataset,
            'created_at': conversation.created_at.isoformat(),
            'updated_at': conversation.updated_at.isoformat()
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/conversations/<int:conversation_id>', methods=['GET'])
@login_required
@access_required
def get_conversation(conversation_id):
    """Get specific conversation with messages"""
    db = get_db()
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp.asc()).all()
        
        result = {
            'id': conversation.id,
            'title': conversation.title,
            'dataset': conversation.dataset,
            'created_at': conversation.created_at.isoformat(),
            'updated_at': conversation.updated_at.isoformat(),
            'messages': []
        }
        
        for msg in messages:
            result['messages'].append({
                'id': msg.id,
                'type': msg.message_type,
                'question': msg.question,
                'response': msg.response,
                'timestamp': msg.timestamp.isoformat()
            })
        
        return jsonify(result)
    finally:
        db.close()

@app.route('/api/conversations/<int:conversation_id>', methods=['DELETE'])
@login_required
@access_required
def delete_conversation(conversation_id):
    """Delete a conversation and all associated files"""
    db = get_db()
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        # Delete associated files from disk and database
        files = db.query(ChatFile).filter(ChatFile.conversation_id == conversation_id).all()
        for chat_file in files:
            # Delete file from disk
            file_path = get_file_full_path(chat_file.file_path)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError as e:
                    print(f"Warning: Could not delete file {file_path}: {e}")
            
            # Delete file record from database
            db.delete(chat_file)
        
        # Delete messages
        db.query(Message).filter(Message.conversation_id == conversation_id).delete()
        
        # Delete conversation
        db.delete(conversation)
        db.commit()
        
        return jsonify({'success': True, 'message': f'Conversation and {len(files)} associated files deleted'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

def clean_text(text):
    """Clean and normalize text content"""
    # Remove extra whitespace and normalize line breaks
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

def extract_text_from_html(html_content, url):
    """Extract clean text content from HTML with table structure preservation"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
        
        # Process tables first to preserve structure
        for table in soup.find_all('table'):
            table_text = convert_table_to_text(table)
            # Replace the table with formatted text
            table.replace_with(soup.new_string(table_text))
        
        # Add separators for table cells that weren't in tables
        for td in soup.find_all(['td', 'th']):
            if td.string:
                td.string.replace_with(f" {td.get_text().strip()} |")
        
        # Add line breaks for table rows
        for tr in soup.find_all('tr'):
            tr.append(soup.new_string("\n"))
        
        # Get text content
        text = soup.get_text()
        
        # Clean up the text but preserve table formatting
        lines = []
        for line in text.splitlines():
            line = line.strip()
            if line:
                lines.append(line)
        
        text = '\n'.join(lines)
        
        # Add URL info at the beginning
        text = f"Source URL: {url}\n\n{text}"
        
        return clean_text(text)
    except Exception as e:
        return f"Error parsing HTML: {str(e)}"

def convert_table_to_text(table):
    """Convert HTML table to readable text format"""
    try:
        rows = []
        
        # Process each row
        for tr in table.find_all('tr'):
            cells = []
            for cell in tr.find_all(['td', 'th']):
                cell_text = cell.get_text().strip()
                # Clean up cell content
                cell_text = ' '.join(cell_text.split())
                cells.append(cell_text)
            
            if cells:  # Only add non-empty rows
                # Join cells with pipe separator for clear column separation
                row_text = ' | '.join(cells)
                rows.append(row_text)
        
        if rows:
            # Add a separator line after header if it looks like a table with headers
            if len(rows) > 1:
                # Check if first row might be headers (common indicators)
                first_row = rows[0].lower()
                if any(word in first_row for word in ['name', 'date', 'price', 'amount', 'total', 'description', 'item']):
                    header_separator = '-' * min(len(rows[0]), 50)
                    rows.insert(1, header_separator)
            
            return '\n\nTABLE:\n' + '\n'.join(rows) + '\n\n'
        
        return ''
    except Exception as e:
        return f'\n[Table extraction error: {str(e)}]\n'

async def scrape_with_javascript(url):
    """Scrape content from a URL using Playwright to handle JavaScript"""
    try:
        async with async_playwright() as p:
            # Launch browser (headless)
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Set user agent to avoid blocking
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            # Navigate to the page
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait a bit more for any lazy-loaded content
            await page.wait_for_timeout(3000)
            
            # Get the fully rendered HTML
            html_content = await page.content()
            
            # Close browser
            await browser.close()
            
            # Extract text from the rendered HTML
            return extract_text_from_html(html_content, url)
            
    except Exception as e:
        return f"Error scraping with JavaScript: {str(e)}"

@app.route('/api/fetch-url', methods=['POST'])
@login_required
@access_required
def fetch_url():
    """Fetch content from a URL and return clean text (with JavaScript support)"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        use_js = data.get('use_js', True)  # Default to JavaScript scraping
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # Validate URL format
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return jsonify({'error': 'Invalid URL format'}), 400
        
        # Add scheme if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        content = None
        method_used = "unknown"
        
        # Try JavaScript scraping first (for dynamic content)
        if use_js:
            try:
                print(f"Attempting JavaScript scraping for: {url}")
                content = asyncio.run(scrape_with_javascript(url))
                method_used = "javascript"
                print(f"JavaScript scraping successful, content length: {len(content)}")
            except Exception as js_error:
                print(f"JavaScript scraping failed: {str(js_error)}")
                content = None
        
        # Fallback to basic HTTP scraping if JS failed or not requested
        if not content or "Error scraping with JavaScript" in content:
            try:
                print(f"Attempting basic HTTP scraping for: {url}")
                # Set headers to mimic a browser
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
                
                # Fetch the URL
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                
                # Extract text content
                content = extract_text_from_html(response.text, url)
                method_used = "http"
                print(f"HTTP scraping successful, content length: {len(content)}")
                
            except Exception as http_error:
                return jsonify({'error': f'Both JavaScript and HTTP scraping failed. JS: {js_error if "js_error" in locals() else "Not attempted"}, HTTP: {str(http_error)}'}), 500
        
        # With GPT-OSS-20B and your powerful hardware, we can handle large content
        # Only truncate if content is extremely large (>100k chars) to prevent memory issues
        max_length = 100000  # Much more generous limit for your hardware
        original_length = len(content)
        if len(content) > max_length:
            content = content[:max_length] + f"\n\n[Content truncated from {original_length} to {max_length} characters - consider processing in smaller chunks]"
        
        return jsonify({
            'content': content,
            'url': url,
            'method_used': method_used,
            'content_length': len(content),
            'original_length': original_length
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

# Projects Management Endpoints
@app.route('/api/projects', methods=['GET'])
@login_required
@access_required
def get_projects():
    """Get user's active projects (Level 1: front page)"""
    db = get_db()
    try:
        projects = db.query(Project).filter(
            Project.user_id == current_user.id,
            Project.is_archived == False,
            Project.is_hidden == False
        ).order_by(Project.updated_at.desc()).all()
        
        projects_data = []
        for project in projects:
            # Count conversations in this project
            conversation_count = db.query(Conversation).filter(
                Conversation.project_id == project.id
            ).count()
            
            projects_data.append({
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'conversation_count': conversation_count,
                'created_at': project.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': project.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({'projects': projects_data})
    finally:
        db.close()

@app.route('/api/projects', methods=['POST'])
@login_required
@access_required
def create_project():
    """Create a new project"""
    data = request.get_json()
    project_name = data.get('name', '').strip()
    project_description = data.get('description', '').strip()
    
    if not project_name:
        return jsonify({'error': 'Project name is required'}), 400
    
    db = get_db()
    try:
        # Check if project name already exists for this user
        existing_project = db.query(Project).filter(
            Project.user_id == current_user.id,
            Project.name == project_name
        ).first()
        
        if existing_project:
            return jsonify({'error': 'Project name already exists'}), 400
        
        # Create new project
        new_project = Project(
            user_id=current_user.id,
            name=project_name,
            description=project_description
        )
        
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        
        return jsonify({
            'success': True,
            'project': {
                'id': new_project.id,
                'name': new_project.name,
                'description': new_project.description,
                'conversation_count': 0,
                'created_at': new_project.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': new_project.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/conversations/<int:conversation_id>/project', methods=['PUT'])
@login_required
@access_required
def assign_conversation_to_project(conversation_id):
    """Assign a conversation to a project"""
    data = request.get_json()
    project_id = data.get('project_id')
    
    db = get_db()
    try:
        # Verify conversation belongs to current user
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        # If project_id is provided, verify it belongs to current user
        if project_id:
            project = db.query(Project).filter(
                Project.id == project_id,
                Project.user_id == current_user.id
            ).first()
            
            if not project:
                return jsonify({'error': 'Project not found'}), 404
        
        # Update conversation's project assignment
        conversation.project_id = project_id
        conversation.updated_at = datetime.utcnow()
        
        # Update project's updated_at if assigning to a project
        if project_id:
            project.updated_at = datetime.utcnow()
        
        db.commit()
        
        return jsonify({
            'success': True,
            'conversation_id': conversation_id,
            'project_id': project_id
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/projects/<int:project_id>/conversations', methods=['GET'])
@login_required
@access_required
def get_project_conversations(project_id):
    """Get conversations for a specific project"""
    db = get_db()
    try:
        # Verify project belongs to current user
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user.id
        ).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Get conversations for this project
        # Sort by starred status first (starred=True first), then by updated_at desc
        conversations = db.query(Conversation).filter(
            Conversation.project_id == project_id,
            Conversation.user_id == current_user.id
        ).order_by(Conversation.is_starred.desc(), Conversation.updated_at.desc()).all()
        
        conversations_data = []
        for conv in conversations:
            conversations_data.append({
                'id': conv.id,
                'title': conv.title,
                'dataset': conv.dataset,
                'is_starred': conv.is_starred,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat(),
                'project_id': conv.project_id
            })
        
        return jsonify({
            'project': {
                'id': project.id,
                'name': project.name,
                'description': project.description
            },
            'conversations': conversations_data
        })
    finally:
        db.close()

# Chat Management Endpoints
@app.route('/api/conversations/<int:conversation_id>/star', methods=['PUT'])
@login_required
@access_required
def toggle_conversation_star(conversation_id):
    """Toggle starred status of a conversation"""
    db = get_db()
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        # Toggle starred status
        conversation.is_starred = not conversation.is_starred
        conversation.updated_at = datetime.utcnow()
        
        db.commit()
        
        return jsonify({
            'success': True,
            'is_starred': conversation.is_starred,
            'message': 'Starred' if conversation.is_starred else 'Unstarred'
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/conversations/<int:conversation_id>/move-to-project', methods=['PUT'])
@login_required
@access_required
def move_conversation_to_project(conversation_id):
    """Move a conversation to a project"""
    data = request.get_json()
    project_id = data.get('project_id')
    
    if not project_id:
        return jsonify({'error': 'Project ID is required'}), 400
    
    db = get_db()
    try:
        # Verify conversation belongs to current user
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        # Verify project belongs to current user
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user.id
        ).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Move conversation to project
        conversation.project_id = project_id
        conversation.updated_at = datetime.utcnow()
        
        # Update project's updated_at timestamp
        project.updated_at = datetime.utcnow()
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': f'Conversation moved to project "{project.name}" successfully',
            'project_id': project_id,
            'project_name': project.name
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/conversations/<int:conversation_id>/title', methods=['PUT'])
@login_required
@access_required
def update_conversation_title(conversation_id):
    """Update the title of a conversation"""
    data = request.get_json()
    new_title = data.get('title', '').strip()
    
    if not new_title:
        return jsonify({'error': 'Title cannot be empty'}), 400
    
    if len(new_title) > 255:
        return jsonify({'error': 'Title too long (max 255 characters)'}), 400
    
    db = get_db()
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        conversation.title = new_title
        conversation.updated_at = datetime.utcnow()
        
        db.commit()
        
        return jsonify({
            'success': True,
            'title': conversation.title,
            'message': 'Title updated successfully'
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/projects/<int:project_id>/name', methods=['PUT'])
@login_required
@access_required
def update_project_name(project_id):
    """Update the name of a project"""
    data = request.get_json()
    new_name = data.get('name', '').strip()
    
    if not new_name:
        return jsonify({'error': 'Project name cannot be empty'}), 400
    
    if len(new_name) > 255:
        return jsonify({'error': 'Project name too long (max 255 characters)'}), 400
    
    db = get_db()
    try:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user.id
        ).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        project.name = new_name
        project.updated_at = datetime.utcnow()
        
        db.commit()
        
        return jsonify({
            'success': True,
            'name': project.name,
            'message': 'Project name updated successfully'
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

# File Upload and Management Endpoints
@app.route('/api/conversations/<int:conversation_id>/upload', methods=['POST'])
@login_required
@access_required
def upload_file_to_conversation(conversation_id):
    """Upload a file to a specific conversation"""
    db = get_db()
    try:
        # Verify conversation exists and belongs to user
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        try:
            # Read file content to compute MD5 hash
            file_content = file.read()
            file_hash = hashlib.md5(file_content).hexdigest()
            
            # Check for duplicate files in this conversation
            existing_file = db.query(ChatFile).filter(
                ChatFile.conversation_id == conversation_id,
                ChatFile.file_hash == file_hash
            ).first()
            
            if existing_file:
                return jsonify({
                    'error': 'This file has already been uploaded to this conversation',
                    'duplicate_file': {
                        'original_filename': existing_file.original_filename,
                        'upload_date': existing_file.upload_date.isoformat()
                    }
                }), 409  # Conflict status code
            
            # Reset file pointer for saving
            file.seek(0)
            
            # Save file using file_utils
            file_metadata = save_uploaded_file(file, conversation_id, current_user.id)
            
            # Create database record
            chat_file = ChatFile(
                conversation_id=conversation_id,
                original_filename=file_metadata['original_filename'],
                system_filename=file_metadata['system_filename'],
                file_path=file_metadata['file_path'],
                file_type=file_metadata['file_type'],
                mime_type=file_metadata['mime_type'],
                file_size=file_metadata['file_size'],
                uploaded_by=current_user.id,
                file_hash=file_hash
            )
            
            db.add(chat_file)
            
            # Update conversation timestamp
            conversation.updated_at = datetime.utcnow()
            
            db.commit()
            
            return jsonify({
                'success': True,
                'file': {
                    'id': chat_file.id,
                    'original_filename': chat_file.original_filename,
                    'file_type': chat_file.file_type,
                    'file_size': chat_file.file_size,
                    'file_size_formatted': format_file_size(chat_file.file_size),
                    'upload_date': chat_file.upload_date.isoformat(),
                    'mime_type': chat_file.mime_type,
                    'is_project_important': chat_file.is_project_important
                },
                'message': 'File uploaded successfully'
            })
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': f'Failed to save file: {str(e)}'}), 500
            
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/conversations/<int:conversation_id>/files', methods=['GET'])
@login_required
@access_required
def get_conversation_files(conversation_id):
    """Get all files attached to a conversation"""
    db = get_db()
    try:
        # Verify conversation exists and belongs to user
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        # Get all files for this conversation
        files = db.query(ChatFile).filter(
            ChatFile.conversation_id == conversation_id
        ).order_by(ChatFile.upload_date.desc()).all()
        
        files_data = []
        for file in files:
            files_data.append({
                'id': file.id,
                'original_filename': file.original_filename,
                'file_type': file.file_type,
                'file_size': file.file_size,
                'file_size_formatted': format_file_size(file.file_size),
                'upload_date': file.upload_date.isoformat(),
                'mime_type': file.mime_type,
                'uploader_id': file.uploaded_by,
                'is_project_important': file.is_project_important,
                'has_been_processed': file.has_been_processed,
                'transcoded_raw_file': file.transcoded_raw_file,
                'summary_raw_file': file.summary_raw_file,
                'human_notes': file.human_notes,
                'date_processed': file.date_processed.isoformat() if file.date_processed else None,
                'time_to_process': file.time_to_process
            })
        
        return jsonify({
            'files': files_data,
            'count': len(files_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/files/<int:file_id>/download', methods=['GET'])
@login_required
@access_required
def download_file(file_id):
    """Download a file by ID"""
    db = get_db()
    try:
        # Get file record
        chat_file = db.query(ChatFile).filter(ChatFile.id == file_id).first()
        
        if not chat_file:
            return jsonify({'error': 'File not found'}), 404
        
        # Verify user has access to this file (through conversation ownership)
        conversation = db.query(Conversation).filter(
            Conversation.id == chat_file.conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get full file path
        file_path = get_file_full_path(chat_file.file_path)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found on disk'}), 404
        
        # Send file
        return send_file(
            file_path,
            as_attachment=True,
            download_name=chat_file.original_filename,
            mimetype=chat_file.mime_type
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/files/<int:file_id>', methods=['DELETE'])
@login_required
@access_required
def delete_file(file_id):
    """Delete a file by ID"""
    db = get_db()
    try:
        # Get file record
        chat_file = db.query(ChatFile).filter(ChatFile.id == file_id).first()
        
        if not chat_file:
            return jsonify({'error': 'File not found'}), 404
        
        # Verify user has access to this file (through conversation ownership)
        conversation = db.query(Conversation).filter(
            Conversation.id == chat_file.conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            return jsonify({'error': 'Access denied'}), 403
        
        # Delete file from disk
        file_path = get_file_full_path(chat_file.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete database record
        db.delete(chat_file)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'File deleted successfully'
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/files/<int:file_id>/toggle-project-important', methods=['PUT'])
@login_required
@access_required
def toggle_file_project_importance(file_id):
    """Toggle whether a file is important to its project"""
    db = get_db()
    try:
        # Get the file and verify ownership
        file_obj = db.query(ChatFile).filter(ChatFile.id == file_id).first()
        if not file_obj:
            return jsonify({'error': 'File not found'}), 404
            
        # Check if user owns the conversation that contains this file
        if file_obj.conversation.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
            
        # Toggle the project importance flag
        file_obj.is_project_important = not file_obj.is_project_important
        db.commit()
        
        return jsonify({
            'success': True,
            'is_project_important': file_obj.is_project_important,
            'message': f'File {"marked as" if file_obj.is_project_important else "unmarked as"} project important'
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/projects/<int:project_id>/important-files', methods=['GET'])
@login_required
@access_required
def get_project_important_files(project_id):
    """Get all files marked as important for a specific project"""
    db = get_db()
    try:
        # Verify project ownership
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user.id
        ).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
            
        # Get all important files from conversations in this project
        important_files = db.query(ChatFile).join(Conversation).filter(
            Conversation.project_id == project_id,
            Conversation.user_id == current_user.id,
            ChatFile.is_project_important == True
        ).order_by(ChatFile.upload_date.desc()).all()
        
        files_data = []
        for file_obj in important_files:
            files_data.append({
                'id': file_obj.id,
                'original_filename': file_obj.original_filename,
                'file_type': file_obj.file_type,
                'mime_type': file_obj.mime_type,
                'file_size': file_obj.file_size,
                'file_size_formatted': format_file_size(file_obj.file_size),
                'upload_date': file_obj.upload_date.isoformat(),
                'conversation_id': file_obj.conversation_id,
                'conversation_title': file_obj.conversation.title,
                'is_project_important': file_obj.is_project_important
            })
            
        return jsonify({
            'success': True,
            'files': files_data,
            'project_name': project.name
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

# File Processing Management Endpoints

@app.route('/api/files/<int:file_id>/processing', methods=['PATCH'])
@login_required
@access_required
def update_file_processing_status(file_id):
    """Update file processing status and human notes"""
    db = get_db()
    try:
        # Get the file and verify ownership
        file_obj = db.query(ChatFile).filter(ChatFile.id == file_id).first()
        if not file_obj:
            return jsonify({'error': 'File not found'}), 404
            
        # Check if user owns the conversation that contains this file
        if file_obj.conversation.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update processing status if provided
        if 'has_been_processed' in data:
            status = data['has_been_processed']
            if status not in [0, 1, 2, 4]:
                return jsonify({'error': 'Invalid processing status. Must be 0, 1, 2, or 4'}), 400
            file_obj.has_been_processed = status
        
        # Update human notes if provided
        if 'human_notes' in data:
            file_obj.human_notes = data['human_notes']
        
        db.commit()
        
        return jsonify({
            'success': True,
            'has_been_processed': file_obj.has_been_processed,
            'human_notes': file_obj.human_notes,
            'message': 'File processing status updated'
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/files/<int:file_id>/reprocess', methods=['POST'])
@login_required
@access_required
def reprocess_file(file_id):
    """Reset file to unprocessed status for reprocessing"""
    db = get_db()
    try:
        # Get the file and verify ownership
        file_obj = db.query(ChatFile).filter(ChatFile.id == file_id).first()
        if not file_obj:
            return jsonify({'error': 'File not found'}), 404
            
        # Check if user owns the conversation that contains this file
        if file_obj.conversation.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Reset processing status
        file_obj.has_been_processed = 0
        file_obj.transcoded_raw_file = None
        file_obj.summary_raw_file = None
        file_obj.date_processed = None
        file_obj.time_to_process = None
        
        # Add note about reprocessing
        current_notes = file_obj.human_notes or ""
        reprocess_note = f"Reprocessed by user at {datetime.utcnow()}"
        file_obj.human_notes = f"{current_notes}\n{reprocess_note}" if current_notes else reprocess_note
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'File queued for reprocessing'
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/files', methods=['GET'])
@login_required
@access_required
def get_all_user_files():
    """Get files uploaded by the current user with pagination"""
    db = get_db()
    try:
        # Pagination params
        try:
            page = int(request.args.get('page', '1'))
        except ValueError:
            page = 1
        try:
            per_page = int(request.args.get('per_page', '50'))
        except ValueError:
            per_page = 50
        page = max(1, page)
        per_page = max(1, min(per_page, 200))

        base_q = db.query(ChatFile).join(Conversation).filter(
            Conversation.user_id == current_user.id
        )

        total_count = base_q.count()

        items = (
            base_q
            .order_by(ChatFile.upload_date.desc())
            .limit(per_page)
            .offset((page - 1) * per_page)
            .all()
        )

        files_data = []
        for file in items:
            conversation = file.conversation
            project = conversation.project if conversation.project_id else None

            files_data.append({
                'id': file.id,
                'original_filename': file.original_filename,
                'file_type': file.file_type,
                'file_size': file.file_size,
                'file_size_formatted': format_file_size(file.file_size),
                'upload_date': file.upload_date.isoformat(),
                'mime_type': file.mime_type,
                'has_been_processed': file.has_been_processed,
                'date_processed': file.date_processed.isoformat() if file.date_processed else None,
                'time_to_process': file.time_to_process,
                'ai_summary': file.ai_summary,
                'status_summary': file.status_summary,
                'human_notes': file.human_notes,
                'conversation': {
                    'id': conversation.id,
                    'title': conversation.title
                },
                'project': {
                    'id': project.id,
                    'name': project.name
                } if project else None
            })

        total_pages = (total_count + per_page - 1) // per_page if per_page else 1

        return jsonify({
            'files': files_data,
            'count': total_count,  # keep original name for compatibility
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/files/<int:file_id>/details', methods=['GET'])
@login_required
@access_required
def get_file_details(file_id):
    """Get detailed information about a specific file"""
    db = get_db()
    try:
        # Get the file and verify ownership
        file_obj = db.query(ChatFile).join(Conversation).filter(
            ChatFile.id == file_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not file_obj:
            return jsonify({'error': 'File not found'}), 404
        
        conversation = file_obj.conversation
        project = conversation.project if conversation.project_id else None
        
        file_data = {
            'id': file_obj.id,
            'original_filename': file_obj.original_filename,
            'system_filename': file_obj.system_filename,
            'file_path': file_obj.file_path,
            'file_type': file_obj.file_type,
            'mime_type': file_obj.mime_type,
            'file_size': file_obj.file_size,
            'file_size_formatted': format_file_size(file_obj.file_size),
            'upload_date': file_obj.upload_date.isoformat(),
            'has_been_processed': file_obj.has_been_processed,
            'transcoded_raw_file': file_obj.transcoded_raw_file,
            'summary_raw_file': file_obj.summary_raw_file,
            'ai_summary': getattr(file_obj, 'ai_summary', None),
            'status_summary': getattr(file_obj, 'status_summary', None),
            'human_notes': file_obj.human_notes,
            'date_processed': file_obj.date_processed.isoformat() if file_obj.date_processed else None,
            'time_to_process': file_obj.time_to_process,
            'is_project_important': file_obj.is_project_important,
            'conversation': {
                'id': conversation.id,
                'title': conversation.title,
                'created_at': conversation.created_at.isoformat(),
                'updated_at': conversation.updated_at.isoformat()
            },
            'project': {
                'id': project.id,
                'name': project.name,
                'description': project.description
            } if project else None
        }
        
        return jsonify(file_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/worker/status', methods=['GET'])
@login_required
@access_required
def get_worker_status():
    """Get background worker status and processing queue info"""
    db = get_db()
    try:
        # Check for files currently being processed
        processing_files = db.query(ChatFile).filter(
            ChatFile.has_been_processed == 1
        ).count()
        
        # Check for unprocessed files in queue
        unprocessed_files = db.query(ChatFile).filter(
            ChatFile.has_been_processed == 0
        ).count()
        
        # Check for processed files
        processed_files = db.query(ChatFile).filter(
            ChatFile.has_been_processed == 2
        ).count()
        
        # Simple check if worker process might be running
        # (This is a basic check - in production you'd want more sophisticated monitoring)
        import subprocess
        try:
            result = subprocess.run(['pgrep', '-f', 'process_unprocessed_files.py'], 
                                  capture_output=True, text=True)
            worker_running = len(result.stdout.strip()) > 0
        except:
            worker_running = False
        
        # Summary worker statistics
        summary_pending = db.query(ChatFile).filter(ChatFile.status_summary == 0).count()
        summary_processing = db.query(ChatFile).filter(ChatFile.status_summary == 1).count()
        summary_ready = db.query(ChatFile).filter(ChatFile.status_summary == 2).count()
        summary_failed = db.query(ChatFile).filter(ChatFile.status_summary == 3).count()
        try:
            sum_result = subprocess.run(['pgrep', '-f', 'summarize_transcoded_files.py'],
                                        capture_output=True, text=True)
            summary_worker_running = len(sum_result.stdout.strip()) > 0
        except:
            summary_worker_running = False
        
        return jsonify({
            'worker_running': worker_running,
            'queue_stats': {
                'unprocessed': unprocessed_files,
                'processing': processing_files,
                'processed': processed_files,
                'total': unprocessed_files + processing_files + processed_files
            },
            'summary_worker_running': summary_worker_running,
            'summary_stats': {
                'pending': summary_pending,
                'processing': summary_processing,
                'ready': summary_ready,
                'failed': summary_failed,
                'total': summary_pending + summary_processing + summary_ready + summary_failed
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

# User Page Route
@app.route('/user')
@login_required
@access_required
def user_page():
    """User dashboard page for managing archives and profile"""
    return render_template('user.html')

# Files Management Routes
@app.route('/files')
@login_required
@access_required
def files_page():
    """Files management page showing all user uploaded files"""
    return render_template('files.html')

@app.route('/files/<int:file_id>')
@login_required
@access_required
def file_details_page(file_id):
    """File details page showing specific file information"""
    return render_template('file_details.html', file_id=file_id)

# Admin and User Management Endpoints
@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    """Admin panel"""
    return render_template('admin.html')

@app.route('/api/admin/users', methods=['GET'])
@login_required
@admin_required
def get_users():
    """Get all users for admin management"""
    db = get_db()
    try:
        users = db.query(User).all()
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'name': user.name,
                'allowedaccess': user.allowedaccess,
                'is_admin': user.is_admin,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        return jsonify({'users': users_data})
    finally:
        db.close()

@app.route('/api/admin/users/<int:user_id>/access', methods=['POST'])
@login_required
@admin_required
def toggle_user_access(user_id):
    """Toggle user access (allow/deny)"""
    db = get_db()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Toggle access
        user.allowedaccess = 'no' if user.allowedaccess == 'yes' else 'yes'
        db.commit()
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'allowedaccess': user.allowedaccess
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/admin/users/<int:user_id>/admin', methods=['POST'])
@login_required
@admin_required
def toggle_user_admin(user_id):
    """Toggle user admin status"""
    db = get_db()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Don't allow removing admin from yourself
        if user.id == current_user.id and user.is_admin:
            return jsonify({'error': 'Cannot remove admin status from yourself'}), 400
        
        # Toggle admin status
        user.is_admin = not user.is_admin
        db.commit()
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'is_admin': user.is_admin
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/admin/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
@admin_required
def reset_user_password(user_id):
    """Reset user password"""
    data = request.get_json()
    new_password = data.get('password')
    
    if not new_password or len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400
    
    db = get_db()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update password
        user.password_hash = generate_password_hash(new_password)
        db.commit()
        
        return jsonify({
            'success': True,
            'message': f'Password reset for user {user.username}'
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/user/info', methods=['GET'])
@login_required
def get_current_user_info():
    """Get current user information including admin status"""
    db = get_db()
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'name': user.name,
            'allowedaccess': user.allowedaccess,
            'is_admin': user.is_admin
        })
    finally:
        db.close()

# API Key Management Endpoints
@app.route('/api/keys', methods=['GET'])
@login_required
@access_required
def get_api_keys():
    """Get user's API keys"""
    db = get_db()
    try:
        keys = db.query(ApiKey).filter(
            ApiKey.user_id == current_user.id,
            ApiKey.is_active == True
        ).all()
        
        result = []
        for key in keys:
            result.append({
                'id': key.id,
                'name': key.key_name,
                'prefix': key.key_prefix,
                'created_at': key.created_at.isoformat(),
                'last_used': key.last_used.isoformat() if key.last_used else None
            })
        
        return jsonify(result)
    finally:
        db.close()

@app.route('/api/keys', methods=['POST'])
@login_required
@access_required
def create_api_key():
    """Create a new API key"""
    data = request.get_json()
    key_name = data.get('name', 'Unnamed Key')
    
    # Generate new API key
    api_key = ApiKey.generate_key()
    key_hash = ApiKey.hash_key(api_key)
    key_prefix = api_key[:10] + "..."
    
    db = get_db()
    try:
        new_key = ApiKey(
            user_id=current_user.id,
            key_name=key_name,
            key_hash=key_hash,
            key_prefix=key_prefix
        )
        
        db.add(new_key)
        db.commit()
        db.refresh(new_key)
        
        return jsonify({
            'id': new_key.id,
            'name': new_key.key_name,
            'key': api_key,  # Only returned once!
            'prefix': new_key.key_prefix,
            'created_at': new_key.created_at.isoformat()
        })
    finally:
        db.close()

@app.route('/api/keys/<int:key_id>', methods=['DELETE'])
@login_required
@access_required
def delete_api_key(key_id):
    """Delete an API key"""
    db = get_db()
    try:
        key = db.query(ApiKey).filter(
            ApiKey.id == key_id,
            ApiKey.user_id == current_user.id
        ).first()
        
        if not key:
            return jsonify({'error': 'API key not found'}), 404
        
        key.is_active = False
        db.commit()
        
        return jsonify({'success': True})
    finally:
        db.close()

# API Endpoints (for programmatic access)
@app.route('/api/v1/fetch-url', methods=['POST'])
@api_key_required
def api_fetch_url():
    """API endpoint to fetch URL content (requires API key)"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        use_js = data.get('use_js', True)
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # Validate URL format
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return jsonify({'error': 'Invalid URL format'}), 400
        
        # Add scheme if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        content = None
        method_used = "unknown"
        
        # Try JavaScript scraping first (for dynamic content)
        if use_js:
            try:
                print(f"API: Attempting JavaScript scraping for: {url}")
                content = asyncio.run(scrape_with_javascript(url))
                method_used = "javascript"
                print(f"API: JavaScript scraping successful, content length: {len(content)}")
            except Exception as js_error:
                print(f"API: JavaScript scraping failed: {str(js_error)}")
                content = None
        
        # Fallback to basic HTTP scraping if JS failed or not requested
        if not content or "Error scraping with JavaScript" in content:
            try:
                print(f"API: Attempting basic HTTP scraping for: {url}")
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
                
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                
                content = extract_text_from_html(response.text, url)
                method_used = "http"
                print(f"API: HTTP scraping successful, content length: {len(content)}")
                
            except Exception as http_error:
                return jsonify({'error': f'Both JavaScript and HTTP scraping failed. JS: {js_error if "js_error" in locals() else "Not attempted"}, HTTP: {str(http_error)}'}), 500
        
        # With GPT-OSS-20B and your powerful hardware, we can handle large content
        # Only truncate if content is extremely large (>100k chars) to prevent memory issues
        max_length = 100000  # Much more generous limit for your hardware
        original_length = len(content)
        if len(content) > max_length:
            content = content[:max_length] + f"\n\n[Content truncated from {original_length} to {max_length} characters - consider processing in smaller chunks]"
        
        return jsonify({
            'content': content,
            'url': url,
            'method_used': method_used,
            'content_length': len(content),
            'original_length': original_length
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/v1/chat', methods=['POST'])
@api_key_required
def api_v1_chat():
    """API endpoint for AI chat (requires API key)"""
    try:
        data = request.get_json()
        dataset = data.get('dataset', '')
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Build the prompt (no history for API calls to keep it simple)
        if dataset.strip():
            if "Source URL:" in dataset:
                prompt = f"You have been provided with content from a web page. Here is the data:\n\n{dataset}\n\nBased on this provided data, please answer the following question:\n{question}"
            else:
                prompt = f"You have been provided with the following dataset:\n\n{dataset}\n\nBased on this provided data, please answer the following question:\n{question}"
        else:
            prompt = f"Question: {question}"
        
        # Debug logging
        print(f"\n=== API CHAT DEBUG ===")
        print(f"User: {request.api_user.username}")
        print(f"Dataset length: {len(dataset)} characters")
        print(f"Question: {question}")
        print(f"Prompt preview (first 500 chars): {prompt[:500]}...")
        print(f"=== END DEBUG ===")
        
        # Send request to Ollama
        ollama_payload = {
            "model": DEFAULT_MODEL,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(OLLAMA_URL, json=ollama_payload, timeout=AI_TIMEOUT_SECONDS)
        response.raise_for_status()
        
        ai_response = response.json()
        ai_text = ai_response.get('response', 'No response received')
        
        return jsonify({
            'response': ai_text,
            'model': ai_response.get('model', DEFAULT_MODEL),
            'prompt_length': len(prompt)
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'AI service error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

# API Key User Management Endpoints
@app.route('/api/v1/conversations', methods=['GET'])
@api_key_required
def api_get_conversations():
    """Get conversations for API key user"""
    db = get_db()
    try:
        conversations = db.query(Conversation).filter(
            Conversation.user_id == request.api_user.id
        ).order_by(Conversation.updated_at.desc()).all()
        
        conversations_data = []
        for conv in conversations:
            message_count = db.query(Message).filter(Message.conversation_id == conv.id).count()
            file_count = db.query(ChatFile).filter(ChatFile.conversation_id == conv.id).count()
            conversations_data.append({
                'id': conv.id,
                'title': conv.title,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat(),
                'message_count': message_count,
                'file_count': file_count,
                'is_starred': conv.is_starred,
                'project_id': conv.project_id,
                'is_archived': conv.is_archived,
                'is_hidden': conv.is_hidden
            })
        
        return jsonify({'conversations': conversations_data})
    finally:
        db.close()

@app.route('/api/v1/conversations', methods=['POST'])
@api_key_required
def api_create_conversation():
    """Create new conversation for API key user"""
    data = request.get_json()
    title = data.get('title', 'API Conversation')
    
    db = get_db()
    try:
        # Cleanup: remove other empty "New Chat" conversations for this user (if they used the default UI title)
        old_new_chats = db.query(Conversation).filter(
            Conversation.user_id == request.api_user.id,
            Conversation.title == 'New Chat'
        ).all()
        for old_conv in old_new_chats:
            msg_count = db.query(Message).filter(Message.conversation_id == old_conv.id).count()
            if msg_count == 0:
                files = db.query(ChatFile).filter(ChatFile.conversation_id == old_conv.id).all()
                for chat_file in files:
                    file_path = get_file_full_path(chat_file.file_path)
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except OSError as e:
                            print(f"Warning: Could not delete file {file_path}: {e}")
                    db.delete(chat_file)
                db.query(Message).filter(Message.conversation_id == old_conv.id).delete()
                db.delete(old_conv)
        
        new_conversation = Conversation(
            title=title,
            user_id=request.api_user.id
        )
        
        db.add(new_conversation)
        db.commit()
        db.refresh(new_conversation)
        
        return jsonify({
            'id': new_conversation.id,
            'title': new_conversation.title,
            'created_at': new_conversation.created_at.isoformat(),
            'user_id': new_conversation.user_id
        }), 201
    finally:
        db.close()

@app.route('/api/v1/conversations/<int:conversation_id>/upload', methods=['POST'])
@api_key_required
def api_upload_file(conversation_id):
    """Upload file to conversation for API key user"""
    # Check if conversation belongs to API key user
    db = get_db()
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == request.api_user.id
        ).first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found or access denied'}), 404
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        try:
            # Save the file using existing file utilities
            file_metadata = save_uploaded_file(file, conversation_id, request.api_user.id)
            
            # Create database record
            chat_file = ChatFile(
                conversation_id=conversation_id,
                original_filename=file_metadata['original_filename'],
                system_filename=file_metadata['system_filename'],
                file_path=file_metadata['file_path'],
                file_type=file_metadata['file_type'],
                mime_type=file_metadata['mime_type'],
                file_size=file_metadata['file_size'],
                uploaded_by=request.api_user.id
            )
            
            db.add(chat_file)
            db.commit()
            db.refresh(chat_file)
            
            return jsonify({
                'id': chat_file.id,
                'filename': chat_file.original_filename,
                'file_type': chat_file.file_type,
                'file_size': chat_file.file_size,
                'upload_date': chat_file.upload_date.isoformat()
            }), 201
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': f'Upload failed: {str(e)}'}), 500
            
    finally:
        db.close()

@app.route('/api/v1/projects', methods=['GET'])
@api_key_required
def api_get_projects():
    """Get projects for API key user"""
    db = get_db()
    try:
        projects = db.query(Project).filter(
            Project.user_id == request.api_user.id
        ).order_by(Project.updated_at.desc()).all()
        
        projects_data = []
        for project in projects:
            conversation_count = db.query(Conversation).filter(Conversation.project_id == project.id).count()
            projects_data.append({
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'created_at': project.created_at.isoformat(),
                'updated_at': project.updated_at.isoformat(),
                'conversation_count': conversation_count,
                'is_archived': project.is_archived,
                'is_hidden': project.is_hidden
            })
        
        return jsonify({'projects': projects_data})
    finally:
        db.close()

@app.route('/api/v1/projects', methods=['POST'])
@api_key_required
def api_create_project():
    """Create new project for API key user"""
    data = request.get_json()
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    
    if not name:
        return jsonify({'error': 'Project name is required'}), 400
    
    db = get_db()
    try:
        new_project = Project(
            name=name,
            description=description,
            user_id=request.api_user.id
        )
        
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        
        return jsonify({
            'id': new_project.id,
            'name': new_project.name,
            'description': new_project.description,
            'created_at': new_project.created_at.isoformat(),
            'user_id': new_project.user_id
        }), 201
    finally:
        db.close()

@app.route('/api/v1/conversations/<int:conversation_id>/files', methods=['GET'])
@api_key_required
def api_get_conversation_files(conversation_id):
    """Get files for a specific conversation (API key auth)"""
    db = get_db()
    try:
        # Check if conversation belongs to API key user
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == request.api_user.id
        ).first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found or access denied'}), 404
        
        # Get files for this conversation
        files = db.query(ChatFile).filter(
            ChatFile.conversation_id == conversation_id
        ).order_by(ChatFile.upload_date.desc()).all()
        
        files_data = []
        for file_obj in files:
            files_data.append({
                'id': file_obj.id,
                'original_filename': file_obj.original_filename,
                'system_filename': file_obj.system_filename,
                'file_type': file_obj.file_type,
                'mime_type': file_obj.mime_type,
                'file_size': file_obj.file_size,
                'upload_date': file_obj.upload_date.isoformat(),
                'has_been_processed': file_obj.has_been_processed,
                'date_processed': file_obj.date_processed.isoformat() if file_obj.date_processed else None,
                'time_to_process': file_obj.time_to_process,
                'is_project_important': file_obj.is_project_important
            })
        
        return jsonify({'files': files_data})
    finally:
        db.close()

@app.route('/api/v1/files/<int:file_id>/details', methods=['GET'])
@api_key_required
def api_get_file_details(file_id):
    """Get detailed information about a specific file (API key auth)"""
    db = get_db()
    try:
        # Get the file and verify ownership through conversation
        file_obj = db.query(ChatFile).join(Conversation).filter(
            ChatFile.id == file_id,
            Conversation.user_id == request.api_user.id
        ).first()
        
        if not file_obj:
            return jsonify({'error': 'File not found or access denied'}), 404
        
        conversation = file_obj.conversation
        
        file_data = {
            'id': file_obj.id,
            'original_filename': file_obj.original_filename,
            'system_filename': file_obj.system_filename,
            'file_path': file_obj.file_path,
            'file_type': file_obj.file_type,
            'mime_type': file_obj.mime_type,
            'file_size': file_obj.file_size,
            'upload_date': file_obj.upload_date.isoformat(),
            'has_been_processed': file_obj.has_been_processed,
            'transcoded_raw_file': file_obj.transcoded_raw_file,
            'summary_raw_file': file_obj.summary_raw_file,
            'human_notes': file_obj.human_notes,
            'date_processed': file_obj.date_processed.isoformat() if file_obj.date_processed else None,
            'time_to_process': file_obj.time_to_process,
            'is_project_important': file_obj.is_project_important,
            'conversation': {
                'id': conversation.id,
                'title': conversation.title,
                'created_at': conversation.created_at.isoformat(),
                'updated_at': conversation.updated_at.isoformat()
            }
        }
        
        return jsonify(file_data)
    finally:
        db.close()

# Archive Management API Endpoints - Three Level System
# Level 1: Active (is_archived=False, is_hidden=False) - Front page
# Level 2: Hidden (is_archived=False, is_hidden=True) - User page only
# Level 3: Archived (is_archived=True) - Simple listing

@app.route('/api/conversations/active', methods=['GET'])
@login_required
@access_required
def get_active_conversations():
    """Get active conversations for current user (Level 1)"""
    db = get_db()
    try:
        conversations = db.query(Conversation).filter(
            Conversation.user_id == current_user.id,
            Conversation.is_archived == False,
            Conversation.is_hidden == False,
            Conversation.project_id == None  # Only show chats not part of projects
        ).order_by(Conversation.is_starred.desc(), Conversation.updated_at.desc()).all()
        
        conversations_data = []
        for conv in conversations:
            message_count = db.query(Message).filter(Message.conversation_id == conv.id).count()
            file_count = db.query(ChatFile).filter(ChatFile.conversation_id == conv.id).count()
            conversations_data.append({
                'id': conv.id,
                'title': conv.title,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat(),
                'message_count': message_count,
                'file_count': file_count,
                'is_starred': conv.is_starred,
                'project_id': conv.project_id
            })
        
        return jsonify({'conversations': conversations_data})
    finally:
        db.close()

@app.route('/api/projects/active', methods=['GET'])
@login_required
@access_required
def get_active_projects():
    """Get active projects for current user (Level 1)"""
    db = get_db()
    try:
        projects = db.query(Project).filter(
            Project.user_id == current_user.id,
            Project.is_archived == False,
            Project.is_hidden == False
        ).order_by(Project.updated_at.desc()).all()
        
        projects_data = []
        for project in projects:
            conversation_count = db.query(Conversation).filter(Conversation.project_id == project.id).count()
            projects_data.append({
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'created_at': project.created_at.isoformat(),
                'updated_at': project.updated_at.isoformat(),
                'conversation_count': conversation_count
            })
        
        return jsonify({'projects': projects_data})
    finally:
        db.close()

@app.route('/api/conversations/hidden', methods=['GET'])
@login_required
@access_required
def get_hidden_conversations():
    """Get hidden conversations for current user (Level 2)"""
    db = get_db()
    try:
        conversations = db.query(Conversation).filter(
            Conversation.user_id == current_user.id,
            Conversation.is_archived == False,
            Conversation.is_hidden == True
        ).order_by(Conversation.updated_at.desc()).all()
        
        conversations_data = []
        for conv in conversations:
            message_count = db.query(Message).filter(Message.conversation_id == conv.id).count()
            conversations_data.append({
                'id': conv.id,
                'title': conv.title,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat(),
                'message_count': message_count,
                'is_starred': conv.is_starred
            })
        
        return jsonify({'conversations': conversations_data})
    finally:
        db.close()

@app.route('/api/conversations/archived', methods=['GET'])
@login_required
@access_required
def get_archived_conversations():
    """Get archived conversations for current user (Level 3)"""
    db = get_db()
    try:
        conversations = db.query(Conversation).filter(
            Conversation.user_id == current_user.id,
            Conversation.is_archived == True
        ).order_by(Conversation.updated_at.desc()).all()
        
        conversations_data = []
        for conv in conversations:
            message_count = db.query(Message).filter(Message.conversation_id == conv.id).count()
            conversations_data.append({
                'id': conv.id,
                'title': conv.title,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat(),
                'message_count': message_count,
                'is_starred': conv.is_starred
            })
        
        return jsonify({'conversations': conversations_data})
    finally:
        db.close()

@app.route('/api/projects/hidden', methods=['GET'])
@login_required
@access_required
def get_hidden_projects():
    """Get hidden projects for current user (Level 2)"""
    db = get_db()
    try:
        projects = db.query(Project).filter(
            Project.user_id == current_user.id,
            Project.is_archived == False,
            Project.is_hidden == True
        ).order_by(Project.updated_at.desc()).all()
        
        projects_data = []
        for project in projects:
            conversation_count = db.query(Conversation).filter(Conversation.project_id == project.id).count()
            projects_data.append({
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'created_at': project.created_at.isoformat(),
                'updated_at': project.updated_at.isoformat(),
                'conversation_count': conversation_count
            })
        
        return jsonify({'projects': projects_data})
    finally:
        db.close()

@app.route('/api/projects/archived', methods=['GET'])
@login_required
@access_required
def get_archived_projects():
    """Get archived projects for current user (Level 3)"""
    db = get_db()
    try:
        projects = db.query(Project).filter(
            Project.user_id == current_user.id,
            Project.is_archived == True
        ).order_by(Project.updated_at.desc()).all()
        
        projects_data = []
        for project in projects:
            conversation_count = db.query(Conversation).filter(Conversation.project_id == project.id).count()
            projects_data.append({
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'created_at': project.created_at.isoformat(),
                'updated_at': project.updated_at.isoformat(),
                'conversation_count': conversation_count
            })
        
        return jsonify({'projects': projects_data})
    finally:
        db.close()

# State Transition Endpoints for Three-Level System

@app.route('/api/conversations/<int:conversation_id>/hide', methods=['POST'])
@login_required
@access_required
def hide_conversation(conversation_id):
    """Hide conversation from front page (Active -> Hidden)"""
    db = get_db()
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
            Conversation.is_archived == False,
            Conversation.is_hidden == False
        ).first()
        
        if not conversation:
            return jsonify({'error': 'Active conversation not found'}), 404
        
        conversation.is_hidden = True
        conversation.updated_at = datetime.utcnow()
        db.commit()
        
        return jsonify({'success': True, 'message': 'Conversation hidden from front page'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/conversations/<int:conversation_id>/show', methods=['POST'])
@login_required
@access_required
def show_conversation(conversation_id):
    """Show conversation on front page (Hidden -> Active)"""
    db = get_db()
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
            Conversation.is_archived == False,
            Conversation.is_hidden == True
        ).first()
        
        if not conversation:
            return jsonify({'error': 'Hidden conversation not found'}), 404
        
        conversation.is_hidden = False
        conversation.updated_at = datetime.utcnow()
        db.commit()
        
        return jsonify({'success': True, 'message': 'Conversation restored to front page'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/conversations/<int:conversation_id>/archive', methods=['POST'])
@login_required
@access_required
def archive_conversation(conversation_id):
    """Archive conversation (Active/Hidden -> Archived)"""
    db = get_db()
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
            Conversation.is_archived == False
        ).first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found or already archived'}), 404
        
        conversation.is_archived = True
        conversation.updated_at = datetime.utcnow()
        db.commit()
        
        return jsonify({'success': True, 'message': 'Conversation archived'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/conversations/<int:conversation_id>/restore', methods=['POST'])
@login_required
@access_required
def restore_conversation(conversation_id):
    """Restore archived conversation to active state (Archived -> Active)"""
    db = get_db()
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
            Conversation.is_archived == True
        ).first()
        
        if not conversation:
            return jsonify({'error': 'Archived conversation not found'}), 404
        
        conversation.is_archived = False
        conversation.is_hidden = False  # Restore to active (front page)
        conversation.updated_at = datetime.utcnow()
        db.commit()
        
        return jsonify({'success': True, 'message': 'Conversation restored to active state'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/projects/<int:project_id>/hide', methods=['POST'])
@login_required
@access_required
def hide_project(project_id):
    """Hide project from front page (Active -> Hidden)"""
    db = get_db()
    try:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user.id,
            Project.is_archived == False,
            Project.is_hidden == False
        ).first()
        
        if not project:
            return jsonify({'error': 'Active project not found'}), 404
        
        project.is_hidden = True
        project.updated_at = datetime.utcnow()
        db.commit()
        
        return jsonify({'success': True, 'message': 'Project hidden from front page'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/projects/<int:project_id>/show', methods=['POST'])
@login_required
@access_required
def show_project(project_id):
    """Show project on front page (Hidden -> Active)"""
    db = get_db()
    try:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user.id,
            Project.is_archived == False,
            Project.is_hidden == True
        ).first()
        
        if not project:
            return jsonify({'error': 'Hidden project not found'}), 404
        
        project.is_hidden = False
        project.updated_at = datetime.utcnow()
        db.commit()
        
        return jsonify({'success': True, 'message': 'Project restored to front page'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/projects/<int:project_id>/archive', methods=['POST'])
@login_required
@access_required
def archive_project(project_id):
    """Archive project (Active/Hidden -> Archived)"""
    db = get_db()
    try:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user.id,
            Project.is_archived == False
        ).first()
        
        if not project:
            return jsonify({'error': 'Project not found or already archived'}), 404
        
        project.is_archived = True
        project.updated_at = datetime.utcnow()
        db.commit()
        
        return jsonify({'success': True, 'message': 'Project archived'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/projects/<int:project_id>/restore', methods=['POST'])
@login_required
@access_required
def restore_project(project_id):
    """Restore archived project to active state (Archived -> Active)"""
    db = get_db()
    try:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user.id,
            Project.is_archived == True
        ).first()
        
        if not project:
            return jsonify({'error': 'Archived project not found'}), 404
        
        project.is_archived = False
        project.is_hidden = False  # Restore to active (front page)
        project.updated_at = datetime.utcnow()
        db.commit()
        
        return jsonify({'success': True, 'message': 'Project restored to active state'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
@login_required
@access_required
def delete_project(project_id):
    """Delete a project and all associated conversations and files"""
    db = get_db()
    try:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == current_user.id
        ).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Get all conversations linked to this project
        conversations = db.query(Conversation).filter(Conversation.project_id == project_id).all()
        
        total_files_deleted = 0
        conversations_deleted = len(conversations)
        
        # Delete each conversation and its associated files
        for conversation in conversations:
            # Delete associated files from disk and database
            files = db.query(ChatFile).filter(ChatFile.conversation_id == conversation.id).all()
            for chat_file in files:
                # Delete file from disk
                file_path = get_file_full_path(chat_file.file_path)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except OSError as e:
                        print(f"Warning: Could not delete file {file_path}: {e}")
                
                # Delete file record from database
                db.delete(chat_file)
                total_files_deleted += 1
            
            # Delete messages for this conversation
            db.query(Message).filter(Message.conversation_id == conversation.id).delete()
            
            # Delete conversation
            db.delete(conversation)
        
        # Delete the project itself
        db.delete(project)
        db.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Project deleted along with {conversations_deleted} conversations and {total_files_deleted} files'
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/user/change-password', methods=['POST'])
@login_required
@access_required
def change_user_password():
    """Change current user's password"""
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Current password and new password are required'}), 400
    
    if len(new_password) < 6:
        return jsonify({'error': 'New password must be at least 6 characters long'}), 400
    
    db = get_db()
    try:
        # Verify current password
        if not check_password_hash(current_user.password_hash, current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Update password
        current_user.password_hash = generate_password_hash(new_password)
        db.commit()
        
        return jsonify({'success': True, 'message': 'Password changed successfully'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

if __name__ == '__main__':
    print(f"Starting AI Chat Interface...")
    print(f"Using model: {DEFAULT_MODEL}")
    print(f"Ollama URL: {OLLAMA_URL}")
    app.run(host='0.0.0.0', port=5785, debug=True, threaded=True, use_reloader=False)
