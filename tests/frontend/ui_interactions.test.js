/**
 * @jest-environment jsdom
 */

const fs = require('fs');
const path = require('path');

// Object to store handlers for the current WebSocket mock instance
let wsEventHandlers = {};

// Mocking WebSocket globally for all tests in this file
global.WebSocket = jest.fn((url) => {
    // Ensure a fresh send mock for each instance, stored in wsEventHandlers for inspection
    const instanceSendMock = jest.fn();
    wsEventHandlers.send = instanceSendMock; // Storing the send mock for this instance

    const mockInstance = {
        url: url,
        readyState: global.WebSocket.OPEN, // Simulate an open connection by default

        // Actual send method on the instance will call the stored mock
        send: (...args) => {
            if (typeof wsEventHandlers.send === 'function') {
                return wsEventHandlers.send(...args);
            }
        },
        // close: jest.fn(), // Keep other methods as simple mocks or enhance as needed
        close: () => { // Potentially store a close mock in wsEventHandlers too if needed for assertions
            if (wsEventHandlers.closeMock) wsEventHandlers.closeMock();
        },

        // Event handlers setters capture functions from script.js into wsEventHandlers
        set onopen(fn) { wsEventHandlers.onopen = fn; },
        get onopen() { return wsEventHandlers.onopen; }, // Getter might not be strictly needed by test if wsEventHandlers is used directly
        set onmessage(fn) { wsEventHandlers.onmessage = fn; },
        get onmessage() { return wsEventHandlers.onmessage; },
        set onerror(fn) { wsEventHandlers.onerror = fn; },
        get onerror() { return wsEventHandlers.onerror; },
        set onclose(fn) { wsEventHandlers.onclose = fn; },
        get onclose() { return wsEventHandlers.onclose; },

        // Methods to simulate server-sent events
        _triggerOpen: (event) => {
            if (typeof wsEventHandlers.onopen === 'function') {
                wsEventHandlers.onopen(event);
            }
        },
        _triggerMessage: (event) => {
            if (typeof wsEventHandlers.onmessage === 'function') {
                wsEventHandlers.onmessage(event);
            }
        },
        _triggerError: (event) => {
            if (typeof wsEventHandlers.onerror === 'function') {
                wsEventHandlers.onerror(event);
            }
        },
        _triggerClose: (event) => {
            if (typeof wsEventHandlers.onclose === 'function') {
                wsEventHandlers.onclose(event);
            }
        }
    };
    return mockInstance;
});

// Define static constants like WebSocket.OPEN if script.js uses them
global.WebSocket.OPEN = 1;
global.WebSocket.CONNECTING = 0;
global.WebSocket.CLOSING = 2;
global.WebSocket.CLOSED = 3;

// Mocking fetch globally
global.fetch = jest.fn(() => Promise.resolve({ 
    ok: true, 
    json: () => Promise.resolve({}), // Default empty JSON response
    text: () => Promise.resolve("")   // Default empty text response
}));

// Mocking an element with a scrollIntoView method
global.Element.prototype.scrollIntoView = jest.fn();


// Import functions to be tested from static/script.js
// This assumes functions in script.js are exportable or globally accessible for testing.
// If script.js directly manipulates global DOM on load, we'll need to simulate that.
// For simplicity, let's assume we can import/require them or test their effects.
// const {
//   sendMessage, displayMessage, showTypingIndicator, hideTypingIndicator,
//   toggleTheme, applyTheme, initializeWebSocket, handleSystemMessage,
//   // ... other relevant functions
// } = require('../../static/script.js'); // Adjust path as necessary

// Or, if script.js runs on load and defines global functions/event listeners:
// We'd load the script in a JSDOM environment before each test.

