"""
Test file to check Pinecone import capabilities
"""
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_pinecone_v2():
    """Test Pinecone V2 API import"""
    try:
        import pinecone
        logger.info("Successfully imported Pinecone V2 API")
        return True
    except ImportError as e:
        logger.error(f"Failed to import Pinecone V2 API: {str(e)}")
        return False

def test_pinecone_v3():
    """Test Pinecone V3 API import"""
    try:
        from pinecone import Pinecone
        logger.info("Successfully imported Pinecone V3 API")
        return True
    except ImportError as e:
        logger.error(f"Failed to import Pinecone V3 API: {str(e)}")
        return False

def test_pinecone_connection():
    """Test Pinecone connection"""
    api_key = os.getenv("PINECONE_API_KEY")
    
    if not api_key:
        logger.warning("No Pinecone API key found in environment")
        return False
        
    # First try V3 API
    try:
        from pinecone import Pinecone
        pc = Pinecone(api_key=api_key)
        indexes = pc.list_indexes()
        logger.info(f"Successfully connected to Pinecone using V3 API. Indexes: {[idx.name for idx in indexes]}")
        return True
    except Exception as e1:
        logger.warning(f"Failed to connect using Pinecone V3 API: {str(e1)}")
        
        # Try V2 API
        try:
            import pinecone
            pinecone.init(api_key=api_key, environment="us-east-1")
            indexes = pinecone.list_indexes()
            logger.info(f"Successfully connected to Pinecone using V2 API. Indexes: {indexes}")
            return True
        except Exception as e2:
            logger.error(f"Failed to connect using Pinecone V2 API: {str(e2)}")
            return False

if __name__ == "__main__":
    logger.info("Testing Pinecone library imports...")
    v2_result = test_pinecone_v2()
    v3_result = test_pinecone_v3()
    
    if v2_result and v3_result:
        logger.info("Both Pinecone V2 and V3 APIs available!")
    elif v2_result:
        logger.info("Only Pinecone V2 API available")
    elif v3_result:
        logger.info("Only Pinecone V3 API available")
    else:
        logger.error("No Pinecone APIs available")
    
    # Test connection if API key exists
    if os.getenv("PINECONE_API_KEY"):
        connection_result = test_pinecone_connection()
        if connection_result:
            logger.info("Successfully connected to Pinecone!")
        else:
            logger.error("Failed to connect to Pinecone")
    else:
        logger.warning("Skipping connection test due to missing API key")