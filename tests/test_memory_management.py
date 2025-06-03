import os
import json
import shutil
import pytest
from unittest.mock import patch, mock_open

# Assuming your classes are in src.memory_manager and src.memory_store
# Adjust these imports if your project structure is different
from src.memory_manager import MentalHealthMemoryManager
from src.memory_store import ConversationMemory
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# --- Tests for MentalHealthMemoryManager (from src/memory_manager.py) ---

@pytest.fixture
def mhm_manager():
    """Provides a MentalHealthMemoryManager instance for in-memory testing."""
    manager = MentalHealthMemoryManager(max_token_limit=50) 
    return manager

class TestMentalHealthMemoryManager:

    def test_MHM_initialization(self, mhm_manager: MentalHealthMemoryManager):
        """Test that the manager initializes correctly for in-memory storage."""
        assert mhm_manager is not None
        assert mhm_manager.max_token_limit == 50 

    def test_MHM_add_and_get_messages(self, mhm_manager: MentalHealthMemoryManager):
        """Test adding user and AI messages and retrieving history."""
        user_id = "user1"

        mhm_manager.add_user_message(user_id, "Hello there!")
        mhm_manager.add_bot_message(user_id, "Hi! How can I help?")
        
        history_obj: ConversationMemory = mhm_manager.get_history(user_id) # Returns src.memory_store.ConversationMemory
        messages_list = history_obj.get_conversation_history(user_id)
        
        assert len(messages_list) == 2
        assert messages_list[0]["role"] == "user"
        assert messages_list[0]["content"] == "Hello there!"
        assert messages_list[1]["role"] == "assistant"
        assert messages_list[1]["content"] == "Hi! How can I help?"

        formatted_history = mhm_manager.get_formatted_history(user_id)
        assert "User: Hello there!" in formatted_history
        assert "Assistant: Hi! How can I help?" in formatted_history

    def test_MHM_history_trimming(self, mhm_manager: MentalHealthMemoryManager):
        """Test that conversation history is trimmed based on max_token_limit."""
        user_id = "user_trim"
        mhm_manager.max_token_limit = 20 # Override for MHM's token trimming

        # Add messages that will exceed the token limit (approximate words as tokens)
        mhm_manager.add_user_message(user_id, "This is user message one, it is quite long and has many words.") # ~12 tokens
        mhm_manager.add_bot_message(user_id, "This is a bot reply, also quite long for testing purposes.") # ~10 tokens
        mhm_manager.add_user_message(user_id, "Another user message that will push it over the very small limit.") # ~12 tokens
        
        history_obj: ConversationMemory = mhm_manager.get_history(user_id)
        messages_list = history_obj.get_conversation_history(user_id)
        
        current_token_count = sum(len(str(msg.get('content','')).split()) for msg in messages_list)
        
        assert current_token_count <= mhm_manager.max_token_limit
        assert len(messages_list) < 3 # We added 3, at least one should be trimmed by MHM's token limit logic
        # Check that the latest message is present
        assert messages_list[-1]["content"] == "Another user message that will push it over the very small limit."

    def test_MHM_update_and_get_user_details(self, mhm_manager: MentalHealthMemoryManager): # Renamed from extract_and_store
        """Test updating and storage of user details (extraction logic is separate)."""
        user_id = "user_details_test"
        
        initial_details = {"name": "Alex", "feelings": "anxious", "triggers": "exams"}
        mhm_manager.update_user_details(user_id, initial_details)
        
        details = mhm_manager.get_user_details(user_id)
        assert details.get("name") == "Alex"
        assert details.get("feelings") == "anxious"

        mhm_manager.update_user_details(user_id, {"concerns": "sleep quality", "name": "Alexander"}) # Update existing, add new
        details = mhm_manager.get_user_details(user_id)
        assert details.get("concerns") == "sleep quality"
        assert details.get("name") == "Alexander" # Name should be updated

    def test_MHM_get_context_for_response(self, mhm_manager: MentalHealthMemoryManager):
        """Test if get_context_for_response formats details and history correctly."""
        user_id = "user_context"
        mhm_manager.add_user_message(user_id, "My name is Sam.")
        mhm_manager.add_bot_message(user_id, "Hi Sam!")
        mhm_manager.update_user_details(user_id, {"name": "Sam", "triggers": "public speaking"})

        context = mhm_manager.get_context_for_response(user_id)
        # These assertions depend on the exact formatting in get_context_for_response & get_formatted_history
        assert "User's name: Sam" in context["user_details"] 
        assert "Anxiety/stress triggers: public speaking" in context["user_details"] 
        # get_formatted_history should now correctly use ConversationMemory from src.memory_store
        assert "User: My name is Sam." in context["history"]
        assert "Assistant: Hi Sam!" in context["history"]

    def test_MHM_session_management_multiple_users(self, mhm_manager: MentalHealthMemoryManager):
        """Test that sessions for different users are isolated."""
        user1_id = "user_session1"
        user2_id = "user_session2"

        mhm_manager.add_user_message(user1_id, "Info for user 1")
        mhm_manager.update_user_details(user1_id, {"name": "UserOne"})

        mhm_manager.add_user_message(user2_id, "Info for user 2")
        mhm_manager.update_user_details(user2_id, {"name": "UserTwo"})

        assert mhm_manager.get_user_details(user1_id).get("name") == "UserOne"
        history1_str = mhm_manager.get_formatted_history(user1_id)
        assert "User: Info for user 1" in history1_str 
        
        assert mhm_manager.get_user_details(user2_id).get("name") == "UserTwo"
        history2_str = mhm_manager.get_formatted_history(user2_id)
        assert "User: Info for user 2" in history2_str

    def test_MHM_clear_history(self, mhm_manager: MentalHealthMemoryManager):
        """Test clearing history for a user, including their details."""
        user_id = "user_clear"
        mhm_manager.add_user_message(user_id, "Test message")
        mhm_manager.update_user_details(user_id, {"name": "Temporary"})
        
        mhm_manager.clear_history(user_id) # This now calls clear_history(user_id) on ConversationMemory
        
        history_obj: ConversationMemory = mhm_manager.get_history(user_id) 
        messages_list = history_obj.get_conversation_history(user_id)
        assert len(messages_list) == 0
        
        assert mhm_manager.get_formatted_history(user_id) == ""
        
        # Check if user details are also cleared as per new MHM.clear_history()
        details = mhm_manager.get_user_details(user_id)
        assert details is None # Or assert details == {} if defaultdict creates an empty dict entry on get

