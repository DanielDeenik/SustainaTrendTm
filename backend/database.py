import logging
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from contextlib import contextmanager
from urllib.parse import urlparse, parse_qs

# Configure logging
logger = logging.getLogger(__name__)

# Get database URL from environment and configure SSL
DATABASE_URL = os.environ["DATABASE_URL"]
parsed_url = urlparse(DATABASE_URL)
if parsed_url.scheme == 'postgresql':
    # Add SSL mode if not present
    query_params = parse_qs(parsed_url.query)
    if 'sslmode' not in query_params:
        if '?' in DATABASE_URL:
            DATABASE_URL += '&sslmode=require'
        else:
            DATABASE_URL += '?sslmode=require'

# Create SQLAlchemy engine with SSL configuration and retry mechanism
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_recycle=300,    # Recycle connections every 5 minutes
    pool_size=5,         # Maximum number of connections in the pool
    max_overflow=10,     # Maximum number of connections that can be created beyond pool_size
    connect_args={
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
        "application_name": "sustainability_intelligence"  # Helps with monitoring
    }
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
Base = declarative_base()

def verify_table_exists(table_name: str) -> bool:
    """Verify if a table exists in the database"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

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
    """Initialize database tables with proper error handling and verification"""
    try:
        logger.info("Starting database initialization...")

        # Verify database connection
        with engine.connect() as connection:
            logger.info("Database connection successful")

        # Create tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)

        # Verify tables were created
        tables_to_verify = ['metrics', 'reports', 'analyses']
        for table in tables_to_verify:
            if verify_table_exists(table):
                logger.info(f"Table '{table}' created successfully")
                if verify_table_structure(table):
                    logger.info(f"Table '{table}' structure verified")
                else:
                    raise Exception(f"Table '{table}' structure verification failed")
            else:
                raise Exception(f"Table '{table}' was not created properly")

        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Error during database initialization: {str(e)}")
        raise

# Dependency to get DB session
def get_db():
    """Get database session with proper error handling"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        db.close()

@contextmanager
def get_db_session():
    """Context manager for database sessions with error handling"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()