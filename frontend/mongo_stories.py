"""
MongoDB Stories Operations for SustainaTrend™ platform
Provides functions for storing and retrieving sustainability stories data from MongoDB
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from bson import ObjectId

from frontend.mongo_client import (
    stories_collection, serialize_document,
    async_stories_collection
)

# Configure logging
logger = logging.getLogger(__name__)


def insert_story(story_data: Dict[str, Any]) -> str:
    """
    Insert a new sustainability story into MongoDB
    
    Args:
        story_data (Dict[str, Any]): Story data to insert
            Must include title, content fields
            
    Returns:
        str: ID of inserted document
    """
    try:
        # Ensure publication_date exists
        if 'publication_date' not in story_data:
            story_data['publication_date'] = datetime.now()
            
        # Insert the document
        collection = stories_collection()
        result = collection.insert_one(story_data)
        
        logger.info(f"Inserted story: {story_data['title']} with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error inserting story: {str(e)}")
        raise


async def async_insert_story(story_data: Dict[str, Any]) -> str:
    """
    Insert a new sustainability story into MongoDB (async version)
    
    Args:
        story_data (Dict[str, Any]): Story data to insert
            Must include title, content fields
            
    Returns:
        str: ID of inserted document
    """
    try:
        # Ensure publication_date exists
        if 'publication_date' not in story_data:
            story_data['publication_date'] = datetime.now()
            
        # Insert the document
        collection = await async_stories_collection()
        result = await collection.insert_one(story_data)
        
        logger.info(f"Inserted story async: {story_data['title']} with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error inserting story async: {str(e)}")
        raise


def get_stories(
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 50,
    skip: int = 0
) -> List[Dict[str, Any]]:
    """
    Get sustainability stories from MongoDB with optional filtering
    
    Args:
        category (str, optional): Filter by category
        tags (List[str], optional): Filter by tags
        start_date (datetime, optional): Filter by minimum publication date
        end_date (datetime, optional): Filter by maximum publication date
        limit (int, optional): Maximum number of stories to return
        skip (int, optional): Number of stories to skip (for pagination)
        
    Returns:
        List[Dict[str, Any]]: List of stories
    """
    try:
        # Build query
        query = {}
        if category:
            query['category'] = category
            
        if tags:
            query['tags'] = {'$in': tags}
            
        # Add date range if specified
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query['$gte'] = start_date
            if end_date:
                date_query['$lte'] = end_date
            if date_query:
                query['publication_date'] = date_query
        
        # Execute query
        collection = stories_collection()
        cursor = collection.find(query).sort('publication_date', -1).skip(skip).limit(limit)
        
        # Serialize documents
        return [serialize_document(doc) for doc in cursor]
    except Exception as e:
        logger.error(f"Error fetching stories: {str(e)}")
        return []


async def async_get_stories(
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 50,
    skip: int = 0
) -> List[Dict[str, Any]]:
    """
    Get sustainability stories from MongoDB with optional filtering (async version)
    
    Args:
        category (str, optional): Filter by category
        tags (List[str], optional): Filter by tags
        start_date (datetime, optional): Filter by minimum publication date
        end_date (datetime, optional): Filter by maximum publication date
        limit (int, optional): Maximum number of stories to return
        skip (int, optional): Number of stories to skip (for pagination)
        
    Returns:
        List[Dict[str, Any]]: List of stories
    """
    try:
        # Build query
        query = {}
        if category:
            query['category'] = category
            
        if tags:
            query['tags'] = {'$in': tags}
            
        # Add date range if specified
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query['$gte'] = start_date
            if end_date:
                date_query['$lte'] = end_date
            if date_query:
                query['publication_date'] = date_query
        
        # Execute query
        collection = await async_stories_collection()
        cursor = collection.find(query).sort('publication_date', -1).skip(skip).limit(limit)
        
        # Serialize documents
        stories = []
        async for doc in cursor:
            stories.append(serialize_document(doc))
        
        return stories
    except Exception as e:
        logger.error(f"Error fetching stories async: {str(e)}")
        return []


def get_story_by_id(story_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific story by ID
    
    Args:
        story_id (str): Story ID
        
    Returns:
        Optional[Dict[str, Any]]: Story data or None if not found
    """
    try:
        collection = stories_collection()
        doc = collection.find_one({'_id': ObjectId(story_id)})
        return serialize_document(doc) if doc else None
    except Exception as e:
        logger.error(f"Error fetching story by ID: {str(e)}")
        return None


