<?php
/**
 * Basic Chat Example - PHP
 * 
 * This example shows how to send a simple question to the AI and get a response.
 */

// Configuration
$apiKey = 'YOUR_API_KEY_HERE';  // Replace with your actual API key
$baseUrl = 'http://localhost:5785';  // Update for your server

// Question to ask the AI
$question = 'What is artificial intelligence?';

// Optional: Include dataset/context
$dataset = '';  // Leave empty for simple questions

// Prepare the request
$url = $baseUrl . '/api/v1/chat';
$data = [
    'question' => $question,
    'dataset' => $dataset
];

$headers = [
    'X-API-Key: ' . $apiKey,
    'Content-Type: application/json'
];

// Initialize cURL
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 60);

// Execute request
echo "Sending question: " . $question . "\n";
echo "Waiting for AI response...\n\n";

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

if (curl_errno($ch)) {
    echo "cURL Error: " . curl_error($ch) . "\n";
    curl_close($ch);
    exit(1);
}

curl_close($ch);

// Process response
if ($httpCode === 200) {
    $result = json_decode($response, true);
    
    if ($result) {
        echo "✅ AI Response:\n";
        echo "================\n";
        echo $result['response'] . "\n\n";
        
        echo "📊 Response Details:\n";
        echo "Model: " . $result['model'] . "\n";
        echo "Prompt Length: " . $result['prompt_length'] . " characters\n";
    } else {
        echo "❌ Error: Invalid JSON response\n";
        echo "Raw response: " . $response . "\n";
    }
} else {
    echo "❌ HTTP Error " . $httpCode . "\n";
    $error = json_decode($response, true);
    if ($error && isset($error['error'])) {
        echo "Error: " . $error['error'] . "\n";
    } else {
        echo "Raw response: " . $response . "\n";
    }
}
?>
