# Mental Health Chatbot - Mindful Companion 🧠

A comprehensive mental health support chatbot built with **Retrieval-Augmented Generation (RAG)** to provide factually accurate, empathetic, and ethically safe responses. The system integrates advanced AI technologies with mental health best practices to offer personalized support while maintaining strict ethical guidelines.

## 🌟 Key Features

### 🔍 **Advanced RAG Architecture**
- **Vector Database Integration**: Uses FAISS for efficient semantic search and document retrieval
- **Intelligent Chunking**: Employs `RecursiveCharacterTextSplitter` with optimized parameters (chunk_size: 1000, overlap: 200)
- **Context-Aware Responses**: Generates responses grounded in curated mental health resources

### 🛡️ **Crisis Detection & Safety**
- **Multi-Level Crisis Detection**: Identifies severe and moderate crisis keywords with context awareness
- **Immediate Crisis Response**: Provides instant access to crisis hotlines and emergency resources
- **Safety Verification**: Follows up to ensure users seek appropriate help
- **Real-time Crisis Alerts**: Visual alerts in the web interface for immediate attention

### 🧭 **Ethical AI Guidelines**
- **Medical Disclaimer System**: Clear boundaries preventing medical diagnoses or prescriptions
- **Content Moderation**: OpenAI Moderation API integration for harmful content filtering
- **Professional Care Redirection**: Encourages seeking licensed mental health professionals
- **Privacy-First Design**: No permanent storage of sensitive conversations

### 💬 **Intelligent Memory Management**
- **Conversation Continuity**: Maintains context across interactions using LangChain's ChatMessageHistory
- **User Detail Extraction**: Automatically identifies and remembers user preferences, triggers, and concerns
- **Personalized Responses**: Tailors advice based on previously shared information
- **Session Management**: Handles multiple concurrent conversations

### 🎨 **Modern Web Interface**
- **Real-time Communication**: WebSocket-based chat with typing indicators
- **Responsive Design**: Works seamlessly across desktop and mobile devices
- **Dark/Light Theme**: Adaptive theming with system preference detection
- **Conversation Management**: Create, load, and manage multiple chat sessions

## 🏗️ Technical Architecture

### **Backend Components**
```
src/
├── chatbot.py              # Main integration orchestrator
├── knowledge_base.py       # RAG implementation with FAISS
├── response_generator.py   # GPT-4 powered response generation
├── crisis_detector.py      # Multi-level crisis identification
├── ethical_guidelines.py   # Medical advice & content moderation
├── memory_manager.py       # LangChain-based conversation memory
└── memory_store.py         # In-memory conversation storage
```

### **Frontend Stack**
- **FastAPI**: Async web framework with WebSocket support
- **Vanilla JavaScript**: Lightweight, responsive client-side application
- **CSS3**: Modern styling with CSS custom properties and animations
- **Real-time Updates**: Live conversation synchronization

### **AI/ML Integration**
- **Language Model**: GPT-4 with temperature=0.3 for balanced creativity and accuracy
- **Embeddings**: OpenAI's text-embedding-ada-002 for semantic search
- **Vector Store**: FAISS for efficient similarity search
- **Content Filtering**: OpenAI Moderation API for safety

## 📚 Knowledge Base Structure

```
knowledge_base/
├── faqs/
│   └── mental_health_faqs.md      # Anxiety, depression, stress management
├── cbt_strategies/
│   └── cbt_exercises.md           # CBT techniques and coping strategies
└── crisis_resources/
    └── crisis_intervention.md     # Crisis hotlines and de-escalation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API key
- 8GB+ RAM (for local vector operations)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Akashpaul2030/Mental_Therapist.git
   cd Mental_Therapist
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create `.env` file:
   ```env
   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Model Settings
   EMBEDDING_MODEL=text-embedding-ada-002
   LLM_MODEL=gpt-4
   TEMPERATURE=0.3
   
   # Vector Database
   VECTOR_DB_PATH=knowledge_base/vector_store
   
   # Crisis Detection
   CRISIS_KEYWORDS=suicide,self-harm,kill myself,end my life,can't go on
   
   # Logging
   LOG_LEVEL=INFO
   LOG_FILE=logs/chatbot.log
   ```

5. **Initialize the knowledge base**
   ```bash
   python -c "from src.knowledge_base import initialize_knowledge_base; initialize_knowledge_base()"
   ```

6. **Start the application**
   ```bash
   python main.py
   ```

7. **Access the interface**
   Open `http://localhost:8000` in your browser

## 🧪 Testing

The project includes comprehensive test suites:

```bash
# Test individual components
python tests/test_knowledge_base.py
python tests/test_response_generator.py
python tests/test_crisis_detector.py
python tests/test_ethical_guidelines.py

# Integration testing
python tests/test_integration.py
```

## 📡 API Endpoints

### WebSocket
- `ws://localhost:8000/ws/{client_id}` - Real-time chat communication

### REST API
- `GET /` - Serve main application
- `POST /api/conversations/new` - Create new conversation
- `GET /api/conversations` - List all conversations  
- `GET /api/conversations/{user_id}` - Get specific conversation
- `POST /clear_history/{client_id}` - Clear conversation history
- `GET /health` - Health check endpoint

## 🔧 Configuration Options

### **Model Configuration**
```python
# Customize in .env
LLM_MODEL=gpt-4  # or gpt-3.5-turbo
TEMPERATURE=0.3  # 0.0-1.0 (creativity vs consistency)
```

### **Crisis Detection Tuning**
```python
# Add custom crisis keywords
CRISIS_KEYWORDS=suicide,self-harm,kill myself,end my life,hopeless
```

### **Memory Settings**
```python
# Adjust conversation history length
MAX_HISTORY_LENGTH=10  # Number of message pairs to retain
```

## 🛡️ Safety & Ethics

### **Built-in Safeguards**
- ✅ **No Medical Diagnoses**: Redirects medical questions to healthcare providers
- ✅ **Crisis Intervention**: Immediate crisis resource provision
- ✅ **Content Moderation**: Filters harmful or inappropriate content
- ✅ **Professional Boundaries**: Clear AI limitations disclosure
- ✅ **Privacy Protection**: No permanent conversation storage


---

**Built with ❤️ for mental health awareness and AI-powered support systems.**
