/*
 * AI Chat Interface JavaScript
 * 
 * This file contains all the JavaScript functionality for the AI chat interface.
 * 
 * Last updated: 2025-08-08
 * Notes for AI: This is the main JavaScript file for the chat interface.
 * All chat-related functionality should be added here.
 */

// Global Variables
let currentConversationId = null;
let conversationHistory = [];
let currentProjectId = null;
let isProjectMode = false;
let currentConversationFiles = [];
let currentProjectFiles = [];

// DOM Elements
let chatMessages, questionInput, datasetInput, sendButton, fetchButton, urlInput, loading;
let conversationsList, projectsList, newChatBtn, newProjectBtn;
let uploadButton, fileInput, fileList;
let projectFilesBtn, projectFilesList, projectFilesSection;
let modelSelect;

// File type icons mapping
const fileTypeIcons = {
    'audio': '🎵',
    'image': '🖼️',
    'text': '📄',
    'document': '📋',
    'archive': '📦',
    'other': '📎'
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeElements();
    initializeEventListeners();
    initializeFileUpload();
    initializeProjectFiles();
    initializeUserMenu();
    initializeMobileToggles();
    
    loadConversations();
    loadProjects();
    loadAvailableModels();
    urlInput.focus();
    
    // Prevent default drag and drop behavior on the entire document
    // to avoid files opening in browser when dropped outside designated areas
    document.addEventListener('dragover', function(e) {
        e.preventDefault();
    });
    
    document.addEventListener('drop', function(e) {
        e.preventDefault();
    });
});

// Initialize Mobile Toggle Functionality
function initializeMobileToggles() {
    const chatHistoryToggle = document.getElementById('chatHistoryToggle');
    const projectsToggle = document.getElementById('projectsToggle');
    const chatHistorySection = document.getElementById('chatHistorySection');
    const projectsSection = document.getElementById('projectsSection');
    
    // Check if we're on mobile (screen width <= 480px)
    function isMobile() {
        return window.innerWidth <= 480;
    }
    
    // Initialize mobile sections state
    function initializeMobileSections() {
        if (isMobile()) {
            // On mobile, start with sections collapsed
            chatHistorySection.classList.add('collapsed');
            projectsSection.classList.add('collapsed');
            chatHistoryToggle.classList.add('collapsed');
            projectsToggle.classList.add('collapsed');
        } else {
            // On desktop, ensure sections are expanded and toggles are hidden
            chatHistorySection.classList.remove('collapsed');
            projectsSection.classList.remove('collapsed');
            chatHistoryToggle.classList.remove('collapsed');
            projectsToggle.classList.remove('collapsed');
        }
    }
    
    // Toggle section visibility
    function toggleSection(toggleBtn, section) {
        const isCollapsed = section.classList.contains('collapsed');
        const toggleIcon = toggleBtn.querySelector('.toggle-icon');
        
        if (isCollapsed) {
            // Expand section
            section.classList.remove('collapsed');
            section.classList.add('expanded');
            toggleBtn.classList.remove('collapsed');
            toggleBtn.classList.add('active');
            if (toggleIcon) toggleIcon.textContent = '▲';
        } else {
            // Collapse section
            section.classList.add('collapsed');
            section.classList.remove('expanded');
            toggleBtn.classList.add('collapsed');
            toggleBtn.classList.remove('active');
            if (toggleIcon) toggleIcon.textContent = '▼';
        }
    }
    
    // Event listeners for toggle buttons
    if (chatHistoryToggle && chatHistorySection) {
        chatHistoryToggle.addEventListener('click', function() {
            if (isMobile()) {
                toggleSection(chatHistoryToggle, chatHistorySection);
            }
        });
    }
    
    if (projectsToggle && projectsSection) {
        projectsToggle.addEventListener('click', function() {
            if (isMobile()) {
                toggleSection(projectsToggle, projectsSection);
            }
        });
    }
    
    // Handle window resize
    window.addEventListener('resize', function() {
        initializeMobileSections();
    });
    
    // Initialize on load
    initializeMobileSections();
}

// Initialize User Menu Dropdown
function initializeUserMenu() {
    const userMenuBtn = document.getElementById('userMenuBtn');
    const userDropdown = document.getElementById('userDropdown');
    const userPageLink = document.getElementById('userPageLink');
    const adminPageLink = document.getElementById('adminPageLink');
    
    if (userMenuBtn && userDropdown) {
        // Toggle dropdown on button click
        userMenuBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            userDropdown.classList.toggle('show');
            
            // Rotate arrow
            const arrow = userMenuBtn.querySelector('.dropdown-arrow');
            if (arrow) {
                arrow.style.transform = userDropdown.classList.contains('show') ? 'rotate(180deg)' : 'rotate(0deg)';
            }
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!userMenuBtn.contains(e.target)) {
                userDropdown.classList.remove('show');
                const arrow = userMenuBtn.querySelector('.dropdown-arrow');
                if (arrow) {
                    arrow.style.transform = 'rotate(0deg)';
                }
            }
        });
    }
    
    // User Page navigation
    if (userPageLink) {
        userPageLink.addEventListener('click', function(e) {
            e.preventDefault();
            // Navigate to user page
            window.location.href = '/user';
        });
    }
    
    // Admin Page navigation
    if (adminPageLink) {
        adminPageLink.addEventListener('click', function(e) {
            e.preventDefault();
            // TODO: Navigate to admin page
            window.location.href = '/admin';
        });
    }
}

