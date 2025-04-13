"""
Service layer for Trendsense functionality.
"""
import logging
from typing import Dict, List, Optional, Any
import pandas as pd
from .trendsense_api import trendsense_client

# Configure logging
logger = logging.getLogger(__name__)

class TrendsenseService:
    """Service for working with sustainability trends."""
    
    def __init__(self):
        """Initialize the Trendsense service."""
        self.api = trendsense_client
    
    def get_trend_analysis(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Get trend analysis for a query.
        
        Args:
            query: Search query
            limit: Maximum number of trends to return
            
        Returns:
            Trend analysis results
        """
        trends = self.api.get_trends(query, limit)
        
        if not trends:
            return {
                "status": "error",
                "message": "No trends found",
                "trends": []
            }
        
        # Process trends
        processed_trends = []
        for trend in trends:
            processed_trend = {
                "id": trend.get("id"),
                "title": trend.get("title"),
                "description": trend.get("description"),
                "source": trend.get("source"),
                "date": trend.get("date"),
                "relevance_score": trend.get("relevance_score", 0),
                "sentiment": trend.get("sentiment", "neutral"),
                "categories": trend.get("categories", []),
                "entities": trend.get("entities", [])
            }
            processed_trends.append(processed_trend)
        
        return {
            "status": "success",
            "count": len(processed_trends),
            "trends": processed_trends
        }
    
    def analyze_sustainability_report(self, report_text: str) -> Dict[str, Any]:
        """Analyze a sustainability report.
        
        Args:
            report_text: Text content of the report
            
        Returns:
            Analysis results
        """
        analysis = self.api.analyze_document(report_text)
        
        if "error" in analysis:
            return {
                "status": "error",
                "message": analysis["error"],
                "analysis": {}
            }
        
        # Process analysis results
        processed_analysis = {
            "summary": analysis.get("summary", ""),
            "key_findings": analysis.get("key_findings", []),
            "metrics": analysis.get("metrics", {}),
            "recommendations": analysis.get("recommendations", []),
            "risks": analysis.get("risks", []),
            "opportunities": analysis.get("opportunities", [])
        }
        
        return {
            "status": "success",
            "analysis": processed_analysis
        }
    
    def get_company_sustainability(self, company_id: str) -> Dict[str, Any]:
        """Get sustainability data for a company.
        
        Args:
            company_id: Company identifier
            
        Returns:
            Sustainability data
        """
        score_data = self.api.get_sustainability_score(company_id)
        
        if "error" in score_data:
            return {
                "status": "error",
                "message": score_data["error"],
                "data": {}
            }
        
        # Process score data
        processed_data = {
            "company_id": company_id,
            "company_name": score_data.get("company_name", ""),
            "overall_score": score_data.get("overall_score", 0),
            "environmental_score": score_data.get("environmental_score", 0),
            "social_score": score_data.get("social_score", 0),
            "governance_score": score_data.get("governance_score", 0),
            "trends": score_data.get("trends", []),
            "comparison": score_data.get("comparison", {})
        }
        
        return {
            "status": "success",
            "data": processed_data
        }

# Create a singleton instance
trendsense_service = TrendsenseService()
