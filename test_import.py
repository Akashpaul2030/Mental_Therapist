# D:\0000000001.Mental_Health\Manus AI\mental_health_chatbot\test_import.py

import sys
import os

# Print the current working directory and Python path
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Check if the src directory is accessible
src_path = os.path.join(os.getcwd(), 'src')
print(f"Does src directory exist? {os.path.exists(src_path)}")

# Try to list files in the src directory
if os.path.exists(src_path):
    print(f"Files in src directory: {os.listdir(src_path)}")

# Try to import the memory store first (simpler module)
try:
    from src.memory_store import ConversationMemory
    print("Successfully imported ConversationMemory")
except ImportError as e:
    print(f"Error importing ConversationMemory: {e}")

# Try importing each component separately
try:
    from src.knowledge_base import initialize_knowledge_base
    print("Successfully imported initialize_knowledge_base")
except ImportError as e:
    print(f"Error importing initialize_knowledge_base: {e}")

try:
    from src.response_generator import ResponseGenerator
    print("Successfully imported ResponseGenerator")
except ImportError as e:
    print(f"Error importing ResponseGenerator: {e}")

try:
    from src.crisis_detector import CrisisDetector
    print("Successfully imported CrisisDetector")
except ImportError as e:
    print(f"Error importing CrisisDetector: {e}")

try:
    from src.ethical_guidelines import EthicalGuidelines
    print("Successfully imported EthicalGuidelines")
except ImportError as e:
    print(f"Error importing EthicalGuidelines: {e}")