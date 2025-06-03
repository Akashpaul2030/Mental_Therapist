"""
Memory Manager Module for Mental Health Chatbot

This module handles conversation memory using LangChain's ChatMessageHistory.
It tracks user details and conversation history to provide context for responses.
"""

import logging
import os
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv
# from langchain.memory import ChatMessageHistory # Deprecated
from langchain_community.chat_message_histories import ChatMessageHistory # Corrected import
from langchain.memory import ConversationBufferMemory # This one seems fine for now, or evaluate if needed
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
import json
import datetime
from collections import defaultdict
# from langchain_core.chat_history import BaseChatMessageHistory # Duplicate if ChatMessageHistory is used
from src.memory_store import ConversationMemory # Removed InMemoryStore from import

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
    """Class to manage mental health chatbot memory using LangChain's chat history."""
    
    def __init__(self, max_token_limit=3000):
        """
        Initializes the MentalHealthMemoryManager.
        Conversations are stored in memory only and not persisted to disk.

        Args:
            max_token_limit (int): The maximum number of tokens to retain in the history.
        """
        self.conversations: Dict[str, ConversationMemory] = defaultdict(ConversationMemory)
        self.user_details: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.max_token_limit = max_token_limit
        logger.info("MentalHealthMemoryManager initialized for in-memory session storage.")

    def get_history(self, user_id: str) -> ConversationMemory:
        return self.conversations[user_id]

    def add_user_message(self, user_id: str, message_content: str):
        history = self.get_history(user_id)
        history.add_user_message(user_id, message_content)
        self._trim_history(user_id)

    def add_bot_message(self, user_id: str, message_content: str):
        history = self.get_history(user_id)
        history.add_bot_message(user_id, message_content)
        self._trim_history(user_id)

    def _trim_history(self, user_id: str):
        history: ConversationMemory = self.get_history(user_id) # history is src.memory_store.ConversationMemory
        
        # Get messages from ConversationMemory's store for this user
        if user_id not in history.store:
            return

        message_dicts = history.store[user_id] # Direct access to the list of message dicts
        
        # Calculate current token count from message_dicts
        # Assuming msg is a dict like {'role': 'user', 'content': '...'}
        current_token_count = sum(len(str(msg.get('content', '')).split()) for msg in message_dicts)

        while current_token_count > self.max_token_limit and message_dicts:
            removed_message_dict = message_dicts.pop(0) # Remove from the beginning (oldest)
            current_token_count -= len(str(removed_message_dict.get('content', '')).split())
            logger.debug(f"Trimmed message dict for user {user_id} by MHM to manage token limit.")
        
        # The list message_dicts is a direct reference to history.store[user_id], so modifications are reflected.
        # No need for history.messages = messages

    def update_user_details(self, user_id: str, details: Dict[str, Any]):
        self.user_details[user_id].update(details)
        logger.info(f"Updated user details for {user_id}: {details}")

    def get_user_details(self, user_id: str) -> Dict:
        """
        Get the stored details for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary of user details (never None)
        """
        details = self.user_details.get(user_id, {})
        if details is None: # This check is technically redundant now with defaultdict(dict) and .get(user_id, {}), but harmless
            return {}
        return details

    def get_all_conversations(self) -> Dict[str, Dict]:
        """
        Get all conversations with basic metadata.
        
        Returns:
            Dictionary mapping user_id to conversation metadata
        """
        result = {}
        
        # Corrected: Iterate through self.conversations which stores ConversationMemory instances
        for user_id, conv_memory_instance in self.conversations.items(): 
            # Get messages from the ConversationMemory instance for this user_id
            message_list = conv_memory_instance.get_conversation_history(user_id)

            if not message_list:
                # For empty conversations (newly created), still include them
                result[user_id] = {
                    'title': "New Conversation",
                    'message_count': 0,
                    'last_updated': datetime.datetime.now().isoformat()
                }
                continue
            
            # Get first user message for title (skip bot messages)
            first_user_message = None
            # message_list is already a list of dicts like {"role": ..., "content": ...}
            for msg_dict in message_list:
                if msg_dict.get('role') == 'user': # Check role from dict
                    first_user_message = msg_dict.get('content')
                    break
            
            # Create title from first user message
            title = "New Conversation"
            if first_user_message:
                words = first_user_message.split()
                if len(words) > 3:
                    title = " ".join(words[:3]) + "..."
                else:
                    title = first_user_message
            
            # Count messages
            message_count = len(message_list)
            
            # Get timestamp (use current time as approximation)
            timestamp = datetime.datetime.now().isoformat()
            
            result[user_id] = {
                'title': title,
                'message_count': message_count,
                'last_updated': timestamp
            }
        
        return result

    def get_conversation_messages(self, user_id: str) -> List[Dict[str, Any]]:
        history: ConversationMemory = self.get_history(user_id) # history is src.memory_store.ConversationMemory
        message_dicts = history.get_conversation_history(user_id)
        # The message_dicts are already in the desired format List[{"role": ..., "content": ...}]
        return message_dicts

    def clear_history(self, user_id: str):
        if user_id in self.conversations:
            # self.conversations[user_id].clear() # Old call for Langchain
            self.conversations[user_id].clear_history(user_id) # Correct call for src.memory_store.ConversationMemory
            logger.info(f"Cleared conversation history for user {user_id}.")
        if user_id in self.user_details:
            del self.user_details[user_id]
            logger.info(f"Cleared user details for {user_id}.")

    def get_formatted_history(self, user_id: str) -> str:
        """
        Get the conversation history formatted as a string.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Formatted conversation history
        """
        if user_id not in self.conversations:
            return ""
        
        history: ConversationMemory = self.conversations[user_id] # history is src.memory_store.ConversationMemory
        message_dicts = history.get_conversation_history(user_id)
        
        formatted_history = []
        for msg_dict in message_dicts:
            role = msg_dict.get('role')
            content = msg_dict.get('content', '')
            if role == 'user':
                formatted_history.append(f"User: {content}")
            elif role == 'assistant':
                formatted_history.append(f"Assistant: {content}")
            # System messages are not explicitly handled by ConversationMemory's add_message, but good to be safe
            elif role == 'system': 
                formatted_history.append(f"System: {content}")
        
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

    def update_conversation_title(self, user_id: str, title: str):
        """
        Update the conversation title for a user.
        
        Args:
            user_id: Unique identifier for the user
            title: New title for the conversation
        """
        # This will be handled by get_all_conversations() dynamically
        # but we can save it to file to ensure persistence
        # self.save_memory_to_file() # This method was removed.
        logger.info(f"Updated conversation title for user {user_id}: {title} (Note: Title is dynamically generated, this call is a placeholder or needs rethinking for persistence if required outside session memory)")