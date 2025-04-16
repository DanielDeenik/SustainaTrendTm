#!/usr/bin/env python3
"""
Script to verify MongoDB data population
"""

import os
import sys
import logging
from pymongo import MongoClient
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB connection settings
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'sustainatrend')

def verify_data():
    """Verify the data in MongoDB."""
    try:
        client = MongoClient(MONGODB_URI)
        # Test connection
        client.admin.command('ping')
        db = client[MONGODB_DB_NAME]
        logger.info(f"Connected to MongoDB: {MONGODB_URI}")
        
        # Check collections
        collections = ['portfolio_companies', 'sustainability_metrics', 'trends', 'stories', 'vc_data']
        for collection in collections:
            count = db[collection].count_documents({})
            logger.info(f"Collection {collection} has {count} documents")
            
            # Show sample document
            sample = db[collection].find_one()
            if sample:
                logger.info(f"Sample document from {collection}:")
                logger.info(f"{sample}")
            
        return True
        
    except Exception as e:
        logger.error(f"Error verifying database: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    if verify_data():
        logger.info("Database verification completed successfully")
    else:
        logger.error("Database verification failed")
        sys.exit(1) 