// Initialize DOM elements
function initializeElements() {
    chatMessages = document.getElementById('chatMessages');
    questionInput = document.getElementById('questionInput');
    datasetInput = document.getElementById('datasetInput');
    sendButton = document.getElementById('sendButton');
    fetchButton = document.getElementById('fetchButton');
    urlInput = document.getElementById('urlInput');
    loading = document.getElementById('loading');
    
    conversationsList = document.getElementById('conversationsList');
    projectsList = document.getElementById('projectsList');
    newChatBtn = document.getElementById('newChatBtn');
    newProjectBtn = document.getElementById('newProjectBtn');
    
    uploadButton = document.getElementById('uploadButton');
    fileInput = document.getElementById('fileInput');
    fileList = document.getElementById('fileList');
    
    projectFilesBtn = document.getElementById('projectFilesBtn');
    projectFilesList = document.getElementById('projectFilesList');
    projectFilesSection = document.getElementById('projectFilesSection');
    
    modelSelect = document.getElementById('modelSelect');
}

// Initialize event listeners
function initializeEventListeners() {
    if (sendButton) sendButton.addEventListener('click', sendMessage);
    if (fetchButton) fetchButton.addEventListener('click', fetchUrlContent);
    if (newChatBtn) newChatBtn.addEventListener('click', newChat);
    if (newProjectBtn) {
        console.log('Binding + New Project button click handler');
        newProjectBtn.addEventListener('click', createNewProject);
    } else {
        console.error('newProjectBtn element not found!');
    }
    
    if (questionInput) {
        questionInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
    
    if (urlInput) {
        urlInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                fetchUrlContent();
            }
        });
    }
}

// Chat Functions
async function sendMessage() {
    const question = questionInput.value.trim();
    const dataset = datasetInput.value.trim();
    
    if (!question) {
        showError('Please enter a question');
        return;
    }
    
    let currentMessage = '';
    if (dataset) {
        currentMessage += `**Dataset/Context:**\n${dataset}\n\n`;
    }
    currentMessage += `**Question:** ${question}`;
    
    addMessage(currentMessage, 'user');
    
    conversationHistory.push({
        type: 'user',
        dataset: dataset,
        question: question,
        formatted: currentMessage
    });
    
    questionInput.value = '';
    
    loading.style.display = 'block';
    sendButton.disabled = true;
    datasetInput.disabled = true;
    questionInput.disabled = true;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                dataset: dataset,
                question: question,
                history: conversationHistory,
                conversation_id: currentConversationId,
                model: window.selectedModel || modelSelect?.value || 'gpt-oss:20b'
            })
        });

        const data = await response.json();

        if (response.ok) {
            addMessage(data.response);
            conversationHistory.push({
                type: 'ai',
                response: data.response
            });
            
            if (data.conversation_id && !currentConversationId) {
                currentConversationId = data.conversation_id;
                loadConversationsRespectingMode();
                loadConversationFiles(currentConversationId);
            }
        } else {
            showError(data.error || 'Unknown error occurred');
        }
    } catch (error) {
        showError('Failed to connect to AI service');
        console.error('Error:', error);
    } finally {
        loading.style.display = 'none';
        sendButton.disabled = false;
        datasetInput.disabled = false;
        questionInput.disabled = false;
        questionInput.focus();
    }
}

function addMessage(content, type = 'ai') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    // Handle null/undefined content
    const safeContent = content || '';
    
    try {
        messageContent.innerHTML = marked.parse(safeContent);
    } catch (error) {
        console.error('Markdown parsing error:', error);
        messageContent.textContent = safeContent; // Fallback to plain text
    }
    
    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Conversation Management
async function loadConversations() {
    try {
        const response = await fetch('/api/conversations');
        const data = await response.json();
        
        // Handle different response formats
        const conversations = Array.isArray(data) ? data : (data.conversations || []);
        
        displayConversations(conversations);
        updateConversationsCount(conversations.length);
    } catch (error) {
        console.error('Failed to load conversations:', error);
        showError('Failed to load conversations');
    }
}

// Helper function to load conversations respecting project mode
async function loadConversationsRespectingMode() {
    if (isProjectMode && currentProjectId) {
        await loadProjectConversations(currentProjectId);
    } else {
        await loadConversations();
    }
}

function displayConversations(conversations) {
    if (conversations.length === 0) {
        conversationsList.innerHTML = '<div style="text-align: center; padding: 20px; color: #6c757d;">No conversations yet. Start a new chat!</div>';
        return;
    }
    
    conversationsList.innerHTML = conversations.map(conv => `
        <div class="conversation-item ${conv.id === currentConversationId ? 'active' : ''}" 
             onclick="loadConversation(${conv.id})" data-conversation-id="${conv.id}"
             draggable="true" ondragstart="handleDragStart(event, ${conv.id})">
            <div class="conversation-header">
                <div class="conversation-title">${conv.title}</div>
                <div class="conversation-actions">
                    <button class="action-btn star" 
                            onclick="event.stopPropagation(); toggleConversationStar(${conv.id})" 
                            title="${conv.is_starred ? 'Remove star' : 'Add star'}">
                        ${conv.is_starred ? '⭐' : '☆'}
                    </button>
                    <button class="action-btn edit" 
                            onclick="event.stopPropagation(); editConversationTitle(${conv.id}, '${conv.title.replace(/'/g, "\\'")}')"
                            title="Edit title">
                        ✏️
                    </button>
                </div>
            </div>
            <div class="conversation-meta">
                <span>Updated: ${new Date(conv.updated_at).toLocaleDateString()}</span>
                <span>Created: ${new Date(conv.created_at).toLocaleDateString()}</span>
            </div>
        </div>
    `).join('');
}

