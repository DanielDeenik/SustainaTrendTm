"""
Ethical AI & Transparency Compliance Routes

API routes for:
- Generating explanations for AI-driven sustainability analysis
- Detecting bias in AI-generated analysis
- Checking regulatory compliance
- Analyzing sustainability reports for compliance
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Dict, List, Any, Optional
import logging
import json
import traceback

from ..services.ethical_ai import (
    generate_explanation, 
    detect_bias, 
    check_regulatory_compliance,
    analyze_sustainability_report_compliance,
    generate_compliance_documentation
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/ethical-ai",
    tags=["ethical-ai"],
    responses={404: {"description": "Not found"}},
)

@router.post("/explain")
async def explain_analysis(request: Request):
    """
    Generate human-readable explanations for AI-driven analysis results.
    Implements Explainable AI (XAI) principles.
    """
    try:
        # Get request data
        data = await request.json()
        analysis_result = data.get("analysis_result", {})
        detail_level = data.get("detail_level", "medium")
        
        # Validate inputs
        if not analysis_result:
            raise HTTPException(status_code=400, detail="Analysis result is required")
            
        if detail_level not in ["low", "medium", "high"]:
            detail_level = "medium"  # Default to medium if invalid
        
        # Generate explanation
        result = generate_explanation(analysis_result, detail_level)
        
        return {
            "status": "success",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating explanation: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating explanation: {str(e)}")

@router.post("/detect-bias")
async def detect_analysis_bias(request: Request):
    """
    Detect potential bias in AI-generated sustainability analysis.
    """
    try:
        # Get request data
        data = await request.json()
        analysis_result = data.get("analysis_result", {})
        company_data = data.get("company_data", {})
        
        # Validate inputs
        if not analysis_result:
            raise HTTPException(status_code=400, detail="Analysis result is required")
            
        if not company_data:
            raise HTTPException(status_code=400, detail="Company data is required")
        
        # Detect bias
        result = detect_bias(analysis_result, company_data)
        
        return {
            "status": "success",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error detecting bias: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error detecting bias: {str(e)}")

@router.post("/check-compliance")
async def check_analysis_compliance(request: Request):
    """
    Check if an AI-generated analysis meets regulatory compliance requirements.
    """
    try:
        # Get request data
        data = await request.json()
        analysis_result = data.get("analysis_result", {})
        regulations = data.get("regulations", ["CSRD", "GDPR"])
        
        # Validate inputs
        if not analysis_result:
            raise HTTPException(status_code=400, detail="Analysis result is required")
            
        # Check compliance
        result = check_regulatory_compliance(analysis_result, regulations)
        
        return {
            "status": "success",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking compliance: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error checking compliance: {str(e)}")

@router.post("/analyze-report")
async def analyze_report_compliance(request: Request):
    """
    Analyze a sustainability report for compliance with regulations and ethical AI principles.
    """
    try:
        # Get request data
        data = await request.json()
        report_text = data.get("report_text", "")
        regulations = data.get("regulations", ["CSRD", "GDPR"])
        
        # Validate inputs
        if not report_text:
            raise HTTPException(status_code=400, detail="Report text is required")
            
        # Analyze report
        result = analyze_sustainability_report_compliance(report_text, regulations)
        
        return {
            "status": "success",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing report: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error analyzing report: {str(e)}")

@router.post("/generate-documentation")
async def generate_compliance_docs(request: Request):
    """
    Generate documentation for audit trails and compliance records.
    """
    try:
        # Get request data
        data = await request.json()
        analysis_result = data.get("analysis_result", {})
        compliance_report = data.get("compliance_report", {})
        
        # Validate inputs
        if not analysis_result:
            raise HTTPException(status_code=400, detail="Analysis result is required")
            
        if not compliance_report:
            raise HTTPException(status_code=400, detail="Compliance report is required")
        
        # Generate documentation
        result = generate_compliance_documentation(analysis_result, compliance_report)
        
        return {
            "status": "success",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating documentation: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating documentation: {str(e)}")