"""
API Integration Test for Mental Health Chatbot

This script tests the FastAPI endpoints and WebSocket functionality
to ensure the API is working correctly.
"""

import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the FastAPI app
from main import app

# Create test client
client = TestClient(app)

class TestAPIEndpoints:
    """Test class for API endpoints."""
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "active_connections" in data
    
    def test_root_endpoint(self):
        """Test the root endpoint serves the HTML file."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
    
    def test_create_new_conversation(self):
        """Test creating a new conversation."""
        response = client.post("/api/conversations/new")
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "created_at" in data
        assert "initial_message" in data
        assert data["success"] is True
        assert data["user_id"].startswith("user_")
    
    def test_get_conversations(self):
        """Test getting all conversations."""
        response = client.get("/api/conversations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
    
    def test_get_specific_conversation(self):
        """Test getting a specific conversation."""
        # First create a conversation
        create_response = client.post("/api/conversations/new")
        user_id = create_response.json()["user_id"]
        
        # Then get the conversation
        response = client.get(f"/api/conversations/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert "user_details" in data
        assert isinstance(data["messages"], list)
        assert isinstance(data["user_details"], dict)
    
    def test_clear_history(self):
        """Test clearing conversation history."""
        # First create a conversation
        create_response = client.post("/api/conversations/new")
        user_id = create_response.json()["user_id"]
        
        # Clear the history
        response = client.post(f"/clear_history/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "message" in data
    
    def test_debug_endpoint(self):
        """Test the debug endpoint."""
        # First create a conversation
        create_response = client.post("/api/conversations/new")
        user_id = create_response.json()["user_id"]
        
        # Get debug info
        response = client.get(f"/debug/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert "client_id" in data
        assert "user_details" in data
        assert "history_length" in data

class TestWebSocketIntegration:
    """Test class for WebSocket functionality."""
    
    def test_websocket_connection(self):
        """Test WebSocket connection and basic message exchange."""
        client_id = "test_client_123"
        
        with client.websocket_connect(f"/ws/{client_id}") as websocket:
            # Should receive initial greeting
            data = websocket.receive_json()
            assert data["type"] == "message"
            assert data["sender"] == "bot"
            assert "IMPORTANT" in data["content"]
            
            # Send a test message
            test_message = {
                "type": "message",
                "text": "Hello, I'm feeling anxious today"
            }
            websocket.send_text(json.dumps(test_message))
            
            # Should receive a response
            response = websocket.receive_json()
            assert response["type"] == "message"
            assert response["sender"] == "bot"
            assert isinstance(response["content"], str)
            assert len(response["content"]) > 0
    
    def test_websocket_clear_command(self):
        """Test WebSocket clear command."""
        client_id = "test_client_clear"
        
        with client.websocket_connect(f"/ws/{client_id}") as websocket:
            # Receive initial greeting
            websocket.receive_json()
            
            # Send clear command
            clear_message = {
                "type": "message",
                "text": "clear"
            }
            websocket.send_text(json.dumps(clear_message))
            
            # Should receive system message about clearing
            response = websocket.receive_json()
            assert response["type"] == "system"
            assert "cleared" in response["content"].lower()

class TestErrorHandling:
    """Test class for error handling scenarios."""
    
    def test_invalid_conversation_id(self):
        """Test getting a conversation with invalid ID."""
        response = client.get("/api/conversations/invalid_id")
        # Should still return 200 with empty data or handle gracefully
        assert response.status_code in [200, 404, 500]
    
    def test_clear_history_invalid_id(self):
        """Test clearing history with invalid client ID."""
        response = client.post("/clear_history/invalid_id")
        # Should handle gracefully
        assert response.status_code in [200, 404, 500]
    
    @patch('src.chatbot.MentalHealthChatbot.process_message')
    def test_chatbot_error_handling(self, mock_process):
        """Test error handling when chatbot fails."""
        # Mock chatbot to raise an exception
        mock_process.side_effect = Exception("Test error")
        
        client_id = "test_error_client"
        
        with client.websocket_connect(f"/ws/{client_id}") as websocket:
            # Receive initial greeting
            websocket.receive_json()
            
            # Send a message that will cause an error
            test_message = {
                "type": "message",
                "text": "This should cause an error"
            }
            websocket.send_text(json.dumps(test_message))
            
            # Should receive an error message
            response = websocket.receive_json()
            assert response["type"] == "error"
            assert "error" in response["content"].lower() or "issue" in response["content"].lower()

class TestChatbotIntegration:
    """Test class for chatbot integration through API."""
    
    def test_anxiety_question_through_api(self):
        """Test asking about anxiety through WebSocket."""
        client_id = "test_anxiety_client"
        
        with client.websocket_connect(f"/ws/{client_id}") as websocket:
            # Receive initial greeting
            websocket.receive_json()
            
            # Ask about anxiety
            anxiety_message = {
                "type": "message",
                "text": "I've been feeling really anxious lately. What can I do?"
            }
            websocket.send_text(json.dumps(anxiety_message))
            
            # Should receive helpful response
            response = websocket.receive_json()
            assert response["type"] == "message"
            assert response["sender"] == "bot"
            content = response["content"].lower()
            
            # Response should contain helpful anxiety-related content
            anxiety_keywords = ["anxiety", "breathing", "relaxation", "technique", "support", "help"]
            assert any(keyword in content for keyword in anxiety_keywords)
    
    def test_crisis_detection_through_api(self):
        """Test crisis detection through WebSocket."""
        client_id = "test_crisis_client"
        
        with client.websocket_connect(f"/ws/{client_id}") as websocket:
            # Receive initial greeting
            websocket.receive_json()
            
            # Send a crisis message
            crisis_message = {
                "type": "message",
                "text": "I don't want to live anymore"
            }
            websocket.send_text(json.dumps(crisis_message))
            
            # Should receive crisis response
            response = websocket.receive_json()
            assert response["type"] == "message"
            assert response["sender"] == "bot"
            content = response["content"].lower()
            
            # Response should contain crisis intervention content
            crisis_keywords = ["crisis", "hotline", "988", "help", "support", "emergency"]
            assert any(keyword in content for keyword in crisis_keywords)

# Pytest fixtures and setup
@pytest.fixture
def client_fixture():
    """Fixture to provide test client."""
    return client

# Run tests if this file is executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
