"""
Story Operations Module for SustainaTrend™ Intelligence Platform

This module provides functions for CRUD operations on sustainability stories,
with support for both Pinecone vector database and fallback mechanisms.
"""

import os
import logging
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

# Initialize logging
logger = logging.getLogger(__name__)

# Configure storage variables
PINECONE_AVAILABLE = os.getenv("PINECONE_API_KEY") is not None
OPENAI_AVAILABLE = os.getenv("OPENAI_API_KEY") is not None
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "multilingual-e5-large")

# In-memory storage for fallback
_stories_cache = []

def update_story_in_pinecone(story_id: str, story_data: Dict[str, Any]) -> bool:
    """
    Update a story in Pinecone
    
    Args:
        story_id: UUID of the story
        story_data: Dictionary with story data
        
    Returns:
        Boolean indicating success
    """
    if not PINECONE_AVAILABLE or not OPENAI_AVAILABLE:
        return False
    
    try:
        from pinecone import Pinecone
        import openai
        
        # Create Pinecone client
        pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        
        # Get OpenAI client
        openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Create a copy of the story data to use as metadata
        metadata = story_data.copy()
        
        # Make sure the story ID is not in the metadata (it's used as the vector ID)
        if 'id' in metadata:
            del metadata['id']
        
        # Generate embedding for the story content
        story_text = f"{story_data.get('title', 'Sustainability Story')}\n\n{story_data.get('content', '')}"
        
        # Get embedding
        response = openai_client.embeddings.create(
            input=story_text,
            model="text-embedding-ada-002"
        )
        embedding = response.data[0].embedding
        
        # Update the vector in Pinecone
        try:
            index = pinecone_client.Index(INDEX_NAME)
            index.upsert(vectors=[
                {"id": story_id, "values": embedding, "metadata": metadata}
            ])
            logger.info(f"Successfully updated story {story_id} in Pinecone")
            return True
        except Exception as e:
            logger.error(f"Error updating story in Pinecone: {e}")
    except Exception as e:
        logger.error(f"Error connecting to Pinecone/OpenAI for story update: {e}")
    
    return False

def update_story(story_id: str, story_data: Dict[str, Any]) -> bool:
    """
    Update a story in storage
    
    Args:
        story_id: UUID of the story
        story_data: Dictionary with story data
        
    Returns:
        Boolean indicating success
    """
    # Update in-memory cache
    global _stories_cache
    
    # Try to update in Pinecone if available
    if PINECONE_AVAILABLE and OPENAI_AVAILABLE:
        try:
            if update_story_in_pinecone(story_id, story_data):
                # Also update in memory so we have it for this session
                for i, story in enumerate(_stories_cache):
                    if story.get('id') == story_id:
                        _stories_cache[i] = story_data
                        break
                return True
        except Exception as e:
            logger.error(f"Error updating story in Pinecone: {e}")
    
    # Try to update in MongoDB if integrated
    try:
        from mongo_stories import update_story as mongo_update
        result = mongo_update(story_id, story_data)
        if result:
            # Also update in memory
            for i, story in enumerate(_stories_cache):
                if story.get('id') == story_id:
                    _stories_cache[i] = story_data
                    break
            logger.info(f"Updated story {story_id} in MongoDB")
            return True
    except Exception as e:
        logger.warning(f"Could not update story in MongoDB: {str(e)}")
    
    # Fallback to in-memory update only
    try:
        found = False
        for i, story in enumerate(_stories_cache):
            if str(story.get('id')) == str(story_id):
                _stories_cache[i] = story_data
                found = True
                break
        
        if not found:
            # Add to cache if not found
            _stories_cache.append(story_data)
        
        logger.info(f"Updated story {story_id} in memory cache")
        return True
    except Exception as e:
        logger.error(f"Error updating story in memory: {e}")
    
    return False

def get_story_from_pinecone(story_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a story from Pinecone by ID
    
    Args:
        story_id: UUID of the story to retrieve
        
    Returns:
        Story dictionary or None if not found
    """
    if not PINECONE_AVAILABLE or not OPENAI_AVAILABLE:
        return None
    
    try:
        from pinecone import Pinecone
        
        # Create Pinecone client
        pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        
        # Query Pinecone for the story by ID
        try:
            index = pinecone_client.Index(INDEX_NAME)
            result = index.fetch(ids=[story_id])
            
            if result.vectors and story_id in result.vectors:
                # Extract metadata (the story content)
                story = result.vectors[story_id].metadata
                
                # Ensure the story has an ID
                if story:
                    story['id'] = story_id
                    return story
        except Exception as e:
            logger.error(f"Error fetching story from Pinecone: {e}")
    except Exception as e:
        logger.error(f"Error connecting to Pinecone for story retrieval: {e}")
    
    return None

def get_story_by_id(story_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a story by ID from any available storage
    
    Args:
        story_id: UUID of the story
        
    Returns:
        Story dictionary or None if not found
    """
    # First check in-memory cache
    global _stories_cache
    for story in _stories_cache:
        if str(story.get('id')) == str(story_id):
            return story
    
    # Try to get from Pinecone
    if PINECONE_AVAILABLE and OPENAI_AVAILABLE:
        story = get_story_from_pinecone(story_id)
        if story:
            # Add to cache for future use
            _stories_cache.append(story)
            return story
    
    # Try to get from MongoDB
    try:
        from mongo_stories import get_story_by_id as mongo_get
        story = mongo_get(story_id)
        if story:
            # Add to cache for future use
            _stories_cache.append(story)
            return story
    except Exception as e:
        logger.warning(f"Could not get story from MongoDB: {str(e)}")
    
    # If not found, return None
    return None

def save_new_story(story_data: Dict[str, Any]) -> str:
    """
    Save a new story to storage
    
    Args:
        story_data: Dictionary with story data
        
    Returns:
        ID of the new story
    """
    # Generate a new ID if not provided
    if 'id' not in story_data:
        story_id = str(uuid.uuid4())
        story_data['id'] = story_id
    else:
        story_id = str(story_data['id'])
    
    # Make sure timestamp is set
    if 'timestamp' not in story_data:
        story_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Save to storage
    if update_story(story_id, story_data):
        return story_id
    
    return story_id  # Return the ID even if save failed

def delete_story(story_id: str) -> bool:
    """
    Delete a story from storage
    
    Args:
        story_id: UUID of the story
        
    Returns:
        Boolean indicating success
    """
    success = False
    
    # Delete from Pinecone if available
    if PINECONE_AVAILABLE and OPENAI_AVAILABLE:
        try:
            from pinecone import Pinecone
            
            # Create Pinecone client
            pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            
            # Delete from Pinecone
            try:
                index = pinecone_client.Index(INDEX_NAME)
                index.delete(ids=[story_id])
                logger.info(f"Deleted story {story_id} from Pinecone")
                success = True
            except Exception as e:
                logger.error(f"Error deleting story from Pinecone: {e}")
        except Exception as e:
            logger.error(f"Error connecting to Pinecone for story deletion: {e}")
    
    # Delete from MongoDB if integrated
    try:
        from mongo_stories import delete_story as mongo_delete
        result = mongo_delete(story_id)
        if result:
            logger.info(f"Deleted story {story_id} from MongoDB")
            success = True
    except Exception as e:
        logger.warning(f"Could not delete story from MongoDB: {str(e)}")
    
    # Delete from in-memory cache
    global _stories_cache
    _stories_cache = [s for s in _stories_cache if str(s.get('id')) != str(story_id)]
    
    return success