async function loadConversation(conversationId) {
    try {
        const response = await fetch(`/api/conversations/${conversationId}`);
        const conversation = await response.json();
        
        if (response.ok) {
            currentConversationId = conversationId;
            conversationHistory = [];
            
            chatMessages.innerHTML = '';
            
            conversation.messages.forEach(msg => {
                if (msg.message_type === 'user') {
                    let formatted = '';
                    if (msg.dataset) {
                        formatted += `**Dataset/Context:**\n${msg.dataset}\n\n`;
                    }
                    formatted += `**Question:** ${msg.question || 'No question provided'}`;
                    
                    addMessage(formatted, 'user');
                    conversationHistory.push({
                        type: 'user',
                        dataset: msg.dataset || '',
                        question: msg.question || '',
                        formatted: formatted
                    });
                } else {
                    // Ensure response is not null/undefined
                    const response = msg.response || 'No response available';
                    addMessage(response);
                    conversationHistory.push({
                        type: 'ai',
                        response: response
                    });
                }
            });
            
            updateActiveConversation(conversationId);
            await loadConversationFiles(conversationId);
        }
    } catch (error) {
        console.error('Failed to load conversation:', error);
        showError('Failed to load conversation');
    }
}

function updateActiveConversation(conversationId) {
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.classList.remove('active');
    });
    
    const activeItem = document.querySelector(`[data-conversation-id="${conversationId}"]`);
    if (activeItem) {
        activeItem.classList.add('active');
    }
}

async function newChat() {
    try {
        // First, check if there's an existing unused conversation we can reuse
        const existingResponse = await fetch('/api/conversations');
        const existingData = await existingResponse.json();
        
        if (existingResponse.ok) {
            const conversations = Array.isArray(existingData) ? existingData : (existingData.conversations || []);
            
            // Look for an unused conversation (message_count = 0) with default title
            const unusedConversation = conversations.find(conv => 
                conv.message_count === 0 && 
                (conv.title === 'New Chat' || conv.title.startsWith('New Chat'))
            );
            
            if (unusedConversation) {
                // Reuse the existing unused conversation
                currentConversationId = unusedConversation.id;
                conversationHistory = [];
                chatMessages.innerHTML = '';
                questionInput.value = '';
                datasetInput.value = '';
                urlInput.value = '';
                
                displayFiles();
                
                document.querySelectorAll('.conversation-item').forEach(item => {
                    item.classList.remove('active');
                });
                
                // Update the active conversation in the UI
                updateActiveConversation(currentConversationId);
                await loadConversationFiles(currentConversationId);
                
                urlInput.focus();
                showMessage('Reusing existing unused chat', 'info');
                return;
            }
        }
        
        // If no unused conversation found, create a new one
        const response = await fetch('/api/conversations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: 'New Chat',
                dataset: ''
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentConversationId = data.conversation_id || data.id;
            conversationHistory = [];
            chatMessages.innerHTML = '';
            questionInput.value = '';
            datasetInput.value = '';
            urlInput.value = '';
            
            displayFiles();
            
            document.querySelectorAll('.conversation-item').forEach(item => {
                item.classList.remove('active');
            });
            
            // Refresh conversations list to show the new chat
            loadConversationsRespectingMode();
            
            urlInput.focus();
            showMessage('Created new chat', 'success');
        } else {
            showMessage('Failed to create new chat', 'error');
        }
    } catch (error) {
        console.error('Failed to create new chat:', error);
        showError('Failed to create new chat');
        showMessage('Failed to create new chat', 'error');
    }
}

async function fetchUrlContent() {
    const url = urlInput.value.trim();
    
    if (!url) {
        showError('Please enter a URL');
        return;
    }
    
    fetchButton.disabled = true;
    fetchButton.textContent = 'Fetching...';
    
    try {
        const response = await fetch('/api/fetch-url', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });

        const data = await response.json();

        if (response.ok) {
            datasetInput.value = data.content;
            urlInput.value = '';
            questionInput.focus();
        } else {
            showError(data.error || 'Failed to fetch URL content');
        }
    } catch (error) {
        showError('Failed to fetch URL content');
        console.error('Error:', error);
    } finally {
        fetchButton.disabled = false;
        fetchButton.textContent = 'Fetch';
    }
}

function updateConversationsCount(count) {
    const countElement = document.getElementById('conversationsCount');
    if (countElement) {
        countElement.textContent = `${count} conversation${count !== 1 ? 's' : ''}`;
    }
}

// Project Management
async function loadProjects() {
    try {
        const response = await fetch('/api/projects');
        const data = await response.json();
        
        // Handle different response formats
        const projects = Array.isArray(data) ? data : (data.projects || []);
        
        displayProjects(projects);
        checkAdminStatus();
    } catch (error) {
        console.error('Failed to load projects:', error);
        showError('Failed to load projects');
    }
}

