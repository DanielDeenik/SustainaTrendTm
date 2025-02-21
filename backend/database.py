from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os
from contextlib import contextmanager
from psycopg2.extras import register_default_jsonb
import psycopg2

# Register JSONB handling globally
register_default_jsonb(globally=True, loads=lambda x: x)

SQLALCHEMY_DATABASE_URL = os.environ["DATABASE_URL"]

# Create SQLAlchemy engine with JSON handling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    json_serializer=lambda obj: obj,
    json_deserializer=lambda obj: obj,
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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