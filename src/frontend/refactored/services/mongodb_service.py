"""
MongoDB Service for SustainaTrend™

This module provides a unified interface for MongoDB operations.
"""

import os
import logging
import traceback
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, OperationFailure
import random

# Configure logger
logger = logging.getLogger(__name__)

class MongoDBService:
    """
    Singleton class for managing MongoDB operations.
    
    This service provides a unified interface for MongoDB operations and ensures
    only one instance exists throughout the application lifecycle.
    """
    
    _instance = None
    _client = None
    _db = None
    _connected = False
    
    def __new__(cls):
        """Ensure only one instance of MongoDBService exists."""
        if cls._instance is None:
            cls._instance = super(MongoDBService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize MongoDB connection."""
        try:
            # Get MongoDB connection details from environment variables
            mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
            db_name = os.getenv('MONGODB_DATABASE', 'sustainatrend')
            
            # Check if we have username and password
            username = os.getenv('MONGODB_USERNAME')
            password = os.getenv('MONGODB_PASSWORD')
            
            # If username and password are provided, use them in the connection string
            if username and password:
                # Parse the URI to add authentication
                if '@' not in mongodb_uri:
                    # Extract protocol and host
                    protocol, rest = mongodb_uri.split('://', 1)
                    mongodb_uri = f"{protocol}://{username}:{password}@{rest}"
            
            # Connect to MongoDB with connection pooling
            self._client = MongoClient(mongodb_uri, maxPoolSize=50, serverSelectionTimeoutMS=5000)
            self._db = self._client[db_name]
            
            # Test connection
            self._client.admin.command('ping')
            self._connected = True
            logger.info(f"Successfully connected to MongoDB at {mongodb_uri}")
            
            # Create indexes
            self._create_indexes()
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            self._connected = False
        except Exception as e:
            logger.error(f"Error initializing MongoDB: {str(e)}")
            logger.error(traceback.format_exc())
            self._connected = False
    
    def _create_indexes(self):
        """Create necessary indexes for collections."""
        try:
            # Define all indexes we want to create
            indexes = {
                'trends': [
                    ([("category", 1)], {}),
                    ([("created_at", -1)], {})
                ],
                'companies': [
                    ([("sector", 1)], {}),
                    ([("created_at", -1)], {})
                ],
                'portfolio_companies': [
                    ([("sector", 1)], {}),
                    ([("created_at", -1)], {})
                ],
                'properties': [
                    ([("location", "2dsphere")], {}),
                    ([("property_id", 1)], {"unique": True})
                ],
                'metrics': [
                    ([("property_id", 1)], {}),
                    ([("date", -1)], {})
                ],
                'insights': [
                    ([("category", 1)], {}),
                    ([("created_at", -1)], {})
                ],
                'models': [
                    ([("type", 1)], {}),
                    ([("created_at", -1)], {})
                ],
                'revenue': [
                    ([("date", -1)], {}),
                    ([("category", 1)], {})
                ]
            }
            
            # Create indexes for each collection
            for collection_name, collection_indexes in indexes.items():
                collection = self._db[collection_name]
                
                # Get existing indexes
                existing_indexes = []
                try:
                    for idx in collection.list_indexes():
                        existing_indexes.append(idx['name'])
                except Exception as e:
                    logger.warning(f"Error listing indexes for {collection_name}: {str(e)}")
                
                # Create each index if it doesn't exist
                for index_spec, options in collection_indexes:
                    # Generate a name for the index
                    index_name = "_".join([f"{field[0]}_{field[1]}" for field in index_spec])
                    
                    # Check if index already exists
                    if index_name not in existing_indexes:
                        try:
                            collection.create_index(index_spec, **options)
                            logger.info(f"Created index {index_name} on {collection_name}")
                        except Exception as e:
                            logger.warning(f"Error creating index {index_name} on {collection_name}: {str(e)}")
                    else:
                        logger.info(f"Index {index_name} already exists on {collection_name}")
            
            logger.info("Successfully processed MongoDB indexes")
        except Exception as e:
            logger.error(f"Error creating indexes: {str(e)}")
            logger.error(traceback.format_exc())
    
    def is_connected(self) -> bool:
        """Check if connected to MongoDB."""
        return self._connected
    
    def close(self):
        """Close MongoDB connection."""
        if self._client:
            self._client.close()
            self._connected = False
            logger.info("MongoDB connection closed")
    
    def get_collection(self, collection_name: str) -> Collection:
        """Get a MongoDB collection."""
        if not self._connected:
            logger.error("MongoDB not connected")
            return None
        return self._db[collection_name]
    
    def find(self, collection: str, query: Dict = None, projection: Dict = None, 
             sort: List = None, limit: int = 0, skip: int = 0) -> List[Dict]:
        """Find documents in a collection."""
        try:
            if not self._connected:
                logger.error("MongoDB not connected")
                return []
                
            collection_obj = self.get_collection(collection)
            if not collection_obj:
                return []
                
            cursor = collection_obj.find(query or {}, projection or {})
            
            if sort:
                cursor = cursor.sort(sort)
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
                
            return list(cursor)
        except Exception as e:
            logger.error(f"Error finding documents in {collection}: {str(e)}")
            logger.error(traceback.format_exc())
            return []
    
    def find_many(self, collection: str, query: Dict = None, projection: Dict = None,
                 sort: List = None, limit: int = 0, skip: int = 0) -> List[Dict]:
        """Alias for find method to maintain compatibility."""
        return self.find(collection, query, projection, sort, limit, skip)
    
    def insert_one(self, collection: str, document: Dict) -> Optional[str]:
        """Insert a single document into a collection."""
        try:
            if not self._connected:
                logger.error("MongoDB not connected")
                return None
                
            collection_obj = self.get_collection(collection)
            if not collection_obj:
                return None
                
            result = collection_obj.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting document into {collection}: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def update_one(self, collection: str, query: Dict, update: Dict) -> bool:
        """Update a single document in a collection."""
        try:
            if not self._connected:
                logger.error("MongoDB not connected")
                return False
                
            collection_obj = self.get_collection(collection)
            if not collection_obj:
                return False
                
            result = collection_obj.update_one(query, update)
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating document in {collection}: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def delete_one(self, collection: str, query: Dict) -> bool:
        """Delete a single document from a collection."""
        try:
            if not self._connected:
                logger.error("MongoDB not connected")
                return False
                
            collection_obj = self.get_collection(collection)
            if not collection_obj:
                return False
                
            result = collection_obj.delete_one(query)
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting document from {collection}: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def get_trends(self, limit: int = 10) -> List[Dict]:
        """Get recent trends."""
        return self.find('trends', sort=[('created_at', -1)], limit=limit)
    
    def get_metrics(self, property_id: str = None, limit: int = 10) -> List[Dict]:
        """Get metrics for a property or all properties."""
        query = {'property_id': property_id} if property_id else {}
        return self.find('metrics', query=query, sort=[('date', -1)], limit=limit)
    
    def get_companies(self, limit: int = 10) -> List[Dict]:
        """Get portfolio companies."""
        return self.find('portfolio_companies', sort=[('created_at', -1)], limit=limit)
    
    def get_insights(self, limit: int = 10) -> List[Dict]:
        """Get insights."""
        return self.find('insights', sort=[('created_at', -1)], limit=limit)
    
    def get_models(self, limit: int = 10) -> List[Dict]:
        """Get models."""
        return self.find('models', sort=[('created_at', -1)], limit=limit)
    
    def get_revenue(self, limit: int = 12) -> List[Dict]:
        """Get revenue data."""
        return self.find('revenue', sort=[('date', -1)], limit=limit)

# Create singleton instance
mongodb_service = MongoDBService()

# Export the singleton instance
__all__ = ['mongodb_service'] 