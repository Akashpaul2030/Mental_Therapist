"""
Ethical Guidelines Module

This module implements ethical guidelines for the mental health chatbot,
including disclaimer system, medical advice redirection, and content moderation.

It includes:
- Disclaimer system for conversation start
- Medical advice redirection
- Integration with OpenAI's Moderation API for content filtering
"""

import os
import logging
import openai
from typing import Dict, Tuple, Any
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

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Disclaimer templates
INITIAL_DISCLAIMER = """
IMPORTANT: I'm an AI chatbot designed to provide general mental health support and information. 
I am not a substitute for professional mental health care. For urgent issues, please contact 
a licensed therapist, counselor, or crisis hotline.

How can I support you today?
"""

SESSION_DISCLAIMER = """
Note: I'm an AI here to provide general support, not a substitute for professional care. 
For urgent issues, please contact a licensed therapist or crisis hotline.
"""

# Medical advice redirection template
MEDICAL_ADVICE_REDIRECTION = """
I'm not qualified to provide medical advice, diagnose conditions, or prescribe treatments. 
For medical concerns, please consult with a healthcare provider who can give you proper 
evaluation and treatment options.

I can still provide general information about mental health topics and coping strategies 
if that would be helpful.
"""

class EthicalGuidelines:
    """Class to implement ethical guidelines for the mental health chatbot."""
    
    def __init__(self):
        """Initialize the ethical guidelines module."""
        self.disclaimer_shown = False
        
    def get_initial_disclaimer(self) -> str:
        """
        Get the initial disclaimer to show at the start of a conversation.
        
        Returns:
            Initial disclaimer string
        """
        self.disclaimer_shown = True
        return INITIAL_DISCLAIMER
    
    def get_session_disclaimer(self) -> str:
        """
        Get the session disclaimer to include in responses.
        
        Returns:
            Session disclaimer string
        """
        return SESSION_DISCLAIMER
    
    def check_medical_advice_request(self, message: str) -> bool:
        """
        Check if a message is requesting medical advice.
        
        Args:
            message: User message
            
        Returns:
            True if the message is requesting medical advice, False otherwise
        """
        medical_keywords = [
            "diagnose", "diagnosis", "medication", "prescribe", "treatment",
            "cure", "heal", "drug", "dosage", "side effect", "symptom",
            "is it normal", "do I have", "should I take", "what medicine"
        ]
        
        message_lower = message.lower()
        for keyword in medical_keywords:
            if keyword in message_lower:
                logger.info(f"Medical advice request detected: {keyword}")
                return True
        
        return False
    
    def get_medical_advice_redirection(self) -> str:
        """
        Get the medical advice redirection message.
        
        Returns:
            Medical advice redirection message
        """
        return MEDICAL_ADVICE_REDIRECTION
    
    def moderate_content(self, content: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Moderate content using OpenAI's Moderation API.
        
        Args:
            content: Content to moderate
            
        Returns:
            Tuple of (is_flagged, moderation_result)
        """
        try:
            response = openai.Moderation.create(input=content)
            result = response["results"][0]
            is_flagged = result["flagged"]
            
            if is_flagged:
                logger.warning(f"Content flagged by moderation API: {result['categories']}")
                
            return is_flagged, result
        except Exception as e:
            logger.error(f"Error moderating content: {e}")
            # Default to not flagged if API call fails
            return False, {}
    
    def get_moderation_response(self, result: Dict[str, Any]) -> str:
        """
        Get a response for moderated content.
        
        Args:
            result: Moderation result
            
        Returns:
            Moderation response message
        """
        categories = []
        for category, flagged in result.get("categories", {}).items():
            if flagged:
                categories.append(category)
        
        category_str = ", ".join(categories)
        
        return f"""
        I'm unable to respond to this message as it contains content that may violate ethical guidelines 
        ({category_str}). As a mental health support chatbot, I'm designed to provide helpful and 
        supportive information in a safe manner.
        
        Please rephrase your message or ask a different question, and I'll be happy to assist you.
        """