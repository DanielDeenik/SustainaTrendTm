"""
MongoDB service for the SustainaTrend™ Intelligence Platform.

This module provides a service for interacting with MongoDB, including connection
management, CRUD operations, and error handling.
"""

import os
import logging
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configure logger
logger = logging.getLogger(__name__)

# Check if pymongo is available
PYMONGO_AVAILABLE = True
try:
    import pymongo
except ImportError:
    PYMONGO_AVAILABLE = False
    logger.warning("PyMongo is not available. Using mock MongoDB service.")

class MongoDBService:
    """
    Service for interacting with MongoDB.
    
    This class provides methods for connecting to MongoDB, performing CRUD operations,
    and handling errors.
    """
    
    _instance = None
    _client = None
    _db = None
    _collections = {}
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance of the service exists."""
        if cls._instance is None:
            cls._instance = super(MongoDBService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the MongoDB service only once."""
        if not self._initialized:
            self.logger = logging.getLogger(__name__)
            self._collections = {}  # Cache for collections
            self._initialize_clients()
            self._initialized = True
    
    def _initialize_clients(self):
        """Initialize MongoDB client and database connection."""
        try:
            if not PYMONGO_AVAILABLE:
                self.logger.warning("Using mock MongoDB service")
                return
                
            uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
            db_name = os.getenv('MONGO_DB_NAME', 'sustainatrend')
            
            self._client = MongoClient(uri)
            self._db = self._client[db_name]
            
            # Test connection
            self._client.server_info()
            self.logger.info(f"Connected to MongoDB: {uri}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MongoDB: {str(e)}")
            self._client = None
            self._db = None
    
    def is_connected(self) -> bool:
        """Check if the MongoDB connection is active and healthy."""
        if not PYMONGO_AVAILABLE or not self._client:
            return False
        try:
            # Ping the server to confirm connection
            self._client.admin.command('ping')
            return True
        except Exception as e:
            self.logger.error(f"MongoDB connection check failed: {str(e)}")
            return False
    
    def get_collection(self, collection_name: str):
        """Get a MongoDB collection by name."""
        if not PYMONGO_AVAILABLE or not self._db:
            self.logger.warning(f"Using mock collection for {collection_name}")
            return MockCollection(collection_name)
            
        if collection_name not in self._collections:
            self._collections[collection_name] = self._db[collection_name]
        return self._collections[collection_name]
    
    def find_one(self, collection_name: str, query: Dict = None, projection: Dict = None) -> Optional[Dict]:
        """Find a single document in a collection."""
        try:
            collection = self.get_collection(collection_name)
            return collection.find_one(query or {}, projection or {})
        except Exception as e:
            self.logger.error(f"Error finding document in {collection_name}: {str(e)}")
            return None
    
    def find_many(self, collection_name: str, query: Dict = None, projection: Dict = None, 
                 sort: List = None, limit: int = None, skip: int = None) -> List[Dict]:
        """Find multiple documents in a collection."""
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.find(query or {}, projection or {})
            
            if sort:
                cursor = cursor.sort(sort)
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
                
            return list(cursor)
        except Exception as e:
            self.logger.error(f"Error finding documents in {collection_name}: {str(e)}")
            return []
    
    def insert_one(self, collection_name: str, document: Dict) -> Optional[str]:
        """Insert a single document into a collection."""
        try:
            collection = self.get_collection(collection_name)
            result = collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            self.logger.error(f"Error inserting document into {collection_name}: {str(e)}")
            return None
    
    def insert_many(self, collection_name: str, documents: List[Dict]) -> List[str]:
        """Insert multiple documents into a collection."""
        try:
            collection = self.get_collection(collection_name)
            result = collection.insert_many(documents)
            return [str(id) for id in result.inserted_ids]
        except Exception as e:
            self.logger.error(f"Error inserting documents into {collection_name}: {str(e)}")
            return []
    
    def update_one(self, collection_name: str, query: Dict, update: Dict, upsert: bool = False) -> bool:
        """Update a single document in a collection."""
        try:
            collection = self.get_collection(collection_name)
            result = collection.update_one(query, update, upsert=upsert)
            return result.modified_count > 0 or result.upserted_id is not None
        except Exception as e:
            self.logger.error(f"Error updating document in {collection_name}: {str(e)}")
            return False
    
    def update_many(self, collection_name: str, query: Dict, update: Dict) -> int:
        """Update multiple documents in a collection."""
        try:
            collection = self.get_collection(collection_name)
            result = collection.update_many(query, update)
            return result.modified_count
        except Exception as e:
            self.logger.error(f"Error updating documents in {collection_name}: {str(e)}")
            return 0
    
    def delete_one(self, collection_name: str, query: Dict) -> bool:
        """Delete a single document from a collection."""
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_one(query)
            return result.deleted_count > 0
        except Exception as e:
            self.logger.error(f"Error deleting document from {collection_name}: {str(e)}")
            return False
    
    def delete_many(self, collection_name: str, query: Dict) -> int:
        """Delete multiple documents from a collection."""
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_many(query)
            return result.deleted_count
        except Exception as e:
            self.logger.error(f"Error deleting documents from {collection_name}: {str(e)}")
            return 0
    
    def count_documents(self, collection_name: str, query: Dict = None) -> int:
        """Count documents in a collection."""
        try:
            collection = self.get_collection(collection_name)
            return collection.count_documents(query or {})
        except Exception as e:
            self.logger.error(f"Error counting documents in {collection_name}: {str(e)}")
            return 0
    
    def create_index(self, collection_name: str, keys: List, unique: bool = False, 
                    background: bool = True, sparse: bool = False) -> bool:
        """Create an index on a collection."""
        try:
            collection = self.get_collection(collection_name)
            collection.create_index(keys, unique=unique, background=background, sparse=sparse)
            return True
        except Exception as e:
            self.logger.error(f"Error creating index on {collection_name}: {str(e)}")
            return False
    
    def drop_index(self, collection_name: str, index_name: str) -> bool:
        """Drop an index from a collection."""
        try:
            collection = self.get_collection(collection_name)
            collection.drop_index(index_name)
            return True
        except Exception as e:
            self.logger.error(f"Error dropping index from {collection_name}: {str(e)}")
            return False
    
    def list_indexes(self, collection_name: str) -> List[Dict]:
        """List all indexes on a collection."""
        try:
            collection = self.get_collection(collection_name)
            return list(collection.list_indexes())
        except Exception as e:
            self.logger.error(f"Error listing indexes on {collection_name}: {str(e)}")
            return []
    
    def close(self):
        """Close the MongoDB connection."""
        if self._client:
            self._client.close()
            self.logger.info("MongoDB connection closed")

    def get_trends(self, category: Optional[str] = None, 
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   limit: Optional[int] = None) -> List[Dict]:
        """Get trends with optional filtering."""
        query = {}
        
        if category:
            query['category'] = category
            
        if start_date or end_date:
            query['date'] = {}
            if start_date:
                query['date']['$gte'] = start_date
            if end_date:
                query['date']['$lte'] = end_date
        
        try:
            collection = self.get_collection('trends')
            cursor = collection.find(query).sort('date', -1)
            
            if limit:
                cursor = cursor.limit(limit)
                
            return list(cursor)
        except Exception as e:
            self.logger.error(f"Error getting trends: {str(e)}")
            return []

    def get_trending_categories(self) -> List[str]:
        """Get list of unique categories from trends collection."""
        try:
            collection = self.get_collection('trends')
            categories = collection.distinct('category')
            return sorted(categories)
        except Exception as e:
            self.logger.error(f"Error getting trending categories: {str(e)}")
            return []

    def get_trend_by_id(self, trend_id: str) -> Optional[Dict]:
        """Get a specific trend by ID."""
        try:
            collection = self.get_collection('trends')
            return collection.find_one({'_id': trend_id})
        except Exception as e:
            self.logger.error(f"Error getting trend by ID: {str(e)}")
            return None

    def get_trend_metrics(self, trend_id: str) -> Dict[str, Any]:
        """Get additional metrics for a trend."""
        try:
            trend = self.get_trend_by_id(trend_id)
            if not trend:
                return {}
                
            # Calculate engagement metrics
            engagement = self.get_collection('engagement').find_one({'trend_id': trend_id})
            
            # Get related companies
            companies = self.get_collection('companies').count_documents({
                'trends': trend_id
            })
            
            return {
                'engagement_score': engagement.get('score', 0) if engagement else 0,
                'social_mentions': engagement.get('mentions', 0) if engagement else 0,
                'related_companies': companies
            }
        except Exception as e:
            self.logger.error(f"Error getting trend metrics: {str(e)}")
            return {}

    def get_metrics(self) -> Dict[str, Any]:
        """Get key metrics across all collections."""
        try:
            metrics = {
                'trends': self.get_collection('trends').count_documents({}),
                'stories': self.get_collection('stories').count_documents({}),
                'portfolio': self.get_collection('portfolio').count_documents({})
            }
            return metrics
        except Exception as e:
            self.logger.error(f"Error fetching metrics: {str(e)}")
            return {}


