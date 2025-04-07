"""
Test script for the ethical guidelines module.

This script tests the ethical guidelines functionality including
disclaimer system, medical advice redirection, and content moderation.
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ethical_guidelines import EthicalGuidelines

# Load environment variables
load_dotenv()

def test_ethical_guidelines():
    """Test the ethical guidelines functionality."""
    print("Initializing ethical guidelines module...")
    ethics = EthicalGuidelines()
    
    # Test disclaimers
    print("\nTesting disclaimer system:")
    initial_disclaimer = ethics.get_initial_disclaimer()
    print(f"Initial Disclaimer:\n{initial_disclaimer}")
    
    session_disclaimer = ethics.get_session_disclaimer()
    print(f"\nSession Disclaimer:\n{session_disclaimer}")
    
    # Test medical advice detection
    print("\nTesting medical advice detection:")
    test_messages = [
        "Can you diagnose my depression?",
        "What medication should I take for anxiety?",
        "Is it normal to feel this way?",
        "Do I have bipolar disorder based on these symptoms?",
        "I've been feeling sad lately.",
        "What are some coping strategies for stress?"
    ]
    
    for message in test_messages:
        is_medical_advice = ethics.check_medical_advice_request(message)
        print(f"\nMessage: {message}")
        print(f"Medical advice request: {is_medical_advice}")
        
        if is_medical_advice:
            redirection = ethics.get_medical_advice_redirection()
            print(f"Redirection:\n{redirection}")
    
    # Test content moderation
    print("\nTesting content moderation:")
    test_contents = [
        "I've been feeling anxious about my upcoming exam.",
        "I want to hurt someone who bullied me.",
        "How can I practice mindfulness meditation?",
        "I hate myself and want to die."
    ]
    
    for content in test_contents:
        is_flagged, result = ethics.moderate_content(content)
        print(f"\nContent: {content}")
        print(f"Flagged: {is_flagged}")
        
        if is_flagged:
            moderation_response = ethics.get_moderation_response(result)
            print(f"Moderation Response:\n{moderation_response}")
    
    print("\nEthical guidelines testing completed.")

if __name__ == "__main__":
    test_ethical_guidelines()
