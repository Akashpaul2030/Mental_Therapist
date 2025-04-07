"""
Test script for the response generation module.

This script tests the response generation functionality with sample queries
and retrieved documents to ensure responses are empathetic and factually accurate.
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.knowledge_base import initialize_knowledge_base
from src.response_generator import ResponseGenerator

# Load environment variables
load_dotenv()

def test_response_generator():
    """Test the response generation functionality."""
    print("Initializing knowledge base...")
    kb = initialize_knowledge_base()
    
    print("Initializing response generator...")
    response_gen = ResponseGenerator()
    
    # Test queries
    test_queries = [
        "I've been feeling really anxious lately and can't sleep. What can I do?",
        "I think I might have depression. Can you diagnose me?",
        "My friend mentioned they're having thoughts about suicide. How can I help them?",
        "What are some CBT techniques I can use for negative thoughts?",
        "I don't know what to do anymore, nothing seems to help."
    ]
    
    print("\nTesting response generation with sample queries:")
    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            # Retrieve relevant documents
            docs = kb.retrieve(query, k=3)
            print(f"Retrieved {len(docs)} documents")
            
            # Generate response
            response = response_gen.generate_response(query, docs)
            print(f"\nGenerated Response:\n{response}")
            
            # Print disclaimer
            print(f"\nDisclaimer:\n{response_gen.get_disclaimer()}")
            
        except Exception as e:
            print(f"Error generating response: {e}")
    
    print("\nResponse generator testing completed.")

if __name__ == "__main__":
    test_response_generator()
