(function() {
    // Global Variables
    const clientId = `client_${Math.random().toString(36).substring(2, 12)}`;
    let ws;
    let messageHistory = [];
    let isTyping = false;
    let currentSession = {
        id: new Date().toISOString(),
        title: "Current Session"
    };

    // DOM Elements
    let messageInput, sendButton, messagesContainer, welcomeScreen, messagesContainerParent;
    let crisisAlert, clearHistoryButton, newChatButton, promptButtons, chatHistoryList;
    let themeSelector, themeToggleButton, settingsButton;
    let themeToggleClickHandler; // To store the event handler reference

    // Initialize DOM elements
    function initDOMElements() {
        messageInput = document.getElementById('messageInput');
        sendButton = document.getElementById('sendButton');
        messagesContainer = document.getElementById('messages');
        welcomeScreen = document.getElementById('welcomeScreen');
        messagesContainerParent = document.querySelector('.messages-container');
        crisisAlert = document.getElementById('crisisAlert');
        clearHistoryButton = document.getElementById('clearHistoryButton');
        newChatButton = document.getElementById('newChatButton');
        promptButtons = document.querySelectorAll('.prompt-btn');
        chatHistoryList = document.getElementById('chatHistoryList');
        themeSelector = document.getElementById('themeSelector');
        themeToggleButton = document.getElementById('themeToggleButton');
        settingsButton = document.getElementById('settingsButton');
    }

    // Theme System
    function applyTheme(theme) {
        const body = document.body;
        
        if (theme === 'dark') {
            body.classList.add('dark-theme');
            localStorage.setItem('theme', 'dark');
        } else if (theme === 'light') {
            body.classList.remove('dark-theme');
            localStorage.setItem('theme', 'light');
        } else {
            localStorage.removeItem('theme');
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                body.classList.add('dark-theme');
            } else {
                body.classList.remove('dark-theme');
            }
        }
        
        updateThemeButton();
        updateThemeSelector();
    }

    function toggleTheme() {
        const body = document.body;
        const isDark = body.classList.contains('dark-theme');
        
        if (isDark) {
            body.classList.remove('dark-theme');
            localStorage.setItem('theme', 'light');
        } else {
            body.classList.add('dark-theme');
            localStorage.setItem('theme', 'dark');
        }
        
        updateThemeButton();
        updateThemeSelector();
    }

    function updateThemeButton() {
        const button = document.getElementById('themeToggleButton');
        if (button) {
            const icon = button.querySelector('i');
            const text = button.querySelector('span');
            const isDark = document.body.classList.contains('dark-theme');
            
            if (icon && text) {
                if (isDark) {
                    icon.className = 'fa-solid fa-sun';
                    text.textContent = 'Light Mode';
                } else {
                    icon.className = 'fa-solid fa-moon';
                    text.textContent = 'Dark Mode';
                }
            }
        }
    }

    function updateThemeSelector() {
        const selector = document.getElementById('themeSelector');
        if (selector) {
            const savedTheme = localStorage.getItem('theme');
            selector.value = savedTheme || 'system';
        }
    }

    function setupThemeButton() {
        const themeBtn = document.getElementById('themeToggleButton');
        if (themeBtn) {
            // If a handler was previously attached, remove it
            if (themeToggleClickHandler) {
                themeBtn.removeEventListener('click', themeToggleClickHandler);
            }
            
            // Define the new handler (or re-define if it captures new state, though not strictly necessary here)
            themeToggleClickHandler = function(e) {
                e.preventDefault();
                e.stopPropagation();
                toggleTheme(); // toggleTheme is accessible here
            };
            
            themeBtn.addEventListener('click', themeToggleClickHandler);
        }
    }

    function initThemeSystem() {
        // Apply saved theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            applyTheme(savedTheme);
        } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.body.classList.add('dark-theme');
        }
        
        // Setup theme toggle button
        setupThemeButton();
        
        // Setup settings button
        const settingsBtn = document.getElementById('settingsButton');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const modal = document.getElementById('settingsModal');
                if (modal) {
                    modal.classList.remove('hidden');
                }
            });
        }
        
        // Setup theme selector
        const themeSelect = document.getElementById('themeSelector');
        if (themeSelect) {
            themeSelect.addEventListener('change', function() {
                applyTheme(this.value);
            });
        }
        
        // Setup modal close buttons
        document.querySelectorAll('.close-modal').forEach(button => {
            const modal = button.closest('.modal');
            if (modal) {
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    modal.classList.add('hidden');
                });
            }
        });
        
        // Listen for system theme changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (!localStorage.getItem('theme')) {
                    if (e.matches) {
                        document.body.classList.add('dark-theme');
                    } else {
                        document.body.classList.remove('dark-theme');
                    }
                    updateThemeButton();
                }
            });
        }
        
        updateThemeButton();
        updateThemeSelector();
    }

    // Initialize the application
    function initApp() {
        initDOMElements();
        initThemeSystem();
        
        // Get or create session ID
        let sessionId = localStorage.getItem('currentSessionId');
        if (!sessionId) {
            sessionId = `user_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
            localStorage.setItem('currentSessionId', sessionId);
        }
        
        currentSession = {
            id: sessionId,
            title: "Current Session"
        };
        
        connectWebSocket(sessionId);
        loadConversationList();
        setupEventListeners();
        setupTextareaAutoResize();
    }

    // Setup event listeners
    function setupEventListeners() {
        if (sendButton) {
            sendButton.addEventListener('click', sendMessage);
        }
        
        if (messageInput) {
            messageInput.addEventListener('input', function() {
                sendButton.disabled = messageInput.value.trim() === '';
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
        }
        
        if (clearHistoryButton) {
            clearHistoryButton.addEventListener('click', clearChatHistory);
        }
        
        if (newChatButton) {
            newChatButton.addEventListener('click', startNewChat);
        }
        
        if (promptButtons) {
            promptButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const promptText = this.textContent;
                    if (messageInput) {
                        messageInput.value = promptText;
                        messageInput.dispatchEvent(new Event('input'));
                        sendMessage();
                    }
                });
            });
        }
        
        if (crisisAlert) {
            const closeBtn = crisisAlert.querySelector('.close-alert');
            if (closeBtn) {
                closeBtn.addEventListener('click', function() {
                    crisisAlert.classList.add('hidden');
                });
            }
        }
    }

    function setupTextareaAutoResize() {
        if (messageInput) {
            messageInput.addEventListener('input', function() {
                this.style.height = 'auto';
                const newHeight = Math.min(this.scrollHeight, 200);
                this.style.height = newHeight + 'px';
            });
        }
    }

    // Load all conversations
    async function loadConversationList() {
        try {
            const response = await fetch('/api/conversations');
            if (response.ok) {
                const conversations = await response.json();
                
                if (chatHistoryList) {
                    chatHistoryList.innerHTML = '';
                    
                    // Add current session first (if it exists)
                    if (currentSession && currentSession.id) {
                        const currentLi = document.createElement('li');
                        currentLi.classList.add('active');
                        currentLi.setAttribute('data-id', currentSession.id);
                        currentLi.innerHTML = `
                            <i class="fa-regular fa-comment-dots"></i>
                            <span>${currentSession.title}</span>
                        `;
                        chatHistoryList.appendChild(currentLi);
                    }
                    
                    // Add all other conversations (excluding current session to avoid duplicates)
                    for (const [userId, convData] of Object.entries(conversations)) {
                        // Skip if this is the current session (already added above)
                        if (currentSession && userId === currentSession.id) continue;
                        
                        const li = document.createElement('li');
                        li.setAttribute('data-id', userId);
                        li.innerHTML = `
                            <i class="fa-regular fa-comment-dots"></i>
                            <span>${convData.title}</span>
                        `;
                        
                        li.addEventListener('click', () => loadConversation(userId));
                        chatHistoryList.appendChild(li);
                    }
                }
            }
        } catch (error) {
            console.error('Error loading conversation list:', error);
        }
    }

    // Load a specific conversation
    async function loadConversation(userId) {
        try {
            const response = await fetch(`/api/conversations/${userId}`);
            if (response.ok) {
                const data = await response.json();
                const messages = data.messages;
                
                if (messagesContainer) {
                    messagesContainer.innerHTML = '';
                }
                
                if (welcomeScreen) {
                    welcomeScreen.classList.add('hidden');
                }
                if (messagesContainerParent) {
                    messagesContainerParent.style.display = 'block';
                }
                
                messageHistory = [];
                
                for (const msg of messages) {
                    if (msg.role === 'user') {
                        addUserMessage(msg.content);
                    } else if (msg.role === 'assistant') {
                        addBotMessage(msg.content);
                    }
                    
                    messageHistory.push({
                        role: msg.role,
                        content: msg.content,
                        timestamp: Date.now()
                    });
                }
                
                currentSession = {
                    id: userId,
                    title: messages.length > 0 && messages[0].role === 'user' 
                        ? truncateTitle(messages[0].content) 
                        : "Loaded Conversation"
                };
                
                document.querySelectorAll('.chat-history li').forEach(li => {
                    li.classList.remove('active');
                    if (li.getAttribute('data-id') === userId) {
                        li.classList.add('active');
                    }
                });
                
                if (ws) {
                    ws.close();
                }
                connectWebSocket(userId);
                
                scrollToBottom();
            }
        } catch (error) {
            console.error('Error loading conversation:', error);
        }
    }

    function truncateTitle(message) {
        const words = message.split(' ');
        if (words.length > 3) {
            return words.slice(0, 3).join(' ') + '...';
        }
        return message;
    }

    // Create a new conversation
    async function startNewChat() {
        try {
            const response = await fetch('/api/conversations/new', {
                method: 'POST'
            });
            
            if (response.ok) {
                const data = await response.json();
                const newUserId = data.user_id;
                
                // Clear current messages
                if (messagesContainer) {
                    messagesContainer.innerHTML = '';
                }
                
                messageHistory = [];
                
                if (crisisAlert) {
                    crisisAlert.classList.add('hidden');
                }
                
                // Show welcome screen for new conversation
                if (welcomeScreen) {
                    welcomeScreen.classList.remove('hidden');
                }
                if (messagesContainerParent) {
                    messagesContainerParent.style.display = 'none';
                }
                
                // Update current session
                currentSession = {
                    id: newUserId,
                    title: "New Conversation"
                };
                
                // Update localStorage with new session
                localStorage.setItem('currentSessionId', newUserId);
                
                // Reload conversation list to include the new conversation
                await loadConversationList();
                
                // Close existing WebSocket and connect to new one
                if (ws) {
                    ws.close();
                }
                connectWebSocket(newUserId);
            }
        } catch (error) {
            console.error('Error creating new conversation:', error);
        }
    }

    // WebSocket connection
    function connectWebSocket(userId = null) {
        const socketUserId = userId || currentSession.id;
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        
        ws = new WebSocket(`${protocol}//${host}/ws/${socketUserId}`);
        
        ws.onopen = () => {
            // Connection established
        };
        
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                
                if (data.type === 'message') {
                    hideWelcomeScreen();
                    stopTypingIndicator();
                    addBotMessage(data.content);
                    
                    messageHistory.push({
                        role: 'bot',
                        content: data.content,
                        timestamp: data.timestamp || Date.now()
                    });
                    
                    // Check for crisis keywords
                    const seriousCrisisKeywords = ['suicide', 'kill myself', 'end my life', 'harming yourself', 'self-harm'];
                    const moderateCrisisKeywords = ['crisis', 'emergency', 'urgent help'];

                    const content = data.content.toLowerCase();
                    const hasSeriousCrisisKeyword = seriousCrisisKeywords.some(keyword => content.includes(keyword));
                    const moderateKeywordsFound = moderateCrisisKeywords.filter(keyword => content.includes(keyword));

                    if (hasSeriousCrisisKeyword || moderateKeywordsFound.length >= 2) {
                        if (crisisAlert) {
                            crisisAlert.classList.remove('hidden');
                        }
                    }
                    
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
            addSystemMessage('Connection lost. Trying to reconnect...');
            setTimeout(() => connectWebSocket(socketUserId), 3000);
        };
        
        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            addSystemMessage('Error connecting to the server. Please refresh the page.');
        };
    }

    // Send a message
    function sendMessage() {
        if (!messageInput || !sendButton || !ws) return;
        
        const message = messageInput.value.trim();
        if (message && ws.readyState === WebSocket.OPEN && !isTyping) {
            hideWelcomeScreen();
            addUserMessage(message);
            
            messageHistory.push({
                role: 'user',
                content: message,
                timestamp: Date.now()
            });
            
            startTypingIndicator();
            
            ws.send(JSON.stringify({
                type: 'message',
                text: message
            }));
            
            messageInput.value = '';
            messageInput.style.height = 'auto';
            sendButton.disabled = true;
            messageInput.focus();
        }
    }

    function hideWelcomeScreen() {
        if (welcomeScreen && !welcomeScreen.classList.contains('hidden')) {
            welcomeScreen.classList.add('hidden');
            if (messagesContainerParent) {
                messagesContainerParent.style.display = 'block';
            }
        }
    }

    function startTypingIndicator() {
        if (!messagesContainer) return;
        
        isTyping = true;
        
        // Remove any existing dynamic typing indicator first to prevent multiple instances
        const existingIndicator = messagesContainer.querySelector('#typingIndicator.message-row');
        if (existingIndicator) {
            existingIndicator.remove();
        }

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

    function stopTypingIndicator() {
        isTyping = false;
        // const typingIndicator = document.getElementById('typingIndicator'); // Old way
        // Be more specific to remove the dynamically added indicator that has the message-row class
        const typingIndicator = messagesContainer.querySelector('#typingIndicator.message-row');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    function addUserMessage(content) {
        if (!messagesContainer) return;
        
        const messageRow = document.createElement('div');
        messageRow.classList.add('message-row', 'user');
        
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

    function addBotMessage(content) {
        if (!messagesContainer) return;
        
        const messageRow = document.createElement('div');
        messageRow.classList.add('message-row');
        
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
        
        const copyBtn = messageRow.querySelector('.copy-btn');
        if (copyBtn) {
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
        }
        
        scrollToBottom();
    }

    function addSystemMessage(content) {
        if (!messagesContainer) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('system-message');
        messageDiv.textContent = content;
        
        messagesContainer.appendChild(messageDiv);
        scrollToBottom();
    }

    function formatMessageContent(content) {
        let formatted = content.replace(/\n/g, '<br>');
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
        formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre>$1</pre>');
        formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
        formatted = formatted.replace(/^\s*-\s*(.*)/gm, '<ul><li>$1</li></ul>');
        formatted = formatted.replace(/<\/ul>\s*<ul>/g, '');
        formatted = formatted.replace(/^\s*(\d+)\.\s*(.*)/gm, '<ol><li>$2</li></ol>');
        formatted = formatted.replace(/<\/ol>\s*<ol>/g, '');
        
        return formatted;
    }

    function scrollToBottom() {
        if (messagesContainerParent) {
            messagesContainerParent.scrollTop = messagesContainerParent.scrollHeight;
        }
    }

    async function clearChatHistory() {
        try {
            const response = await fetch(`/clear_history/${currentSession.id}`, { method: 'POST' });
            if (response.ok) {
                if (messagesContainer) {
                    messagesContainer.innerHTML = '';
                }
                if (crisisAlert) {
                    crisisAlert.classList.add('hidden');
                }
                
                messageHistory = [];
                
                if (welcomeScreen) {
                    welcomeScreen.classList.remove('hidden');
                }
                if (messagesContainerParent) {
                    messagesContainerParent.style.display = 'none';
                }
                
                addSystemMessage('Conversation history has been cleared.');
            } else {
                addSystemMessage('Failed to clear history. Please try again.');
            }
        } catch (error) {
            console.error('Error clearing history:', error);
            addSystemMessage('Failed to clear history. Please try again.');
        }
    }

    function updateChatTitle(message) {
        const title = truncateTitle(message);
        currentSession.title = title;
        
        // Update the title in the conversation list immediately
        const currentSessionElement = document.querySelector(`li[data-id="${currentSession.id}"]`);
        if (currentSessionElement) {
            const titleSpan = currentSessionElement.querySelector('span');
            if (titleSpan) {
                titleSpan.textContent = title;
            }
        }
        
        // Don't reload the entire list, just update the current session title
    }

    // Call initApp when the DOM is ready
    if (document.readyState === "loading") {  // Or "interactive" or "complete"
        document.addEventListener("DOMContentLoaded", initApp);
    } else {  // DOMContentLoaded has already fired
        initApp();
    }
})();