"""
MongoDB Metrics Operations for SustainaTrend™ platform
Provides functions for storing and retrieving sustainability metrics data from MongoDB
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from bson import ObjectId

from mongo_client import (
    metrics_collection, serialize_document,
    async_metrics_collection
)

# Configure logging
logger = logging.getLogger(__name__)


def insert_metric(metric_data: Dict[str, Any]) -> str:
    """
    Insert a new sustainability metric into MongoDB
    
    Args:
        metric_data (Dict[str, Any]): Metric data to insert
            Must include name, category, value fields
            
    Returns:
        str: ID of inserted document
    """
    try:
        # Ensure timestamp exists
        if 'timestamp' not in metric_data:
            metric_data['timestamp'] = datetime.now()
            
        # Insert the document
        collection = metrics_collection()
        result = collection.insert_one(metric_data)
        
        logger.info(f"Inserted metric: {metric_data['name']} with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error inserting metric: {str(e)}")
        raise


async def async_insert_metric(metric_data: Dict[str, Any]) -> str:
    """
    Insert a new sustainability metric into MongoDB (async version)
    
    Args:
        metric_data (Dict[str, Any]): Metric data to insert
            Must include name, category, value fields
            
    Returns:
        str: ID of inserted document
    """
    try:
        # Ensure timestamp exists
        if 'timestamp' not in metric_data:
            metric_data['timestamp'] = datetime.now()
            
        # Insert the document
        collection = await async_metrics_collection()
        result = await collection.insert_one(metric_data)
        
        logger.info(f"Inserted metric async: {metric_data['name']} with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error inserting metric async: {str(e)}")
        raise


def get_metrics(
    category: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Get sustainability metrics from MongoDB with optional filtering
    
    Args:
        category (str, optional): Filter by category
        start_date (datetime, optional): Filter by minimum date
        end_date (datetime, optional): Filter by maximum date
        limit (int, optional): Maximum number of metrics to return
        
    Returns:
        List[Dict[str, Any]]: List of metrics
    """
    try:
        # Build query
        query = {}
        if category:
            query['category'] = category
            
        # Add date range if specified
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query['$gte'] = start_date
            if end_date:
                date_query['$lte'] = end_date
            if date_query:
                query['timestamp'] = date_query
        
        # Execute query
        collection = metrics_collection()
        cursor = collection.find(query).sort('timestamp', -1).limit(limit)
        
        # Serialize documents
        return [serialize_document(doc) for doc in cursor]
    except Exception as e:
        logger.error(f"Error fetching metrics: {str(e)}")
        return []