describe('UI Interactions - static/script.js', () => {

    let scriptContent;
    let chatMessagesDiv;
    let messageInput;
    let sendButton;
    let themeToggle;
    let typingIndicator;

    beforeAll(() => {
        // Read the script content once
        const scriptPath = path.resolve(__dirname, '../../static/script.js');
        try {
            scriptContent = fs.readFileSync(scriptPath, 'utf8');
        } catch (err) {
            console.error("Failed to read static/script.js:", err);
            throw new Error("Could not read static/script.js. Make sure the path is correct.");
        }
    });

    beforeEach(() => {
        // Thoroughly reset JSDOM's document state
        document.head.innerHTML = ''; // Clear the head
        // Set up a basic HTML structure that script.js expects
        document.body.innerHTML = `
            <div id="messages"></div>
            <input type="text" id="messageInput" />
            <button id="sendButton">Send</button>
            <button id="themeToggleButton">Toggle Theme</button>
            <button id="newChatButton">New Chat</button>
            <button id="clearHistoryButton">Clear History</button>
            <div id="typingIndicator" style="display: none;">Bot is typing...</div>
            <template id="user-message-template">
                <div class="message user-message"><div class="message-content"></div></div>
            </template>
            <template id="bot-message-template">
                <div class="message bot-message"><div class="message-content"></div></div>
            </template>
            <template id="system-message-template">
                <div class="message system-message"><div class="message-content"></div></div>
            </template>
        `;

        chatMessagesDiv = document.getElementById('messages');
        messageInput = document.getElementById('messageInput');
        sendButton = document.getElementById('sendButton');
        themeToggle = document.getElementById('themeToggleButton');
        typingIndicator = document.getElementById('typingIndicator');

        global.WebSocket.mockClear();
        // Clear the stored event handlers and specific mocks for the new test
        wsEventHandlers = {
            send: undefined, // Explicitly reset send mock holder
            closeMock: jest.fn() // Example if we wanted to test close calls
        };

        if (global.WebSocket.mock.instances.length > 0) {
            const mockWsInstance = global.WebSocket.mock.instances[global.WebSocket.mock.instances.length - 1];
            mockWsInstance.send.mockClear();
            mockWsInstance.close.mockClear();
        }
        
        // Clear fetch mock calls before each test too
        global.fetch.mockClear();

        const scriptEl = document.createElement('script');
        scriptEl.textContent = scriptContent;
        document.head.appendChild(scriptEl);
    });

    describe('WebSocket Message Handling', () => {
        test('should display a user message when sent', () => {
            messageInput.value = 'Hello bot!';
            sendButton.click(); // This should trigger sendMessage in script.js, which calls addUserMessage
            
            // script.js creates: <div class="message-row user">...<div class="message-content">...<div class="message-text">content</div></div></div>
            const userMessageRows = chatMessagesDiv.querySelectorAll('.message-row.user');
            expect(userMessageRows.length).toBeGreaterThan(0);
            const lastUserMessageRow = userMessageRows[userMessageRows.length - 1];
            const messageTextDiv = lastUserMessageRow.querySelector('.message-text');
            expect(messageTextDiv).not.toBeNull();
            expect(messageTextDiv.textContent).toContain('Hello bot!');
        });

        test('should display a bot message when WebSocket receives a message', () => {
            // Ensure WebSocket was instantiated by script.js
            expect(global.WebSocket.mock.instances.length).toBeGreaterThan(0);
            // const mockWsInstance = global.WebSocket.mock.instances[global.WebSocket.mock.instances.length - 1]; // We might not need the instance for this part
            
            const mockBotMessage = { type: 'message', content: 'Hi user!', sender: 'bot', timestamp: Date.now() };
            
            // Manually trigger the onmessage handler stored in wsEventHandlers
            if (typeof wsEventHandlers.onmessage === 'function') {
                wsEventHandlers.onmessage({ data: JSON.stringify(mockBotMessage) });
            } else {
                console.warn("wsEventHandlers.onmessage is not a function in 'should display a bot message' test");
                expect(typeof wsEventHandlers.onmessage).toBe('function'); 
            }
            
            // script.js creates: <div class="message-row">...<div class="message-content"><div class="message-sender">Mindful Companion</div><div class="message-text">content</div>...</div></div>
            const botMessageRows = chatMessagesDiv.querySelectorAll('.message-row:not(.user)'); // Exclude user messages
            expect(botMessageRows.length).toBeGreaterThan(0);
            const lastBotMessageRow = botMessageRows[botMessageRows.length - 1];
            const messageTextDivBot = lastBotMessageRow.querySelector('.message-text');
            expect(messageTextDivBot).not.toBeNull();
            expect(messageTextDivBot.textContent).toContain('Hi user!');
        });

        test('should attempt to send user message via WebSocket when send button is clicked', () => {
            messageInput.value = 'Test message to send';
            sendButton.click();

            expect(global.WebSocket).toHaveBeenCalled(); 
            // We don't need the instance for the send assertion if send is captured in wsEventHandlers
            // const lastMockInstance = global.WebSocket.mock.instances[global.WebSocket.mock.instances.length - 1];
            // expect(lastMockInstance).toBeDefined(); 
            
            // Check the send mock stored in wsEventHandlers
            expect(wsEventHandlers.send).toHaveBeenCalledTimes(1);
            expect(wsEventHandlers.send).toHaveBeenCalledWith(JSON.stringify({
                type: 'message',
                text: 'Test message to send'
            }));
        });
    });

    describe('Typing Indicators', () => {
        test('should display typing indicator when user sends a message', () => {
            messageInput.value = 'Are you typing?';
            sendButton.click();
            // script.js's sendMessage calls startTypingIndicator()
            // which creates an element with id 'typingIndicator' (this is different from the pre-existing one)
            // The original typingIndicator div might be for bot typing. Let's check for the dynamic one.
            const dynamicTypingIndicator = document.getElementById('typingIndicator'); // This might be the one created by startTypingIndicator
            expect(dynamicTypingIndicator).not.toBeNull();
            // The actual check for style.display might be tricky if script.js immediately replaces it.
            // For now, let's assume its presence implies it's visible or was briefly.
            // A better check might be if the bot responds, then it hides.
            // The `startTypingIndicator` in script.js creates a new div.
            // The one we have in `beforeEach` `typingIndicator` is the template `div id="typing-indicator"`.
            // Let's look for the structure created by script.js
            const typingIndicatorMessageRow = chatMessagesDiv.querySelector('#typingIndicator.message-row');
            expect(typingIndicatorMessageRow).not.toBeNull();
        });

        test('should hide typing indicator when bot responds', () => {
            messageInput.value = 'Are you there?';
            sendButton.click(); // User sends, typing indicator appears

            let typingIndicatorMessageRow = chatMessagesDiv.querySelector('#typingIndicator.message-row');
            expect(typingIndicatorMessageRow).not.toBeNull();


            // Simulate WebSocket receiving a message from the bot
            expect(global.WebSocket.mock.instances.length).toBeGreaterThan(0);
            // const mockWsInstance = global.WebSocket.mock.instances[global.WebSocket.mock.instances.length - 1]; // Not needed for triggering if using wsEventHandlers directly

            const mockBotResponse = { type: 'message', content: 'Yes, I am here.', sender: 'bot' };
            // Manually trigger the onmessage handler stored in wsEventHandlers
            if (typeof wsEventHandlers.onmessage === 'function') {
                wsEventHandlers.onmessage({ data: JSON.stringify(mockBotResponse) });
            } else {
                console.warn("wsEventHandlers.onmessage is not a function in 'should hide typing indicator' test");
                expect(typeof wsEventHandlers.onmessage).toBe('function');
            }
            
            // After bot responds, script.js's onmessage calls stopTypingIndicator()
            typingIndicatorMessageRow = chatMessagesDiv.querySelector('#typingIndicator.message-row');
            expect(typingIndicatorMessageRow).toBeNull();
        });
    });

    describe('Theme Switching', () => {
        test('theme toggle button click should toggle theme class on body and in localStorage', () => {
            // Ensure initial state is light theme for predictability
            document.body.classList.remove('dark-theme');
            localStorage.setItem('theme', 'light');
            
            // `themeToggle` is already fetched in beforeEach and script.js no longer clones it.
            themeToggle.click(); 
            expect(document.body.classList.contains('dark-theme')).toBe(true);
            expect(localStorage.getItem('theme')).toBe('dark');

            themeToggle.click(); // Click again
            expect(document.body.classList.contains('dark-theme')).toBe(false);
            expect(localStorage.getItem('theme')).toBe('light');
        });
    });
});

// Note on imports/requires:
// The ability to directly require functions from `static/script.js` depends on how that
// file is structured. If it's a simple script that defines global functions or immediately
// invoked function expressions (IIFEs) that attach listeners, testing becomes more about
// simulating events and checking DOM state.
// If `script.js` can be refactored to export its functions (e.g., using CommonJS or ES6 modules,
// though that's less "vanilla" for a simple static script), testing becomes easier.
// For this sketch, I've assumed some functions might be directly callable/importable for clarity.
// In a real Jest setup, you might load the entire script.js into the JSDOM environment
// using `fs.readFileSync` and then `eval` or by attaching it as a script tag, then test effects. 