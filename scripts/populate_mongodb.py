#!/usr/bin/env python3
"""
MongoDB Population Script for SustainaTrend™
This script populates MongoDB with mock data for development and testing.
"""

import os
import sys
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pymongo import MongoClient
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB connection settings
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'sustainatrend')

# Mock data constants
COMPANIES = {
    'tech1': {
        'name': 'EcoTech Solutions',
        'sector': 'Technology',
        'status': 'Active',
        'founded': 2018,
        'employees': 150,
        'location': 'San Francisco, CA'
    },
    'energy1': {
        'name': 'GreenEnergy Corp',
        'sector': 'Energy',
        'status': 'Active',
        'founded': 2015,
        'employees': 300,
        'location': 'Austin, TX'
    },
    'trans1': {
        'name': 'Sustainable Transport',
        'sector': 'Transportation',
        'status': 'Active',
        'founded': 2020,
        'employees': 75,
        'location': 'Boston, MA'
    }
}

SUSTAINABILITY_METRICS = [
    'carbon_emissions',
    'renewable_energy_usage',
    'waste_reduction',
    'water_consumption',
    'employee_satisfaction',
    'diversity_score'
]

TREND_CATEGORIES = [
    'Renewable Energy',
    'Circular Economy',
    'Carbon Capture',
    'Sustainable Agriculture',
    'Green Transportation',
    'Waste Management'
]

def connect_to_mongodb():
    """Connect to MongoDB and return the client and database."""
    try:
        client = MongoClient(MONGODB_URI)
        db = client[MONGODB_DB_NAME]
        logger.info(f"Connected to MongoDB: {MONGODB_URI}")
        return client, db
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        return None, None

def generate_portfolio_companies() -> List[Dict[str, Any]]:
    """Generate mock portfolio company data."""
    companies = []
    for company_id, details in COMPANIES.items():
        company = {
            'id': company_id,
            **details,
            'investment_round': random.choice(['Seed', 'Series A', 'Series B']),
            'investment_amount': random.randint(1, 50) * 1000000,
            'investment_date': (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat(),
            'sustainability_score': random.randint(60, 95),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        companies.append(company)
    return companies

def generate_sustainability_metrics() -> List[Dict[str, Any]]:
    """Generate mock sustainability metrics data."""
    metrics = []
    for company_id in COMPANIES.keys():
        for year in range(2020, 2024):
            for quarter in range(1, 5):
                metric = {
                    'company_id': company_id,
                    'reporting_period': f"{year}-Q{quarter}",
                    'metrics': {
                        metric: random.randint(50, 100) for metric in SUSTAINABILITY_METRICS
                    },
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                metrics.append(metric)
    return metrics

def generate_trends() -> List[Dict[str, Any]]:
    """Generate mock trend data."""
    trends = []
    for category in TREND_CATEGORIES:
        for year in range(2020, 2024):
            trend = {
                'category': category,
                'year': year,
                'growth_rate': random.uniform(5, 25),
                'market_size': random.randint(1, 100) * 1000000000,
                'key_players': random.randint(5, 20),
                'confidence_score': random.randint(70, 95),
                'description': f"Growing trend in {category} with significant market potential",
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            trends.append(trend)
    return trends

def generate_stories() -> List[Dict[str, Any]]:
    """Generate mock story data."""
    stories = []
    story_templates = [
        "How {company} is revolutionizing {sector} with sustainable innovation",
        "{company}'s journey to carbon neutrality",
        "Breaking barriers: {company}'s impact on {sector} sustainability"
    ]
    
    for company_id, details in COMPANIES.items():
        for _ in range(3):
            story = {
                'company_id': company_id,
                'title': random.choice(story_templates).format(
                    company=details['name'],
                    sector=details['sector']
                ),
                'content': f"Lorem ipsum dolor sit amet, consectetur adipiscing elit. {details['name']} is making waves in the {details['sector']} industry.",
                'views': random.randint(100, 10000),
                'likes': random.randint(10, 500),
                'shares': random.randint(5, 200),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            stories.append(story)
    return stories

def generate_vc_data() -> List[Dict[str, Any]]:
    """Generate mock VC/PE data."""
    vc_data = []
    for company_id, details in COMPANIES.items():
        vc_entry = {
            'company_id': company_id,
            'valuation': random.randint(10, 500) * 1000000,
            'total_funding': random.randint(1, 50) * 1000000,
            'investors': [
                f"VC Fund {i+1}" for i in range(random.randint(2, 5))
            ],
            'exit_potential': random.randint(60, 95),
            'market_size': random.randint(1, 100) * 1000000000,
            'competition_level': random.choice(['Low', 'Medium', 'High']),
            'regulatory_environment': random.choice(['Favorable', 'Neutral', 'Challenging']),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        vc_data.append(vc_entry)
    return vc_data

def create_index_if_not_exists(collection, index_spec, **kwargs):
    """Create an index if it doesn't already exist."""
    try:
        collection.create_index(index_spec, **kwargs)
        logger.info(f"Created index {index_spec} on {collection.name}")
    except Exception as e:
        logger.warning(f"Index {index_spec} already exists on {collection.name}: {e}")

def populate_database():
    """Populate MongoDB with mock data."""
    try:
        client = MongoClient(MONGODB_URI)
        # Test connection
        client.admin.command('ping')
        db = client[MONGODB_DB_NAME]
        logger.info(f"Connected to MongoDB: {MONGODB_URI}")
        
        # Clear existing data
        collections = ['portfolio_companies', 'sustainability_metrics', 'trends', 'stories', 'vc_data']
        for collection in collections:
            db[collection].delete_many({})
            logger.info(f"Cleared collection: {collection}")
        
        # Generate and insert mock data
        portfolio_companies = generate_portfolio_companies()
        db['portfolio_companies'].insert_many(portfolio_companies)
        logger.info(f"Inserted {len(portfolio_companies)} portfolio companies")
        
        sustainability_metrics = generate_sustainability_metrics()
        db['sustainability_metrics'].insert_many(sustainability_metrics)
        logger.info(f"Inserted {len(sustainability_metrics)} sustainability metrics")
        
        trends = generate_trends()
        db['trends'].insert_many(trends)
        logger.info(f"Inserted {len(trends)} trends")
        
        stories = generate_stories()
        db['stories'].insert_many(stories)
        logger.info(f"Inserted {len(stories)} stories")
        
        vc_data = generate_vc_data()
        db['vc_data'].insert_many(vc_data)
        logger.info(f"Inserted {len(vc_data)} VC data entries")
        
        # Create indexes
        create_index_if_not_exists(db['portfolio_companies'], 'id', unique=True)
        create_index_if_not_exists(db['portfolio_companies'], 'sector')
        create_index_if_not_exists(db['portfolio_companies'], 'status')
        
        create_index_if_not_exists(db['sustainability_metrics'], [('company_id', 1), ('reporting_period', 1)], unique=True)
        create_index_if_not_exists(db['sustainability_metrics'], 'reporting_period')
        
        create_index_if_not_exists(db['trends'], 'category')
        create_index_if_not_exists(db['trends'], 'year')
        
        create_index_if_not_exists(db['stories'], 'company_id')
        create_index_if_not_exists(db['stories'], 'created_at')
        
        create_index_if_not_exists(db['vc_data'], 'company_id', unique=True)
        
        logger.info("Successfully populated database with mock data")
        return True
        
    except Exception as e:
        logger.error(f"Error populating database: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    if populate_database():
        logger.info("Database population completed successfully")
    else:
        logger.error("Database population failed")
        sys.exit(1) 