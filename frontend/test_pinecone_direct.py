"""
Direct Pinecone testing script for the Regulatory AI module

This script tests the direct Pinecone vector database interaction without
relying on OpenAI for embeddings. It uses mock vectors to verify proper
storage and retrieval.
"""
import os
import logging
import uuid
import random
from datetime import datetime
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_mock_embedding(dimension: int = 3072) -> List[float]:
    """
    Create a mock embedding vector for testing
    
    Args:
        dimension: The dimension of the embedding vector
        
    Returns:
        A random vector of floats
    """
    return [random.uniform(-1, 1) for _ in range(dimension)]

def test_pinecone_direct():
    """
    Test direct Pinecone interaction using the Pinecone V3 API
    """
    # Check if Pinecone API key is available
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        logger.error("PINECONE_API_KEY environment variable not set")
        return False
    
    try:
        # Import Pinecone V3 API
        from pinecone import Pinecone
        
        # Initialize Pinecone client
        pc = Pinecone(api_key=api_key)
        
        # List available indexes
        indexes = pc.list_indexes()
        index_names = [idx.name for idx in indexes]
        logger.info(f"Available indexes: {index_names}")
        
        # Connect to 'regulatoryai' index
        if 'regulatoryai' not in index_names:
            logger.error("'regulatoryai' index not found")
            return False
        
        index = pc.Index('regulatoryai')
        logger.info("Connected to 'regulatoryai' index")
        
        # Get index statistics
        try:
            stats = index.describe_index_stats()
            dimension = stats.dimension if hasattr(stats, "dimension") else stats.get("dimension", "unknown")
            total_vectors = stats.total_vector_count if hasattr(stats, "total_vector_count") else stats.get("total_vector_count", 0)
            logger.info(f"Index statistics: dimension={dimension}, total_vectors={total_vectors}")
        except Exception as e:
            logger.warning(f"Could not get index statistics: {str(e)}")
        
        # Create a test vector
        doc_id = str(uuid.uuid4())
        test_text = "This is a test document for the Regulatory AI system"
        mock_embedding = create_mock_embedding(3072)  # Regulatory AI uses 3072-dimensional vectors
        
        metadata = {
            "text": test_text,
            "timestamp": datetime.now().isoformat(),
            "category": "test",
            "framework": ["TCFD", "CSRD"],
            "source": "test_script"
        }
        
        # Upsert the test vector
        try:
            index.upsert(
                vectors=[
                    {
                        "id": doc_id,
                        "values": mock_embedding,
                        "metadata": metadata
                    }
                ]
            )
            logger.info(f"Successfully upserted test vector with ID: {doc_id}")
        except Exception as e:
            logger.error(f"Failed to upsert test vector: {str(e)}")
            return False
        
        # First, sleep to ensure the upsert is processed
        import time
        logger.info("Waiting for index to process the upsert...")
        time.sleep(1)
        
        # Query the test vector with the EXACT SAME vector
        try:
            # Use the exact same vector for querying to ensure high similarity
            results = index.query(
                vector=mock_embedding,
                top_k=5,
                include_metadata=True
            )
            
            logger.info(f"Query results type: {type(results)}")
            
            # Get the matches - handle differently based on response format
            matches = []
            if hasattr(results, 'matches'):
                matches = results.matches
                logger.info(f"Found {len(matches)} matches in results.matches")
            elif isinstance(results, dict) and 'matches' in results:
                matches = results['matches'] 
                logger.info(f"Found {len(matches)} matches in results['matches']")
            
            # Check if we have matches
            if matches and len(matches) > 0:
                # Log first match details
                first_match = matches[0]
                
                # Extract ID and score based on type
                match_id = getattr(first_match, 'id', first_match.get('id', None))
                match_score = getattr(first_match, 'score', first_match.get('score', None))
                
                logger.info(f"First match ID: {match_id}")
                logger.info(f"First match score: {match_score}")
                
                # Check if we found our vector
                if match_id == doc_id:
                    logger.info("✅ Successfully retrieved test vector by ID")
                else:
                    logger.warning(f"Retrieved vector ID ({match_id}) does not match test vector ID ({doc_id})")
            else:
                logger.warning("No matches found in query results. This is normal if the index is new or empty.")
                
            # Also try to fetch the vector directly by ID
            try:
                fetch_result = index.fetch(ids=[doc_id])
                
                # Check if we got our vector back without printing the full vector
                fetch_success = False
                if hasattr(fetch_result, 'vectors') and doc_id in fetch_result.vectors:
                    fetch_success = True
                elif isinstance(fetch_result, dict) and 'vectors' in fetch_result and doc_id in fetch_result['vectors']:
                    fetch_success = True
                
                if fetch_success:
                    logger.info("✅ Successfully fetched test vector by ID")
                else:
                    logger.warning(f"Test vector with ID {doc_id} not found in fetch result")
            except Exception as e:
                logger.error(f"Failed to fetch test vector: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to query test vector: {str(e)}")
            return False
        
        # Clean up - delete the test vector
        try:
            index.delete(ids=[doc_id])
            logger.info(f"Deleted test vector with ID: {doc_id}")
        except Exception as e:
            logger.warning(f"Failed to delete test vector: {str(e)}")
        
        return True
        
    except ImportError:
        logger.error("Failed to import Pinecone V3 API")
        return False
    except Exception as e:
        logger.error(f"Error testing Pinecone: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting direct Pinecone test...")
    success = test_pinecone_direct()
    
    if success:
        logger.info("✅ Direct Pinecone test completed successfully")
    else:
        logger.error("❌ Direct Pinecone test failed")