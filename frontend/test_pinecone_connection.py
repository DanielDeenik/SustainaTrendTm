"""
Test Pinecone connection for SustainaTrend™ Intelligence Platform

This script tests the connection to Pinecone and verifies that the API key is working correctly.
It uses the Pinecone v2.2.4 client which is already installed.
"""
import os
import logging
import sys
from time import sleep
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get Pinecone API key from environment
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "regulatoryai")

if not PINECONE_API_KEY:
    logger.error("PINECONE_API_KEY environment variable not set")
    sys.exit(1)

def test_pinecone_connection():
    """Test connection to Pinecone using v2.2.4 client"""
    try:
        logger.info("Importing Pinecone client (v2.2.4)...")
        import pinecone
        
        logger.info(f"Using Pinecone version: {pinecone.__version__}")
        
        logger.info("Initializing Pinecone client...")
        pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
        
        # List all indexes to verify connection
        logger.info("Listing all indexes...")
        indexes = pinecone.list_indexes()
        logger.info(f"Available indexes: {indexes}")
        
        # Check if our target index exists
        if not indexes:
            logger.info(f"No indexes found. Creating new '{PINECONE_INDEX_NAME}' index...")
            # Create the index if it doesn't exist
            pinecone.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=3072,  # For OpenAI embeddings
                metric="cosine"
            )
            logger.info(f"Created new index '{PINECONE_INDEX_NAME}'")
            logger.info("Waiting for index to initialize...")
            sleep(10)  # Wait for index to initialize
        elif PINECONE_INDEX_NAME not in indexes:
            logger.info(f"Index '{PINECONE_INDEX_NAME}' not found. Creating it...")
            # Create the index if it doesn't exist
            pinecone.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=3072,  # For OpenAI embeddings
                metric="cosine"
            )
            logger.info(f"Created new index '{PINECONE_INDEX_NAME}'")
            logger.info("Waiting for index to initialize...")
            sleep(10)  # Wait for index to initialize
        else:
            logger.info(f"Index '{PINECONE_INDEX_NAME}' already exists")
        
        # Connect to the index
        logger.info(f"Connecting to index '{PINECONE_INDEX_NAME}'...")
        index = pinecone.Index(PINECONE_INDEX_NAME)
        
        # Get index stats
        logger.info("Getting index stats...")
        stats = index.describe_index_stats()
        logger.info(f"Index stats: {stats}")
        
        # Test vector operations using the example from docs
        logger.info("Testing vector operations...")
        
        # Test upsert
        test_vectors = [
            {
                "id": "test_vec1",
                "values": [0.1] * 3072,  # Create a vector of appropriate dimension
                "metadata": {"source": "test", "type": "regulatory_document"}
            }
        ]
        
        # Upsert the test vector
        logger.info("Upserting test vector...")
        upsert_response = index.upsert(vectors=test_vectors, namespace="test")
        logger.info(f"Upsert response: {upsert_response}")
        
        # Query the test vector
        logger.info("Querying test vector...")
        query_response = index.query(
            namespace="test",
            vector=[0.1] * 3072,
            top_k=1,
            include_values=True,
            include_metadata=True
        )
        logger.info(f"Query response: {query_response}")
        
        # Delete the test vector
        logger.info("Cleaning up test vector...")
        index.delete(ids=["test_vec1"], namespace="test")
        
        logger.info("Pinecone connection test completed successfully!")
        return True
        
    except ImportError as e:
        logger.error(f"Failed to import Pinecone: {e}")
        return False
    except Exception as e:
        logger.error(f"Error testing Pinecone connection: {e}")
        logger.error(f"Stack trace: {sys.exc_info()}")
        return False

if __name__ == "__main__":
    success = test_pinecone_connection()
    if success:
        logger.info("Pinecone connection test PASSED!")
        sys.exit(0)
    else:
        logger.error("Pinecone connection test FAILED!")
        sys.exit(1)