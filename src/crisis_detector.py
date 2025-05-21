"""
Crisis Detection Module

This module handles the detection and response to crisis situations in user messages,
such as mentions of suicide, self-harm, or other urgent mental health concerns.

It includes:
- Keyword detection for crisis situations
- Crisis response templates
- Safety verification mechanisms
"""

import os
import re
import logging
from typing import Dict, Tuple, List
from dotenv import load_dotenv

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

# Crisis keywords from environment variables or default list
DEFAULT_CRISIS_KEYWORDS = "suicide,self-harm,kill myself,end my life,can't go on,want to die,hurt myself"
CRISIS_KEYWORDS = os.getenv('CRISIS_KEYWORDS', DEFAULT_CRISIS_KEYWORDS).split(',')

# Crisis hotlines by country
CRISIS_HOTLINES = {
    "US": {
        "name": "National Suicide Prevention Lifeline",
        "number": "988 or 1-800-273-8255",
        "text": "Text HOME to 741741",
        "website": "https://988lifeline.org/"
    },
    "UK": {
        "name": "Samaritans",
        "number": "116 123",
        "text": "Text SHOUT to 85258",
        "website": "https://www.samaritans.org/"
    },
    "Canada": {
        "name": "Canada Suicide Prevention Service",
        "number": "1-833-456-4566",
        "text": "Text HOME to 686868",
        "website": "https://www.crisisservicescanada.ca/"
    },
    "Australia": {
        "name": "Lifeline Australia",
        "number": "13 11 14",
        "text": "Text 0477 13 11 14",
        "website": "https://www.lifeline.org.au/"
    },
    "International": {
        "name": "International Association for Suicide Prevention",
        "website": "https://www.iasp.info/resources/Crisis_Centres/"
    }
}

# Default country for crisis hotlines
DEFAULT_COUNTRY = "US"

# Crisis response templates
CRISIS_RESPONSE_TEMPLATE = """
I'm deeply concerned about what you've shared. Your life matters, and I strongly urge you to reach out for immediate support.

Please contact {hotline_name} right now at {hotline_number}.
{text_line}

This is a serious situation that requires professional support. These trained counselors are available 24/7 and can provide immediate help.

Would you be willing to reach out to them? Your safety is the top priority right now.
"""

SAFETY_VERIFICATION_MESSAGE = """
I want to check in with you. Have you contacted the crisis hotline or spoken with a mental health professional? 
Your wellbeing is important, and I want to make sure you're getting the support you need.
"""

class CrisisDetector:
    """Class to detect and respond to crisis situations."""
    
    def __init__(self, country: str = DEFAULT_COUNTRY):
        """
        Initialize the crisis detector.
        
        Args:
            country: Country code for crisis hotlines
        """
        self.country = country
        self.crisis_keywords = [keyword.strip().lower() for keyword in CRISIS_KEYWORDS]
        self.in_crisis_mode = False
        self.safety_verified = False
        
    def detect_crisis(self, message: str) -> bool:
        """
        Detect if a message contains crisis keywords.
        
        Args:
            message: User message
            
        Returns:
            True if crisis is detected, False otherwise
        """
        message_lower = message.lower()
        
        # Skip very short messages to avoid false positives
        if len(message_lower.split()) < 3:
            return False
            
        # Define different levels of crisis keywords
        severe_keywords = [
            "suicide", "kill myself", "end my life", "want to die",
            "going to kill myself", "planning to end it", "taking my life",
            "don't want to live", "better off dead", "no reason to live"
        ]
        
        moderate_keywords = [
            "self-harm", "hurt myself", "can't go on", "hopeless",
            "worthless", "no hope", "no future", "too much pain",
            "can't take it", "don't want to be here"
        ]
        
        # Negation words to avoid false positives
        negation_words = ["not", "don't", "never", "no", "won't", "wouldn't", "shouldn't"]
        
        # Check for severe keywords - immediate crisis detection
        for keyword in severe_keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, message_lower):
                # Check for negation before the keyword
                words_before = message_lower[:message_lower.find(keyword)].split()
                if not any(neg in words_before[-3:] for neg in negation_words):
                    logger.warning(f"Severe crisis keyword detected: {keyword}")
                    self.in_crisis_mode = True
                    return True
        
        # For moderate keywords, require more context or multiple matches
        moderate_matches = 0
        for keyword in moderate_keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, message_lower):
                # Check for negation before the keyword
                words_before = message_lower[:message_lower.find(keyword)].split()
                if not any(neg in words_before[-3:] for neg in negation_words):
                    moderate_matches += 1
        
        # Only trigger crisis mode if multiple moderate keywords are found
        # or if a moderate keyword appears with strong emotional context
        emotional_context = any(word in message_lower for word in ["really", "so", "very", "extremely", "absolutely"])
        if moderate_matches >= 2 or (moderate_matches >= 1 and emotional_context):
            logger.warning(f"Multiple moderate crisis keywords detected")
            self.in_crisis_mode = True
            return True
        
        return False
    
    def get_crisis_response(self) -> str:
        """
        Get the appropriate crisis response.
        
        Returns:
            Crisis response message
        """
        hotline = CRISIS_HOTLINES.get(self.country, CRISIS_HOTLINES["International"])
        
        # Format the crisis response
        text_line = f"You can also {hotline.get('text', '')}." if hotline.get('text') else ""
        response = CRISIS_RESPONSE_TEMPLATE.format(
            hotline_name=hotline["name"],
            hotline_number=hotline.get("number", ""),
            text_line=text_line
        )
        
        # Add website information
        if hotline.get("website"):
            response += f"\nAdditional resources are available at: {hotline['website']}"
        
        return response
    
    def check_safety_verification(self, message: str) -> bool:
        """
        Check if the user has verified their safety.
        
        Args:
            message: User message
            
        Returns:
            True if safety is verified, False otherwise
        """
        if not self.in_crisis_mode:
            return True
        
        # Look for positive confirmation keywords
        positive_keywords = ["yes", "called", "contacted", "talked", "speaking", "safe", "better", "okay", "ok"]
        message_lower = message.lower()
        
        for keyword in positive_keywords:
            if keyword in message_lower:
                logger.info("User has indicated safety verification")
                self.safety_verified = True
                self.in_crisis_mode = False
                return True
        
        return False
    
    def get_safety_verification_message(self) -> str:
        """
        Get the safety verification message.
        
        Returns:
            Safety verification message
        """
        return SAFETY_VERIFICATION_MESSAGE
    
    def reset_crisis_mode(self) -> None:
        """Reset the crisis mode."""
        self.in_crisis_mode = False
        self.safety_verified = False