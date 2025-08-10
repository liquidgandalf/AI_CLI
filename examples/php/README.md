# PHP API Examples

This folder contains PHP examples for interacting with the AI CLI API.

## Setup

1. Make sure you have PHP with cURL support installed
2. Get your API key from the AI CLI admin interface
3. Update the `$apiKey` and `$baseUrl` variables in each example

## Examples

- **[basic-chat.php](basic-chat.php)** - Send a simple chat message and get AI response
- **[conversation-management.php](conversation-management.php)** - Create and manage conversations
- **[file-upload.php](file-upload.php)** - Upload files to conversations
- **[file-retrieval.php](file-retrieval.php)** - Retrieve processed file transcripts
- **[project-management.php](project-management.php)** - Create and manage projects
- **[url-fetching.php](url-fetching.php)** - Fetch and process web content
- **[complete-workflow.php](complete-workflow.php)** - Full workflow example

## Running Examples

```bash
php basic-chat.php
php conversation-management.php
# etc...
```

## Error Handling

All examples include proper error handling and will display:
- HTTP status codes
- Error messages from the API
- Connection issues

## Authentication

All requests use the `X-API-Key` header for authentication:

```php
$headers = [
    'X-API-Key: ' . $apiKey,
    'Content-Type: application/json'
];
```