class MockCollection:
    """Mock MongoDB collection for testing and development."""
    
    def __init__(self, name):
        self.name = name
        self.documents = []
        self.indexes = []
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Created mock collection: {name}")
    
    def find_one(self, query=None, projection=None):
        """Mock find_one operation."""
        self.logger.debug(f"Mock find_one on {self.name} with query: {query}")
        return None
    
    def find(self, query=None, projection=None):
        """Mock find operation."""
        self.logger.debug(f"Mock find on {self.name} with query: {query}")
        return []
    
    def insert_one(self, document):
        """Mock insert_one operation."""
        self.logger.debug(f"Mock insert_one on {self.name} with document: {document}")
        return MockInsertOneResult("mock_id")
    
    def insert_many(self, documents):
        """Mock insert_many operation."""
        self.logger.debug(f"Mock insert_many on {self.name} with {len(documents)} documents")
        return MockInsertManyResult(["mock_id"] * len(documents))
    
    def update_one(self, query, update, upsert=False):
        """Mock update_one operation."""
        self.logger.debug(f"Mock update_one on {self.name} with query: {query}")
        return MockUpdateResult(1, 1)
    
    def update_many(self, query, update):
        """Mock update_many operation."""
        self.logger.debug(f"Mock update_many on {self.name} with query: {query}")
        return MockUpdateResult(1, 1)
    
    def delete_one(self, query):
        """Mock delete_one operation."""
        self.logger.debug(f"Mock delete_one on {self.name} with query: {query}")
        return MockDeleteResult(1)
    
    def delete_many(self, query):
        """Mock delete_many operation."""
        self.logger.debug(f"Mock delete_many on {self.name} with query: {query}")
        return MockDeleteResult(1)
    
    def count_documents(self, query=None):
        """Mock count_documents operation."""
        self.logger.debug(f"Mock count_documents on {self.name} with query: {query}")
        return 0
    
    def create_index(self, keys, unique=False, background=True, sparse=False):
        """Mock create_index operation."""
        self.logger.debug(f"Mock create_index on {self.name} with keys: {keys}")
        return "mock_index"
    
    def drop_index(self, index_name):
        """Mock drop_index operation."""
        self.logger.debug(f"Mock drop_index on {self.name} with index: {index_name}")
        return None
    
    def list_indexes(self):
        """Mock list_indexes operation."""
        self.logger.debug(f"Mock list_indexes on {self.name}")
        return []


