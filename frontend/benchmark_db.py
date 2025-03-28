"""
Benchmark MongoDB Connector for SustainaTrend™ Platform
Handles MongoDB operations specifically for the Benchmarking Engine
"""

import logging
import json
from datetime import datetime
from bson import ObjectId

# Configure logging
logger = logging.getLogger(__name__)

# Import MongoDB connection functions
try:
    from mongo_client import (
        get_database, 
        benchmarking_collection, 
        serialize_document,
        verify_connection
    )
except ImportError:
    try:
        from frontend.mongo_client import (
            get_database, 
            benchmarking_collection, 
            serialize_document, 
            verify_connection
        )
    except ImportError:
        logger.error("MongoDB client module not found")
        
        # Define fallback functions
        def get_database():
            return None
            
        def benchmarking_collection():
            return None
            
        def serialize_document(doc):
            return doc
            
        def verify_connection():
            return False


def initialize_benchmarking_collection():
    """
    Initialize the benchmarking collection with indexes
    Creates the collection if it does not exist
    """
    try:
        # Check MongoDB connection
        if not verify_connection():
            logger.warning("MongoDB connection not available, skipping benchmarking collection initialization")
            return False
            
        # Get or create benchmarking collection
        collection = benchmarking_collection()
        if not collection:
            logger.warning("MongoDB benchmarking collection not available")
            return False
            
        # Create indexes if they don't exist
        collection.create_index([("company_id", 1)], background=True)
        collection.create_index([("framework", 1)], background=True)
        collection.create_index([("sector", 1)], background=True)
        collection.create_index([("region", 1)], background=True)
        collection.create_index([("timestamp", -1)], background=True)
        
        logger.info("Benchmarking collection initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing benchmarking collection: {str(e)}")
        return False


def save_benchmark_data(data):
    """
    Save benchmark data to MongoDB
    
    Args:
        data (dict): Benchmark data to save
        
    Returns:
        str: ID of saved document, None if failed
    """
    try:
        # Check MongoDB connection
        if not verify_connection():
            logger.warning("MongoDB connection not available, cannot save benchmark data")
            return None
            
        # Get benchmarking collection
        collection = benchmarking_collection()
        if not collection:
            logger.warning("MongoDB benchmarking collection not available")
            return None
            
        # Add timestamp
        data['timestamp'] = datetime.utcnow()
        
        # Insert document
        result = collection.insert_one(data)
        
        # Return ID of inserted document
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error saving benchmark data: {str(e)}")
        return None


def get_benchmark_data(company_id=None, framework=None, limit=100):
    """
    Get benchmark data from MongoDB
    
    Args:
        company_id (str, optional): Filter by company ID
        framework (str, optional): Filter by framework
        limit (int, optional): Maximum number of records to return
        
    Returns:
        list: List of benchmark data documents
    """
    try:
        # Check MongoDB connection
        if not verify_connection():
            logger.warning("MongoDB connection not available, cannot get benchmark data")
            return []
            
        # Get benchmarking collection
        collection = benchmarking_collection()
        if not collection:
            logger.warning("MongoDB benchmarking collection not available")
            return []
            
        # Build query
        query = {}
        if company_id:
            query['company_id'] = company_id
        if framework:
            query['framework'] = framework
            
        # Execute query
        cursor = collection.find(query).sort('timestamp', -1).limit(limit)
        
        # Convert to list and serialize
        result = [serialize_document(doc) for doc in cursor]
        
        return result
    except Exception as e:
        logger.error(f"Error getting benchmark data: {str(e)}")
        return []


def get_peer_companies(sector, region, size=None, limit=5):
    """
    Get peer companies from MongoDB for benchmarking
    
    Args:
        sector (str): Industry sector
        region (str): Geographic region
        size (str, optional): Company size
        limit (int, optional): Maximum number of peers to return
        
    Returns:
        list: List of peer companies
    """
    try:
        # Check MongoDB connection
        if not verify_connection():
            logger.warning("MongoDB connection not available, cannot get peer companies")
            return []
            
        # Get benchmarking collection
        collection = benchmarking_collection()
        if not collection:
            logger.warning("MongoDB benchmarking collection not available")
            return []
            
        # Build aggregate pipeline
        pipeline = [
            # Match by sector and region
            {"$match": {
                "company_profile.sector": sector,
                "company_profile.region": region
            }},
            # Group by company
            {"$group": {
                "_id": "$company_id",
                "name": {"$first": "$company_profile.name"},
                "sector": {"$first": "$company_profile.sector"},
                "region": {"$first": "$company_profile.region"},
                "size": {"$first": "$company_profile.size"},
                "last_updated": {"$max": "$timestamp"}
            }},
            # Sort by last updated
            {"$sort": {"last_updated": -1}},
            # Limit results
            {"$limit": limit}
        ]
        
        # If size is specified, add it to the match criteria
        if size:
            pipeline[0]["$match"]["company_profile.size"] = size
            
        # Execute aggregate query
        cursor = collection.aggregate(pipeline)
        
        # Convert to list and serialize
        result = [serialize_document(doc) for doc in cursor]
        
        return result
    except Exception as e:
        logger.error(f"Error getting peer companies: {str(e)}")
        return []


def get_framework_benchmarks(framework_id, sector=None, limit=50):
    """
    Get benchmark data for a specific framework
    
    Args:
        framework_id (str): Framework identifier
        sector (str, optional): Filter by industry sector
        limit (int, optional): Maximum number of records to return
        
    Returns:
        list: List of framework benchmark data
    """
    try:
        # Check MongoDB connection
        if not verify_connection():
            logger.warning("MongoDB connection not available, cannot get framework benchmarks")
            return []
            
        # Get benchmarking collection
        collection = benchmarking_collection()
        if not collection:
            logger.warning("MongoDB benchmarking collection not available")
            return []
            
        # Build query
        query = {"framework": framework_id}
        if sector:
            query["company_profile.sector"] = sector
            
        # Execute query
        cursor = collection.find(query).sort('timestamp', -1).limit(limit)
        
        # Convert to list and serialize
        result = [serialize_document(doc) for doc in cursor]
        
        return result
    except Exception as e:
        logger.error(f"Error getting framework benchmarks: {str(e)}")
        return []


def save_benchmark_assessment(company_id, assessment_data):
    """
    Save benchmark assessment data to MongoDB
    
    Args:
        company_id (str): Company identifier
        assessment_data (dict): Assessment data
        
    Returns:
        str: ID of saved document, None if failed
    """
    try:
        # Check MongoDB connection
        if not verify_connection():
            logger.warning("MongoDB connection not available, cannot save benchmark assessment")
            return None
            
        # Get benchmarking collection
        collection = benchmarking_collection()
        if not collection:
            logger.warning("MongoDB benchmarking collection not available")
            return None
            
        # Prepare document
        document = {
            "company_id": company_id,
            "assessment_type": "framework",
            "assessment_data": assessment_data,
            "timestamp": datetime.utcnow()
        }
        
        # Insert document
        result = collection.insert_one(document)
        
        # Return ID of inserted document
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error saving benchmark assessment: {str(e)}")
        return None