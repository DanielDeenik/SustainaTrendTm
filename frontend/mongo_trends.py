"""
MongoDB Trend Operations for SustainaTrend™ platform
Provides functions for storing and retrieving sustainability trend data from MongoDB
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from bson import ObjectId

from frontend.mongo_client import (
    trends_collection, serialize_document,
    async_trends_collection
)

# Configure logging
logger = logging.getLogger(__name__)


def insert_trend(trend_data: Dict[str, Any]) -> str:
    """
    Insert a new sustainability trend into MongoDB
    
    Args:
        trend_data (Dict[str, Any]): Trend data to insert
            Must include name, category, virality_score fields
            
    Returns:
        str: ID of inserted document
    """
    try:
        # Ensure created_at exists
        if 'created_at' not in trend_data:
            trend_data['created_at'] = datetime.now()
            
        # Insert the document
        collection = trends_collection()
        result = collection.insert_one(trend_data)
        
        logger.info(f"Inserted trend: {trend_data['name']} with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error inserting trend: {str(e)}")
        raise


async def async_insert_trend(trend_data: Dict[str, Any]) -> str:
    """
    Insert a new sustainability trend into MongoDB (async version)
    
    Args:
        trend_data (Dict[str, Any]): Trend data to insert
            Must include name, category, virality_score fields
            
    Returns:
        str: ID of inserted document
    """
    try:
        # Ensure created_at exists
        if 'created_at' not in trend_data:
            trend_data['created_at'] = datetime.now()
            
        # Insert the document
        collection = await async_trends_collection()
        result = await collection.insert_one(trend_data)
        
        logger.info(f"Inserted trend async: {trend_data['name']} with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error inserting trend async: {str(e)}")
        raise


def get_trends(
    category: Optional[str] = None,
    min_virality: Optional[float] = None,
    timeframe: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Get sustainability trends from MongoDB with optional filtering
    
    Args:
        category (str, optional): Filter by category
        min_virality (float, optional): Minimum virality score
        timeframe (str, optional): Timeframe filter ('week', 'month', 'quarter', 'year')
        limit (int, optional): Maximum number of trends to return
        
    Returns:
        List[Dict[str, Any]]: List of trends
    """
    try:
        # Build query
        query = {}
        if category:
            query['category'] = category
            
        if min_virality is not None:
            query['virality_score'] = {'$gte': min_virality}
            
        # Add timeframe filter if specified
        if timeframe:
            date_query = {}
            now = datetime.now()
            
            if timeframe == 'week':
                # Last 7 days
                date_query['$gte'] = datetime(now.year, now.month, now.day - 7)
            elif timeframe == 'month':
                # Last 30 days
                date_query['$gte'] = datetime(now.year, now.month - 1, now.day)
            elif timeframe == 'quarter':
                # Last 90 days
                date_query['$gte'] = datetime(now.year, now.month - 3, now.day)
            elif timeframe == 'year':
                # Last 365 days
                date_query['$gte'] = datetime(now.year - 1, now.month, now.day)
                
            if date_query:
                query['created_at'] = date_query
        
        # Execute query
        collection = trends_collection()
        cursor = collection.find(query).sort('virality_score', -1).limit(limit)
        
        # Serialize documents
        return [serialize_document(doc) for doc in cursor]
    except Exception as e:
        logger.error(f"Error fetching trends: {str(e)}")
        return []


