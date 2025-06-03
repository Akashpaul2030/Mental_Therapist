"""
Knowledge Base Integration Module

This module handles the integration of mental health knowledge resources into a vector database
for efficient retrieval using the RAG approach.

It includes:
- Document loading and text splitting
- Embedding generation
- Vector database creation and management
- Retrieval functionality
"""

import os
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

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

class KnowledgeBase:
    """Class to manage the mental health knowledge base."""
    
    def __init__(self, knowledge_base_dir: str, vector_db_path: str):
        """
        Initialize the knowledge base.
        
        Args:
            knowledge_base_dir: Directory containing knowledge base documents
            vector_db_path: Path to store the vector database
        """
        self.knowledge_base_dir = knowledge_base_dir
        self.vector_db_path = vector_db_path
        self.embeddings = OpenAIEmbeddings(
            model=os.getenv('EMBEDDING_MODEL', 'text-embedding-ada-002')
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.vector_store = None
        
    def load_documents(self) -> List[Document]:
        """
        Load documents from the knowledge base directory.
        
        Returns:
            List of loaded documents
        """
        logger.info(f"Loading documents from {self.knowledge_base_dir}")
        
        try:
            # Load markdown files from the knowledge base directory
            loader = DirectoryLoader(
                self.knowledge_base_dir,
                glob="**/*.md",
                loader_cls=TextLoader
            )
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} documents")
            return documents
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            raise
    
    def process_documents(self, documents: List[Document]) -> List[Document]:
        """
        Process documents by splitting them into chunks.
        
        Args:
            documents: List of documents to process
            
        Returns:
            List of processed document chunks
        """
        logger.info("Processing documents")
        
        try:
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Created {len(chunks)} document chunks")
            return chunks
        except Exception as e:
            logger.error(f"Error processing documents: {e}")
            raise
    
    def create_vector_store(self, documents: List[Document]) -> None:
        """
        Create a vector store from the processed documents.
        
        Args:
            documents: List of processed document chunks
        """
        logger.info("Creating vector store")
        
        try:
            self.vector_store = FAISS.from_documents(
                documents,
                self.embeddings
            )
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.vector_db_path), exist_ok=True)
            # Save the vector store
            self.vector_store.save_local(self.vector_db_path)
            logger.info(f"Vector store created and saved to {self.vector_db_path}")
        except Exception as e:
            logger.error(f"Error creating vector store: {e}")
            raise
    
    def load_vector_store(self) -> bool:
        """
        Load an existing vector store.
        
        Returns:
            True if vector store was loaded successfully, False otherwise
        """
        logger.info(f"Loading vector store from {self.vector_db_path}")
        
        try:
            if os.path.exists(self.vector_db_path):
                self.vector_store = FAISS.load_local(
                    self.vector_db_path,
                    self.embeddings
                )
                logger.info("Vector store loaded successfully")
                return True
            else:
                logger.warning(f"Vector store not found at {self.vector_db_path}")
                return False
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False
    
    def setup(self) -> None:
        """
        Set up the knowledge base by loading documents, processing them,
        and creating a vector store.
        """
        logger.info("Setting up knowledge base")
        
        # Try to load existing vector store
        if not self.load_vector_store():
            # If not found, create a new one
            documents = self.load_documents()
            processed_docs = self.process_documents(documents)
            self.create_vector_store(processed_docs)
    
    def retrieve(self, query: str, k: int = 3) -> List[Document]:
        """
        Retrieve relevant documents for a given query.
        
        Args:
            query: User query
            k: Number of documents to retrieve
            
        Returns:
            List of relevant documents
        """
        logger.info(f"Retrieving documents for query: {query}")
        
        if not self.vector_store:
            if not self.load_vector_store():
                logger.error("Vector store not available")
                raise ValueError("Vector store not available. Run setup() first.")
        
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            logger.info(f"Retrieved {len(docs)} documents")
            return docs
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            raise

def initialize_knowledge_base() -> KnowledgeBase:
    """
    Initialize and set up the knowledge base.
    
    Returns:
        Initialized KnowledgeBase instance
    """
    knowledge_base_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "knowledge_base"
    )
    vector_db_path = os.getenv('VECTOR_DB_PATH', os.path.join(knowledge_base_dir, "vector_store"))
    
    kb = KnowledgeBase(knowledge_base_dir, vector_db_path)
    kb.setup()
    
    return kb