class MockInsertOneResult:
    """Mock result for insert_one operation."""
    
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id


class MockInsertManyResult:
    """Mock result for insert_many operation."""
    
    def __init__(self, inserted_ids):
        self.inserted_ids = inserted_ids


class MockUpdateResult:
    """Mock result for update operations."""
    
    def __init__(self, matched_count, modified_count, upserted_id=None):
        self.matched_count = matched_count
        self.modified_count = modified_count
        self.upserted_id = upserted_id


class MockDeleteResult:
    """Mock result for delete operations."""
    
    def __init__(self, deleted_count):
        self.deleted_count = deleted_count


def get_mongodb_service() -> MongoDBService:
    """
    Get the MongoDB service instance.
    
    Returns:
        MongoDBService: The MongoDB service instance.
    """
    return MongoDBService()


def get_database():
    """
    Get the MongoDB database instance.
    
    Returns:
        pymongo.database.Database: The MongoDB database instance.
    """
    service = MongoDBService()
    return service._db


def verify_connection():
    """
    Verify the MongoDB connection.
    
    Returns:
        bool: True if the connection is successful, False otherwise.
    """
    try:
        service = MongoDBService()
        if service._client:
            # Try to execute a simple command to check connection
            service._client.admin.command('ping')
            return True
        return False
    except Exception as e:
        logger.error(f"Error verifying MongoDB connection: {str(e)}")
        return False 