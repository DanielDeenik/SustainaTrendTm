import os
import logging
from contextlib import contextmanager
from typing import Dict, Any, Generator
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
from backend.utils.logger import logger

def get_db_config() -> Dict[str, Any]:
    """Get database configuration from environment variables"""
    required_vars = ['DATABASE_URL', 'PGDATABASE', 'PGUSER', 'PGPASSWORD', 'PGHOST', 'PGPORT']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

    # Prefer DATABASE_URL if available
    if os.getenv('DATABASE_URL'):
        return {'dsn': os.getenv('DATABASE_URL')}

    return {
        'dbname': os.getenv('PGDATABASE'),
        'user': os.getenv('PGUSER'),
        'password': os.getenv('PGPASSWORD'),
        'host': os.getenv('PGHOST'),
        'port': os.getenv('PGPORT')
    }

@contextmanager
def get_db() -> Generator[connection, None, None]:
    """Database connection context manager with improved error handling"""
    conn = None
    try:
        conn = psycopg2.connect(**get_db_config(), cursor_factory=RealDictCursor)
        logger.info("Database connection established successfully")
        yield conn
        conn.commit()
    except psycopg2.OperationalError as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise Exception("Failed to connect to the database. Please check your database configuration.") from e
    except psycopg2.Error as e:
        logger.error(f"Database error: {str(e)}")
        if conn:
            conn.rollback()
        raise Exception(f"A database error occurred: {str(e)}") from e
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed")

def verify_db_connection() -> bool:
    """Verify database connection and create tables if needed"""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                # Test connection
                cur.execute("SELECT 1")
                logger.info("Database connection test successful")

                # Create metrics table if it doesn't exist
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
                logger.info("Metrics table verified/created successfully")
                return True
    except Exception as e:
        logger.error(f"Database verification failed: {str(e)}")
        return False

def init_db() -> None:
    """Initialize database with proper error handling"""
    try:
        logger.info("Starting database initialization...")
        if not verify_db_connection():
            raise Exception("Failed to verify database connection and schema")
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise