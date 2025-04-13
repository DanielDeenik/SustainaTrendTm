"""
MongoDB Service

This module provides a unified interface for MongoDB operations, supporting both
synchronous (PyMongo) and asynchronous (Motor) clients.
"""

import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Try to import MongoDB libraries
try:
    from pymongo import MongoClient
    from pymongo.collection import Collection
    from pymongo.database import Database
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False
    logger.error("PyMongo not available. Please install pymongo: pip install pymongo")

try:
    import motor.motor_asyncio
    MOTOR_AVAILABLE = True
except ImportError:
    MOTOR_AVAILABLE = False
    logger.error("Motor not available. Please install motor: pip install motor")

class MongoDBService:
    """MongoDB service for handling database operations."""
    
    def __init__(self, connection_string: Optional[str] = None, db_name: str = "sustainatrend"):
        """Initialize the MongoDB service."""
        if not PYMONGO_AVAILABLE:
            raise ImportError("PyMongo is required for MongoDB operations")
            
        self.connection_string = connection_string or os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        self.db_name = db_name
        self.client = None
        self.db = None
        self.async_client = None
        self.async_db = None
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize MongoDB clients."""
        try:
            if PYMONGO_AVAILABLE:
                self.client = MongoClient(self.connection_string)
                self.db = self.client[self.db_name]
                logger.info(f"Connected to MongoDB at {self.connection_string}")
                
                # Test connection
                self.client.server_info()
                logger.info("MongoDB connection test successful")
            
            if MOTOR_AVAILABLE:
                self.async_client = motor.motor_asyncio.AsyncIOMotorClient(self.connection_string)
                self.async_db = self.async_client[self.db_name]
                logger.info("Async MongoDB client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB clients: {e}")
            raise
    
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
        collection = self.get_collection(collection_name)
        result = collection.insert_one(document)
        return str(result.inserted_id)
    
    async def insert_one_async(self, collection_name: str, document: Dict[str, Any]) -> str:
        """Insert a single document into a collection asynchronously."""
        collection = self.get_async_collection(collection_name)
        result = await collection.insert_one(document)
        return str(result.inserted_id)
    
    def find_one(self, collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document in a collection."""
        collection = self.get_collection(collection_name)
        return collection.find_one(query)
    
    async def find_one_async(self, collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document in a collection asynchronously."""
        collection = self.get_async_collection(collection_name)
        return await collection.find_one(query)
    
    def find_many(self, collection_name: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find multiple documents in a collection."""
        collection = self.get_collection(collection_name)
        return list(collection.find(query))
    
    async def find_many_async(self, collection_name: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find multiple documents in a collection asynchronously."""
        collection = self.get_async_collection(collection_name)
        cursor = collection.find(query)
        return await cursor.to_list(length=None)
    
    def update_one(self, collection_name: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """Update a single document in a collection."""
        collection = self.get_collection(collection_name)
        result = collection.update_one(query, {"$set": update})
        return result.modified_count > 0
    
    async def update_one_async(self, collection_name: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """Update a single document in a collection asynchronously."""
        collection = self.get_async_collection(collection_name)
        result = await collection.update_one(query, {"$set": update})
        return result.modified_count > 0
    
    def delete_one(self, collection_name: str, query: Dict[str, Any]) -> bool:
        """Delete a single document from a collection."""
        collection = self.get_collection(collection_name)
        result = collection.delete_one(query)
        return result.deleted_count > 0
    
    async def delete_one_async(self, collection_name: str, query: Dict[str, Any]) -> bool:
        """Delete a single document from a collection asynchronously."""
        collection = self.get_async_collection(collection_name)
        result = await collection.delete_one(query)
        return result.deleted_count > 0
    
    def close(self):
        """Close MongoDB connections."""
        if self.client:
            self.client.close()
        if self.async_client:
            self.async_client.close()
        logger.info("MongoDB connections closed")

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