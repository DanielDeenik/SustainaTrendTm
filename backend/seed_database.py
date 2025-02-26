#!/usr/bin/env python3
"""
Seed database with sample sustainability metrics
"""
import sys
import os
import logging
import psycopg2
from datetime import datetime, timedelta
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_config():
    """Get database configuration from environment variables"""
    # Check if DATABASE_URL exists first
    if os.getenv('DATABASE_URL'):
        logger.info("Using DATABASE_URL for connection")
        return {'dsn': os.getenv('DATABASE_URL')}

    # Otherwise use individual connection parameters
    elif os.getenv('PGDATABASE') and os.getenv('PGUSER') and os.getenv('PGPASSWORD') and os.getenv('PGHOST'):
        logger.info("Using PGDATABASE, PGUSER, etc. for connection")
        return {
            'dbname': os.getenv('PGDATABASE'),
            'user': os.getenv('PGUSER'),
            'password': os.getenv('PGPASSWORD'),
            'host': os.getenv('PGHOST'),
            'port': os.getenv('PGPORT', '5432')
        }
    else:
        raise EnvironmentError("Missing required database environment variables")

def seed_metrics():
    """Seed the database with sample sustainability metrics"""
    conn = None
    try:
        # Connect to database using direct connection parameters
        if os.getenv('DATABASE_URL'):
            conn = psycopg2.connect(os.getenv('DATABASE_URL'))
            logger.info("Connected to database using DATABASE_URL")
        else:
            conn = psycopg2.connect(
                dbname=os.getenv('PGDATABASE'),
                user=os.getenv('PGUSER'),
                password=os.getenv('PGPASSWORD'),
                host=os.getenv('PGHOST'),
                port=os.getenv('PGPORT', '5432')
            )
            logger.info("Connected to database using individual parameters")

        # Create metrics table if it doesn't exist
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    value NUMERIC NOT NULL,
                    unit TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metric_metadata JSONB DEFAULT '{}'::jsonb
                )
            """)
            conn.commit()
            logger.info("Metrics table created or verified")

        # Generate sample metrics data
        metrics_data = []

        # Define the metrics to generate
        metrics_to_generate = [
            {"name": "Carbon Emissions", "category": "emissions", "unit": "tons CO2e", "initial_value": 45, "trend": "decrease"},
            {"name": "Energy Consumption", "category": "energy", "unit": "MWh", "initial_value": 1250, "trend": "decrease"},
            {"name": "Water Usage", "category": "water", "unit": "kiloliters", "initial_value": 350, "trend": "decrease"},
            {"name": "Waste Recycled", "category": "waste", "unit": "percent", "initial_value": 65, "trend": "increase"},
            {"name": "ESG Score", "category": "social", "unit": "score", "initial_value": 72, "trend": "increase"}
        ]

        # Generate data for the past 6 months
        now = datetime.now()
        for i in range(6):
            timestamp = now - timedelta(days=30 * (5 - i))
            for metric in metrics_to_generate:
                if metric["trend"] == "decrease":
                    value = metric["initial_value"] * (1 - 0.05 * i)  # 5% decrease each month
                else:
                    value = metric["initial_value"] * (1 + 0.05 * i)  # 5% increase each month

                # Add some random variation
                variation = random.uniform(-0.02, 0.02)
                value = value * (1 + variation)

                metrics_data.append((
                    metric["name"],
                    metric["category"],
                    round(value, 2),
                    metric["unit"],
                    timestamp
                ))

        # Insert metrics into database
        with conn.cursor() as cur:
            # First clear existing data
            cur.execute("DELETE FROM metrics")
            conn.commit()
            logger.info("Cleared existing metrics data")

            # Insert new data
            for metric in metrics_data:
                cur.execute("""
                    INSERT INTO metrics (name, category, value, unit, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                """, metric)

            conn.commit()
            logger.info(f"Successfully inserted {len(metrics_data)} sample metrics")

    except Exception as e:
        logger.error(f"Error seeding database: {str(e)}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed")

    return True

if __name__ == "__main__":
    logger.info("Starting database seeding...")
    try:
        success = seed_metrics()
        if success:
            logger.info("Database seeding completed successfully")
            sys.exit(0)
        else:
            logger.error("Database seeding failed")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in seeding: {str(e)}")
        sys.exit(1)