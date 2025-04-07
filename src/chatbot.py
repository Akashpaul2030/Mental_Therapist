"""
Main Chatbot Integration Module

This module integrates all components of the mental health chatbot:
- Knowledge base integration
- Response generation
- Crisis detection
- Ethical guidelines

It provides a unified interface for interacting with the chatbot.
"""

import os
import logging
from typing import Dict, Any, Tuple
from dotenv import load_dotenv

# Import component modules
from src.knowledge_base import initialize_knowledge_base
from src.response_generator import ResponseGenerator
from src.crisis_detector import CrisisDetector
from src.ethical_guidelines import EthicalGuidelines

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

class MentalHealthChatbot:
    """Main chatbot class that integrates all components."""
    
    def __init__(self):
        """Initialize the chatbot with all its components."""
        logger.info("Initializing Mental Health Chatbot")
        
        # Initialize components
        self.knowledge_base = initialize_knowledge_base()
        self.response_generator = ResponseGenerator()
        self.crisis_detector = CrisisDetector()
        self.ethics = EthicalGuidelines()
        
        # Conversation state
        self.conversation_started = False
    
    def start_conversation(self) -> str:
        """
        Start a new conversation with the chatbot.
        
        Returns:
            Initial greeting with disclaimer
        """
        self.conversation_started = True
        return self.ethics.get_initial_disclaimer()
    
    def process_message(self, message: str) -> str:
        """
        Process a user message and generate a response.
        
        Args:
            message: User message
            
        Returns:
            Chatbot response
        """
        logger.info(f"Processing message: {message}")
        
        # Start conversation if not started
        if not self.conversation_started:
            self.conversation_started = True
        
        # Check for crisis keywords
        if self.crisis_detector.detect_crisis(message):
            logger.warning("Crisis detected in user message")
            return self.crisis_detector.get_crisis_response()
        
        # Check if user is in crisis mode and needs to verify safety
        if self.crisis_detector.in_crisis_mode:
            safety_verified = self.crisis_detector.check_safety_verification(message)
            if not safety_verified:
                return self.crisis_detector.get_safety_verification_message()
        
        # Check for medical advice request
        if self.ethics.check_medical_advice_request(message):
            logger.info("Medical advice request detected")
            return self.ethics.get_medical_advice_redirection()
        
        # Moderate content
        is_flagged, moderation_result = self.ethics.moderate_content(message)
        if is_flagged:
            logger.warning("Content flagged by moderation API")
            return self.ethics.get_moderation_response(moderation_result)
        
        try:
            # Retrieve relevant documents from knowledge base
            docs = self.knowledge_base.retrieve(message, k=3)
            
            # Generate response
            response = self.response_generator.generate_response(message, docs)
            
            # Add session disclaimer if not a special response
            if not self.crisis_detector.in_crisis_mode:
                response = f"{response}\n\n{self.ethics.get_session_disclaimer()}"
            
            return response
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "I'm sorry, I encountered an error while processing your message. Please try again or contact support if the issue persists."