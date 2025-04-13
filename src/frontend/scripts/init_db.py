#!/usr/bin/env python
"""
Database Initialization Script

This script initializes the MongoDB database with proper collections and indexes
for the SustainaTrend application.
"""

import os
import sys
import logging
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/init_db.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def connect_to_mongodb():
    """Connect to MongoDB and return the database."""
    try:
        # Get MongoDB connection string from environment
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        db_name = os.getenv("MONGO_DB_NAME", "sustainatrend")
        
        logger.info(f"Connecting to MongoDB at {mongo_uri}")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.server_info()
        logger.info("Successfully connected to MongoDB")
        
        # Get database
        db = client[db_name]
        return db
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)

def create_collections(db):
    """Create collections with proper schemas."""
    collections = [
        "metrics",
        "stories",
        "trends",
        "strategies",
        "companies",
        "users",
        "portfolios",
        "assessments"
    ]
    
    for collection in collections:
        if collection not in db.list_collection_names():
            logger.info(f"Creating collection: {collection}")
            db.create_collection(collection)
        else:
            logger.info(f"Collection already exists: {collection}")

def create_indexes(db):
    """Create indexes for collections."""
    # Metrics collection indexes
    db.metrics.create_index([("category", ASCENDING)])
    db.metrics.create_index([("timestamp", DESCENDING)])
    db.metrics.create_index([("name", ASCENDING)])
    
    # Stories collection indexes
    db.stories.create_index([("category", ASCENDING)])
    db.stories.create_index([("timestamp", DESCENDING)])
    db.stories.create_index([("title", ASCENDING)])
    
    # Trends collection indexes
    db.trends.create_index([("category", ASCENDING)])
    db.trends.create_index([("timestamp", DESCENDING)])
    db.trends.create_index([("name", ASCENDING)])
    
    # Strategies collection indexes
    db.strategies.create_index([("title", ASCENDING)])
    db.strategies.create_index([("potential_revenue", ASCENDING)])
    
    # Companies collection indexes
    db.companies.create_index([("name", ASCENDING)])
    db.companies.create_index([("ticker", ASCENDING)])
    db.companies.create_index([("sector", ASCENDING)])
    
    # Users collection indexes
    db.users.create_index([("email", ASCENDING)], unique=True)
    db.users.create_index([("username", ASCENDING)], unique=True)
    
    # Portfolios collection indexes
    db.portfolios.create_index([("user_id", ASCENDING)])
    db.portfolios.create_index([("company_id", ASCENDING)])
    
    # Assessments collection indexes
    db.assessments.create_index([("company_id", ASCENDING)])
    db.assessments.create_index([("timestamp", DESCENDING)])
    
    logger.info("Created indexes for all collections")

def insert_sample_data(db):
    """Insert sample data into collections."""
    # Sample metrics
    metrics = [
        {
            "name": "Carbon Emissions 1",
            "category": "Carbon Emissions",
            "value": 75.5,
            "unit": "tons",
            "timestamp": datetime.now(),
            "trend": [
                {"date": "2023-01-01", "value": 80.0},
                {"date": "2023-02-01", "value": 78.5},
                {"date": "2023-03-01", "value": 77.0},
                {"date": "2023-04-01", "value": 75.5}
            ],
            "change": -5.6,
            "change_type": "positive"
        },
        {
            "name": "Energy Efficiency 1",
            "category": "Energy Efficiency",
            "value": 85.2,
            "unit": "%",
            "timestamp": datetime.now(),
            "trend": [
                {"date": "2023-01-01", "value": 80.0},
                {"date": "2023-02-01", "value": 82.0},
                {"date": "2023-03-01", "value": 83.5},
                {"date": "2023-04-01", "value": 85.2}
            ],
            "change": 6.5,
            "change_type": "positive"
        }
    ]
    
    # Sample stories
    stories = [
        {
            "id": "story-1",
            "title": "Carbon Emissions Reduction Initiative",
            "content": "Our organization has successfully reduced carbon emissions by 15% through implementation of energy-efficient technologies and practices.",
            "category": "Carbon Emissions",
            "tags": ["climate action", "carbon reduction", "energy efficiency"],
            "metrics": ["Carbon Emissions 1", "Energy Efficiency 1"],
            "timestamp": datetime.now().isoformat(),
            "author": "Sustainability Team",
            "image_url": "/static/images/story-1.jpg",
            "impact_score": 85.5
        }
    ]
    
    # Sample trends
    trends = [
        {
            "id": "trend-1",
            "name": "Carbon Neutrality Pledges",
            "category": "Climate Action",
            "virality_score": 87,
            "sentiment": 0.78,
            "mentions": 1458,
            "description": "Companies pledging to achieve carbon neutrality by 2030",
            "impact_statement": "High potential for emissions reduction",
            "category_display": "Climate Action",
            "timeframe": "Long-term trend",
            "timestamp": datetime.now().isoformat(),
            "sources": ["News Articles", "Corporate Reports", "Social Media"],
            "momentum": "increasing"
        }
    ]
    
    # Sample strategies
    strategies = [
        {
            "title": "Carbon Credit Trading Platform",
            "description": "Develop a marketplace for trading verified carbon credits, connecting sustainability-focused companies with offset providers.",
            "potential_revenue": "High",
            "implementation_complexity": "Medium",
            "time_to_market": "6-12 months",
            "key_metrics": ["Transaction Volume", "User Growth", "Verification Rate"],
            "estimated_roi": "35-45%"
        }
    ]
    
    # Insert sample data
    if db.metrics.count_documents({}) == 0:
        db.metrics.insert_many(metrics)
        logger.info(f"Inserted {len(metrics)} sample metrics")
    
    if db.stories.count_documents({}) == 0:
        db.stories.insert_many(stories)
        logger.info(f"Inserted {len(stories)} sample stories")
    
    if db.trends.count_documents({}) == 0:
        db.trends.insert_many(trends)
        logger.info(f"Inserted {len(trends)} sample trends")
    
    if db.strategies.count_documents({}) == 0:
        db.strategies.insert_many(strategies)
        logger.info(f"Inserted {len(strategies)} sample strategies")

def main():
    """Main function to initialize the database."""
    try:
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Connect to MongoDB
        db = connect_to_mongodb()
        
        # Create collections
        create_collections(db)
        
        # Create indexes
        create_indexes(db)
        
        # Insert sample data
        insert_sample_data(db)
        
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 