async def async_get_metrics(
    category: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Get sustainability metrics from MongoDB with optional filtering (async version)
    
    Args:
        category (str, optional): Filter by category
        start_date (datetime, optional): Filter by minimum date
        end_date (datetime, optional): Filter by maximum date
        limit (int, optional): Maximum number of metrics to return
        
    Returns:
        List[Dict[str, Any]]: List of metrics
    """
    try:
        # Build query
        query = {}
        if category:
            query['category'] = category
            
        # Add date range if specified
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query['$gte'] = start_date
            if end_date:
                date_query['$lte'] = end_date
            if date_query:
                query['timestamp'] = date_query
        
        # Execute query
        collection = await async_metrics_collection()
        cursor = collection.find(query).sort('timestamp', -1).limit(limit)
        
        # Serialize documents
        metrics = []
        async for doc in cursor:
            metrics.append(serialize_document(doc))
        
        return metrics
    except Exception as e:
        logger.error(f"Error fetching metrics async: {str(e)}")
        return []


def get_metric_by_id(metric_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific metric by ID
    
    Args:
        metric_id (str): Metric ID
        
    Returns:
        Optional[Dict[str, Any]]: Metric data or None if not found
    """
    try:
        collection = metrics_collection()
        doc = collection.find_one({'_id': ObjectId(metric_id)})
        return serialize_document(doc) if doc else None
    except Exception as e:
        logger.error(f"Error fetching metric by ID: {str(e)}")
        return None


async def async_get_metric_by_id(metric_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific metric by ID (async version)
    
    Args:
        metric_id (str): Metric ID
        
    Returns:
        Optional[Dict[str, Any]]: Metric data or None if not found
    """
    try:
        collection = await async_metrics_collection()
        doc = await collection.find_one({'_id': ObjectId(metric_id)})
        return serialize_document(doc) if doc else None
    except Exception as e:
        logger.error(f"Error fetching metric by ID async: {str(e)}")
        return None


def update_metric(metric_id: str, update_data: Dict[str, Any]) -> bool:
    """
    Update a metric by ID
    
    Args:
        metric_id (str): Metric ID
        update_data (Dict[str, Any]): Data to update
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        collection = metrics_collection()
        result = collection.update_one(
            {'_id': ObjectId(metric_id)},
            {'$set': update_data}
        )
        
        success = result.modified_count > 0
        if success:
            logger.info(f"Updated metric with ID: {metric_id}")
        else:
            logger.warning(f"No metric found with ID: {metric_id}")
        
        return success
    except Exception as e:
        logger.error(f"Error updating metric: {str(e)}")
        return False


async def async_update_metric(metric_id: str, update_data: Dict[str, Any]) -> bool:
    """
    Update a metric by ID (async version)
    
    Args:
        metric_id (str): Metric ID
        update_data (Dict[str, Any]): Data to update
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        collection = await async_metrics_collection()
        result = await collection.update_one(
            {'_id': ObjectId(metric_id)},
            {'$set': update_data}
        )
        
        success = result.modified_count > 0
        if success:
            logger.info(f"Updated metric async with ID: {metric_id}")
        else:
            logger.warning(f"No metric found with ID: {metric_id}")
        
        return success
    except Exception as e:
        logger.error(f"Error updating metric async: {str(e)}")
        return False


def delete_metric(metric_id: str) -> bool:
    """
    Delete a metric by ID
    
    Args:
        metric_id (str): Metric ID
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        collection = metrics_collection()
        result = collection.delete_one({'_id': ObjectId(metric_id)})
        
        success = result.deleted_count > 0
        if success:
            logger.info(f"Deleted metric with ID: {metric_id}")
        else:
            logger.warning(f"No metric found with ID: {metric_id}")
        
        return success
    except Exception as e:
        logger.error(f"Error deleting metric: {str(e)}")
        return False


async def async_delete_metric(metric_id: str) -> bool:
    """
    Delete a metric by ID (async version)
    
    Args:
        metric_id (str): Metric ID
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        collection = await async_metrics_collection()
        result = await collection.delete_one({'_id': ObjectId(metric_id)})
        
        success = result.deleted_count > 0
        if success:
            logger.info(f"Deleted metric async with ID: {metric_id}")
        else:
            logger.warning(f"No metric found with ID: {metric_id}")
        
        return success
    except Exception as e:
        logger.error(f"Error deleting metric async: {str(e)}")
        return False


def get_categories() -> List[str]:
    """
    Get all unique categories from the metrics collection
    
    Returns:
        List[str]: List of unique categories
    """
    try:
        collection = metrics_collection()
        result = collection.distinct("category")
        return result
    except Exception as e:
        logger.error(f"Error getting metric categories: {str(e)}")
        return []


async def async_get_categories() -> List[str]:
    """
    Get all unique categories from the metrics collection (async version)
    
    Returns:
        List[str]: List of unique categories
    """
    try:
        collection = await async_metrics_collection()
        result = await collection.distinct("category")
        return result
    except Exception as e:
        logger.error(f"Error getting metric categories async: {str(e)}")
        return []


def bulk_insert_metrics(metrics: List[Dict[str, Any]]) -> int:
    """
    Insert multiple metrics at once
    
    Args:
        metrics (List[Dict[str, Any]]): List of metrics to insert
        
    Returns:
        int: Number of metrics inserted
    """
    try:
        # Ensure each metric has a timestamp
        for metric in metrics:
            if 'timestamp' not in metric:
                metric['timestamp'] = datetime.now()
        
        collection = metrics_collection()
        result = collection.insert_many(metrics)
        
        count = len(result.inserted_ids)
        logger.info(f"Bulk inserted {count} metrics")
        return count
    except Exception as e:
        logger.error(f"Error bulk inserting metrics: {str(e)}")
        return 0


async def async_bulk_insert_metrics(metrics: List[Dict[str, Any]]) -> int:
    """
    Insert multiple metrics at once (async version)
    
    Args:
        metrics (List[Dict[str, Any]]): List of metrics to insert
        
    Returns:
        int: Number of metrics inserted
    """
    try:
        # Ensure each metric has a timestamp
        for metric in metrics:
            if 'timestamp' not in metric:
                metric['timestamp'] = datetime.now()
        
        collection = await async_metrics_collection()
        result = await collection.insert_many(metrics)
        
        count = len(result.inserted_ids)
        logger.info(f"Bulk inserted {count} metrics async")
        return count
    except Exception as e:
        logger.error(f"Error bulk inserting metrics async: {str(e)}")
        return 0


def get_metrics_count(category: Optional[str] = None) -> int:
    """
    Get the count of metrics, optionally filtered by category
    
    Args:
        category (str, optional): Category to filter by
        
    Returns:
        int: Count of metrics
    """
    try:
        collection = metrics_collection()
        query = {'category': category} if category else {}
        return collection.count_documents(query)
    except Exception as e:
        logger.error(f"Error getting metrics count: {str(e)}")
        return 0


async def async_get_metrics_count(category: Optional[str] = None) -> int:
    """
    Get the count of metrics, optionally filtered by category (async version)
    
    Args:
        category (str, optional): Category to filter by
        
    Returns:
        int: Count of metrics
    """
    try:
        collection = await async_metrics_collection()
        query = {'category': category} if category else {}
        return await collection.count_documents(query)
    except Exception as e:
        logger.error(f"Error getting metrics count async: {str(e)}")
        return 0