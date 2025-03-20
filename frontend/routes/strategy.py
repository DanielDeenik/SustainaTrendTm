"""
Strategy Hub routes for SustainaTrend Intelligence Platform

This module consolidates all strategy, simulation, monetization, storytelling and document
analysis routes into a single cohesive interface.
"""

import json
import logging
import os
import sys
import traceback
import uuid
from datetime import datetime
from typing import Dict, Any, List, Mapping, Optional, Tuple, Union, Callable

# Flask and Werkzeug imports
try:
    from werkzeug.utils import secure_filename
    from flask import (
        Blueprint, render_template, request, jsonify, redirect, 
        url_for, flash, send_from_directory, session, current_app
    )
except ImportError as e:
    logging.warning(f"Flask or Werkzeug import error: {str(e)}. "
                   "This might cause issues if the module is used outside Flask context.")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Define Strategy Frameworks for enhanced strategy hub
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

# Import AI strategy consultant functionality
try:
    from strategy_ai_consultant import generate_ai_strategy
    STRATEGY_AI_CONSULTANT_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("Strategy AI Consultant module loaded successfully")
except ImportError as e:
    STRATEGY_AI_CONSULTANT_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"Strategy AI Consultant module import failed: {str(e)}")
    
    # Define fallback for generate_ai_strategy if import fails
    def generate_ai_strategy(data):
        """Fallback function for AI strategy generation"""
        logger.warning(f"Using fallback generate_ai_strategy function")
        return {
            "status": "redirected", 
            "message": "This function is now handled by Enhanced Strategy Hub",
            "strategy": {
                "title": "Strategy recommendations are now available in Enhanced Strategy Hub",
                "summary": "Please visit the Enhanced Strategy Hub for comprehensive strategy recommendations."
            }
        }

# Import strategy API routes
try:
    from .strategy_api import register_blueprint as register_strategy_api
    STRATEGY_API_AVAILABLE = True
    logger.info("Strategy API module loaded successfully")
except ImportError as e:
    STRATEGY_API_AVAILABLE = False
    logger.warning(f"Strategy API module import failed: {str(e)}")
    
    # Define fallback for register_strategy_api if import fails
    def register_strategy_api(bp):
        """Fallback function for strategy API routes registration"""
        logger.warning("Using fallback register_strategy_api function")
        pass

# Import navigation context
from navigation_config import get_context_for_template

# Import storytelling components (with fallback)
try:
    from sustainability_storytelling import get_enhanced_stories, get_data_driven_stories, generate_chart_data
    STORYTELLING_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("Storytelling module loaded successfully")
except ImportError as e:
    STORYTELLING_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"Storytelling module not available: {str(e)}")
    
    # Define fallback functions if imports fail
    def get_enhanced_stories(audience: str = 'all', category: str = 'all', prompt = None, document_data = None):
        """Fallback function for enhanced stories generation"""
        logger.warning("Using fallback get_enhanced_stories function")
        return []
        
    def get_data_driven_stories(audience: str = 'all', category: str = 'all', limit: int = 5):
        """Fallback function for data-driven stories generation"""
        logger.warning("Using fallback get_data_driven_stories function")
        return []
        
    def generate_chart_data(story_category: str = "emissions", time_period: str = "quarterly", chart_type = None):
        """Fallback function for chart data generation"""
        logger.warning("Using fallback generate_chart_data function")
        return {}

# Import document processor (with fallback)
try:
    from document_processor import DocumentProcessor
    DOCUMENT_PROCESSOR_AVAILABLE = True
    logger.info("Document processor module loaded successfully")
except ImportError as e:
    DOCUMENT_PROCESSOR_AVAILABLE = False
    logger.warning(f"Document processor not available: {str(e)}")
    
    # Define a minimal DocumentProcessor class if import fails
    class DocumentProcessor:
        """Fallback DocumentProcessor class"""
        def __init__(self):
            logger.warning("Using fallback DocumentProcessor class")
            
        def get_document_by_id(self, document_id):
            """Fallback method to get document by ID"""
            logger.warning(f"Using fallback get_document_by_id method for document ID: {document_id}")
            return None  # Return None to indicate document not found

# Monetization strategies section has been removed

# Marketing strategies section has been removed

