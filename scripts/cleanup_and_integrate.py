import os
import shutil
import glob
from pathlib import Path

def remove_directory(directory):
    """Remove a directory and all its contents."""
    if os.path.exists(directory):
        print(f"Removing directory: {directory}")
        shutil.rmtree(directory)
    else:
        print(f"Directory not found: {directory}")

def remove_file(file_path):
    """Remove a file if it exists."""
    if os.path.exists(file_path):
        print(f"Removing file: {file_path}")
        os.remove(file_path)
    else:
        print(f"File not found: {file_path}")

def move_file(source, destination):
    """Move a file to its new location."""
    try:
        # Create destination directory if it doesn't exist
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.move(source, destination)
        print(f"Moved {source} to {destination}")
    except Exception as e:
        print(f"Error moving {source}: {e}")

def cleanup_codebase():
    """Remove redundant files and tests."""
    # Remove test directories and files
    remove_directory("tests")
    remove_directory("test_files")
    
    # Remove test files in root directory
    test_files = glob.glob("test_*.py") + glob.glob("test_*.txt")
    for file in test_files:
        remove_file(file)
    
    # Remove redundant files
    redundant_files = [
        "take_dashboard_screenshot.py",
        "take_screenshot.py",
        "temp.txt",
        "newest_test.txt",
        "cookies.txt",
        "curl_output.txt",
        "additional_doc1.txt",
        "additional_doc2.txt",
        "run_tests.py",
        "screenshot.py",
        "push_to_github.sh",
        "replit.nix",
        ".replit.new",
        "uv.lock"
    ]
    
    for file in redundant_files:
        remove_file(file)
    
    # Remove redundant directories
    redundant_dirs = [
        "clean_backups",
        "attached_assets",
        "page_samples",
        "replit_agent",
        ".replit-workflows",
        ".replit.d",
        "screenshots"
    ]
    
    for directory in redundant_dirs:
        remove_directory(directory)
    
    # Remove duplicate files
    duplicate_files = [
        "story_edit_script.js",  # Keep updated_story_edit_script.js
        "run_initialize_pinecone.py"  # Keep the one in src/frontend
    ]
    
    for file in duplicate_files:
        remove_file(file)

