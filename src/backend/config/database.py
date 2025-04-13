"""
Database Configuration Module

This module provides database connection management for both MongoDB and ChromaDB.
"""

import os
import logging
from typing import Optional
import pymongo
import chromadb
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'trendsense')

# Vector Database Configuration
VECTOR_DB_PATH = os.getenv('VECTOR_DB_PATH', './vector_db')
VECTOR_DB_COLLECTION = os.getenv('VECTOR_DB_COLLECTION', 'default_collection')
VC_LENS_COLLECTION = os.getenv('VC_LENS_COLLECTION', 'vc_lens_collection')

# Global clients
_mongodb_client: Optional[pymongo.MongoClient] = None
_vector_db_client: Optional[chromadb.Client] = None
_vc_lens_collection: Optional[chromadb.Collection] = None


def get_mongodb_client() -> pymongo.MongoClient:
    """Get MongoDB client instance"""
    global _mongodb_client
    
    if _mongodb_client is None:
        try:
            _mongodb_client = pymongo.MongoClient(MONGODB_URI)
            logger.info(f"Successfully connected to MongoDB at {MONGODB_URI}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    return _mongodb_client


def get_vector_db_client() -> chromadb.Client:
    """Get Vector Database client instance"""
    global _vector_db_client
    
    if _vector_db_client is None:
        try:
            _vector_db_client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
            logger.info(f"Successfully connected to Vector DB at {VECTOR_DB_PATH}")
        except Exception as e:
            logger.error(f"Failed to connect to Vector DB: {str(e)}")
            raise
    
    return _vector_db_client


def get_vc_lens_collection() -> chromadb.Collection:
    """Get VC Lens collection from Vector Database"""
    global _vc_lens_collection
    
    if _vc_lens_collection is None:
        try:
            client = get_vector_db_client()
            _vc_lens_collection = client.get_or_create_collection(
                name=VC_LENS_COLLECTION,
                metadata={"description": "VC Lens document embeddings and analysis"}
            )
            logger.info(f"Successfully connected to VC Lens collection: {VC_LENS_COLLECTION}")
        except Exception as e:
            logger.error(f"Failed to connect to VC Lens collection: {str(e)}")
            raise
    
    return _vc_lens_collection


def close_connections():
    """Close all database connections"""
    global _mongodb_client, _vector_db_client
    
    if _mongodb_client:
        try:
            _mongodb_client.close()
            logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {str(e)}")
        finally:
            _mongodb_client = None
    
    if _vector_db_client:
        # ChromaDB doesn't require explicit connection closing
        logger.info("Vector DB connection released")
        _vector_db_client = None 