async def async_get_trends(
    category: Optional[str] = None,
    min_virality: Optional[float] = None,
    timeframe: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Get sustainability trends from MongoDB with optional filtering (async version)
    
    Args:
        category (str, optional): Filter by category
        min_virality (float, optional): Minimum virality score
        timeframe (str, optional): Timeframe filter ('week', 'month', 'quarter', 'year')
        limit (int, optional): Maximum number of trends to return
        
    Returns:
        List[Dict[str, Any]]: List of trends
    """
    try:
        # Build query
        query = {}
        if category:
            query['category'] = category
            
        if min_virality is not None:
            query['virality_score'] = {'$gte': min_virality}
            
        # Add timeframe filter if specified
        if timeframe:
            date_query = {}
            now = datetime.now()
            
            if timeframe == 'week':
                # Last 7 days
                date_query['$gte'] = datetime(now.year, now.month, now.day - 7)
            elif timeframe == 'month':
                # Last 30 days
                date_query['$gte'] = datetime(now.year, now.month - 1, now.day)
            elif timeframe == 'quarter':
                # Last 90 days
                date_query['$gte'] = datetime(now.year, now.month - 3, now.day)
            elif timeframe == 'year':
                # Last 365 days
                date_query['$gte'] = datetime(now.year - 1, now.month, now.day)
                
            if date_query:
                query['created_at'] = date_query
        
        # Execute query
        collection = await async_trends_collection()
        cursor = collection.find(query).sort('virality_score', -1).limit(limit)
        
        # Serialize documents
        trends = []
        async for doc in cursor:
            trends.append(serialize_document(doc))
        
        return trends
    except Exception as e:
        logger.error(f"Error fetching trends async: {str(e)}")
        return []


def get_trend_by_id(trend_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific trend by ID
    
    Args:
        trend_id (str): Trend ID
        
    Returns:
        Optional[Dict[str, Any]]: Trend data or None if not found
    """
    try:
        collection = trends_collection()
        doc = collection.find_one({'_id': ObjectId(trend_id)})
        return serialize_document(doc) if doc else None
    except Exception as e:
        logger.error(f"Error fetching trend by ID: {str(e)}")
        return None


async def async_get_trend_by_id(trend_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific trend by ID (async version)
    
    Args:
        trend_id (str): Trend ID
        
    Returns:
        Optional[Dict[str, Any]]: Trend data or None if not found
    """
    try:
        collection = await async_trends_collection()
        doc = await collection.find_one({'_id': ObjectId(trend_id)})
        return serialize_document(doc) if doc else None
    except Exception as e:
        logger.error(f"Error fetching trend by ID async: {str(e)}")
        return None


def update_trend(trend_id: str, update_data: Dict[str, Any]) -> bool:
    """
    Update a trend by ID
    
    Args:
        trend_id (str): Trend ID
        update_data (Dict[str, Any]): Data to update
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        collection = trends_collection()
        result = collection.update_one(
            {'_id': ObjectId(trend_id)},
            {'$set': update_data}
        )
        
        success = result.modified_count > 0
        if success:
            logger.info(f"Updated trend with ID: {trend_id}")
        else:
            logger.warning(f"No trend found with ID: {trend_id}")
        
        return success
    except Exception as e:
        logger.error(f"Error updating trend: {str(e)}")
        return False


async def async_update_trend(trend_id: str, update_data: Dict[str, Any]) -> bool:
    """
    Update a trend by ID (async version)
    
    Args:
        trend_id (str): Trend ID
        update_data (Dict[str, Any]): Data to update
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        collection = await async_trends_collection()
        result = await collection.update_one(
            {'_id': ObjectId(trend_id)},
            {'$set': update_data}
        )
        
        success = result.modified_count > 0
        if success:
            logger.info(f"Updated trend async with ID: {trend_id}")
        else:
            logger.warning(f"No trend found with ID: {trend_id}")
        
        return success
    except Exception as e:
        logger.error(f"Error updating trend async: {str(e)}")
        return False


def delete_trend(trend_id: str) -> bool:
    """
    Delete a trend by ID
    
    Args:
        trend_id (str): Trend ID
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        collection = trends_collection()
        result = collection.delete_one({'_id': ObjectId(trend_id)})
        
        success = result.deleted_count > 0
        if success:
            logger.info(f"Deleted trend with ID: {trend_id}")
        else:
            logger.warning(f"No trend found with ID: {trend_id}")
        
        return success
    except Exception as e:
        logger.error(f"Error deleting trend: {str(e)}")
        return False


async def async_delete_trend(trend_id: str) -> bool:
    """
    Delete a trend by ID (async version)
    
    Args:
        trend_id (str): Trend ID
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        collection = await async_trends_collection()
        result = await collection.delete_one({'_id': ObjectId(trend_id)})
        
        success = result.deleted_count > 0
        if success:
            logger.info(f"Deleted trend async with ID: {trend_id}")
        else:
            logger.warning(f"No trend found with ID: {trend_id}")
        
        return success
    except Exception as e:
        logger.error(f"Error deleting trend async: {str(e)}")
        return False


def get_trending_categories() -> List[Dict[str, Any]]:
    """
    Get categories sorted by average virality score
    
    Returns:
        List[Dict[str, Any]]: List of categories with virality stats
    """
    try:
        collection = trends_collection()
        pipeline = [
            {
                '$group': {
                    '_id': '$category',
                    'avgVirality': {'$avg': '$virality_score'},
                    'count': {'$sum': 1}
                }
            },
            {
                '$sort': {'avgVirality': -1}
            },
            {
                '$project': {
                    'category': '$_id',
                    'avgVirality': 1,
                    'count': 1,
                    '_id': 0
                }
            }
        ]
        
        result = list(collection.aggregate(pipeline))
        return result
    except Exception as e:
        logger.error(f"Error getting trending categories: {str(e)}")
        return []


async def async_get_trending_categories() -> List[Dict[str, Any]]:
    """
    Get categories sorted by average virality score (async version)
    
    Returns:
        List[Dict[str, Any]]: List of categories with virality stats
    """
    try:
        collection = await async_trends_collection()
        pipeline = [
            {
                '$group': {
                    '_id': '$category',
                    'avgVirality': {'$avg': '$virality_score'},
                    'count': {'$sum': 1}
                }
            },
            {
                '$sort': {'avgVirality': -1}
            },
            {
                '$project': {
                    'category': '$_id',
                    'avgVirality': 1,
                    'count': 1,
                    '_id': 0
                }
            }
        ]
        
        result = []
        async for doc in collection.aggregate(pipeline):
            result.append(doc)
        
        return result
    except Exception as e:
        logger.error(f"Error getting trending categories async: {str(e)}")
        return []


def get_trend_time_series(category: Optional[str] = None, days: int = 30) -> List[Dict[str, Any]]:
    """
    Get trend virality scores over time as a time series
    
    Args:
        category (str, optional): Filter by category
        days (int, optional): Number of days to include
        
    Returns:
        List[Dict[str, Any]]: Time series data
    """
    try:
        collection = trends_collection()
        
        # Build match query
        match_query = {}
        if category:
            match_query['category'] = category
            
        # Add date range
        now = datetime.now()
        start_date = datetime(now.year, now.month, now.day - days)
        match_query['created_at'] = {'$gte': start_date}
        
        pipeline = [
            {'$match': match_query},
            {
                '$group': {
                    '_id': {
                        'year': {'$year': '$created_at'},
                        'month': {'$month': '$created_at'},
                        'day': {'$dayOfMonth': '$created_at'}
                    },
                    'avgVirality': {'$avg': '$virality_score'},
                    'count': {'$sum': 1}
                }
            },
            {'$sort': {'_id.year': 1, '_id.month': 1, '_id.day': 1}},
            {
                '$project': {
                    'date': {
                        '$dateFromParts': {
                            'year': '$_id.year',
                            'month': '$_id.month',
                            'day': '$_id.day'
                        }
                    },
                    'avgVirality': 1,
                    'count': 1,
                    '_id': 0
                }
            }
        ]
        
        result = list(collection.aggregate(pipeline))
        
        # Convert dates to strings for serialization
        for item in result:
            item['date'] = item['date'].isoformat()
            
        return result
    except Exception as e:
        logger.error(f"Error getting trend time series: {str(e)}")
        return []


async def async_get_trend_time_series(category: Optional[str] = None, days: int = 30) -> List[Dict[str, Any]]:
    """
    Get trend virality scores over time as a time series (async version)
    
    Args:
        category (str, optional): Filter by category
        days (int, optional): Number of days to include
        
    Returns:
        List[Dict[str, Any]]: Time series data
    """
    try:
        collection = await async_trends_collection()
        
        # Build match query
        match_query = {}
        if category:
            match_query['category'] = category
            
        # Add date range
        now = datetime.now()
        start_date = datetime(now.year, now.month, now.day - days)
        match_query['created_at'] = {'$gte': start_date}
        
        pipeline = [
            {'$match': match_query},
            {
                '$group': {
                    '_id': {
                        'year': {'$year': '$created_at'},
                        'month': {'$month': '$created_at'},
                        'day': {'$dayOfMonth': '$created_at'}
                    },
                    'avgVirality': {'$avg': '$virality_score'},
                    'count': {'$sum': 1}
                }
            },
            {'$sort': {'_id.year': 1, '_id.month': 1, '_id.day': 1}},
            {
                '$project': {
                    'date': {
                        '$dateFromParts': {
                            'year': '$_id.year',
                            'month': '$_id.month',
                            'day': '$_id.day'
                        }
                    },
                    'avgVirality': 1,
                    'count': 1,
                    '_id': 0
                }
            }
        ]
        
        result = []
        async for doc in collection.aggregate(pipeline):
            # Convert dates to strings for serialization
            doc['date'] = doc['date'].isoformat()
            result.append(doc)
            
        return result
    except Exception as e:
        logger.error(f"Error getting trend time series async: {str(e)}")
        return []


def bulk_insert_trends(trends: List[Dict[str, Any]]) -> int:
    """
    Insert multiple trends at once
    
    Args:
        trends (List[Dict[str, Any]]): List of trends to insert
        
    Returns:
        int: Number of trends inserted
    """
    try:
        # Ensure each trend has a created_at
        for trend in trends:
            if 'created_at' not in trend:
                trend['created_at'] = datetime.now()
        
        collection = trends_collection()
        result = collection.insert_many(trends)
        
        count = len(result.inserted_ids)
        logger.info(f"Bulk inserted {count} trends")
        return count
    except Exception as e:
        logger.error(f"Error bulk inserting trends: {str(e)}")
        return 0


async def async_bulk_insert_trends(trends: List[Dict[str, Any]]) -> int:
    """
    Insert multiple trends at once (async version)
    
    Args:
        trends (List[Dict[str, Any]]): List of trends to insert
        
    Returns:
        int: Number of trends inserted
    """
    try:
        # Ensure each trend has a created_at
        for trend in trends:
            if 'created_at' not in trend:
                trend['created_at'] = datetime.now()
        
        collection = await async_trends_collection()
        result = await collection.insert_many(trends)
        
        count = len(result.inserted_ids)
        logger.info(f"Bulk inserted {count} trends async")
        return count
    except Exception as e:
        logger.error(f"Error bulk inserting trends async: {str(e)}")
        return 0