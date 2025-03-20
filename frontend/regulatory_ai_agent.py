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
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Add backend path to make Flask module available
try:
    from flask import Blueprint, render_template, request, jsonify, current_app
except ImportError:
    # This is a fallback if the normal import fails
    try:
        backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if backend_path not in sys.path:
            sys.path.append(backend_path)
        from flask import Blueprint, render_template, request, jsonify, current_app
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

# Create blueprint
regulatory_ai_bp = Blueprint('regulatory_ai', __name__, url_prefix='/regulatory-ai')

def register_routes(app):
    """
    Register the Regulatory AI Agent routes with a Flask application
    
    Args:
        app: Flask application
    """
    # This function is called from routes/regulatory_ai_agent.py
    # The blueprint 'regulatory_ai_bp' is registered separately
    logger.info("Regulatory AI Agent routes registered")
    return app

# Try to import AI connector module
try:
    from frontend.utils.ai_connector import get_generative_ai, generate_embedding, get_rag_system
    AI_CONNECTOR_AVAILABLE = True
    RAG_AVAILABLE = True
    logger.info("AI connector module loaded successfully")
    logger.info("Imported regulatory_ai_agent from absolute path")
except ImportError as e:
    try:
        # Fallback to relative import for when running from within the frontend directory
        from utils.ai_connector import get_generative_ai, generate_embedding, get_rag_system
        AI_CONNECTOR_AVAILABLE = True
        RAG_AVAILABLE = True
        logger.info("AI connector module loaded successfully from relative path")
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
                result = json.loads(ai_response.text)
                
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
                assessment = json.loads(response.text)
                assessment["framework"] = framework_id
                assessment["framework_name"] = framework["full_name"]
                assessment["date"] = datetime.now().isoformat()
                return assessment
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse AI response as JSON: {response.text}")
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
        logger.error(f"Error in RAG analysis API: {str(e)}")
        return jsonify({"error": str(e)}), 500

@regulatory_ai_bp.route('/api/file-assessment', methods=['POST'])
def api_file_assessment():
    """API endpoint for assessing document files against regulatory frameworks"""
    try:
        # Get form data
        framework_id = request.form.get('framework_id', 'ESRS')
        
        # Check for file upload
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
            
        # Process uploaded file
        try:
            # Read file content
            document_text = file.read().decode('utf-8')
        except UnicodeDecodeError:
            # If not UTF-8, try with ISO-8859-1 (Latin-1)
            file.seek(0)
            document_text = file.read().decode('latin-1')
        
        if not document_text:
            return jsonify({"error": "Could not extract text from file"}), 400
            
        # Get AI assistant to perform the assessment
        assessment_result = assess_document_compliance(document_text, framework_id)
        
        return jsonify(assessment_result)
    except Exception as e:
        # Log the error
        app.logger.error(f"Error in file assessment: {str(e)}")
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
                logger.error(f"Error using RAG system for form analysis: {str(e)}")
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
        logger.error(f"Error in RAG form analysis API: {str(e)}")
        
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
def register_routes(app):
    """
    Register routes with Flask application
    
    Args:
        app: Flask application
    """
    app.register_blueprint(regulatory_ai_bp)
    logger.info("Regulatory AI Agent routes registered")