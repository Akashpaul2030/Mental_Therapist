// Global Variables
const clientId = `client_${Math.random().toString(36).substring(2, 12)}`;
let ws;
let messageHistory = [];
let darkModeEnabled = false;
let isTyping = false;
let currentSession = {
    id: new Date().toISOString(),
    title: "Current Session"
};

// DOM Elements
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const messagesContainer = document.getElementById('messages');
const welcomeScreen = document.getElementById('welcomeScreen');
const messagesContainerParent = document.querySelector('.messages-container');
const crisisAlert = document.getElementById('crisisAlert');
const clearHistoryButton = document.getElementById('clearHistoryButton');
const newChatButton = document.getElementById('newChatButton');
const promptButtons = document.querySelectorAll('.prompt-btn');
const chatHistoryList = document.getElementById('chatHistoryList');
const themeSelector = document.getElementById('themeSelector');

// Initialize the application
function initApp() {
    // Check for dark mode preference
    checkDarkModePreference();
    
    // Connect to WebSocket
    connectWebSocket();
    
    // Setup event listeners
    setupEventListeners();
    
    // Auto-resize textarea
    setupTextareaAutoResize();
}

// Check system dark mode preference
function checkDarkModePreference() {
    const savedTheme = localStorage.getItem('theme');
    
    if (savedTheme === 'dark') {
        enableDarkMode();
    } else if (savedTheme === 'light') {
        disableDarkMode();
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        enableDarkMode();
    }
    
    // Update theme selector if it exists
    if (themeSelector) {
        themeSelector.value = savedTheme || 'system';
    }
}

// Enable dark mode
function enableDarkMode() {
    document.body.classList.add('dark-theme');
    darkModeEnabled = true;
}

// Disable dark mode
function disableDarkMode() {
    document.body.classList.remove('dark-theme');
    darkModeEnabled = false;
}

// Setup event listeners
function setupEventListeners() {
    // Send button click
    sendButton.addEventListener('click', sendMessage);
    
    // Input keypress (Enter to send)
    messageInput.addEventListener('input', function() {
        sendButton.disabled = messageInput.value.trim() === '';
        
        // Auto-resize as you type
        this.style.height = 'auto';
        const newHeight = Math.min(this.scrollHeight, 200);
        this.style.height = newHeight + 'px';
    });
    
    messageInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Clear history button
    clearHistoryButton.addEventListener('click', clearChatHistory);
    
    // New chat button
    newChatButton.addEventListener('click', startNewChat);
    
    // Prompt buttons
    promptButtons.forEach(button => {
        button.addEventListener('click', function() {
            const promptText = this.textContent;
            messageInput.value = promptText;
            messageInput.dispatchEvent(new Event('input'));
            sendMessage();
        });
    });
    
    // Close crisis alert
    if (crisisAlert) {
        const closeBtn = crisisAlert.querySelector('.close-alert');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                crisisAlert.classList.add('hidden');
            });
        }
    }
    
    // Theme selector
    if (themeSelector) {
        themeSelector.addEventListener('change', function() {
            const selectedTheme = this.value;
            
            if (selectedTheme === 'dark') {
                enableDarkMode();
                localStorage.setItem('theme', 'dark');
            } else if (selectedTheme === 'light') {
                disableDarkMode();
                localStorage.setItem('theme', 'light');
            } else {
                // System preference
                localStorage.removeItem('theme');
                if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                    enableDarkMode();
                } else {
                    disableDarkMode();
                }
            }
        });
    }
    
    // Modal controls
    document.querySelectorAll('.close-modal').forEach(button => {
        const modal = button.closest('.modal');
        button.addEventListener('click', () => {
            modal.classList.add('hidden');
        });
    });
    
    // Settings button (if exists)
    const settingsButton = document.querySelector('.settings-btn');
    const settingsModal = document.getElementById('settingsModal');
    
    if (settingsButton && settingsModal) {
        settingsButton.addEventListener('click', () => {
            settingsModal.classList.remove('hidden');
        });
    }
}

// Setup textarea auto-resize
function setupTextareaAutoResize() {
    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        const newHeight = Math.min(this.scrollHeight, 200);
        this.style.height = newHeight + 'px';
    });
}

