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
from datetime import datetime
from typing import Dict, Any, List, Optional
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session

# Import common utilities and constants
from frontend.utils.template_utils import get_context_for_template
from frontend.strategy_ai_consultant import STRATEGY_AI_CONSULTANT_AVAILABLE
from frontend.routes.strategy import STRATEGY_FRAMEWORKS

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
            **nav_context
        )
        
    except Exception as e:
        logger.error(f"Error in enhanced strategy hub: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Redirect to the original strategy hub in case of error
        flash("An error occurred loading the Enhanced Strategy Hub. Please try again later.", "error")
        return redirect(url_for('strategy.unified_strategy_hub'))


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
            "analysis_url": url_for('strategy.strategy_hub_document_view', document_id=file_id)
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
        
        # Render the framework selection guide template
        return render_template(
            "strategy/framework_selection_guide.html",
            page_title="Framework Selection Guide",
            active_nav="strategy",
            frameworks=STRATEGY_FRAMEWORKS,
            industry_mappings=INDUSTRY_FRAMEWORK_MAPPING,
            **nav_context
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


def register_blueprint(app):
    """Register the enhanced strategy blueprint with the given app"""
    app.register_blueprint(enhanced_strategy_bp)
    logger.info("Enhanced Strategy Hub routes registered")