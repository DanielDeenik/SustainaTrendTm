#!/usr/bin/env python
"""
SustainaTrend™ Intelligence Platform - Database Initialization
This script initializes the MongoDB database with sample data for IKpartners and Qconcepts.
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

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
        logging.FileHandler('logs/init_db.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Company data
COMPANIES = {
    "ikpartners": {
        "name": "IKpartners",
        "industry": "Technology",
        "size": "Medium",
        "location": "Amsterdam"
    },
    "qconcepts": {
        "name": "Qconcepts",
        "industry": "Consulting",
        "size": "Small",
        "location": "Rotterdam"
    }
}

# Sample metrics data
METRICS = [
    {
        "name": "Carbon Footprint",
        "category": "Environmental",
        "unit": "tCO2e",
        "description": "Total greenhouse gas emissions"
    },
    {
        "name": "Energy Consumption",
        "category": "Environmental",
        "unit": "kWh",
        "description": "Total energy usage"
    },
    {
        "name": "Water Usage",
        "category": "Environmental",
        "unit": "m³",
        "description": "Total water consumption"
    },
    {
        "name": "Employee Satisfaction",
        "category": "Social",
        "unit": "%",
        "description": "Employee satisfaction score"
    },
    {
        "name": "Gender Diversity",
        "category": "Social",
        "unit": "%",
        "description": "Percentage of female employees"
    }
]

# Sample trends data
TRENDS = [
    {
        "name": "Circular Economy",
        "category": "Environmental",
        "description": "Transition to circular business models",
        "growth_rate": 0.15,
        "sentiment": "positive"
    },
    {
        "name": "Remote Work",
        "category": "Social",
        "description": "Increase in remote work adoption",
        "growth_rate": 0.25,
        "sentiment": "positive"
    },
    {
        "name": "Green Energy",
        "category": "Environmental",
        "description": "Shift to renewable energy sources",
        "growth_rate": 0.20,
        "sentiment": "positive"
    }
]

def generate_sample_metrics(company_id: str, days: int = 30) -> List[Dict[str, Any]]:
    """
    Generate sample metrics data for a company
    
    Args:
        company_id (str): Company ID
        days (int): Number of days to generate data for
        
    Returns:
        List[Dict[str, Any]]: Sample metrics data
    """
    metrics_data = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    for metric in METRICS:
        base_value = random.uniform(100, 1000)
        for i in range(days):
            date = start_date + timedelta(days=i)
            value = base_value * (1 + random.uniform(-0.1, 0.1))
            
            metrics_data.append({
                "name": metric["name"],
                "category": metric["category"],
                "value": round(value, 2),
                "unit": metric["unit"],
                "company_id": company_id,
                "company": COMPANIES[company_id]["name"],
                "timestamp": date,
                "progress": random.randint(0, 100)
            })
    
    return metrics_data

def generate_sample_trends(days: int = 30) -> List[Dict[str, Any]]:
    """
    Generate sample trends data
    
    Args:
        days (int): Number of days to generate data for
        
    Returns:
        List[Dict[str, Any]]: Sample trends data
    """
    trends_data = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    for trend in TRENDS:
        for i in range(days):
            date = start_date + timedelta(days=i)
            virality = random.uniform(0.5, 1.0)
            
            trends_data.append({
                "name": trend["name"],
                "category": trend["category"],
                "description": trend["description"],
                "virality_score": round(virality, 2),
                "growth_rate": trend["growth_rate"],
                "sentiment": trend["sentiment"],
                "companies": list(COMPANIES.keys()),
                "created_at": date
            })
    
    return trends_data

def generate_sample_stories(company_id: str, days: int = 30) -> List[Dict[str, Any]]:
    """
    Generate sample stories data for a company
    
    Args:
        company_id (str): Company ID
        days (int): Number of days to generate data for
        
    Returns:
        List[Dict[str, Any]]: Sample stories data
    """
    stories_data = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    story_templates = [
        {
            "title": "Company {company} Achieves {metric} Reduction",
            "category": "Environmental",
            "content": "{company} has successfully reduced their {metric} by {value}% through innovative sustainability initiatives."
        },
        {
            "title": "{company} Leads Industry in {trend}",
            "category": "Social",
            "content": "{company} is at the forefront of the {trend} movement, setting new standards for the industry."
        }
    ]
    
    for i in range(days):
        date = start_date + timedelta(days=i)
        template = random.choice(story_templates)
        
        if template["category"] == "Environmental":
            metric = random.choice([m for m in METRICS if m["category"] == "Environmental"])
            value = random.randint(10, 30)
            title = template["title"].format(
                company=COMPANIES[company_id]["name"],
                metric=metric["name"]
            )
            content = template["content"].format(
                company=COMPANIES[company_id]["name"],
                metric=metric["name"],
                value=value
            )
        else:
            trend = random.choice([t for t in TRENDS if t["category"] == "Social"])
            title = template["title"].format(
                company=COMPANIES[company_id]["name"],
                trend=trend["name"]
            )
            content = template["content"].format(
                company=COMPANIES[company_id]["name"],
                trend=trend["name"]
            )
        
        stories_data.append({
            "title": title,
            "category": template["category"],
            "content": content,
            "company_id": company_id,
            "company": COMPANIES[company_id]["name"],
            "publication_date": date,
            "source": "Company Press Release"
        })
    
    return stories_data

def init_database():
    """Initialize the database with sample data"""
    try:
        # Verify MongoDB connection
        if not mongodb_service.verify_connection():
            logger.error("Could not connect to MongoDB")
            return False
            
        # Get collections
        metrics_collection = mongodb_service.get_collection('metrics')
        trends_collection = mongodb_service.get_collection('trends')
        stories_collection = mongodb_service.get_collection('stories')
        
        # Clear existing data
        metrics_collection.delete_many({})
        trends_collection.delete_many({})
        stories_collection.delete_many({})
        
        # Generate and insert sample data
        for company_id in COMPANIES:
            # Insert metrics
            metrics_data = generate_sample_metrics(company_id)
            metrics_collection.insert_many(metrics_data)
            logger.info(f"Inserted {len(metrics_data)} metrics for {COMPANIES[company_id]['name']}")
            
            # Insert stories
            stories_data = generate_sample_stories(company_id)
            stories_collection.insert_many(stories_data)
            logger.info(f"Inserted {len(stories_data)} stories for {COMPANIES[company_id]['name']}")
        
        # Insert trends
        trends_data = generate_sample_trends()
        trends_collection.insert_many(trends_data)
        logger.info(f"Inserted {len(trends_data)} trends")
        
        return True
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        return False
    finally:
        # Close MongoDB connection
        mongodb_service.close()

def main():
    """Main function"""
    try:
        print("Initializing SustainaTrend™ Intelligence Platform database...")
        
        if init_database():
            print("Database initialization completed successfully!")
        else:
            print("Database initialization failed. Check logs for details.")
            
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 