function displayProjects(projects) {
    if (projects.length === 0) {
        projectsList.innerHTML = '<div style="text-align: center; padding: 20px; color: #6c757d;">No projects yet. Create your first project!</div>';
        return;
    }
    
    projectsList.innerHTML = projects.map(project => `
        <div class="project-item ${currentProjectId === project.id ? 'active' : ''}" 
             onclick="switchToProject(${project.id}, '${project.name.replace(/'/g, "\\'")}')"
             ondragover="handleDragOver(event)" ondrop="handleDrop(event, ${project.id})">
            <div class="project-header">
                <div class="project-title">${project.name}</div>
                <div class="project-actions">
                    <button class="action-btn star" 
                            onclick="event.stopPropagation(); toggleProjectStar(${project.id})" 
                            title="${project.is_starred ? 'Remove star' : 'Add star'}">
                        ${project.is_starred ? '⭐' : '☆'}
                    </button>
                    <button class="action-btn edit" 
                            onclick="event.stopPropagation(); editProjectTitle(${project.id}, '${project.name.replace(/'/g, "\\'")}')"
                            title="Edit project name">
                        ✏️
                    </button>
                </div>
            </div>
            <div class="project-meta">
                <span>${project.conversation_count} chat${project.conversation_count !== 1 ? 's' : ''}</span>
                <span>Updated: ${new Date(project.updated_at).toLocaleDateString()}</span>
            </div>
        </div>
    `).join('');
}

async function createNewProject() {
    const projectName = prompt('Enter project name:');
    if (!projectName || !projectName.trim()) {
        return;
    }
    
    try {
        const response = await fetch('/api/projects', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: projectName.trim() })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            loadProjects();
            showMessage('Project created successfully', 'success');
        } else {
            showError(data.error || 'Failed to create project');
        }
    } catch (error) {
        console.error('Failed to create project:', error);
        showError('Failed to create project');
    }
}

function switchToProject(projectId, projectName) {
    currentProjectId = projectId;
    isProjectMode = true;
    
    const indicator = document.getElementById('projectModeIndicator');
    const currentProjectNameSpan = document.getElementById('currentProjectName');
    
    if (indicator && currentProjectNameSpan) {
        indicator.style.display = 'block';
        currentProjectNameSpan.textContent = projectName;
    }
    
    document.querySelectorAll('.project-item').forEach(item => {
        item.classList.remove('active');
    });
    event.currentTarget.classList.add('active');
    
    loadProjectConversations(projectId);
    updateProjectFilesVisibility();
    
    if (currentConversationId) {
        newChat();
    }
}

function switchToGeneralMode() {
    currentProjectId = null;
    isProjectMode = false;
    
    const indicator = document.getElementById('projectModeIndicator');
    if (indicator) {
        indicator.style.display = 'none';
    }
    
    document.querySelectorAll('.project-item').forEach(item => {
        item.classList.remove('active');
    });
    
    loadConversations();
    updateProjectFilesVisibility();
}

// File Upload Functions
function initializeFileUpload() {
    if (!uploadButton || !fileInput) return;
    
    uploadButton.addEventListener('click', function() {
        fileInput.click();
    });
    
    fileInput.addEventListener('change', function(e) {
        const files = Array.from(e.target.files);
        if (files.length > 0) {
            uploadFiles(files);
        }
    });
    
    // Add drag and drop functionality to the chat area
    const chatArea = document.getElementById('chatMessages');
    if (chatArea) {
        chatArea.addEventListener('dragover', handleFileDragOver);
        chatArea.addEventListener('dragleave', handleFileDragLeave);
        chatArea.addEventListener('drop', handleFileDrop);
    }
    
    // Also add to the main chat panel
    const chatPanel = document.querySelector('.chat-panel');
    if (chatPanel) {
        chatPanel.addEventListener('dragover', handleFileDragOver);
        chatPanel.addEventListener('dragleave', handleFileDragLeave);
        chatPanel.addEventListener('drop', handleFileDrop);
    }
    
    // Add drag and drop to the upload button itself
    if (uploadButton) {
        uploadButton.addEventListener('dragover', handleFileDragOver);
        uploadButton.addEventListener('dragleave', handleFileDragLeave);
        uploadButton.addEventListener('drop', handleFileDrop);
    }
}

// File Drag and Drop Handlers
function handleFileDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    event.dataTransfer.dropEffect = 'copy';
    
    // Add visual feedback
    event.currentTarget.classList.add('file-drag-over');
}

function handleFileDragLeave(event) {
    event.preventDefault();
    event.stopPropagation();
    
    // Remove visual feedback
    event.currentTarget.classList.remove('file-drag-over');
}

function handleFileDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    
    // Remove visual feedback
    event.currentTarget.classList.remove('file-drag-over');
    
    const files = Array.from(event.dataTransfer.files);
    if (files.length > 0) {
        uploadFiles(files);
        showMessage(`Dropped ${files.length} file${files.length > 1 ? 's' : ''} for upload`, 'success');
    }
}

async function uploadFiles(files) {
    // If no conversation exists, show error message
    if (!currentConversationId) {
        showMessage('Please click "New Chat" first to enable file uploads', 'error');
        return;
    }
    
    for (const file of files) {
        await uploadSingleFile(file);
    }
    
    fileInput.value = '';
}

