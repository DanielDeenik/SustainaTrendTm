import logging
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from contextlib import contextmanager
import time
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.environ["DATABASE_URL"]

# Create engine with optimized settings
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

def init_db():
    """Initialize database with proper error handling"""
    try:
        logger.info("Starting database initialization...")

        # Verify database connection
        if not verify_db_connection():
            raise Exception("Failed to establish database connection")

        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise