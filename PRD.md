# Product Requirements Document: Mental Health Chatbot - Mindful Companion

## 1. Introduction

A comprehensive mental health support chatbot built with Retrieval-Augmented Generation (RAG) to provide factually accurate, empathetic, and ethically safe responses. The system integrates advanced AI technologies with mental health best practices to offer personalized support while maintaining strict ethical guidelines.

The problem addressed is providing accessible and reliable mental health support through an AI-powered chatbot interface.

## 2. Goals

The primary and secondary objectives of the Mindful Companion chatbot are as follows:

- To provide factually accurate, empathetic, and ethically safe responses to users seeking mental health support.
- To integrate advanced AI technologies, specifically RAG, with established mental health best practices and curated knowledge.
- To offer personalized support by remembering user preferences, triggers, and conversation history, tailoring responses accordingly.
- To maintain strict ethical guidelines, prioritizing user privacy, data safety, and responsible AI interaction.
- To provide immediate access to crisis hotlines and emergency resources for users identified as being in acute distress.
- To encourage users to seek diagnosis, treatment, and ongoing care from licensed mental health professionals when appropriate, acting as a supportive tool rather than a replacement.
- To actively filter harmful or inappropriate content to maintain a safe and supportive environment for all users.

## 3. Target Users

The Mindful Companion chatbot is designed for individuals seeking accessible and immediate mental health support, guidance, and information. This includes, but is not limited to:

- Individuals experiencing symptoms of common mental health concerns such as anxiety, stress, or low mood, who are looking for initial support or coping strategies.
- Users who may be hesitant to seek traditional therapy or are looking for a supplementary tool to complement their existing mental health care.
- People seeking a confidential space to explore their feelings and gain insights based on evidence-based psychological principles (e.g., CBT techniques).
- Users in need of quick access to information about mental health topics or crisis resources.
- Individuals looking for personalized support that adapts to their stated concerns and preferences over time.

The chatbot is not intended for individuals in acute, severe crisis requiring immediate medical or psychiatric intervention (though it will guide them to such resources), nor is it a replacement for diagnosis or treatment by qualified healthcare professionals.

## 4. Project Overview

### 4.1. RAG Architecture

🔍 Advanced RAG Architecture
Vector Database Integration: Uses FAISS for efficient semantic search and document retrieval
Intelligent Chunking: Employs RecursiveCharacterTextSplitter with optimized parameters (chunk_size: 1000, overlap: 200)
Context-Aware Responses: Generates responses grounded in curated mental health resources

### 4.2. Crisis Detection

🛡️ Crisis Detection & Safety
Multi-Level Crisis Detection: Identifies severe and moderate crisis keywords with context awareness
Immediate Crisis Response: Provides instant access to crisis hotlines and emergency resources
Safety Verification: Follows up to ensure users seek appropriate help
Real-time Crisis Alerts: Visual alerts in the web interface for immediate attention

### 4.3. Ethical Guidelines

🧭 Ethical AI Guidelines
Medical Disclaimer System: Clear boundaries preventing medical diagnoses or prescriptions
Content Moderation: OpenAI Moderation API integration for harmful content filtering
Professional Care Redirection: Encourages seeking licensed mental health professionals
Privacy-First Design: No permanent storage of sensitive conversations

### 4.4. Memory Management

💬 Intelligent Memory Management
Conversation Continuity: Maintains context across interactions using LangChain's ChatMessageHistory
User Detail Extraction: Automatically identifies and remembers user preferences, triggers, and concerns
Personalized Responses: Tailors advice based on previously shared information
Session Management: Handles multiple concurrent conversations

### 4.5. Web Interface

🎨 Modern Web Interface
Real-time Communication: WebSocket-based chat with typing indicators
Responsive Design: Works seamlessly across desktop and mobile devices
Dark/Light Theme: Adaptive theming with system preference detection
Conversation Management: Create, load, and manage multiple chat sessions

🏗️ Technical Architecture (Frontend Stack)
FastAPI: Async web framework with WebSocket support
Vanilla JavaScript: Lightweight, responsive client-side application
CSS3: Modern styling with CSS custom properties and animations
Real-time Updates: Live conversation synchronization

## 5. Functional Requirements

The Mindful Companion chatbot must perform the following functions:

### 5.1. RAG Architecture & Knowledge Retrieval
1.  **Vector Database Integration**: The system must use FAISS for vector database integration, enabling efficient semantic search and document retrieval from the knowledge base.
2.  **Intelligent Chunking**: The system must employ `RecursiveCharacterTextSplitter` with a configured chunk size of 1000 characters and an overlap of 200 characters for intelligent document chunking before embedding.
3.  **Context-Grounded Responses**: The system must generate responses that are grounded in information retrieved from curated mental health resources (FAQs, CBT exercises, crisis intervention guides).
4.  **Knowledge Base Access**: The system must be able to retrieve and utilize information from the following knowledge base files:
    *   `faqs/mental_health_faqs.md` (for anxiety, depression, stress management)
    *   `cbt_strategies/cbt_exercises.md` (for CBT techniques)
    *   `crisis_resources/crisis_intervention.md` (for crisis hotlines and procedures)

### 5.2. Crisis Detection & Safety
1.  **Multi-Level Keyword Detection**: The system must identify severe and moderate crisis-related keywords and phrases within user messages, with awareness of contextual cues (e.g., negation, emotional intensifiers).
2.  **Immediate Crisis Response**: Upon detection of a crisis, the system must provide an immediate response containing relevant crisis hotlines and emergency resource information, tailored by region if possible.
3.  **Safety Verification Follow-up**: After providing an initial crisis response, the system must attempt to follow up to encourage the user to seek appropriate help and to verify if they have done so.
4.  **Visual Crisis Alerts (Web Interface)**: The web interface must display clear, real-time visual alerts when a crisis situation is detected or being handled, to draw attention to the critical nature of the interaction.

### 5.3. Ethical AI Guidelines & Content Moderation
1.  **Medical Disclaimer System**: The system must present clear disclaimers at the start of conversations and as needed, stating that it is an AI and not a substitute for professional medical/mental health advice, diagnosis, or treatment.
2.  **Medical Advice Redirection**: The system must detect when users are seeking medical diagnoses or prescriptions and redirect them to consult qualified healthcare professionals.
3.  **Content Moderation**: The system must integrate the OpenAI Moderation API (or equivalent) to filter user input and bot responses for harmful, inappropriate, or unsafe content.
4.  **Redirection to Professionals**: The system should generally encourage users to seek support from licensed mental health professionals for diagnosis, treatment, and ongoing care, especially when user needs exceed the chatbot's capabilities.

### 5.4. Intelligent Memory Management & Personalization
1.  **Conversation Continuity**: The system must maintain conversation context across multiple turns within a session using mechanisms like LangChain's `ChatMessageHistory`.
2.  **User Detail Extraction & Storage**: The system must automatically attempt to identify and remember key user details shared during conversations, such as name, preferences, stated triggers, and concerns.
3.  **Personalized Responses**: The system must tailor its advice and responses based on previously shared user information and conversation history to provide a more personal and continuous experience.
4.  **Session Management**: The system must be able to handle multiple concurrent user conversations independently, maintaining distinct memory and context for each.

### 5.5. Web Interface Functionality
1.  **Real-time Communication**: The web interface must support real-time, bidirectional chat communication using WebSockets, including visual typing indicators for both user and bot.
2.  **Responsive Design**: The web interface must be responsive and usable across various devices, including desktops, tablets, and mobile phones.
3.  **Adaptive Theming**: The web interface must support both dark and light themes, with the ability to adapt based on user system preferences and allow manual toggling.
4.  **Conversation Management UI**: The web interface must allow users to create new chat sessions, load previous sessions from a list, and manage their ongoing conversations.

### 5.6. Backend API Endpoints
1.  **WebSocket Chat Endpoint**: The system must provide a WebSocket endpoint (e.g., `ws://localhost:8000/ws/{client_id}`) for real-time, stateful chat communication.
2.  **Create New Conversation API**: The system must provide a REST API endpoint (e.g., `POST /api/conversations/new`) to initiate a new chat session and receive a unique session/client ID.
3.  **List Conversations API**: The system must provide a REST API endpoint (e.g., `GET /api/conversations`) to retrieve a list of all existing conversations (or conversations accessible to the user).
4.  **Get Specific Conversation API**: The system must provide a REST API endpoint (e.g., `GET /api/conversations/{user_id}`) to retrieve the message history and details of a specific conversation.
5.  **Clear History API**: The system must provide a REST API endpoint (e.g., `POST /clear_history/{client_id}`) to clear the conversation history for a given session.
6.  **Health Check API**: The system must provide a REST API endpoint (e.g., `GET /health`) for system health monitoring.

## 6. Non-Functional Requirements

### 6.1. Performance
1.  **Response Quality**: The system must generate responses with a balance of creativity, factual accuracy (grounded in the knowledge base), and empathy, utilizing GPT-4 with a configured temperature of 0.3.
2.  **Search Efficiency**: The system must ensure efficient semantic search and document retrieval from the vector database (FAISS).
3.  **Latency**: Response times for typical user queries should be within acceptable limits for a real-time chat application (specific metrics to be defined, e.g., <3-5 seconds for P95).

### 6.2. Security & Safety
1.  **Content Filtering**: The system must utilize the OpenAI Moderation API (or equivalent) to filter both user input and generated responses for harmful, inappropriate, or unsafe content.
2.  **Medical Boundaries**: The system must maintain clear boundaries by not providing medical diagnoses or prescriptions, and redirecting users to professionals for such needs.
3.  **Data Privacy**: **No permanent storage of sensitive personal information or full conversation transcripts beyond the active session duration should occur without explicit user consent and appropriate anonymization/security measures if ever implemented.** (Current implementation note: `src/memory_manager.py` saves to `data/chat_memory.json`, which needs review against this NFR - See Task 8.2).
4.  **Crisis Follow-up**: The system must include a mechanism to follow up with users identified to be in crisis to encourage them to seek appropriate help.

