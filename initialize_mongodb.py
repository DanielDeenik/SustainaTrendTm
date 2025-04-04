#!/usr/bin/env python
"""
MongoDB Initialization Utility for SustainaTrend™ Platform

This script verifies MongoDB connection, sets up collections and indexes,
and provides utility commands for the SustainaTrend™ platform.

Usage:
    python initialize_mongodb.py --verify
    python initialize_mongodb.py --setup
    python initialize_mongodb.py --test-data
"""

import os
import sys
import logging
import argparse
import json
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mongodb_init")

try:
    # Try importing the MongoDB client and utilities
    try:
        from frontend.mongo_client import (
            get_database, verify_connection, close_connections, 
            benchmarking_collection, serialize_document
        )
        logger.info("MongoDB client imported from frontend package")
    except ImportError:
        # Fallback to direct import
        from mongo_client import (
            get_database, verify_connection, close_connections, 
            benchmarking_collection, serialize_document
        )
        logger.info("MongoDB client imported directly")
        
    try:
        from frontend.benchmark_db import (
            initialize_benchmarking_collection, save_benchmark_data,
            get_benchmark_data, get_peer_companies
        )
        logger.info("Benchmarking DB module imported from frontend package")
    except ImportError:
        # Fallback to direct import
        from benchmark_db import (
            initialize_benchmarking_collection, save_benchmark_data,
            get_benchmark_data, get_peer_companies
        )
        logger.info("Benchmarking DB module imported directly")
except ImportError as e:
    logger.error(f"Failed to import MongoDB modules: {str(e)}")
    logger.error("Make sure you're running this script from the project root")
    sys.exit(1)

def verify_mongodb_connection():
    """
    Verify MongoDB connection is working
    """
    logger.info("Verifying MongoDB connection...")
    
    try:
        # Check if connection works
        if verify_connection():
            logger.info("✅ MongoDB connection is working!")
            
            # Get and print database details
            db = get_database()
            collection_names = db.list_collection_names()
            logger.info(f"Available collections: {', '.join(collection_names) if collection_names else 'No collections'}")
            
            return True
        else:
            logger.error("❌ MongoDB connection failed!")
            return False
    except Exception as e:
        logger.error(f"❌ Error connecting to MongoDB: {str(e)}")
        return False

def setup_collections_and_indexes():
    """
    Set up collections and indexes for the SustainaTrend™ platform
    """
    if not verify_mongodb_connection():
        return False
    
    try:
        logger.info("Setting up collections and indexes...")
        
        # Initialize benchmarking collection with indexes
        if initialize_benchmarking_collection():
            logger.info("✅ Benchmarking collection initialized successfully")
        else:
            logger.warning("⚠️ Failed to initialize benchmarking collection")
        
        logger.info("Collections and indexes setup complete")
        return True
    except Exception as e:
        logger.error(f"❌ Error setting up collections: {str(e)}")
        return False

def create_test_data():
    """
    Create test data for the SustainaTrend™ platform
    """
    if not verify_mongodb_connection():
        return False
    
    try:
        logger.info("Creating test data for benchmarking...")
        
        # Sample company profiles for test data
        companies = [
            {
                "company_id": str(uuid.uuid4()),
                "company_profile": {
                    "name": "EcoTech Solutions",
                    "sector": "Technology",
                    "region": "EU",
                    "size": "Medium (251-1000)"
                },
                "framework": "CSRD",
                "benchmark_data": {
                    "company_name": "EcoTech Solutions",
                    "framework": "Corporate Sustainability Reporting Directive",
                    "timestamp": datetime.now().isoformat(),
                    "metrics": [
                        {
                            "id": "scope1_emissions",
                            "name": "Scope 1 Emissions",
                            "unit": "tCO2e",
                            "category": "Environmental",
                            "your_value": 78,
                            "industry_median": 65,
                            "top_quartile": 85,
                            "percentile": 82
                        },
                        {
                            "id": "renewable_energy",
                            "name": "Renewable Energy Percentage",
                            "unit": "%",
                            "category": "Environmental",
                            "your_value": 45,
                            "industry_median": 30,
                            "top_quartile": 50,
                            "percentile": 75
                        }
                    ]
                },
                "insights": [
                    {
                        "metric": "Scope 1 Emissions",
                        "type": "strength",
                        "description": "You are at the 82th percentile for Scope 1 Emissions.",
                        "recommendation": "Maintain this strong performance."
                    }
                ]
            },
            {
                "company_id": str(uuid.uuid4()),
                "company_profile": {
                    "name": "GreenEnergy Co",
                    "sector": "Energy",
                    "region": "North America",
                    "size": "Large (1001-5000)"
                },
                "framework": "TCFD",
                "benchmark_data": {
                    "company_name": "GreenEnergy Co",
                    "framework": "Task Force on Climate-related Financial Disclosures",
                    "timestamp": datetime.now().isoformat(),
                    "metrics": [
                        {
                            "id": "physical_risk_exposure",
                            "name": "Physical Climate Risk Exposure",
                            "unit": "Score",
                            "category": "Risk",
                            "your_value": 65,
                            "industry_median": 70,
                            "top_quartile": 90,
                            "percentile": 45
                        }
                    ]
                },
                "insights": [
                    {
                        "metric": "Physical Climate Risk Exposure",
                        "type": "gap",
                        "description": "Your Physical Climate Risk Exposure is below the industry median.",
                        "recommendation": "Consider developing strategies to improve Physical Climate Risk Exposure."
                    }
                ]
            }
        ]
        
        # Save each company's benchmark data
        for company in companies:
            doc_id = save_benchmark_data(company)
            if doc_id:
                logger.info(f"✅ Test data created for {company['company_profile']['name']}, ID: {doc_id}")
            else:
                logger.warning(f"⚠️ Failed to create test data for {company['company_profile']['name']}")
        
        logger.info("Test data creation complete")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating test data: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="MongoDB Initialization Utility for SustainaTrend™ Platform")
    parser.add_argument("--verify", action="store_true", help="Verify MongoDB connection")
    parser.add_argument("--setup", action="store_true", help="Set up collections and indexes")
    parser.add_argument("--test-data", action="store_true", help="Create test data")
    
    args = parser.parse_args()
    
    try:
        if args.verify:
            verify_mongodb_connection()
        elif args.setup:
            setup_collections_and_indexes()
        elif args.test-data:
            create_test_data()
        else:
            # If no arguments provided, run all steps
            logger.info("Running all initialization steps...")
            if verify_mongodb_connection():
                setup_collections_and_indexes()
                create_test_data()
    finally:
        # Close MongoDB connections
        close_connections()

if __name__ == "__main__":
    main()