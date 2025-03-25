"""
Initialize Pinecone for the RegulatoryAI module

This script initializes the Pinecone connection for the RegulatoryAI module.
It creates the necessary index if it doesn't exist.
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to sys.path for proper imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def initialize_pinecone():
    """Initialize Pinecone for the RegulatoryAI module"""
    try:
        # Import the initialize_pinecone function
        from frontend.initialize_pinecone import initialize_pinecone as init_pinecone
        from frontend.initialize_pinecone import test_pinecone_connection, is_pinecone_available
        
        # Initialize Pinecone
        logger.info("Initializing Pinecone...")
        success = init_pinecone()
        
        if success:
            logger.info("Pinecone successfully initialized!")
            # Test the connection
            connection_status = test_pinecone_connection()
            logger.info(f"Pinecone connection test: {'Success' if connection_status else 'Failed'}")
            
            # Check if Pinecone is available
            available = is_pinecone_available()
            logger.info(f"Pinecone availability: {'Available' if available else 'Not available'}")
            
            return success and connection_status and available
        else:
            logger.error("Failed to initialize Pinecone")
            return False
            
    except ImportError as e:
        logger.error(f"Failed to import Pinecone initialization functions: {e}")
        return False
    except Exception as e:
        logger.error(f"An error occurred during Pinecone initialization: {e}")
        return False

if __name__ == "__main__":
    initialize_pinecone()