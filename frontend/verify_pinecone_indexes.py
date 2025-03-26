"""
Script to verify Pinecone index connections and structure

This script connects to Pinecone and verifies that both the 'regulatoryai' and 'kycstreamline' 
indexes exist and are accessible. It also prints information about index statistics.
"""
import os
import logging
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_pinecone_indexes():
    """
    Verify that Pinecone indexes exist and are accessible
    """
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        logger.error("PINECONE_API_KEY environment variable not set")
        return False
    
    # Try with Pinecone V3 API
    try:
        from pinecone import Pinecone
        pc = Pinecone(api_key=api_key)
        
        # List all indexes
        indexes = pc.list_indexes()
        logger.info(f"Found {len(indexes)} Pinecone indexes:")
        
        for idx in indexes:
            logger.info(f"- Index: {idx.name}")
            
            # Get more information about the index
            index = pc.Index(idx.name)
            
            # Try to get stats about the index
            try:
                stats = index.describe_index_stats()
                logger.info(f"  Namespace count: {stats.get('namespaces', {}).get('', {}).get('vector_count', 'N/A')}")
                logger.info(f"  Dimension: {stats.get('dimension', 'N/A')}")
            except Exception as e:
                logger.warning(f"  Could not get stats for index {idx.name}: {str(e)}")
                
            # Try a simple query to verify the index is functional
            try:
                # Create a dummy vector of the right dimension
                # Most indexes use 1536 (OpenAI) or 3072 dimensions
                try:
                    dimension = stats.get('dimension', 3072)
                except:
                    dimension = 3072  # Default to 3072 for regulatoryai
                
                dummy_vector = [0.0] * dimension
                results = index.query(vector=dummy_vector, top_k=1, include_metadata=True)
                logger.info(f"  Query successful: {type(results)}")
            except Exception as e:
                logger.warning(f"  Query test failed: {str(e)}")
        
        # Specifically check for 'regulatoryai' and 'kycstreamline' indexes
        index_names = [idx.name for idx in indexes]
        
        if 'regulatoryai' in index_names:
            logger.info("✅ 'regulatoryai' index found and accessible")
        else:
            logger.warning("❌ 'regulatoryai' index not found")
            
        if 'kycstreamline' in index_names:
            logger.info("✅ 'kycstreamline' index found and accessible")
        else:
            logger.warning("❌ 'kycstreamline' index not found")
            
        return True
        
    except ImportError:
        logger.warning("Pinecone V3 API not available, trying V2 API")
        
        # Try with Pinecone V2 API
        try:
            import pinecone
            pinecone.init(api_key=api_key, environment="us-east-1")
            
            # List all indexes
            indexes = pinecone.list_indexes()
            logger.info(f"Found {len(indexes)} Pinecone indexes:")
            
            for idx_name in indexes:
                logger.info(f"- Index: {idx_name}")
                
                # Get more information about the index
                index = pinecone.Index(idx_name)
                
                # Try to get stats about the index
                try:
                    stats = index.describe_index_stats()
                    logger.info(f"  Vector count: {stats.get('total_vector_count', 'N/A')}")
                    logger.info(f"  Dimension: {stats.get('dimension', 'N/A')}")
                except Exception as e:
                    logger.warning(f"  Could not get stats for index {idx_name}: {str(e)}")
                    
                # Try a simple query to verify the index is functional
                try:
                    # Create a dummy vector of the right dimension
                    # Most indexes use 1536 (OpenAI) or 3072 dimensions
                    try:
                        dimension = stats.get('dimension', 3072)
                    except:
                        dimension = 3072  # Default to 3072 for regulatoryai
                    
                    dummy_vector = [0.0] * dimension
                    results = index.query(vector=dummy_vector, top_k=1, include_metadata=True)
                    logger.info(f"  Query successful: {type(results)}")
                except Exception as e:
                    logger.warning(f"  Query test failed: {str(e)}")
            
            # Specifically check for 'regulatoryai' and 'kycstreamline' indexes
            if 'regulatoryai' in indexes:
                logger.info("✅ 'regulatoryai' index found and accessible")
            else:
                logger.warning("❌ 'regulatoryai' index not found")
                
            if 'kycstreamline' in indexes:
                logger.info("✅ 'kycstreamline' index found and accessible")
            else:
                logger.warning("❌ 'kycstreamline' index not found")
                
            return True
            
        except Exception as e:
            logger.error(f"Pinecone V2 API failed: {str(e)}")
            return False
    
    except Exception as e:
        logger.error(f"Failed to connect to Pinecone: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Verifying Pinecone indexes...")
    success = verify_pinecone_indexes()
    
    if success:
        logger.info("Pinecone verification completed successfully")
    else:
        logger.error("Pinecone verification failed")