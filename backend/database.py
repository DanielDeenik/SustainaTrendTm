import os
import logging
import traceback
from contextlib import contextmanager
from typing import Dict, Any, Generator
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extensions import connection

# Configure logging directly instead of relying on backend.utils.logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global connection pool
_pool = None

def get_db_config() -> Dict[str, Any]:
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

def get_connection_pool():
    """Get or create a database connection pool"""
    global _pool
    if _pool is None:
        try:
            # Configure connection parameters from environment
            db_config = get_db_config()

            # Create a connection pool with minimum 1 and maximum 10 connections
            _pool = ThreadedConnectionPool(1, 10, **db_config, cursor_factory=RealDictCursor)
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create database connection pool: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    return _pool

@contextmanager
def get_db() -> Generator[connection, None, None]:
    """Database connection context manager with improved error handling and connection pooling"""
    conn = None
    pool = None
    try:
        # Print environment variables for debugging (without showing sensitive values)
        logger.debug(f"DATABASE_URL exists: {bool(os.getenv('DATABASE_URL'))}")
        logger.debug(f"PGDATABASE exists: {bool(os.getenv('PGDATABASE'))}")
        logger.debug(f"PGUSER exists: {bool(os.getenv('PGUSER'))}")
        logger.debug(f"PGHOST exists: {bool(os.getenv('PGHOST'))}")
        logger.debug(f"PGPORT exists: {bool(os.getenv('PGPORT'))}")

        # Get a connection from the pool
        try:
            pool = get_connection_pool()
            conn = pool.getconn()
            logger.info("Database connection obtained from pool")
        except Exception as pool_error:
            logger.warning(f"Connection pool failed: {str(pool_error)}. Trying direct connection...")
            # Fall back to direct connection if pool fails
            conn = psycopg2.connect(**get_db_config(), cursor_factory=RealDictCursor)
            logger.info("Direct database connection established")

        # Ensure autocommit is OFF (default) to allow explicit transaction control
        conn.autocommit = False

        # Yield the connection for use in the with block
        yield conn

        # If we got here without exception, commit the transaction
        conn.commit()
        logger.info("Database transaction committed successfully")

    except psycopg2.OperationalError as e:
        error_message = str(e)
        if "endpoint is disabled" in error_message:
            logger.error("Database endpoint is disabled. Please activate the endpoint in your database provider's console.")
        else:
            logger.error(f"Database connection failed: {error_message}")
            logger.error(traceback.format_exc())
        if conn:
            conn.rollback()
            logger.info("Transaction rolled back due to error")
        raise Exception("Failed to connect to the database. Please check your database configuration.") from e
    except psycopg2.Error as e:
        logger.error(f"Database error: {str(e)}")
        logger.error(traceback.format_exc())
        if conn:
            conn.rollback()
            logger.info("Transaction rolled back due to database error")
        raise Exception(f"A database error occurred: {str(e)}") from e
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        if conn:
            conn.rollback()
            logger.info("Transaction rolled back due to unexpected error")
        raise
    finally:
        if conn:
            # If using pool, return connection to pool; otherwise close it
            if pool:
                try:
                    pool.putconn(conn)
                    logger.debug("Connection returned to pool")
                except Exception as return_error:
                    logger.error(f"Error returning connection to pool: {str(return_error)}")
                    logger.error(traceback.format_exc())
                    conn.close()
                    logger.debug("Connection closed directly")
            else:
                conn.close()
                logger.debug("Database connection closed")

def verify_db_connection() -> bool:
    """Verify database connection and create tables if needed"""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                # Test connection with timeout
                cur.execute("SELECT 1")
                logger.info("Database connection test successful")

                # Create sustainability_stories table if it doesn't exist
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS sustainability_stories (
                        id SERIAL PRIMARY KEY,
                        company_name TEXT NOT NULL,
                        industry TEXT NOT NULL,
                        story_content JSONB NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        story_metadata JSONB DEFAULT '{}'::jsonb
                    )
                """)
                logger.info("Sustainability stories table verified/created successfully")

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
        logger.error(traceback.format_exc())
        return False

def init_db() -> None:
    """Initialize database with proper error handling"""
    try:
        logger.info("Starting database initialization...")
        if not verify_db_connection():
            logger.warning("Failed to verify database connection and schema, but continuing startup...")
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        logger.error(traceback.format_exc())
        # Continue instead of raising - let the app try to function
        logger.warning("Continuing startup despite database initialization failure")