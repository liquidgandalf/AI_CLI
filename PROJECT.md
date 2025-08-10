# AI Chat Interface with Web Scraping & API System

## 🎯 Project Overview

A locally hosted AI-powered chat interface with advanced web scraping capabilities, user authentication, conversation management, and programmatic API access. Built for analyzing web content with AI assistance and supporting automated workflows.

## 🏗️ Architecture

```
AI_CLI/
├── app.py                 # Main Flask application
├── database.py           # SQLAlchemy models and database setup
├── templates/
│   ├── chat.html         # Main chat interface
│   ├── login.html        # User login page
│   └── register.html     # User registration page
├── requirements.txt      # Python dependencies
├── ai_chat.db           # SQLite database (auto-created)
└── PROJECT.md           # This documentation
```

## 🚀 Features Implemented

### ✅ Core Functionality
- **Local AI Integration**: Connects to Ollama (gemma3:12b model)
- **Advanced Web Scraping**: 
  - Basic HTTP scraping with BeautifulSoup
  - JavaScript-capable scraping with Playwright for dynamic content
  - Automatic fallback between methods
- **Intelligent Prompting**: AI receives clear context about scraped data
- **Markdown Rendering**: AI responses formatted with headers, tables, lists, etc.

### ✅ User Management
- **Classic Authentication**: Username/password login and registration
- **Secure Password Hashing**: Using Werkzeug
- **Session Management**: Flask-Login integration
- **User Isolation**: Each user's data is completely separate

### ✅ Conversation System
- **Persistent History**: All conversations saved to database
- **Sidebar Navigation**: Easy access to previous conversations
- **Context Preservation**: Full conversation history maintained
- **Smart Prompt Building**: Token-aware history management

### ✅ API System
- **API Key Authentication**: Secure programmatic access
- **Web UI Management**: Create/delete API keys through interface
- **Usage Tracking**: Monitor when keys were last used
- **RESTful Endpoints**: Clean API design for external programs

## 🔧 Technical Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **AI**: Ollama local service
- **Scraping**: Requests + BeautifulSoup + Playwright
- **Frontend**: Vanilla JavaScript with modern CSS
- **Authentication**: Flask-Login + Werkzeug password hashing

## 📊 Database Schema

```sql
Users: id, username, email, password_hash, name, created_at
Conversations: id, user_id, title, dataset, created_at, updated_at
Messages: id, conversation_id, message_type, question, response, timestamp
ApiKeys: id, user_id, key_name, key_hash, key_prefix, is_active, created_at, last_used
```

## 🌐 API Endpoints

### Web Interface (requires login)
- `GET /` - Redirect to chat or login
- `GET /chat` - Main chat interface
- `POST /login` - User authentication
- `POST /register` - User registration
- `POST /api/chat` - Send message to AI
- `POST /api/fetch-url` - Scrape URL content
- `GET /api/conversations` - List user's conversations
- `GET /api/keys` - List user's API keys
- `POST /api/keys` - Create new API key

### Programmatic API (requires API key)
- `POST /api/v1/fetch-url` - Scrape URL with JavaScript support
- `POST /api/v1/chat` - Send question to AI with dataset context

## 🔑 API Usage Examples

### Creating an API Key
1. Login to web interface
2. Click "Manage Keys" in sidebar
3. Enter descriptive name
4. Copy the generated key (shown only once!)

### Using the API
```python
import requests

API_KEY = "sk-your-generated-key"
BASE_URL = "http://localhost:5785"
headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# Scrape a URL
response = requests.post(f"{BASE_URL}/api/v1/fetch-url", 
    headers=headers,
    json={"url": "https://example.com", "use_js": True}
)
content = response.json()["content"]

# Ask AI about the content
response = requests.post(f"{BASE_URL}/api/v1/chat",
    headers=headers,
    json={
        "dataset": content,
        "question": "Summarize the main points"
    }
)
answer = response.json()["response"]
```

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8+
- Ollama installed and running
- Available model (gemma3:12b recommended)

### Installation
```bash
# Clone/navigate to project directory
cd AI_CLI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Initialize database
python database.py

# Start application
python app.py
```

### Access
- Web Interface: http://localhost:5785
- Create account or login
- Start chatting with AI!

## 🎯 Use Cases

### Interactive Web Analysis
1. Enter URL in the interface
2. Click "Fetch" to scrape content
3. Ask questions about the scraped data
4. Get AI-powered analysis with markdown formatting

### Automated Part Number Processing
```python
# Your automation script can:
part_numbers = ["ABC123", "XYZ789", "DEF456"]

for part in part_numbers:
    url = f"https://supplier.com/part/{part}"
    
    # Scrape the part page
    content = scrape_url(url)
    
    # Ask AI to extract key info
    analysis = ask_ai(content, "What is the price, availability, and specifications?")
    
    # Process the response
    process_part_data(part, analysis)
```

## 🔧 Configuration

### Environment Variables
- `SECRET_KEY`: Flask session security (default provided)
- `OLLAMA_URL`: Ollama service URL (default: http://localhost:11434)
- `DEFAULT_MODEL`: AI model to use (default: gemma3:12b)

### Customization
- **Models**: Change `DEFAULT_MODEL` in app.py
- **Scraping**: Adjust timeouts and limits in scraping functions
- **UI**: Modify templates/chat.html for interface changes
- **Database**: Switch from SQLite by changing `DATABASE_URL`

## 🐛 Troubleshooting

### Common Issues
1. **AI not responding**: Check Ollama is running (`ollama serve`)
2. **JavaScript scraping fails**: Ensure Playwright browsers installed
3. **Database errors**: Run `python database.py` to reinitialize
4. **API key issues**: Check header format: `X-API-Key: your-key`

### Debug Information
- Server logs show scraping method used and content length
- AI prompt debugging enabled in console
- API usage tracked in database

## 🚀 Next Steps / Future Enhancements

### Planned Features
- Database interrogation workflows
- Advanced data processing pipelines
- Export/import conversation data
- Enhanced API rate limiting
- Multi-model support

### Scaling Considerations
- Move to PostgreSQL for production
- Add Redis for session storage
- Implement proper WSGI server (Gunicorn)
- Add HTTPS support
- Container deployment (Docker)

## 📝 Development Notes

### Key Design Decisions
- **Playwright over Selenium**: Better performance and reliability
- **SQLite for development**: Simple setup, easy to backup
- **Token-aware prompting**: Ensures important context survives
- **Secure API keys**: Hashed storage, one-time display
- **Fallback scraping**: Graceful degradation when JS fails

### Code Organization
- `app.py`: All routes and business logic
- `database.py`: Clean ORM models
- `templates/`: Minimal, functional UI
- Clear separation between web and API endpoints

## 🎉 Success Metrics

✅ **Fully functional AI chat with web scraping**  
✅ **JavaScript-capable dynamic content handling**  
✅ **Secure user authentication and data isolation**  
✅ **Persistent conversation history**  
✅ **Beautiful markdown-formatted responses**  
✅ **Complete API system for automation**  
✅ **Ready for part number processing workflows**

---

**Project Status**: Production-ready for local use  
**Last Updated**: August 2025  
**Next Session**: Ready for database interrogation features and advanced workflows
