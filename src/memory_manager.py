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

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

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
        # self.memory_file_path = memory_file_path # Removed
        # self.load_memory_from_file() # Removed
        logger.info("MentalHealthMemoryManager initialized for in-memory session storage.")

    def _save_memory_to_file(self):
        """
        This method is now a no-op as conversations are not persisted to disk.
        """
        pass # No operation

    # def load_memory_from_file(self):
    #     """
    #     Loads memory state from the JSON file if it exists.
    #     This method is no longer used as memory is not persisted.
    #     """
    #     if os.path.exists(self.memory_file_path):
    #         try:
    #             with open(self.memory_file_path, 'r') as f:
    #                 data = json.load(f)
    #                 for user_id, conv_data in data.get("conversations", {}).items():
    #                     # Reconstruct ConversationMemory instances
    #                     # This requires ConversationMemory to be adaptable or have a from_dict method
    #                     temp_store = InMemoryStore()
    #                     for msg_data in conv_data.get("messages", []):
    #                         if msg_data["type"] == "human":
    #                             temp_store.add_message(HumanMessage(content=msg_data["content"]))
    #                         elif msg_data["type"] == "ai":
    #                             temp_store.add_message(AIMessage(content=msg_data["content"]))
    #                         elif msg_data["type"] == "system":
    #                             temp_store.add_message(SystemMessage(content=msg_data["content"]))
    #                     self.conversations[user_id].store = temp_store.messages # Or however ConversationMemory stores messages
    #                     self.conversations[user_id].user_id = user_id 
    #                 self.user_details = defaultdict(dict, data.get("user_details", {}))
    #             logger.info(f"Memory loaded from {self.memory_file_path}")
    #         except Exception as e:
    #             logger.error(f"Error loading memory from {self.memory_file_path}: {e}")
    #     else:
    #         logger.info("No memory file found, starting with empty memory.")

    def get_history(self, user_id: str) -> ConversationMemory:
        return self.conversations[user_id]

    def add_user_message(self, user_id: str, message_content: str):
        history = self.get_history(user_id)
        history.add_user_message(user_id, message_content)
        self._trim_history(user_id)
        # self._save_memory_to_file() # Removed call

    def add_bot_message(self, user_id: str, message_content: str):
        history = self.get_history(user_id)
        history.add_bot_message(user_id, message_content)
        self._trim_history(user_id)
        # self._save_memory_to_file() # Removed call

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
        # self._save_memory_to_file() # Removed call

    def get_user_details(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.user_details.get(user_id)

    def get_all_conversations(self) -> Dict[str, Dict[str, Any]]:
        all_convos = {}
        for user_id, conv_memory in self.conversations.items(): # conv_memory is src.memory_store.ConversationMemory
            title = "Conversation" 
            last_updated_ts = None # Timestamps not available per message in current ConversationMemory
            message_count = 0

            message_dicts = conv_memory.get_conversation_history(user_id)
            if message_dicts:
                message_count = len(message_dicts)
                first_user_message_content = next((msg_dict.get('content') for msg_dict in message_dicts if msg_dict.get('role') == 'user'), None)
                if first_user_message_content:
                    title = (first_user_message_content[:30] + '...') if len(first_user_message_content) > 30 else first_user_message_content
                
                # last_msg_obj and timestamp logic removed as dicts don't have additional_kwargs
            
            all_convos[user_id] = {
                "title": title,
                "message_count": message_count,
                "last_updated": last_updated_ts, # Will be None
            }
        return all_convos

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
        # self._save_memory_to_file() # Removed call

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