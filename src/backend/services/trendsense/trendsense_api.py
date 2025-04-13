"""
Trendsense API integration for sustainability trend analysis.
"""
import os
import logging
from typing import Dict, List, Optional, Any
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class TrendsenseAPI:
    """Client for interacting with the Trendsense API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Trendsense API client.
        
        Args:
            api_key: API key for authentication. If not provided, will try to get from environment.
        """
        self.api_key = api_key or os.getenv("TRENDSENSE_API_KEY")
        if not self.api_key:
            logger.warning("TRENDSENSE_API_KEY not found in environment variables")
        
        self.base_url = os.getenv("TRENDSENSE_API_URL", "https://api.trendsense.ai/v1")
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
    
    def get_trends(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get sustainability trends based on a query.
        
        Args:
            query: Search query for trends
            limit: Maximum number of trends to return
            
        Returns:
            List of trend objects
        """
        if not self.api_key:
            logger.warning("Cannot fetch trends: API key not available")
            return []
        
        try:
            response = self.session.get(
                f"{self.base_url}/trends",
                params={"q": query, "limit": limit}
            )
            response.raise_for_status()
            return response.json().get("trends", [])
        except Exception as e:
            logger.error(f"Error fetching trends: {e}")
            return []
    
    def analyze_document(self, document_text: str) -> Dict[str, Any]:
        """Analyze a document for sustainability insights.
        
        Args:
            document_text: Text content of the document
            
        Returns:
            Analysis results
        """
        if not self.api_key:
            logger.warning("Cannot analyze document: API key not available")
            return {"error": "API key not available"}
        
        try:
            response = self.session.post(
                f"{self.base_url}/analyze",
                json={"text": document_text}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error analyzing document: {e}")
            return {"error": str(e)}
    
    def get_sustainability_score(self, company_id: str) -> Dict[str, Any]:
        """Get sustainability score for a company.
        
        Args:
            company_id: Company identifier
            
        Returns:
            Sustainability score data
        """
        if not self.api_key:
            logger.warning("Cannot get sustainability score: API key not available")
            return {"error": "API key not available"}
        
        try:
            response = self.session.get(
                f"{self.base_url}/companies/{company_id}/sustainability"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting sustainability score: {e}")
            return {"error": str(e)}

# Create a singleton instance
trendsense_client = TrendsenseAPI()
