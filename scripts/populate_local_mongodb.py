"""
Script to populate the local MongoDB with initial data for the SustainaTrend™ platform.
"""
import os
import sys
import logging
from datetime import datetime, timedelta
import random

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.frontend.refactored.services.mongodb_service import MongoDBService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def populate_database():
    """Populate the MongoDB database with initial data."""
    try:
        # Initialize MongoDB service
        mongodb = MongoDBService()
        
        # Clear existing collections
        collections = ['metrics', 'stories', 'trends', 'strategies', 'companies', 'users', 'portfolios', 'assessments']
        for collection_name in collections:
            collection = mongodb.get_collection(collection_name)
            collection.delete_many({})
            logger.info(f"Cleared collection: {collection_name}")
        
        # Populate companies
        companies = [
            {
                'name': 'EcoTech Solutions',
                'industry': 'Clean Technology',
                'description': 'Developing innovative solutions for renewable energy and waste management.',
                'founded': 2018,
                'employees': 120,
                'location': 'Amsterdam, Netherlands',
                'website': 'https://example.com/ecotech',
                'sustainability_score': 85,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
            },
            {
                'name': 'GreenBuild Materials',
                'industry': 'Construction',
                'description': 'Manufacturing sustainable building materials from recycled resources.',
                'founded': 2015,
                'employees': 250,
                'location': 'Berlin, Germany',
                'website': 'https://example.com/greenbuild',
                'sustainability_score': 78,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
            },
            {
                'name': 'Sustainable Foods',
                'industry': 'Agriculture',
                'description': 'Producing organic and sustainable food products with minimal environmental impact.',
                'founded': 2017,
                'employees': 85,
                'location': 'Copenhagen, Denmark',
                'website': 'https://example.com/sustainablefoods',
                'sustainability_score': 92,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
            }
        ]
        
        for company in companies:
            mongodb.insert_one('companies', company)
        
        logger.info(f"Inserted {len(companies)} companies")
        
        # Populate metrics
        metrics = [
            {
                'name': 'Carbon Emissions Reduction',
                'category': 'Environmental',
                'description': 'Percentage reduction in carbon emissions compared to baseline year.',
                'unit': '%',
                'target': 30,
                'current_value': 22,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
            },
            {
                'name': 'Water Usage Efficiency',
                'category': 'Environmental',
                'description': 'Gallons of water used per unit of production.',
                'unit': 'gallons/unit',
                'target': 5,
                'current_value': 7,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
            },
            {
                'name': 'Employee Satisfaction',
                'category': 'Social',
                'description': 'Employee satisfaction score based on surveys.',
                'unit': 'score',
                'target': 85,
                'current_value': 78,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
            },
            {
                'name': 'Sustainable Supplier Ratio',
                'category': 'Supply Chain',
                'description': 'Percentage of suppliers with verified sustainability practices.',
                'unit': '%',
                'target': 75,
                'current_value': 62,
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
            }
        ]
        
        for metric in metrics:
            mongodb.insert_one('metrics', metric)
        
        logger.info(f"Inserted {len(metrics)} metrics")
        
        # Populate trends
        trends = [
            {
                'title': 'Circular Economy Adoption',
                'category': 'Business Model',
                'description': 'Companies are increasingly adopting circular economy principles to reduce waste and create closed-loop systems.',
                'impact_level': 'High',
                'confidence': 0.85,
                'source': 'Industry Report 2023',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
            },
            {
                'title': 'Renewable Energy Integration',
                'category': 'Technology',
                'description': 'Integration of renewable energy sources into business operations is becoming standard practice.',
                'impact_level': 'Medium',
                'confidence': 0.78,
                'source': 'Energy Market Analysis',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
            },
            {
                'title': 'Sustainable Supply Chain Transparency',
                'category': 'Supply Chain',
                'description': 'Increasing demand for transparency in supply chains to verify sustainability claims.',
                'impact_level': 'High',
                'confidence': 0.92,
                'source': 'Consumer Survey 2023',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
            }
        ]
        
        for trend in trends:
            mongodb.insert_one('trends', trend)
        
        logger.info(f"Inserted {len(trends)} trends")
        
        # Populate stories
        stories = [
            {
                'title': 'EcoTech Solutions Launches New Solar Panel Technology',
                'content': 'EcoTech Solutions has developed a new solar panel technology that increases efficiency by 25% while reducing manufacturing costs.',
                'company_id': companies[0]['_id'],
                'date': datetime.now() - timedelta(days=random.randint(1, 30)),
                'source': 'Company Press Release',
                'url': 'https://example.com/news/ecotech-solar',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
            },
            {
                'title': 'GreenBuild Materials Expands to New Markets',
                'content': 'GreenBuild Materials has announced expansion into three new European markets, bringing sustainable building materials to more regions.',
                'company_id': companies[1]['_id'],
                'date': datetime.now() - timedelta(days=random.randint(1, 30)),
                'source': 'Industry News',
                'url': 'https://example.com/news/greenbuild-expansion',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
            },
            {
                'title': 'Sustainable Foods Receives Environmental Award',
                'content': 'Sustainable Foods has been recognized with the European Environmental Innovation Award for their sustainable farming practices.',
                'company_id': companies[2]['_id'],
                'date': datetime.now() - timedelta(days=random.randint(1, 30)),
                'source': 'Award Announcement',
                'url': 'https://example.com/news/sustainable-foods-award',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
            }
        ]
        
        for story in stories:
            mongodb.insert_one('stories', story)
        
        logger.info(f"Inserted {len(stories)} stories")
        
        # Populate strategies
        strategies = [
            {
                'name': 'Carbon Neutrality by 2030',
                'description': 'Strategy to achieve carbon neutrality across all operations by 2030.',
                'category': 'Environmental',
                'timeline': 'Long-term',
                'status': 'In Progress',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
            },
            {
                'name': '100% Renewable Energy',
                'description': 'Transition to 100% renewable energy sources for all operations.',
                'category': 'Environmental',
                'timeline': 'Medium-term',
                'status': 'Planning',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
            },
            {
                'name': 'Zero Waste Operations',
                'description': 'Implement zero waste practices across all operations.',
                'category': 'Environmental',
                'timeline': 'Short-term',
                'status': 'In Progress',
                'created_at': datetime.now() - timedelta(days=random.randint(1, 365))
            }
        ]
        
        for strategy in strategies:
            mongodb.insert_one('strategies', strategy)
        
        logger.info(f"Inserted {len(strategies)} strategies")
        
        logger.info("Database populated with initial data successfully")
        
    except Exception as e:
        logger.error(f"Error populating database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    populate_database() 