# --- Tests for ConversationMemory (from src/memory_store.py) ---
# These tests now reflect that ConversationMemory is a multi-user store,
# and user_id is passed to its methods, not set at initialization.

@pytest.fixture
def cm_memory(): # Renamed fixture for clarity
    """Provides a ConversationMemory instance with a specific history length for its own tests."""
    # ConversationMemory's max_history_length is about pairs of messages, not tokens
    # user_id is NOT passed to constructor.
    return ConversationMemory(max_history_length=2)

class TestConversationMemory:
    # Define a consistent user_id for these tests
    TEST_USER_ID = "test_cm_user"

    def test_CM_initialization(self, cm_memory: ConversationMemory):
        """Test ConversationMemory initializes."""
        assert cm_memory is not None
        assert cm_memory.max_history_length == 2
        # user_id is not an attribute of ConversationMemory instance itself.
        # No assertion for cm_memory.user_id here.

    def test_CM_add_and_get_messages(self, cm_memory: ConversationMemory):
        """Test adding user/bot messages and retrieving history."""
        
        cm_memory.add_user_message(self.TEST_USER_ID, "Hello CM")
        cm_memory.add_bot_message(self.TEST_USER_ID, "Hi CM user") # Corrected from add_ai_message and added user_id

        history_list = cm_memory.get_conversation_history(self.TEST_USER_ID) # Access messages via method
        assert len(history_list) == 2
        assert history_list[0]["role"] == "user"
        assert history_list[0]["content"] == "Hello CM"
        assert history_list[1]["role"] == "assistant"
        assert history_list[1]["content"] == "Hi CM user"

        formatted_output = cm_memory.get_formatted_history(self.TEST_USER_ID)
        assert "User: Hello CM" in formatted_output
        assert "Assistant: Hi CM user" in formatted_output


    def test_CM_history_trimming(self, cm_memory: ConversationMemory):
        """Test history trimming for ConversationMemory. max_history_length is in pairs."""
        # max_history_length=2 means 2 pairs, so 4 messages total (2 user, 2 bot)
        
        for i in range(3): 
            cm_memory.add_user_message(self.TEST_USER_ID, f"User {i+1}")
            cm_memory.add_bot_message(self.TEST_USER_ID, f"Bot {i+1}")
        
        history_list = cm_memory.get_conversation_history(self.TEST_USER_ID)
        # Expecting max_history_length * 2 messages
        assert len(history_list) == cm_memory.max_history_length * 2 
        assert history_list[0]["content"] == "User 2" 
        assert history_list[-1]["content"] == "Bot 3"

    def test_CM_clear_history(self, cm_memory: ConversationMemory):
        """Test clearing history."""
        cm_memory.add_user_message(self.TEST_USER_ID, "To be cleared")
        cm_memory.clear_history(self.TEST_USER_ID) # Pass user_id
        
        assert len(cm_memory.get_conversation_history(self.TEST_USER_ID)) == 0

    def test_CM_get_empty_history(self, cm_memory: ConversationMemory):
        """Test retrieving history for a new user returns empty list as per implementation."""
        new_user_id = "new_user_for_empty_test"
        # For a freshly initialized ConversationMemory, history for a new user_id is empty.
        assert len(cm_memory.get_conversation_history(new_user_id)) == 0 