def integrate_trendsense():
    """Integrate trendsense functionality into the codebase."""
    # Create trendsense module in backend
    trendsense_dir = Path("src/backend/services/trendsense")
    trendsense_dir.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py file
    with open(trendsense_dir / "__init__.py", "w") as f:
        f.write("""\"\"\"
Trendsense module for sustainability trend analysis.
\"\"\"
""")
    
    # Create trendsense_api.py file
    with open(trendsense_dir / "trendsense_api.py", "w") as f:
        f.write("""\"\"\"
Trendsense API integration for sustainability trend analysis.
\"\"\"
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
    \"\"\"Client for interacting with the Trendsense API.\"\"\"
    
    def __init__(self, api_key: Optional[str] = None):
        \"\"\"Initialize the Trendsense API client.
        
        Args:
            api_key: API key for authentication. If not provided, will try to get from environment.
        \"\"\"
        self.api_key = api_key or os.getenv("TRENDSENSE_API_KEY")
        if not self.api_key:
            logger.warning("TRENDSENSE_API_KEY not found in environment variables")
        
        self.base_url = os.getenv("TRENDSENSE_API_URL", "https://api.trendsense.ai/v1")
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
    
    def get_trends(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        \"\"\"Get sustainability trends based on a query.
        
        Args:
            query: Search query for trends
            limit: Maximum number of trends to return
            
        Returns:
            List of trend objects
        \"\"\"
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
        \"\"\"Analyze a document for sustainability insights.
        
        Args:
            document_text: Text content of the document
            
        Returns:
            Analysis results
        \"\"\"
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
        \"\"\"Get sustainability score for a company.
        
        Args:
            company_id: Company identifier
            
        Returns:
            Sustainability score data
        \"\"\"
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
""")
    
    # Create trendsense_service.py file
    with open(trendsense_dir / "trendsense_service.py", "w") as f:
        f.write("""\"\"\"
Service layer for Trendsense functionality.
\"\"\"
import logging
from typing import Dict, List, Optional, Any
import pandas as pd
from .trendsense_api import trendsense_client

# Configure logging
logger = logging.getLogger(__name__)

class TrendsenseService:
    \"\"\"Service for working with sustainability trends.\"\"\"
    
    def __init__(self):
        \"\"\"Initialize the Trendsense service.\"\"\"
        self.api = trendsense_client
    
    def get_trend_analysis(self, query: str, limit: int = 10) -> Dict[str, Any]:
        \"\"\"Get trend analysis for a query.
        
        Args:
            query: Search query
            limit: Maximum number of trends to return
            
        Returns:
            Trend analysis results
        \"\"\"
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
        \"\"\"Analyze a sustainability report.
        
        Args:
            report_text: Text content of the report
            
        Returns:
            Analysis results
        \"\"\"
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
        \"\"\"Get sustainability data for a company.
        
        Args:
            company_id: Company identifier
            
        Returns:
            Sustainability data
        \"\"\"
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
""")
    
    # Update config.py to include trendsense settings
    config_file = Path("config/config.py")
    if config_file.exists():
        with open(config_file, "r") as f:
            config_content = f.read()
        
        # Add trendsense API settings if they don't exist
        if "TRENDSENSE_API_KEY" not in config_content:
            with open(config_file, "a") as f:
                f.write("""
# Trendsense API settings
TRENDSENSE_API_KEY = os.getenv("TRENDSENSE_API_KEY")
TRENDSENSE_API_URL = os.getenv("TRENDSENSE_API_URL", "https://api.trendsense.ai/v1")
""")
    
    # Update .env.example to include trendsense settings
    env_example_file = Path("config/.env.example")
    if env_example_file.exists():
        with open(env_example_file, "r") as f:
            env_content = f.read()
        
        # Add trendsense API settings if they don't exist
        if "TRENDSENSE_API_KEY" not in env_content:
            with open(env_example_file, "a") as f:
                f.write("""
# Trendsense API settings
TRENDSENSE_API_KEY=your-trendsense-api-key
TRENDSENSE_API_URL=https://api.trendsense.ai/v1
""")
    
    # Create a trendsense API endpoint in the backend
    api_dir = Path("src/backend/api")
    api_dir.mkdir(parents=True, exist_ok=True)
    
    with open(api_dir / "trendsense_api.py", "w") as f:
        f.write("""\"\"\"
API endpoints for Trendsense functionality.
\"\"\"
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Optional
from pydantic import BaseModel

from ..services.trendsense.trendsense_service import trendsense_service

router = APIRouter(prefix="/trendsense", tags=["trendsense"])

class TrendQuery(BaseModel):
    \"\"\"Query model for trend analysis.\"\"\"
    query: str
    limit: Optional[int] = 10

class DocumentAnalysis(BaseModel):
    \"\"\"Document for analysis.\"\"\"
    text: str

class CompanyQuery(BaseModel):
    \"\"\"Company query model.\"\"\"
    company_id: str

@router.post("/trends")
async def get_trends(query: TrendQuery):
    \"\"\"Get sustainability trends based on a query.\"\"\"
    result = trendsense_service.get_trend_analysis(query.query, query.limit)
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result

@router.post("/analyze")
async def analyze_document(document: DocumentAnalysis):
    \"\"\"Analyze a sustainability document.\"\"\"
    result = trendsense_service.analyze_sustainability_report(document.text)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/company")
async def get_company_sustainability(company: CompanyQuery):
    \"\"\"Get sustainability data for a company.\"\"\"
    result = trendsense_service.get_company_sustainability(company.company_id)
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result
""")
    
    # Update main.py to include the trendsense API router
    main_file = Path("src/backend/main.py")
    if main_file.exists():
        with open(main_file, "r") as f:
            main_content = f.read()
        
        # Add trendsense API router if it doesn't exist
        if "trendsense_api" not in main_content:
            # Find the imports section
            import_index = main_content.find("from fastapi import")
            if import_index != -1:
                # Add the import
                new_import = "from .api.trendsense_api import router as trendsense_router\\n"
                main_content = main_content[:import_index] + new_import + main_content[import_index:]
            
            # Find the app.include_router section
            router_index = main_content.find("app.include_router")
            if router_index != -1:
                # Add the router
                new_router = "app.include_router(trendsense_router)\\n"
                main_content = main_content[:router_index] + new_router + main_content[router_index:]
            
            # Write the updated content
            with open(main_file, "w") as f:
                f.write(main_content)
    
    print("Trendsense integration complete!")

def main():
    """Main function to clean up and integrate."""
    print("Cleaning up codebase...")
    cleanup_codebase()
    
    print("Integrating trendsense...")
    integrate_trendsense()
    
    print("Done!")

if __name__ == "__main__":
    main() 