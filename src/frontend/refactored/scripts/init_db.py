#!/usr/bin/env python3
"""
Script to initialize the MongoDB database with collections and indexes.
"""
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def connect_to_mongodb():
    """Connect to MongoDB."""
    try:
        from pymongo import MongoClient
        uri = os.getenv('MONGODB_URI')
        if not uri:
            raise ValueError("MONGODB_URI environment variable not set")
        
        client = MongoClient(uri)
        db = client.get_database()
        logger.info("Connected to MongoDB")
        return db
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {str(e)}")
        sys.exit(1)

def create_collections(db):
    """Create collections if they don't exist."""
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
            db.create_collection(collection)
            logger.info(f"Created collection: {collection}")

def create_indexes(db):
    """Create indexes for collections."""
    try:
        # Drop existing indexes
        for collection_name in db.list_collection_names():
            collection = db[collection_name]
            collection.drop_indexes()
            logger.info(f"Dropped existing indexes for collection: {collection_name}")
        
        # Metrics collection indexes
        db.metrics.create_index([("category", 1)], name="metrics_category_1")
        db.metrics.create_index([("timestamp", -1)], name="metrics_timestamp_-1")
        
        # Stories collection indexes
        db.stories.create_index([("type", 1)], name="stories_type_1")
        db.stories.create_index([("timestamp", -1)], name="stories_timestamp_-1")
        
        # Trends collection indexes
        db.trends.create_index([("category", 1)], name="trends_category_1")
        db.trends.create_index([("timestamp", -1)], name="trends_timestamp_-1")
        
        # Strategies collection indexes
        db.strategies.create_index([("type", 1)], name="strategies_type_1")
        db.strategies.create_index([("timestamp", -1)], name="strategies_timestamp_-1")
        
        # Companies collection indexes
        db.companies.create_index([("name", 1)], name="companies_name_1", unique=True)
        db.companies.create_index([("sector", 1)], name="companies_sector_1")
        
        # Users collection indexes
        db.users.create_index([("email", 1)], name="users_email_1", unique=True)
        db.users.create_index([("username", 1)], name="users_username_1", unique=True)
        
        # Portfolios collection indexes
        db.portfolios.create_index([("user_id", 1)], name="portfolios_user_id_1")
        db.portfolios.create_index([("timestamp", -1)], name="portfolios_timestamp_-1")
        
        # Assessments collection indexes
        db.assessments.create_index([("company_id", 1)], name="assessments_company_id_1")
        db.assessments.create_index([("timestamp", -1)], name="assessments_timestamp_-1")
        
        logger.info("Created indexes for all collections")
    except Exception as e:
        logger.error(f"Error creating indexes: {str(e)}")
        raise

def insert_sample_data(db):
    """Insert sample data into collections."""
    # Sample metrics
    if db.metrics.count_documents({}) == 0:
        metrics = [
            {
                "category": "environmental",
                "value": 85.5,
                "timestamp": datetime.now(),
                "source": "sample"
            },
            {
                "category": "social",
                "value": 78.2,
                "timestamp": datetime.now(),
                "source": "sample"
            }
        ]
        db.metrics.insert_many(metrics)
        logger.info("Inserted sample metrics")
    
    # Sample stories
    if db.stories.count_documents({}) == 0:
        stories = [
            {
                "type": "success",
                "title": "Sample Success Story",
                "content": "This is a sample success story.",
                "timestamp": datetime.now()
            }
        ]
        db.stories.insert_many(stories)
        logger.info("Inserted sample stories")
    
    # Sample trends
    if db.trends.count_documents({}) == 0:
        trends = [
            {
                "category": "renewable_energy",
                "description": "Growing adoption of renewable energy",
                "timestamp": datetime.now()
            }
        ]
        db.trends.insert_many(trends)
        logger.info("Inserted sample trends")
    
    # Sample strategies
    if db.strategies.count_documents({}) == 0:
        strategies = [
            {
                "type": "carbon_reduction",
                "description": "Strategy for reducing carbon emissions",
                "timestamp": datetime.now()
            }
        ]
        db.strategies.insert_many(strategies)
        logger.info("Inserted sample strategies")

def main():
    """Main function to initialize the database."""
    try:
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
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
        logger.error(f"Error initializing database: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 