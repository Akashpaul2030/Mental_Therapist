"""
Memory Manager Module for Mental Health Chatbot

This module handles conversation memory using langgraph's InMemoryStore.
It tracks user details and conversation history to provide context for responses.
"""

import logging
import os
from typing import Dict, List, Any, Optional
from langgraph.store.memory import InMemoryStore
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.getenv('LOG_FILE', 'chatbot.log')
)
logger = logging.getLogger(__name__)

class MentalHealthMemoryManager:
    """Class to manage mental health chatbot memory."""
    
    def __init__(self, max_history_length: int = 10):
        """Initialize the memory manager."""
        self.store = {}  # Simple dictionary instead of InMemoryStore
        self.max_history_length = max_history_length
        self.user_detail_keys = ['name', 'triggers', 'situations', 'concerns']
        logger.info("Initialized mental health memory manager")
    
    def get_user_entry(self, user_id: str) -> Dict:
        """
        Get or create a user entry in the memory store.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            User memory entry dictionary
        """
        key = f"user_{user_id}"
        if key not in self.store:
            # Initialize a new user entry
            self.store[key] = {
                "conversation": [],
                "details": {k: None for k in self.user_detail_keys}
            }
            logger.info(f"Created new memory entry for user {user_id}")
        
        return self.store[key]
    
    def add_user_message(self, user_id: str, message: str) -> None:
        """
        Add a user message to the conversation history.
        
        Args:
            user_id: Unique identifier for the user
            message: User's message
        """
        entry = self.get_user_entry(user_id)
        
        # Add user message to conversation
        entry["conversation"].append({"role": "user", "content": message})
        
        # Trim history if needed
        if len(entry["conversation"]) > self.max_history_length * 2:
            entry["conversation"] = entry["conversation"][-(self.max_history_length * 2):]
        
        logger.info(f"Added user message for user {user_id}")
    
    def add_bot_message(self, user_id: str, message: str) -> None:
        """
        Add a bot message to the conversation history.
        
        Args:
            user_id: Unique identifier for the user
            message: Bot's message
        """
        entry = self.get_user_entry(user_id)
        
        # Add bot message to conversation
        entry["conversation"].append({"role": "assistant", "content": message})
        
        logger.info(f"Added bot message for user {user_id}")
    
    def update_user_details(self, user_id: str, details: Dict) -> None:
        """
        Update user details in memory.
        
        Args:
            user_id: Unique identifier for the user
            details: Dictionary of user details to update
        """
        entry = self.get_user_entry(user_id)
        
        # Update only valid detail keys
        for k, v in details.items():
            if k in self.user_detail_keys and v:
                entry["details"][k] = v
        
        logger.info(f"Updated details for user {user_id}")
    
    def extract_details_from_message(self, message: str) -> Dict:
        """
        Extract potential user details from a message.
        
        Args:
            message: User message to analyze
            
        Returns:
            Dictionary of extracted details
        """
        details = {}
        
        # Simple name extraction (look for "my name is" or "I am")
        name_patterns = ["my name is ", "i'm ", "i am "]
        for pattern in name_patterns:
            if pattern in message.lower():
                # Extract the text after the pattern until the end of the sentence or message
                start = message.lower().find(pattern) + len(pattern)
                end = message.find(".", start)
                if end == -1:
                    end = len(message)
                potential_name = message[start:end].strip()
                # Extract just the first word as a name
                first_name = potential_name.split()[0] if potential_name.split() else ""
                if first_name and len(first_name) > 1:
                    details["name"] = first_name
                    break
        
        # Extract anxiety/stress triggers
        trigger_patterns = ["anxious about ", "anxiety when ", "stress about ", "stressed by "]
        for pattern in trigger_patterns:
            if pattern in message.lower():
                start = message.lower().find(pattern) + len(pattern)
                end = message.find(".", start)
                if end == -1:
                    end = len(message)
                trigger = message[start:end].strip()
                if trigger:
                    details["triggers"] = trigger
                    details["situations"] = trigger  # Duplicate for flexibility
                    break
        
        return details
    
    def get_conversation_history(self, user_id: str) -> List[Dict[str, str]]:
        """
        Get the conversation history for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            List of conversation messages
        """
        entry = self.get_user_entry(user_id)
        return entry["conversation"]
    
    def get_user_details(self, user_id: str) -> Dict:
        """
        Get the stored details for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary of user details
        """
        entry = self.get_user_entry(user_id)
        return entry["details"]
    
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
    
    def get_context_for_response(self, user_id: str) -> Dict:
        """
        Get the full context for response generation.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary with history and user details
        """
        details = self.get_user_details(user_id)
        history = self.get_formatted_history(user_id)
        
        # Create context string based on available details
        context_parts = []
        
        if details.get("name"):
            context_parts.append(f"User's name: {details['name']}")
        
        if details.get("triggers"):
            context_parts.append(f"Anxiety/stress triggers: {details['triggers']}")
        
        if details.get("situations"):
            context_parts.append(f"Difficult situations mentioned: {details['situations']}")
        
        if details.get("concerns"):
            context_parts.append(f"Specific concerns: {details['concerns']}")
        
        context = "\n".join(context_parts)
        
        return {
            "history": history,
            "user_details": context
        }
    
    def clear_history(self, user_id: str) -> None:
        """
        Clear the conversation history for a user.
        
        Args:
            user_id: Unique identifier for the user
        """
        entry = self.get_user_entry(user_id)
        
        # Clear conversation but keep user details
        entry["conversation"] = []
        
        logger.info(f"Cleared conversation history for user {user_id}")
    
    def clear_all(self, user_id: str) -> None:
        """
        Clear both conversation history and user details.
        
        Args:
            user_id: Unique identifier for the user
        """
        key = f"user_{user_id}"
        
        # Create a fresh entry
        self.store[key] = {
            "conversation": [],
            "details": {k: None for k in self.user_detail_keys}
        }
        
        logger.info(f"Cleared all data for user {user_id}")