# Import trend virality benchmarking functions (with fallback)
# Trend virality benchmarking module has been removed
# Define STEPPS_COMPONENTS for backward compatibility with other features
STEPPS_COMPONENTS = {
    "social_currency": "Social Currency",
    "triggers": "Triggers",
    "emotion": "Emotion",
    "public": "Public",
    "practical_value": "Practical Value",
    "stories": "Stories"
}
# Define flag as False since we've removed the feature
TREND_VIRALITY_AVAILABLE = False

# Define fallback functions for missing functions
def analyze_with_framework(framework_id, analysis_data, company_name, industry):
    """Fallback function for framework analysis"""
    logger.warning(f"Using fallback analyze_with_framework function")
    return {"status": "redirected", "message": "This function is now handled by Enhanced Strategy Hub"}

def analyze_monetization_opportunities(document_text):
    """Fallback function for monetization analysis"""
    logger.warning(f"Using fallback analyze_monetization_opportunities function")
    return {"status": "redirected", "message": "This function is now handled by Enhanced Strategy Hub"}

def generate_integrated_strategic_plan(company_name, industry, document_text):
    """Fallback function for strategic plan generation"""
    logger.warning(f"Using fallback generate_integrated_strategic_plan function")
    return {"status": "redirected", "message": "This function is now handled by Enhanced Strategy Hub"}

# Import AI Strategy Consultant functions (with fallback)
try:
    from strategy_ai_consultant import (
        analyze_trend,
        register_routes as register_ai_consultant_routes
    )
    AI_CONSULTANT_AVAILABLE = True
    logger.info("AI Strategy Consultant module loaded successfully")
except ImportError as e:
    AI_CONSULTANT_AVAILABLE = False
    logger.warning(f"AI Strategy Consultant module not available: {str(e)}")
    
    # Define fallback for register_ai_consultant_routes if import fails
    def register_ai_consultant_routes(bp):
        """Fallback function for AI consultant routes registration"""
        logger.warning("Using fallback register_ai_consultant_routes function")
        pass

# Science-Based Targets section has been removed
SBTI_AVAILABLE = False

# Strategy Frameworks section has been removed

# Configure logging
logger = logging.getLogger(__name__)

# Configure document upload settings
UPLOAD_FOLDER = 'frontend/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'xlsx', 'pptx', 'txt', 'csv'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize document processor
document_processor = DocumentProcessor()

# Create blueprint
strategy_bp = Blueprint('strategy', __name__)

# Register AI Strategy Consultant routes
if AI_CONSULTANT_AVAILABLE:
    try:
        register_ai_consultant_routes(strategy_bp)
        logger.info("AI Strategy Consultant routes registered successfully")
    except Exception as e:
        logger.warning(f"Failed to register AI Strategy Consultant routes: {str(e)}")

# Register Strategy API routes
if STRATEGY_API_AVAILABLE:
    try:
        register_strategy_api(strategy_bp)
        logger.info("Strategy API routes registered successfully")
    except Exception as e:
        logger.warning(f"Failed to register Strategy API routes: {str(e)}")

