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
import time

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
        # Print environment variables for debugging (without showing sensitive values)
        logger.info(f"DATABASE_URL exists: {bool(os.getenv('DATABASE_URL'))}")
        logger.info(f"PGDATABASE exists: {bool(os.getenv('PGDATABASE'))}")
        logger.info(f"PGUSER exists: {bool(os.getenv('PGUSER'))}")
        logger.info(f"PGHOST exists: {bool(os.getenv('PGHOST'))}")
        logger.info(f"PGPORT exists: {bool(os.getenv('PGPORT'))}")

        # Wait a moment to ensure database is ready
        time.sleep(2)

        # Connect to database
        db_config = get_db_config()
        logger.info("Attempting database connection...")
        conn = psycopg2.connect(**db_config)
        logger.info("Database connection established")

        # Create metrics table if it doesn't exist
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL CHECK (category IN ('emissions', 'water', 'energy', 'waste', 'social', 'governance')),
                    value NUMERIC NOT NULL CHECK (value >= 0),
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
        # Return False instead of exiting to allow script to continue
        return False
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed")

    return True

if __name__ == "__main__":
    logger.info("Starting database seeding...")
    success = seed_metrics()
    if success:
        logger.info("Database seeding completed successfully")
        sys.exit(0)
    else:
        logger.error("Database seeding failed")
        # Use a non-zero exit code but don't raise an exception
        sys.exit(1)