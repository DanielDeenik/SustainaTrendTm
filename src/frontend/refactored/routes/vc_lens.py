"""
VC-Lens™ Routes for SustainaTrend™ Platform
Provides AI-powered investor lens with automated fund-fit analysis and startup impact summary
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app
import os
import json
import uuid
from datetime import datetime, timedelta
import random
from werkzeug.utils import secure_filename
import logging

# Import MongoDB service
from ..services.mongodb_service import MongoDBService, get_database, verify_connection
mongodb_service = MongoDBService()

# Import Gemini/Google AI functionality if available
try:
    from ..utils.gemini_search import GeminiSearchController
    gemini_controller = GeminiSearchController()
    gemini_available = True
except ImportError:
    gemini_available = False
    # Define a placeholder GeminiSearchController
    class GeminiSearchController:
        def __init__(self):
            pass
    gemini_controller = None

# Import VC Lens Service
try:
    from src.backend.services.vc_lens_service import VCLensService
    vc_lens_service = VCLensService()
except ImportError:
    # Create a simple mock if the service is not available
    class VCLensService:
        def __init__(self):
            pass
        
        def process_document(self, document_path, metadata=None):
            return {"success": True, "doc_id": str(uuid.uuid4()), "chunks_processed": 1}
        
        def search_similar(self, query, limit=5):
            return []
    vc_lens_service = VCLensService()

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
vc_lens_bp = Blueprint('vc_lens', __name__, url_prefix='/vc-lens')

# Helper functions
def get_metrics():
    """Get sustainability metrics from MongoDB."""
    try:
        db = get_database()
        metrics = list(db.sustainability_metrics.find())
        return metrics
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        return []

def get_metrics_by_category(category):
    """Get sustainability metrics by category from MongoDB."""
    try:
        db = get_database()
        metrics = list(db.sustainability_metrics.find({"category": category}))
        return metrics
    except Exception as e:
        logger.error(f"Error fetching metrics by category: {e}")
        return []

def get_trends():
    """Get sustainability trends from MongoDB."""
    try:
        db = get_database()
        trends = list(db.trends.find())
        return trends
    except Exception as e:
        logger.error(f"Error fetching trends: {e}")
        return []

def get_trending_categories():
    """Get trending categories from MongoDB."""
    try:
        db = get_database()
        categories = list(db.trends.aggregate([
            {"$group": {"_id": "$category", "count": {"$sum": 1}, "growth_rate": {"$avg": "$growth_rate"}}},
            {"$project": {"name": "$_id", "count": 1, "growth_rate": 1, "description": {"$concat": ["Trending in ", "$_id"]}}},
            {"$sort": {"count": -1}},
            {"$limit": 6}
        ]))
        return categories
    except Exception as e:
        logger.error(f"Error fetching trending categories: {e}")
        return []

def get_stories_collection():
    """Get stories collection from MongoDB."""
    try:
        db = get_database()
        return db.stories
    except Exception as e:
        logger.error(f"Error getting stories collection: {e}")
        return None

# Routes
@vc_lens_bp.route('/')
def index():
    """VC-Lens™ main page"""
    
    # Get trending categories for portfolio mapping
    trending_categories = []
    try:
        trending_categories = get_trending_categories()
    except Exception as e:
        logger.error(f"Error fetching trending categories: {e}")
    
    # Get sample recent stories to display as examples
    recent_stories = []
    try:
        stories_collection = get_stories_collection()
        if stories_collection:
            recent_stories = list(stories_collection.find().sort('created_at', -1).limit(4))
    except Exception as e:
        logger.error(f"Error fetching recent stories: {e}")
    
    # Check if Gemini AI is available
    ai_available = gemini_controller is not None
    
    return render_template(
        'vc_lens/index.html',
        active_nav='vc_lens',
        trending_categories=trending_categories,
        recent_stories=recent_stories,
        ai_available=ai_available
    )

@vc_lens_bp.route('/upload', methods=['GET', 'POST'])
def upload_document():
    """Handle document upload and processing"""
    if request.method == 'POST':
        try:
            # Check if file was uploaded
            if 'document' not in request.files:
                return jsonify({
                    'success': False,
                    'error': 'No file uploaded'
                }), 400
            
            file = request.files['document']
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'No file selected'
                }), 400
            
            # Save file temporarily
            filename = secure_filename(file.filename)
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'vc_lens')
            os.makedirs(upload_path, exist_ok=True)
            file_path = os.path.join(upload_path, filename)
            file.save(file_path)
            
            # Process document
            metadata = {
                'uploaded_by': request.form.get('uploaded_by', 'unknown'),
                'document_type': request.form.get('document_type', 'unknown'),
                'tags': request.form.get('tags', '').split(',')
            }
            
            result = vc_lens_service.process_document(file_path, metadata)
            
            # Clean up temporary file
            os.remove(file_path)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'doc_id': result['doc_id'],
                    'message': f"Document processed successfully. {result['chunks_processed']} chunks processed."
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Unknown error processing document')
                }), 500
            
        except Exception as e:
            logger.error(f"Error processing document upload: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # GET request - render upload form
    return render_template('vc_lens/upload.html', active_nav='vc_lens')

@vc_lens_bp.route('/analyze/<doc_id>')
def analyze_document(doc_id):
    """Analyze a processed document"""
    try:
        # Get analysis type from query parameters
        analysis_type = request.args.get('type', 'comprehensive')
        
        # Perform analysis
        result = vc_lens_service.analyze_startup(doc_id, analysis_type)
        
        if result['success']:
            return render_template(
                'vc_lens/analysis.html',
                active_nav='vc_lens',
                analysis=result
            )
        else:
            return render_template(
                'vc_lens/error.html',
                active_nav='vc_lens',
                error=result.get('error', 'Unknown error analyzing document')
            )
            
    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        return render_template(
            'vc_lens/error.html',
            active_nav='vc_lens',
            error=str(e)
        )

@vc_lens_bp.route('/portfolio-fit/<doc_id>', methods=['GET', 'POST'])
def portfolio_fit(doc_id):
    """Compare document against portfolio criteria"""
    try:
        if request.method == 'POST':
            # Get portfolio criteria from request
            portfolio_criteria = request.json
            
            # Compare against criteria
            result = vc_lens_service.compare_portfolio_fit(doc_id, portfolio_criteria)
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Unknown error comparing portfolio fit')
                }), 500
                
        # GET request - render portfolio fit form
        return render_template(
            'vc_lens/portfolio_fit.html',
            active_nav='vc_lens',
            doc_id=doc_id
        )
            
    except Exception as e:
        logger.error(f"Error comparing portfolio fit: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 