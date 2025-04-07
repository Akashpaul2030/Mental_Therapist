"""
Integration Test for Mental Health Chatbot

This script tests the complete functionality of the mental health chatbot
by integrating all components and simulating user interactions.
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.chatbot import MentalHealthChatbot

# Load environment variables
load_dotenv()

def test_chatbot_integration():
    """Test the complete chatbot functionality with various scenarios."""
    print("Initializing Mental Health Chatbot...")
    chatbot = MentalHealthChatbot()
    
    # Start conversation
    print("\n=== Starting Conversation ===")
    greeting = chatbot.start_conversation()
    print(f"Chatbot: {greeting}")
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "General Mental Health Question",
            "messages": [
                "What are some ways to manage anxiety?"
            ]
        },
        {
            "name": "Medical Advice Request",
            "messages": [
                "Do I have depression based on these symptoms?"
            ]
        },
        {
            "name": "Crisis Situation",
            "messages": [
                "I can't take it anymore, I want to end my life",
                "Yes, I called the hotline"  # Safety verification
            ]
        },
        {
            "name": "CBT Techniques Request",
            "messages": [
                "Can you suggest some CBT exercises for negative thoughts?"
            ]
        },
        {
            "name": "Sleep Issues",
            "messages": [
                "I've been having trouble sleeping. What can I do?"
            ]
        }
    ]
    
    # Run through each test scenario
    for scenario in test_scenarios:
        print(f"\n\n=== Testing Scenario: {scenario['name']} ===")
        
        for i, message in enumerate(scenario['messages']):
            print(f"\nUser: {message}")
            response = chatbot.process_message(message)
            print(f"Chatbot: {response}")
    
    print("\n=== Integration Testing Completed ===")

if __name__ == "__main__":
    test_chatbot_integration()
