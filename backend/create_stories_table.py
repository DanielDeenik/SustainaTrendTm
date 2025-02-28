#!/usr/bin/env python3
"""
Create sustainability_stories table in the database
"""
import os
import logging
import sys
from database import get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_stories_table():
    """Create the sustainability_stories table if it doesn't exist"""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                # Create the sustainability_stories table
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

                # Add index on company_name for faster lookups
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_sustainability_stories_company 
                    ON sustainability_stories(company_name)
                """)

                logger.info("Sustainability stories table created or verified")
                return True
    except Exception as e:
        logger.error(f"Error creating sustainability_stories table: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Creating sustainability stories table...")
    try:
        success = create_stories_table()
        if success:
            logger.info("Table creation completed successfully")
            sys.exit(0)
        else:
            logger.error("Table creation failed")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)