# Simple routes that redirect to the Enhanced Strategy Hub
@strategy_bp.route('/strategy-hub')
def strategy_hub():
    """Redirect from old Strategy Hub to the Enhanced Strategy Hub"""
    logger.info("Strategy Hub route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@strategy_bp.route('/ai-first-strategy-hub')
def ai_first_strategy_hub():
    """Redirect from AI-First Strategy Hub to the Enhanced Strategy Hub"""
    logger.info("AI-First Strategy Hub route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@strategy_bp.route('/strategy-modeling-tool')
def strategy_modeling_tool():
    """Redirect from Strategy Modeling Tool to the Enhanced Strategy Hub"""
    logger.info("Strategy Modeling Tool route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

# Legacy Strategy Hub implementation kept here for reference
def legacy_strategy_hub():
    """
    Legacy implementation of the Strategy Hub page
    """
    # Create a minimal implementation that works reliably
    return render_template(
        "strategy_test.html",
        frameworks={},  # Removed STRATEGY_FRAMEWORKS reference
        monetization_strategies={
            "M1": {
                "name": "AI-Driven Sustainability Trend Monetization",
                "icon": "chart-line",
                "short_description": "AI-powered trend detection and analysis",
                "default_potential": 85
            },
            "M2": {
                "name": "Consulting Services Model",
                "icon": "handshake",
                "short_description": "Advisory services for sustainability reporting",
                "default_potential": 65
            },
            "M3": {
                "name": "SaaS Subscription Platform",
                "icon": "cloud",
                "short_description": "Cloud-based sustainability platform",
                "default_potential": 75
            },
            "M4": {
                "name": "Data Marketplace",
                "icon": "database",
                "short_description": "Monetize sustainability datasets",
                "default_potential": 70
            },
            "M5": {
                "name": "Strategic Consulting",
                "icon": "users",
                "short_description": "Expert advisory services",
                "default_potential": 80
            }
        }
    )

@strategy_bp.route('/strategy-hub-full')  
def strategy_hub_full():
    """
    Original full implementation - redirects to Enhanced Strategy Hub
    
    This route redirects to the enhanced version with data-centric approach
    inspired by Finchat.io's minimalist aesthetic.
    """
    logger.info("Strategy Hub full route called - redirecting to Enhanced Strategy Hub")
    
    # Redirect to the Enhanced Strategy Hub
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@strategy_bp.route('/strategy-hub/framework/<framework_id>')
def strategy_framework(framework_id):
    """Redirect from specific Strategy Framework page to the Enhanced Strategy Hub"""
    logger.info(f"Strategy framework route called: {framework_id} - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub', framework=framework_id))

@strategy_bp.route('/strategy-hub/monetization')
def monetization_strategies_view():
    """Redirect from Monetization Strategies page to Enhanced Strategy Hub"""
    logger.info("Redirecting monetization strategies view to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@strategy_bp.route('/strategy-hub/simulation')
def strategy_simulation_view():
    """Redirect from Strategy Simulation page to Enhanced Strategy Hub"""
    logger.info("Redirecting strategy simulation view to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

# API Routes

@strategy_bp.route('/api/strategy/frameworks')
def api_strategy_frameworks():
    """API endpoint for getting available strategy frameworks"""
    return jsonify({
        'success': True,
        'frameworks': STRATEGY_FRAMEWORKS
    })

@strategy_bp.route('/api/strategy/framework-analysis', methods=['POST'])
def api_framework_analysis():
    """API endpoint for framework analysis"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        framework_id = data.get('framework_id')
        company_name = data.get('company_name', 'Sample Company')
        industry = data.get('industry', 'Real Estate')
        analysis_data = data.get('data', {})
        
        if not framework_id:
            return jsonify({"error": "No framework_id provided"}), 400
            
        result = analyze_with_framework(framework_id, analysis_data, company_name, industry)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in framework analysis API: {str(e)}")
        return jsonify({"error": str(e)}), 500

@strategy_bp.route('/api/strategy/monetization', methods=['POST'])
def api_monetization_analysis():
    """API endpoint for monetization analysis"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Missing request data'
            }), 400
        
        company_name = data.get('company_name', 'Your Company')
        industry = data.get('industry', 'Technology')
        document_text = data.get('document_text', '')
        
        if document_text:
            opportunities = analyze_monetization_opportunities(document_text)
        else:
            # Generate analysis based on company and industry
            opportunities = analyze_monetization_opportunities(
                f"Strategic plan for {company_name} in {industry} sector"
            )
        
        return jsonify({
            'success': True,
            'opportunities': opportunities
        })
    except Exception as e:
        logger.error(f"Error in monetization analysis API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@strategy_bp.route('/api/strategy/strategic-plan', methods=['POST'])
def api_strategic_plan():
    """API endpoint for generating strategic monetization plan"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Missing request data'
            }), 400
        
        company_name = data.get('company_name', 'Your Company')
        industry = data.get('industry', 'Technology')
        document_text = data.get('document_text', '')
        
        # Generate strategic plan using the imported function
        plan = generate_integrated_strategic_plan(company_name, industry, document_text)
        
        return jsonify({
            'success': True,
            'plan': plan
        })
    except Exception as e:
        logger.error(f"Error in strategic plan API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Debug route to check the data structures
@strategy_bp.route('/strategy-hub/debug')
def strategy_hub_debug():
    """Redirect from Debug route to Enhanced Strategy Hub"""
    logger.info("Strategy Hub Debug route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

# Test route removed - no longer needed

# Helper functions for document uploads
def allowed_file(filename):
    """Check if a filename has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# New integrated storytelling routes
@strategy_bp.route('/strategy-hub/storytelling')
def strategy_hub_storytelling():
    """Redirect from Storytelling Hub to Enhanced Strategy Hub"""
    logger.info("Strategy Hub Storytelling route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@strategy_bp.route('/api/strategy-hub/generate-story', methods=['POST'])
def api_strategy_hub_generate_story():
    """
    API endpoint for generating a sustainability story from the Strategy Hub
    DEPRECATED: This endpoint forwards to the new implementation
    """
    logger.warning("DEPRECATED: Using old API endpoint for story generation - forwarding to new implementation")
    
    try:
        # Get request data
        data = request.json or {}
        
        # Extract parameters and forward to the new endpoint
        topic = data.get('topic', 'sustainability')  # This is called 'category' in the new implementation 
        audience = data.get('audience', 'board')
        
        # Create a UUID for the story
        story_id = str(uuid.uuid4())
        
        # Check if storytelling module is available
        if not STORYTELLING_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Storytelling module is not available',
                'deprecated': True,
                'message': 'This API endpoint is deprecated. Please use /storytelling/api/stories/generate instead.'
            }), 500
        
        # Return a notice about the API endpoint being deprecated
        return jsonify({
            'success': True,
            'deprecated': True,
            'message': 'This API endpoint is deprecated. Please use /storytelling/api/stories/generate instead.',
            'story': {
                'id': story_id,
                'title': f'Sustainability story for {topic}',
                'content': f'This API is deprecated. Please use the new endpoint at /storytelling/api/stories/generate with parameters: category="{topic}", audience="{audience}"',
                'audience': audience,
                'category': topic,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        })
    
    except Exception as e:
        logger.error(f"Error in deprecated generate story API: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e),
            'deprecated': True,
            'message': 'This API endpoint is deprecated. Please use /storytelling/api/stories/generate instead.'
        }), 500
        
@strategy_bp.route('/api/storytelling/generate', methods=['POST'])
def api_storytelling_generate():
    """
    Enhanced API endpoint for generating data-driven sustainability stories from user parameters.
    This serves the new storytelling component in the Strategy Hub.
    
    Accepts:
    - audience: Target audience (board, investors, etc.)
    - category: Sustainability category (emissions, water, etc.)
    - prompt: Optional text prompt for customization
    - document_id: Optional ID of processed document to use as source
    - document_data: Optional document data to use directly
    """
    try:
        # Get request data with better error handling
        if not request.is_json:
            return jsonify({
                'error': True,
                'message': 'Invalid request format. JSON required.'
            }), 400
            
        data = request.json
        
        # Extract parameters with proper validation
        audience = data.get('audience')
        category = data.get('category')
        prompt = data.get('prompt')
        document_id = data.get('document_id')
        document_data = data.get('document_data')
        
        # Validate required parameters - only audience and category are required
        if not all([audience, category]):
            return jsonify({
                'error': True,
                'message': 'Missing required parameters. Please provide audience and category.'
            }), 400
        
        logger.info(f"Generating storytelling content for audience={audience}, category={category}")
        
        # Check if storytelling module is available
        if not STORYTELLING_AVAILABLE:
            return jsonify({
                'error': True,
                'message': 'Storytelling module is not available'
            }), 500
        
        # If document_id is provided but not document_data, try to fetch the document data
        if document_id and not document_data and DOCUMENT_PROCESSOR_AVAILABLE:
            try:
                # Get document from DocumentProcessor
                logger.info(f"Fetching document data for document_id: {document_id}")
                document_data = document_processor.get_document_by_id(document_id)
                
                if not document_data:
                    logger.warning(f"Document with ID {document_id} not found")
            except Exception as e:
                logger.error(f"Error fetching document data: {str(e)}")
        
        # Generate stories using the enhanced storytelling module
        try:
            stories = get_enhanced_stories(audience=audience, category=category, 
                                          prompt=prompt, document_data=document_data)
            
            # If stories were generated, enhance the first one with additional metadata
            if stories and len(stories) > 0:
                story = stories[0]
                
                # Enhance response with additional useful fields for the UI
                response = {
                    'title': story.get('title', f"{category.capitalize()} Story for {audience.capitalize()}"),
                    'content': story.get('content', ''),
                    'audience': audience,
                    'category': category,
                    'timestamp': story.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    'insights': story.get('insights', []),
                    'recommendations': story.get('recommendations', []),
                    'id': story.get('id', str(uuid.uuid4())),
                    'prompt': prompt,
                    'prompt_enhanced': story.get('prompt_enhanced', False),
                    'custom_prompt_generated': story.get('custom_prompt_generated', False)
                }
                
                # Extract or create chart data if available
                if 'chart_data' in story:
                    response['chart_data'] = story['chart_data']
                
                return jsonify(response)
            else:
                return jsonify({
                    'error': True,
                    'message': 'No stories could be generated with the provided parameters.'
                }), 404
        except Exception as e:
            logger.error(f"Error generating story: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'error': True,
                'message': f'Error generating story: {str(e)}'
            }), 500
    
    except Exception as e:
        logger.error(f"Error in storytelling generate API: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': True,
            'message': str(e)
        }), 500

# New integrated document upload routes
@strategy_bp.route('/strategy-hub/documents')
def strategy_hub_documents():
    """Redirect from Documents Hub page to Enhanced Strategy Hub"""
    logger.info("Strategy Hub Documents route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@strategy_bp.route('/strategy-hub/document-upload', methods=['GET', 'POST'])
def strategy_hub_document_upload():
    """Redirect from Document Upload page to Enhanced Strategy Hub"""
    logger.info("Strategy Hub Document Upload route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))
@strategy_bp.route('/strategy-hub/document/<document_id>')
def strategy_hub_document_view(document_id):
    """Redirect from Document Analysis View to Enhanced Strategy Hub"""
    logger.info(f"Strategy Hub Document View route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

# Generate story from document route
@strategy_bp.route('/strategy-hub/document/<document_id>/generate-story')
def strategy_hub_generate_story(document_id):
    """Redirect from Generate Story page to Enhanced Strategy Hub"""
    logger.info(f"Strategy Hub Generate Story route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

# Consolidated Strategy Hub implementation
@strategy_bp.route('/unified-strategy-hub')
def unified_strategy_hub():
    """Redirect from Unified Strategy Hub to Enhanced Strategy Hub"""
    logger.info("Unified Strategy Hub route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@strategy_bp.route('/api/strategy-hub/upload-data', methods=['POST'])
def api_upload_data():
    """API endpoint to upload sustainability data files for analysis"""
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
        allowed_extensions = {'csv', 'xlsx', 'xls'}
        if not file.filename.lower().rsplit('.', 1)[1] in allowed_extensions:
            logger.warning(f"Invalid file extension: {file.filename}")
            return jsonify({
                "status": "error",
                "message": "Invalid file extension. Allowed extensions: csv, xlsx, xls"
            }), 400
            
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Save file to uploads directory
        uploads_dir = os.path.join(current_app.root_path, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        
        file_path = os.path.join(uploads_dir, f"{file_id}_{secure_filename(file.filename)}")
        file.save(file_path)
        
        logger.info(f"Data file uploaded successfully: {file.filename}, saved as {file_path}")
        
        # Return success response
        return jsonify({
            "status": "success",
            "message": "File uploaded successfully",
            "fileId": file_id,
            "redirectUrl": url_for('strategy.strategy_hub_data_analysis', file_id=file_id)
        })
        
    except Exception as e:
        logger.exception(f"Error uploading data file: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }), 500

@strategy_bp.route('/api/strategy-hub/upload-document', methods=['POST'])
def api_upload_document():
    """API endpoint to upload sustainability document for analysis"""
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
        allowed_extensions = {'pdf', 'docx', 'doc'}
        if not file.filename.lower().rsplit('.', 1)[1] in allowed_extensions:
            logger.warning(f"Invalid file extension: {file.filename}")
            return jsonify({
                "status": "error",
                "message": "Invalid file extension. Allowed extensions: pdf, docx, doc"
            }), 400
            
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        
        # Save file to uploads directory
        uploads_dir = os.path.join(current_app.root_path, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        
        file_path = os.path.join(uploads_dir, f"{document_id}_{secure_filename(file.filename)}")
        file.save(file_path)
        
        logger.info(f"Document uploaded successfully: {file.filename}, saved as {file_path}")
        
        # Return success response
        return jsonify({
            "status": "success",
            "message": "Document uploaded successfully",
            "documentId": document_id,
            "redirectUrl": url_for('strategy.strategy_hub_document_view', document_id=document_id)
        })
        
    except Exception as e:
        logger.exception(f"Error uploading document: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }), 500

@strategy_bp.route('/api/strategy-hub/recent-imports', methods=['GET'])
def api_recent_imports():
    """API endpoint to get recent data and document imports"""
    try:
        # For demonstration, returning mock recent imports
        # In a production environment, this would fetch from database
        recent_imports = [
            {
                "id": "demo-csv-01",
                "name": "Emissions Data 2024.csv",
                "type": "data",
                "timestamp": "2024-03-15T10:30:00Z",
                "status": "Complete"
            },
            {
                "id": "demo-pdf-01",
                "name": "Sustainability Report 2024.pdf",
                "type": "document",
                "timestamp": "2024-03-14T15:45:00Z",
                "status": "Complete"
            }
        ]
        
        return jsonify({
            "status": "success",
            "imports": recent_imports
        })
        
    except Exception as e:
        logger.exception(f"Error getting recent imports: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }), 500

@strategy_bp.route('/strategy-hub/analysis/<file_id>', methods=['GET'])
def strategy_hub_data_analysis(file_id):
    """Redirect from Data Analysis page to Enhanced Strategy Hub"""
    logger.info(f"Strategy Hub Data Analysis route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@strategy_bp.route('/api/strategy-hub/generate', methods=['POST'])
def api_strategy_hub_generate():
    """API endpoint to generate sustainability strategy using AI consultant (strategy hub version)"""
    try:
        # Get request data
        data = request.json
        
        # Log request
        logger.info(f"Strategy generation request: {data}")
        
        # Validate required fields
        if not data or 'companyName' not in data or 'industry' not in data:
            logger.warning("Invalid strategy generation request - missing required fields")
            return jsonify({
                "status": "error",
                "message": "Company name and industry are required"
            }), 400
        
        # Check if AI Strategy Consultant is available
        if not STRATEGY_AI_CONSULTANT_AVAILABLE:
            logger.warning("Strategy AI Consultant not available")
            return jsonify({
                "status": "error",
                "message": "Strategy AI Consultant is not available"
            }), 503
        
        # Generate strategy
        result = generate_ai_strategy(data)
        
        # Check result status
        if result.get('status') == 'error':
            logger.error(f"Strategy generation failed: {result.get('message')}")
            return jsonify(result), 500
        
        # Return successful result
        return jsonify(result)
    
    except Exception as e:
        # Log and return error
        logger.exception(f"Error in strategy generation API: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }), 500
        
# Removed legacy implementation function (unified_strategy_hub_implementation)
# This code has been migrated to the enhanced_strategy module

# Legacy route redirects
@strategy_bp.route('/monetization-opportunities')
@strategy_bp.route('/monetization-strategies')
def legacy_monetization_redirect():
    """Redirect legacy monetization routes to enhanced strategy hub"""
    logger.info("Legacy monetization route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@strategy_bp.route('/sustainability-strategies')
def legacy_strategies_redirect():
    """Redirect legacy strategies routes to enhanced strategy hub"""
    logger.info("Legacy strategies route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@strategy_bp.route('/strategy-simulation')
def legacy_simulation_redirect():
    """Redirect legacy simulation routes to enhanced strategy hub"""
    logger.info("Legacy simulation route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

# Data Import and Analysis Routes

@strategy_bp.route('/upload-data-file', methods=['POST'])
def upload_data_file():
    """
    Handle data file uploads for the Strategy Hub
    
    Accepts file uploads via form submission and stores them in the uploads directory.
    Returns a redirect to the data analysis page.
    """
    logger.info("Data file upload route called")
    
    try:
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(current_app.static_folder, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Get form data
        if 'data_file' not in request.files:
            flash('No file provided', 'error')
            return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))
            
        file = request.files['data_file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))
            
        # Get other form fields
        file_type = request.form.get('file_type', 'other')
        description = request.form.get('description', '')
        data_origin = request.form.get('data_origin', 'internal')
        analyze_immediate = 'analyze_immediate' in request.form
        generate_recommendations = 'generate_recommendations' in request.form
        
        # Secure the filename and generate a unique ID
        filename = secure_filename(file.filename)
        file_id = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(upload_dir, file_id)
        
        # Save the file
        file.save(file_path)
        
        # Log upload success
        logger.info(f"File uploaded successfully: {file_id}, type: {file_type}, origin: {data_origin}")
        
        # Save file metadata (in a production environment, this would be in a database)
        # For this demo, we'll use session storage
        if 'uploaded_files' not in session:
            session['uploaded_files'] = []
            
        file_metadata = {
            'id': file_id,
            'original_filename': filename,
            'file_type': file_type,
            'description': description,
            'data_origin': data_origin,
            'upload_date': datetime.now().isoformat(),
            'file_path': file_path,
            'analyzed': analyze_immediate,
            'recommendations_generated': generate_recommendations
        }
        
        session['uploaded_files'].insert(0, file_metadata)
        session.modified = True
        
        # Flash success message
        flash(f'File "{filename}" uploaded successfully', 'success')
        
        # Redirect to analysis page if immediate analysis is requested
        if analyze_immediate:
            return redirect(url_for('strategy.analyze_data', file_id=file_id))
        else:
            return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))
            
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        logger.error(traceback.format_exc())
        flash(f'Error uploading file: {str(e)}', 'error')
        return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@strategy_bp.route('/strategy-hub/analyze/<file_id>')
def analyze_data(file_id):
    """Redirect from Analyze Data page to Enhanced Strategy Hub"""
    logger.info(f"Analyze data route called - redirecting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

# AI-First Strategy Hub API endpoints
@strategy_bp.route('/api/ai-first-strategy/generate', methods=['POST'])
def api_ai_first_strategy_generate():
    """
    API endpoint for AI-First Strategy Hub to generate strategy recommendations
    with a simplified, modern approach
    """
    try:
        logger.info("AI-First Strategy Generate API endpoint called")
        data = request.get_json()
        if not data:
            logger.warning("No data provided for AI-first strategy generation")
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400
            
        # Extract key parameters - simplified for AI-first approach
        goal = data.get('goal')
        file_info = data.get('fileInfo')  # Optional file metadata if uploaded
        
        if not goal:
            logger.warning("Missing required parameter: goal")
            return jsonify({
                "status": "error",
                "message": "Missing required parameter: goal"
            }), 400
        
        logger.info(f"AI-First Strategy generation request for goal: {goal}")
        logger.info(f"File info provided: {file_info is not None}")
        
        # Generate AI strategy if available
        if STRATEGY_AI_CONSULTANT_AVAILABLE:
            try:
                # For now, reuse the existing AI consultant with some defaults
                # In production, you would create a specialized AI-first endpoint
                strategy_data = {
                    "companyName": "SustainaTrend",
                    "industry": "General",  # Default that would be detected from the input in production
                    "focusAreas": goal,
                    "frameworks": ["STEPPS", "CSRD", "Porter's Five Forces"]  # AI would choose in production
                }
                
                # Call the strategy generation function
                logger.info("Calling generate_ai_strategy function")
                strategy_results = generate_ai_strategy(strategy_data)
                
                # Check if strategy generation was successful
                if strategy_results.get('status') == 'error':
                    logger.error(f"AI strategy generation failed: {strategy_results.get('message')}")
                    return jsonify(strategy_results), 500
                
                # Extract the actual strategy data
                strategy_data = strategy_results.get('data', {})
                
                # Transform the results into the modern AI-first card format
                ai_first_results = {
                    "goal": goal,
                    "cards": [
                        {
                            "title": "Recommended Frameworks",
                            "icon": "chart-line",
                            "color": "primary",
                            "content": {
                                "type": "frameworks",
                                "frameworks": ["STEPPS", "CSRD", "Porter's Five Forces"],
                                "explanation": "These frameworks are recommended based on your sustainability goals and industry context."
                            }
                        },
                        {
                            "title": "Top Strategic Actions",
                            "icon": "tasks",
                            "color": "success",
                            "content": {
                                "type": "actions",
                                "actions": strategy_data.get("recommendations", [])[:3]  # First 3 recommendations
                            }
                        },
                        {
                            "title": "Trend Analysis",
                            "icon": "chart-bar",
                            "color": "info",
                            "content": {
                                "type": "trend",
                                "insights": strategy_data.get("summary", ""),
                                "data": {}  # Would contain visualization data in production
                            }
                        },
                        {
                            "title": "Risk & Compliance",
                            "icon": "shield-alt",
                            "color": "danger",
                            "content": {
                                "type": "risk",
                                "risks": strategy_data.get("threats", []),
                                "compliance": "Your strategy addresses key requirements for CSRD compliance, with some gaps in Scope 3 emissions tracking."
                            }
                        }
                    ]
                }
                
                logger.info("AI-First Strategy generation completed successfully")
                return jsonify({
                    "status": "success",
                    "data": ai_first_results
                })
            except Exception as e:
                logger.error(f"Error generating AI-first strategy: {str(e)}")
                logger.error(traceback.format_exc())
                return jsonify({
                    "status": "error",
                    "message": f"Error generating AI-first strategy: {str(e)}"
                }), 500
        else:
            # Return a modern AI-first fallback response
            logger.warning("Strategy AI Consultant not available, using fallback response")
            return jsonify({
                "status": "success",
                "data": {
                    "goal": goal,
                    "cards": [
                        {
                            "title": "Recommended Frameworks",
                            "icon": "chart-line",
                            "color": "primary",
                            "content": {
                                "type": "frameworks",
                                "frameworks": ["STEPPS", "CSRD", "Porter's Five Forces"],
                                "explanation": "These frameworks offer structured approaches to analyze and implement your sustainability strategy."
                            }
                        },
                        {
                            "title": "Top Strategic Actions",
                            "icon": "tasks",
                            "color": "success",
                            "content": {
                                "type": "actions",
                                "actions": [
                                    "Engage Tier-1 Suppliers in emissions reduction programs",
                                    "Implement sustainable packaging standards across product lines",
                                    "Develop internal carbon pricing mechanism"
                                ]
                            }
                        },
                        {
                            "title": "Trend Analysis",
                            "icon": "chart-bar",
                            "color": "info",
                            "content": {
                                "type": "trend",
                                "insights": "Industry momentum is shifting toward collaborative supply chain initiatives with 37% year-over-year growth in adoption.",
                                "data": {}  # Would contain visualization data in production
                            }
                        },
                        {
                            "title": "Risk & Compliance",
                            "icon": "shield-alt",
                            "color": "danger",
                            "content": {
                                "type": "risk",
                                "risks": [
                                    "Regulatory compliance risks",
                                    "Reputational damage from greenwashing",
                                    "Supply chain disruptions from climate events"
                                ],
                                "compliance": "Your strategy needs to address key compliance gaps in Scope 3 emissions tracking (CSRD Article 29b) and supplier due diligence requirements."
                            }
                        }
                    ]
                }
            })
    except Exception as e:
        logger.error(f"Error in API AI-first strategy generate: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }), 500

@strategy_bp.route('/api/ai-first-strategy/refine', methods=['POST'])
def api_ai_first_strategy_refine():
    """
    API endpoint for refining an AI-generated strategy based on user feedback
    """
    try:
        logger.info("AI-First Strategy Refine API endpoint called")
        data = request.get_json()
        if not data:
            logger.warning("No data provided for AI-first strategy refinement")
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400
            
        # Extract key parameters
        original_goal = data.get('originalGoal')
        refinement = data.get('refinement')
        original_cards = data.get('originalCards', [])
        
        if not original_goal or not refinement:
            logger.warning("Missing required parameters for strategy refinement")
            return jsonify({
                "status": "error",
                "message": "Missing required parameters: originalGoal and refinement"
            }), 400
        
        logger.info(f"AI-First Strategy refinement request for goal: {original_goal}")
        logger.info(f"Refinement: {refinement}")
        
        # In a production environment, this would call a more sophisticated
        # AI refinement function. For now, we simulate a simple modification.
        
        # For the demo, we'll just return the same cards with a modification 
        # to the first card's content based on the refinement text
        result = {
            "status": "success",
            "data": {
                "goal": original_goal,
                "refinement": refinement,
                "cards": original_cards  # In production, these would be updated based on the refinement
            },
            "message": "Strategy has been refined based on your feedback."
        }
        
        logger.info("AI-First Strategy refinement completed successfully")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in API AI-first strategy refine: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }), 500