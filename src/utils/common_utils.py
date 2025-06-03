"""
Common utility functions for the chatbot.
"""

def get_greeting(user_id: str = None) -> str:
    """
    Returns a generic greeting message.
    Optionally, could be personalized if user_id is known and details are available.
    """
    if user_id:
        # Placeholder for potential personalized greeting in the future
        # For now, returns a generic greeting even with user_id
        return "Hello! I'm Mindful Companion, your personal AI assistant for mental well-being. How can I support you today?"
    return "Hello! I'm Mindful Companion, your personal AI assistant for mental well-being. How can I help you?"

# Example of another utility function that might exist here:
# import re
# def sanitize_input(text: str) -> str:
#     """Removes potentially harmful characters or patterns from input text."""
#     # Add actual sanitization logic here if needed
#     return re.sub(r'[^a-zA-Z0-9\s,.!?-]', '', text) 