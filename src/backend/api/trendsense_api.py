"""
API endpoints for Trendsense functionality.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Optional
from pydantic import BaseModel

from ..services.trendsense.trendsense_service import trendsense_service

router = APIRouter(prefix="/trendsense", tags=["trendsense"])

class TrendQuery(BaseModel):
    """Query model for trend analysis."""
    query: str
    limit: Optional[int] = 10

class DocumentAnalysis(BaseModel):
    """Document for analysis."""
    text: str

class CompanyQuery(BaseModel):
    """Company query model."""
    company_id: str

@router.post("/trends")
async def get_trends(query: TrendQuery):
    """Get sustainability trends based on a query."""
    result = trendsense_service.get_trend_analysis(query.query, query.limit)
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result

@router.post("/analyze")
async def analyze_document(document: DocumentAnalysis):
    """Analyze a sustainability document."""
    result = trendsense_service.analyze_sustainability_report(document.text)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/company")
async def get_company_sustainability(company: CompanyQuery):
    """Get sustainability data for a company."""
    result = trendsense_service.get_company_sustainability(company.company_id)
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result
