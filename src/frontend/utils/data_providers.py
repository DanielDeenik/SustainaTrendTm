"""
Data Providers

This module contains functions for retrieving data from various sources.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..services.mongodb_service import get_mongodb_service

logger = logging.getLogger(__name__)

def get_metrics() -> Dict[str, Any]:
    """
    Get sustainability metrics from MongoDB.
    
    Returns:
        Dict[str, Any]: Dictionary containing sustainability metrics
    """
    try:
        service = get_mongodb_service()
        latest_metrics = service.find_one(
            'metrics',
            {},
            sort=[('timestamp', -1)]  # Get the most recent entry
        )
        
        if not latest_metrics:
            logger.warning("No metrics found in database")
            return {
                'environmental': {
                    'carbon_emissions': 0.0,
                    'renewable_energy': 0.0,
                    'waste_reduction': 0.0
                },
                'social': {
                    'employee_satisfaction': 0.0,
                    'community_engagement': 0.0,
                    'diversity_score': 0.0
                },
                'governance': {
                    'board_diversity': 0.0,
                    'transparency_score': 0.0,
                    'ethics_compliance': 0.0
                },
                'timestamp': datetime.now()
            }
        
        # Remove MongoDB _id field
        latest_metrics.pop('_id', None)
        return latest_metrics
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise

def get_stories() -> Dict[str, str]:
    """
    Get sustainability stories from MongoDB.
        
    Returns:
        Dict[str, str]: Dictionary containing story types and their content
    """
    try:
        service = get_mongodb_service()
        stories = service.find_many('stories', {}, sort=[('timestamp', -1)])
        
        if not stories:
            logger.warning("No stories found in database")
            return {}
        
        # Convert MongoDB documents to dictionary
        stories_dict = {}
        for story in stories:
            story_type = story.get('type')
            if story_type:
                stories_dict[story_type] = {
                    'title': story.get('title', ''),
                    'content': story.get('content', ''),
                    'metrics': story.get('metrics', {}),
                    'timestamp': story.get('timestamp', datetime.now())
                }
        
        return stories_dict
    except Exception as e:
        logger.error(f"Failed to get stories: {e}")
        raise

def get_trends() -> List[Dict[str, Any]]:
    """
    Get sustainability trends from MongoDB.
    
    Returns:
        List[Dict[str, Any]]: List of trend dictionaries
    """
    try:
        service = get_mongodb_service()
        trends = service.find_many('trends', {}, sort=[('timestamp', -1)])
        
        if not trends:
            logger.warning("No trends found in database")
            return []
        
        # Remove MongoDB _id fields and ensure all required fields are present
        processed_trends = []
        for trend in trends:
            trend.pop('_id', None)
            processed_trends.append({
                'name': trend.get('name', ''),
                'description': trend.get('description', ''),
                'impact_score': float(trend.get('impact_score', 0.0)),
                'category': trend.get('category', ''),
                'timestamp': trend.get('timestamp', datetime.now())
            })
        
        return processed_trends
    except Exception as e:
        logger.error(f"Failed to get trends: {e}")
        raise

def get_strategies() -> List[Dict[str, Any]]:
    """
    Get monetization strategies from MongoDB.
    
    Returns:
        List[Dict[str, Any]]: List of strategy dictionaries
    """
    try:
        service = get_mongodb_service()
        strategies = service.find_many('strategies', {}, sort=[('timestamp', -1)])
        
        if not strategies:
            logger.warning("No strategies found in database")
            return []
        
        # Remove MongoDB _id fields and ensure all required fields are present
        processed_strategies = []
        for strategy in strategies:
            strategy.pop('_id', None)
            processed_strategies.append({
                'name': strategy.get('name', ''),
                'description': strategy.get('description', ''),
                'potential_revenue': float(strategy.get('potential_revenue', 0.0)),
                'implementation_cost': float(strategy.get('implementation_cost', 0.0)),
                'roi': float(strategy.get('roi', 0.0)),
                'category': strategy.get('category', ''),
                'timestamp': strategy.get('timestamp', datetime.now())
            })
        
        return processed_strategies
    except Exception as e:
        logger.error(f"Failed to get strategies: {e}")
        raise

def get_monetization_strategies() -> List[Dict[str, Any]]:
    """
    Get monetization strategies from MongoDB.
    This is an alias for get_strategies() for backward compatibility.
        
    Returns:
        List[Dict[str, Any]]: List of strategy dictionaries
    """
    return get_strategies()