// Connect to WebSocket
function connectWebSocket() {
    // Get the current host
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    
    ws = new WebSocket(`${protocol}//${host}/ws/${clientId}`);
    
    ws.onopen = () => {
        console.log('Connected to WebSocket');
        // We'll let the server send the welcome message
    };
    
    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'message') {
                // Hide welcome screen if visible
                hideWelcomeScreen();
                
                // Stop typing indicator
                stopTypingIndicator();
                
                // Add message to DOM
                addBotMessage(data.content);
                
                // Store in message history
                messageHistory.push({
                    role: 'bot',
                    content: data.content,
                    timestamp: data.timestamp || Date.now()
                });
                
                // Check for crisis keywords
                const crisisKeywords = ['suicide', 'kill myself', 'end my life', 'crisis', 'emergency'];
                if (crisisKeywords.some(keyword => data.content.toLowerCase().includes(keyword))) {
                    crisisAlert.classList.remove('hidden');
                }
                
                // Update chat title if this is the first exchange
                if (messageHistory.length === 2) {
                    updateChatTitle(messageHistory[0].content);
                }
            } else if (data.type === 'system') {
                addSystemMessage(data.content);
            }
        } catch (error) {
            console.error('Error parsing message:', error);
        }
    };
    
    ws.onclose = () => {
        console.log('Disconnected from WebSocket');
        addSystemMessage('Connection lost. Trying to reconnect...');
        // Try to reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        addSystemMessage('Error connecting to the server. Please refresh the page.');
    };
}

// Send a message
function sendMessage() {
    const message = messageInput.value.trim();
    if (message && ws && ws.readyState === WebSocket.OPEN && !isTyping) {
        // Hide welcome screen if visible
        hideWelcomeScreen();
        
        // Add user message to UI
        addUserMessage(message);
        
        // Store in message history
        messageHistory.push({
            role: 'user',
            content: message,
            timestamp: Date.now()
        });
        
        // Show typing indicator
        startTypingIndicator();
        
        // Send message to server
        ws.send(JSON.stringify({
            type: 'message',
            text: message
        }));
        
        // Clear input
        messageInput.value = '';
        messageInput.style.height = 'auto';
        sendButton.disabled = true;
        
        // Focus back on input
        messageInput.focus();
    }
}

// Hide welcome screen
function hideWelcomeScreen() {
    if (welcomeScreen && !welcomeScreen.classList.contains('hidden')) {
        welcomeScreen.classList.add('hidden');
        messagesContainerParent.style.display = 'block';
    }
}

