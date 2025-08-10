<?php
/**
 * Conversation Management Example - PHP
 * 
 * This example shows how to create conversations, list them, and add messages to existing conversations.
 */

// Configuration
$apiKey = 'YOUR_API_KEY_HERE';  // Replace with your actual API key
$baseUrl = 'http://localhost:5785';  // Update for your server

$headers = [
    'X-API-Key: ' . $apiKey,
    'Content-Type: application/json'
];

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

echo "=== Conversation Management Example ===\n\n";

// 1. List existing conversations
echo "1. Listing existing conversations...\n";
$result = makeRequest($baseUrl . '/api/v1/conversations', 'GET', null, $headers);

if ($result['code'] === 200) {
    $conversations = json_decode($result['response'], true);
    echo "✅ Found " . count($conversations['conversations']) . " conversations:\n";
    
    foreach ($conversations['conversations'] as $conv) {
        echo "  - ID: {$conv['id']}, Title: {$conv['title']}, Messages: {$conv['message_count']}, Files: {$conv['file_count']}\n";
    }
    echo "\n";
} else {
    echo "❌ Error listing conversations: " . $result['response'] . "\n\n";
}

// 2. Create a new conversation
echo "2. Creating a new conversation...\n";
$newConvData = [
    'title' => 'API Test Conversation - ' . date('Y-m-d H:i:s')
];

$result = makeRequest($baseUrl . '/api/v1/conversations', 'POST', $newConvData, $headers);

if ($result['code'] === 201) {
    $newConv = json_decode($result['response'], true);
    echo "✅ Created conversation:\n";
    echo "  - ID: {$newConv['id']}\n";
    echo "  - Title: {$newConv['title']}\n";
    echo "  - Created: {$newConv['created_at']}\n\n";
    
    $conversationId = $newConv['id'];
} else {
    echo "❌ Error creating conversation: " . $result['response'] . "\n\n";
    exit(1);
}

// 3. Send a message to the new conversation (using basic chat)
echo "3. Sending a message to the new conversation...\n";
$chatData = [
    'question' => 'Hello! This is a test message sent via API. Can you confirm you received this?',
    'dataset' => ''
];

$result = makeRequest($baseUrl . '/api/v1/chat', 'POST', $chatData, $headers);

if ($result['code'] === 200) {
    $chatResponse = json_decode($result['response'], true);
    echo "✅ AI Response:\n";
    echo "  " . substr($chatResponse['response'], 0, 100) . "...\n\n";
} else {
    echo "❌ Error sending chat message: " . $result['response'] . "\n\n";
}

// 4. List conversations again to see the update
echo "4. Listing conversations again to see updates...\n";
$result = makeRequest($baseUrl . '/api/v1/conversations', 'GET', null, $headers);

if ($result['code'] === 200) {
    $conversations = json_decode($result['response'], true);
    echo "✅ Updated conversation list:\n";
    
    foreach ($conversations['conversations'] as $conv) {
        if ($conv['id'] == $conversationId) {
            echo "  ➤ NEW: ID: {$conv['id']}, Title: {$conv['title']}, Messages: {$conv['message_count']}, Files: {$conv['file_count']}\n";
        } else {
            echo "  - ID: {$conv['id']}, Title: {$conv['title']}, Messages: {$conv['message_count']}, Files: {$conv['file_count']}\n";
        }
    }
} else {
    echo "❌ Error listing conversations: " . $result['response'] . "\n";
}

echo "\n=== Conversation Management Complete ===\n";
?>
