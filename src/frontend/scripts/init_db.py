#!/usr/bin/env python
"""
Database Initialization Script

This script initializes the MongoDB database with the necessary collections and indexes
for the SustainaTrend application.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, List

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from src.frontend.services.mongodb_service import get_mongodb_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def connect_to_mongodb():
    """Connect to MongoDB and return the service instance."""
    try:
        service = get_mongodb_service()
        logger.info("Successfully connected to MongoDB")
        return service
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)

def create_collections(db):
    """Create the necessary collections if they don't exist."""
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
        else:
            logger.info(f"Collection already exists: {collection}")

def create_indexes(db):
    """Create indexes for the collections."""
    try:
        # Drop existing indexes except _id
        for collection in db.list_collection_names():
            db[collection].drop_indexes()
            logger.info(f"Dropped existing indexes for collection: {collection}")
        
        # Metrics collection indexes
        db.metrics.create_index([("timestamp", -1)])
        db.metrics.create_index([("category", 1)])
        
        # Stories collection indexes
        db.stories.create_index([("timestamp", -1)])
        db.stories.create_index([("type", 1)])
        db.stories.create_index([("category", 1)])
        
        # Trends collection indexes
        db.trends.create_index([("timestamp", -1)])
        db.trends.create_index([("category", 1)])
        db.trends.create_index([("impact_score", -1)])
        
        # Strategies collection indexes
        db.strategies.create_index([("timestamp", -1)])
        db.strategies.create_index([("category", 1)])
        db.strategies.create_index([("roi", -1)])
        
        # Companies collection indexes
        db.companies.create_index([("name", 1)], unique=True)
        db.companies.create_index([("industry", 1)])
        db.companies.create_index([("sustainability_score", -1)])
        
        # Users collection indexes
        db.users.create_index([("email", 1)], unique=True)
        db.users.create_index([("username", 1)], unique=True)
        
        # Portfolios collection indexes
        db.portfolios.create_index([("user_id", 1)])
        db.portfolios.create_index([("timestamp", -1)])
        
        # Assessments collection indexes
        db.assessments.create_index([("company_id", 1)])
        db.assessments.create_index([("timestamp", -1)])
        db.assessments.create_index([("category", 1)])
        
        logger.info("Successfully created all indexes")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        raise

def insert_sample_data(db):
    """Insert sample data into the collections if they are empty."""
    # Sample metrics data
    if db.metrics.count_documents({}) == 0:
        sample_metrics = {
            "environmental": {
                "carbon_emissions": 75.5,
                "renewable_energy": 45.2,
                "waste_reduction": 60.8
            },
            "social": {
                "employee_satisfaction": 85.3,
                "community_engagement": 78.9,
                "diversity_score": 82.1
            },
            "governance": {
                "board_diversity": 65.4,
                "transparency_score": 88.7,
                "ethics_compliance": 92.3
            },
            "timestamp": datetime.now()
        }
        db.metrics.insert_one(sample_metrics)
        logger.info("Inserted sample metrics data")
    
    # Sample stories data
    if db.stories.count_documents({}) == 0:
        sample_stories = [
            {
                "type": "environmental",
                "title": "Renewable Energy Initiative",
                "content": "Company X achieved 100% renewable energy usage across all facilities.",
                "metrics": {
                    "energy_savings": 45.2,
                    "carbon_reduction": 30.5
                },
                "timestamp": datetime.now()
            },
            {
                "type": "social",
                "title": "Community Development Program",
                "content": "Implemented new community development initiatives in local areas.",
                "metrics": {
                    "community_impact": 78.9,
                    "employee_engagement": 85.3
                },
                "timestamp": datetime.now()
            }
        ]
        db.stories.insert_many(sample_stories)
        logger.info("Inserted sample stories data")
    
    # Sample trends data
    if db.trends.count_documents({}) == 0:
        sample_trends = [
            {
                "name": "Circular Economy",
                "description": "Growing adoption of circular economy principles in manufacturing",
                "impact_score": 85.5,
                "category": "environmental",
                "timestamp": datetime.now()
            },
            {
                "name": "Social Impact Investing",
                "description": "Increasing focus on social impact in investment decisions",
                "impact_score": 78.3,
                "category": "social",
                "timestamp": datetime.now()
            }
        ]
        db.trends.insert_many(sample_trends)
        logger.info("Inserted sample trends data")
    
    # Sample strategies data
    if db.strategies.count_documents({}) == 0:
        sample_strategies = [
            {
                "name": "Green Product Line",
                "description": "Launch eco-friendly product line with sustainable materials",
                "potential_revenue": 1500000,
                "implementation_cost": 500000,
                "roi": 200,
                "category": "product",
                "timestamp": datetime.now()
            },
            {
                "name": "Carbon Offset Program",
                "description": "Implement carbon offset program for supply chain",
                "potential_revenue": 800000,
                "implementation_cost": 300000,
                "roi": 167,
                "category": "operational",
                "timestamp": datetime.now()
            }
        ]
        db.strategies.insert_many(sample_strategies)
        logger.info("Inserted sample strategies data")

def main():
    """Main function to initialize the database."""
    try:
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Connect to MongoDB
        service = connect_to_mongodb()
        db = service.db
        
        # Create collections
        create_collections(db)
        
        # Create indexes
        create_indexes(db)
        
        # Insert sample data
        insert_sample_data(db)
        
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)
    finally:
        # Close MongoDB connections
        service.close()

if __name__ == "__main__":
    main() 