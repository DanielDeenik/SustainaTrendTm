"""
MongoDB Service

This module provides a unified interface for MongoDB operations, supporting both
synchronous (PyMongo) and asynchronous (Motor) clients.
"""

import logging
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Check if we should use mock MongoDB
USE_MOCK_MONGODB = os.getenv('USE_MOCK_MONGODB', 'False').lower() == 'true'

# Try to import MongoDB libraries
try:
    from pymongo import MongoClient
    from pymongo.collection import Collection
    from pymongo.database import Database
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False
    logger.warning("PyMongo not available. Using mock MongoDB service.")

try:
    import motor.motor_asyncio
    MOTOR_AVAILABLE = True
except ImportError:
    MOTOR_AVAILABLE = False
    logger.warning("Motor not available. Async MongoDB operations will not be available.")

class MongoDBService:
    """MongoDB service for handling database operations."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, connection_string: Optional[str] = None, db_name: str = "sustainatrend"):
        """Initialize the MongoDB service."""
        if not hasattr(self, 'initialized'):
            self.connection_string = connection_string or os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
            self.db_name = db_name
            self.client = None
            self.db = None
            self.async_client = None
            self.async_db = None
            self.initialized = True
            
            # Only initialize if not using mock MongoDB
            if not USE_MOCK_MONGODB and PYMONGO_AVAILABLE:
                self._initialize_clients()
            else:
                logger.info("Using mock MongoDB service")
    
    def _initialize_clients(self):
        """Initialize MongoDB clients."""
        try:
            # Initialize synchronous client
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=2000)
            self.db = self.client[self.db_name]
            
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB at {self.connection_string}")
            
            # Initialize asynchronous client if available
            if MOTOR_AVAILABLE:
                self.async_client = motor.motor_asyncio.AsyncIOMotorClient(self.connection_string)
                self.async_db = self.async_client[self.db_name]
                logger.info("Async MongoDB client initialized")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            self.client = None
            self.db = None
            self.async_client = None
            self.async_db = None
        except Exception as e:
            logger.error(f"Error initializing MongoDB clients: {str(e)}")
            self.client = None
            self.db = None
            self.async_client = None
            self.async_db = None
    
    def get_collection(self, collection_name: str) -> Collection:
        """Get a MongoDB collection."""
        if not self.db:
            raise RuntimeError("MongoDB client not initialized")
        return self.db[collection_name]
    
    def get_async_collection(self, collection_name: str):
        """Get an async MongoDB collection."""
        if not self.async_db:
            raise RuntimeError("Async MongoDB client not initialized")
        return self.async_db[collection_name]
    
    def insert_one(self, collection_name: str, document: Dict[str, Any]) -> str:
        """Insert a single document into a collection."""
        try:
            collection = self.get_collection(collection_name)
            document['timestamp'] = datetime.now()
            result = collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to insert document into {collection_name}: {e}")
            raise
    
    async def insert_one_async(self, collection_name: str, document: Dict[str, Any]) -> str:
        """Insert a single document into a collection asynchronously."""
        try:
            collection = self.get_async_collection(collection_name)
            document['timestamp'] = datetime.now()
            result = await collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to insert document into {collection_name}: {e}")
            raise
    
    def find_one(self, collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document in a collection."""
        try:
            collection = self.get_collection(collection_name)
            return collection.find_one(query)
        except Exception as e:
            logger.error(f"Failed to find document in {collection_name}: {e}")
            raise
    
    async def find_one_async(self, collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document in a collection asynchronously."""
        try:
            collection = self.get_async_collection(collection_name)
            return await collection.find_one(query)
        except Exception as e:
            logger.error(f"Failed to find document in {collection_name}: {e}")
            raise
    
    def find_many(self, collection_name: str, query: Dict[str, Any], sort: Optional[List[tuple]] = None) -> List[Dict[str, Any]]:
        """Find multiple documents in a collection."""
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.find(query)
            if sort:
                cursor = cursor.sort(sort)
            return list(cursor)
        except Exception as e:
            logger.error(f"Failed to find documents in {collection_name}: {e}")
            raise
    
    async def find_many_async(self, collection_name: str, query: Dict[str, Any], sort: Optional[List[tuple]] = None) -> List[Dict[str, Any]]:
        """Find multiple documents in a collection asynchronously."""
        try:
            collection = self.get_async_collection(collection_name)
            cursor = collection.find(query)
            if sort:
                cursor = cursor.sort(sort)
            return await cursor.to_list(length=None)
        except Exception as e:
            logger.error(f"Failed to find documents in {collection_name}: {e}")
            raise
    
    def update_one(self, collection_name: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """Update a single document in a collection."""
        try:
            collection = self.get_collection(collection_name)
            update['$set']['last_updated'] = datetime.now()
            result = collection.update_one(query, update)
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update document in {collection_name}: {e}")
            raise
    
    async def update_one_async(self, collection_name: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """Update a single document in a collection asynchronously."""
        try:
            collection = self.get_async_collection(collection_name)
            update['$set']['last_updated'] = datetime.now()
            result = await collection.update_one(query, update)
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update document in {collection_name}: {e}")
            raise
    
    def delete_one(self, collection_name: str, query: Dict[str, Any]) -> bool:
        """Delete a single document from a collection."""
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_one(query)
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete document from {collection_name}: {e}")
            raise
    
    async def delete_one_async(self, collection_name: str, query: Dict[str, Any]) -> bool:
        """Delete a single document from a collection asynchronously."""
        try:
            collection = self.get_async_collection(collection_name)
            result = await collection.delete_one(query)
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete document from {collection_name}: {e}")
            raise
    
    def close(self):
        """Close MongoDB connections."""
        try:
            if self.client:
                self.client.close()
            if self.async_client:
                self.async_client.close()
            logger.info("MongoDB connections closed")
        except Exception as e:
            logger.error(f"Failed to close MongoDB connections: {e}")
            raise

def get_mongodb_service() -> MongoDBService:
    """Get a MongoDB service instance."""
    return MongoDBService()

def get_database() -> Optional[Database]:
    """Get a MongoDB database instance."""
    service = get_mongodb_service()
    return service.db

def verify_connection() -> bool:
    """Verify MongoDB connection."""
    try:
        service = get_mongodb_service()
        if service.client:
            # Try a simple command to verify connection
            service.client.server_info()
            logger.info("MongoDB connection verified")
            return True
        
        logger.warning("MongoDB connection not available")
        return False
    except Exception as e:
        logger.error(f"Failed to verify MongoDB connection: {e}")
        return False

def close_connections():
    """Close MongoDB connections."""
    try:
        service = get_mongodb_service()
        service.close()
        logger.info("MongoDB connections closed")
    except Exception as e:
        logger.error(f"Failed to close MongoDB connections: {e}") 