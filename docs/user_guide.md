# Mental Health Chatbot - User Guide

## Introduction

The Mental Health Chatbot is designed to provide factually accurate, empathetic, and ethically safe responses to users seeking mental health support. It uses a Retrieval-Augmented Generation (RAG) approach to retrieve information from a curated mental health knowledge base and respond in a supportive tone while adhering to crisis protocols and privacy standards.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- OpenAI API key
- Required Python packages (listed in requirements.txt)

### Installation

1. Clone the repository or extract the provided files to your local machine.

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables by creating a `.env` file in the project root with the following content:
   ```
   # OpenAI API configuration
   OPENAI_API_KEY=your_openai_api_key_here

   # Vector database settings
   VECTOR_DB_PATH=knowledge_base/vector_store

   # Model settings
   EMBEDDING_MODEL=text-embedding-ada-002
   LLM_MODEL=gpt-4
   TEMPERATURE=0.3

   # Crisis detection settings
   CRISIS_KEYWORDS=suicide,self-harm,kill myself,end my life,can't go on

   # Logging settings
   LOG_LEVEL=INFO
   LOG_FILE=logs/chatbot.log
   ```

5. Create the logs directory:
   ```bash
   mkdir -p logs
   ```

### Running the Chatbot

To run the chatbot, use the provided `main.py` script:

```bash
python main.py
```

## Features

### Knowledge Base

The chatbot includes a comprehensive knowledge base with:

- Mental health FAQs covering anxiety, depression, stress management, and seeking help
- CBT exercises and coping strategies
- Crisis intervention resources

### Empathetic Responses

The chatbot is designed to provide empathetic responses that:

- Validate the user's feelings and experiences
- Avoid judgmental language
- Present strategies as options rather than commands
- Balance empathy with factual information

### Crisis Detection

The chatbot includes a crisis detection system that:

- Identifies crisis keywords like "suicide," "self-harm," etc.
- Provides immediate responses with crisis hotline information
- Follows up to ensure the user has sought help

### Ethical Guidelines

The chatbot follows strict ethical guidelines:

- Includes disclaimers about its limitations
- Redirects medical advice requests to healthcare professionals
- Filters harmful content using OpenAI's Moderation API

## Example Interactions

### General Mental Health Question

**User**: What are some ways to manage anxiety?

**Chatbot**: *[Provides information about anxiety management techniques from the knowledge base with an empathetic tone]*

### Crisis Situation

**User**: I can't take it anymore, I want to end my life.

**Chatbot**: *[Provides crisis response with hotline information and urges immediate professional help]*

### Medical Advice Request

**User**: Do I have depression based on these symptoms?

**Chatbot**: *[Explains it cannot provide medical diagnoses and encourages consulting a healthcare professional]*

## Customizing the Chatbot

### Adding to the Knowledge Base

To add new information to the knowledge base:

1. Create markdown files in the appropriate subdirectory:
   - `knowledge_base/faqs/` for general mental health information
   - `knowledge_base/cbt_strategies/` for CBT exercises and coping strategies
   - `knowledge_base/crisis_resources/` for crisis intervention resources

2. Run the knowledge base setup script to update the vector database:
   ```bash
   python -c "from src.knowledge_base import initialize_knowledge_base; initialize_knowledge_base()"
   ```

### Modifying Crisis Keywords

To modify the crisis keywords, update the `CRISIS_KEYWORDS` variable in your `.env` file:

```
CRISIS_KEYWORDS=keyword1,keyword2,keyword3
```

### Changing the Language Model

To use a different language model, update the `LLM_MODEL` variable in your `.env` file:

```
LLM_MODEL=gpt-3.5-turbo
```

## Troubleshooting

### API Key Issues

If you encounter API key errors:
- Verify your OpenAI API key is correct
- Check that the API key has the necessary permissions
- Ensure the API key is properly set in the `.env` file

### Vector Database Errors

If the chatbot fails to retrieve information:
- Check that the vector database has been properly initialized
- Verify the `VECTOR_DB_PATH` is correct in the `.env` file
- Run the knowledge base setup script to rebuild the vector database

### General Issues

For general issues:
- Check the log file specified in the `.env` file
- Verify all required packages are installed
- Ensure Python version is 3.10 or higher

## Privacy and Data Handling

The chatbot is designed with privacy in mind:
- No user data is stored permanently
- Conversations are not saved beyond the current session
- No personally identifiable information is collected

## Support and Feedback

For support or to provide feedback, please contact [support email or contact information].

## Disclaimer

This chatbot is not a substitute for professional mental health care. It is designed to provide general support and information only. For urgent issues, please contact a licensed therapist, counselor, or crisis hotline.
