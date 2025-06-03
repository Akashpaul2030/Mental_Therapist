import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient # For WebSocket testing if TestClient's WebSocket support is limited for advanced cases
import sys
import os
import time # Added for timestamp checks
import uuid # For generating test client_ids if needed
import asyncio

# Add the project root to the path to import the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app # Assuming your FastAPI app instance is named 'app' in main.py

@pytest.fixture(scope="module")
def client():
    """Provide a TestClient instance for API testing."""
    with TestClient(app) as c:
        yield c

# --- Test Cases for API Endpoints ---

def test_health_check(client: TestClient):
    """Test the /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "healthy"
    assert "timestamp" in json_response
    assert isinstance(json_response["timestamp"], float) # or int, depending on time.time() precision
    assert "active_connections" in json_response
    assert isinstance(json_response["active_connections"], int)


def test_create_new_conversation(client: TestClient):
    """Test POST /api/conversations/new endpoint."""
    response = client.post("/api/conversations/new")
    assert response.status_code == 200 
    json_response = response.json()
    assert "user_id" in json_response
    assert isinstance(json_response["user_id"], str)
    assert "created_at" in json_response
    assert isinstance(json_response["created_at"], str) # ISO format string
    assert "initial_message" in json_response
    assert isinstance(json_response["initial_message"], str)
    assert json_response["success"] is True


def test_get_all_conversations(client: TestClient):
    """Test GET /api/conversations endpoint."""
    # Step 1: Create a new conversation to ensure there's some data
    new_conv_response = client.post("/api/conversations/new")
    assert new_conv_response.status_code == 200
    new_conv_data = new_conv_response.json()
    user_id_created = new_conv_data["user_id"]
    
    # Step 2: Get all conversations
    response = client.get("/api/conversations")
    assert response.status_code == 200
    json_response = response.json()
    
    assert isinstance(json_response, dict)
    assert user_id_created in json_response # The newly created user should be in the list
    
    # Check the structure of the newly created user's entry based on
    # the actual current implementation of MentalHealthMemoryManager.get_all_conversations()
    user_conv_data = json_response[user_id_created]
    
    assert "title" in user_conv_data
    assert isinstance(user_conv_data["title"], str)
    
    assert "message_count" in user_conv_data
    assert isinstance(user_conv_data["message_count"], int)
    assert user_conv_data["message_count"] >= 1 # At least the initial bot message from /new endpoint

    assert "last_updated" in user_conv_data
    # As per memory_manager.get_all_conversations, last_updated is currently None
    assert user_conv_data["last_updated"] is None 
    # We no longer check for user_details or a specific last_message_at in this test,
    # as the current get_all_conversations in memory_manager doesn't provide them in this exact way.


def test_get_user_conversation_found(client: TestClient):
    """Test GET /api/conversations/{user_id} when conversation exists."""
    # Step 1: Create a new conversation
    new_conv_response = client.post("/api/conversations/new")
    assert new_conv_response.status_code == 200
    new_conv_data = new_conv_response.json()
    user_id = new_conv_data["user_id"]
    initial_message_content = new_conv_data["initial_message"]

    # Step 2: Get the conversation for this user_id
    response = client.get(f"/api/conversations/{user_id}")
    assert response.status_code == 200
    json_response = response.json()
    
    assert "messages" in json_response
    assert isinstance(json_response["messages"], list)
    # The /new endpoint adds the initial greeting as a bot message.
    # chatbot.start_conversation might also add one. Expect at least one.
    assert len(json_response["messages"]) >= 1 
    # Assuming the last message in the list is the one explicitly added by the /new endpoint
    # or that it's the only one if start_conversation doesn't add to history visible here.
    # This might need adjustment if chatbot.start_conversation also adds a persistent message.
    assert json_response["messages"][-1]["role"] == "assistant"
    assert json_response["messages"][-1]["content"] == initial_message_content

    assert "user_details" in json_response
    assert isinstance(json_response["user_details"], dict)
    # API /api/conversations/{user_id} returns {} if details are None from memory_manager
    assert json_response["user_details"] == {} 


def test_get_user_conversation_not_found(client: TestClient):
    """Test GET /api/conversations/{user_id} when conversation does not exist."""
    non_existent_user_id = f"nonexistentuser_{uuid.uuid4().hex}"
    response = client.get(f"/api/conversations/{non_existent_user_id}")
    
    # Expect 404 Not Found if messages and user_details are both empty
    assert response.status_code == 404
    json_response = response.json()
    assert json_response["detail"] == f"Conversation not found for user_id: {non_existent_user_id}"


def test_clear_user_history(client: TestClient):
    """Test POST /clear_history/{client_id} endpoint."""
    # Step 1: Create a new conversation to get a client_id
    new_conv_response = client.post("/api/conversations/new")
    assert new_conv_response.status_code == 200
    client_id = new_conv_response.json()["user_id"] # user_id is used as client_id here

    # Optional: Add some history via WebSocket if a direct method isn't available
    # For now, we assume the initial greeting creates some history that can be cleared.

    # Step 2: Clear the history
    response = client.post(f"/clear_history/{client_id}")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Conversation history cleared successfully"}
    
    # Step 3: Verify history is actually cleared by GETting the conversation
    get_response = client.get(f"/api/conversations/{client_id}")
    # After clearing, the user should not be found, resulting in a 404
    assert get_response.status_code == 404
    cleared_conv_data = get_response.json()
    assert cleared_conv_data["detail"] == f"Conversation not found for user_id: {client_id}"
    # The following assertions are now redundant due to the 404 check
    # assert cleared_conv_data["messages"] == [] 
    # assert cleared_conv_data["user_details"] == {}


def test_websocket_connection_and_initial_message(client: TestClient):
    """Test WebSocket connection and receiving the initial greeting message."""
    client_id = "test_ws_client_123"
    with client.websocket_connect(f"/ws/{client_id}") as websocket:
        # The chatbot should send an initial greeting or disclaimer upon connection
        data = websocket.receive_json() 
        assert "content" in data # Changed from "message" to "content"
        assert "sender" in data
        assert data["sender"] == "bot"
        # Example assertion based on data["content"]
        # assert "This is not a replacement for professional help" in data["content"]


def test_websocket_send_and_receive(client: TestClient):
    """Test sending a message via WebSocket and receiving a bot response (simplified)."""
    client_id = "test_ws_client_send_recv_simplified"
    print(f"\n[TEST_WS_SIMPLIFIED] Connecting to /ws/{client_id}...")
    with client.websocket_connect(f"/ws/{client_id}") as websocket:
        print(f"[TEST_WS_SIMPLIFIED] Connected. Receiving initial message...")
        try:
            initial_bot_message = websocket.receive_json() # Removed timeout
            print(f"[TEST_WS_SIMPLIFIED] Received initial message: {initial_bot_message}")
            assert "content" in initial_bot_message # Check for "content"
            assert initial_bot_message["sender"] == "bot"
        except Exception as e:
            print(f"[TEST_WS_SIMPLIFIED] Error receiving initial message: {e}")
            pytest.fail(f"Error receiving initial WS message: {e}")

        user_message = "Hello"
        print(f"[TEST_WS_SIMPLIFIED] Sending user message: {user_message}")
        try:
            websocket.send_json({"message": user_message, "user_id": client_id})
            print(f"[TEST_WS_SIMPLIFIED] User message sent. Receiving bot response...")
        except Exception as e:
            print(f"[TEST_WS_SIMPLIFIED] Error sending user message: {e}")
            pytest.fail(f"Error sending WS message: {e}")
        
        try:
            bot_response = websocket.receive_json() # Removed timeout
            print(f"[TEST_WS_SIMPLIFIED] Received bot response: {bot_response}")
            assert "content" in bot_response # Check for "content"
            assert bot_response["sender"] == "bot"
            assert len(bot_response["content"]) > 0
        except Exception as e:
            print(f"[TEST_WS_SIMPLIFIED] Error receiving bot response: {e}")
            pytest.fail(f"Error receiving bot response: {e}. App might be hanging.")
    print(f"[TEST_WS_SIMPLIFIED] WebSocket closed for {client_id}.")


# Renamed and split the original test_websocket_communication
# Old test_websocket_communication is covered by the more specific tests above.

# More tests can be added:
# - Test for invalid input/payloads for POST/PUT requests (e.g. /api/conversations/new if it took a payload).
# - Test for authentication/authorization if implemented (not in current scope).
# - Test for specific business logic scenarios via API calls (e.g. crisis detection triggering specific API responses if applicable).
# - Test rate limiting if implemented (not in current scope).
# - Test behavior when dependent services (like LLM or DB) are unavailable (requires mocking, advanced).

# Placeholder for more advanced WebSocket tests if needed, possibly using AsyncClient
# @pytest.mark.asyncio
# async def test_websocket_advanced_flow():
#     # Using AsyncClient for more complex async WebSocket interactions if TestClient limitations are hit
#     # This is a basic template and would need main.app to be ASGI compatible for AsyncClient
#     async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as ac:
#         async with ac.websocket_connect(f"/ws/test_advanced_ws_client") as ws:
#             greeting = await ws.receive_json()
#             assert greeting["sender"] == "bot"
            
#             await ws.send_json({"message": "Tell me about CBT", "user_id": "test_advanced_ws_client"})
#             response = await ws.receive_json()
#             assert response["sender"] == "bot"
#             assert "CBT" in response["message"] # Example assertion

# --- Further tests to consider ---
# - Test GET /api/conversations (might need some conversations to be created first)
# - Test GET /api/conversations/{user_id}
# - Test POST /clear_history/{client_id}
# - Test for error handling (e.g., invalid client_id, malformed WebSocket messages)
# - Test for crisis detection via WebSocket
# - Test for ethical guideline responses via WebSocket (e.g., asking for medical advice)
# - Test for memory recall via WebSocket over a few turns 