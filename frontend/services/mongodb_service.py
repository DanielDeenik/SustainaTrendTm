"""
MongoDB Service for SustainaTrend Intelligence Platform

This service provides a unified interface for MongoDB operations,
supporting both PyMongo and Motor (async) clients.
"""

import logging
import os
from typing import Any, Dict, List, Optional, Union

# Try to import pymongo
try:
    import pymongo
    from pymongo import MongoClient
    from pymongo.collection import Collection
    from pymongo.database import Database
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False
    # Create placeholder types for type hints when pymongo is not available
    class Collection:
        def insert_one(self, document):
            class Result:
                inserted_id = None
            return Result()
            
        def find(self, query=None):
            class Cursor:
                def __iter__(self):
                    # Make the cursor iterable
                    return iter([])
                
                def skip(self, n):
                    return self
                
                def limit(self, n):
                    return self
                
                def sort(self, order):
                    return self
                
                def to_list(self, length=None):
                    return []
            return Cursor()
            
        def update_one(self, query, update, upsert=False):
            class Result:
                modified_count = 0
                upserted_id = None
            return Result()
            
        def delete_one(self, query):
            class Result:
                deleted_count = 0
            return Result()
    
    class Database:
        pass
    
    class MongoClient:
        def __init__(self, *args, **kwargs):
            pass
        
        def __getitem__(self, name):
            return None

# Try to import motor for async MongoDB operations
try:
    import motor.motor_asyncio
    MOTOR_AVAILABLE = True
except ImportError:
    MOTOR_AVAILABLE = False
    # Create mock module for when motor is not available
    class MockMotor:
        class motor_asyncio:
            class AsyncIOMotorClient:
                def __init__(self, *args, **kwargs):
                    pass
                
                def __getitem__(self, name):
                    class MockDB:
                        def __getitem__(self, collection_name):
                            class MockCollection:
                                async def insert_one(self, document):
                                    class Result:
                                        inserted_id = None
                                    return Result()
                                
                                async def find(self, query=None):
                                    class Cursor:
                                        def __iter__(self):
                                            # Make the cursor iterable
                                            return iter([])
                                            
                                        def skip(self, n):
                                            return self
                                        
                                        def limit(self, n):
                                            return self
                                        
                                        def sort(self, order):
                                            return self
                                        
                                        async def to_list(self, length=None):
                                            return []
                                    return Cursor()
                                
                                async def update_one(self, query, update, upsert=False):
                                    class Result:
                                        modified_count = 0
                                        upserted_id = None
                                    return Result()
                                
                                async def delete_one(self, query):
                                    class Result:
                                        deleted_count = 0
                                    return Result()
                            return MockCollection()
                    return MockDB()
    
    motor = MockMotor()

# Setup logging
logger = logging.getLogger(__name__)