async function uploadSingleFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`/api/conversations/${currentConversationId}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentConversationFiles.push(data.file);
            displayFiles();
            showMessage(`File "${data.file.original_filename}" uploaded successfully`, 'success');
        } else {
            // Handle duplicate file error with more specific messaging
            if (response.status === 409 && data.duplicate_file) {
                showMessage(`File "${file.name}" already exists in this conversation (uploaded on ${new Date(data.duplicate_file.upload_date).toLocaleDateString()})`, 'warning');
            } else {
                showMessage(`Failed to upload "${file.name}": ${data.error}`, 'error');
            }
        }
    } catch (error) {
        console.error('Upload error:', error);
        showMessage(`Failed to upload "${file.name}": ${error.message}`, 'error');
    }
}

async function loadConversationFiles(conversationId) {
    if (!conversationId) {
        currentConversationFiles = [];
        displayFiles();
        return;
    }
    
    try {
        const response = await fetch(`/api/conversations/${conversationId}/files`);
        const data = await response.json();
        
        if (response.ok) {
            currentConversationFiles = data.files || [];
            displayFiles();
        } else {
            currentConversationFiles = [];
            displayFiles();
        }
    } catch (error) {
        console.error('Failed to load files:', error);
        currentConversationFiles = [];
        displayFiles();
    }
}

function displayFiles() {
    if (!fileList || currentConversationFiles.length === 0) {
        if (fileList) fileList.innerHTML = '';
        return;
    }
    
    fileList.innerHTML = currentConversationFiles.map(file => {
        // Debug logging to understand file processing status
        console.log(`File: ${file.original_filename}, has_been_processed: ${file.has_been_processed}, type: ${typeof file.has_been_processed}`);
        
        const icon = fileTypeIcons[file.file_type] || fileTypeIcons.other;
        const isImportant = file.is_project_important;
        const projectToggleIcon = isImportant ? '⭐' : '☆';
        const projectToggleClass = isImportant ? 'project-toggle important' : 'project-toggle';
        const projectToggleTitle = isImportant ? 'Remove from project important files' : 'Mark as project important';
        
        // Processing status
        const processingStatus = getProcessingStatusDisplay(file.has_been_processed);
        const processingTime = file.time_to_process ? `${file.time_to_process.toFixed(2)}s` : '';
        const processedDate = file.date_processed ? new Date(file.date_processed).toLocaleDateString() : '';
        
        // Show processing info for audio files or processed files
        const showProcessingInfo = file.file_type === 'audio' || file.has_been_processed > 0;
        const processingInfoHtml = showProcessingInfo ? `
            <div class="file-processing-info">
                <span class="processing-status ${getProcessingStatusClass(file.has_been_processed)}">${processingStatus}</span>
                ${processingTime ? `<span class="processing-time">${processingTime}</span>` : ''}
                ${processedDate ? `<span class="processed-date">${processedDate}</span>` : ''}
            </div>
        ` : '';
        
        // Admin controls for processing
        const adminControlsHtml = showProcessingInfo ? `
            <button class="file-action-btn processing" onclick="showProcessingDetails(${file.id})" title="View Processing Details">
                📄
            </button>
            ${(file.has_been_processed && file.has_been_processed > 0) ? `<button class="file-action-btn use-dataset" onclick="useFileAsDataset(${file.id})" title="Use as Dataset">📝</button>` : ''}
            ${(!file.has_been_processed || file.has_been_processed === 0) ? `<button class="file-action-btn reprocess" onclick="reprocessFile(${file.id})" title="Reprocess File">🔄</button>` : ''}
        ` : '';
        
        return `
            <div class="file-item ${file.file_type}" data-file-id="${file.id}">
                <div class="file-info">
                    <div class="file-icon">${icon}</div>
                    <div class="file-details">
                        <div class="file-name">${file.original_filename}</div>
                        <div class="file-meta">${file.file_size_formatted} • ${file.file_type} • ${new Date(file.upload_date).toLocaleDateString()}</div>
                        ${processingInfoHtml}
                    </div>
                </div>
                <div class="file-actions">
                    <button class="file-action-btn ${projectToggleClass}" onclick="toggleFileProjectImportance(${file.id})" title="${projectToggleTitle}">
                        ${projectToggleIcon}
                    </button>
                    ${adminControlsHtml}
                    <button class="file-action-btn download" onclick="downloadFile(${file.id})" title="Download">
                        ⬇️
                    </button>
                    <button class="file-action-btn delete" onclick="deleteFile(${file.id})" title="Delete">
                        🗑️
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

// Project Files Functions
function initializeProjectFiles() {
    if (!projectFilesBtn) return;
    
    projectFilesBtn.addEventListener('click', function() {
        if (projectFilesList.style.display === 'none') {
            projectFilesList.style.display = 'block';
            loadProjectFiles(currentProjectId);
        } else {
            projectFilesList.style.display = 'none';
        }
    });
}

function updateProjectFilesVisibility() {
    if (!projectFilesSection) return;
    
    if (currentProjectId) {
        projectFilesSection.style.display = 'block';
        loadProjectFiles(currentProjectId);
    } else {
        projectFilesSection.style.display = 'none';
        currentProjectFiles = [];
        if (document.getElementById('projectFilesCount')) {
            document.getElementById('projectFilesCount').textContent = '0';
        }
    }
}

// Admin Status Check
async function checkAdminStatus() {
    try {
        const response = await fetch('/api/user/status');
        const data = await response.json();
        
        if (response.ok && data.is_admin) {
            const adminSection = document.getElementById('adminSection');
            if (adminSection) {
                adminSection.style.display = 'block';
            }
        }
    } catch (error) {
        console.log('Could not check admin status:', error);
    }
}

// Additional Project Functions
async function loadProjectConversations(projectId) {
    try {
        const response = await fetch(`/api/projects/${projectId}/conversations`);
        const data = await response.json();
        
        if (response.ok) {
            displayConversations(data.conversations);
            updateConversationsCount(data.conversations.length);
        } else {
            showError('Failed to load project conversations');
        }
    } catch (error) {
        console.error('Failed to load project conversations:', error);
        showError('Failed to load project conversations');
    }
}

