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
        # Using pinecone-client v2.2.4 for compatibility
        logger.info("Initializing Pinecone with v2.2.4")
        import pinecone
        
        # Initialize with pinecone-client API
        try:
            # Simple initialization with API key only (let Pinecone determine the best environment)
            pinecone.init(api_key=PINECONE_API_KEY)
            logger.info("Pinecone client initialized successfully with v2.2.4")
            
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
            
    except Exception as e:
        logger.error(f"Error importing Pinecone: {e}")
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
        # Using pinecone-client v2.2.4 for compatibility
        logger.info("Testing Pinecone connection with v2.2.4")
        import pinecone
        
        try:
            # Simple initialization with API key only (let Pinecone determine the best environment)
            pinecone.init(api_key=PINECONE_API_KEY)
            logger.info("Pinecone client initialized successfully for testing")
            
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
            
    except Exception as e:
        logger.error(f"Error importing Pinecone for testing: {e}")
        return False


def get_index_name() -> str:
    """Get the name of the current Pinecone index"""
    return current_index_name


def is_pinecone_available() -> bool:
    """
    Check if Pinecone is available
    
    This method first checks the global flag, and then attempts a connection
    test if the flag is False. This provides a more reliable check, especially
    in environments with intermittent connectivity.
    
    Returns:
        bool: True if Pinecone is available, False otherwise
    """
    global pinecone_available
    
    # First, check our cached status
    if pinecone_available:
        return True
        
    # If not available, attempt a lightweight test
    if PINECONE_API_KEY:
        try:
            import pinecone
            
            try:
                # Simple initialization with minimal overhead
                pinecone.init(api_key=PINECONE_API_KEY)
                
                # Just try to list indexes - don't need to actually connect
                try:
                    pinecone.list_indexes()
                    # If we get here, connectivity is working
                    pinecone_available = True
                    return True
                except Exception:
                    # Network connectivity issue with Pinecone API
                    return False
                    
            except Exception:
                # Error during initialization
                return False
                
        except ImportError:
            # Pinecone library not available
            return False
    
    # No API key
    return False


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