"""
Pinecone Initialization Script for SustainaTrend™ Intelligence Platform

This script creates or connects to the required Pinecone index for the storytelling feature
with the correct dimensionality for OpenAI embeddings.
"""
import os
import logging
from time import sleep
from typing import Optional, Dict, Any, List, Tuple, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("python-dotenv not installed, skipping .env file loading")

# Global constants
PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY', '')
DEFAULT_INDEX_NAME = 'sustainability-storytelling'
DIMENSION = 1536  # OpenAI ada-002 embedding dimension

# Global state
current_index_name = DEFAULT_INDEX_NAME
pinecone_available = False


def initialize_pinecone() -> bool:
    """
    Initialize Pinecone with the required index for sustainability storytelling
    
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    global current_index_name, pinecone_available
    
    if not PINECONE_API_KEY:
        logger.error("PINECONE_API_KEY environment variable not set")
        return False
    
    try:
        # Try with the new SDK first
        try:
            logger.info("Using the latest Pinecone SDK")
            from pinecone import Pinecone, ServerlessSpec
            
            # Initialize Pinecone client
            pc = Pinecone(api_key=PINECONE_API_KEY)
            logger.info("Pinecone client initialized successfully")
            
            # List available indexes
            indexes = pc.list_indexes().names()
            logger.info(f"Available indexes: {indexes}")
            
            # First check if our default index exists
            if DEFAULT_INDEX_NAME in indexes:
                logger.info(f"Index '{DEFAULT_INDEX_NAME}' already exists")
                # Connect to the existing index
                index = pc.Index(DEFAULT_INDEX_NAME)
                stats = index.describe_index_stats()
                logger.info(f"Index stats: {stats}")
                current_index_name = DEFAULT_INDEX_NAME
                pinecone_available = True
                return True
            
            # If no default index, try to use any available index
            if indexes:
                # Use the first available index
                alt_index_name = indexes[0]
                logger.info(f"Using existing index '{alt_index_name}' instead of creating new one")
                
                # Connect to existing index
                try:
                    index = pc.Index(alt_index_name)
                    logger.info(f"Successfully connected to alternative index: {alt_index_name}")
                    # Store index name for later reference
                    current_index_name = alt_index_name
                    pinecone_available = True
                    return True
                except Exception as e:
                    logger.error(f"Error connecting to alternative index: {e}")
            
            # If we got here, we need to create a new index
            # This will only work on paid plans with correct region settings
            try:
                logger.info(f"Creating new index: {DEFAULT_INDEX_NAME}")
                # Use gcp-starter for free tier
                pc.create_index(
                    name=DEFAULT_INDEX_NAME,
                    dimension=DIMENSION,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="gcp", region="us-central1")
                )
                
                logger.info(f"Created new index '{DEFAULT_INDEX_NAME}' with dimension {DIMENSION}")
                
                # Wait for index initialization
                logger.info("Waiting for index initialization...")
                sleep(10)  # Wait for index to initialize
                
                # Connect to the new index
                index = pc.Index(DEFAULT_INDEX_NAME)
                logger.info(f"Connected to new index '{DEFAULT_INDEX_NAME}'")
                current_index_name = DEFAULT_INDEX_NAME
                pinecone_available = True
                return True
            except Exception as e:
                logger.error(f"Error creating new index: {e}")
                logger.warning("Using fallback mode without Pinecone")
                return False
                
        except ImportError:
            # Fallback for older Pinecone SDK version
            logger.warning("Using legacy Pinecone SDK (deprecated)")
            import pinecone
            
            # Initialize with the older API - use gcp-starter for free tier
            pinecone.init(api_key=PINECONE_API_KEY, environment="gcp-starter")
            logger.info("Legacy Pinecone client initialized")
            
            # Check if index exists
            existing_indexes = pinecone.list_indexes()
            logger.info(f"Existing Pinecone indexes: {existing_indexes}")
            
            if DEFAULT_INDEX_NAME in existing_indexes:
                logger.info(f"Index '{DEFAULT_INDEX_NAME}' already exists")
                # Connect to the existing index
                index = pinecone.Index(DEFAULT_INDEX_NAME)
                logger.info(f"Connected to existing index '{DEFAULT_INDEX_NAME}'")
                current_index_name = DEFAULT_INDEX_NAME
                pinecone_available = True
                return True
            
            # Use an existing index if possible
            if existing_indexes:
                # Use the first available index
                alt_index_name = existing_indexes[0]
                logger.info(f"Using existing index '{alt_index_name}' instead of creating new one")
                
                # Connect to existing index
                try:
                    index = pinecone.Index(alt_index_name)
                    logger.info(f"Successfully connected to alternative index: {alt_index_name}")
                    current_index_name = alt_index_name
                    pinecone_available = True
                    return True
                except Exception as e:
                    logger.error(f"Error connecting to alternative index: {e}")
            
            # If we get here, try to create a new index
            try:
                pinecone.create_index(
                    name=DEFAULT_INDEX_NAME,
                    dimension=DIMENSION,
                    metric="cosine"
                )
                logger.info(f"Created new index '{DEFAULT_INDEX_NAME}' with dimension {DIMENSION}")
                
                # Wait for index initialization
                logger.info("Waiting for index initialization...")
                sleep(10)
                
                # Connect to the new index
                index = pinecone.Index(DEFAULT_INDEX_NAME)
                logger.info(f"Connected to new index '{DEFAULT_INDEX_NAME}'")
                current_index_name = DEFAULT_INDEX_NAME
                pinecone_available = True
                return True
            except Exception as e:
                logger.error(f"Error creating new index: {e}")
                logger.warning("Using fallback mode without Pinecone")
                return False
            
    except Exception as e:
        logger.error(f"Error initializing Pinecone: {e}")
        return False


def test_pinecone_connection() -> bool:
    """
    Test Pinecone connection and index availability
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    global current_index_name, pinecone_available
    
    if not PINECONE_API_KEY:
        logger.error("PINECONE_API_KEY environment variable not set")
        return False
    
    try:
        # Try with the new SDK first
        try:
            from pinecone import Pinecone
            
            # Initialize Pinecone client
            pc = Pinecone(api_key=PINECONE_API_KEY)
            logger.info("Pinecone client initialized successfully")
            
            # List available indexes
            indexes = pc.list_indexes().names()
            logger.info(f"Available indexes: {indexes}")
            
            if current_index_name in indexes:
                # Connect to the index
                index = pc.Index(current_index_name)
                stats = index.describe_index_stats()
                logger.info(f"Index stats: {stats}")
                logger.info("Pinecone connectivity test: SUCCESS")
                pinecone_available = True
                return True
            elif indexes:
                # Use first available index
                alt_index_name = indexes[0]
                logger.info(f"Current index not found, using '{alt_index_name}' instead")
                index = pc.Index(alt_index_name)
                stats = index.describe_index_stats()
                logger.info(f"Index stats for '{alt_index_name}': {stats}")
                current_index_name = alt_index_name
                pinecone_available = True
                return True
            else:
                logger.error("No indexes found. Using fallback mode.")
                return False
                
        except ImportError:
            # Fallback to older SDK
            logger.warning("Using legacy Pinecone SDK for testing")
            import pinecone
            
            # Initialize with older API
            pinecone.init(api_key=PINECONE_API_KEY, environment="gcp-starter")
            logger.info("Legacy Pinecone client initialized for testing")
            
            # List available indexes
            indexes = pinecone.list_indexes()
            logger.info(f"Available indexes: {indexes}")
            
            if current_index_name in indexes:
                # Connect to the index
                index = pinecone.Index(current_index_name)
                stats = index.describe_index_stats()
                logger.info(f"Index stats: {stats}")
                logger.info("Pinecone connectivity test: SUCCESS")
                pinecone_available = True
                return True
            elif indexes:
                # Use first available index
                alt_index_name = indexes[0]
                logger.info(f"Current index not found, using '{alt_index_name}' instead")
                index = pinecone.Index(alt_index_name)
                stats = index.describe_index_stats()
                logger.info(f"Index stats for '{alt_index_name}': {stats}")
                current_index_name = alt_index_name
                pinecone_available = True
                return True
            else:
                logger.error("No indexes found. Using fallback mode.")
                return False
                
    except Exception as e:
        logger.error(f"Error testing Pinecone connection: {e}")
        return False


