"""
Memory Store Module

This module handles conversation memory storage using langgraph's InMemoryStore.
It allows the chatbot to maintain conversation context and history.
"""

import logging
import os
from typing import Dict, List, Any, Optional
from langgraph.store.memory import InMemoryStore
from dotenv import load_dotenv

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

class ConversationMemory:
    """Class to manage conversation memory storage."""
    
    def __init__(self, max_history_length: int = 10):
        """
        Initialize the conversation memory.
        
        Args:
            max_history_length: Maximum number of conversation turns to store
        """
        # Create a singleton memory store (shared across all instances)
        self.memory_store = InMemoryStore()
        self.max_history_length = max_history_length
        logger.info("Initialized conversation memory store")
    
    def add_user_message(self, user_id: str, message: str) -> None:
        """
        Add a user message to the conversation history.
        
        Args:
            user_id: Unique identifier for the user
            message: User's message
        """
        try:
            # Get existing conversation history or create new one
            key = f"conversation_{user_id}"
            conversation = self.get_conversation_history(user_id)
            
            # Add user message to history
            conversation.append({"role": "user", "content": message})
            
            # Trim history if it exceeds max length
            if len(conversation) > self.max_history_length * 2:  # *2 because we count pairs of messages
                conversation = conversation[-(self.max_history_length * 2):]
            
            # Store updated conversation
            self.memory_store.set(key, conversation)
            logger.info(f"Added user message for user {user_id}")
        except Exception as e:
            logger.error(f"Error adding user message: {e}")
    
    def add_bot_message(self, user_id: str, message: str) -> None:
        """
        Add a bot message to the conversation history.
        
        Args:
            user_id: Unique identifier for the user
            message: Bot's message
        """
        try:
            # Get existing conversation history or create new one
            key = f"conversation_{user_id}"
            conversation = self.get_conversation_history(user_id)
            
            # Add bot message to history
            conversation.append({"role": "assistant", "content": message})
            
            # Store updated conversation
            self.memory_store.set(key, conversation)
            logger.info(f"Added bot message for user {user_id}")
        except Exception as e:
            logger.error(f"Error adding bot message: {e}")
    
    def get_conversation_history(self, user_id: str) -> List[Dict[str, str]]:
        """
        Get the conversation history for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            List of conversation messages
        """
        try:
            # Create a consistent key for this user
            key = f"conversation_{user_id}"
            
            # Try to get conversation history
            conversation = self.memory_store.get(key)
            if conversation is None:
                # If no history exists, initialize empty list
                conversation = []
                self.memory_store.set(key, conversation)
                logger.info(f"Created new conversation history for user {user_id}")
            else:
                logger.info(f"Retrieved existing conversation history for user {user_id} with {len(conversation)} messages")
                
            return conversation
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {e}")
            return []
    
    def get_formatted_history(self, user_id: str) -> str:
        """
        Get the conversation history formatted as a string.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Formatted conversation history
        """
        conversation = self.get_conversation_history(user_id)
        if not conversation:
            return ""
            
        formatted_history = []
        
        for msg in conversation:
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted_history.append(f"{role}: {msg['content']}")
        
        return "\n\n".join(formatted_history)
    
    def clear_history(self, user_id: str) -> None:
        """
        Clear the conversation history for a user.
        
        Args:
            user_id: Unique identifier for the user
        """
        try:
            key = f"conversation_{user_id}"
            self.memory_store.set(key, [])
            logger.info(f"Cleared conversation history for user {user_id}")
        except Exception as e:
            logger.error(f"Error clearing conversation history: {e}")