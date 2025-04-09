#!/usr/bin/env python3
"""
Main script for running the Mental Health Chatbot.

This script provides a simple command-line interface for interacting with the chatbot.
It utilizes the conversation memory system to maintain context between interactions.
"""

import os
import logging
import uuid
from dotenv import load_dotenv

# Import the chatbot module
from src.chatbot import MentalHealthChatbot

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.getenv('LOG_FILE', 'chatbot.log')
)
logger = logging.getLogger(__name__)

def main():
    """Run the Mental Health Chatbot with a simple command-line interface."""
    print("Starting Mental Health Chatbot...")
    
    # Initialize the chatbot
    chatbot = MentalHealthChatbot()
    
    # Generate a unique user ID for this session
    user_id = str(uuid.uuid4())
    print(f"Session ID: {user_id}")
    
    # Start conversation with disclaimer
    greeting = chatbot.start_conversation(user_id)
    print(f"\nChatbot: {greeting}")
    
    # Main conversation loop
    print("\nType 'exit', 'quit', or 'bye' to end the conversation.")
    print("Type 'clear' to clear conversation history.")
    print("Type 'history' to view current conversation history.")
    print("Type 'debug' to print debug information.")
    
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        # Check for exit command
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("\nChatbot: Thank you for talking with me. Take care of yourself, and remember that professional help is available if you need it.")
            break
        
        # Check for clear history command
        if user_input.lower() == 'clear':
            chatbot.memory.clear_history(user_id)
            print("\nChatbot: Conversation history has been cleared.")
            continue
        
        # Check for view history command
        if user_input.lower() == 'history':
            history = chatbot.get_conversation_history(user_id)
            print("\n----- CONVERSATION HISTORY -----")
            print(history if history else "No conversation history available.")
            print("---------------------------------")
            continue
        
        # Check for debug command
        if user_input.lower() == 'debug':
            conversation = chatbot.memory.get_conversation_history(user_id)
            print("\n----- DEBUG INFORMATION -----")
            print(f"User ID: {user_id}")
            print(f"Conversation started: {chatbot.conversation_started}")
            print(f"Number of messages in history: {len(conversation)}")
            for i, msg in enumerate(conversation):
                print(f"Message {i+1}: {msg['role']} - {msg['content'][:50]}...")
            print("-----------------------------")
            continue
        
        # Process user input and get response
        response = chatbot.process_message(user_input, user_id)
        print(f"\nChatbot: {response}")

if __name__ == "__main__":
    main()