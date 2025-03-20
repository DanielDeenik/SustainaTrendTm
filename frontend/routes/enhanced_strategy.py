"""
Enhanced Strategy Hub Module for SustainaTrend™

This module provides routes for the new enhanced Strategy Hub with Finchat.io-level
UI polish and interactive components.

Features:
- Primary hub for all strategy-related functionality
- Consolidated monetization strategies (redirected from /monetization-strategies)
- Consolidated sustainability strategies
- Interactive framework selection guide
- Regulatory AI Agent integration
- Document analysis with PDF upload capabilities

Note: This is the definitive implementation for monetization and strategy features.
Other routes are configured to redirect here for a unified experience.
"""

import logging
import traceback
import uuid
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session

# Import common utilities and constants
import os

# Define path for template utils
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'utils'))
try:
    from template_utils import get_context_for_template
except ImportError:
    # Fallback function if import fails
    def get_context_for_template():
        return {"navigation": [], "theme_preference": "dark"}

# Import Strategy AI Consultant
try:
    sys.path.append('..')
    from strategy_ai_consultant import StrategyAIConsultant, STRATEGY_AI_CONSULTANT_AVAILABLE
    strategy_ai = StrategyAIConsultant()
    logger = logging.getLogger(__name__)
    logger.info("Strategy AI Consultant module loaded successfully in enhanced strategy")
except ImportError as e:
    STRATEGY_AI_CONSULTANT_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"Strategy AI Consultant module import failed in enhanced strategy: {str(e)}")
    
    # Define fallback class for function signature compatibility
    class FallbackStrategyAI:
        def generate_ai_strategy(self, company_name, industry, focus_areas=None, trend_analysis=None):
            return {
                "status": "error",
                "message": "The Strategy AI Consultant module is not available. Please check your installation."
            }
    
    strategy_ai = FallbackStrategyAI()

# Define Strategy Frameworks (moved from strategy.py to here for consolidation)
STRATEGY_FRAMEWORKS = {
    "sbti": {
        "name": "Science-Based Targets Initiative",
        "description": "Align corporate targets with the Paris Agreement's 1.5°C pathway.",
        "icon": "chart-line",
        "color": "green"
    },
    "tcfd": {
        "name": "Task Force on Climate-related Financial Disclosures",
        "description": "Framework for climate risk assessment and disclosure.",
        "icon": "file-text",
        "color": "blue" 
    },
    "csrd": {
        "name": "Corporate Sustainability Reporting Directive",
        "description": "EU reporting standards for sustainability information.",
        "icon": "clipboard-list",
        "color": "indigo"
    },
    "gri": {
        "name": "Global Reporting Initiative",
        "description": "Standards for sustainability reporting on economic, environmental and social impacts.",
        "icon": "globe",
        "color": "teal"
    },
    "sdg": {
        "name": "UN Sustainable Development Goals",
        "description": "17 integrated global goals for sustainable development.",
        "icon": "target",
        "color": "cyan"
    }
}

# Import storytelling functions if available
try:
    from frontend.sustainability_storytelling import (
        get_enhanced_stories, get_data_driven_stories, STORYTELLING_AVAILABLE
    )
except ImportError:
    STORYTELLING_AVAILABLE = False
    get_enhanced_stories = lambda **kwargs: []
    get_data_driven_stories = lambda: []

# Set up logging
logger = logging.getLogger(__name__)

# Create the blueprint
enhanced_strategy_bp = Blueprint('enhanced_strategy', __name__)

# Constants for feature availability
DOCUMENT_PROCESSOR_AVAILABLE = True
TREND_VIRALITY_AVAILABLE = True
SBTI_AVAILABLE = True
AI_CONSULTANT_AVAILABLE = STRATEGY_AI_CONSULTANT_AVAILABLE

