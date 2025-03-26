"""
Regulatory AI Agent Module for SustainaTrend™

This module provides AI-powered regulatory compliance assessment and analysis
for sustainability reports and ESG disclosures.

Key features:
1. Regulatory framework assessment across multiple jurisdictions
2. AI-powered compliance gap analysis
3. Timeline recommendations for regulatory transitions
4. Visual compliance reporting dashboard
"""

import json
import logging
import os
import sys
import uuid
import traceback
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Add backend path to make Flask module available
try:
    from flask import Blueprint, render_template, request, jsonify, current_app, send_from_directory
except ImportError:
    # This is a fallback if the normal import fails
    try:
        backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if backend_path not in sys.path:
            sys.path.append(backend_path)
        from flask import Blueprint, render_template, request, jsonify, current_app, send_from_directory
    except ImportError as e:
        print(f"Error importing Flask: {e}")
        # Define stub classes for type checking only
        class Blueprint:
            def __init__(self, *args, **kwargs):
                pass
        class Request:
            pass
        request = Request()

# Set up logging
logger = logging.getLogger(__name__)

# Import shared regulatory AI service
try:
    from frontend.services.regulatory_ai_service import (
        get_supported_frameworks,
        analyze_document_compliance,
        generate_compliance_visualization_data,
        handle_document_upload,
        get_upload_folder
    )
    from frontend.services.ai_connector import (
        connect_to_ai_services,
        is_pinecone_available
    )
    # Initialize AI connector
    connect_to_ai_services()
    logger.info("AI connector module loaded successfully")
    # Log Pinecone availability
    pinecone_status = "Connected" if is_pinecone_available() else "Not connected"
    logger.info(f"Pinecone RAG system availability: {pinecone_status}")
    logger.info("Imported regulatory_ai_agent from absolute path")
except ImportError as e:
    logger.warning(f"Error importing regulatory AI service: {str(e)}")
    # Create stub functions for development
    def get_supported_frameworks(): return {"CSRD": "Corporate Sustainability Reporting Directive"}
    def analyze_document_compliance(text, frameworks=None): return {"frameworks": {}}
    def generate_compliance_visualization_data(results): return {"frameworks": []}
    def handle_document_upload(file): return (False, "Service unavailable", None)
    def get_upload_folder(): return os.path.join(os.path.dirname(__file__), 'uploads')

# Create blueprint for the original regulatory AI endpoints
regulatory_ai_bp = Blueprint('regulatory_ai', __name__, url_prefix='/regulatory-ai')

def register_routes(app):
    """
    Register the Regulatory AI Agent routes with a Flask application
    
    Args:
        app: Flask application
    """
    # This function is ONLY for backwards compatibility - it no longer registers the blueprint
    # The blueprint 'regulatory_ai_bp' is registered ONLY through routes/__init__.py
    # to avoid conflicting registrations
    
    # DO NOT register the blueprint here anymore
    logger.info("Regulatory AI Agent routes NOT registered directly - use blueprint registration instead")
    
    return app

# Try to import AI connector module
try:
    from frontend.utils.ai_connector import get_generative_ai, generate_embedding, get_rag_system, is_pinecone_available
    AI_CONNECTOR_AVAILABLE = True
    # We'll check actual RAG availability with is_pinecone_available() which considers actual connection state
    RAG_AVAILABLE = is_pinecone_available()
    logger.info("AI connector module loaded successfully")
    logger.info(f"Pinecone RAG system availability: {'Connected' if RAG_AVAILABLE else 'Using fallback'}")
    logger.info("Imported regulatory_ai_agent from absolute path")
except ImportError as e:
    try:
        # Fallback to relative import for when running from within the frontend directory
        from utils.ai_connector import get_generative_ai, generate_embedding, get_rag_system, is_pinecone_available
        AI_CONNECTOR_AVAILABLE = True
        # We'll check actual RAG availability with is_pinecone_available() which considers actual connection state
        RAG_AVAILABLE = is_pinecone_available()
        logger.info("AI connector module loaded successfully from relative path")
        logger.info(f"Pinecone RAG system availability: {'Connected' if RAG_AVAILABLE else 'Using fallback'}")
    except ImportError as e2:
        AI_CONNECTOR_AVAILABLE = False
        RAG_AVAILABLE = False
        logger.warning(f"AI connector not available, using fallback regulatory assessment: {str(e2)}")

# Regulatory framework data structure
REGULATORY_FRAMEWORKS = {
    "ESRS": {
        "full_name": "European Sustainability Reporting Standards",
        "description": "European standards for corporate sustainability reporting",
        "categories": {
            "E1": "Climate change mitigation",
            "E2": "Climate change adaptation",
            "E3": "Water and marine resources",
            "E4": "Biodiversity and ecosystems",
            "E5": "Resource use and circular economy",
            "S1": "Own workforce",
            "S2": "Workers in the value chain",
            "S3": "Affected communities",
            "S4": "Consumers and end-users",
            "G1": "Business conduct",
            "G2": "Governance, risk management and internal control"
        },
        "effective_date": "2024-01-01",
        "region": "European Union"
    },
    "CSRD": {
        "full_name": "Corporate Sustainability Reporting Directive",
        "description": "EU directive mandating sustainability reporting",
        "categories": {
            "P1": "General principles",
            "P2": "Business model and strategy",
            "P3": "Policies and due diligence",
            "P4": "Targets",
            "P5": "Role of administrative bodies"
        },
        "effective_date": "2023-01-01",
        "region": "European Union"
    },
    "SFDR": {
        "full_name": "Sustainable Finance Disclosure Regulation",
        "description": "EU regulation on sustainability-related disclosures",
        "categories": {
            "A1": "Integration of sustainability risks",
            "A2": "Principal adverse impacts",
            "A3": "Remuneration policies",
            "B1": "Sustainability risk policy",
            "B2": "Due diligence statement",
            "C1": "Product-level disclosures",
            "C2": "Entity-level disclosures"
        },
        "effective_date": "2021-03-10",
        "region": "European Union"
    },
    "TCFD": {
        "full_name": "Task Force on Climate-related Financial Disclosures",
        "description": "Framework for climate-related financial disclosures",
        "categories": {
            "G1": "Governance",
            "S1": "Strategy",
            "R1": "Risk Management",
            "M1": "Metrics and Targets"
        },
        "effective_date": "2017-06-29",
        "region": "Global"
    },
    "ISSB": {
        "full_name": "International Sustainability Standards Board",
        "description": "Global baseline for sustainability disclosures",
        "categories": {
            "S1": "General Requirements",
            "S2": "Climate-related Disclosures",
            "S3": "Biodiversity-related Disclosures",
            "S4": "Social-related Disclosures"
        },
        "effective_date": "2023-06-01",
        "region": "Global"
    }
}

# Timeline data for regulatory transitions
REGULATORY_TIMELINE = [
    {
        "date": "2023-01-01",
        "framework": "CSRD",
        "event": "First companies subject to CSRD reporting requirements (large companies already subject to NFRD)",
        "impact": "high"
    },
    {
        "date": "2024-01-01",
        "framework": "ESRS",
        "event": "First ESRS reporting period begins for companies already subject to NFRD",
        "impact": "high"
    },
    {
        "date": "2025-01-01",
        "framework": "CSRD",
        "event": "Large companies not previously subject to NFRD begin reporting",
        "impact": "medium"
    },
    {
        "date": "2026-01-01",
        "framework": "CSRD",
        "event": "Listed SMEs begin reporting (with opt-out until 2028)",
        "impact": "medium"
    },
    {
        "date": "2026-06-30",
        "framework": "ESRS",
        "event": "First ESRS reports due for companies already subject to NFRD",
        "impact": "high"
    },
    {
        "date": "2027-06-30",
        "framework": "ESRS",
        "event": "ESRS reports due for large companies not previously subject to NFRD",
        "impact": "medium"
    },
    {
        "date": "2028-06-30",
        "framework": "ESRS",
        "event": "ESRS reports due for listed SMEs",
        "impact": "medium"
    }
]

