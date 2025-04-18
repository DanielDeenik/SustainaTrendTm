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
        'vc_lens.html',
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

@vc_lens_bp.route('/search')
def search_documents():
    """Search for similar documents"""
    try:
        # Get search parameters
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 5))
        
        # Get filter criteria
        filter_criteria = {}
        for key in ['industry', 'stage', 'uploaded_by']:
            value = request.args.get(key)
            if value:
                filter_criteria[key] = value
        
        # Search documents
        results = vc_lens_service.search_similar(query, limit, filter_criteria)
        
        return render_template(
            'vc_lens/search_results.html',
            active_nav='vc_lens',
            query=query,
            results=results
        )
        
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        return render_template(
            'vc_lens/error.html',
            active_nav='vc_lens',
            error=str(e)
        )

@vc_lens_bp.route('/api/documents')
def list_documents():
    """List all processed documents"""
    try:
        # Get documents from service
        documents = []
        for doc_id, metadata in vc_lens_service.metadata_store.items():
            doc_data = vc_lens_service.document_store[doc_id]
            documents.append({
                'doc_id': doc_id,
                'metadata': metadata,
                'entities': doc_data['entities']
            })
        
        return jsonify({
            'success': True,
            'documents': documents
        })
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@vc_lens_bp.route('/api/documents/<doc_id>')
def get_document(doc_id):
    """Get document details"""
    try:
        if doc_id not in vc_lens_service.document_store:
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404
        
        doc_data = vc_lens_service.document_store[doc_id]
        metadata = vc_lens_service.metadata_store[doc_id]
        
        return jsonify({
            'success': True,
            'document': {
                'metadata': metadata,
                'text': doc_data['text'],
                'chunks': doc_data['chunks'],
                'entities': doc_data['entities']
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting document: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@vc_lens_bp.route('/startup-assessment')
def startup_assessment():
    """Startup sustainability assessment tool with three modules"""
    return render_template(
        'vc_lens/startup_assessment.html',
        active_nav='vc_lens',
        csrd_frameworks=[
            {'id': 'gri', 'name': 'GRI Standards', 'description': 'Global Reporting Initiative Standards'},
            {'id': 'sasb', 'name': 'SASB', 'description': 'Sustainability Accounting Standards Board'},
            {'id': 'tcfd', 'name': 'TCFD', 'description': 'Task Force on Climate-related Financial Disclosures'},
            {'id': 'esrs', 'name': 'ESRS', 'description': 'European Sustainability Reporting Standards'}
        ]
    )

@vc_lens_bp.route('/startup-assessment/foundational')
def startup_assessment_foundational():
    """Foundational readiness module for startup sustainability assessment"""
    return render_template(
        'vc_lens/startup_assessment_foundational.html',
        active_nav='vc_lens',
        frameworks=[
            {'id': 'gri', 'name': 'GRI Standards', 'description': 'Global Reporting Initiative Standards'},
            {'id': 'sasb', 'name': 'SASB', 'description': 'Sustainability Accounting Standards Board'},
            {'id': 'tcfd', 'name': 'TCFD', 'description': 'Task Force on Climate-related Financial Disclosures'},
            {'id': 'esrs', 'name': 'ESRS', 'description': 'European Sustainability Reporting Standards'},
            {'id': 'sfdr', 'name': 'SFDR', 'description': 'Sustainable Finance Disclosure Regulation'}
        ]
    )

@vc_lens_bp.route('/startup-assessment/forward-metrics')
def startup_assessment_forward_metrics():
    """Forward-looking metrics module for startup sustainability assessment"""
    return render_template(
        'vc_lens/startup_assessment_forward.html',
        active_nav='vc_lens',
        metric_types=[
            {'id': 'carbon', 'name': 'Carbon Emissions', 'unit': 'tCO2e'},
            {'id': 'energy', 'name': 'Energy Use', 'unit': 'MWh'},
            {'id': 'water', 'name': 'Water Consumption', 'unit': 'm³'},
            {'id': 'waste', 'name': 'Waste Generation', 'unit': 'tonnes'},
            {'id': 'circular', 'name': 'Circularity Index', 'unit': '%'}
        ]
    )

@vc_lens_bp.route('/startup-assessment/narrative')
def startup_assessment_narrative():
    """Narrative alignment module for startup sustainability assessment"""
    return render_template(
        'vc_lens/startup_assessment_narrative.html',
        active_nav='vc_lens',
        sdgs=[
            {'id': 1, 'name': 'No Poverty'},
            {'id': 2, 'name': 'Zero Hunger'},
            {'id': 3, 'name': 'Good Health and Well-being'},
            {'id': 4, 'name': 'Quality Education'},
            {'id': 5, 'name': 'Gender Equality'},
            {'id': 6, 'name': 'Clean Water and Sanitation'},
            {'id': 7, 'name': 'Affordable and Clean Energy'},
            {'id': 8, 'name': 'Decent Work and Economic Growth'},
            {'id': 9, 'name': 'Industry, Innovation and Infrastructure'},
            {'id': 10, 'name': 'Reduced Inequality'},
            {'id': 11, 'name': 'Sustainable Cities and Communities'},
            {'id': 12, 'name': 'Responsible Consumption and Production'},
            {'id': 13, 'name': 'Climate Action'},
            {'id': 14, 'name': 'Life Below Water'},
            {'id': 15, 'name': 'Life on Land'},
            {'id': 16, 'name': 'Peace, Justice and Strong Institutions'},
            {'id': 17, 'name': 'Partnerships for the Goals'}
        ]
    )

@vc_lens_bp.route('/api/portfolio-fit', methods=['POST'])
def api_portfolio_fit():
    """API endpoint to assess portfolio fit based on sustainability metrics"""
    
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Get document ID from session
    doc_id = session.get('thesis_file', {}).get('doc_id')
    if not doc_id:
        return jsonify({"error": "No thesis document found"}), 400
    
    # Search for similar documents
    similar_docs = vc_lens_service.search_similar(
        query=data.get('company_name', ''),
        limit=5
    )
    
    # Generate analysis based on similar documents
    result = {
        "company": data.get('company_name', 'Sample Company'),
        "sector": data.get('sector', 'Technology'),
        "fit_score": random.randint(65, 95),
        "analysis": f"{data.get('company_name', 'Sample Company')} shows strong alignment with your investment thesis, particularly in sustainability innovation and carbon reduction technologies.",
        "metrics": {
            "carbon_reduction": random.randint(20, 40),
            "renewable_adoption": random.randint(30, 80),
            "social_impact": random.randint(40, 90),
            "governance_rating": random.randint(50, 95)
        },
        "similar_documents": similar_docs
    }
    
    return jsonify(result)

@vc_lens_bp.route('/api/sustainability-assessment', methods=['POST'])
def api_sustainability_assessment():
    """API endpoint to generate sustainability assessment for startups"""
    
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    company_name = data.get('company_name', 'Sample Startup')
    sector = data.get('sector', 'Technology')
    
    # Generate mock assessment results
    result = {
        "company": company_name,
        "timestamp": datetime.now().isoformat(),
        "modules": {
            "foundational_readiness": {
                "score": random.randint(60, 95),
                "frameworks": {
                    "gri": random.randint(30, 100),
                    "sasb": random.randint(30, 100),
                    "tcfd": random.randint(30, 100),
                    "esrs": random.randint(30, 100)
                },
                "gap_analysis": [
                    "Missing governance disclosure on board oversight",
                    "Incomplete Scope 3 emissions inventory",
                    "Limited reporting on water stress management"
                ],
                "maturity_commentary": f"{company_name} demonstrates strong foundational sustainability reporting practices with room for improvement in emissions inventory management and water metrics."
            },
            "forward_metrics": {
                "carbon_forecast": {
                    "current_year": random.randint(500, 2000),
                    "year_1": random.randint(400, 1800),
                    "year_2": random.randint(350, 1600),
                    "year_3": random.randint(300, 1400),
                    "year_5": random.randint(250, 1200)
                },
                "renewable_growth": {
                    "current_year": random.randint(10, 30),
                    "year_5": random.randint(30, 60)
                },
                "circular_index": random.randint(30, 80),
                "efficiency_metrics": {
                    "water": {"trend": "improving", "percent_change": random.randint(5, 25)},
                    "energy": {"trend": "improving", "percent_change": random.randint(5, 30)}
                }
            },
            "narrative_alignment": {
                "sdg_mapping": [3, 7, 12, 13],
                "key_messages": [
                    f"{company_name} is on track to reduce carbon emissions by 30% within 5 years",
                    f"Circular economy initiatives expected to create €2.5M in value by 2027",
                    f"Strong alignment with EU Taxonomy for sustainable activities"
                ],
                "investor_story": f"{company_name} has reduced Scope 2 emissions by {random.randint(15, 35)}% YoY, outperforming {random.randint(60, 85)}% of industry peers in Northern Europe. Their CSRD readiness score is {random.randint(75, 95)}%, and sentiment analysis from 120+ online sources shows an {random.randint(10, 25)}% improvement in positive press after their Q4 sustainability campaign. Based on predictive modeling, they are likely to exceed their SBTi targets by 2026."
            }
        }
    }
    
    return jsonify(result)

@vc_lens_bp.route('/api/assessment/foundational', methods=['POST'])
def api_assessment_foundational():
    """API endpoint for foundational readiness assessment module"""
    
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    company_name = data.get('company_name', 'Sample Startup')
    sector = data.get('sector', 'Technology')
    size = data.get('size', 'Small (51-250)')
    frameworks = data.get('frameworks', [])
    
    # Default scores for frameworks if none selected
    if not frameworks:
        frameworks = ['gri', 'sasb', 'tcfd', 'esrs']
    
    # Generate assessment results
    framework_scores = {}
    for framework in frameworks:
        framework_scores[framework] = random.randint(30, 100)
    
    # Create gap analysis based on lowest scoring frameworks
    gap_analysis = []
    for framework, score in framework_scores.items():
        if score < 60:
            if framework == 'gri':
                gap_analysis.append("Missing comprehensive GRI disclosures on material topics")
            elif framework == 'sasb':
                gap_analysis.append("Incomplete SASB industry-specific metrics")
            elif framework == 'tcfd':
                gap_analysis.append("Limited TCFD governance disclosure on board oversight")
            elif framework == 'esrs':
                gap_analysis.append("Missing ESRS E1 climate change mitigation metrics")
            elif framework == 'sfdr':
                gap_analysis.append("Incomplete indicators for SFDR Principal Adverse Impact reporting")
    
    # If no low scores, add some generic gaps
    if not gap_analysis:
        gap_analysis = [
            "Incomplete Scope 3 emissions inventory",
            "Limited reporting on water stress management",
            "Missing governance disclosure on sustainability oversight"
        ]
    
    # Generate overall score (weighted average of framework scores)
    overall_score = sum(framework_scores.values()) / len(framework_scores)
    
    result = {
        "company": company_name,
        "sector": sector,
        "size": size,
        "timestamp": datetime.now().isoformat(),
        "assessment_id": str(uuid.uuid4()) if 'uuid' in globals() else f"{int(datetime.now().timestamp())}",
        "overall_score": round(overall_score),
        "frameworks": framework_scores,
        "gap_analysis": gap_analysis[:3],  # Limit to 3 gaps
        "maturity_commentary": f"{company_name} demonstrates {get_maturity_level(overall_score)} foundational sustainability reporting practices.",
        "recommendations": generate_foundational_recommendations(framework_scores, sector, size)
    }
    
    return jsonify(result)

@vc_lens_bp.route('/api/assessment/forward-metrics', methods=['POST'])
def api_assessment_forward_metrics():
    """API endpoint for forward-looking metrics assessment module"""
    
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    company_name = data.get('company_name', 'Sample Startup')
    sector = data.get('sector', 'Technology')
    size = data.get('size', 'Small (51-250)')
    base_year = data.get('base_year', datetime.now().year)
    metrics = data.get('metrics', ['carbon', 'energy', 'water', 'waste', 'circular'])
    
    # Generate forecast data for each selected metric
    forecasts = {}
    for metric in metrics:
        # Base values vary by sector and company size
        base_value = get_base_metric_value(metric, sector, size)
        
        # Generate yearly forecasts (with improvement trajectory)
        yearly_data = {
            "current_year": base_value,
            "year_1": int(base_value * (1 - 0.05 * random.uniform(0.8, 1.2))),
            "year_2": int(base_value * (1 - 0.12 * random.uniform(0.8, 1.2))),
            "year_3": int(base_value * (1 - 0.20 * random.uniform(0.8, 1.2))),
            "year_5": int(base_value * (1 - 0.35 * random.uniform(0.8, 1.2)))
        }
        
        # For some metrics like renewable or circular, trend is upward
        if metric in ['renewable', 'circular']:
            current = random.randint(10, 30)
            yearly_data = {
                "current_year": current,
                "year_1": min(100, current + random.randint(5, 10)),
                "year_2": min(100, current + random.randint(10, 20)),
                "year_3": min(100, current + random.randint(15, 30)),
                "year_5": min(100, current + random.randint(25, 45))
            }
        
        forecasts[metric] = yearly_data
    
    # Generate improvement metrics
    improvement_metrics = {}
    for metric in metrics:
        if metric not in ['circular', 'renewable']:  # Metrics with downward trend
            current = forecasts[metric]["current_year"]
            year_5 = forecasts[metric]["year_5"]
            percent_change = round(((year_5 - current) / current) * 100)
            trend = "improving" if percent_change < 0 else "worsening"
            improvement_metrics[metric] = {
                "trend": trend,
                "percent_change": abs(percent_change)
            }
        else:  # Metrics with upward trend
            current = forecasts[metric]["current_year"]
            year_5 = forecasts[metric]["year_5"]
            percent_change = round(((year_5 - current) / current) * 100)
            trend = "improving" if percent_change > 0 else "worsening"
            improvement_metrics[metric] = {
                "trend": trend,
                "percent_change": abs(percent_change)
            }
    
    result = {
        "company": company_name,
        "sector": sector,
        "size": size,
        "base_year": base_year,
        "timestamp": datetime.now().isoformat(),
        "assessment_id": str(uuid.uuid4()) if 'uuid' in globals() else f"{int(datetime.now().timestamp())}",
        "forecasts": forecasts,
        "improvement_metrics": improvement_metrics,
        "commentary": generate_metrics_commentary(forecasts, improvement_metrics, company_name, sector),
        "peer_comparison": generate_metrics_peer_comparison(forecasts, sector)
    }
    
    return jsonify(result)

@vc_lens_bp.route('/api/assessment/narrative', methods=['POST'])
def api_assessment_narrative():
    """API endpoint for narrative alignment assessment module"""
    
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    company_name = data.get('company_name', 'Sample Startup')
    sector = data.get('sector', 'Technology')
    size = data.get('size', 'Small (51-250)')
    thesis = data.get('thesis', '')
    selected_sdgs = data.get('sdgs', [])
    
    # If no SDGs selected, choose some based on sector
    if not selected_sdgs:
        selected_sdgs = get_default_sdgs_for_sector(sector)
    
    # Generate key messages based on company and SDGs
    key_messages = generate_key_messages(company_name, sector, selected_sdgs)
    
    # Generate VC-specific investor story with metrics
    investor_story = f"{company_name} has reduced Scope 2 emissions by {random.randint(15, 35)}% YoY, outperforming {random.randint(60, 85)}% of industry peers in their sector. Their regulatory readiness score is {random.randint(75, 95)}%, and sentiment analysis from 120+ online sources shows an {random.randint(10, 25)}% improvement in positive press after their latest sustainability initiative. Based on predictive modeling, they are likely to exceed their sustainability targets by 2026, giving them a competitive advantage in attracting ESG-focused capital."
    
    result = {
        "company": company_name,
        "sector": sector,
        "size": size,
        "timestamp": datetime.now().isoformat(),
        "assessment_id": str(uuid.uuid4()) if 'uuid' in globals() else f"{int(datetime.now().timestamp())}",
        "sdg_mapping": selected_sdgs,
        "key_messages": key_messages,
        "investor_story": investor_story,
        "eu_taxonomy_alignment": get_eu_taxonomy_alignment(sector),
        "impact_metrics": generate_impact_metrics(selected_sdgs, sector),
        "sentiment_analysis": {
            "positive": random.randint(65, 85),
            "neutral": random.randint(10, 25),
            "negative": random.randint(1, 10),
            "trending": random.choice(["up", "stable"])
        }
    }
    
    return jsonify(result)

# Helper functions for assessment modules

def get_maturity_level(score):
    """Determine maturity level based on score"""
    if score >= 80:
        return "advanced"
    elif score >= 60:
        return "progressive"
    elif score >= 40:
        return "developing"
    else:
        return "early-stage"

def generate_foundational_recommendations(framework_scores, sector, size):
    """Generate recommendations based on framework scores, sector and company size"""
    recommendations = []
    
    # Add recommendations based on low framework scores
    for framework, score in framework_scores.items():
        if score < 60:
            if framework == 'gri':
                recommendations.append("Develop a materiality assessment to identify key reporting topics aligned with GRI standards")
            elif framework == 'sasb':
                recommendations.append(f"Implement SASB industry-specific metrics for {sector} sector")
            elif framework == 'tcfd':
                recommendations.append("Establish board-level oversight for climate-related risks and opportunities")
            elif framework == 'esrs':
                recommendations.append("Develop comprehensive climate metrics aligned with ESRS E1 requirements")
            elif framework == 'sfdr':
                recommendations.append("Implement data collection for Principal Adverse Impact indicators")
    
    # Add size-specific recommendations
    if "Small" in size or "Startup" in size:
        recommendations.append("Focus on core material metrics most relevant to your investors and key stakeholders")
    
    # Add sector-specific recommendations
    if sector == "Technology":
        recommendations.append("Prioritize GHG Protocol-aligned Scope 3 emissions from purchased goods and services")
    elif sector == "Manufacturing":
        recommendations.append("Develop circular economy metrics and waste reduction targets")
    elif sector == "Energy":
        recommendations.append("Focus on transition risk scenarios and renewable energy adoption metrics")
    elif sector == "Financial Services":
        recommendations.append("Implement TCFD-aligned climate stress testing for investment portfolio")
    
    # Ensure we have at least 3 recommendations
    default_recommendations = [
        "Establish a baseline for Scope 1 and 2 emissions",
        "Develop a formal ESG governance structure with clear responsibilities",
        "Create a simple data collection process for material sustainability metrics"
    ]
    
    while len(recommendations) < 3:
        # Add remaining default recommendations that aren't already included
        for rec in default_recommendations:
            if rec not in recommendations:
                recommendations.append(rec)
                break
    
    return recommendations[:3]  # Return top 3 recommendations

def get_base_metric_value(metric, sector, size):
    """Get base metric values based on sector and company size"""
    # Size multiplier
    size_multiplier = 1.0
    if "Small" in size or "Startup" in size:
        size_multiplier = 0.5
    elif "Medium" in size:
        size_multiplier = 1.0
    elif "Large" in size:
        size_multiplier = 2.0
    elif "Enterprise" in size:
        size_multiplier = 3.5
    
    # Base values by metric and sector
    base_values = {
        "carbon": {
            "Technology": 1000,
            "Manufacturing": 5000,
            "Energy": 8000,
            "Financial Services": 800,
            "Healthcare": 1200,
            "default": 1500
        },
        "energy": {
            "Technology": 2000,
            "Manufacturing": 8000,
            "Energy": 10000,
            "Financial Services": 1500,
            "Healthcare": 3000,
            "default": 3000
        },
        "water": {
            "Technology": 500,
            "Manufacturing": 8000,
            "Energy": 12000,
            "Financial Services": 300,
            "Healthcare": 5000,
            "default": 2000
        },
        "waste": {
            "Technology": 100,
            "Manufacturing": 800,
            "Energy": 500,
            "Financial Services": 50,
            "Healthcare": 300,
            "default": 200
        }
    }
    
    # Get base value for sector, or use default if sector not found
    sector_values = base_values.get(metric, {"default": 1000})
    base = sector_values.get(sector, sector_values.get("default", 1000))
    
    # Apply size multiplier and some randomness
    return int(base * size_multiplier * random.uniform(0.8, 1.2))

def generate_metrics_commentary(forecasts, improvement_metrics, company_name, sector):
    """Generate commentary for forward-looking metrics"""
    # Extract key improvements for commentary
    key_improvements = []
    for metric, data in improvement_metrics.items():
        if data["trend"] == "improving":
            if metric == "carbon":
                key_improvements.append(f"a {data['percent_change']}% reduction in carbon emissions")
            elif metric == "energy":
                key_improvements.append(f"a {data['percent_change']}% reduction in energy consumption")
            elif metric == "water":
                key_improvements.append(f"a {data['percent_change']}% reduction in water usage")
            elif metric == "waste":
                key_improvements.append(f"a {data['percent_change']}% reduction in waste generation")
            elif metric == "circular":
                key_improvements.append(f"a {data['percent_change']}% increase in circular economy index")
            elif metric == "renewable":
                key_improvements.append(f"a {data['percent_change']}% increase in renewable energy adoption")
    
    # Build the commentary
    commentary = f"Based on current trajectory, {company_name} is on track to achieve "
    
    if key_improvements:
        if len(key_improvements) == 1:
            commentary += f"{key_improvements[0]}"
        elif len(key_improvements) == 2:
            commentary += f"{key_improvements[0]} and {key_improvements[1]}"
        else:
            commentary += ", ".join(key_improvements[:-1]) + f", and {key_improvements[-1]}"
        
        commentary += f" by {datetime.now().year + 5}. "
    else:
        commentary += f"significant sustainability improvements by {datetime.now().year + 5}. "
    
    # Add sector-specific commentary
    if sector == "Technology":
        commentary += "This places them in a strong position among technology peers, particularly for attracting ESG-focused investment."
    elif sector == "Manufacturing":
        commentary += "This represents an above-average improvement trajectory for the manufacturing sector, potentially reducing regulatory and operational risks."
    elif sector == "Energy":
        commentary += "For an energy company, these projections align well with sectoral transition pathway expectations for 2030 climate targets."
    else:
        commentary += "These improvements align with investor expectations for measurable sustainability progress over the next five years."
    
    return commentary

def generate_metrics_peer_comparison(forecasts, sector):
    """Generate peer comparison data for forward metrics"""
    # Generate 3-5 peer companies for comparison
    peer_count = random.randint(3, 5)
    peers = []
    
    # Sample peer names by sector
    peer_names = {
        "Technology": ["TechGreen", "EcoSoft", "SustainableTech", "GreenByte", "EnviroTech"],
        "Manufacturing": ["GreenManufacturing", "EcoFactory", "SustainMake", "CleanProduction", "CircularMfg"],
        "Energy": ["CleanPower", "GreenEnergy", "RenewCorp", "SustainablePower", "EcoEnergy"],
        "Financial Services": ["GreenFinance", "SustainCapital", "EcoBank", "ESGWealth", "ClimateInvest"],
        "default": ["PeerA", "PeerB", "PeerC", "PeerD", "PeerE"]
    }
    
    # Get peer names for sector, or use default if sector not found
    available_peers = peer_names.get(sector, peer_names["default"])
    selected_peers = random.sample(available_peers, min(peer_count, len(available_peers)))
    
    # Choose a key metric for comparison (carbon, energy, or circular)
    key_metric = random.choice(["carbon", "energy", "circular"])
    if key_metric not in forecasts:
        key_metric = list(forecasts.keys())[0] if forecasts else "carbon"
    
    # Current company value
    company_value = forecasts[key_metric]["current_year"]
    company_future = forecasts[key_metric]["year_5"]
    
    # Direction of improvement (lower is better for carbon, energy, etc; higher is better for circular, renewable)
    lower_is_better = key_metric not in ["circular", "renewable"]
    
    # Determine improvement direction for user company
    if lower_is_better:
        company_improving = company_future < company_value
    else:
        company_improving = company_future > company_value
    
    # Generate peer data
    for peer_name in selected_peers:
        # Generate current value (around the company value with some variation)
        variation = random.uniform(0.7, 1.3)
        peer_current = int(company_value * variation)
        
        # Determine if peer is improving better or worse than company
        peer_performance = random.choice(["better", "worse", "similar"])
        
        if peer_performance == "better":
            # Peer improves more than company
            if lower_is_better:
                if company_improving:
                    # Both improving, peer improves more
                    improvement_factor = random.uniform(1.05, 1.2)
                    peer_future = int(peer_current * (1 - (((company_value - company_future) / company_value) * improvement_factor)))
                else:
                    # Company not improving, but peer is
                    peer_future = int(peer_current * 0.85)
            else:
                if company_improving:
                    # Both improving, peer improves more
                    improvement_factor = random.uniform(1.05, 1.2)
                    increase_percentage = ((company_future - company_value) / company_value) * improvement_factor
                    peer_future = int(peer_current * (1 + increase_percentage))
                else:
                    # Company not improving, but peer is
                    peer_future = int(peer_current * 1.15)
        
        elif peer_performance == "worse":
            # Peer improves less than company
            if lower_is_better:
                if company_improving:
                    # Both improving, peer improves less
                    improvement_factor = random.uniform(0.5, 0.9)
                    peer_future = int(peer_current * (1 - (((company_value - company_future) / company_value) * improvement_factor)))
                else:
                    # Company not improving, peer is worse
                    peer_future = int(peer_current * 1.1)
            else:
                if company_improving:
                    # Both improving, peer improves less
                    improvement_factor = random.uniform(0.5, 0.9)
                    increase_percentage = ((company_future - company_value) / company_value) * improvement_factor
                    peer_future = int(peer_current * (1 + increase_percentage))
                else:
                    # Company not improving, peer is worse
                    peer_future = int(peer_current * 0.9)
        
        else:  # "similar"
            # Peer improves similarly to company
            if lower_is_better:
                improvement_percentage = (company_value - company_future) / company_value
                peer_future = int(peer_current * (1 - improvement_percentage * random.uniform(0.95, 1.05)))
            else:
                improvement_percentage = (company_future - company_value) / company_value
                peer_future = int(peer_current * (1 + improvement_percentage * random.uniform(0.95, 1.05)))
        
        # Add peer to results
        peers.append({
            "name": peer_name,
            "current_value": peer_current,
            "future_value": peer_future,
            "metric": key_metric,
            "unit": "tCO2e" if key_metric == "carbon" else ("MWh" if key_metric == "energy" else 
                    ("m³" if key_metric == "water" else 
                    ("tonnes" if key_metric == "waste" else "%")))
        })
    
    return {
        "metric": key_metric,
        "company_current": company_value,
        "company_future": company_future,
        "peers": peers
    }

def get_default_sdgs_for_sector(sector):
    """Get default SDGs for a given sector"""
    # Map sectors to relevant SDGs
    sector_sdgs = {
        "Technology": [7, 9, 11, 12, 13],
        "Energy": [7, 9, 11, 12, 13],
        "Manufacturing": [8, 9, 12, 13],
        "Consumer Goods": [3, 6, 12, 13, 14, 15],
        "Healthcare": [3, 6, 10],
        "Financial Services": [1, 5, 8, 10, 13],
        "Food & Agriculture": [2, 6, 12, 13, 15],
        "Transportation": [9, 11, 13],
        "Construction": [9, 11, 12, 13],
        "Retail": [8, 10, 12],
        "Media & Entertainment": [4, 5, 10, 16],
        "default": [8, 9, 12, 13]
    }
    
    # Get SDGs for sector, or use default if sector not found
    relevant_sdgs = sector_sdgs.get(sector, sector_sdgs["default"])
    
    # Return 3-4 randomly selected SDGs from the relevant ones
    selected_count = min(len(relevant_sdgs), random.randint(3, 4))
    return sorted(random.sample(relevant_sdgs, selected_count))

def generate_key_messages(company_name, sector, sdgs):
    """Generate key sustainability messages based on company, sector, and SDGs"""
    messages = []
    
    # SDG-specific messages
    sdg_messages = {
        1: f"{company_name} supports financial inclusion initiatives aligned with SDG 1",
        2: f"{company_name} contributes to sustainable food systems and nutrition security",
        3: f"{company_name} promotes health and well-being through its sustainable products and operations",
        4: f"{company_name} supports education initiatives and skills development",
        5: f"{company_name} advances gender equality and inclusive workplace practices",
        6: f"{company_name} implements water stewardship and water efficiency measures",
        7: f"{company_name} is on track to achieve {random.randint(50, 90)}% renewable energy use by {datetime.now().year + random.randint(3, 7)}",
        8: f"{company_name} creates decent work and sustainable economic growth in its communities",
        9: f"{company_name} invests in sustainable infrastructure and innovation",
        10: f"{company_name} works to reduce inequalities through its operations and value chain",
        11: f"{company_name} contributes to sustainable cities and communities",
        12: f"{company_name} implements circular economy initiatives expected to create €{random.randint(1, 5)}M in value by {datetime.now().year + random.randint(2, 5)}",
        13: f"{company_name} is on track to reduce carbon emissions by {random.randint(25, 50)}% within 5 years",
        14: f"{company_name} supports ocean conservation and sustainable maritime practices",
        15: f"{company_name} promotes biodiversity and sustainable land management",
        16: f"{company_name} upholds ethical business practices and transparency",
        17: f"{company_name} builds partnerships for sustainable development goals"
    }
    
    # Add messages for each selected SDG
    for sdg in sdgs:
        if sdg in sdg_messages:
            messages.append(sdg_messages[sdg])
    
    # Add sector-specific messages
    if sector == "Technology":
        messages.append(f"{company_name} develops sustainable technology solutions that enable emissions reduction across sectors")
    elif sector == "Energy":
        messages.append(f"Strong alignment with EU Taxonomy for sustainable energy activities")
    elif sector == "Manufacturing":
        messages.append(f"{company_name} is implementing sustainable manufacturing practices that reduce resource intensity by {random.randint(15, 30)}%")
    elif sector == "Financial Services":
        messages.append(f"{company_name} aligns with Article 8 of SFDR with {random.randint(60, 90)}% of products meeting sustainability criteria")
    
    # Ensure we have at least 3 messages
    default_messages = [
        f"{company_name} has implemented an ESG governance structure with board-level oversight",
        f"{company_name} measures and reports its sustainability impact in line with leading frameworks",
        f"{company_name} engages with stakeholders to identify material sustainability issues"
    ]
    
    while len(messages) < 3:
        # Add remaining default messages that aren't already included
        for msg in default_messages:
            if msg not in messages:
                messages.append(msg)
                break
    
    # Return 3 key messages
    return messages[:3]

def get_eu_taxonomy_alignment(sector):
    """Generate EU Taxonomy alignment metrics based on sector"""
    # Sector-based default alignment percentages
    sector_alignment = {
        "Technology": {"eligible": random.randint(30, 60), "aligned": random.randint(15, 40)},
        "Energy": {"eligible": random.randint(60, 90), "aligned": random.randint(30, 70)},
        "Manufacturing": {"eligible": random.randint(40, 70), "aligned": random.randint(20, 50)},
        "Financial Services": {"eligible": random.randint(50, 80), "aligned": random.randint(25, 60)},
        "Healthcare": {"eligible": random.randint(20, 50), "aligned": random.randint(10, 30)},
        "default": {"eligible": random.randint(25, 55), "aligned": random.randint(10, 35)}
    }
    
    # Get alignment for sector, or use default if sector not found
    alignment = sector_alignment.get(sector, sector_alignment["default"])
    
    # Ensure aligned is not greater than eligible
    if alignment["aligned"] > alignment["eligible"]:
        alignment["aligned"] = alignment["eligible"]
    
    # Add assessment and recommendation
    if alignment["aligned"] > 50:
        assessment = "Strong alignment with EU Taxonomy criteria"
        recommendation = "Continue building on existing alignment and prepare for expanded Taxonomy criteria"
    elif alignment["aligned"] > 25:
        assessment = "Moderate alignment with EU Taxonomy criteria"
        recommendation = "Focus on closing gaps in key eligible activities and improving data quality"
    else:
        assessment = "Early-stage alignment with EU Taxonomy criteria"
        recommendation = "Prioritize highest eligibility areas and develop a roadmap for progressive alignment"
    
    return {
        "revenue_eligible": alignment["eligible"],
        "revenue_aligned": alignment["aligned"],
        "capex_eligible": min(100, alignment["eligible"] + random.randint(5, 15)),
        "capex_aligned": min(100, alignment["aligned"] + random.randint(5, 15)),
        "assessment": assessment,
        "recommendation": recommendation
    }

def generate_impact_metrics(sdgs, sector):
    """Generate impact metrics based on selected SDGs and sector"""
    impact_metrics = []
    
    # Map SDGs to relevant impact metrics
    sdg_metrics = {
        1: {"metric": "Financial inclusion", "value": f"{random.randint(1000, 5000)} beneficiaries"},
        2: {"metric": "Sustainable food systems", "value": f"{random.randint(50, 500)} tonnes sustainable production"},
        3: {"metric": "Health improvement", "value": f"{random.randint(5000, 20000)} people reached"},
        4: {"metric": "Education access", "value": f"{random.randint(500, 2000)} students supported"},
        5: {"metric": "Gender diversity", "value": f"{random.randint(35, 50)}% women in workforce"},
        6: {"metric": "Water saved", "value": f"{random.randint(1000, 10000)} m³ annually"},
        7: {"metric": "Clean energy generated", "value": f"{random.randint(500, 5000)} MWh annually"},
        8: {"metric": "Jobs created", "value": f"{random.randint(10, 500)} new positions"},
        9: {"metric": "R&D in sustainable tech", "value": f"€{random.randint(100, 2000)}K invested"},
        10: {"metric": "Pay equity ratio", "value": f"{random.randint(90, 99)}%"},
        11: {"metric": "Urban sustainability", "value": f"{random.randint(2, 10)} cities impacted"},
        12: {"metric": "Waste diverted from landfill", "value": f"{random.randint(50, 500)} tonnes"},
        13: {"metric": "Emissions avoided", "value": f"{random.randint(100, 2000)} tCO2e"},
        14: {"metric": "Ocean protection", "value": f"{random.randint(1, 10)} initiatives supported"},
        15: {"metric": "Land preserved", "value": f"{random.randint(5, 100)} hectares"},
        16: {"metric": "Transparency score", "value": f"{random.randint(70, 95)}/100"},
        17: {"metric": "Partnerships", "value": f"{random.randint(3, 15)} sustainable development partnerships"}
    }
    
    # Add metrics for each selected SDG
    for sdg in sdgs:
        if sdg in sdg_metrics:
            impact_metrics.append({
                "sdg": sdg,
                "metric": sdg_metrics[sdg]["metric"],
                "value": sdg_metrics[sdg]["value"]
            })
    
    # Add sector-specific impact metric
    sector_metrics = {
        "Technology": {"metric": "Digital inclusion", "value": f"{random.randint(5000, 50000)} users reached"},
        "Energy": {"metric": "GHG intensity reduction", "value": f"{random.randint(10, 40)}% reduction"},
        "Manufacturing": {"metric": "Sustainable materials", "value": f"{random.randint(15, 60)}% recycled content"},
        "Financial Services": {"metric": "Sustainable finance", "value": f"€{random.randint(1, 50)}M mobilized"},
        "Healthcare": {"metric": "Affordable treatment", "value": f"{random.randint(1000, 10000)} patients served"},
        "default": {"metric": "Sustainability initiative", "value": f"{random.randint(2, 8)} projects completed"}
    }
    
    # Get sector metric, or use default if sector not found
    sector_metric = sector_metrics.get(sector, sector_metrics["default"])
    impact_metrics.append({
        "sdg": "sector",
        "metric": sector_metric["metric"],
        "value": sector_metric["value"]
    })
    
    return impact_metrics

# Helper function to generate sample mapping data
def generate_sample_mapping():
    """Generate sample thesis mapping data for the demo"""
    return {
        "thesis_themes": [
            {
                "theme": "Climate Tech Innovation",
                "keywords": ["carbon reduction", "emissions tracking", "climate adaptation"],
                "match_score": 87,
                "matching_companies": ["Climate AI", "CarbonTrack", "GreenTech Solutions"]
            },
            {
                "theme": "Circular Economy Solutions",
                "keywords": ["waste reduction", "recycling", "remanufacturing"],
                "match_score": 74,
                "matching_companies": ["CircularPack", "WasteZero", "ReCraft Materials"]
            },
            {
                "theme": "Water Conservation Technology",
                "keywords": ["water efficiency", "irrigation tech", "water recycling"],
                "match_score": 68,
                "matching_companies": ["AquaSmart", "HydroEfficient", "WaterWise Tech"]
            }
        ],
        "esg_alignment": {
            "environmental": {
                "score": 92,
                "target_metrics": ["carbon intensity", "renewable energy adoption", "waste reduction"]
            },
            "social": {
                "score": 78,
                "target_metrics": ["diversity metrics", "community impact", "supply chain ethics"]
            },
            "governance": {
                "score": 84,
                "target_metrics": ["board diversity", "executive compensation", "risk management"]
            }
        },
        "regulatory_relevance": [
            {"framework": "CSRD", "relevance": "High", "description": "Directly addresses CSRD reporting requirements"},
            {"framework": "EU Taxonomy", "relevance": "Medium", "description": "Aligns with sustainable economic activities"},
            {"framework": "SFDR", "relevance": "Medium-High", "description": "Maps to Article 8 and 9 fund requirements"}
        ]
    }