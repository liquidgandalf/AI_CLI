<?php
/**
 * File Upload Example - PHP
 * 
 * This example shows how to upload files to conversations for processing.
 */

// Configuration
$apiKey = 'YOUR_API_KEY_HERE';  // Replace with your actual API key
$baseUrl = 'http://localhost:5785';  // Update for your server

function makeRequest($url, $method = 'GET', $data = null, $headers = []) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_TIMEOUT, 60);
    
    if ($method === 'POST') {
        curl_setopt($ch, CURLOPT_POST, true);
        if ($data) {
            curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
        }
    }
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    return ['response' => $response, 'code' => $httpCode];
}

echo "=== File Upload Example ===\n\n";

// 1. First, create a conversation to upload files to
echo "1. Creating a conversation for file uploads...\n";
$headers = [
    'X-API-Key: ' . $apiKey,
    'Content-Type: application/json'
];

$newConvData = [
    'title' => 'File Upload Test - ' . date('Y-m-d H:i:s')
];

$result = makeRequest($baseUrl . '/api/v1/conversations', 'POST', $newConvData, $headers);

if ($result['code'] === 201) {
    $newConv = json_decode($result['response'], true);
    echo "✅ Created conversation ID: {$newConv['id']}\n\n";
    $conversationId = $newConv['id'];
} else {
    echo "❌ Error creating conversation: " . $result['response'] . "\n";
    exit(1);
}

// 2. Create a sample file to upload
echo "2. Creating a sample text file...\n";
$sampleContent = "This is a sample text file created for API testing.\n\n";
$sampleContent .= "File created at: " . date('Y-m-d H:i:s') . "\n";
$sampleContent .= "This file demonstrates the file upload functionality of the AI CLI API.\n\n";
$sampleContent .= "Supported file types include:\n";
$sampleContent .= "- Text files (.txt, .md, .html, .css, .js, .json, .xml, .py, .sql)\n";
$sampleContent .= "- Documents (.pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx)\n";
$sampleContent .= "- Images (.jpg, .jpeg, .png, .gif, .webp, .svg, .bmp)\n";
$sampleContent .= "- Audio (.mp3, .wav, .ogg, .m4a, .aac, .flac, .mpga)\n";
$sampleContent .= "- Archives (.zip, .tar, .gz, .rar)\n";

$tempFile = tempnam(sys_get_temp_dir(), 'api_test_') . '.txt';
file_put_contents($tempFile, $sampleContent);
echo "✅ Created sample file: " . basename($tempFile) . "\n\n";

// 3. Upload the file to the conversation
echo "3. Uploading file to conversation...\n";

// For file uploads, we need to use multipart/form-data
$uploadHeaders = [
    'X-API-Key: ' . $apiKey
    // Don't set Content-Type for multipart uploads - cURL will set it automatically
];

$postFields = [
    'file' => new CURLFile($tempFile, 'text/plain', 'sample-file.txt')
];

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $baseUrl . '/api/v1/conversations/' . $conversationId . '/upload');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $postFields);
curl_setopt($ch, CURLOPT_HTTPHEADER, $uploadHeaders);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 60);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

if (curl_errno($ch)) {
    echo "❌ cURL Error: " . curl_error($ch) . "\n";
    curl_close($ch);
    unlink($tempFile);
    exit(1);
}

curl_close($ch);

if ($httpCode === 201) {
    $uploadResult = json_decode($response, true);
    echo "✅ File uploaded successfully!\n";
    echo "  - File ID: {$uploadResult['id']}\n";
    echo "  - Filename: {$uploadResult['filename']}\n";
    echo "  - File Type: {$uploadResult['file_type']}\n";
    echo "  - File Size: {$uploadResult['file_size']} bytes\n";
    echo "  - Upload Date: {$uploadResult['upload_date']}\n\n";
    
    $fileId = $uploadResult['id'];
} else {
    echo "❌ Upload failed with HTTP code: " . $httpCode . "\n";
    $error = json_decode($response, true);
    if ($error && isset($error['error'])) {
        echo "Error: " . $error['error'] . "\n";
    } else {
        echo "Raw response: " . $response . "\n";
    }
    unlink($tempFile);
    exit(1);
}

// 4. Clean up the temporary file
unlink($tempFile);

// 5. Verify the file was associated with the conversation
echo "4. Verifying file association with conversation...\n";
$result = makeRequest($baseUrl . '/api/v1/conversations', 'GET', null, $headers);

if ($result['code'] === 200) {
    $conversations = json_decode($result['response'], true);
    
    foreach ($conversations['conversations'] as $conv) {
        if ($conv['id'] == $conversationId) {
            echo "✅ Conversation now has {$conv['file_count']} file(s) attached\n";
            break;
        }
    }
} else {
    echo "❌ Error verifying conversation: " . $result['response'] . "\n";
}

echo "\n=== File Upload Complete ===\n";
echo "\nNext steps:\n";
echo "- The uploaded file will be processed by the background worker\n";
echo "- Use file-retrieval.php to get the processed transcript\n";
echo "- Check the files page in your web interface to see processing status\n";
?>
