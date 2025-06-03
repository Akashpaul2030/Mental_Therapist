"""
Main Chatbot Integration Module

This module integrates all components of the mental health chatbot:
- Knowledge base integration
- Response generation
- Crisis detection
- Ethical guidelines
- Conversation memory

It provides a unified interface for interacting with the chatbot.
"""

import os
import logging
import uuid
from typing import Dict, Any, Tuple, Optional
from dotenv import load_dotenv

# Import component modules
from src.knowledge_base import initialize_knowledge_base
from src.response_generator import ResponseGenerator
from src.crisis_detector import CrisisDetector
from src.ethical_guidelines import EthicalGuidelines
from src.memory_manager import MentalHealthMemoryManager
from src.utils.common_utils import get_greeting
from langchain_core.messages import HumanMessage, AIMessage

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
        logger.info("Initializing MentalHealthChatbot...")
        self.knowledge_base = initialize_knowledge_base()
        self.response_generator = ResponseGenerator(self.knowledge_base)
        self.crisis_detector = CrisisDetector()
        self.ethical_guidelines = EthicalGuidelines()
        # Initialize memory manager with max_token_limit
        self.memory = MentalHealthMemoryManager(max_token_limit=3000) 
        self.active_connections = {}
        self.user_safety_followup_timers = {}
        logger.info("MentalHealthChatbot initialized successfully.")
        
        # Conversation state
        self.conversation_started = False
        self.current_user_id = None
    
    def start_conversation(self, user_id: Optional[str] = None) -> str:
        """
        Start a new conversation with the chatbot.
        
        Args:
            user_id: Optional user identifier. If None, a new ID is generated.
            
        Returns:
            Initial greeting with disclaimer
        """
        # Generate a user ID if not provided
        if user_id is None:
            user_id = str(uuid.uuid4())
        
        logger.info(f"Starting conversation with user {user_id}")
        self.current_user_id = user_id
        self.conversation_started = True
        
        # Clear any existing conversation history
        self.memory.clear_history(user_id)
        
        initial_message = self.ethical_guidelines.get_initial_disclaimer()
        
        # Add bot message to conversation history
        self.memory.add_bot_message(user_id, initial_message)
        
        return initial_message
    
    def process_message(self, message: str, user_id: Optional[str] = None) -> str:
        """
        Process a user message and generate a response.
        
        Args:
            message: User message
            user_id: Optional user identifier. Uses current user ID if None.
            
        Returns:
            Chatbot response
        """
        logger.info(f"Processing message: {message}")
        
        # Use current user ID if not provided
        if user_id is None:
            if self.current_user_id is None:
                self.current_user_id = str(uuid.uuid4())
                logger.info(f"Created new user ID: {self.current_user_id}")
            user_id = self.current_user_id
        else:
            self.current_user_id = user_id
        
        # Start conversation if not started
        if not self.conversation_started:
            self.conversation_started = True
        
        # Extract user details from message
        details = self.memory.extract_details_from_message(message)
        if details:
            self.memory.update_user_details(user_id, details)
            logger.info(f"Extracted user details: {details}")
        
        # Add user message to conversation history
        self.memory.add_user_message(user_id, message)
        
        # Get conversation context for response generation
        context = self.memory.get_context_for_response(user_id)
        logger.info(f"Retrieved context with {len(context['history'].split(chr(10))) if context['history'] else 0} history lines")
        
        # Check for crisis keywords
        if self.crisis_detector.detect_crisis(message):
            logger.warning("Crisis detected in user message")
            response = self.crisis_detector.get_crisis_response()
            self.memory.add_bot_message(user_id, response)
            return response
        
        # Check if user is in crisis mode and needs to verify safety
        if self.crisis_detector.in_crisis_mode:
            safety_verified = self.crisis_detector.check_safety_verification(message)
            if not safety_verified:
                response = self.crisis_detector.get_safety_verification_message()
                self.memory.add_bot_message(user_id, response)
                return response
        
        # Check for medical advice request
        if self.ethical_guidelines.check_medical_advice_request(message):
            logger.info("Medical advice request detected")
            response = self.ethical_guidelines.get_medical_advice_redirection()
            self.memory.add_bot_message(user_id, response)
            return response
        
        # Moderate content
        is_flagged, moderation_result = self.ethical_guidelines.moderate_content(message)
        if is_flagged:
            logger.warning("Content flagged by moderation API")
            response = self.ethical_guidelines.get_moderation_response(moderation_result)
            self.memory.add_bot_message(user_id, response)
            return response
        
        try:
            # Retrieve relevant documents from knowledge base
            docs = self.knowledge_base.retrieve(message, k=3)
            
            # Generate response with conversation history and user details as additional context
            try:
                response = self.response_generator.generate_response(
                    message, 
                    docs, 
                    context["history"],
                    context["user_details"]
                )
            except TypeError:
                # Fallback if the response generator doesn't support user_details parameter
                logger.warning("Response generator doesn't support user_details, using fallback method")
                response = self.response_generator.generate_response(
                    message, 
                    docs, 
                    context["history"]
                )
            
            # Add session disclaimer if not a special response
            if not self.crisis_detector.in_crisis_mode:
                response = f"{response}\n\n{self.ethical_guidelines.get_session_disclaimer()}"
            
            # Add bot message to conversation history
            self.memory.add_bot_message(user_id, response)
            
            return response
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            error_msg = "I'm sorry, I encountered an error while processing your message. Please try again or contact support if the issue persists."
            self.memory.add_bot_message(user_id, error_msg)
            return error_msg
    
    def get_conversation_history(self, user_id: Optional[str] = None) -> str:
        """
        Get the conversation history for a user.
        
        Args:
            user_id: Optional user identifier. Uses current user ID if None.
            
        Returns:
            Formatted conversation history
        """
        if user_id is None:
            if self.current_user_id is None:
                return "No conversation history available."
            user_id = self.current_user_id
        
        return self.memory.get_formatted_history(user_id)
    
    def get_user_details(self, user_id: Optional[str] = None) -> Dict:
        """
        Get the stored details for a user.
        
        Args:
            user_id: Optional user identifier. Uses current user ID if None.
            
        Returns:
            Dictionary of user details
        """
        if user_id is None:
            if self.current_user_id is None:
                return {}
            user_id = self.current_user_id
        
        return self.memory.get_user_details(user_id)