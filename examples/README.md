# API Examples

This directory contains examples for using the AI CLI API in different programming languages.

## Available Examples

- **[PHP Examples](php/)** - PHP implementations for API interactions
- **[Python Examples](python/)** - Python implementations for API interactions

## API Key Setup

Before using any examples, you'll need to:

1. Generate an API key from your AI CLI admin interface
2. Replace `YOUR_API_KEY_HERE` in the examples with your actual API key
3. Update the base URL if your server is running on a different host/port

## Base API URL

Default: `http://localhost:5785`

For production: `https://horizon.thevault.me.uk`

## Available Operations

All examples demonstrate:

- ✅ **Chat Operations** - Send questions and get AI responses
- ✅ **Conversation Management** - Create, list, and manage chat conversations
- ✅ **File Upload** - Upload files to conversations for processing
- ✅ **File Retrieval** - Get processed file transcripts and raw content
- ✅ **Project Management** - Create and manage projects
- ✅ **URL Fetching** - Fetch and process web content

## Supported File Types

- **Audio**: `.mp3`, `.wav`, `.ogg`, `.m4a`, `.aac`, `.flac`, `.mpga`
- **Images**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.svg`, `.bmp`
- **Text**: `.txt`, `.md`, `.html`, `.css`, `.js`, `.json`, `.xml`, `.py`, `.sql`
- **Documents**: `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx`
- **Archives**: `.zip`, `.tar`, `.gz`, `.rar`

Maximum file size: 100MB
