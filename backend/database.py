import os
import logging
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor

# Configure logging
logger = logging.getLogger(__name__)

def get_db_config():
    """Get database configuration from environment variables"""
    return {
        'dbname': os.getenv('PGDATABASE'),
        'user': os.getenv('PGUSER'),
        'password': os.getenv('PGPASSWORD'),
        'host': os.getenv('PGHOST'),
        'port': os.getenv('PGPORT')
    }

@contextmanager
def get_db():
    """Database connection context manager"""
    conn = None
    try:
        conn = psycopg2.connect(**get_db_config(), cursor_factory=RealDictCursor)
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def verify_db_connection() -> bool:
    """Verify database connection and create table if needed"""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                # Create metrics table if it doesn't exist
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS metrics (
                        id SERIAL PRIMARY KEY,
                        name TEXT NOT NULL,
                        category TEXT NOT NULL,
                        value NUMERIC NOT NULL,
                        unit TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # Test connection
                cur.execute("SELECT 1")
                return True
    except Exception as e:
        logger.error(f"Database connection verification failed: {str(e)}")
        return False

def init_db():
    """Initialize database with proper error handling"""
    try:
        logger.info("Starting database initialization...")

        # Verify database connection
        if not verify_db_connection():
            raise Exception("Failed to establish database connection")

        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise