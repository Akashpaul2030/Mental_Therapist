"""
Script to test the knowledge base integration functionality.

This script initializes the knowledge base and tests the retrieval functionality
with sample queries to ensure the vector database is working properly.
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path to import the knowledge_base module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.knowledge_base import initialize_knowledge_base

# Load environment variables
load_dotenv()

def test_knowledge_base():
    """Test the knowledge base retrieval functionality."""
    print("Initializing knowledge base...")
    kb = initialize_knowledge_base()
    
    # Test queries
    test_queries = [
        "What is anxiety and how can I manage it?",
        "Can you suggest some CBT exercises for depression?",
        "What should I do if someone is having suicidal thoughts?",
        "How can I improve my sleep quality?",
        "What are some grounding techniques for panic attacks?"
    ]
    
    print("\nTesting retrieval functionality with sample queries:")
    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            docs = kb.retrieve(query, k=2)
            print(f"Retrieved {len(docs)} documents")
            for i, doc in enumerate(docs):
                print(f"\nDocument {i+1}:")
                print(f"Source: {doc.metadata.get('source', 'Unknown')}")
                print(f"Content: {doc.page_content[:200]}...")
        except Exception as e:
            print(f"Error retrieving documents: {e}")
    
    print("\nKnowledge base testing completed.")

if __name__ == "__main__":
    test_knowledge_base()
