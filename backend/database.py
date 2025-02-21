from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os
from contextlib import contextmanager
import json

# Get database URL from environment
SQLALCHEMY_DATABASE_URL = os.environ["DATABASE_URL"]

# Create SQLAlchemy engine with proper JSON handling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    json_serializer=json.dumps,
    json_deserializer=json.loads,
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
Base = declarative_base()

# Function to initialize database
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_session():
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()