"""
MongoDB Service Layer for SustainaTrend™

This module provides a standardized service layer for MongoDB operations,
ensuring consistent access patterns across the application.
"""

import logging
from typing import List, Dict, Any, Optional, Sequence
from datetime import datetime, timedelta

from frontend.mongo_client import (
    verify_connection, 
    get_database, 
    serialize_document,
    metrics_collection,
    trends_collection,
    stories_collection
)

# Configure logging
logger = logging.getLogger(__name__)

class MongoDBService:
    """Service class for standardized MongoDB operations"""
    
    @staticmethod
    def check_connection() -> bool:
        """
        Check if MongoDB connection is available
        
        Returns:
            bool: True if connection is available, False otherwise
        """
        try:
            return verify_connection()
        except Exception as e:
            logger.error(f"Error checking MongoDB connection: {str(e)}")
            return False
            
    @classmethod
    def get_metrics(
        cls,
        category: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get sustainability metrics with optional filtering
        
        Args:
            category: Filter by category (optional)
            start_date: Filter by minimum date (optional)
            end_date: Filter by maximum date (optional)
            limit: Maximum number of metrics to return
            
        Returns:
            List of metrics as dictionaries
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
            
            # Serialize documents and filter out None values
            metrics = []
            for doc in cursor:
                if doc is not None:
                    metrics.append(serialize_document(doc))
            
            logger.info(f"Retrieved {len(metrics)} metrics from MongoDB")
            return metrics
        except Exception as e:
            logger.error(f"Error getting metrics from MongoDB: {str(e)}")
            return []
    
    @classmethod
    def get_trends(
        cls,
        category: Optional[str] = None,
        min_virality: Optional[float] = None,
        timeframe: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get sustainability trends with optional filtering
        
        Args:
            category: Filter by category (optional)
            min_virality: Minimum virality score (optional)
            timeframe: Timeframe filter (optional)
            limit: Maximum number of trends to return
            
        Returns:
            List of trends as dictionaries
        """
        try:
            # Build query
            query = {}
            if category:
                query['category'] = category
                
            if min_virality is not None:
                query['virality_score'] = {'$gte': min_virality}
                
            if timeframe:
                # Calculate date threshold based on timeframe
                now = datetime.now()
                date_threshold = None
                
                if timeframe == 'week':
                    date_threshold = now - timedelta(days=7)
                elif timeframe == 'month':
                    date_threshold = now - timedelta(days=30)
                elif timeframe == 'quarter':
                    date_threshold = now - timedelta(days=90)
                elif timeframe == 'year':
                    date_threshold = now - timedelta(days=365)
                    
                if date_threshold:
                    query['timestamp'] = {'$gte': date_threshold}
            
            # Execute query
            collection = trends_collection()
            cursor = collection.find(query).sort('virality_score', -1).limit(limit)
            
            # Serialize documents and filter out None values
            trends = []
            for doc in cursor:
                if doc is not None:
                    trends.append(serialize_document(doc))
            
            logger.info(f"Retrieved {len(trends)} trends from MongoDB")
            return trends
        except Exception as e:
            logger.error(f"Error getting trends from MongoDB: {str(e)}")
            return []
    
    @classmethod
    def get_stories(
        cls,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get sustainability stories with optional filtering
        
        Args:
            category: Filter by category (optional)
            tags: Filter by tags (optional)
            start_date: Filter by minimum date (optional)
            end_date: Filter by maximum date (optional)
            limit: Maximum number of stories to return
            skip: Number of stories to skip (for pagination)
            
        Returns:
            List of stories as dictionaries
        """
        try:
            # Build query
            query = {}
            if category:
                query['category'] = category
                
            if tags:
                query['tags'] = {'$in': tags}
                
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
            
            # Serialize documents and filter out None values
            stories = []
            for doc in cursor:
                if doc is not None:
                    stories.append(serialize_document(doc))
            
            logger.info(f"Retrieved {len(stories)} stories from MongoDB")
            return stories
        except Exception as e:
            logger.error(f"Error getting stories from MongoDB: {str(e)}")
            return []
    
    @classmethod
    def insert_metric(cls, metric_data: Dict[str, Any]) -> Optional[str]:
        """
        Insert a new sustainability metric
        
        Args:
            metric_data: Metric data to insert
            
        Returns:
            ID of inserted document or None if failed
        """
        try:
            # Ensure timestamp exists
            if 'timestamp' not in metric_data:
                metric_data['timestamp'] = datetime.now()
                
            # Insert the document
            collection = metrics_collection()
            result = collection.insert_one(metric_data)
            
            logger.info(f"Inserted metric: {metric_data.get('name', 'Unknown')} with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting metric: {str(e)}")
            return None
    
    @classmethod
    def insert_trend(cls, trend_data: Dict[str, Any]) -> Optional[str]:
        """
        Insert a new sustainability trend
        
        Args:
            trend_data: Trend data to insert
            
        Returns:
            ID of inserted document or None if failed
        """
        try:
            # Ensure timestamp exists
            if 'timestamp' not in trend_data:
                trend_data['timestamp'] = datetime.now()
                
            # Insert the document
            collection = trends_collection()
            result = collection.insert_one(trend_data)
            
            logger.info(f"Inserted trend: {trend_data.get('name', 'Unknown')} with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting trend: {str(e)}")
            return None
    
    @classmethod
    def insert_story(cls, story_data: Dict[str, Any]) -> Optional[str]:
        """
        Insert a new sustainability story
        
        Args:
            story_data: Story data to insert
            
        Returns:
            ID of inserted document or None if failed
        """
        try:
            # Ensure publication date exists
            if 'publication_date' not in story_data:
                story_data['publication_date'] = datetime.now()
                
            # Insert the document
            collection = stories_collection()
            result = collection.insert_one(story_data)
            
            logger.info(f"Inserted story: {story_data.get('title', 'Unknown')} with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting story: {str(e)}")
            return None
    
    @classmethod
    def get_categories(cls) -> List[str]:
        """
        Get all unique categories from the metrics collection
        
        Returns:
            List of unique category names
        """
        try:
            collection = metrics_collection()
            result = collection.distinct("category")
            return result
        except Exception as e:
            logger.error(f"Error getting categories: {str(e)}")
            return []