#!/usr/bin/env python3
"""
Test script to verify database connectivity and storytelling table operations
"""
import os
import json
import logging
from datetime import datetime
from database import get_db, verify_db_connection

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_db_connection():
    """Test basic database connectivity"""
    logger.info("Testing database connection...")
    result = verify_db_connection()
    if result:
        logger.info("Database connection successful and tables verified")
    else:
        logger.error("Database connection or table verification failed")
    return result

def test_create_story():
    """Test creating a sustainability story directly"""
    logger.info("Testing story creation in database...")
    
    # Create test story data
    company_name = "Test Company"
    industry = "Technology"
    story_content = {
        "Company": "Test Company",
        "Industry": "Technology",
        "Industry_Context": "Test industry context",
        "Sustainability_Strategy": "Test sustainability strategy",
        "Competitor_Benchmarking": ["Competitor 1", "Competitor 2"],
        "Monetization_Model": "Test monetization model",
        "Investment_Pathway": "Test investment pathway",
        "Actionable_Recommendations": ["Recommendation 1", "Recommendation 2"]
    }
    
    # Add timestamps
    now = datetime.now()
    
    # Convert story content to JSON
    content_json = json.dumps(story_content)
    
    # Create metadata
    metadata = {"metrics": {"views": 0, "likes": 0, "shares": 0}}
    metadata_json = json.dumps(metadata)
    
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                # First check if test stories already exist
                cur.execute("""
                    SELECT COUNT(*) as count FROM sustainability_stories
                    WHERE company_name = %s AND industry = %s
                """, (company_name, industry))
                result = cur.fetchone()
                existing_count = result['count']
                logger.info(f"Found {existing_count} existing test stories")
                
                # Insert new test story
                logger.info("Inserting test story into database...")
                cur.execute("""
                    INSERT INTO sustainability_stories
                    (company_name, industry, story_content, created_at, updated_at, story_metadata)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    company_name,
                    industry,
                    content_json,
                    now,
                    now,
                    metadata_json
                ))
                
                result = cur.fetchone()
                if result and 'id' in result:
                    story_id = result['id']
                    logger.info(f"Test story created successfully with ID: {story_id}")
                    
                    # Verify the story was saved by retrieving it
                    cur.execute("""
                        SELECT id, company_name, industry, created_at
                        FROM sustainability_stories
                        WHERE id = %s
                    """, (story_id,))
                    
                    story = cur.fetchone()
                    if story:
                        logger.info(f"Retrieved test story: ID={story['id']}, Company={story['company_name']}")
                        return True
                    else:
                        logger.error("Failed to retrieve the newly created story")
                        return False
                else:
                    logger.error("Failed to get ID for newly created story")
                    return False
    except Exception as e:
        logger.error(f"Error in test_create_story: {str(e)}")
        return False

def count_stories():
    """Count the number of stories in the database"""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) as count FROM sustainability_stories")
                result = cur.fetchone()
                count = result['count']
                logger.info(f"Total stories in database: {count}")
                return count
    except Exception as e:
        logger.error(f"Error counting stories: {str(e)}")
        return 0

def main():
    """Run the database tests"""
    logger.info("Starting database connectivity tests...")
    
    # Test connection
    if not test_db_connection():
        logger.error("Database connection test failed, exiting")
        return False
    
    # Count existing stories
    initial_count = count_stories()
    
    # Test creating a story
    if test_create_story():
        logger.info("Story creation test passed")
        
        # Verify story count increased
        new_count = count_stories()
        if new_count > initial_count:
            logger.info(f"Story count verification passed: {initial_count} → {new_count}")
        else:
            logger.error(f"Story count did not increase: {initial_count} → {new_count}")
        
        return True
    else:
        logger.error("Story creation test failed")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("All database tests completed successfully")
    else:
        logger.error("Database tests failed")
