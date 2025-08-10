<?php
/**
 * File Retrieval Example - PHP
 * 
 * This example shows how to retrieve processed file transcripts and raw content.
 */

// Configuration
$apiKey = 'YOUR_API_KEY_HERE';  // Replace with your actual API key
$baseUrl = 'http://localhost:5785';  // Update for your server

function makeRequest($url, $method = 'GET', $data = null, $headers = []) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    
    if ($method === 'POST') {
        curl_setopt($ch, CURLOPT_POST, true);
        if ($data) {
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        }
    }
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    return ['response' => $response, 'code' => $httpCode];
}

echo "=== File Retrieval Example ===\n\n";

$headers = [
    'X-API-Key: ' . $apiKey,
    'Content-Type: application/json'
];

// 1. List all conversations to find ones with files
echo "1. Finding conversations with files...\n";
$result = makeRequest($baseUrl . '/api/v1/conversations', 'GET', null, $headers);

if ($result['code'] === 200) {
    $conversations = json_decode($result['response'], true);
    $conversationsWithFiles = array_filter($conversations['conversations'], function($conv) {
        return $conv['file_count'] > 0;
    });
    
    if (empty($conversationsWithFiles)) {
        echo "❌ No conversations with files found. Please run file-upload.php first.\n";
        exit(1);
    }
    
    echo "✅ Found " . count($conversationsWithFiles) . " conversation(s) with files:\n";
    foreach ($conversationsWithFiles as $conv) {
        echo "  - ID: {$conv['id']}, Title: {$conv['title']}, Files: {$conv['file_count']}\n";
    }
    echo "\n";
    
    // Use the first conversation with files
    $selectedConv = reset($conversationsWithFiles);
    $conversationId = $selectedConv['id'];
    echo "Using conversation ID: {$conversationId}\n\n";
    
} else {
    echo "❌ Error listing conversations: " . $result['response'] . "\n";
    exit(1);
}

// 2. Get files for the selected conversation
echo "2. Getting files for conversation {$conversationId}...\n";
$result = makeRequest($baseUrl . '/api/conversations/' . $conversationId . '/files', 'GET', null, $headers);

if ($result['code'] === 200) {
    $filesData = json_decode($result['response'], true);
    $files = $filesData['files'];
    
    echo "✅ Found " . count($files) . " file(s):\n";
    foreach ($files as $file) {
        $status = '';
        switch ($file['has_been_processed']) {
            case 0: $status = 'Unprocessed'; break;
            case 1: $status = 'Processing'; break;
            case 2: $status = 'Processed'; break;
            case 4: $status = 'Do Not Process'; break;
            default: $status = 'Unknown'; break;
        }
        
        echo "  - ID: {$file['id']}, Name: {$file['original_filename']}, Type: {$file['file_type']}, Status: {$status}\n";
    }
    echo "\n";
    
    if (empty($files)) {
        echo "❌ No files found in conversation.\n";
        exit(1);
    }
    
    $selectedFile = reset($files);
    $fileId = $selectedFile['id'];
    
} else {
    echo "❌ Error getting files: " . $result['response'] . "\n";
    exit(1);
}

// 3. Get detailed file information
echo "3. Getting detailed file information for file ID {$fileId}...\n";
$result = makeRequest($baseUrl . '/api/files/' . $fileId . '/details', 'GET', null, $headers);

if ($result['code'] === 200) {
    $fileDetails = json_decode($result['response'], true);
    
    echo "✅ File Details:\n";
    echo "  - Original Name: {$fileDetails['original_filename']}\n";
    echo "  - File Type: {$fileDetails['file_type']}\n";
    echo "  - MIME Type: {$fileDetails['mime_type']}\n";
    echo "  - File Size: {$fileDetails['file_size']} bytes\n";
    echo "  - Processing Status: ";
    
    switch ($fileDetails['has_been_processed']) {
        case 0: echo "Unprocessed\n"; break;
        case 1: echo "Processing\n"; break;
        case 2: echo "Processed\n"; break;
        case 4: echo "Do Not Process\n"; break;
        default: echo "Unknown\n"; break;
    }
    
    echo "  - Upload Date: {$fileDetails['upload_date']}\n";
    
    if (isset($fileDetails['processed_content']) && !empty($fileDetails['processed_content'])) {
        echo "\n📄 PROCESSED TRANSCRIPT:\n";
        echo "========================\n";
        echo $fileDetails['processed_content'] . "\n\n";
    } else {
        echo "  - No processed content available yet\n\n";
    }
    
} else {
    echo "❌ Error getting file details: " . $result['response'] . "\n";
}

// 4. Download raw file content
echo "4. Downloading raw file content...\n";
$downloadHeaders = [
    'X-API-Key: ' . $apiKey
];

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $baseUrl . '/api/files/' . $fileId . '/download');
curl_setopt($ch, CURLOPT_HTTPHEADER, $downloadHeaders);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 30);

$rawContent = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$contentType = curl_getinfo($ch, CURLINFO_CONTENT_TYPE);
curl_close($ch);

if ($httpCode === 200) {
    echo "✅ Raw file downloaded successfully\n";
    echo "  - Content Type: {$contentType}\n";
    echo "  - Content Length: " . strlen($rawContent) . " bytes\n";
    
    // If it's a text file, show a preview
    if (strpos($contentType, 'text/') === 0) {
        echo "\n📄 RAW CONTENT PREVIEW (first 500 chars):\n";
        echo "==========================================\n";
        echo substr($rawContent, 0, 500);
        if (strlen($rawContent) > 500) {
            echo "\n... (truncated)\n";
        }
        echo "\n\n";
    } else {
        echo "  - Binary file content not displayed\n\n";
    }
} else {
    echo "❌ Error downloading file: HTTP {$httpCode}\n";
    if ($rawContent) {
        $error = json_decode($rawContent, true);
        if ($error && isset($error['error'])) {
            echo "Error: " . $error['error'] . "\n";
        }
    }
    echo "\n";
}

echo "=== File Retrieval Complete ===\n";
echo "\nNote: If files show as 'Unprocessed', you may need to:\n";
echo "1. Start the background worker: python process_unprocessed_files.py --loop\n";
echo "2. Wait for processing to complete\n";
echo "3. Run this script again to see processed content\n";
?>