async def async_get_story_by_id(story_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific story by ID (async version)
    
    Args:
        story_id (str): Story ID
        
    Returns:
        Optional[Dict[str, Any]]: Story data or None if not found
    """
    try:
        collection = await async_stories_collection()
        doc = await collection.find_one({'_id': ObjectId(story_id)})
        return serialize_document(doc) if doc else None
    except Exception as e:
        logger.error(f"Error fetching story by ID async: {str(e)}")
        return None


def update_story(story_id: str, update_data: Dict[str, Any]) -> bool:
    """
    Update a story by ID
    
    Args:
        story_id (str): Story ID
        update_data (Dict[str, Any]): Data to update
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        collection = stories_collection()
        result = collection.update_one(
            {'_id': ObjectId(story_id)},
            {'$set': update_data}
        )
        
        success = result.modified_count > 0
        if success:
            logger.info(f"Updated story with ID: {story_id}")
        else:
            logger.warning(f"No story found with ID: {story_id}")
        
        return success
    except Exception as e:
        logger.error(f"Error updating story: {str(e)}")
        return False


async def async_update_story(story_id: str, update_data: Dict[str, Any]) -> bool:
    """
    Update a story by ID (async version)
    
    Args:
        story_id (str): Story ID
        update_data (Dict[str, Any]): Data to update
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        collection = await async_stories_collection()
        result = await collection.update_one(
            {'_id': ObjectId(story_id)},
            {'$set': update_data}
        )
        
        success = result.modified_count > 0
        if success:
            logger.info(f"Updated story async with ID: {story_id}")
        else:
            logger.warning(f"No story found with ID: {story_id}")
        
        return success
    except Exception as e:
        logger.error(f"Error updating story async: {str(e)}")
        return False


def delete_story(story_id: str) -> bool:
    """
    Delete a story by ID
    
    Args:
        story_id (str): Story ID
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        collection = stories_collection()
        result = collection.delete_one({'_id': ObjectId(story_id)})
        
        success = result.deleted_count > 0
        if success:
            logger.info(f"Deleted story with ID: {story_id}")
        else:
            logger.warning(f"No story found with ID: {story_id}")
        
        return success
    except Exception as e:
        logger.error(f"Error deleting story: {str(e)}")
        return False


async def async_delete_story(story_id: str) -> bool:
    """
    Delete a story by ID (async version)
    
    Args:
        story_id (str): Story ID
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        collection = await async_stories_collection()
        result = await collection.delete_one({'_id': ObjectId(story_id)})
        
        success = result.deleted_count > 0
        if success:
            logger.info(f"Deleted story async with ID: {story_id}")
        else:
            logger.warning(f"No story found with ID: {story_id}")
        
        return success
    except Exception as e:
        logger.error(f"Error deleting story async: {str(e)}")
        return False


def get_story_count(category: Optional[str] = None, tags: Optional[List[str]] = None) -> int:
    """
    Get the count of stories, optionally filtered by category and/or tags
    
    Args:
        category (str, optional): Category to filter by
        tags (List[str], optional): Tags to filter by
        
    Returns:
        int: Count of stories
    """
    try:
        collection = stories_collection()
        query = {}
        
        if category:
            query['category'] = category
            
        if tags:
            query['tags'] = {'$in': tags}
            
        return collection.count_documents(query)
    except Exception as e:
        logger.error(f"Error getting story count: {str(e)}")
        return 0


async def async_get_story_count(category: Optional[str] = None, tags: Optional[List[str]] = None) -> int:
    """
    Get the count of stories, optionally filtered by category and/or tags (async version)
    
    Args:
        category (str, optional): Category to filter by
        tags (List[str], optional): Tags to filter by
        
    Returns:
        int: Count of stories
    """
    try:
        collection = await async_stories_collection()
        query = {}
        
        if category:
            query['category'] = category
            
        if tags:
            query['tags'] = {'$in': tags}
            
        return await collection.count_documents(query)
    except Exception as e:
        logger.error(f"Error getting story count async: {str(e)}")
        return 0


def get_popular_tags(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get the most popular tags used in stories
    
    Args:
        limit (int, optional): Maximum number of tags to return
        
    Returns:
        List[Dict[str, Any]]: List of tags with counts
    """
    try:
        collection = stories_collection()
        pipeline = [
            {'$unwind': '$tags'},
            {'$group': {'_id': '$tags', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': limit},
            {'$project': {'tag': '$_id', 'count': 1, '_id': 0}}
        ]
        
        result = list(collection.aggregate(pipeline))
        return result
    except Exception as e:
        logger.error(f"Error getting popular tags: {str(e)}")
        return []


async def async_get_popular_tags(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get the most popular tags used in stories (async version)
    
    Args:
        limit (int, optional): Maximum number of tags to return
        
    Returns:
        List[Dict[str, Any]]: List of tags with counts
    """
    try:
        collection = await async_stories_collection()
        pipeline = [
            {'$unwind': '$tags'},
            {'$group': {'_id': '$tags', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': limit},
            {'$project': {'tag': '$_id', 'count': 1, '_id': 0}}
        ]
        
        result = []
        async for doc in collection.aggregate(pipeline):
            result.append(doc)
            
        return result
    except Exception as e:
        logger.error(f"Error getting popular tags async: {str(e)}")
        return []


def search_stories(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search stories by text content
    
    Args:
        query (str): Search query text
        limit (int, optional): Maximum number of results to return
        
    Returns:
        List[Dict[str, Any]]: List of matching stories
    """
    try:
        collection = stories_collection()
        # Create text index if it doesn't exist
        collection.create_index([('title', 'text'), ('content', 'text'), ('summary', 'text')])
        
        # Execute text search
        cursor = collection.find(
            {'$text': {'$search': query}},
            {'score': {'$meta': 'textScore'}}
        ).sort([('score', {'$meta': 'textScore'})]).limit(limit)
        
        return [serialize_document(doc) for doc in cursor]
    except Exception as e:
        logger.error(f"Error searching stories: {str(e)}")
        return []


async def async_search_stories(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search stories by text content (async version)
    
    Args:
        query (str): Search query text
        limit (int, optional): Maximum number of results to return
        
    Returns:
        List[Dict[str, Any]]: List of matching stories
    """
    try:
        collection = await async_stories_collection()
        # Create text index if it doesn't exist
        await collection.create_index([('title', 'text'), ('content', 'text'), ('summary', 'text')])
        
        # Execute text search
        cursor = collection.find(
            {'$text': {'$search': query}},
            {'score': {'$meta': 'textScore'}}
        ).sort([('score', {'$meta': 'textScore'})]).limit(limit)
        
        result = []
        async for doc in cursor:
            result.append(serialize_document(doc))
            
        return result
    except Exception as e:
        logger.error(f"Error searching stories async: {str(e)}")
        return []


def bulk_insert_stories(stories: List[Dict[str, Any]]) -> int:
    """
    Insert multiple stories at once
    
    Args:
        stories (List[Dict[str, Any]]): List of stories to insert
        
    Returns:
        int: Number of stories inserted
    """
    try:
        # Ensure each story has a publication_date
        for story in stories:
            if 'publication_date' not in story:
                story['publication_date'] = datetime.now()
        
        collection = stories_collection()
        result = collection.insert_many(stories)
        
        count = len(result.inserted_ids)
        logger.info(f"Bulk inserted {count} stories")
        return count
    except Exception as e:
        logger.error(f"Error bulk inserting stories: {str(e)}")
        return 0


async def async_bulk_insert_stories(stories: List[Dict[str, Any]]) -> int:
    """
    Insert multiple stories at once (async version)
    
    Args:
        stories (List[Dict[str, Any]]): List of stories to insert
        
    Returns:
        int: Number of stories inserted
    """
    try:
        # Ensure each story has a publication_date
        for story in stories:
            if 'publication_date' not in story:
                story['publication_date'] = datetime.now()
        
        collection = await async_stories_collection()
        result = await collection.insert_many(stories)
        
        count = len(result.inserted_ids)
        logger.info(f"Bulk inserted {count} stories async")
        return count
    except Exception as e:
        logger.error(f"Error bulk inserting stories async: {str(e)}")
        return 0