# Industry-to-Framework mapping for recommendation engine
INDUSTRY_FRAMEWORK_MAPPING = {
    "energy": ["sbti", "tcfd", "csrd"],
    "technology": ["sdg", "gri", "csrd"],
    "financial": ["tcfd", "csrd", "gri"],
    "manufacturing": ["gri", "sbti", "csrd"],
    "healthcare": ["sdg", "gri", "csrd"],
    "retail": ["sdg", "gri", "sbti"],
    "agriculture": ["sbti", "gri", "sdg"],
    "transportation": ["sbti", "tcfd", "csrd"],
    "construction": ["gri", "sbti", "csrd"],
    "hospitality": ["sdg", "gri", "csrd"]
}

@enhanced_strategy_bp.route('/enhanced-strategy-hub')
def enhanced_strategy_hub():
    """
    Enhanced Strategy Hub with Finchat.io-level UI and Interactive Components
    
    This combines all strategy-related features into a modern, 3-dashboard interface:
    - Strategy Modeler: Document analysis with PDF upload capabilities
    - Virality Trends: Trend analysis with STEPPS framework visualization
    - Data Analysis: Flexible data integration from multiple sources
    """
    logger.info("Enhanced Strategy Hub route called")
    
    try:
        # Get navigation context
        nav_context = get_context_for_template()
        
        # Get recent documents (use real data in production)
        try:
            # In production, fetch real documents from database
            recent_documents = [
                {
                    "id": "sustainability_report_2024.pdf",
                    "title": "Sustainability Report 2024",
                    "category": "ESG Report",
                    "description": "Annual sustainability report with emissions data and ESG metrics.",
                    "timestamp": "March 1, 2024",
                    "page_count": 42
                },
                {
                    "id": "csrd_assessment.pdf",
                    "title": "CSRD Compliance Assessment",
                    "category": "Regulatory",
                    "description": "Assessment of company compliance with CSRD reporting requirements.",
                    "timestamp": "February 15, 2024",
                    "page_count": 18
                },
                {
                    "id": "emissions_data_2023.xlsx",
                    "title": "GHG Emissions Data 2023",
                    "category": "Data",
                    "description": "Greenhouse gas emissions data across all business operations.",
                    "timestamp": "January 20, 2024",
                    "page_count": 3
                }
            ]
        except Exception as e:
            logger.warning(f"Error fetching documents: {str(e)}")
            recent_documents = []
        
        # Get recent stories
        if STORYTELLING_AVAILABLE:
            try:
                # Fetch real stories from the database
                recent_stories = get_enhanced_stories(audience='all', category='all')
                # Limit the stories to display
                recent_stories = recent_stories[:3] if recent_stories and len(recent_stories) > 3 else recent_stories
                logger.info(f"Fetched {len(recent_stories)} stories for enhanced hub")
            except Exception as e:
                logger.warning(f"Error fetching stories for enhanced hub: {str(e)}")
                # Fall back to sample stories
                recent_stories = get_data_driven_stories()
                # Limit the stories to display
                recent_stories = recent_stories[:3] if recent_stories and len(recent_stories) > 3 else recent_stories
        else:
            # If storytelling is not available, use empty list
            recent_stories = []
        
        # Get monetization strategies
        try:
            from frontend.monetization_strategies import get_monetization_strategies
            monetization_strategies = get_monetization_strategies()
        except Exception as e:
            logger.warning(f"Error getting monetization strategies: {str(e)}")
            monetization_strategies = {}
        
        # Get marketing strategies
        try:
            from frontend.marketing_strategies import get_marketing_strategies
            marketing_strategies = get_marketing_strategies()
        except Exception as e:
            logger.warning(f"Error getting marketing strategies: {str(e)}")
            marketing_strategies = {}
        
        # Get trend data
        trend_data = None
        benchmark_data = None
        
        # Get STEPPS components
        try:
            from frontend.trend_virality_benchmarking import STEPPS_COMPONENTS
        except ImportError:
            STEPPS_COMPONENTS = {
                "S": {"name": "Social Currency", "description": "How sharing information makes people look to others"},
                "T": {"name": "Triggers", "description": "Environmental cues that prompt people to think about related things"},
                "E": {"name": "Emotion", "description": "When we care, we share; emotional content gets attention"},
                "P": {"name": "Public", "description": "Built to show, built to grow; visibility drives imitation"},
                "P": {"name": "Practical Value", "description": "Useful content gets shared more often"},
                "S": {"name": "Stories", "description": "Information travels under the guise of idle chatter"}
            }
        
        # SBTI categories
        try:
            from frontend.science_based_targets import SBTI_CATEGORIES
            sbti_targets = None
            sbti_reference_companies = None
        except ImportError:
            SBTI_CATEGORIES = {}
            sbti_targets = None
            sbti_reference_companies = None
        
        # Get active_nav from nav_context if available or set it
        if 'active_nav' in nav_context:
            # Remove active_nav from nav_context to avoid duplicate
            nav_context_copy = {k: v for k, v in nav_context.items() if k != 'active_nav'}
        else:
            nav_context_copy = nav_context
            
        # Render the enhanced template with all components
        return render_template(
            "strategy/enhanced_strategy_hub.html",
            page_title="Enhanced Strategy Hub",
            active_nav="strategy",  # Set the active navigation item to highlight in sidebar
            frameworks=STRATEGY_FRAMEWORKS,
            monetization_strategies=monetization_strategies,
            marketing_strategies=marketing_strategies,  # Added marketing strategies
            recent_documents=recent_documents,
            recent_stories=recent_stories,
            stepps_components=STEPPS_COMPONENTS,  # STEPPS virality components
            trend_data=trend_data,  # Added trend analysis data
            benchmark_data=benchmark_data,  # Added benchmark data
            sbti_categories=SBTI_CATEGORIES,  # Added Science-Based Targets categories
            sbti_targets=sbti_targets,  # Added Science-Based Targets data
            sbti_reference_companies=sbti_reference_companies,  # Added SBTI reference companies
            document_processor_available=DOCUMENT_PROCESSOR_AVAILABLE,
            storytelling_available=STORYTELLING_AVAILABLE,
            trend_virality_available=TREND_VIRALITY_AVAILABLE,  # Added flag for trend virality
            sbti_available=SBTI_AVAILABLE,  # Added flag for Science-Based Targets
            ai_consultant_available=AI_CONSULTANT_AVAILABLE,  # Added flag for AI Strategy Consultant
            **nav_context_copy
        )
        
    except Exception as e:
        logger.error(f"Error in enhanced strategy hub: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Show error page instead of redirecting to the now-removed strategy hub
        flash("An error occurred loading the Enhanced Strategy Hub. Please try again later.", "error")
        return render_template('error.html', 
                            error_title="Strategy Hub Error",
                            error_message="An error occurred loading the Enhanced Strategy Hub. Please try again later.",
                            return_link="/",
                            return_text="Return to Home")


@enhanced_strategy_bp.route('/api/strategy-hub/upload-pdf', methods=['POST'])
def api_upload_pdf():
    """API endpoint to upload and analyze PDF documents"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            logger.warning("No file part in request")
            return jsonify({
                "status": "error",
                "message": "No file part in the request"
            }), 400
            
        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            logger.warning("No file selected")
            return jsonify({
                "status": "error",
                "message": "No file selected"
            }), 400
            
        # Check file extension
        allowed_extensions = {'pdf', 'docx', 'doc', 'xlsx', 'xls', 'csv'}
        if '.' not in file.filename or file.filename.lower().rsplit('.', 1)[1] not in allowed_extensions:
            logger.warning(f"Invalid file extension: {file.filename}")
            return jsonify({
                "status": "error",
                "message": f"Invalid file extension. Allowed extensions: {', '.join(allowed_extensions)}"
            }), 400
            
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Get options from request
        extract_entities = request.form.get('extract_entities', 'false').lower() == 'true'
        benchmark = request.form.get('benchmark', 'false').lower() == 'true'
        regulatory_check = request.form.get('regulatory_check', 'false').lower() == 'true'
        
        # In a production environment, save the file and process it asynchronously
        # For this demo, we'll return a success response
        
        return jsonify({
            "status": "success",
            "message": "Document uploaded successfully",
            "file_id": file_id,
            "filename": file.filename,
            "analysis_url": url_for('enhanced_strategy.strategy_hub_document_view_redirect', document_id=file_id)
        })
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }), 500


@enhanced_strategy_bp.route('/api/strategy-hub/trend-analysis', methods=['POST'])
def api_trend_analysis():
    """API endpoint for trend analysis"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400
            
        trend = data.get('trend')
        industry = data.get('industry', 'all')
        
        if not trend:
            return jsonify({
                "status": "error",
                "message": "No trend specified"
            }), 400
        
        # In a production environment, this would call your trend analysis service
        # For this demo, we'll return a simulated response
        
        return jsonify({
            "status": "success",
            "trend": trend,
            "industry": industry,
            "analysis": {
                "virality_score": 78,
                "stepps_scores": {
                    "social_currency": 82,
                    "triggers": 76,
                    "emotion": 85,
                    "public": 65,
                    "practical_value": 80,
                    "stories": 78
                },
                "maturity": "emerging",
                "maturity_score": 45,
                "industries": [
                    {"name": "Technology", "impact": 85},
                    {"name": "Manufacturing", "impact": 75},
                    {"name": "Energy", "impact": 92},
                    {"name": "Retail", "impact": 65},
                    {"name": "Finance", "impact": 70}
                ],
                "strategic_implications": [
                    {
                        "area": "Strategic Assessment",
                        "potential": "High",
                        "timeframe": "Short-term (3-6 months)",
                        "response": f"Conduct comprehensive assessment of {trend} impact on organization's value chain"
                    },
                    {
                        "area": "Capability Development",
                        "potential": "Medium",
                        "timeframe": "Medium-term (1-2 years)",
                        "response": f"Build organizational capabilities to leverage {trend} for competitive advantage"
                    },
                    {
                        "area": "Innovation Pipeline",
                        "potential": "High",
                        "timeframe": "Long-term (2-4 years)",
                        "response": f"Integrate {trend} into product development and innovation pipeline"
                    }
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"Error in trend analysis: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }), 500


@enhanced_strategy_bp.route('/framework-selection-guide')
def framework_selection_guide():
    """
    Framework Selection Guide - Interactive tool to help users select the most appropriate
    sustainability reporting framework based on their industry and goals.
    
    This page provides:
    - Industry-specific framework recommendations
    - Interactive selection tool
    - Detailed comparisons between frameworks
    - Case studies of successful implementations
    """
    logger.info("Framework Selection Guide route called")
    
    try:
        # Get navigation context
        nav_context = get_context_for_template()
        
        # Get active_nav from nav_context if available or set it
        if 'active_nav' in nav_context:
            # Remove active_nav from nav_context to avoid duplicate
            nav_context_copy = {k: v for k, v in nav_context.items() if k != 'active_nav'}
        else:
            nav_context_copy = nav_context
            
        # Render the framework selection guide template
        return render_template(
            "strategy/framework_selection_guide.html",
            page_title="Framework Selection Guide",
            active_nav="strategy",
            frameworks=STRATEGY_FRAMEWORKS,
            industry_mappings=INDUSTRY_FRAMEWORK_MAPPING,
            **nav_context_copy
        )
    except Exception as e:
        logger.error(f"Error in framework selection guide: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Redirect to enhanced strategy hub in case of error
        flash("An error occurred loading the Framework Selection Guide. Please try again later.", "error")
        return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))


@enhanced_strategy_bp.route('/api/framework-recommendation', methods=['POST'])
def api_framework_recommendation():
    """API endpoint for getting framework recommendations based on industry and goals"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400
            
        industry = data.get('industry', '')
        goals = data.get('goals', [])
        company_size = data.get('company_size', 'medium')
        region = data.get('region', 'global')
        
        if not industry:
            return jsonify({
                "status": "error",
                "message": "Industry is required"
            }), 400
        
        # Get framework recommendations based on industry
        if industry.lower() in INDUSTRY_FRAMEWORK_MAPPING:
            recommended_frameworks = INDUSTRY_FRAMEWORK_MAPPING[industry.lower()]
        else:
            # Default to global frameworks if industry not found
            recommended_frameworks = ["gri", "sdg"]
        
        # Build framework details
        framework_details = []
        for framework_id in recommended_frameworks:
            if framework_id in STRATEGY_FRAMEWORKS:
                framework = STRATEGY_FRAMEWORKS[framework_id]
                framework_details.append({
                    "id": framework_id,
                    "name": framework["name"],
                    "description": framework["description"],
                    "icon": framework["icon"],
                    "color": framework["color"],
                    "match_score": calculate_match_score(framework_id, industry, goals, company_size, region)
                })
        
        # Sort by match score
        framework_details.sort(key=lambda x: x["match_score"], reverse=True)
        
        return jsonify({
            "status": "success",
            "industry": industry,
            "recommendations": framework_details
        })
    except Exception as e:
        logger.error(f"Error in framework recommendation: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }), 500


def calculate_match_score(framework_id, industry, goals, company_size, region):
    """Calculate match score between framework and company characteristics"""
    base_score = 50
    
    # Industry match bonus
    if industry.lower() in INDUSTRY_FRAMEWORK_MAPPING:
        industry_frameworks = INDUSTRY_FRAMEWORK_MAPPING[industry.lower()]
        if framework_id in industry_frameworks:
            # Higher bonus for frameworks that are primary recommendations for industry
            position = industry_frameworks.index(framework_id)
            base_score += 30 - (position * 5)  # 30 for first, 25 for second, 20 for third
    
    # Goal match bonus
    goal_keywords = {
        "compliance": ["csrd", "gri"],
        "emissions": ["sbti", "tcfd"],
        "reporting": ["gri", "csrd"],
        "financing": ["tcfd", "gri"],
        "stakeholder": ["sdg", "gri"],
        "social": ["sdg", "gri"],
        "environmental": ["sbti", "tcfd", "csrd"]
    }
    
    for goal in goals:
        goal_lower = goal.lower()
        for keyword, frameworks in goal_keywords.items():
            if keyword in goal_lower and framework_id in frameworks:
                base_score += 5
    
    # Company size adjustment
    size_mapping = {
        "small": {"gri": -5, "csrd": -10, "tcfd": -5, "sdg": 5, "sbti": 0},
        "medium": {"gri": 0, "csrd": 0, "tcfd": 0, "sdg": 0, "sbti": 0},
        "large": {"gri": 5, "csrd": 10, "tcfd": 5, "sdg": 0, "sbti": 5}
    }
    
    if company_size in size_mapping and framework_id in size_mapping[company_size]:
        base_score += size_mapping[company_size][framework_id]
    
    # Region adjustment
    region_mapping = {
        "eu": {"csrd": 15, "gri": 5, "tcfd": 5, "sdg": 0, "sbti": 0},
        "us": {"csrd": -5, "gri": 5, "tcfd": 10, "sdg": 0, "sbti": 5},
        "asia": {"csrd": -5, "gri": 5, "tcfd": 0, "sdg": 5, "sbti": 0},
        "global": {"csrd": 0, "gri": 10, "tcfd": 5, "sdg": 10, "sbti": 5}
    }
    
    if region in region_mapping and framework_id in region_mapping[region]:
        base_score += region_mapping[region][framework_id]
    
    # Ensure score is between 0 and 100
    return max(0, min(100, base_score))


# Legacy route redirects - consolidating all strategy routes into enhanced_strategy.py
@enhanced_strategy_bp.route('/strategy-hub')
def strategy_hub_redirect():
    """Redirect from old strategy hub to enhanced strategy hub"""
    logger.info("Legacy strategy hub route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@enhanced_strategy_bp.route('/unified-strategy-hub')
def unified_strategy_hub_redirect():
    """Redirect from unified strategy hub to enhanced strategy hub"""
    logger.info("Unified Strategy Hub route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@enhanced_strategy_bp.route('/ai-first-strategy-hub')
def ai_first_strategy_hub_redirect():
    """Redirect from AI-first strategy hub to enhanced strategy hub"""
    logger.info("AI-First Strategy Hub route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@enhanced_strategy_bp.route('/strategy-modeling-tool')
def strategy_modeling_tool_redirect():
    """Redirect from strategy modeling tool to enhanced strategy hub"""
    logger.info("Strategy Modeling Tool route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@enhanced_strategy_bp.route('/strategy-hub-full')
def strategy_hub_full_redirect():
    """Redirect from full strategy hub to enhanced strategy hub"""
    logger.info("Full Strategy Hub route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@enhanced_strategy_bp.route('/strategy-hub/framework/<framework_id>')
def strategy_framework_redirect(framework_id):
    """Redirect from framework view to framework selection guide"""
    logger.info(f"Strategy Framework route called for {framework_id} - redirecting to Framework Selection Guide")
    return redirect(url_for('enhanced_strategy.framework_selection_guide'))

@enhanced_strategy_bp.route('/strategy-hub/monetization')
def strategy_monetization_redirect():
    """Redirect from monetization page to enhanced strategy hub"""
    logger.info("Strategy Monetization route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@enhanced_strategy_bp.route('/monetization-opportunities')
def monetization_opportunities_redirect():
    """Redirect from monetization opportunities to enhanced strategy hub"""
    logger.info("Monetization Opportunities route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@enhanced_strategy_bp.route('/monetization-strategies')
def monetization_strategies_redirect():
    """Redirect from monetization strategies to enhanced strategy hub"""
    logger.info("Monetization Strategies route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@enhanced_strategy_bp.route('/sustainability-strategies')
def sustainability_strategies_redirect():
    """Redirect from sustainability strategies to enhanced strategy hub"""
    logger.info("Sustainability Strategies route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@enhanced_strategy_bp.route('/strategy-simulation')
def strategy_simulation_redirect():
    """Redirect from strategy simulation to enhanced strategy hub"""
    logger.info("Strategy Simulation route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@enhanced_strategy_bp.route('/strategy-hub/storytelling')
def strategy_hub_storytelling_redirect():
    """Redirect from storytelling page to enhanced strategy hub"""
    logger.info("Strategy Hub Storytelling route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@enhanced_strategy_bp.route('/strategy-hub/documents')
def strategy_hub_documents_redirect():
    """Redirect from documents page to enhanced strategy hub"""
    logger.info("Strategy Hub Documents route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@enhanced_strategy_bp.route('/strategy-hub/document-upload', methods=['GET', 'POST'])
def strategy_hub_document_upload_redirect():
    """Redirect from document upload page to enhanced strategy hub"""
    logger.info("Strategy Hub Document Upload route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@enhanced_strategy_bp.route('/strategy-hub/document/<document_id>')
def strategy_hub_document_view_redirect(document_id):
    """Redirect from document view page to enhanced strategy hub"""
    logger.info(f"Strategy Hub Document View route called for document ID {document_id} - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@enhanced_strategy_bp.route('/strategy-hub/analysis/<file_id>', methods=['GET'])
def strategy_hub_data_analysis_redirect(file_id):
    """Redirect from data analysis page to enhanced strategy hub"""
    logger.info(f"Strategy Hub Data Analysis route called for file ID {file_id} - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@enhanced_strategy_bp.route('/strategy-hub/debug')
def strategy_hub_debug_redirect():
    """Redirect from debug page to enhanced strategy hub"""
    logger.info("Strategy Hub Debug route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

# API routes that should redirect to enhanced strategy API endpoints
@enhanced_strategy_bp.route('/api/strategy/frameworks')
def api_strategy_frameworks_redirect():
    """Redirect from frameworks API to framework recommendation API"""
    logger.info("Strategy Frameworks API route called - redirecting to Framework Recommendation API")
    return redirect(url_for('enhanced_strategy.api_framework_recommendation'))


@enhanced_strategy_bp.route('/api/generate-strategy', methods=['POST'])
def api_generate_strategy():
    """
    API endpoint to generate AI-powered strategy (matching frontend path)
    
    Accepts:
        - companyName: Name of the company
        - industry: Industry of the company
        - focusAreas: List of focus areas (optional)
        - trendInput: Trend analysis information (optional)
        
    Returns:
        JSON with strategy information
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "Please provide company name and industry information."
            }), 400
            
        # Extract required parameters
        company_name = data.get('companyName')
        industry = data.get('industry')
        
        if not company_name or not industry:
            return jsonify({
                "status": "error",
                "message": "Please provide both company name and industry."
            }), 400
            
        # Extract optional parameters
        focus_areas = data.get('focusAreas', '')
        trend_input = data.get('trendInput', '')
        
        # Generate strategy using AI consultant
        result = strategy_ai.generate_ai_strategy(
            company_name=company_name,
            industry=industry,
            focus_areas=focus_areas,
            trend_analysis=trend_input
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error generating AI strategy: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"An error occurred while generating the strategy: {str(e)}"
        }), 500


@enhanced_strategy_bp.route('/api/strategy/generate', methods=['POST'])
def api_strategy_generate():
    """
    API endpoint to generate AI-powered strategy
    
    Accepts:
        - companyName: Name of the company
        - industry: Industry of the company
        - focusAreas: List of focus areas (optional)
        - trendInput: Trend analysis information (optional)
        
    Returns:
        JSON with strategy information
    """
    return api_generate_strategy()
    

@enhanced_strategy_bp.route('/api/strategy/recommendations', methods=['POST'])
def api_strategy_recommendations():
    """
    API endpoint to get recommendations based on an existing strategy
    
    Accepts:
        - company_name: Name of the company
        - industry: Industry of the company
        - strategy_points: List of existing strategy points
        
    Returns:
        JSON with recommended enhancements and improvements
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400
            
        # Extract parameters
        company_name = data.get('company_name')
        industry = data.get('industry')
        strategy_points = data.get('strategy_points', [])
        
        if not company_name or not industry:
            return jsonify({
                "status": "error",
                "message": "Company name and industry are required"
            }), 400
            
        if not strategy_points or not isinstance(strategy_points, list):
            return jsonify({
                "status": "error",
                "message": "Strategy points must be provided as a list"
            }), 400
            
        # Generate recommendations using AI consultant
        # This would normally call a method on the strategy_ai object
        # For now, we'll provide a simple response structure
        
        recommendations = []
        for i, point in enumerate(strategy_points):
            recommendations.append({
                "original_point": point,
                "enhanced_point": f"Enhanced: {point}",
                "rationale": f"Enhancement recommendation based on latest sustainability trends and best practices in {industry}.",
                "impact_score": round(4.0 + (i % 3) * 2.0, 1)  # Simulate varying impact scores
            })
            
        return jsonify({
            "status": "success",
            "company_name": company_name,
            "industry": industry,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating strategy recommendations: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }), 500


def register_blueprint(app):
    """Register the enhanced strategy blueprint with the given app"""
    app.register_blueprint(enhanced_strategy_bp)
    logger.info("Enhanced Strategy Hub routes registered")