class MongoDBService:
    """MongoDB service for the SustainaTrend Intelligence Platform"""
    
    def __init__(self, connection_string: Optional[str] = None, db_name: str = "sustainatrend"):
        """
        Initialize the MongoDB service
        
        Args:
            connection_string: MongoDB connection string (optional, will use environment variable if not provided)
            db_name: Name of the database to use
        """
        self.connection_string = connection_string or os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
        self.db_name = db_name
        self.client = None
        self.db = None
        self.async_client = None
        self.async_db = None
        
        # Initialize synchronous client if available
        if PYMONGO_AVAILABLE:
            try:
                self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
                self.db = self.client[self.db_name]
                logger.info(f"MongoDB service initialized with database '{self.db_name}'")
            except Exception as e:
                logger.warning(f"Failed to initialize MongoDB client: {str(e)}")
                self.client = None
                self.db = None
        else:
            logger.warning("PyMongo not available, synchronous operations will not work")
        
        # Initialize asynchronous client if available
        if MOTOR_AVAILABLE:
            try:
                self.async_client = motor.motor_asyncio.AsyncIOMotorClient(self.connection_string)
                self.async_db = self.async_client[self.db_name]
                logger.info(f"Async MongoDB service initialized with database '{self.db_name}'")
            except Exception as e:
                logger.warning(f"Failed to initialize async MongoDB client: {str(e)}")
                self.async_client = None
                self.async_db = None
        else:
            logger.warning("Motor not available, asynchronous operations will not work")
    
    def get_collection(self, collection_name: str) -> Optional[Collection]:
        """
        Get a MongoDB collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            MongoDB collection or None if not available
        """
        if not self.db:
            logger.warning(f"Cannot get collection '{collection_name}': MongoDB client not initialized")
            return None
        
        return self.db[collection_name]
    
    async def get_async_collection(self, collection_name: str) -> Optional[Any]:
        """
        Get an async MongoDB collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Async MongoDB collection or None if not available
        """
        if not self.async_db:
            logger.warning(f"Cannot get async collection '{collection_name}': Async MongoDB client not initialized")
            return None
        
        return self.async_db[collection_name]
    
    def insert_document(self, collection_name: str, document: Dict[str, Any]) -> Optional[str]:
        """
        Insert a document into a collection
        
        Args:
            collection_name: Name of the collection
            document: Document to insert
            
        Returns:
            ID of the inserted document or None if insertion failed
        """
        collection = self.get_collection(collection_name)
        if not collection:
            return None
        
        try:
            result = collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to insert document into '{collection_name}': {str(e)}")
            return None
    
    async def insert_document_async(self, collection_name: str, document: Dict[str, Any]) -> Optional[str]:
        """
        Insert a document into a collection asynchronously
        
        Args:
            collection_name: Name of the collection
            document: Document to insert
            
        Returns:
            ID of the inserted document or None if insertion failed
        """
        collection = await self.get_async_collection(collection_name)
        if not collection:
            return None
        
        try:
            result = await collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to insert document into '{collection_name}' asynchronously: {str(e)}")
            return None
    
    def find_documents(self, collection_name: str, query: Dict[str, Any], limit: int = 0, 
                      sort_by: Optional[List[tuple]] = None, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Find documents in a collection
        
        Args:
            collection_name: Name of the collection
            query: Query to find documents
            limit: Maximum number of documents to return (0 for all)
            sort_by: List of (field, direction) tuples to sort by
            skip: Number of documents to skip
            
        Returns:
            List of documents or empty list if no documents found or error occurred
        """
        collection = self.get_collection(collection_name)
        if not collection:
            return []
        
        try:
            cursor = collection.find(query).skip(skip)
            
            if limit > 0:
                cursor = cursor.limit(limit)
                
            if sort_by:
                cursor = cursor.sort(sort_by)
            
            # Handle the case where cursor might not be iterable (in mock implementation)
            try:
                return list(cursor)
            except (TypeError, AttributeError):
                logger.warning(f"Cursor is not iterable, returning empty list")
                return []
        except Exception as e:
            logger.error(f"Failed to find documents in '{collection_name}': {str(e)}")
            return []
    
    async def find_documents_async(self, collection_name: str, query: Dict[str, Any], limit: int = 0,
                                  sort_by: Optional[List[tuple]] = None, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Find documents in a collection asynchronously
        
        Args:
            collection_name: Name of the collection
            query: Query to find documents
            limit: Maximum number of documents to return (0 for all)
            sort_by: List of (field, direction) tuples to sort by
            skip: Number of documents to skip
            
        Returns:
            List of documents or empty list if no documents found or error occurred
        """
        collection = await self.get_async_collection(collection_name)
        if not collection:
            return []
        
        try:
            cursor = collection.find(query).skip(skip)
            
            if limit > 0:
                cursor = cursor.limit(limit)
                
            if sort_by:
                cursor = cursor.sort(sort_by)
                
            return await cursor.to_list(length=limit if limit > 0 else None)
        except Exception as e:
            logger.error(f"Failed to find documents in '{collection_name}' asynchronously: {str(e)}")
            return []
    
    def update_document(self, collection_name: str, query: Dict[str, Any], update: Dict[str, Any], 
                       upsert: bool = False) -> bool:
        """
        Update a document in a collection
        
        Args:
            collection_name: Name of the collection
            query: Query to find document to update
            update: Update to apply
            upsert: Whether to insert if document not found
            
        Returns:
            True if update succeeded, False otherwise
        """
        collection = self.get_collection(collection_name)
        if not collection:
            return False
        
        try:
            result = collection.update_one(query, update, upsert=upsert)
            return result.modified_count > 0 or (upsert and result.upserted_id is not None)
        except Exception as e:
            logger.error(f"Failed to update document in '{collection_name}': {str(e)}")
            return False
    
    async def update_document_async(self, collection_name: str, query: Dict[str, Any], update: Dict[str, Any],
                                  upsert: bool = False) -> bool:
        """
        Update a document in a collection asynchronously
        
        Args:
            collection_name: Name of the collection
            query: Query to find document to update
            update: Update to apply
            upsert: Whether to insert if document not found
            
        Returns:
            True if update succeeded, False otherwise
        """
        collection = await self.get_async_collection(collection_name)
        if not collection:
            return False
        
        try:
            result = await collection.update_one(query, update, upsert=upsert)
            return result.modified_count > 0 or (upsert and result.upserted_id is not None)
        except Exception as e:
            logger.error(f"Failed to update document in '{collection_name}' asynchronously: {str(e)}")
            return False
    
    def delete_document(self, collection_name: str, query: Dict[str, Any]) -> bool:
        """
        Delete a document from a collection
        
        Args:
            collection_name: Name of the collection
            query: Query to find document to delete
            
        Returns:
            True if deletion succeeded, False otherwise
        """
        collection = self.get_collection(collection_name)
        if not collection:
            return False
        
        try:
            result = collection.delete_one(query)
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete document from '{collection_name}': {str(e)}")
            return False
    
    async def delete_document_async(self, collection_name: str, query: Dict[str, Any]) -> bool:
        """
        Delete a document from a collection asynchronously
        
        Args:
            collection_name: Name of the collection
            query: Query to find document to delete
            
        Returns:
            True if deletion succeeded, False otherwise
        """
        collection = await self.get_async_collection(collection_name)
        if not collection:
            return False
        
        try:
            result = await collection.delete_one(query)
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete document from '{collection_name}' asynchronously: {str(e)}")
            return False

# Create a singleton instance
mongodb_service = MongoDBService()

def get_mongodb_service() -> MongoDBService:
    """
    Get the MongoDB service singleton
    
    Returns:
        MongoDB service instance
    """
    return mongodb_service