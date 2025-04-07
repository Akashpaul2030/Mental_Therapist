"""
Response Generation Module

This module handles the generation of empathetic and factually accurate responses
based on retrieved knowledge base documents using the RAG approach.

It includes:
- Response generation using LangChain and OpenAI models
- Empathetic tone guidelines
- Fallback responses for when no relevant information is found
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import Document

# Load environment variables
load_dotenv()

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.getenv('LOG_FILE', os.path.join('logs', 'chatbot.log'))
)
logger = logging.getLogger(__name__)

# Empathetic response templates
EMPATHETIC_PHRASES = [
    "I understand that you're feeling {emotion}. That sounds really challenging.",
    "Thank you for sharing this with me. It's completely okay to feel {emotion}.",
    "I appreciate you opening up about this. Many people experience {emotion} in similar situations.",
    "It sounds like you're going through a difficult time with {situation}.",
    "I'm here to listen and support you through these {emotion} feelings."
]

# Fallback response when no relevant information is found
FALLBACK_RESPONSE = """
I'm sorry you're going through this. While I don't have specific advice for your situation, 
I strongly recommend reaching out to a licensed mental health professional who can provide 
personalized support. Would you like me to provide information on how to find mental health resources?
"""

# Disclaimer to include at the start of conversations
DISCLAIMER = """
Note: I'm an AI here to provide general support, not a substitute for professional care. 
For urgent issues, please contact a licensed therapist or crisis hotline.
"""

# Medical advice redirection
MEDICAL_ADVICE_REDIRECTION = """
I'm not qualified to provide medical advice or diagnose conditions. For medical concerns, 
please consult with a healthcare provider who can give you proper evaluation and treatment options.
"""

class ResponseGenerator:
    """Class to generate empathetic and factually accurate responses."""
    
    def __init__(self):
        """Initialize the response generator."""
        self.llm = ChatOpenAI(
            model=os.getenv('LLM_MODEL', 'gpt-4'),
            temperature=float(os.getenv('TEMPERATURE', 0.3))
        )
        
        # Create the response generation prompt template
        self.response_template = PromptTemplate(
            input_variables=["context", "query", "tone_guidelines"],
            template="""
            You are a mental health support chatbot designed to provide empathetic and factually accurate responses.
            
            CONTEXT INFORMATION:
            {context}
            
            EMPATHETIC TONE GUIDELINES:
            {tone_guidelines}
            
            USER QUERY:
            {query}
            
            Please provide a helpful, empathetic response based on the context information provided.
            Always prioritize user safety and well-being in your response.
            Do not diagnose conditions or provide medical advice.
            If the context doesn't contain relevant information, acknowledge this and suggest seeking professional help.
            
            RESPONSE:
            """
        )
        
        # Create the LLM chain
        self.response_chain = LLMChain(
            llm=self.llm,
            prompt=self.response_template
        )
        
    def _format_context(self, documents: List[Document]) -> str:
        """
        Format retrieved documents into context for the response generation.
        
        Args:
            documents: List of retrieved documents
            
        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant information found."
        
        context_parts = []
        for i, doc in enumerate(documents):
            source = doc.metadata.get('source', 'Unknown source')
            content = doc.page_content
            context_parts.append(f"Document {i+1} (from {source}):\n{content}\n")
        
        return "\n".join(context_parts)
    
    def _get_empathetic_tone_guidelines(self) -> str:
        """
        Get empathetic tone guidelines for response generation.
        
        Returns:
            Empathetic tone guidelines string
        """
        guidelines = [
            "Use a warm, supportive tone throughout your response.",
            "Validate the user's feelings and experiences.",
            "Avoid judgmental language or minimizing their concerns.",
            "Use phrases like 'I understand', 'That sounds difficult', or 'It's okay to feel this way'.",
            "Balance empathy with factual information from the provided context.",
            "When suggesting strategies, present them as options rather than commands.",
            "Acknowledge the limits of your support and encourage professional help when appropriate."
        ]
        
        return "\n".join(f"- {guideline}" for guideline in guidelines)
    
    def _detect_medical_advice_request(self, query: str) -> bool:
        """
        Detect if the query is asking for medical advice.
        
        Args:
            query: User query
            
        Returns:
            True if the query is asking for medical advice, False otherwise
        """
        medical_keywords = [
            "diagnose", "diagnosis", "medication", "prescribe", "treatment",
            "cure", "heal", "drug", "dosage", "side effect", "symptom"
        ]
        
        query_lower = query.lower()
        for keyword in medical_keywords:
            if keyword in query_lower:
                return True
        
        return False
    
    def generate_response(self, query: str, documents: List[Document]) -> str:
        """
        Generate an empathetic and factually accurate response based on retrieved documents.
        
        Args:
            query: User query
            documents: List of retrieved documents
            
        Returns:
            Generated response
        """
        logger.info(f"Generating response for query: {query}")
        
        # Check if the query is asking for medical advice
        if self._detect_medical_advice_request(query):
            logger.info("Medical advice request detected")
            return MEDICAL_ADVICE_REDIRECTION
        
        # Format the context from retrieved documents
        context = self._format_context(documents)
        
        # Get empathetic tone guidelines
        tone_guidelines = self._get_empathetic_tone_guidelines()
        
        try:
            # Generate response
            if not documents:
                logger.info("No relevant documents found, using fallback response")
                return FALLBACK_RESPONSE
            
            response = self.response_chain.run(
                context=context,
                query=query,
                tone_guidelines=tone_guidelines
            )
            
            logger.info("Response generated successfully")
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return FALLBACK_RESPONSE
    
    def get_disclaimer(self) -> str:
        """
        Get the disclaimer to include at the start of conversations.
        
        Returns:
            Disclaimer string
        """
        return DISCLAIMER