def get_index_name() -> str:
    """Get the name of the current Pinecone index"""
    return current_index_name


def is_pinecone_available() -> bool:
    """Check if Pinecone is available"""
    return pinecone_available


if __name__ == "__main__":
    if not PINECONE_API_KEY:
        logger.error("PINECONE_API_KEY environment variable not set")
        print("ERROR: PINECONE_API_KEY environment variable not set. Please set it in your .env file")
        exit(1)
    
    logger.info("Starting Pinecone initialization...")
    success = initialize_pinecone()
    
    if success:
        logger.info("Pinecone initialization completed successfully")
        print(f"SUCCESS: Pinecone index '{current_index_name}' initialized successfully")
        
        # Test the connection
        test_success = test_pinecone_connection()
        if test_success:
            print("CONNECTIVITY TEST: Pinecone index is available and ready to use")
        else:
            print("CONNECTIVITY TEST FAILED: Please check the logs for details")
    else:
        logger.error("Pinecone initialization failed")
        print("ERROR: Pinecone initialization failed. Please check the logs for details")
        print("\nLATENT CONCEPT MODEL STATUS:")
        print("- Using fallback mode for Sustainability Storytelling")
        print("- Story generation will work but without vector-based semantic understanding")
        print("- To enable full LCM capabilities, please check the logs for errors")
        print("="*80)