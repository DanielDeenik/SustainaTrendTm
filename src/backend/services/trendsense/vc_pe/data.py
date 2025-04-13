"""
VC/PE Data Module for SustainaTrend™
This module provides data access functions for VC/PE specific features.
"""

import os
import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection settings
MONGODB_URI = os.getenv('MONGODB_URI')
MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'sustainatrend')

# Initialize MongoDB client
try:
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB_NAME]
    print(f"Connected to MongoDB: {MONGODB_URI}")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    client = None
    db = None

def get_mongodb_data():
    """Get data from MongoDB or fall back to generated data if connection fails."""
    if db is None:
        return None
    return db

def generate_portfolio_metrics():
    """Generate portfolio metrics data"""
    return {
        'total_investments': random.randint(30, 50),
        'total_value': round(random.uniform(100, 500), 2),
        'avg_esg_score': round(random.uniform(70, 90), 1),
        'sustainability_metrics': {
            'carbon_reduction': round(random.uniform(10, 30), 1),
            'renewable_energy': round(random.uniform(20, 40), 1),
            'water_efficiency': round(random.uniform(15, 35), 1)
        }
    }

def generate_company_benchmarks():
    """Generate company benchmark data"""
    sectors = ['Clean Energy', 'Sustainable Tech', 'Green Infrastructure', 'Waste Management']
    companies = []
    
    for _ in range(10):
        companies.append({
            'name': f'Company {_+1}',
            'sector': random.choice(sectors),
            'esg_score': round(random.uniform(60, 95), 1),
            'carbon_footprint': round(random.uniform(100, 1000), 1),
            'sustainability_rating': random.choice(['A+', 'A', 'B+', 'B', 'C+']),
            'investment_date': (datetime.now() - timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d')
        })
    
    return {
        'companies': companies,
        'industry_averages': {
            'esg_score': 75.5,
            'carbon_footprint': 550,
            'renewable_adoption': 35.2
        }
    }

def generate_sustainability_insights():
    """Generate sustainability insights"""
    return {
        'trends': [
            {
                'category': 'Carbon Reduction',
                'trend': 'positive',
                'change': '+15.3%',
                'insight': 'Portfolio companies showing strong progress in carbon reduction initiatives'
            },
            {
                'category': 'Renewable Energy',
                'trend': 'positive',
                'change': '+22.1%',
                'insight': 'Increased adoption of renewable energy sources across portfolio'
            },
            {
                'category': 'Water Management',
                'trend': 'neutral',
                'change': '+2.5%',
                'insight': 'Moderate improvements in water efficiency measures'
            }
        ],
        'recommendations': [
            'Focus on water management improvements across portfolio',
            'Expand renewable energy initiatives to smaller portfolio companies',
            'Implement standardized ESG reporting across all investments'
        ]
    } 