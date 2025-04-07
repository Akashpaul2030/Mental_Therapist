# Mental Health Chatbot - System Documentation

## System Architecture

The Mental Health Chatbot is built using a Retrieval-Augmented Generation (RAG) approach to provide factually accurate, empathetic, and ethically safe responses. The system architecture consists of several modular components that work together:

### 1. Knowledge Base Integration

The knowledge base component is responsible for storing and retrieving mental health information:

- **Document Storage**: Mental health resources are organized in three categories:
  - Mental health FAQs
  - CBT exercises and coping strategies
  - Crisis intervention resources

- **Vector Database**: Uses FAISS (Facebook AI Similarity Search) to store document embeddings for efficient semantic retrieval.

- **Document Processing**: Text is split into chunks and embedded using OpenAI's text-embedding-ada-002 model.

- **Retrieval Functionality**: Retrieves the most relevant documents based on semantic similarity to user queries.

### 2. Response Generation System

The response generation component creates empathetic and helpful responses:

- **LangChain Integration**: Uses LangChain to orchestrate the RAG pipeline.

- **Context-Aware Responses**: Generates responses grounded in retrieved documents to minimize hallucinations.

- **Empathetic Tone Guidelines**: Ensures responses adopt a supportive and non-judgmental tone.

- **Fallback Responses**: Provides appropriate responses when no relevant information is found.

### 3. Crisis Detection Protocol

The crisis detection component identifies and responds to potential crisis situations:

- **Keyword Detection**: Identifies crisis keywords like "suicide," "self-harm," etc.

- **Crisis Response Templates**: Provides immediate responses with crisis hotline information.

- **Safety Verification**: Follows up to ensure the user has sought help and is safe.

### 4. Ethical Guidelines

The ethical guidelines component ensures responsible and safe interactions:

- **Disclaimer System**: Clearly communicates the chatbot's limitations at the beginning of conversations.

- **Medical Advice Redirection**: Identifies when users are seeking diagnoses or treatment recommendations.

- **Content Moderation**: Uses OpenAI's Moderation API to filter harmful content.

### 5. Main Chatbot Integration

The main chatbot module integrates all components:

- **Unified Interface**: Provides a single entry point for processing user messages.

- **Message Flow**: 
  1. Checks for crisis keywords
  2. Verifies safety if in crisis mode
  3. Checks for medical advice requests
  4. Moderates content
  5. Retrieves relevant documents
  6. Generates appropriate responses
  7. Adds disclaimers as needed

## Component Interactions

```
User Message
    │
    ▼
┌─────────────────┐
│ Main Chatbot    │
└─────────────────┘
    │
    ├─────────────┬─────────────┬─────────────┐
    │             │             │             │
    ▼             ▼             ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Crisis      │ │ Ethical     │ │ Knowledge   │ │ Response    │
│ Detection   │ │ Guidelines  │ │ Base        │ │ Generation  │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
    │             │                   │             │
    └─────────────┴───────────────────┴─────────────┘
                              │
                              ▼
                      Chatbot Response
```

## API Usage

### OpenAI API

The chatbot uses several OpenAI APIs:

1. **Text Embedding API**
   - Model: text-embedding-ada-002
   - Purpose: Creating vector embeddings for knowledge base documents
   - Usage: Called during knowledge base setup and for embedding user queries

2. **Chat Completion API**
   - Model: gpt-4
   - Temperature: 0.3 (configurable via environment variables)
   - Purpose: Generating empathetic responses based on retrieved context
   - Usage: Called for each user message that passes safety checks

3. **Moderation API**
   - Purpose: Filtering harmful or inappropriate content
   - Usage: Called for each user message before processing

### Environment Variables

The chatbot uses the following environment variables:

```
# OpenAI API configuration
OPENAI_API_KEY=your_openai_api_key_here

# Vector database settings
VECTOR_DB_PATH=/home/ubuntu/mental_health_chatbot/knowledge_base/vector_store

# Model settings
EMBEDDING_MODEL=text-embedding-ada-002
LLM_MODEL=gpt-4
TEMPERATURE=0.3

# Crisis detection settings
CRISIS_KEYWORDS=suicide,self-harm,kill myself,end my life,can't go on

# Logging settings
LOG_LEVEL=INFO
LOG_FILE=/home/ubuntu/mental_health_chatbot/logs/chatbot.log
```

## Data Flow

1. **User Input**: The user sends a message to the chatbot.

2. **Crisis Detection**: The message is checked for crisis keywords.
   - If crisis keywords are detected, a crisis response is returned.
   - If the user is in crisis mode, safety verification is checked.

3. **Ethical Checks**: The message is checked for medical advice requests and moderated for harmful content.
   - If medical advice is requested, a redirection message is returned.
   - If content is flagged by moderation, an appropriate response is returned.

4. **Knowledge Retrieval**: The message is embedded and used to retrieve relevant documents from the knowledge base.

5. **Response Generation**: The retrieved documents are used as context to generate an empathetic and helpful response.

6. **Response Delivery**: The final response, with appropriate disclaimers, is returned to the user.

## Testing Framework

The chatbot includes comprehensive testing for all components:

1. **Component Tests**:
   - Knowledge base retrieval testing
   - Response generation testing
   - Crisis detection testing
   - Ethical guidelines testing

2. **Integration Testing**:
   - Tests all components working together
   - Simulates various user scenarios:
     - General mental health questions
     - Medical advice requests
     - Crisis situations
     - CBT technique requests
     - Sleep issues

## Deployment Considerations

When deploying the chatbot to production:

1. **API Key Security**: Ensure OpenAI API keys are securely stored and not exposed.

2. **Data Privacy**: Implement proper data handling practices to comply with HIPAA/GDPR.

3. **Scaling**: Consider implementing a queue system for handling multiple concurrent users.

4. **Monitoring**: Set up logging and monitoring to track usage and detect issues.

5. **Regular Updates**: Keep the knowledge base updated with the latest mental health information.

6. **User Feedback**: Implement a mechanism to collect and incorporate user feedback.

## Limitations and Future Improvements

1. **Personalization**: Add user profiles to provide more personalized responses.

2. **Multi-language Support**: Extend the chatbot to support multiple languages.

3. **Voice Interface**: Add speech-to-text and text-to-speech capabilities.

4. **Expanded Knowledge Base**: Continuously add more mental health resources.

5. **Improved Crisis Detection**: Enhance the crisis detection algorithm with machine learning.

6. **Integration with Professional Services**: Add the ability to connect users with licensed therapists.
