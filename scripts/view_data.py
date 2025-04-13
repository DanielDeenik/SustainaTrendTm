#!/usr/bin/env python
"""
SustainaTrend™ Intelligence Platform - Data Viewer
This script allows viewing the MongoDB data for IKpartners and Qconcepts.
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from tabulate import tabulate
from pymongo import MongoClient
from bson import ObjectId

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import MongoDB service
from src.frontend.services.mongodb_service import MongoDBService

# Initialize MongoDB service
mongodb_service = MongoDBService()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/view_data.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Company data
COMPANIES = {
    "ikpartners": "IKpartners",
    "qconcepts": "Qconcepts"
}

def format_date(date):
    """Format date for display"""
    if isinstance(date, datetime):
        return date.strftime("%Y-%m-%d %H:%M:%S")
    return str(date)

def view_metrics(company_id=None, category=None, limit=10):
    """
    View metrics data
    
    Args:
        company_id (str, optional): Filter by company ID
        category (str, optional): Filter by category
        limit (int, optional): Maximum number of metrics to display
    """
    try:
        # Get metrics collection
        metrics_collection = mongodb_service.get_collection('metrics')
        
        # Build query
        query = {}
        if company_id:
            query["company_id"] = company_id
        if category:
            query["category"] = category
        
        # Execute query
        cursor = metrics_collection.find(query).sort("timestamp", -1).limit(limit)
        
        # Format data for display
        data = []
        for doc in cursor:
            data.append([
                doc.get("name", ""),
                doc.get("category", ""),
                doc.get("value", ""),
                doc.get("unit", ""),
                doc.get("company", ""),
                format_date(doc.get("timestamp", "")),
                f"{doc.get('progress', 0)}%"
            ])
        
        # Display data
        if data:
            headers = ["Name", "Category", "Value", "Unit", "Company", "Timestamp", "Progress"]
            print(tabulate(data, headers=headers, tablefmt="grid"))
            print(f"Showing {len(data)} metrics")
        else:
            print("No metrics found")
            
    except Exception as e:
        logger.error(f"Error viewing metrics: {str(e)}")
        print(f"Error: {str(e)}")

def view_trends(category=None, min_virality=None, limit=10):
    """
    View trends data
    
    Args:
        category (str, optional): Filter by category
        min_virality (float, optional): Minimum virality score
        limit (int, optional): Maximum number of trends to display
    """
    try:
        # Get trends collection
        trends_collection = mongodb_service.get_collection('trends')
        
        # Build query
        query = {}
        if category:
            query["category"] = category
        if min_virality is not None:
            query["virality_score"] = {"$gte": min_virality}
        
        # Execute query
        cursor = trends_collection.find(query).sort("virality_score", -1).limit(limit)
        
        # Format data for display
        data = []
        for doc in cursor:
            companies = [COMPANIES.get(c, c) for c in doc.get("companies", [])]
            data.append([
                doc.get("name", ""),
                doc.get("category", ""),
                doc.get("virality_score", ""),
                format_date(doc.get("created_at", "")),
                doc.get("growth_rate", ""),
                doc.get("sentiment", ""),
                ", ".join(companies)
            ])
        
        # Display data
        if data:
            headers = ["Name", "Category", "Virality Score", "Created At", "Growth Rate", "Sentiment", "Companies"]
            print(tabulate(data, headers=headers, tablefmt="grid"))
            print(f"Showing {len(data)} trends")
        else:
            print("No trends found")
            
    except Exception as e:
        logger.error(f"Error viewing trends: {str(e)}")
        print(f"Error: {str(e)}")

def view_stories(company_id=None, category=None, limit=10):
    """
    View stories data
    
    Args:
        company_id (str, optional): Filter by company ID
        category (str, optional): Filter by category
        limit (int, optional): Maximum number of stories to display
    """
    try:
        # Get stories collection
        stories_collection = mongodb_service.get_collection('stories')
        
        # Build query
        query = {}
        if company_id:
            query["company_id"] = company_id
        if category:
            query["category"] = category
        
        # Execute query
        cursor = stories_collection.find(query).sort("publication_date", -1).limit(limit)
        
        # Format data for display
        data = []
        for doc in cursor:
            # Truncate content for display
            content = doc.get("content", "")
            if len(content) > 100:
                content = content[:100] + "..."
                
            data.append([
                doc.get("title", ""),
                doc.get("category", ""),
                doc.get("company", ""),
                format_date(doc.get("publication_date", "")),
                content
            ])
        
        # Display data
        if data:
            headers = ["Title", "Category", "Company", "Publication Date", "Content"]
            print(tabulate(data, headers=headers, tablefmt="grid"))
            print(f"Showing {len(data)} stories")
        else:
            print("No stories found")
            
    except Exception as e:
        logger.error(f"Error viewing stories: {str(e)}")
        print(f"Error: {str(e)}")

def view_collection_stats():
    """View collection statistics"""
    try:
        # Get collections
        metrics_collection = mongodb_service.get_collection('metrics')
        trends_collection = mongodb_service.get_collection('trends')
        stories_collection = mongodb_service.get_collection('stories')
        
        # Get collection stats
        stats = [
            ["Metrics", metrics_collection.count_documents({})],
            ["Trends", trends_collection.count_documents({})],
            ["Stories", stories_collection.count_documents({})]
        ]
        
        # Display stats
        headers = ["Collection", "Document Count"]
        print(tabulate(stats, headers=headers, tablefmt="grid"))
            
    except Exception as e:
        logger.error(f"Error viewing collection stats: {str(e)}")
        print(f"Error: {str(e)}")

def main():
    """Main function"""
    try:
        # Verify MongoDB connection
        if not mongodb_service.verify_connection():
            print("Error: Could not connect to MongoDB")
            return
            
        # View collection stats
        print("\nCollection Statistics:")
        view_collection_stats()
        
        # View metrics
        print("\nRecent Metrics:")
        view_metrics(limit=5)
        
        # View trends
        print("\nRecent Trends:")
        view_trends(limit=5)
        
        # View stories
        print("\nRecent Stories:")
        view_stories(limit=5)
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        print(f"Error: {str(e)}")
    finally:
        # Close MongoDB connection
        mongodb_service.close()

if __name__ == "__main__":
    main() 