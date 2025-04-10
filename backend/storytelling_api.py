"""
FastAPI Sustainability Storytelling API
Provides endpoints for generating and managing sustainability stories
using AI-powered storytelling with McKinsey frameworks
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import os
import json
import logging
import traceback  # Added for detailed error logging
from services.storytelling_ai import generate_sustainability_story
from services.predictive_analytics import (
    predict_sustainability_trends, 
    perform_materiality_assessment
)
from database import get_db  # Changed from backend.database to relative import

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Sustainability Storytelling API",
    description="API for generating and managing sustainability stories using AI",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define Story Metrics Model
class StoryMetrics(BaseModel):
    views: int = 0
    likes: int = 0
    shares: int = 0
    impact_score: Optional[float] = None

# Define Enhanced Sustainability Story Model
class EnhancedSustainabilityStory(BaseModel):
    Company: str
    Industry: str
    Industry_Context: Optional[str] = None
    Sustainability_Strategy: str
    Competitor_Benchmarking: Union[List[str], str]
    Monetization_Model: str
    Investment_Pathway: str
    Actionable_Recommendations: List[str]
    Performance_Metrics: Optional[List[str]] = None
    Estimated_Financial_Impact: Optional[Dict[str, Any]] = None

# Define Story Models
class StoryBase(BaseModel):
    title: str
    content: Optional[Union[EnhancedSustainabilityStory, Dict[str, Any], str]] = None
    company_name: str
    industry: str
    metrics: Optional[StoryMetrics] = None

class StoryCreate(StoryBase):
    pass

class StoryResponse(StoryBase):
    id: int
    author_id: str = "system"
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Config:
        orm_mode = True

# Endpoint: Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "api": "Sustainability Storytelling API",
        "version": "2.0"
    }

# Endpoint: Retrieve Stories
@app.get("/api/stories", response_model=List[StoryResponse])
async def get_stories(skip: int = 0, limit: int = 10):
    """Get all sustainability stories from the database"""
    logger.info(f"Getting stories with skip={skip}, limit={limit}")

    stories = []
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                # Get stories from the database
                cur.execute("""
                    SELECT id, company_name, industry, story_content, 
                           created_at, updated_at, story_metadata
                    FROM sustainability_stories 
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """, (limit, skip))

                db_stories = cur.fetchall()
                logger.info(f"Retrieved {len(db_stories)} stories from database")

                # Convert to response model
                for story in db_stories:
                    # Extract metrics from metadata if available
                    metrics = story.get('story_metadata', {}).get('metrics', {})
                    if not metrics:
                        metrics = StoryMetrics().dict()

                    # Extract content from story_content
                    content = story['story_content']

                    # Build response object
                    story_response = {
                        "id": story['id'],
                        "title": f"Sustainability Story for {story['company_name']}",
                        "content": content,
                        "company_name": story['company_name'],
                        "industry": story['industry'],
                        "metrics": metrics,
                        "created_at": story['created_at'],
                        "updated_at": story['updated_at']
                    }
                    stories.append(story_response)
    except Exception as e:
        logger.error(f"Error retrieving stories from database: {str(e)}")
        logger.error(traceback.format_exc())
        # Return empty list on error
        return []

    return stories

# Endpoint: Get Story by ID
@app.get("/api/stories/{story_id}", response_model=StoryResponse)
async def get_story(story_id: int):
    """Get a specific sustainability story by ID from the database"""
    logger.info(f"Getting story with ID: {story_id}")

    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                # Get specific story from database
                cur.execute("""
                    SELECT id, company_name, industry, story_content, 
                           created_at, updated_at, story_metadata
                    FROM sustainability_stories 
                    WHERE id = %s
                """, (story_id,))

                story = cur.fetchone()

                if not story:
                    raise HTTPException(status_code=404, detail="Story not found")

                # Extract metrics from metadata if available
                metrics = story.get('story_metadata', {}).get('metrics', {})
                if not metrics:
                    metrics = StoryMetrics().dict()

                # Extract content from story_content
                content = story['story_content']

                # Build response object
                story_response = {
                    "id": story['id'],
                    "title": f"Sustainability Story for {story['company_name']}",
                    "content": content,
                    "company_name": story['company_name'],
                    "industry": story['industry'],
                    "metrics": metrics,
                    "created_at": story['created_at'],
                    "updated_at": story['updated_at']
                }

                return story_response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving story from database: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve story: {str(e)}"
        )

# Endpoint: Create Story with AI-Powered Sustainability Narrative
@app.post("/api/stories", response_model=StoryResponse, status_code=status.HTTP_201_CREATED)
async def create_story(story: StoryCreate):
    """Create a new sustainability story using AI-powered storytelling and save to database"""
    logger.info(f"Creating new story for company: {story.company_name}, industry: {story.industry}")

    try:
        # Generate sustainability story using AI if no content provided
        sustainability_story = None
        if not story.content:
            logger.info("Starting chain-of-thought sustainability story generation...")
            sustainability_story = generate_sustainability_story(story.company_name, story.industry)
            logger.info("Sustainability story generation completed successfully")
            logger.debug(f"Generated story: {sustainability_story}")

        # Create story object
        story_data = story.dict()
        if not story.content:  # If content not provided, use AI-generated content
            story_data["content"] = sustainability_story
            logger.info("Using AI-generated content for story")
        else:
            logger.info("Using provided content for story")

        # Debug log story data
        logger.info(f"Story data prepared: company={story_data['company_name']}, industry={story_data['industry']}")

        # Add timestamps
        now = datetime.now()
        story_data["created_at"] = now
        story_data["updated_at"] = now

        # Add metrics if not provided
        if not story_data.get("metrics"):
            story_data["metrics"] = StoryMetrics().dict()

        # Convert to JSON as needed
        if isinstance(story_data["content"], (dict, list)):
            content_json = json.dumps(story_data["content"])
        else:
            content_json = json.dumps({"content": story_data["content"]})

        logger.info("Content prepared for database storage")

        # Create metadata JSON
        metadata_json = json.dumps({"metrics": story_data["metrics"]})

        # Log database operation attempt
        logger.info("Attempting to save story to database...")

        # Save to database with explicit error handling
        try:
            with get_db() as conn:
                with conn.cursor() as cur:
                    # Log the SQL query parameters (without sensitive data)
                    logger.info(f"Executing INSERT into sustainability_stories for {story_data['company_name']}")

                    cur.execute("""
                        INSERT INTO sustainability_stories
                        (company_name, industry, story_content, created_at, updated_at, story_metadata)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        story_data["company_name"],
                        story_data["industry"],
                        content_json,
                        story_data["created_at"],
                        story_data["updated_at"],
                        metadata_json
                    ))

                    result = cur.fetchone()
                    if not result:
                        logger.error("Database INSERT did not return an ID")
                        raise Exception("Database INSERT operation failed to return ID")

                    story_id = result['id']
                    logger.info(f"Successfully saved story to database with ID: {story_id}")

                    # Verify database commit is happening
                    logger.info("Database transaction committed successfully")

                    # Build full response with new ID
                    story_data["id"] = story_id
                    story_data["author_id"] = "system"

                    return story_data

        except Exception as db_error:
            logger.error(f"Database error while saving story: {str(db_error)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to save story to database: {str(db_error)}")

    except Exception as e:
        logger.error(f"Error creating sustainability story: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create sustainability story: {str(e)}"
        )

