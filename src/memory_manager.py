"""
Memory Manager Module for Mental Health Chatbot

This module handles conversation memory using LangChain's ChatMessageHistory.
It tracks user details and conversation history to provide context for responses.
"""

import logging
import os
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import json
import datetime

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
    
    def __init__(self, max_history_length: int = 10):
        """Initialize the memory manager."""
        self.chat_histories = {}  # Dictionary to store chat histories by user ID
        self.user_details = {}  # Dictionary to store user details by user ID
        self.max_history_length = max_history_length
        self.user_detail_keys = ['name', 'triggers', 'situations', 'concerns']
        self.memory_file = os.path.join('data', 'chat_memory.json')
        self.load_memory_from_file()
        logger.info("Initialized mental health memory manager")
    
    def load_memory_from_file(self):
        """Load memory from file if it exists."""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    
                    # Load user details
                    self.user_details = data.get('user_details', {})
                    
                    # Create ChatMessageHistory for each conversation
                    for user_id, messages in data.get('conversations', {}).items():
                        history = ChatMessageHistory()
                        for msg in messages:
                            if msg['role'] == 'user':
                                history.add_user_message(msg['content'])
                            elif msg['role'] == 'assistant':
                                history.add_ai_message(msg['content'])
                            elif msg['role'] == 'system':
                                history.add_message(SystemMessage(content=msg['content']))
                        
                        self.chat_histories[user_id] = history
                    
                logger.info(f"Loaded memory for {len(self.chat_histories)} conversations from file")
        except Exception as e:
            logger.error(f"Error loading memory from file: {e}")
    
    def save_memory_to_file(self):
        """Save memory to file."""
        try:
            # Prepare data structure
            data = {
                'user_details': self.user_details,
                'conversations': {}
            }
            
            # Convert ChatMessageHistory to serializable format
            for user_id, history in self.chat_histories.items():
                messages = []
                for msg in history.messages:
                    if isinstance(msg, HumanMessage):
                        messages.append({'role': 'user', 'content': msg.content})
                    elif isinstance(msg, AIMessage):
                        messages.append({'role': 'assistant', 'content': msg.content})
                    elif isinstance(msg, SystemMessage):
                        messages.append({'role': 'system', 'content': msg.content})
                
                data['conversations'][user_id] = messages
            
            # Save to file
            with open(self.memory_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved memory for {len(self.chat_histories)} conversations to file")
        except Exception as e:
            logger.error(f"Error saving memory to file: {e}")
    
    def get_chat_history(self, user_id: str) -> ChatMessageHistory:
        """
        Get or create a chat history for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            ChatMessageHistory for the user
        """
        if user_id not in self.chat_histories:
            self.chat_histories[user_id] = ChatMessageHistory()
        
        return self.chat_histories[user_id]
    
    def add_user_message(self, user_id: str, message: str) -> None:
        """
        Add a user message to the conversation history.
        
        Args:
            user_id: Unique identifier for the user
            message: User's message
        """
        # Get chat history
        chat_history = self.get_chat_history(user_id)
        
        # Add message
        chat_history.add_user_message(message)
        
        # Extract details from message
        details = self.extract_details_from_message(message)
        if details:
            self.update_user_details(user_id, details)
        
        # Save to file after updates
        self.save_memory_to_file()
        
        logger.info(f"Added user message for user {user_id}")
    
    def add_bot_message(self, user_id: str, message: str) -> None:
        """
        Add a bot message to the conversation history.
        
        Args:
            user_id: Unique identifier for the user
            message: Bot's message
        """
        # Get chat history
        chat_history = self.get_chat_history(user_id)
        
        # Add message
        chat_history.add_ai_message(message)
        
        # Save to file after updates
        self.save_memory_to_file()
        
        logger.info(f"Added bot message for user {user_id}")
    
    def update_user_details(self, user_id: str, details: Dict) -> None:
        """
        Update user details in memory.
        
        Args:
            user_id: Unique identifier for the user
            details: Dictionary of user details to update
        """
        # Initialize user details if not exists
        if user_id not in self.user_details:
            self.user_details[user_id] = {k: None for k in self.user_detail_keys}
        
        # Update only valid detail keys
        for k, v in details.items():
            if k in self.user_detail_keys and v:
                self.user_details[user_id][k] = v
        
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
    
    def get_conversation_messages(self, user_id: str) -> List[Dict[str, str]]:
        """
        Get the conversation messages for a user in a serializable format.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            List of message dictionaries with 'role' and 'content'
        """
        if user_id not in self.chat_histories:
            return []
        
        history = self.chat_histories[user_id]
        messages = []
        
        for msg in history.messages:
            if isinstance(msg, HumanMessage):
                messages.append({'role': 'user', 'content': msg.content})
            elif isinstance(msg, AIMessage):
                messages.append({'role': 'assistant', 'content': msg.content})
        
        return messages
    
    def get_all_conversations(self) -> Dict[str, Dict]:
        """
        Get all conversations with basic metadata.
        
        Returns:
            Dictionary mapping user_id to conversation metadata
        """
        result = {}
        
        for user_id, history in self.chat_histories.items():
            # Skip empty conversations
            if not history.messages:
                continue
                
            # Get first message for title
            first_message = None
            for msg in history.messages:
                if isinstance(msg, HumanMessage):
                    first_message = msg.content
                    break
            
            # Create title from first message
            title = "New Conversation"
            if first_message:
                words = first_message.split()
                if len(words) > 3:
                    title = " ".join(words[:3]) + "..."
                else:
                    title = first_message
            
            # Count messages
            message_count = len([msg for msg in history.messages])
            
            # Get timestamp (approximated from current time)
            timestamp = datetime.datetime.now().isoformat()
            
            result[user_id] = {
                'title': title,
                'message_count': message_count,
                'last_updated': timestamp
            }
        
        return result
    
    def get_user_details(self, user_id: str) -> Dict:
        """
        Get the stored details for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary of user details
        """
        return self.user_details.get(user_id, {})
    
    def get_formatted_history(self, user_id: str) -> str:
        """
        Get the conversation history formatted as a string.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Formatted conversation history
        """
        if user_id not in self.chat_histories:
            return ""
        
        history = self.chat_histories[user_id]
        formatted_history = []
        
        for msg in history.messages:
            if isinstance(msg, HumanMessage):
                formatted_history.append(f"User: {msg.content}")
            elif isinstance(msg, AIMessage):
                formatted_history.append(f"Assistant: {msg.content}")
        
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
        if user_id in self.chat_histories:
            self.chat_histories[user_id] = ChatMessageHistory()
            self.save_memory_to_file()
        
        logger.info(f"Cleared conversation history for user {user_id}")
    
    def clear_all(self, user_id: str) -> None:
        """
        Clear both conversation history and user details.
        
        Args:
            user_id: Unique identifier for the user
        """
        if user_id in self.chat_histories:
            self.chat_histories[user_id] = ChatMessageHistory()
        
        if user_id in self.user_details:
            self.user_details[user_id] = {k: None for k in self.user_detail_keys}
        
        self.save_memory_to_file()
        
        logger.info(f"Cleared all data for user {user_id}")