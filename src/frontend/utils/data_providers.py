"""
Data Providers

This module contains functions for retrieving data from various sources.
"""

from typing import Dict, Any, List
from datetime import datetime
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db: Database = client['sustainatrend']
metrics_collection: Collection = db['metrics']
stories_collection: Collection = db['stories']
trends_collection: Collection = db['trends']
strategies_collection: Collection = db['strategies']

def get_metrics() -> Dict[str, Any]:
    """
    Get sustainability metrics from MongoDB.
    
    Returns:
        Dict[str, Any]: Dictionary containing sustainability metrics
    """
    latest_metrics = metrics_collection.find_one(
        sort=[('timestamp', -1)]  # Get the most recent entry
    )
    
    if not latest_metrics:
        # If no metrics found, return default values
        return {
            'carbon_footprint': 0,
            'energy_usage': 0,
            'water_consumption': 0,
            'waste_recycled': 0,
            'renewable_energy': 0,
            'timestamp': datetime.now()
        }
    
    # Remove MongoDB _id field
    latest_metrics.pop('_id', None)
    return latest_metrics

def get_stories() -> Dict[str, str]:
    """
    Get sustainability stories from MongoDB.
    
    Returns:
        Dict[str, str]: Dictionary containing story types and their content
    """
    stories = stories_collection.find()
    
    if not stories:
        # If no stories found, return empty dictionary
        return {}
    
    # Convert MongoDB cursor to dictionary
    stories_dict = {}
    for story in stories:
        story_type = story.get('type')
        if story_type:
            stories_dict[story_type] = story.get('content', '')
    
    return stories_dict

def get_trends() -> List[Dict[str, Any]]:
    """
    Get sustainability trends from MongoDB.
    
    Returns:
        List[Dict[str, Any]]: List of trend dictionaries
    """
    trends = trends_collection.find()
    
    if not trends:
        # If no trends found, return empty list
        return []
    
    # Convert MongoDB cursor to list and remove _id fields
    trends_list = []
    for trend in trends:
        trend.pop('_id', None)
        trends_list.append(trend)
    
    return trends_list

def get_strategies() -> List[Dict[str, Any]]:
    """
    Get monetization strategies from MongoDB.
    
    Returns:
        List[Dict[str, Any]]: List of strategy dictionaries
    """
    strategies = strategies_collection.find()
    
    if not strategies:
        # If no strategies found, return empty list
        return []
    
    # Convert MongoDB cursor to list and remove _id fields
    strategies_list = []
    for strategy in strategies:
        strategy.pop('_id', None)
        strategies_list.append(strategy)
    
    return strategies_list

def get_monetization_strategies() -> List[Dict[str, Any]]:
    """
    Get monetization strategies from MongoDB.
    This is an alias for get_strategies() for backward compatibility.
    
    Returns:
        List[Dict[str, Any]]: List of strategy dictionaries
    """
    return get_strategies()