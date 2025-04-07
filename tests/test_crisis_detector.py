"""
Test script for the crisis detection module.

This script tests the crisis detection functionality with sample messages
to ensure proper identification of crisis situations and appropriate responses.
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.crisis_detector import CrisisDetector

# Load environment variables
load_dotenv()

def test_crisis_detector():
    """Test the crisis detection functionality."""
    print("Initializing crisis detector...")
    crisis_detector = CrisisDetector()
    
    # Test messages
    test_messages = [
        "I've been feeling really down lately.",
        "I think I might want to kill myself.",
        "Nothing is working and I can't go on anymore.",
        "I've been having thoughts about hurting myself.",
        "I'm having a hard time but I'm talking to my therapist.",
        "Sometimes I just want to end it all.",
        "I'm feeling anxious about my upcoming exam."
    ]
    
    print("\nTesting crisis detection with sample messages:")
    for message in test_messages:
        print(f"\nMessage: {message}")
        
        # Detect crisis
        is_crisis = crisis_detector.detect_crisis(message)
        print(f"Crisis detected: {is_crisis}")
        
        if is_crisis:
            # Get crisis response
            response = crisis_detector.get_crisis_response()
            print(f"\nCrisis Response:\n{response}")
            
            # Test safety verification
            test_replies = ["Yes, I called them", "No, I don't want to"]
            for reply in test_replies:
                safety_verified = crisis_detector.check_safety_verification(reply)
                print(f"\nUser reply: {reply}")
                print(f"Safety verified: {safety_verified}")
                
                if not safety_verified:
                    verification_msg = crisis_detector.get_safety_verification_message()
                    print(f"Verification message:\n{verification_msg}")
            
            # Reset crisis mode for next test
            crisis_detector.reset_crisis_mode()
    
    print("\nCrisis detector testing completed.")

if __name__ == "__main__":
    test_crisis_detector()