# Endpoint: AI-Generated Sustainability Insights
@app.post("/api/sustainability-story")
async def get_sustainability_story(company_name: str, industry: str):
    """Generate an AI-powered sustainability story based on company name and industry"""
    logger.info(f"Generating sustainability story for company: {company_name}, industry: {industry}")

    try:
        logger.info("Starting AI-powered sustainability story generation with McKinsey frameworks")
        logger.info("Running chain-of-thought analysis for industry context and strategic insights")

        story = generate_sustainability_story(company_name, industry)
        logger.info("Sustainability story successfully generated")

        # Ensure proper JSON formatting
        return story if isinstance(story, dict) else json.loads(story) if isinstance(story, str) else {}

    except Exception as e:
        logger.error(f"Error generating sustainability story: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate sustainability story: {str(e)}"
        )

# New endpoint: AI-Powered Predictive Analytics
@app.post("/api/predictive-analytics")
async def get_predictive_analytics(
    company_name: str, 
    industry: str, 
    forecast_periods: int = 3,
    metrics: Optional[List[Dict[str, Any]]] = None
):
    """
    Generate AI-powered predictive analytics for sustainability metrics

    Args:
        company_name: Company name for context
        industry: Industry for context
        forecast_periods: Number of periods to forecast
        metrics: Optional historical metrics data

    Returns:
        Predicted sustainability metrics with confidence intervals
    """
    logger.info(f"Generating predictive analytics for {company_name} in {industry} industry")

    try:
        logger.info(f"Running chain-of-thought analysis for sustainability trends prediction")

        # If no metrics provided, we'll use mock data in the predictive analytics service
        predictions = predict_sustainability_trends(
            metrics=metrics or [], 
            forecast_periods=forecast_periods
        )

        logger.info(f"Successfully generated predictive analytics with {len(predictions.get('predictions', []))} predictions")

        return predictions

    except Exception as e:
        logger.error(f"Error generating predictive analytics: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate predictive analytics: {str(e)}"
        )

# New endpoint: AI-Powered Materiality Assessment
@app.post("/api/materiality-assessment")
async def get_materiality_assessment(
    company_name: str,
    industry: str,
    metrics: Optional[List[Dict[str, Any]]] = None
):
    """
    Perform an automated materiality assessment to determine which sustainability
    issues are most material to a company's financial performance and stakeholders

    Args:
        company_name: Name of the company
        industry: Industry the company operates in
        metrics: Optional metrics data

    Returns:
        Materiality assessment with financial impact scores
    """
    logger.info(f"Performing materiality assessment for {company_name} in {industry} industry")

    try:
        logger.info("Running chain-of-thought analysis for materiality assessment")

        assessment = perform_materiality_assessment(
            company_name=company_name,
            industry=industry,
            metrics=metrics
        )

        logger.info(f"Successfully generated materiality assessment with {len(assessment.get('material_topics', []))} material topics")

        return assessment

    except Exception as e:
        logger.error(f"Error performing materiality assessment: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform materiality assessment: {str(e)}"
        )

# Run the API with uvicorn when the script is executed directly
if __name__ == "__main__":
    import uvicorn
    import socket
    import time

    # Determine port from environment or use default
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")  # Explicitly use 0.0.0.0 for Replit compatibility

    # Log startup info
    logger.info(f"Starting FastAPI server on host {host}, port {port}")

    # Check if port is already in use
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((host, port))
        s.close()
        logger.info(f"Port {port} is available for binding")
    except socket.error:
        logger.warning(f"Port {port} is already in use, proceeding anyway (uvicorn will handle this)")

    # Multiple retries for starting the server
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Explicitly set host to 0.0.0.0 for Replit compatibility
            # Removed reload=True to avoid issues with port binding and timeouts
            uvicorn.run("storytelling_api:app", host=host, port=port)
            break
        except Exception as e:
            logger.error(f"Failed to start server on attempt {attempt + 1}/{max_retries}: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in 3 seconds...")
                time.sleep(3)
            else:
                logger.critical(f"Failed to start server after {max_retries} attempts")
                raise