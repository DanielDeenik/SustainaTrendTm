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
from services.storytelling_ai import generate_sustainability_story
from services.predictive_analytics import (
    predict_sustainability_trends, 
    perform_materiality_assessment
)

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

# In-memory storage for stories since we don't have a DB connection yet
stories_db = []
story_id_counter = 1

# Helper functions for story management
def get_story_by_id(story_id: int):
    for story in stories_db:
        if story["id"] == story_id:
            return story
    return None

def add_story(story_data):
    global story_id_counter
    story_data["id"] = story_id_counter
    story_id_counter += 1
    stories_db.append(story_data)
    return story_data

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
    """Get all sustainability stories"""
    logger.info(f"Getting stories with skip={skip}, limit={limit}")
    return stories_db[skip:skip+limit]

# Endpoint: Get Story by ID
@app.get("/api/stories/{story_id}", response_model=StoryResponse)
async def get_story(story_id: int):
    """Get a specific sustainability story by ID"""
    logger.info(f"Getting story with ID: {story_id}")
    story = get_story_by_id(story_id)
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

# Endpoint: Create Story with AI-Powered Sustainability Narrative
@app.post("/api/stories", response_model=StoryResponse, status_code=status.HTTP_201_CREATED)
async def create_story(story: StoryCreate):
    """Create a new sustainability story using AI-powered storytelling"""
    logger.info(f"Creating new story for company: {story.company_name}, industry: {story.industry}")

    try:
        # Generate sustainability story using AI
        logger.info("Starting chain-of-thought sustainability story generation...")
        sustainability_story = generate_sustainability_story(story.company_name, story.industry)
        logger.info("Sustainability story generation completed successfully")

        # Create story object
        story_data = story.dict()
        if not story.content:  # If content not provided, use AI-generated content
            story_data["content"] = sustainability_story

        # Add timestamps
        now = datetime.now()
        story_data["created_at"] = now
        story_data["updated_at"] = now

        # Add metrics if not provided
        if not story_data.get("metrics"):
            story_data["metrics"] = StoryMetrics().dict()

        # Save to our in-memory DB
        saved_story = add_story(story_data)

        logger.info(f"Successfully created story with ID: {saved_story['id']}")
        return saved_story

    except Exception as e:
        logger.error(f"Error creating sustainability story: {str(e)}")
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform materiality assessment: {str(e)}"
        )

# Run the API with uvicorn when the script is executed directly
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting FastAPI server on port {port}")
    uvicorn.run("storytelling_api:app", host="0.0.0.0", port=port, reload=True)