"""
Sustainability API Routes

This module provides API endpoints for sustainability analysis and storytelling.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

from services.ai_analysis import analyze_sustainability
from services.monetization import monetize_data
from services.strategy_ai import apa_ai_consultant
from services.storytelling_ai import generate_sustainability_story
from services.predictive_analytics import (
    predict_sustainability_trends, 
    perform_materiality_assessment
)

# Create router
router = APIRouter(
    prefix="/api/sustainability",
    tags=["sustainability"],
    responses={404: {"description": "Not found"}},
)

# Models
class StoryMetrics(BaseModel):
    views: int = 0
    likes: int = 0
    shares: int = 0
    impact_score: Optional[float] = None

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

# Routes
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "sustainability-api",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/analysis")
async def sustainability_analysis(company_name: str, industry: str):
    """Analyze sustainability for a company"""
    try:
        result = analyze_sustainability(company_name, industry)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze sustainability: {str(e)}"
        )

@router.post("/monetization")
async def monetization_strategy(company_name: str):
    """Generate monetization strategy for a company"""
    try:
        result = monetize_data(company_name)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate monetization strategy: {str(e)}"
        )

@router.post("/apa-strategy")
async def apa_strategy(company_name: str):
    """Generate APA strategy for a company"""
    try:
        result = apa_ai_consultant(company_name)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate APA strategy: {str(e)}"
        )

@router.post("/story")
async def get_sustainability_story(company_name: str, industry: str):
    """Generate a sustainability story for a company"""
    try:
        result = generate_sustainability_story(company_name, industry)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate sustainability story: {str(e)}"
        )

@router.post("/predictive-analytics")
async def get_predictive_analytics(
    company_name: str, 
    industry: str, 
    forecast_periods: int = 3,
    metrics: Optional[List[Dict[str, Any]]] = None
):
    """Generate predictive analytics for a company"""
    try:
        result = predict_sustainability_trends(
            company_name, 
            industry, 
            forecast_periods, 
            metrics
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate predictive analytics: {str(e)}"
        )

@router.post("/materiality-assessment")
async def get_materiality_assessment(
    company_name: str,
    industry: str,
    metrics: Optional[List[Dict[str, Any]]] = None
):
    """Generate materiality assessment for a company"""
    try:
        result = perform_materiality_assessment(
            company_name, 
            industry, 
            metrics
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate materiality assessment: {str(e)}"
        ) 