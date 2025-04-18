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
from src.frontend.refactored.services.mongodb_service import mongodb_service
from src.frontend.refactored.services.config_service import config_service

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
        # Use the singleton MongoDB service instance
        metrics = mongodb_service.find_many('sustainability_metrics', query={})
        return metrics
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        return []

def get_metrics_by_category(category):
    """Get sustainability metrics by category from MongoDB."""
    try:
        # Use the singleton MongoDB service instance
        metrics = mongodb_service.find_many('sustainability_metrics', query={"category": category})
        return metrics
    except Exception as e:
        logger.error(f"Error fetching metrics by category: {e}")
        return []

def get_trends():
    """Get sustainability trends from MongoDB."""
    try:
        # Use the singleton MongoDB service instance
        trends = mongodb_service.find_many('trends', query={})
        return trends
    except Exception as e:
        logger.error(f"Error fetching trends: {e}")
        return []

def get_trending_categories():
    """Get trending categories from MongoDB."""
    try:
        # Use the singleton MongoDB service instance
        collection = mongodb_service.get_collection('trends')
        categories = list(collection.aggregate([
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
        # Use the singleton MongoDB service instance
        return mongodb_service.get_collection('stories')
    except Exception as e:
        logger.error(f"Error getting stories collection: {e}")
        return None

# Routes
@vc_lens_bp.route('/')
def index():
    """Render the VC Lens dashboard."""
    try:
        # Use the singleton MongoDB service instance
        mongodb = mongodb_service
        
        # Fetch portfolio companies
        companies = mongodb.find_many('portfolio_companies', query={}, sort=[('name', 1)])
        
        # Fetch investment metrics
        metrics = {
            'total_companies': len(companies),
            'total_investment': sum(company.get('investment_amount', 0) for company in companies),
            'average_roi': sum(company.get('roi', 0) for company in companies) / len(companies) if companies else 0
        }
        
        return render_template('vc_lens/dashboard.html',
                             companies=companies,
                             metrics=metrics)
    except Exception as e:
        logger.error(f"Error in VC Lens dashboard: {str(e)}")
        return render_template('errors/500.html'), 500

@vc_lens_bp.route('/api/companies')
def get_companies():
    """API endpoint for portfolio companies."""
    try:
        # Use the singleton MongoDB service instance
        mongodb = mongodb_service
        
        # Get filter parameters
        sector = request.args.get('sector')
        stage = request.args.get('stage')
        limit = int(request.args.get('limit', 100))
        
        # Build query
        query = {}
        if sector:
            query['sector'] = sector
        if stage:
            query['stage'] = stage
        
        # Get companies
        companies = mongodb.find_many('portfolio_companies', query=query, sort=[('name', 1)], limit=limit)
        
        return jsonify(companies)
    except Exception as e:
        logger.error(f"Error getting companies: {str(e)}")
        return jsonify({'error': str(e)}), 500

@vc_lens_bp.route('/api/metrics')
def get_metrics():
    """API endpoint for investment metrics."""
    try:
        # Use the singleton MongoDB service instance
        mongodb = mongodb_service
        
        # Get filter parameters
        sector = request.args.get('sector')
        stage = request.args.get('stage')
        
        # Build query
        query = {}
        if sector:
            query['sector'] = sector
        if stage:
            query['stage'] = stage
        
        # Get companies
        companies = mongodb.find_many('portfolio_companies', query=query)
        
        # Calculate metrics
        metrics = {
            'total_companies': len(companies),
            'total_investment': sum(company.get('investment_amount', 0) for company in companies),
            'average_roi': sum(company.get('roi', 0) for company in companies) / len(companies) if companies else 0,
            'sector_distribution': {},
            'stage_distribution': {}
        }
        
        # Calculate distributions
        for company in companies:
            # Sector distribution
            sector = company.get('sector', 'Unknown')
            if sector not in metrics['sector_distribution']:
                metrics['sector_distribution'][sector] = 0
            metrics['sector_distribution'][sector] += 1
            
            # Stage distribution
            stage = company.get('stage', 'Unknown')
            if stage not in metrics['stage_distribution']:
                metrics['stage_distribution'][stage] = 0
            metrics['stage_distribution'][stage] += 1
        
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@vc_lens_bp.route('/api/company/<company_id>')
def get_company(company_id):
    """API endpoint for company details."""
    try:
        # Use the singleton MongoDB service instance
        mongodb = mongodb_service
        
        # Get company details
        company = mongodb.find_one('portfolio_companies', query={'_id': company_id})
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Get company metrics
        metrics = mongodb.get_company_metrics(company_id)
        
        return jsonify({
            'company': company,
            'metrics': metrics
        })
    except Exception as e:
        logger.error(f"Error getting company details: {str(e)}")
        return jsonify({'error': str(e)}), 500

@vc_lens_bp.route('/api/trends')
def get_trends():
    """API endpoint for investment trends."""
    try:
        # Use the singleton MongoDB service instance
        mongodb = mongodb_service
        
        # Get filter parameters
        timeframe = request.args.get('timeframe', '30d')
        limit = int(request.args.get('limit', 20))
        
        # Calculate date range
        end_date = datetime.now()
        if timeframe == '7d':
            start_date = end_date - timedelta(days=7)
        elif timeframe == '30d':
            start_date = end_date - timedelta(days=30)
        elif timeframe == '90d':
            start_date = end_date - timedelta(days=90)
        else:  # 1y
            start_date = end_date - timedelta(days=365)
        
        # Get trends
        trends = mongodb.get_trends(
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        return jsonify(trends)
    except Exception as e:
        logger.error(f"Error getting trends: {str(e)}")
        return jsonify({'error': str(e)}), 500

@vc_lens_bp.route('/api/benchmarks')
def get_benchmarks():
    """API endpoint for industry benchmarks."""
    try:
        # Use the singleton MongoDB service instance
        mongodb = mongodb_service
        
        # Get filter parameters
        sector = request.args.get('sector')
        stage = request.args.get('stage')
        
        # Get benchmarks
        benchmarks = mongodb.find_many('benchmarks', query={
            'sector': sector,
            'stage': stage
        })
        
        return jsonify(benchmarks)
    except Exception as e:
        logger.error(f"Error getting benchmarks: {str(e)}")
        return jsonify({'error': str(e)}), 500

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