### 6.3. Maintainability
1.  **Programming Language**: The backend of the project primarily uses Python 3.10+.
2.  **Frameworks**: The backend API is built using FastAPI. The frontend is built using Vanilla JavaScript and CSS3.
3.  **Modularity**: Code should be organized into logical modules with clear responsibilities (e.g., knowledge base, response generation, crisis detection, ethical guidelines, memory management).
4.  **Test Coverage**: The project aims to include comprehensive test suites for backend components (knowledge base, response generator, crisis detector, ethical guidelines, memory manager, and integration tests for core logic). (Note: Current test coverage for memory management and API endpoints needs improvement - See Tasks 7.4, 7.5).
5.  **Configuration**: Key parameters (e.g., model names, API keys, paths) should be configurable via environment variables or configuration files.

### 6.4. Scalability
1.  **Semantic Search**: The system is designed for efficient semantic search using FAISS, which can scale to large knowledge bases.
2.  **Concurrent Users**: The system must handle multiple concurrent user conversations effectively. (Current implementation uses user_id based separation; further stress testing may be needed for high concurrency).

### 6.5. Usability & Accessibility
1.  **Responsive Design**: The web interface must be responsive and provide a good user experience across desktop, tablet, and mobile devices.
2.  **Adaptive Theming**: The web interface must support both dark and light themes, with detection of system preferences and a manual toggle.
3.  **Clarity**: Chatbot responses should be clear, concise, and easy to understand.
4.  **Accessibility (A11y)**: The web interface should strive to meet WCAG 2.1 AA accessibility standards where feasible (e.g., keyboard navigation, sufficient color contrast, ARIA attributes where appropriate).

### 6.6. Ethical Adherence
1.  **Guideline Implementation**: All implemented ethical guidelines (disclaimers, moderation, crisis handling, professional redirection) must be consistently applied.
2.  **Transparency**: The chatbot should be transparent about its AI nature and its limitations.

## 7. Success Metrics

The success of the Mindful Companion chatbot will be measured by a combination of qualitative and quantitative metrics, including but not limited to:

### 7.1. User Satisfaction & Engagement
1.  **User Feedback**: Collection of qualitative feedback through surveys or in-app prompts (e.g., thumbs up/down on responses, open-ended comments). Target: Predominantly positive sentiment.
2.  **Session Duration**: Average length of user interaction sessions. Longer sessions may indicate higher engagement.
3.  **Conversation Depth**: Average number of turns per conversation. Deeper conversations can indicate user trust and perceived utility.
4.  **Retention Rate**: Percentage of users returning for multiple sessions over a defined period (if user identification across sessions is implemented and consented to).

### 7.2. Response Quality & Accuracy
1.  **Factual Accuracy**: Percentage of responses accurately reflecting information from the knowledge base, assessed through manual review or automated checks (e.g., RAGAS metrics like faithfulness).
2.  **Empathy Score**: Qualitative assessment of response empathy by human reviewers or potentially an ML model trained for empathy detection.
3.  **Helpfulness Score**: User ratings on whether the bot's responses were helpful to their query/situation.
4.  **Knowledge Base Grounding**: Percentage of responses successfully grounded in the curated knowledge base, minimizing ungrounded or hallucinatory statements.

### 7.3. Crisis Detection & Ethical Adherence
1.  **Crisis Detection Rate**: Accuracy in identifying crisis situations (true positives) and minimizing false negatives, evaluated against a benchmark dataset or through simulated interactions.
2.  **Appropriate Crisis Resource Provision**: Percentage of detected crises where correct and relevant emergency resources are provided.
3.  **Content Moderation Effectiveness**: Effectiveness of the OpenAI Moderation API in filtering harmful content, measured by the low incidence of inappropriate content passing through (both user input and bot generation).
4.  **Adherence to Ethical Guidelines**: Low incidence of responses that give medical advice, fail to provide disclaimers, or violate other established ethical protocols. Monitored through logging and audits.
5.  **Redirection Success**: Tracking instances where users are appropriately redirected to professional help and, if possible, feedback on whether this redirection was perceived as helpful.

### 7.4. System Performance & Reliability
1.  **API Uptime**: Percentage of time the chatbot service is available and responsive.
2.  **Response Latency**: As defined in NFR 6.1.3 (e.g., P95 response time <3-5 seconds).
3.  **Error Rates**: Low rate of system errors or exceptions during user interactions.

### 7.5. Task Completion (If Applicable for Specific Features)
1.  If specific guided interactions or tasks are introduced (e.g., completing a CBT exercise), the completion rate of these tasks by users. 