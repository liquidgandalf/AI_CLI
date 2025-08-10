# Python API Examples

This folder contains Python examples for interacting with the AI CLI API.

## Setup

1. Make sure you have Python 3.6+ installed
2. Install required packages:
   ```bash
   pip install requests
   ```
3. Get your API key from the AI CLI admin interface
4. Update the `API_KEY` and `BASE_URL` variables in each example

## Examples

- **[basic_chat.py](basic_chat.py)** - Send a simple chat message and get AI response
- **[conversation_management.py](conversation_management.py)** - Create and manage conversations
- **[file_upload.py](file_upload.py)** - Upload files to conversations
- **[file_retrieval.py](file_retrieval.py)** - Retrieve processed file transcripts
- **[project_management.py](project_management.py)** - Create and manage projects
- **[url_fetching.py](url_fetching.py)** - Fetch and process web content
- **[complete_workflow.py](complete_workflow.py)** - Full workflow example

## Running Examples

```bash
python basic_chat.py
python conversation_management.py
# etc...
```

## Dependencies

All examples use the `requests` library for HTTP requests:

```python
import requests
import json
```

## Error Handling

All examples include proper error handling and will display:
- HTTP status codes
- Error messages from the API
- Connection issues
- JSON parsing errors

## Authentication

All requests use the `X-API-Key` header for authentication:

```python
headers = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
}
```

## Configuration

Update these variables in each script:

```python
API_KEY = 'YOUR_API_KEY_HERE'  # Replace with your actual API key
BASE_URL = 'http://localhost:5785'  # Update for your server
```
