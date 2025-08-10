/*
 * User Page JavaScript
 * 
 * This file contains all JavaScript functionality for the user dashboard page.
 * Handles archive management, profile settings, and admin navigation.
 * 
 * Functions:
 * - Section navigation
 * - Archive loading and management
 * - Profile management
 * - Password change functionality
 * - Search and filtering
 * 
 * Last updated: 2025-08-08
 * Notes for AI: This is the main JavaScript file for the user page.
 * All user page functionality should be added here.
 */

// Global variables
let activeChats = [];
let activeProjects = [];
let hiddenChats = [];
let hiddenProjects = [];
let archivedChats = [];
let archivedProjects = [];

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeUserPage();
    loadActiveChats();
    loadActiveProjects();
    loadHiddenChats();
    loadHiddenProjects();
    loadArchivedChats();
    loadArchivedProjects();
});

// Initialize user page functionality
function initializeUserPage() {
    // Initialize search functionality
    initializeSearch();
    
    // Initialize password change modal
    initializePasswordModal();
    
    // Load initial data
    showSection('archives');
}

// Section Navigation
function showSection(sectionName) {
    // Hide all sections
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => section.classList.remove('active'));
    
    // Remove active class from all nav buttons
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(btn => btn.classList.remove('active'));
    
    // Show selected section
    const targetSection = document.getElementById(sectionName + '-section');
    if (targetSection) {
        targetSection.classList.add('active');
    }
    
    // Activate corresponding nav button
    const activeButton = Array.from(navButtons).find(btn => 
        btn.textContent.toLowerCase().includes(sectionName.toLowerCase()) ||
        (sectionName === 'archives' && btn.textContent.includes('Archives')) ||
        (sectionName === 'profile' && btn.textContent.includes('Profile')) ||
        (sectionName === 'admin' && btn.textContent.includes('Admin'))
    );
    
    if (activeButton) {
        activeButton.classList.add('active');
    }
}

// Archive Management Functions - Three Level System