// Start typing indicator
function startTypingIndicator() {
    isTyping = true;
    
    const typingIndicator = document.createElement('div');
    typingIndicator.classList.add('message-row');
    typingIndicator.innerHTML = `
        <div class="avatar bot-avatar">
            <i class="fa-solid fa-brain"></i>
        </div>
        <div class="message-content">
            <div class="message-sender">Mindful Companion</div>
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    typingIndicator.id = 'typingIndicator';
    
    messagesContainer.appendChild(typingIndicator);
    scrollToBottom();
}

// Stop typing indicator
function stopTypingIndicator() {
    isTyping = false;
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Add user message to UI
function addUserMessage(content) {
    const messageRow = document.createElement('div');
    messageRow.classList.add('message-row', 'user');
    
    // Format message content
    const formattedContent = formatMessageContent(content);
    
    messageRow.innerHTML = `
        <div class="avatar">
            <i class="fa-solid fa-user"></i>
        </div>
        <div class="message-content">
            <div class="message-sender">You</div>
            <div class="message-text">${formattedContent}</div>
        </div>
    `;
    
    messagesContainer.appendChild(messageRow);
    scrollToBottom();
}

// Add bot message to UI
function addBotMessage(content) {
    const messageRow = document.createElement('div');
    messageRow.classList.add('message-row');
    
    // Format message content
    const formattedContent = formatMessageContent(content);
    
    messageRow.innerHTML = `
        <div class="avatar bot-avatar">
            <i class="fa-solid fa-brain"></i>
        </div>
        <div class="message-content">
            <div class="message-sender">Mindful Companion</div>
            <div class="message-text">${formattedContent}</div>
            <div class="message-actions">
                <button class="copy-btn"><i class="fa-regular fa-copy"></i> Copy</button>
            </div>
        </div>
    `;
    
    messagesContainer.appendChild(messageRow);
    
    // Add event listener to copy button
    const copyBtn = messageRow.querySelector('.copy-btn');
    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(content)
            .then(() => {
                copyBtn.innerHTML = '<i class="fa-solid fa-check"></i> Copied';
                setTimeout(() => {
                    copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i> Copy';
                }, 2000);
            })
            .catch(err => {
                console.error('Failed to copy text: ', err);
            });
    });
    
    scrollToBottom();
}

// Add system message to UI
function addSystemMessage(content) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('system-message');
    messageDiv.textContent = content;
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Format message content with simple markdown-like formatting
function formatMessageContent(content) {
    // Replace line breaks with <br>
    let formatted = content.replace(/\n/g, '<br>');
    
    // Bold text
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Italic text
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Code blocks
    formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre>$1</pre>');
    
    // Inline code
    formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Simple lists
    formatted = formatted.replace(/^\s*-\s*(.*)/gm, '<ul><li>$1</li></ul>');
    formatted = formatted.replace(/<\/ul>\s*<ul>/g, '');
    
    // Numbered lists
    formatted = formatted.replace(/^\s*(\d+)\.\s*(.*)/gm, '<ol><li>$2</li></ol>');
    formatted = formatted.replace(/<\/ol>\s*<ol>/g, '');
    
    return formatted;
}

// Scroll to bottom of messages
function scrollToBottom() {
    messagesContainerParent.scrollTop = messagesContainerParent.scrollHeight;
}

// Clear chat history
async function clearChatHistory() {
    try {
        const response = await fetch(`/clear_history/${clientId}`, { method: 'POST' });
        if (response.ok) {
            // Clear UI
            messagesContainer.innerHTML = '';
            crisisAlert.classList.add('hidden');
            
            // Clear message history
            messageHistory = [];
            
            // Show welcome screen again
            welcomeScreen.classList.remove('hidden');
            messagesContainerParent.style.display = 'none';
            
            // Add system message
            addSystemMessage('Conversation history has been cleared.');
        } else {
            addSystemMessage('Failed to clear history. Please try again.');
        }
    } catch (error) {
        console.error('Error clearing history:', error);
        addSystemMessage('Failed to clear history. Please try again.');
    }
}

// Start a new chat
function startNewChat() {
    // Clear message container
    messagesContainer.innerHTML = '';
    
    // Reset message history
    messageHistory = [];
    
    // Hide crisis alert if visible
    crisisAlert.classList.add('hidden');
    
    // Show welcome screen
    welcomeScreen.classList.remove('hidden');
    messagesContainerParent.style.display = 'none';
    
    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';
    sendButton.disabled = true;
    
    // Set current session
    currentSession = {
        id: new Date().toISOString(),
        title: "Current Session"
    };
    
    // Update UI
    updateChatHistoryList();
    
    // Reconnect WebSocket (optional, to start fresh)
    if (ws) {
        ws.close();
    }
    connectWebSocket();
}

// Update chat title based on first message
function updateChatTitle(message) {
    // Create a title from the first few words of the message
    const words = message.split(' ');
    const titleWords = words.slice(0, 4);
    const title = titleWords.join(' ') + (words.length > 4 ? '...' : '');
    
    currentSession.title = title;
    updateChatHistoryList();
}

// Update the chat history list in the sidebar
function updateChatHistoryList() {
    chatHistoryList.innerHTML = '';
    
    const li = document.createElement('li');
    li.classList.add('active');
    li.innerHTML = `
        <i class="fa-regular fa-comment-dots"></i>
        <span>${currentSession.title}</span>
    `;
    
    chatHistoryList.appendChild(li);
}

// Event listener for when DOM is loaded
document.addEventListener('DOMContentLoaded', initApp);

// Handle visibility change
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible') {
        // Check if WebSocket is closed and reconnect if needed
        if (ws && (ws.readyState === WebSocket.CLOSED || ws.readyState === WebSocket.CLOSING)) {
            connectWebSocket();
        }
    }
});