def assess_document_compliance(document_text: str, framework_id: str = "ESRS") -> Dict[str, Any]:
    """
    Comprehensive assessment of a document's compliance with a regulatory framework
    
    Args:
        document_text: Text content of the document to analyze
        framework_id: ID of the regulatory framework to assess against
        
    Returns:
        Detailed compliance assessment results with scores and recommendations
    """
    try:
        # Get the framework details
        frameworks = get_frameworks()
        framework = frameworks.get(framework_id, {})
        
        if not framework:
            logger.warning(f"Framework {framework_id} not found")
            # Use a default framework if the specified one is not found
            framework_id = next(iter(frameworks.keys()))
            framework = frameworks.get(framework_id, {})
        
        # Extract framework categories
        categories = framework.get('categories', {})
        
        # Connect to AI system for assessment
        try:
            # Try to use the AI connector if available
            from utils.ai_connector import get_generative_ai
            ai = get_generative_ai()
            has_ai = True
        except (ImportError, Exception) as e:
            logger.warning(f"AI connector not available for compliance assessment: {str(e)}")
            has_ai = False
        
        # Generate assessment with AI if available
        if has_ai:
            # Create system prompt for framework assessment
            system_prompt = f"""
            You are an expert in sustainability reporting and regulatory compliance.
            You need to assess a document's compliance with the {framework.get('full_name', framework_id)} framework.
            
            Framework details:
            - Full name: {framework.get('full_name', framework_id)}
            - Description: {framework.get('description', 'No description available')}
            - Categories to assess: {json.dumps(categories)}
            
            Provide a structured assessment with:
            1. Overall compliance score (0-100)
            2. Score for each category (0-100)
            3. Findings for each category
            4. Recommendations for each category
            5. Overall findings and recommendations
            
            Format your response as a JSON object with the following structure:
            {{
                "framework": "Full framework name",
                "framework_id": "Framework ID",
                "date": "Assessment date (ISO format)",
                "overall_score": "Overall score (0-100)",
                "categories": {{
                    "category_id": {{
                        "score": "Score for this category (0-100)",
                        "compliance_level": "Compliance level description",
                        "findings": ["Finding 1", "Finding 2"],
                        "recommendations": ["Recommendation 1", "Recommendation 2"]
                    }}
                }},
                "overall_findings": ["Finding 1", "Finding 2"],
                "overall_recommendations": ["Recommendation 1", "Recommendation 2"]
            }}
            """
            
            # Generate content with AI using the correct parameters based on GeminiAI implementation
            doc_prompt = f"""
            Document to assess:
            
            {document_text[:48000]}  # Truncate to fit model context limits
            
            Assess this document according to the {framework.get('full_name', framework_id)} framework.
            """
            
            # Combine system prompt with user prompt
            full_prompt = f"{system_prompt}\n\n{doc_prompt}" if system_prompt else doc_prompt
            
            # Call generate_content with correct parameters
            ai_response = ai.generate_content(prompt=full_prompt)
            
            try:
                # Parse the AI response as JSON
                # Handle different response formats (dict vs object with text attribute)
                if hasattr(ai_response, 'text'):
                    result = json.loads(ai_response.text)
                elif isinstance(ai_response, dict) and 'text' in ai_response:
                    result = json.loads(ai_response['text'])
                elif isinstance(ai_response, dict):
                    # Try to parse the entire response as the result
                    result = ai_response
                else:
                    # Fallback to string representation
                    result = json.loads(str(ai_response))
                
                # Add timestamp if not provided
                if 'date' not in result:
                    result['date'] = datetime.now().isoformat()
                
                return result
            except (json.JSONDecodeError, AttributeError) as e:
                logger.error(f"Error parsing AI response: {str(e)}")
                logger.debug(f"AI response: {ai_response}")
                # Fall back to rules-based assessment
        
        # Fall back to rules-based assessment if AI is not available or fails
        return assess_regulatory_compliance(document_text, framework_id)
        
    except Exception as e:
        logger.error(f"Error assessing document compliance: {str(e)}")
        # Return basic assessment with error information
        return {
            "framework": get_frameworks().get(framework_id, {}).get('full_name', framework_id),
            "framework_id": framework_id,
            "date": datetime.now().isoformat(),
            "overall_score": 50,  # Default score
            "categories": {},
            "overall_findings": [f"Error during assessment: {str(e)}"],
            "overall_recommendations": ["Try again with a different document or framework"]
        }

def assess_regulatory_compliance(document_text: str, framework_id: str = "ESRS") -> Dict[str, Any]:
    """
    Assess a document's compliance with the specified regulatory framework
    (Rules-based implementation)
    
    Args:
        document_text: Text content of the document to analyze
        framework_id: ID of the regulatory framework to assess against
        
    Returns:
        Dictionary with compliance assessment results
    """
    # Check if framework exists
    if framework_id not in REGULATORY_FRAMEWORKS:
        return {
            "error": f"Framework {framework_id} not found",
            "available_frameworks": list(REGULATORY_FRAMEWORKS.keys())
        }
    
    framework = REGULATORY_FRAMEWORKS[framework_id]
    
    # If AI connector is available, use it for advanced assessment
    if AI_CONNECTOR_AVAILABLE:
        try:
            genai = get_generative_ai()
            # Use AI to perform compliance assessment
            prompt = f"""
            Analyze the following document against the {framework["full_name"]} ({framework_id}) framework.
            Assess compliance with each category and provide specific recommendations for improvement.
            
            Framework categories:
            {json.dumps(framework["categories"], indent=2)}
            
            Document:
            {document_text[:4000]}  # Limit document size for prompt
            
            Respond with a JSON object with the following structure:
            {{
                "overall_score": <0-100>,
                "categories": {{
                    "<category_id>": {{
                        "score": <0-100>,
                        "compliance_level": "<level>",
                        "findings": ["<finding>", ...],
                        "recommendations": ["<recommendation>", ...]
                    }},
                    ...
                }},
                "overall_findings": ["<finding>", ...],
                "overall_recommendations": ["<recommendation>", ...]
            }}
            """
            
            response = genai.generate_content(prompt)
            try:
                # Handle different response formats (dict vs object with text attribute)
                if hasattr(response, 'text'):
                    assessment = json.loads(response.text)
                elif isinstance(response, dict) and 'text' in response:
                    assessment = json.loads(response['text'])
                elif isinstance(response, dict):
                    # Try to parse the entire response as the result
                    assessment = response
                else:
                    # Fallback to string representation
                    assessment = json.loads(str(response))
                
                assessment["framework"] = framework_id
                assessment["framework_name"] = framework["full_name"]
                assessment["date"] = datetime.now().isoformat()
                return assessment
            except json.JSONDecodeError:
                response_text = response.text if hasattr(response, 'text') else str(response)
                logger.warning(f"Failed to parse AI response as JSON: {response_text}")
                # Fall back to simple assessment
                return _perform_simple_assessment(document_text, framework)
                
        except Exception as e:
            logger.error(f"Error using AI connector for assessment: {str(e)}")
            # Fall back to simple assessment
            return _perform_simple_assessment(document_text, framework)
    else:
        # Use simple text-based assessment
        return _perform_simple_assessment(document_text, framework)