// Active Conversations (Level 1)
async function loadActiveChats() {
    const loadingElement = document.getElementById('active-chats-loading');
    const listElement = document.getElementById('active-chats-list');
    
    if (loadingElement) loadingElement.style.display = 'block';
    if (listElement) listElement.innerHTML = '';
    
    try {
        const response = await fetch('/api/conversations/active');
        const data = await response.json();
        
        if (response.ok) {
            activeChats = data.conversations || [];
            displayActiveChats(activeChats);
        } else {
            showMessage('Failed to load active conversations: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error loading active chats:', error);
        showMessage('Failed to connect to server', 'error');
    } finally {
        if (loadingElement) loadingElement.style.display = 'none';
    }
}

// Active Projects (Level 1)
async function loadActiveProjects() {
    const loadingElement = document.getElementById('active-projects-loading');
    const listElement = document.getElementById('active-projects-list');
    
    if (loadingElement) loadingElement.style.display = 'block';
    if (listElement) listElement.innerHTML = '';
    
    try {
        const response = await fetch('/api/projects/active');
        const data = await response.json();
        
        if (response.ok) {
            activeProjects = data.projects || [];
            displayActiveProjects(activeProjects);
        } else {
            showMessage('Failed to load active projects: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error loading active projects:', error);
        showMessage('Failed to connect to server', 'error');
    } finally {
        if (loadingElement) loadingElement.style.display = 'none';
    }
}

// Hidden Conversations (Level 2)
async function loadHiddenChats() {
    const loadingElement = document.getElementById('hidden-chats-loading');
    const listElement = document.getElementById('hidden-chats-list');
    
    if (loadingElement) loadingElement.style.display = 'block';
    if (listElement) listElement.innerHTML = '';
    
    try {
        const response = await fetch('/api/conversations/hidden');
        const data = await response.json();
        
        if (response.ok) {
            hiddenChats = data.conversations || [];
            displayHiddenChats(hiddenChats);
        } else {
            showMessage('Failed to load hidden conversations: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error loading hidden chats:', error);
        showMessage('Failed to connect to server', 'error');
    } finally {
        if (loadingElement) loadingElement.style.display = 'none';
    }
}

// Hidden Projects (Level 2)
async function loadHiddenProjects() {
    const loadingElement = document.getElementById('hidden-projects-loading');
    const listElement = document.getElementById('hidden-projects-list');
    
    if (loadingElement) loadingElement.style.display = 'block';
    if (listElement) listElement.innerHTML = '';
    
    try {
        const response = await fetch('/api/projects/hidden');
        const data = await response.json();
        
        if (response.ok) {
            hiddenProjects = data.projects || [];
            displayHiddenProjects(hiddenProjects);
        } else {
            showMessage('Failed to load hidden projects: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error loading hidden projects:', error);
        showMessage('Failed to connect to server', 'error');
    } finally {
        if (loadingElement) loadingElement.style.display = 'none';
    }
}

// Archived Conversations (Level 3)
async function loadArchivedChats() {
    const loadingElement = document.getElementById('archived-chats-loading');
    const listElement = document.getElementById('archived-chats-list');
    
    if (loadingElement) loadingElement.style.display = 'block';
    if (listElement) listElement.innerHTML = '';
    
    try {
        const response = await fetch('/api/conversations/archived');
        const data = await response.json();
        
        if (response.ok) {
            archivedChats = data.conversations || [];
            displayArchivedChats(archivedChats);
        } else {
            showMessage('Failed to load archived conversations: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error loading archived chats:', error);
        showMessage('Failed to connect to server', 'error');
    } finally {
        if (loadingElement) loadingElement.style.display = 'none';
    }
}

// Archived Projects (Level 3)
async function loadArchivedProjects() {
    const loadingElement = document.getElementById('archived-projects-loading');
    const listElement = document.getElementById('archived-projects-list');
    
    if (loadingElement) loadingElement.style.display = 'block';
    if (listElement) listElement.innerHTML = '';
    
    try {
        const response = await fetch('/api/projects/archived');
        const data = await response.json();
        
        if (response.ok) {
            archivedProjects = data.projects || [];
            displayArchivedProjects(archivedProjects);
        } else {
            showMessage('Failed to load archived projects: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error loading archived projects:', error);
        showMessage('Failed to connect to server', 'error');
    } finally {
        if (loadingElement) loadingElement.style.display = 'none';
    }
}

// Display Functions for Three-Level System

function displayActiveChats(chats) {
    const listElement = document.getElementById('active-chats-list');
    if (!listElement) return;
    
    if (chats.length === 0) {
        listElement.innerHTML = '<div class="no-items">No active conversations found</div>';
        return;
    }
    
    let html = '';
    chats.forEach(chat => {
        const createdDate = new Date(chat.created_at).toLocaleDateString();
        const updatedDate = new Date(chat.updated_at).toLocaleDateString();
        const starIcon = chat.is_starred ? '⭐' : '';
        const projectInfo = chat.project_id ? ' (In Project)' : '';
        
        html += `
            <div class="archived-item active-item">
                <div class="item-info">
                    <h4 class="item-title">
                        <a href="/chat?conversation=${chat.id}" class="chat-link">
                            ${starIcon}${escapeHtml(chat.title)}${projectInfo}
                        </a>
                    </h4>
                    <div class="item-meta">
                        <span class="meta-item">📅 Created: ${createdDate}</span>
                        <span class="meta-item">🔄 Updated: ${updatedDate}</span>
                        <span class="meta-item">💬 Messages: ${chat.message_count}</span>
                        <span class="meta-item">📎 Files: ${chat.file_count || 0}</span>
                    </div>
                </div>
                <div class="item-actions">
                    <button onclick="hideChat(${chat.id})" class="action-btn btn-warning" title="Hide from front page">
                        👁️ Hide
                    </button>
                    <button onclick="archiveChat(${chat.id})" class="action-btn btn-danger" title="Archive fully">
                        📦 Archive
                    </button>
                </div>
            </div>
        `;
    });
    
    listElement.innerHTML = html;
}

function displayActiveProjects(projects) {
    const listElement = document.getElementById('active-projects-list');
    if (!listElement) return;
    
    if (projects.length === 0) {
        listElement.innerHTML = '<div class="no-items">No active projects found</div>';
        return;
    }
    
    let html = '';
    projects.forEach(project => {
        const createdDate = new Date(project.created_at).toLocaleDateString();
        const updatedDate = new Date(project.updated_at).toLocaleDateString();
        
        html += `
            <div class="archived-item active-item">
                <div class="item-info">
                    <h4 class="item-title">
                        <a href="/chat?project=${project.id}" class="project-link">
                            ${escapeHtml(project.name)}
                        </a>
                    </h4>
                    <p class="item-description">${escapeHtml(project.description || 'No description')}</p>
                    <div class="item-meta">
                        <span class="meta-item">📅 Created: ${createdDate}</span>
                        <span class="meta-item">🔄 Updated: ${updatedDate}</span>
                        <span class="meta-item">💬 Conversations: ${project.conversation_count}</span>
                    </div>
                </div>
                <div class="item-actions">
                    <button onclick="hideProject(${project.id})" class="action-btn btn-warning" title="Hide from front page">
                        👁️ Hide
                    </button>
                    <button onclick="archiveProject(${project.id})" class="action-btn btn-danger" title="Archive fully">
                        📦 Archive
                    </button>
                </div>
            </div>
        `;
    });
    
    listElement.innerHTML = html;
}

function displayHiddenChats(chats) {
    const listElement = document.getElementById('hidden-chats-list');
    if (!listElement) return;
    
    if (chats.length === 0) {
        listElement.innerHTML = '<div class="no-items">No hidden conversations found</div>';
        return;
    }
    
    let html = '';
    chats.forEach(chat => {
        const createdDate = new Date(chat.created_at).toLocaleDateString();
        const updatedDate = new Date(chat.updated_at).toLocaleDateString();
        const starIcon = chat.is_starred ? '⭐' : '';
        
        html += `
            <div class="archived-item hidden-item">
                <div class="item-info">
                    <h4 class="item-title">
                        <a href="/chat?conversation=${chat.id}" class="chat-link">
                            ${starIcon}${escapeHtml(chat.title)}
                        </a>
                    </h4>
                    <div class="item-meta">
                        <span class="meta-item">📅 Created: ${createdDate}</span>
                        <span class="meta-item">🔄 Updated: ${updatedDate}</span>
                        <span class="meta-item">💬 Messages: ${chat.message_count}</span>
                        <span class="meta-item">📎 Files: ${chat.file_count || 0}</span>
                    </div>
                </div>
                <div class="item-actions">
                    <button onclick="showChat(${chat.id})" class="action-btn btn-success" title="Show on front page">
                        👁️ Show
                    </button>
                    <button onclick="archiveChat(${chat.id})" class="action-btn btn-warning" title="Archive fully">
                        📦 Archive
                    </button>
                </div>
            </div>
        `;
    });
    
    listElement.innerHTML = html;
}

function displayHiddenProjects(projects) {
    const listElement = document.getElementById('hidden-projects-list');
    if (!listElement) return;
    
    if (projects.length === 0) {
        listElement.innerHTML = '<div class="no-items">No hidden projects found</div>';
        return;
    }
    
    let html = '';
    projects.forEach(project => {
        const createdDate = new Date(project.created_at).toLocaleDateString();
        const updatedDate = new Date(project.updated_at).toLocaleDateString();
        
        html += `
            <div class="archived-item hidden-item">
                <div class="item-info">
                    <h4 class="item-title">
                        <a href="/chat?project=${project.id}" class="project-link">
                            ${escapeHtml(project.name)}
                        </a>
                    </h4>
                    <p class="item-description">${escapeHtml(project.description || 'No description')}</p>
                    <div class="item-meta">
                        <span class="meta-item">📅 Created: ${createdDate}</span>
                        <span class="meta-item">🔄 Updated: ${updatedDate}</span>
                        <span class="meta-item">💬 Conversations: ${project.conversation_count}</span>
                    </div>
                </div>
                <div class="item-actions">
                    <button onclick="showProject(${project.id})" class="action-btn btn-success" title="Show on front page">
                        👁️ Show
                    </button>
                    <button onclick="archiveProject(${project.id})" class="action-btn btn-warning" title="Archive fully">
                        📦 Archive
                    </button>
                </div>
            </div>
        `;
    });
    
    listElement.innerHTML = html;
}

function displayArchivedChats(chats) {
    const listElement = document.getElementById('archived-chats-list');
    if (!listElement) return;
    
    if (chats.length === 0) {
        listElement.innerHTML = '<div class="no-items">No archived conversations found</div>';
        return;
    }
    
    let html = '';
    chats.forEach(chat => {
        const createdDate = new Date(chat.created_at).toLocaleDateString();
        const updatedDate = new Date(chat.updated_at).toLocaleDateString();
        const starIcon = chat.is_starred ? '⭐' : '';
        
        html += `
            <div class="archived-item">
                <div class="item-info">
                    <h4 class="item-title">${starIcon}${escapeHtml(chat.title)}</h4>
                    <div class="item-meta">
                        <span class="meta-item">📅 Created: ${createdDate}</span>
                        <span class="meta-item">🔄 Updated: ${updatedDate}</span>
                        <span class="meta-item">💬 Messages: ${chat.message_count}</span>
                    </div>
                </div>
                <div class="item-actions">
                    <button onclick="restoreChat(${chat.id})" class="action-btn btn-primary" title="Restore to active">
                        🔄 Restore
                    </button>
                    <button onclick="deleteChat(${chat.id})" class="action-btn btn-danger" title="Delete permanently">
                        🗑️ Delete
                    </button>
                </div>
            </div>
        `;
    });
    
    listElement.innerHTML = html;
}

function displayArchivedProjects(projects) {
    const listElement = document.getElementById('archived-projects-list');
    if (!listElement) return;
    
    if (projects.length === 0) {
        listElement.innerHTML = '<div class="no-items">No archived projects found</div>';
        return;
    }
    
    let html = '';
    projects.forEach(project => {
        const createdDate = new Date(project.created_at).toLocaleDateString();
        const updatedDate = new Date(project.updated_at).toLocaleDateString();
        
        html += `
            <div class="archived-item">
                <div class="item-info">
                    <h4 class="item-title">${escapeHtml(project.name)}</h4>
                    <p class="item-description">${escapeHtml(project.description || 'No description')}</p>
                    <div class="item-meta">
                        <span class="meta-item">📅 Created: ${createdDate}</span>
                        <span class="meta-item">🔄 Updated: ${updatedDate}</span>
                        <span class="meta-item">💬 Conversations: ${project.conversation_count}</span>
                    </div>
                </div>
                <div class="item-actions">
                    <button onclick="restoreProject(${project.id})" class="action-btn btn-primary" title="Restore to active">
                        🔄 Restore
                    </button>
                    <button onclick="deleteProject(${project.id})" class="action-btn btn-danger" title="Delete permanently">
                        🗑️ Delete
                    </button>
                </div>
            </div>
        `;
    });
    
    listElement.innerHTML = html;
}

// Archive Action Functions - Three Level System

// Show/Hide Actions (Level 1 <-> Level 2)
async function showChat(chatId) {
    try {
        const response = await fetch(`/api/conversations/${chatId}/show`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Conversation restored to front page', 'success');
            loadHiddenChats(); // Refresh hidden list
        } else {
            showMessage('Failed to show conversation: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error showing chat:', error);
        showMessage('Failed to connect to server', 'error');
    }
}

async function hideChat(chatId) {
    try {
        const response = await fetch(`/api/conversations/${chatId}/hide`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Conversation hidden from front page', 'success');
            loadActiveChats(); // Refresh active list
            loadHiddenChats(); // Refresh hidden list
        } else {
            showMessage('Failed to hide conversation: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error hiding chat:', error);
        showMessage('Failed to connect to server', 'error');
    }
}

async function showProject(projectId) {
    try {
        const response = await fetch(`/api/projects/${projectId}/show`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Project restored to front page', 'success');
            loadHiddenProjects(); // Refresh hidden list
        } else {
            showMessage('Failed to show project: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error showing project:', error);
        showMessage('Failed to connect to server', 'error');
    }
}

async function hideProject(projectId) {
    try {
        const response = await fetch(`/api/projects/${projectId}/hide`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Project hidden from front page', 'success');
            loadActiveProjects(); // Refresh active list
            loadHiddenProjects(); // Refresh hidden list
        } else {
            showMessage('Failed to hide project: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error hiding project:', error);
        showMessage('Failed to connect to server', 'error');
    }
}

// Archive Actions (Level 1/2 -> Level 3)
async function archiveChat(chatId) {
    try {
        const response = await fetch(`/api/conversations/${chatId}/archive`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Conversation archived', 'success');
            loadActiveChats(); // Refresh active list
            loadHiddenChats(); // Refresh hidden list
            loadArchivedChats(); // Refresh archived list
        } else {
            showMessage('Failed to archive conversation: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error archiving chat:', error);
        showMessage('Failed to connect to server', 'error');
    }
}

async function archiveProject(projectId) {
    try {
        const response = await fetch(`/api/projects/${projectId}/archive`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Project archived', 'success');
            loadActiveProjects(); // Refresh active list
            loadHiddenProjects(); // Refresh hidden list
            loadArchivedProjects(); // Refresh archived list
        } else {
            showMessage('Failed to archive project: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error archiving project:', error);
        showMessage('Failed to connect to server', 'error');
    }
}

// Restore Actions (Level 3 -> Level 1)
async function restoreChat(chatId) {
    try {
        const response = await fetch(`/api/conversations/${chatId}/restore`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Conversation restored successfully', 'success');
            loadArchivedChats(); // Refresh the list
        } else {
            showMessage('Failed to restore conversation: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error restoring chat:', error);
        showMessage('Failed to connect to server', 'error');
    }
}

async function restoreProject(projectId) {
    try {
        const response = await fetch(`/api/projects/${projectId}/restore`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Project restored successfully', 'success');
            loadArchivedProjects(); // Refresh the list
        } else {
            showMessage('Failed to restore project: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error restoring project:', error);
        showMessage('Failed to connect to server', 'error');
    }
}

async function deleteChat(chatId) {
    try {
        const response = await fetch(`/api/conversations/${chatId}`, {
            method: 'DELETE'
        });
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Conversation deleted permanently', 'success');
            loadArchivedChats(); // Refresh the list
        } else {
            showMessage('Failed to delete conversation: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error deleting chat:', error);
        showMessage('Failed to connect to server', 'error');
    }
}

async function deleteProject(projectId) {
    try {
        const response = await fetch(`/api/projects/${projectId}`, {
            method: 'DELETE'
        });
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Project deleted permanently', 'success');
            loadArchivedProjects(); // Refresh the list
        } else {
            showMessage('Failed to delete project: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error deleting project:', error);
        showMessage('Failed to connect to server', 'error');
    }
}

// Search Functionality - Three Level System
function initializeSearch() {
    // Active items search
    const activeChatsSearch = document.getElementById('activeChatsSearch');
    const activeProjectsSearch = document.getElementById('activeProjectsSearch');
    
    // Hidden items search
    const hiddenChatsSearch = document.getElementById('hiddenChatsSearch');
    const hiddenProjectsSearch = document.getElementById('hiddenProjectsSearch');
    
    // Archived items search
    const archivedChatsSearch = document.getElementById('archivedChatsSearch');
    const archivedProjectsSearch = document.getElementById('archivedProjectsSearch');
    
    if (activeChatsSearch) {
        activeChatsSearch.addEventListener('input', function() {
            filterActiveChats(this.value);
        });
    }
    
    if (activeProjectsSearch) {
        activeProjectsSearch.addEventListener('input', function() {
            filterActiveProjects(this.value);
        });
    }
    
    if (hiddenChatsSearch) {
        hiddenChatsSearch.addEventListener('input', function() {
            filterHiddenChats(this.value);
        });
    }
    
    if (hiddenProjectsSearch) {
        hiddenProjectsSearch.addEventListener('input', function() {
            filterHiddenProjects(this.value);
        });
    }
    
    if (archivedChatsSearch) {
        archivedChatsSearch.addEventListener('input', function() {
            filterArchivedChats(this.value);
        });
    }
    
    if (archivedProjectsSearch) {
        archivedProjectsSearch.addEventListener('input', function() {
            filterArchivedProjects(this.value);
        });
    }
}

function filterActiveChats(searchTerm) {
    const filteredChats = activeChats.filter(chat => 
        chat.title.toLowerCase().includes(searchTerm.toLowerCase())
    );
    displayActiveChats(filteredChats);
}

function filterActiveProjects(searchTerm) {
    const filteredProjects = activeProjects.filter(project => 
        project.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
    displayActiveProjects(filteredProjects);
}

function filterHiddenChats(searchTerm) {
    const filteredChats = hiddenChats.filter(chat => 
        chat.title.toLowerCase().includes(searchTerm.toLowerCase())
    );
    displayHiddenChats(filteredChats);
}

function filterHiddenProjects(searchTerm) {
    const filteredProjects = hiddenProjects.filter(project => 
        project.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
    displayHiddenProjects(filteredProjects);
}

function filterArchivedChats(searchTerm) {
    const filteredChats = archivedChats.filter(chat => 
        chat.title.toLowerCase().includes(searchTerm.toLowerCase())
    );
    displayArchivedChats(filteredChats);
}

function filterArchivedProjects(searchTerm) {
    const filteredProjects = archivedProjects.filter(project => 
        project.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
    displayArchivedProjects(filteredProjects);
}

// Password Change Modal
function initializePasswordModal() {
    const form = document.getElementById('changePasswordForm');
    if (form) {
        form.addEventListener('submit', handlePasswordChange);
    }
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('changePasswordModal');
        if (event.target === modal) {
            closeChangePasswordModal();
        }
    });
}

function showChangePasswordModal() {
    const modal = document.getElementById('changePasswordModal');
    if (modal) {
        modal.style.display = 'block';
        const currentPasswordInput = document.getElementById('currentPassword');
        if (currentPasswordInput) {
            currentPasswordInput.focus();
        }
    }
}

function closeChangePasswordModal() {
    const modal = document.getElementById('changePasswordModal');
    if (modal) {
        modal.style.display = 'none';
        const form = document.getElementById('changePasswordForm');
        if (form) {
            form.reset();
        }
    }
}

async function handlePasswordChange(e) {
    e.preventDefault();
    
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmNewPassword = document.getElementById('confirmNewPassword').value;
    
    // Validation
    if (newPassword !== confirmNewPassword) {
        showMessage('New passwords do not match', 'error');
        return;
    }
    
    if (newPassword.length < 6) {
        showMessage('New password must be at least 6 characters long', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/user/change-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            })
        });
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Password changed successfully', 'success');
            closeChangePasswordModal();
        } else {
            showMessage('Failed to change password: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error changing password:', error);
        showMessage('Failed to connect to server', 'error');
    }
}

// Utility Functions
function showMessage(message, type = 'info') {
    const messageArea = document.getElementById('message-area');
    if (!messageArea) return;
    
    messageArea.innerHTML = `<div class="${type}">${escapeHtml(message)}</div>`;
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (messageArea.innerHTML.includes(message)) {
            messageArea.innerHTML = '';
        }
    }, 5000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
