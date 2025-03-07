"""
MongoDB client for SustainaTrend™ platform
Provides connection and database access functions for MongoDB integration
"""

import os
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# Default connection settings
DEFAULT_MONGO_URI = "mongodb://localhost:27017/"
DEFAULT_DB_NAME = "sustainatrend"

# Get MongoDB URI from environment or use default
MONGO_URI = os.environ.get("MONGO_URI", DEFAULT_MONGO_URI)
DB_NAME = os.environ.get("MONGO_DB_NAME", DEFAULT_DB_NAME)

# Singleton client instances
_sync_client = None
_async_client = None


def get_sync_client():
    """
    Get or create a synchronized MongoDB client
    Returns a reused connection if one exists

    Returns:
        MongoClient: MongoDB client instance
    """
    global _sync_client
    if _sync_client is None:
        try:
            logger.info(f"Connecting to MongoDB at {MONGO_URI}")
            _sync_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            # Verify connection is working
            _sync_client.admin.command('ping')
            logger.info("MongoDB connection established successfully")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"MongoDB connection failed: {str(e)}")
            raise
    return _sync_client


def get_async_client():
    """
    Get or create an asynchronous MongoDB client
    Returns a reused connection if one exists

    Returns:
        AsyncIOMotorClient: Asynchronous MongoDB client instance
    """
    global _async_client
    if _async_client is None:
        try:
            logger.info(f"Connecting to MongoDB (async) at {MONGO_URI}")
            _async_client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            logger.info("Async MongoDB connection initialized")
        except Exception as e:
            logger.error(f"Async MongoDB connection failed: {str(e)}")
            raise
    return _async_client


def get_database(db_name=None):
    """
    Get a MongoDB database instance
    
    Args:
        db_name (str, optional): Database name. Defaults to DB_NAME.
    
    Returns:
        Database: MongoDB database instance
    """
    client = get_sync_client()
    return client[db_name or DB_NAME]


def get_async_database(db_name=None):
    """
    Get an asynchronous MongoDB database instance
    
    Args:
        db_name (str, optional): Database name. Defaults to DB_NAME.
    
    Returns:
        AsyncIOMotorDatabase: Asynchronous MongoDB database instance
    """
    client = get_async_client()
    return client[db_name or DB_NAME]


def close_connections():
    """
    Close all MongoDB connections
    Call this function when shutting down the application
    """
    global _sync_client, _async_client
    
    if _sync_client:
        logger.info("Closing MongoDB sync connection")
        _sync_client.close()
        _sync_client = None
    
    if _async_client:
        logger.info("Closing MongoDB async connection")
        _async_client.close()
        _async_client = None


async def verify_async_connection():
    """
    Verify that the async MongoDB connection works
    
    Returns:
        bool: True if connection works, False otherwise
    """
    client = get_async_client()
    try:
        # Run a simple command to verify the connection works
        await client.admin.command("ping")
        return True
    except Exception as e:
        logger.error(f"Async MongoDB verification failed: {str(e)}")
        return False


def verify_connection():
    """
    Verify that the MongoDB connection works
    
    Returns:
        bool: True if connection works, False otherwise
    """
    try:
        client = get_sync_client()
        client.admin.command("ping")
        return True
    except Exception as e:
        logger.error(f"MongoDB verification failed: {str(e)}")
        return False


# Helper functions for common MongoDB operations

def serialize_document(document):
    """
    Serialize MongoDB document to make it JSON serializable
    Handles ObjectId, datetime, etc.
    
    Args:
        document (dict): MongoDB document
        
    Returns:
        dict: Serialized document
    """
    if document is None:
        return None
    
    result = {}
    for key, value in document.items():
        # Handle ObjectId
        if key == '_id' and hasattr(value, '__str__'):
            result['id'] = str(value)
        # Handle datetime
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        # Handle nested documents
        elif isinstance(value, dict):
            result[key] = serialize_document(value)
        # Handle lists of documents
        elif isinstance(value, list) and all(isinstance(item, dict) for item in value):
            result[key] = [serialize_document(item) for item in value]
        else:
            result[key] = value
    
    return result


def metrics_collection():
    """
    Get the metrics collection
    
    Returns:
        Collection: MongoDB collection for sustainability metrics
    """
    db = get_database()
    return db.metrics


def trends_collection():
    """
    Get the trends collection
    
    Returns:
        Collection: MongoDB collection for sustainability trends
    """
    db = get_database()
    return db.trends


def stories_collection():
    """
    Get the stories collection
    
    Returns:
        Collection: MongoDB collection for sustainability stories
    """
    db = get_database()
    return db.stories


async def async_metrics_collection():
    """
    Get the async metrics collection
    
    Returns:
        AsyncIOMotorCollection: Async MongoDB collection for sustainability metrics
    """
    db = get_async_database()
    return db.metrics


async def async_trends_collection():
    """
    Get the async trends collection
    
    Returns:
        AsyncIOMotorCollection: Async MongoDB collection for sustainability trends
    """
    db = get_async_database()
    return db.trends


async def async_stories_collection():
    """
    Get the async stories collection
    
    Returns:
        AsyncIOMotorCollection: Async MongoDB collection for sustainability stories
    """
    db = get_async_database()
    return db.stories