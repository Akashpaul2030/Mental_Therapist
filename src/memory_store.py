"""
Memory Store Module

This module handles conversation memory storage using langgraph's InMemoryStore.
It allows the chatbot to maintain conversation context and history.
"""

import logging
import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
# from langgraph.checkpoint.base import BaseCheckpointSaver # Not used if we simplify
# from langgraph.checkpoint.memory import MemoryStore # Replacing with simple dict
# from langchain_core.runnables import RunnableConfig # Not used if we simplify
# from langchain_core.pydantic_v1 import Field # Not used
# from langchain_core.messages import AIMessage, HumanMessage # Not used in this class directly

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
    """Manages conversation history for multiple users using a simple dictionary as a store."""

    def __init__(self, max_history_length: int = 10):
        """Initialize the conversation memory."""
        self.store: Dict[str, List[Dict[str, str]]] = {}  # User ID -> List of messages
        self.max_history_length = max_history_length # Max (user, ai) message pairs
        logger.info("Initialized ConversationMemory with a dictionary store.")

    def get_conversation_history(self, user_id: str) -> List[Dict[str, str]]:
        """
        Retrieve the conversation history for a given user.

        Args:
            user_id: The unique identifier for the user.

        Returns:
            A list of message dictionaries for the user, or an empty list if no history.
        """
        try:
            return self.store.get(user_id, [])
        except Exception as e:
            logger.error(f"Error retrieving conversation history for user {user_id}: {e}")
            return []

    def add_message(self, user_id: str, role: str, content: str) -> None:
        """
        Add a message to the conversation history for a user and ensure history length.

        Args:
            user_id: The unique identifier for the user.
            role: The role of the message sender ('user' or 'assistant').
            content: The content of the message.
        """
        try:
            if user_id not in self.store:
                self.store[user_id] = []
            
            self.store[user_id].append({"role": role, "content": content})

            # Trim history: keep only the last max_history_length pairs (i.e., max_history_length * 2 messages)
            if len(self.store[user_id]) > self.max_history_length * 2:
                self.store[user_id] = self.store[user_id][-(self.max_history_length * 2):]
            
            # logger.info(f"Added {role} message for user {user_id}") # Logged by callers if needed
        except Exception as e:
            logger.error(f"Error adding {role} message for user {user_id}: {e}")

    def add_user_message(self, user_id: str, message_content: str) -> None:
        """Add a user message to the history."""
        self.add_message(user_id, "user", message_content)
        logger.info(f"Added user message for user {user_id} in ConversationMemory")

    def add_bot_message(self, user_id: str, message_content: str) -> None:
        """Add a bot (assistant) message to the history."""
        self.add_message(user_id, "assistant", message_content)
        logger.info(f"Added assistant message for user {user_id} in ConversationMemory")

    def get_formatted_history(self, user_id: str) -> str:
        """
        Get the conversation history formatted as a string.

        Args:
            user_id: The unique identifier for the user.

        Returns:
            A string representation of the conversation history.
        """
        history_list = self.get_conversation_history(user_id)
        if not history_list:
            return ""
        
        formatted = []
        for msg in history_list:
            sender = "User" if msg['role'] == 'user' else "Assistant"
            formatted.append(f"{sender}: {msg['content']}")
        return "\n".join(formatted)

    def clear_history(self, user_id: str) -> None:
        """
        Clear the conversation history for a specific user.

        Args:
            user_id: The unique identifier for the user whose history to clear.
        """
        try:
            if user_id in self.store:
                del self.store[user_id]
                logger.info(f"Cleared conversation history for user {user_id} in ConversationMemory")
            else:
                logger.info(f"No history found to clear for user {user_id} in ConversationMemory")
        except Exception as e:
            logger.error(f"Error clearing history for user {user_id}: {e}")

# Example usage (optional)
if __name__ == '__main__':
    memory = ConversationMemory(max_history_length=2)
    uid1 = "user123"
    uid2 = "user456"

    memory.add_user_message(uid1, "Hello there!")
    memory.add_bot_message(uid1, "Hi! How can I help you today?")
    memory.add_user_message(uid1, "I'm feeling a bit down.")
    memory.add_bot_message(uid1, "I'm sorry to hear that. Would you like to talk about it?")
    memory.add_user_message(uid1, "Yes, please. It's about my work.") # This should trim the first pair
    memory.add_bot_message(uid1, "Okay, I'm here to listen. Tell me about your work.")

    print(f"History for {uid1}:\n{memory.get_formatted_history(uid1)}")
    # Expected: User: I'm feeling a bit down.... Bot: Okay, I'm here to listen...
    # Total 4 messages (2 pairs)

    memory.add_user_message(uid2, "I need help with anxiety.")
    memory.add_bot_message(uid2, "I can share some techniques for managing anxiety.")
    print(f"\nHistory for {uid2}:\n{memory.get_formatted_history(uid2)}")

    memory.clear_history(uid1)
    print(f"\nHistory for {uid1} after clearing: '{memory.get_formatted_history(uid1)}'")

    print(f"\nAll stored data: {memory.store}")