async function toggleConversationStar(conversationId) {
    try {
        const response = await fetch(`/api/conversations/${conversationId}/star`, {
            method: 'PUT'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            if (isProjectMode && currentProjectId) {
                loadProjectConversations(currentProjectId);
            } else {
                loadConversations();
            }
            showMessage(data.message, 'success');
        } else {
            showMessage(`Failed to toggle star: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Star toggle error:', error);
        showMessage(`Failed to toggle star: ${error.message}`, 'error');
    }
}

async function toggleProjectStar(projectId) {
    try {
        const response = await fetch(`/api/projects/${projectId}/star`, {
            method: 'PUT'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            loadProjects();
            showMessage(data.message, 'success');
        } else {
            showMessage(`Failed to toggle star: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Star toggle error:', error);
        showMessage(`Failed to toggle star: ${error.message}`, 'error');
    }
}

async function toggleFileProjectImportance(fileId) {
    try {
        const response = await fetch(`/api/files/${fileId}/toggle-project-important`, {
            method: 'PUT'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const fileIndex = currentConversationFiles.findIndex(f => f.id === fileId);
            if (fileIndex !== -1) {
                currentConversationFiles[fileIndex].is_project_important = data.is_project_important;
                displayFiles();
            }
            
            if (currentProjectId) {
                loadProjectFiles(currentProjectId);
            }
            
            showMessage(data.message, 'success');
        } else {
            showMessage(`Failed to toggle file importance: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Toggle importance error:', error);
        showMessage(`Failed to toggle file importance: ${error.message}`, 'error');
    }
}

async function downloadFile(fileId) {
    try {
        const response = await fetch(`/api/files/${fileId}/download`);
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = '';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } else {
            const data = await response.json();
            showMessage(`Failed to download file: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Download error:', error);
        showMessage(`Failed to download file: ${error.message}`, 'error');
    }
}

async function deleteFile(fileId) {
    if (!confirm('Are you sure you want to delete this file?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/files/${fileId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentConversationFiles = currentConversationFiles.filter(f => f.id !== fileId);
            displayFiles();
            showMessage('File deleted successfully', 'success');
        } else {
            showMessage(`Failed to delete file: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Delete error:', error);
        showMessage(`Failed to delete file: ${error.message}`, 'error');
    }
}

async function loadProjectFiles(projectId) {
    if (!projectId) {
        if (projectFilesList) {
            projectFilesList.innerHTML = '<div style="text-align: center; color: #6c757d; padding: 10px;">No project selected</div>';
        }
        if (document.getElementById('projectFilesCount')) {
            document.getElementById('projectFilesCount').textContent = '0';
        }
        return;
    }
    
    try {
        const response = await fetch(`/api/projects/${projectId}/important-files`);
        const data = await response.json();
        
        if (response.ok) {
            currentProjectFiles = data.files || [];
            displayProjectFiles();
            if (document.getElementById('projectFilesCount')) {
                document.getElementById('projectFilesCount').textContent = currentProjectFiles.length;
            }
        } else {
            console.error('Failed to load project files:', data.error);
            if (projectFilesList) {
                projectFilesList.innerHTML = '<div style="text-align: center; color: #dc3545; padding: 10px;">Failed to load files</div>';
            }
            if (document.getElementById('projectFilesCount')) {
                document.getElementById('projectFilesCount').textContent = '0';
            }
        }
    } catch (error) {
        console.error('Failed to load project files:', error);
        if (projectFilesList) {
            projectFilesList.innerHTML = '<div style="text-align: center; color: #dc3545; padding: 10px;">Error loading files</div>';
        }
        if (document.getElementById('projectFilesCount')) {
            document.getElementById('projectFilesCount').textContent = '0';
        }
    }
}

function displayProjectFiles() {
    if (!projectFilesList) return;
    
    if (currentProjectFiles.length === 0) {
        projectFilesList.innerHTML = '<div style="text-align: center; color: #6c757d; padding: 10px;">No important files in this project</div>';
        return;
    }
    
    projectFilesList.innerHTML = currentProjectFiles.map(file => {
        const icon = fileTypeIcons[file.file_type] || fileTypeIcons.other;
        
        return `
            <div class="project-file-item" data-file-id="${file.id}">
                <div class="project-file-info">
                    <div class="file-icon">${icon}</div>
                    <div>
                        <div class="project-file-name">${file.original_filename}</div>
                        <div class="project-file-meta">${file.file_size_formatted} • ${file.conversation_title}</div>
                    </div>
                </div>
                <div class="project-file-actions">
                    <button class="file-action-btn download" onclick="downloadFile(${file.id})" title="Download">
                        ⬇️
                    </button>
                    <button class="file-action-btn" onclick="openConversationWithFile(${file.conversation_id})" title="Go to conversation">
                        💬
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

async function openConversationWithFile(conversationId) {
    await loadConversation(conversationId);
    
    if (projectFilesList) {
        projectFilesList.style.display = 'none';
    }
    
    showMessage('Opened conversation containing the file', 'success');
}

// Drag and Drop Functions
let draggedConversationId = null;

function handleDragStart(event, conversationId) {
    draggedConversationId = conversationId;
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('text/html', event.target.outerHTML);
    event.target.style.opacity = '0.5';
}

function handleDragOver(event) {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
    event.currentTarget.classList.add('drag-over');
}

function handleDragLeave(event) {
    event.currentTarget.classList.remove('drag-over');
}

async function handleDrop(event, projectId) {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');
    
    if (!draggedConversationId) {
        return;
    }
    
    try {
        const response = await fetch(`/api/conversations/${draggedConversationId}/move-to-project`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ project_id: projectId })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Refresh both conversations and projects lists
            loadConversationsRespectingMode();
            loadProjects();
            showMessage(data.message || 'Conversation moved to project successfully', 'success');
        } else {
            showMessage(`Failed to move conversation: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Move conversation error:', error);
        showMessage(`Failed to move conversation: ${error.message}`, 'error');
    } finally {
        draggedConversationId = null;
        // Reset opacity for all conversation items
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.style.opacity = '1';
        });
    }
}

// Inline editing functions for conversation and project titles
function editConversationTitle(id, currentTitle) {
    const conversationItem = document.querySelector(`[data-conversation-id="${id}"]`);
    if (!conversationItem) return;
    
    const titleElement = conversationItem.querySelector('.conversation-title');
    if (!titleElement) return;
    
    // Create input element
    const input = document.createElement('input');
    input.type = 'text';
    input.value = currentTitle;
    input.className = 'title-edit-input';
    input.style.cssText = `
        width: 100%;
        padding: 4px 8px;
        border: 1px solid #007bff;
        border-radius: 4px;
        font-size: 14px;
        font-weight: 500;
        background: white;
        outline: none;
    `;
    
    // Replace title with input
    titleElement.style.display = 'none';
    titleElement.parentNode.insertBefore(input, titleElement.nextSibling);
    input.focus();
    input.select();
    
    // Handle save/cancel
    const saveTitle = async () => {
        const newTitle = input.value.trim();
        if (newTitle && newTitle !== currentTitle) {
            try {
                const response = await fetch(`/api/conversations/${id}/title`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ title: newTitle })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    titleElement.textContent = newTitle;
                    showMessage('Conversation title updated successfully', 'success');
                } else {
                    showMessage(`Failed to update title: ${data.error}`, 'error');
                }
            } catch (error) {
                console.error('Title update error:', error);
                showMessage(`Failed to update title: ${error.message}`, 'error');
            }
        }
        
        // Restore original title display
        input.remove();
        titleElement.style.display = '';
    };
    
    const cancelEdit = () => {
        input.remove();
        titleElement.style.display = '';
    };
    
    // Event listeners
    input.addEventListener('blur', saveTitle);
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            saveTitle();
        } else if (e.key === 'Escape') {
            e.preventDefault();
            cancelEdit();
        }
    });
}

function editProjectTitle(id, currentName) {
    const projectItem = document.querySelector(`[onclick*="switchToProject(${id}"]`);
    if (!projectItem) return;
    
    const titleElement = projectItem.querySelector('.project-title');
    if (!titleElement) return;
    
    // Create input element
    const input = document.createElement('input');
    input.type = 'text';
    input.value = currentName;
    input.className = 'title-edit-input';
    input.style.cssText = `
        width: 100%;
        padding: 4px 8px;
        border: 1px solid #007bff;
        border-radius: 4px;
        font-size: 14px;
        font-weight: 500;
        background: white;
        outline: none;
    `;
    
    // Replace title with input
    titleElement.style.display = 'none';
    titleElement.parentNode.insertBefore(input, titleElement.nextSibling);
    input.focus();
    input.select();
    
    // Handle save/cancel
    const saveTitle = async () => {
        const newName = input.value.trim();
        if (newName && newName !== currentName) {
            try {
                const response = await fetch(`/api/projects/${id}/name`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ name: newName })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    titleElement.textContent = newName;
                    // Update project mode indicator if this is the current project
                    if (currentProjectId === id) {
                        const currentProjectNameSpan = document.getElementById('currentProjectName');
                        if (currentProjectNameSpan) {
                            currentProjectNameSpan.textContent = newName;
                        }
                    }
                    showMessage('Project name updated successfully', 'success');
                } else {
                    showMessage(`Failed to update project name: ${data.error}`, 'error');
                }
            } catch (error) {
                console.error('Project name update error:', error);
                showMessage(`Failed to update project name: ${error.message}`, 'error');
            }
        }
        
        // Restore original title display
        input.remove();
        titleElement.style.display = '';
    };
    
    const cancelEdit = () => {
        input.remove();
        titleElement.style.display = '';
    };
    
    // Event listeners
    input.addEventListener('blur', saveTitle);
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            saveTitle();
        } else if (e.key === 'Escape') {
            e.preventDefault();
            cancelEdit();
        }
    });
}

// File Processing Status Functions

function getProcessingStatusDisplay(status) {
    switch (status) {
        case 0: return 'Unprocessed';
        case 1: return 'Processing...';
        case 2: return 'Processed';
        case 4: return 'Do Not Process';
        default: return 'Unknown';
    }
}

function getProcessingStatusClass(status) {
    switch (status) {
        case 0: return 'status-unprocessed';
        case 1: return 'status-processing';
        case 2: return 'status-processed';
        case 4: return 'status-do-not-process';
        default: return 'status-unknown';
    }
}

async function showProcessingDetails(fileId) {
    const file = currentConversationFiles.find(f => f.id === fileId);
    if (!file) {
        showMessage('File not found', 'error');
        return;
    }
    
    const statusText = getProcessingStatusDisplay(file.has_been_processed);
    const processedDate = file.date_processed ? new Date(file.date_processed).toLocaleString() : 'Not processed';
    const processingTime = file.time_to_process ? `${file.time_to_process.toFixed(2)} seconds` : 'N/A';
    
    let content = `
        <div class="processing-details">
            <h3>Processing Details: ${file.original_filename}</h3>
            <div class="detail-row">
                <strong>Status:</strong> <span class="${getProcessingStatusClass(file.has_been_processed)}">${statusText}</span>
            </div>
            <div class="detail-row">
                <strong>File Type:</strong> ${file.file_type}
            </div>
            <div class="detail-row">
                <strong>Processed Date:</strong> ${processedDate}
            </div>
            <div class="detail-row">
                <strong>Processing Time:</strong> ${processingTime}
            </div>
    `;
    
    if (file.human_notes) {
        content += `
            <div class="detail-row">
                <strong>Notes:</strong>
                <div class="human-notes">${file.human_notes}</div>
            </div>
        `;
    }
    
    if (file.transcoded_raw_file) {
        const preview = file.transcoded_raw_file.substring(0, 500);
        const hasMore = file.transcoded_raw_file.length > 500;
        content += `
            <div class="detail-row">
                <strong>Transcribed Content:</strong>
                <div class="transcribed-content">
                    <pre>${preview}${hasMore ? '...\n\n[Content truncated - full content available via download]' : ''}</pre>
                </div>
            </div>
        `;
    }
    
    content += `
            <div class="detail-actions">
                <textarea id="humanNotesInput" placeholder="Add human notes..." rows="3" style="width: 100%; margin: 10px 0;">${file.human_notes || ''}</textarea>
                <button onclick="updateHumanNotes(${fileId})" class="btn btn-primary">Update Notes</button>
                ${file.has_been_processed !== 1 ? `<button onclick="reprocessFile(${fileId})" class="btn btn-secondary">Reprocess</button>` : ''}
            </div>
        </div>
    `;
    
    // Create modal
    const modal = document.createElement('div');
    modal.className = 'processing-modal';
    modal.innerHTML = `
        <div class="processing-modal-content">
            ${content}
            <button class="processing-modal-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close on background click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

async function updateHumanNotes(fileId) {
    const notesInput = document.getElementById('humanNotesInput');
    if (!notesInput) return;
    
    const notes = notesInput.value.trim();
    
    try {
        const response = await fetch(`/api/files/${fileId}/processing`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ human_notes: notes })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Notes updated successfully', 'success');
            const file = currentConversationFiles.find(f => f.id === fileId);
            if (file) {
                file.human_notes = notes;
            }
        } else {
            showMessage(`Failed to update notes: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Update notes error:', error);
        showMessage(`Failed to update notes: ${error.message}`, 'error');
    }
}

async function reprocessFile(fileId) {
    if (!confirm('Are you sure you want to reprocess this file? This will reset its processing status and queue it for processing again.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/files/${fileId}/reprocess`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('File queued for reprocessing', 'success');
            displayFiles();
        } else {
            showMessage(`Failed to reprocess file: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Reprocess file error:', error);
        showMessage(`Failed to reprocess file: ${error.message}`, 'error');
    }
}

// Load available models from Ollama
async function loadAvailableModels() {
    try {
        const response = await fetch('/api/models');
        if (response.ok) {
            const data = await response.json();
            populateModelDropdown(data.models || []);
        } else {
            console.error('Failed to load models:', response.statusText);
            // Keep the default model if we can't load from Ollama
        }
    } catch (error) {
        console.error('Error loading models:', error);
        // Keep the default model if we can't load from Ollama
    }
}

// Populate the model dropdown with available models
function populateModelDropdown(models) {
    if (!modelSelect || !models.length) {
        return;
    }
    
    // Clear existing options
    modelSelect.innerHTML = '';
    
    // Get current selected model (default)
    const currentModel = 'gpt-oss:20b';
    let currentModelFound = false;
    
    // Add each model as an option
    models.forEach(model => {
        const option = document.createElement('option');
        option.value = model.name;
        option.textContent = model.name;
        
        // Select the current model if found
        if (model.name === currentModel) {
            option.selected = true;
            currentModelFound = true;
        }
        
        modelSelect.appendChild(option);
    });
    
    // If current model wasn't found in the list, select the first available model
    if (!currentModelFound && models.length > 0) {
        modelSelect.selectedIndex = 0;
    }
    
    // Add event listener for model changes
    modelSelect.addEventListener('change', handleModelChange);
}

// Handle model selection changes
function handleModelChange(event) {
    const selectedModel = event.target.value;
    console.log('Model changed to:', selectedModel);
    
    // Store the selected model for future chat requests
    // This will be used when sending chat messages
    window.selectedModel = selectedModel;
    
    // Show a message to indicate the model has been changed
    showMessage(`AI model changed to: ${selectedModel}`, 'info');
}

// Use processed file content as dataset
async function useFileAsDataset(fileId) {
    try {
        const response = await fetch(`/api/files/${fileId}/details`);
        if (response.ok) {
            const data = await response.json();
            
            // Check for processed content in the correct field name
            const processedContent = data.transcoded_raw_file || data.processed_content || '';
            
            if (processedContent && processedContent.trim()) {
                // Populate the dataset input with the processed content
                if (datasetInput) {
                    datasetInput.value = processedContent;
                    
                    // Show success message
                    showMessage(`Dataset populated with content from "${data.original_filename}"`, 'success');
                    
                    // Focus on the question input for user convenience
                    if (questionInput) {
                        questionInput.focus();
                    }
                } else {
                    showMessage('Dataset input not found', 'error');
                }
            } else {
                showMessage('No processed content available for this file', 'warning');
            }
        } else {
            const errorData = await response.json();
            showMessage(`Failed to load file content: ${errorData.error || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        console.error('Error loading file content:', error);
        showMessage(`Error loading file content: ${error.message}`, 'error');
    }
}
