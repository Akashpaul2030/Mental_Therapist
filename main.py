#!/usr/bin/env python3
"""
Main script for running the Mental Health Chatbot.

This script provides a simple command-line interface for interacting with the chatbot.
"""

import os
import logging
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
    
    # Start conversation with disclaimer
    greeting = chatbot.start_conversation()
    print(f"\nChatbot: {greeting}")
    
    # Main conversation loop
    print("\nType 'exit', 'quit', or 'bye' to end the conversation.")
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        # Check for exit command
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("\nChatbot: Thank you for talking with me. Take care of yourself, and remember that professional help is available if you need it.")
            break
        
        # Process user input and get response
        response = chatbot.process_message(user_input)
        print(f"\nChatbot: {response}")

if __name__ == "__main__":
    main()