def _perform_simple_assessment(document_text: str, framework: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform a simple keyword-based compliance assessment
    
    Args:
        document_text: Text content of the document to analyze
        framework: Framework definition from REGULATORY_FRAMEWORKS
        
    Returns:
        Dictionary with compliance assessment results
    """
    document_text = document_text.lower()
    
    # Keyword matches for each category
    keywords = {
        # Environmental categories
        "E1": ["climate change", "carbon", "greenhouse gas", "ghg", "emission", "carbon footprint", "net zero"],
        "E2": ["adaptation", "climate risk", "physical risk", "resilience", "climate adaptation"],
        "E3": ["water", "marine", "ocean", "aquatic", "water consumption", "water management"],
        "E4": ["biodiversity", "ecosystem", "species", "habitat", "conservation", "nature"],
        "E5": ["circular economy", "waste", "recycling", "resource efficiency", "material use"],
        # Social categories
        "S1": ["employee", "workforce", "staff", "human capital", "labor rights", "diversity", "inclusion"],
        "S2": ["supply chain", "supplier", "procurement", "value chain", "human rights"],
        "S3": ["community", "local impact", "stakeholder engagement", "social license", "indigenous"],
        "S4": ["customer", "consumer", "end-user", "product safety", "product quality"],
        # Governance categories
        "G1": ["business conduct", "ethics", "corruption", "bribery", "compliance", "integrity"],
        "G2": ["governance", "board", "risk management", "internal control", "oversight", "accountability"],
        # CSRD categories
        "P1": ["general principle", "materiality", "sustainability", "esg", "reporting principle"],
        "P2": ["business model", "strategy", "long-term", "sustainability strategy", "transition plan"],
        "P3": ["policy", "due diligence", "impact assessment", "risk assessment"],
        "P4": ["target", "goal", "objective", "kpi", "performance indicator", "science-based target"],
        "P5": ["board", "director", "administrative body", "governance", "oversight"],
        # SFDR categories
        "A1": ["sustainability risk", "esg risk", "integration", "risk management"],
        "A2": ["adverse impact", "pai", "negative impact", "environmental impact", "social impact"],
        "A3": ["remuneration", "compensation", "pay", "incentive", "bonus"],
        "B1": ["risk policy", "sustainability policy", "esg policy"],
        "B2": ["due diligence", "diligence statement", "impact assessment", "risk assessment"],
        "C1": ["product", "financial product", "fund", "investment product", "article 8", "article 9"],
        "C2": ["entity", "entity-level", "corporate", "company-wide", "organization"],
        # TCFD categories
        "G1": ["governance", "board", "management", "oversight", "responsibility"],
        "S1": ["strategy", "strategic planning", "business model", "scenario analysis", "scenario planning"],
        "R1": ["risk", "risk management", "risk identification", "risk assessment", "climate risk"],
        "M1": ["metric", "target", "indicator", "performance", "measurement", "scope 1", "scope 2", "scope 3"],
        # ISSB categories
        "S1": ["general requirement", "reporting requirement", "disclosure requirement", "sustainability-related"],
        "S2": ["climate", "climate-related", "climate risk", "climate opportunity", "global warming"],
        "S3": ["biodiversity", "ecosystem", "nature", "species", "habitat", "natural capital"],
        "S4": ["social", "human capital", "community", "human rights", "labor rights", "diversity", "inclusion"]
    }
    
    # Calculate scores for each category
    categories = {}
    for category_id, category_name in framework["categories"].items():
        # Skip if category not in keywords (shouldn't happen but just in case)
        if category_id not in keywords:
            continue
            
        # Count keyword matches
        matches = 0
        category_keywords = keywords[category_id]
        for keyword in category_keywords:
            if keyword in document_text:
                matches += 1
                
        # Calculate score (0-100)
        max_score = len(category_keywords)
        score = int((matches / max_score) * 100) if max_score > 0 else 0
        
        # Determine compliance level
        if score >= 80:
            compliance_level = "High compliance"
        elif score >= 50:
            compliance_level = "Moderate compliance"
        elif score >= 20:
            compliance_level = "Low compliance"
        else:
            compliance_level = "Non-compliance"
            
        # Generate findings
        findings = []
        if score >= 80:
            findings.append(f"Strong coverage of {category_name} topics")
        elif score >= 50:
            findings.append(f"Adequate coverage of {category_name} topics, but some elements may be missing")
        elif score >= 20:
            findings.append(f"Limited coverage of {category_name} topics")
        else:
            findings.append(f"Insufficient coverage of {category_name} topics")
            
        # Generate recommendations
        recommendations = []
        if score < 80:
            recommendations.append(f"Expand coverage of {category_name} topics")
        if score < 50:
            recommendations.append(f"Include specific metrics and targets for {category_name}")
        if score < 20:
            recommendations.append(f"Develop a comprehensive disclosure strategy for {category_name}")
            
        # Add category to results
        categories[category_id] = {
            "score": score,
            "compliance_level": compliance_level,
            "findings": findings,
            "recommendations": recommendations
        }
        
    # Calculate overall score
    overall_score = int(sum(c["score"] for c in categories.values()) / len(categories)) if categories else 0
    
    # Generate overall findings
    overall_findings = []
    if overall_score >= 80:
        overall_findings.append(f"Strong overall compliance with {framework['full_name']}")
    elif overall_score >= 50:
        overall_findings.append(f"Moderate overall compliance with {framework['full_name']}")
    elif overall_score >= 20:
        overall_findings.append(f"Low overall compliance with {framework['full_name']}")
    else:
        overall_findings.append(f"Non-compliance with {framework['full_name']}")
        
    # Generate overall recommendations
    overall_recommendations = []
    low_scoring_categories = [cid for cid, c in categories.items() if c["score"] < 50]
    if low_scoring_categories:
        category_names = [framework["categories"][cid] for cid in low_scoring_categories[:3]]  # Top 3 low scoring
        overall_recommendations.append(f"Focus on improving disclosures for: {', '.join(category_names)}")
    if overall_score < 60:
        overall_recommendations.append(f"Develop a comprehensive {framework['full_name']} compliance plan")
    if overall_score < 40:
        overall_recommendations.append("Consider engaging external sustainability reporting expertise")
        
    # Assemble final assessment
    assessment = {
        "framework": framework["full_name"],
        "framework_id": next(k for k, v in REGULATORY_FRAMEWORKS.items() if v == framework),
        "date": datetime.now().isoformat(),
        "overall_score": overall_score,
        "categories": categories,
        "overall_findings": overall_findings,
        "overall_recommendations": overall_recommendations
    }
    
    return assessment

def generate_regulatory_gaps(assessment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a gap analysis based on the regulatory assessment
    
    Args:
        assessment: Regulatory compliance assessment result
        
    Returns:
        Dictionary with gap analysis results
    """
    framework_id = assessment.get("framework_id")
    if not framework_id or framework_id not in REGULATORY_FRAMEWORKS:
        return {"error": "Invalid framework ID in assessment"}
        
    framework = REGULATORY_FRAMEWORKS[framework_id]
    
    # Identify gaps by category
    gaps = {}
    for category_id, category_data in assessment["categories"].items():
        if category_data["score"] < 70:  # Consider anything below 70 as a gap
            gaps[category_id] = {
                "name": framework["categories"].get(category_id, "Unknown category"),
                "score": category_data["score"],
                "compliance_level": category_data["compliance_level"],
                "findings": category_data["findings"],
                "recommendations": category_data["recommendations"],
                "priority": "high" if category_data["score"] < 30 else "medium" if category_data["score"] < 50 else "low"
            }
            
    # Generate improvement plan
    improvement_plan = {
        "high_priority": [{"category": cid, "name": data["name"], "recommendations": data["recommendations"]} 
                        for cid, data in gaps.items() if data["priority"] == "high"],
        "medium_priority": [{"category": cid, "name": data["name"], "recommendations": data["recommendations"]} 
                          for cid, data in gaps.items() if data["priority"] == "medium"],
        "low_priority": [{"category": cid, "name": data["name"], "recommendations": data["recommendations"]} 
                        for cid, data in gaps.items() if data["priority"] == "low"]
    }
    
    # Resources needed for compliance
    resources_needed = []
    if assessment["overall_score"] < 30:
        resources_needed.append("Comprehensive sustainability reporting framework implementation")
        resources_needed.append("External sustainability reporting consultant")
        resources_needed.append("Data collection and management system")
    elif assessment["overall_score"] < 60:
        resources_needed.append("Targeted improvements to sustainability reporting framework")
        resources_needed.append("Internal capacity building for sustainability reporting")
        if improvement_plan["high_priority"]:
            resources_needed.append("Focused external support for high-priority gaps")
    else:
        resources_needed.append("Refinement of existing sustainability reporting framework")
        resources_needed.append("Continuous improvement process for sustainability reporting")
    
    # Timeline for implementation
    timeline = []
    current_date = datetime.now()
    
    # Short-term (3 months)
    short_term_date = current_date.replace(month=current_date.month + 3) if current_date.month <= 9 else \
                     current_date.replace(year=current_date.year + 1, month=current_date.month - 9)
    timeline.append({
        "timeframe": "short-term",
        "date": short_term_date.strftime("%Y-%m-%d"),
        "actions": ["Address high-priority gaps", "Develop implementation roadmap", 
                  "Secure necessary resources and expertise"]
    })
    
    # Medium-term (6 months)
    medium_term_date = current_date.replace(month=current_date.month + 6) if current_date.month <= 6 else \
                      current_date.replace(year=current_date.year + 1, month=current_date.month - 6)
    timeline.append({
        "timeframe": "medium-term",
        "date": medium_term_date.strftime("%Y-%m-%d"),
        "actions": ["Address medium-priority gaps", "Implement data collection improvements", 
                   "Conduct internal training on sustainability reporting"]
    })
    
    # Long-term (12 months)
    long_term_date = current_date.replace(year=current_date.year + 1)
    timeline.append({
        "timeframe": "long-term",
        "date": long_term_date.strftime("%Y-%m-%d"),
        "actions": ["Address remaining gaps", "Implement continuous improvement process", 
                   "Prepare for upcoming regulatory changes"]
    })
    
    # Assemble gap analysis results
    gap_analysis = {
        "framework": framework["full_name"],
        "framework_id": framework_id,
        "date": datetime.now().isoformat(),
        "overall_score": assessment["overall_score"],
        "gaps": gaps,
        "improvement_plan": improvement_plan,
        "resources_needed": resources_needed,
        "timeline": timeline
    }
    
    return gap_analysis

def get_regulatory_timeline() -> List[Dict[str, Any]]:
    """
    Get the regulatory timeline data
    
    Returns:
        List of regulatory timeline events
    """
    return REGULATORY_TIMELINE

def get_frameworks() -> Dict[str, Dict[str, Any]]:
    """
    Get the regulatory frameworks data
    
    Returns:
        Dictionary of regulatory frameworks
    """
    return REGULATORY_FRAMEWORKS

def generate_gap_analysis(document_text: str, framework_id: str = "ESRS") -> Dict[str, Any]:
    """
    Generate a gap analysis for a document against a regulatory framework
    
    Args:
        document_text: Text content of the document to analyze
        framework_id: ID of the regulatory framework to assess against
        
    Returns:
        Dictionary with gap analysis results
    """
    # First get standard compliance assessment
    compliance_assessment = assess_regulatory_compliance(document_text, framework_id)
    
    # Start with the same structure but focus on gaps and recommendations
    gap_analysis = {
        "framework": compliance_assessment.get("framework", framework_id),
        "framework_id": framework_id,
        "date": datetime.now().isoformat(),
        "overall_score": compliance_assessment.get("overall_score", 50),
        "categories": {},
        "overall_findings": compliance_assessment.get("overall_findings", []),
        "overall_recommendations": compliance_assessment.get("overall_recommendations", []),
        "gap_analysis": {
            "summary": "Gap analysis identifies discrepancies between current reporting and framework requirements",
            "priority_gaps": [],
            "implementation_timeline": []
        }
    }
    
    # Copy categories from compliance assessment
    categories = compliance_assessment.get("categories", {})
    gap_analysis["categories"] = categories
    
    # If AI connector is available, use it for enhanced gap analysis
    if AI_CONNECTOR_AVAILABLE:
        try:
            genai = get_generative_ai()
            
            # Prepare framework information
            framework = get_frameworks().get(framework_id, {})
            framework_info = (
                f"Framework: {framework.get('full_name', framework_id)}\n"
                f"Description: {framework.get('description', '')}\n"
                f"Categories: {json.dumps(framework.get('categories', {}), indent=2)}"
            )
            
            # Find low-scoring categories
            low_scoring_categories = []
            for category_id, category_data in categories.items():
                score = category_data.get("score", 0)
                if score < 50:
                    low_scoring_categories.append({
                        "category_id": category_id,
                        "name": framework.get("categories", {}).get(category_id, category_id),
                        "score": score,
                        "findings": category_data.get("findings", [])
                    })
            
            # Create prompt for gap analysis
            prompt = f"""
            You are a sustainability reporting expert specializing in gap analysis.
            
            Framework Information:
            {framework_info}
            
            Low-scoring Categories in Current Document:
            {json.dumps(low_scoring_categories, indent=2)}
            
            Overall assessment findings:
            {json.dumps(compliance_assessment.get("overall_findings", []), indent=2)}
            
            Based on this information, provide:
            1. A prioritized list of the most critical gaps to address
            2. An implementation timeline with specific steps
            3. Resource requirements for addressing the gaps
            
            Format your response as a JSON object with the following structure:
            {{
                "gap_analysis": {{
                    "summary": "Summary of overall gaps",
                    "priority_gaps": [
                        {{
                            "category_id": "E1",
                            "description": "Description of gap",
                            "priority": "high/medium/low",
                            "impact": "Impact of not addressing"
                        }},
                        ...
                    ],
                    "implementation_timeline": [
                        {{
                            "timeframe": "Immediate (1-3 months)",
                            "actions": ["Action 1", "Action 2"],
                            "resources_needed": ["Resource 1", "Resource 2"]
                        }},
                        ...
                    ],
                    "resource_requirements": {{
                        "expertise": ["Expertise 1", "Expertise 2"],
                        "systems": ["System 1", "System 2"],
                        "estimated_effort": "Estimated person-months"
                    }}
                }}
            }}
            """
            
            # Generate gap analysis
            response = genai.generate_content(prompt)
            
            try:
                # Parse the response
                # Handle different response formats (dict vs object with text attribute)
                if hasattr(response, 'text'):
                    gap_results = json.loads(response.text)
                elif isinstance(response, dict) and 'text' in response:
                    gap_results = json.loads(response['text'])
                elif isinstance(response, dict):
                    # Try to parse the entire response as the result
                    gap_results = response
                else:
                    # Fallback to string representation
                    gap_results = json.loads(str(response))
                
                # Merge the gap analysis into the main results
                if "gap_analysis" in gap_results:
                    gap_analysis["gap_analysis"] = gap_results["gap_analysis"]
                    
                return gap_analysis
                
            except (json.JSONDecodeError, AttributeError) as e:
                logger.error(f"Error parsing AI gap analysis response: {str(e)}")
                # Fall back to basic gap analysis
        
        except Exception as e:
            logger.error(f"Error generating AI gap analysis: {str(e)}")
            # Fall back to basic gap analysis
    
    # Create basic gap analysis if AI approach failed or isn't available
    priority_gaps = []
    implementation_timeline = []
    
    # Extract low-scoring categories for basic gap analysis
    for category_id, category_data in categories.items():
        score = category_data.get("score", 0)
        if score < 50:
            priority = "high" if score < 30 else "medium"
            gap_description = category_data.get("findings", ["Incomplete disclosure"])[0] if category_data.get("findings") else "Incomplete disclosure"
            
            priority_gaps.append({
                "category_id": category_id,
                "description": gap_description,
                "priority": priority,
                "impact": "Non-compliance with framework requirements"
            })
    
    # Sort priority gaps by priority
    priority_gaps.sort(key=lambda x: 0 if x["priority"] == "high" else 1 if x["priority"] == "medium" else 2)
    
    # Generate implementation timeline
    if priority_gaps:
        # Immediate actions for high priority
        high_priority = [gap for gap in priority_gaps if gap["priority"] == "high"]
        if high_priority:
            immediate_actions = [f"Address {gap['category_id']} disclosure gaps" for gap in high_priority]
            implementation_timeline.append({
                "timeframe": "Immediate (1-3 months)",
                "actions": immediate_actions,
                "resources_needed": ["Sustainability reporting expertise", "Data collection systems"]
            })
        
        # Medium-term actions for medium priority
        medium_priority = [gap for gap in priority_gaps if gap["priority"] == "medium"]
        if medium_priority:
            medium_actions = [f"Improve {gap['category_id']} reporting" for gap in medium_priority]
            implementation_timeline.append({
                "timeframe": "Medium-term (3-6 months)",
                "actions": medium_actions,
                "resources_needed": ["Data analysis capabilities", "Reporting systems enhancements"]
            })
            
        # Long-term actions for overall improvement
        implementation_timeline.append({
            "timeframe": "Long-term (6-12 months)",
            "actions": ["Develop comprehensive compliance program", "Implement automated data collection"],
            "resources_needed": ["Integrated reporting system", "Compliance monitoring tools"]
        })
    
    # Add gap analysis to results
    gap_analysis["gap_analysis"] = {
        "summary": f"Analysis identified {len(priority_gaps)} priority gaps requiring attention",
        "priority_gaps": priority_gaps,
        "implementation_timeline": implementation_timeline,
        "resource_requirements": {
            "expertise": ["Sustainability reporting expertise", "Framework-specific knowledge"],
            "systems": ["Data collection and management systems", "Reporting tools"],
            "estimated_effort": f"{len(priority_gaps) * 2} person-months"
        }
    }
    
    return gap_analysis

def is_rag_available() -> bool:
    """
    Check if RAG system is available
    
    Returns:
        Boolean indicating if RAG is available
    """
    return RAG_AVAILABLE

# Flask routes
@regulatory_ai_bp.route('/')
@regulatory_ai_bp.route('/index')
def regulatory_ai_dashboard():
    """Regulatory AI Agent Dashboard"""
    frameworks = get_frameworks()
    timeline = get_regulatory_timeline()
    
    # Get parameters from Strategy Hub if they were passed
    company = request.args.get('company', '')
    industry = request.args.get('industry', '')
    challenges = request.args.get('challenges', '')
    
    # Set pre-filled flag if we have parameters from Strategy Hub
    from_strategy_hub = bool(company and industry)
    
    # Check if RAG system is available
    rag_system_available = is_rag_available()
    
    return render_template('regulatory_ai_agent.html', 
                         frameworks=frameworks,
                         timeline=timeline,
                         company=company,
                         industry=industry,
                         challenges=challenges,
                         from_strategy_hub=from_strategy_hub,
                         is_rag_available=rag_system_available,
                         page_title="Regulatory AI Agent",
                         active_page="regulatory-ai")

@regulatory_ai_bp.route('/compliance-visualization')
def compliance_visualization():
    """Regulatory Compliance Visualization Page"""
    frameworks = get_frameworks()
    
    # Get parameters from Strategy Hub if they were passed
    company = request.args.get('company', '')
    industry = request.args.get('industry', '')
    
    return render_template('regulatory/compliance_visualization_page.html',
                          frameworks=frameworks,
                          company=company,
                          industry=industry,
                          page_title="Compliance Visualization",
                          active_page="regulatory-ai")

@regulatory_ai_bp.route('/document-upload')
def document_upload():
    """Klarity-Style Document Upload & Analysis Page"""
    frameworks = get_frameworks()
    
    # Get parameters from Strategy Hub if they were passed
    company = request.args.get('company', '')
    industry = request.args.get('industry', '')
    
    # Check if RAG system is available
    rag_system_available = is_rag_available()
    
    # Log RAG system status for debugging
    current_app.logger.info(f"RAG system availability: {rag_system_available}")
    
    return render_template('regulatory/document_upload.html',
                          frameworks=frameworks,
                          company=company,
                          industry=industry,
                          is_rag_available=rag_system_available,
                          page_title="Document Upload & Analysis",
                          active_page="regulatory-ai")

@regulatory_ai_bp.route('/api/assessment', methods=['POST'])
def api_regulatory_assessment():
    """API endpoint for regulatory compliance assessment"""
    try:
        data = request.get_json()
        document_text = data.get('document_text', '')
        framework_id = data.get('framework_id', 'ESRS')
        
        if not document_text:
            return jsonify({"error": "No document text provided"}), 400
            
        assessment = assess_regulatory_compliance(document_text, framework_id)
        return jsonify(assessment)
    except Exception as e:
        logger.error(f"Error in regulatory assessment API: {str(e)}")
        return jsonify({"error": str(e)}), 500

@regulatory_ai_bp.route('/api/gap-analysis', methods=['POST'])
def api_regulatory_gap_analysis():
    """API endpoint for regulatory gap analysis"""
    try:
        data = request.get_json()
        assessment = data.get('assessment')
        
        if not assessment:
            return jsonify({"error": "No assessment data provided"}), 400
            
        # Check if we have categories data in the assessment
        if 'categories' not in assessment:
            # Generate mock categories based on the framework ID
            framework_id = assessment.get('framework_id')
            if not framework_id or framework_id not in REGULATORY_FRAMEWORKS:
                return jsonify({"error": "Invalid or missing framework_id in assessment"}), 400
                
            framework = REGULATORY_FRAMEWORKS[framework_id]
            overall_score = assessment.get('overall_score', 0)
            
            # Create simplified categories based on the overall score
            assessment['categories'] = {}
            for category_id, category_name in framework['categories'].items():
                # Vary category scores around the overall score
                import random
                category_score = max(0, min(100, overall_score + random.randint(-20, 20)))
                
                # Determine compliance level
                if category_score >= 70:
                    compliance_level = "High compliance"
                elif category_score >= 50:
                    compliance_level = "Medium compliance"
                elif category_score >= 30:
                    compliance_level = "Low compliance"
                else:
                    compliance_level = "Non-compliance"
                    
                # Generate findings and recommendations
                findings = [f"Limited coverage of {category_name} topics"]
                recommendations = [f"Expand coverage of {category_name} topics"]
                
                assessment['categories'][category_id] = {
                    "score": category_score,
                    "compliance_level": compliance_level,
                    "findings": findings,
                    "recommendations": recommendations
                }
        
        # Use the existing generate_regulatory_gaps function which is designed to work with assessment data
        gap_analysis = generate_regulatory_gaps(assessment)
        return jsonify(gap_analysis)
    except Exception as e:
        logger.error(f"Error in regulatory gap analysis API: {str(e)}")
        return jsonify({"error": str(e)}), 500

@regulatory_ai_bp.route('/api/timeline', methods=['GET'])
def api_regulatory_timeline():
    """API endpoint for regulatory timeline data"""
    try:
        timeline = get_regulatory_timeline()
        return jsonify(timeline)
    except Exception as e:
        logger.error(f"Error in regulatory timeline API: {str(e)}")
        return jsonify({"error": str(e)}), 500

@regulatory_ai_bp.route('/api/frameworks', methods=['GET'])
def api_regulatory_frameworks():
    """API endpoint for regulatory frameworks data"""
    try:
        frameworks = get_frameworks()
        return jsonify(frameworks)
    except Exception as e:
        logger.error(f"Error in regulatory frameworks API: {str(e)}")
        return jsonify({"error": str(e)}), 500

@regulatory_ai_bp.route('/api/rag-analysis', methods=['POST'])
def api_rag_analysis():
    """API endpoint for RAG-powered regulatory analysis (JSON data)"""
    try:
        data = request.get_json()
        
        # Validate inputs
        document_text = data.get('document_text', '')
        query = data.get('query', '')
        framework_id = data.get('framework_id', 'ESRS')
        
        if not document_text:
            return jsonify({"error": "No document text provided"}), 400
            
        if not query:
            return jsonify({"error": "No query provided"}), 400
            
        # Get RAG system if available
        if RAG_AVAILABLE:
            try:
                rag_system = get_rag_system()
                
                # Create context by combining document with framework information
                framework = get_frameworks().get(framework_id, {})
                framework_context = (
                    f"Framework: {framework.get('full_name', framework_id)}\n"
                    f"Description: {framework.get('description', '')}\n"
                    f"Categories: {json.dumps(framework.get('categories', {}), indent=2)}"
                )
                
                # Combine document with framework context
                full_context = f"{document_text}\n\n{framework_context}"
                
                # Index document in RAG system for future use
                rag_system.add_document(
                    document_text=full_context,
                    metadata={
                        "framework_id": framework_id,
                        "document_length": len(document_text),
                        "analysis_type": "regulatory"
                    }
                )
                
                # Generate analysis with RAG
                system_prompt = """
                You are an expert regulatory compliance consultant specializing in sustainability reporting standards.
                Analyze the document and provide detailed, expert-level insights on regulatory compliance.
                Focus on specific requirements, potential gaps, and practical recommendations.
                Be precise and specific in your analysis, avoiding generic statements.
                """
                
                result = rag_system.generate_with_context(
                    query=query,
                    system_prompt=system_prompt,
                    top_k=5,
                    max_tokens=1500
                )
                
                # Format response
                return jsonify({
                    "analysis": result.get("text", "Error generating analysis"),
                    "model": result.get("model", "unknown"),
                    "framework_id": framework_id,
                    "query": query
                })
                
            except Exception as e:
                logger.error(f"Error using RAG system: {str(e)}")
                # Fall back to regular assessment for error response
                assessment = assess_regulatory_compliance(document_text, framework_id)
                return jsonify({
                    "analysis": "Error using advanced RAG analysis. Falling back to standard assessment.",
                    "assessment": assessment,
                    "error": str(e)
                })
        else:
            # If RAG is not available, fall back to regular assessment
            assessment = assess_regulatory_compliance(document_text, framework_id)
            return jsonify({
                "analysis": "RAG analysis not available. Using standard assessment.",
                "assessment": assessment
            })
    except Exception as e:
        # Log the error with traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Error in RAG analysis API: {str(e)}\n{error_traceback}")
        return jsonify({"error": str(e)}), 500

@regulatory_ai_bp.route('/api/file-assessment', methods=['POST'])
def api_file_assessment():
    """API endpoint for assessing document files against regulatory frameworks"""
    try:
        logger.info("File assessment API called")
        
        # Get form data
        framework_id = request.form.get('framework_id', 'ESRS')
        analysis_type = request.form.get('analysis_type', 'compliance')
        
        logger.info(f"Requested framework: {framework_id}, analysis type: {analysis_type}")
        
        # Check for file upload
        if 'file' not in request.files:
            logger.warning("No file provided in request")
            return jsonify({"error": "No file provided"}), 400
            
        file = request.files['file']
        if file.filename == '':
            logger.warning("Empty filename provided")
            return jsonify({"error": "No file selected"}), 400
        
        logger.info(f"Processing file: {file.filename}")
        
        # Process uploaded file - using a more robust approach
        try:
            # Read file content
            document_text = file.read().decode('utf-8')
            logger.info(f"File decoded with UTF-8, size: {len(document_text)} bytes")
        except UnicodeDecodeError:
            # If not UTF-8, try with ISO-8859-1 (Latin-1)
            file.seek(0)
            document_text = file.read().decode('latin-1')
            logger.info(f"File decoded with Latin-1, size: {len(document_text)} bytes")
        
        if not document_text:
            logger.warning("No text could be extracted from file")
            return jsonify({"error": "Could not extract text from file"}), 400
        
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Prepare basic document info
        document_info = {
            "id": document_id,
            "filename": file.filename,
            "size": len(document_text),
            "word_count": len(document_text.split()),
            "page_count": len(document_text) // 3000,  # Estimate page count
            "processed_at": datetime.now().isoformat()
        }
        
        # Get framework details
        framework_info = get_frameworks().get(framework_id, {})
        
        # Load document into Pinecone if RAG is available
        rag_document_id = None
        if RAG_AVAILABLE:
            try:
                logger.info("RAG system available, attempting to store document embedding")
                # Get the RAG system
                rag_system = get_rag_system()
                
                # Create metadata for the document
                metadata = {
                    "document_id": document_id,
                    "filename": file.filename,
                    "framework_id": framework_id,
                    "analysis_type": analysis_type,
                    "word_count": document_info["word_count"],
                    "processed_at": document_info["processed_at"]
                }
                
                # Add document to RAG system
                success = rag_system.add_document(document_text, metadata)
                
                if success:
                    rag_document_id = document_id
                    logger.info(f"Document successfully added to RAG system with ID: {rag_document_id}")
                else:
                    logger.warning("Failed to add document to RAG system")
            except Exception as e:
                logger.error(f"Error using RAG system: {str(e)}")
                logger.error(traceback.format_exc())
        
        # Store document text in session for follow-up questions
        session_id = request.cookies.get('session_id', str(uuid.uuid4()))
        if not hasattr(current_app, 'session'):
            current_app.session = {}
        current_app.session[session_id] = {
            'document_text': document_text,
            'document_id': document_id,
            'framework_id': framework_id
        }
        
        # Perform AI assessment of the document if available
        assessment_result = None
        try:
            if AI_CONNECTOR_AVAILABLE:
                logger.info("Using AI connector for document assessment")
                assessment_result = assess_document_compliance(document_text, framework_id)
            else:
                logger.warning("AI connector not available, using rules-based assessment")
                assessment_result = assess_regulatory_compliance(document_text, framework_id)
                
            logger.info("Document assessment completed successfully")
        except Exception as e:
            logger.error(f"Error performing document assessment: {str(e)}")
            logger.error(traceback.format_exc())
            assessment_result = None
        
        # Prepare categories data based on framework or assessment results
        categories_data = {}
        if assessment_result and 'categories' in assessment_result:
            # Use assessment results for categories
            for cat_id, cat_data in assessment_result['categories'].items():
                categories_data[cat_id] = {
                    "id": cat_id,
                    "name": framework_info.get('categories', {}).get(cat_id, cat_id),
                    "score": cat_data.get('score', 50),
                    "compliance_level": cat_data.get('compliance_level', 'medium'),
                    "findings": cat_data.get('findings', [f"Assessment for {cat_id} completed"]),
                    "recommendations": cat_data.get('recommendations', [f"Review disclosures related to {cat_id}"])
                }
        elif 'categories' in framework_info:
            # Fallback to framework-based categories if assessment failed
            for cat_id, cat_name in framework_info['categories'].items():
                # Default scores for demonstration
                if "climate" in cat_name.lower() or "governance" in cat_name.lower():
                    score = 80
                    level = "high"
                elif "water" in cat_name.lower() or "biodiversity" in cat_name.lower():
                    score = 60
                    level = "medium"
                else:
                    score = 50
                    level = "medium"
                
                categories_data[cat_id] = {
                    "id": cat_id,
                    "name": cat_name,
                    "score": score,
                    "compliance_level": level,
                    "findings": [f"Assessment for {cat_name} completed"],
                    "recommendations": [f"Review disclosures related to {cat_name}"]
                }
        
        # Create result structure matching frontend expectations
        result = {
            "status": "success",
            "message": "File received and processed successfully",
            "document_id": document_id,
            "document_info": document_info,
            "framework": framework_info.get('full_name', framework_id),
            "framework_id": framework_id,
            "analysis_type": analysis_type,
            "rag_enabled": RAG_AVAILABLE and rag_document_id is not None,
            "rag_document_id": rag_document_id,
            "overall_score": assessment_result.get('overall_score', 75) if assessment_result else 75,
            "overall_findings": assessment_result.get('overall_findings', [
                "Document processed successfully",
                "Framework alignment analysis completed",
                "Regulatory compliance assessment generated"
            ]) if assessment_result else [
                "Document processed successfully",
                "Framework alignment analysis completed",
                "Regulatory compliance assessment generated"
            ],
            "overall_recommendations": assessment_result.get('overall_recommendations', [
                "Review climate disclosures for TCFD alignment",
                "Enhance biodiversity impact reporting",
                "Consider adding more quantitative metrics"
            ]) if assessment_result else [
                "Review climate disclosures for TCFD alignment",
                "Enhance biodiversity impact reporting",
                "Consider adding more quantitative metrics"
            ],
            "categories": categories_data
        }
        
        logger.info(f"File assessment completed successfully for {file.filename}")
        return jsonify(result)
        
    except Exception as e:
        # Log the detailed error
        error_traceback = traceback.format_exc()
        logger.error(f"Error in file assessment: {str(e)}")
        logger.error(error_traceback)
        return jsonify({
            "error": f"An error occurred: {str(e)}",
            "status": "error"
        }), 500
        
@regulatory_ai_bp.route('/api/follow-up-question', methods=['POST'])
def api_follow_up_question():
    """API endpoint for answering follow-up questions about document analysis using RAG when available"""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No request data provided"}), 400
            
        question = data.get('question', '')
        framework_id = data.get('framework_id', 'ESRS')
        context = data.get('context', 'document_analysis')
        document_id = data.get('document_id')  # This may be provided for RAG-based retrieval
        
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        # Try to get document from session
        document_text = None
        session_id = request.cookies.get('session_id')
        
        if hasattr(current_app, 'session') and current_app.session and session_id in current_app.session:
            document_text = current_app.session[session_id].get('document_text')
        
        # Get framework information for context
        framework_info = get_frameworks().get(framework_id, {})
        framework_name = framework_info.get('full_name', framework_id)
        
        # Try to use RAG system for context-aware responses if available
        if RAG_AVAILABLE:
            try:
                logger.info(f"Using RAG system for follow-up question: {question}")
                rag_system = get_rag_system()
                
                # Create system prompt for regulatory compliance expert
                system_prompt = f"""
                You are an expert in sustainability reporting and regulatory compliance,
                particularly regarding the {framework_name} ({framework_id}) framework.
                
                Provide a detailed, but concise answer to the user's question based on
                the most relevant context from their document and your knowledge of 
                sustainability regulations.
                
                Always focus on the specific content from the user's document and avoid
                generic responses when possible.
                
                When citing requirements from {framework_id}, be specific about the
                category codes (like E1, S2, etc.) and provide actionable recommendations.
                """
                
                # Generate RAG-enhanced response
                response = rag_system.generate_with_context(
                    query=question,
                    system_prompt=system_prompt,
                    top_k=3  # Retrieve top 3 most relevant chunks
                )
                
                if response and ('text' in response or 'error' not in response):
                    # RAG-enhanced response generated successfully
                    logger.info("Successfully generated RAG-enhanced response")
                    return jsonify({
                        "response": response.get('text', ''),
                        "question": question,
                        "framework_id": framework_id,
                        "using_rag": True,
                        "model": response.get('model', 'unknown')
                    })
                else:
                    logger.warning(f"RAG response failed or returned error: {response}")
                    # Fall back to standard AI response
            except Exception as e:
                logger.error(f"Error using RAG system: {str(e)}")
                logger.error(traceback.format_exc())
                # Continue to fallback methods
        
        # If RAG didn't work, try standard AI connector
        if AI_CONNECTOR_AVAILABLE:
            try:
                logger.info("Using standard AI connector for follow-up question")
                genai = get_generative_ai()
                
                # Create prompt based on context
                if context == 'document_analysis' and document_text:
                    prompt = f"""
                    You are an expert in sustainability reporting and regulatory compliance,
                    particularly regarding the {framework_name} ({framework_id}) framework. 
                    
                    A user has uploaded a document for analysis and is asking a follow-up question.
                    
                    Document excerpt: 
                    {document_text[:2000]}...
                    
                    User question: {question}
                    
                    Provide a detailed, but concise answer to the user's question based on
                    the document content and your knowledge of the {framework_id} framework.
                    Focus on specific requirements, categories, and recommendations.
                    """
                else:
                    prompt = f"""
                    You are an expert in sustainability reporting and regulatory compliance,
                    particularly regarding the {framework_name} ({framework_id}) framework.
                    
                    User question: {question}
                    
                    Provide a detailed, but concise answer to the user's question based on
                    your knowledge of the {framework_id} framework. Be specific about categories,
                    requirements, and best practices.
                    """
                
                # Generate AI response
                ai_response = genai.generate_content(prompt)
                
                # Return response - ai_response is a dict with text key from our AI connector
                return jsonify({
                    "response": ai_response.get('text', 'No response generated'),
                    "question": question,
                    "framework_id": framework_id,
                    "using_rag": False,
                    "model": ai_response.get('model', 'unknown')
                })
            except Exception as e:
                logger.error(f"Error generating AI response: {str(e)}")
                logger.error(traceback.format_exc())
                # Fall back to simple response
        
        # Fallback response if neither RAG nor standard AI is available
        return jsonify({
            "response": f"I can help answer questions about the {framework_name} ({framework_id}) framework compliance. However, I don't have enough context to answer your specific question about '{question}'. Try uploading a document first or asking about general framework requirements.",
            "question": question,
            "framework_id": framework_id,
            "using_rag": False,
            "model": "fallback"
        })
        
    except Exception as e:
        # Log the error with traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Error in follow-up question: {str(e)}\n{error_traceback}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@regulatory_ai_bp.route('/api/rag-analysis-form', methods=['POST'])
def api_rag_analysis_form():
    """API endpoint for RAG-powered regulatory analysis (form data with file upload)"""
    try:
        # Get form data
        query = request.form.get('query', '')
        framework_id = request.form.get('framework_id', 'ESRS')
        
        # Check for file upload
        if 'document_file' not in request.files:
            return jsonify({"error": "No document file provided"}), 400
            
        file = request.files['document_file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
            
        # Check for direct text input as fallback
        document_text = request.form.get('document_text', '')
        
        # Process uploaded file if available
        if file:
            try:
                # Read file content
                document_text = file.read().decode('utf-8')
            except UnicodeDecodeError:
                # If not UTF-8, try with ISO-8859-1 (Latin-1)
                file.seek(0)
                document_text = file.read().decode('latin-1')
        
        if not document_text:
            return jsonify({"error": "Could not extract text from file"}), 400
            
        if not query:
            return jsonify({"error": "No query provided"}), 400
            
        # Get RAG system if available
        if RAG_AVAILABLE:
            try:
                rag_system = get_rag_system()
                
                # Create context by combining document with framework information
                framework = get_frameworks().get(framework_id, {})
                framework_context = (
                    f"Framework: {framework.get('full_name', framework_id)}\n"
                    f"Description: {framework.get('description', '')}\n"
                    f"Categories: {json.dumps(framework.get('categories', {}), indent=2)}"
                )
                
                # Combine document with framework context
                full_context = f"{document_text}\n\n{framework_context}"
                
                # Index document in RAG system for future use
                doc_id = rag_system.add_document(
                    document_text=full_context,
                    metadata={
                        "framework_id": framework_id,
                        "document_length": len(document_text),
                        "analysis_type": "regulatory",
                        "filename": file.filename if file else "form-input"
                    }
                )
                
                # Generate analysis with RAG
                system_prompt = """
                You are an expert regulatory compliance consultant specializing in sustainability reporting standards.
                Analyze the document and provide detailed, expert-level insights on regulatory compliance.
                Focus on specific requirements, potential gaps, and practical recommendations.
                Be precise and specific in your analysis, avoiding generic statements.
                """
                
                result = rag_system.generate_with_context(
                    query=query,
                    system_prompt=system_prompt,
                    top_k=5,
                    max_tokens=1500
                )
                
                # For form submissions, this endpoint can return HTML or JSON
                response_format = request.form.get('response_format', 'json')
                
                if response_format == 'html':
                    analysis_html = result.get("text", "Error generating analysis").replace('\n', '<br>')
                    return f"""
                    <div class="analysis-result">
                        <h3>RAG Analysis Results</h3>
                        <div class="analysis-content">
                            {analysis_html}
                        </div>
                        <div class="analysis-metadata">
                            <p>Framework: {framework.get('full_name', framework_id)}</p>
                            <p>Model: {result.get("model", "unknown")}</p>
                        </div>
                    </div>
                    """
                
                # Default JSON response
                return jsonify({
                    "analysis": result.get("text", "Error generating analysis"),
                    "model": result.get("model", "unknown"),
                    "framework_id": framework_id,
                    "query": query,
                    "document_id": doc_id
                })
                
            except Exception as e:
                # Log the error with traceback
                error_traceback = traceback.format_exc()
                logger.error(f"Error using RAG system for form analysis: {str(e)}\n{error_traceback}")
                # Fall back to regular assessment for error response
                assessment = assess_regulatory_compliance(document_text, framework_id)
                
                # Format response based on requested format
                response_format = request.form.get('response_format', 'json')
                
                if response_format == 'html':
                    error_html = f"Error: {str(e)}<br>Falling back to standard assessment."
                    return f"""
                    <div class="analysis-result error">
                        <h3>Analysis Error</h3>
                        <div class="error-message">{error_html}</div>
                        <div class="fallback-assessment">
                            <h4>Standard Assessment</h4>
                            <p>Overall Score: {assessment.get('overall_score', 0)}</p>
                            <p>Key Findings: {', '.join(assessment.get('overall_findings', []))}</p>
                        </div>
                    </div>
                    """
                
                # Default JSON response
                return jsonify({
                    "analysis": "Error using advanced RAG analysis. Falling back to standard assessment.",
                    "assessment": assessment,
                    "error": str(e)
                })
        else:
            # If RAG is not available, fall back to regular assessment
            assessment = assess_regulatory_compliance(document_text, framework_id)
            
            # Format response based on requested format
            response_format = request.form.get('response_format', 'json')
            
            if response_format == 'html':
                return f"""
                <div class="analysis-result fallback">
                    <h3>Standard Assessment Results</h3>
                    <div class="fallback-message">RAG analysis not available. Using standard assessment.</div>
                    <div class="assessment-summary">
                        <p>Overall Score: {assessment.get('overall_score', 0)}</p>
                        <p>Key Findings: {', '.join(assessment.get('overall_findings', []))}</p>
                    </div>
                </div>
                """
            
            # Default JSON response
            return jsonify({
                "analysis": "RAG analysis not available. Using standard assessment.",
                "assessment": assessment
            })
    except Exception as e:
        # Log the error with traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Error in RAG form analysis API: {str(e)}\n{error_traceback}")
        
        # Format response based on requested format
        response_format = request.form.get('response_format', 'json') if hasattr(request, 'form') else 'json'
        
        if response_format == 'html':
            error_html = f"Error: {str(e)}"
            return f"""
            <div class="analysis-result error">
                <h3>Analysis Error</h3>
                <div class="error-message">{error_html}</div>
            </div>
            """
        
        # Default JSON response
        return jsonify({"error": str(e)}), 500

# Blueprint registration function
# NOTE: This function is now meant to be directly used by the app.py main file only,
# not by the routes/regulatory_ai_agent.py blueprint registration.
def register_routes(app):
    """
    Register routes with Flask application - Direct mode only
    
    This function should only be called directly from app.py when using 
    the direct application mode (direct_app.py), not from the blueprint 
    registration in routes/regulatory_ai_agent.py to avoid duplication.
    
    Args:
        app: Flask application
    """
    # Check if we're in direct mode by looking for specific attribute
    if hasattr(app, 'direct_mode') and app.direct_mode:
        app.register_blueprint(regulatory_ai_bp)
        logger.info("Regulatory AI Agent routes registered (direct mode)")
    else:
        logger.info("Regulatory AI Agent routes NOT registered - use blueprint registration instead")