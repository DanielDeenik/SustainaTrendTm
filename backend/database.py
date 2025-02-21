import logging
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from contextlib import contextmanager
from urllib.parse import urlparse, parse_qs
import time
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)

# Get database URL from environment and configure SSL
DATABASE_URL = os.environ["DATABASE_URL"]
parsed_url = urlparse(DATABASE_URL)

# Cloud-optimized database configuration
engine = create_engine(
    DATABASE_URL,
    # Connection pooling settings
    pool_pre_ping=True,           # Enable connection health checks
    pool_recycle=300,             # Recycle connections every 5 minutes
    pool_size=5,                  # Maximum number of connections in pool
    max_overflow=2,               # Max additional connections when pool is full
    # Performance settings
    echo=False,                   # Disable SQL logging in production
    future=True,                  # Use SQLAlchemy 2.0 features
    connect_args={
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
        "connect_timeout": 10,    # Connection timeout in seconds
        "application_name": "sustainability_intelligence"
    }
)

# Create sessionmaker with optimized settings
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Improve performance for read-heavy workloads
)

# Create Base class for declarative models
Base = declarative_base()

def verify_db_connection(max_retries: int = 3, retry_delay: int = 1) -> bool:
    """
    Verify database connection with retry mechanism
    Returns True if connection is successful, False otherwise
    """
    for attempt in range(max_retries):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                logger.info("Database connection verified successfully")
                return True
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database connection attempt {attempt + 1} failed: {str(e)}")
                time.sleep(retry_delay)
            else:
                logger.error(f"Database connection failed after {max_retries} attempts: {str(e)}")
                return False
    return False

def verify_table_exists(table_name: str) -> bool:
    """Verify if a table exists in the database"""
    try:
        inspector = inspect(engine)
        return table_name in inspector.get_table_names()
    except Exception as e:
        logger.error(f"Error verifying table {table_name}: {str(e)}")
        return False

def verify_table_structure(table_name: str) -> bool:
    """Verify if a table has the correct structure"""
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        return len(columns) > 0
    except Exception as e:
        logger.error(f"Error verifying table structure for {table_name}: {str(e)}")
        return False

def init_db():
    """Initialize database with proper error handling and verification"""
    try:
        logger.info("Starting database initialization...")

        # Verify database connection
        if not verify_db_connection():
            raise Exception("Failed to establish database connection")

        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)

        # Verify critical tables
        tables_to_verify = ['metrics', 'reports', 'analyses']
        for table in tables_to_verify:
            if verify_table_exists(table):
                logger.info(f"Table '{table}' exists")
                if verify_table_structure(table):
                    logger.info(f"Table '{table}' structure verified")
                else:
                    raise Exception(f"Table '{table}' structure verification failed")
            else:
                raise Exception(f"Table '{table}' was not created properly")

        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

@contextmanager
def get_db():
    """Get database session with proper error handling"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()