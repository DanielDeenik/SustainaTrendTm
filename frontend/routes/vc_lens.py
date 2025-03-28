"""
VC-Lens™ Routes for SustainaTrend™ Platform
Provides AI-powered investor lens with automated fund-fit analysis and startup impact summary
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import os
import json
from datetime import datetime, timedelta
import random
from werkzeug.utils import secure_filename

# Import MongoDB connections
try:
    # Try direct import first
    from mongo_client import get_db, get_stories_collection
except ImportError:
    try:
        # Try with full path
        from frontend.mongo_client import get_db, get_stories_collection
    except ImportError:
        # Define fallback functions if mongo_client.py is not found
        def get_db():
            return None
        
        def get_stories_collection():
            return None

try:
    # Try direct import first
    from mongo_metrics import get_metrics, get_metrics_by_category
except ImportError:
    try:
        # Try with full path
        from frontend.mongo_metrics import get_metrics, get_metrics_by_category
    except ImportError:
        # Define fallback functions if mongo_metrics.py is not found
        def get_metrics():
            return []
        
        def get_metrics_by_category(category):
            return []

try:
    # Try direct import first
    from mongo_trends import get_trends, get_trending_categories
except ImportError:
    try:
        # Try with full path
        from frontend.mongo_trends import get_trends, get_trending_categories
    except ImportError:
        # Define fallback functions if mongo_trends.py is not found
        def get_trends():
            return []
        
        def get_trending_categories():
            return []

# Import MongoDB service
try:
    from services.mongodb_service import MongoDBService
except ImportError:
    try:
        from frontend.services.mongodb_service import MongoDBService
    except ImportError:
        # Create a simple mock if the service is not available
        class MongoDBService:
            def __init__(self, *args, **kwargs):
                pass

# Import Gemini/Google AI functionality if available
try:
    # Try direct import from utils directory
    from utils.gemini_search import GeminiSearchController
    gemini_available = True
except ImportError:
    try:
        # Try import from gemini_search in frontend directory
        from gemini_search import GeminiSearchController
        gemini_available = True
    except ImportError:
        try:
            # Try with frontend prefix
            from frontend.gemini_search import GeminiSearchController
            gemini_available = True
        except ImportError:
            gemini_available = False
            # Define a placeholder GeminiSearchController
            class GeminiSearchController:
                def __init__(self):
                    pass

# Create blueprint
vc_lens_bp = Blueprint('vc_lens', __name__, url_prefix='/vc-insights')

# Initialize Gemini controller if available
gemini_controller = None
if gemini_available:
    try:
        gemini_controller = GeminiSearchController()
    except Exception as e:
        print(f"Error initializing Gemini controller: {e}")

@vc_lens_bp.route('/')
def index():
    """VC-Lens™ main page"""
    
    # Get trending categories for portfolio mapping
    trending_categories = []
    try:
        trending_categories = get_trending_categories()
    except Exception as e:
        print(f"Error fetching trending categories: {e}")
    
    # Get sample recent stories to display as examples
    recent_stories = []
    try:
        stories_collection = get_stories_collection()
        if stories_collection:
            recent_stories = list(stories_collection.find().sort('created_at', -1).limit(4))
    except Exception as e:
        print(f"Error fetching recent stories: {e}")
    
    # Check if Gemini AI is available
    ai_available = gemini_controller is not None
    
    return render_template(
        'vc_lens/index.html',
        active_nav='vc_lens',
        trending_categories=trending_categories,
        recent_stories=recent_stories,
        ai_available=ai_available
    )

@vc_lens_bp.route('/upload-thesis', methods=['GET', 'POST'])
def upload_thesis():
    """Upload investment thesis for analysis"""
    
    if request.method == 'POST':
        # Process file upload
        if 'thesis_file' not in request.files:
            return jsonify({"error": "No file part"}), 400
            
        file = request.files['thesis_file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        if file:
            # Save file
            filename = secure_filename(file.filename)
            save_path = os.path.join('uploads', 'thesis', filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            file.save(save_path)
            
            # Store file info in session
            session['thesis_file'] = {
                'filename': filename,
                'path': save_path,
                'uploaded_at': datetime.now().isoformat()
            }
            
            # Redirect to analysis page
            return redirect(url_for('vc_lens.analyze_thesis'))
    
    return render_template(
        'vc_lens/upload_thesis.html',
        active_nav='vc_lens'
    )

@vc_lens_bp.route('/analyze-thesis')
def analyze_thesis():
    """Analyze investment thesis and map to sustainability data"""
    
    # Check if thesis file exists in session
    if 'thesis_file' not in session:
        return redirect(url_for('vc_lens.upload_thesis'))
    
    # Get thesis file info
    thesis_file = session['thesis_file']
    
    # Generate sample mapping data
    # In a real implementation, this would analyze the thesis document
    sample_mapping = generate_sample_mapping()
    
    return render_template(
        'vc_lens/thesis_analysis.html',
        active_nav='vc_lens',
        thesis_file=thesis_file,
        mapping=sample_mapping
    )

@vc_lens_bp.route('/startup-assessment')
def startup_assessment():
    """Startup sustainability assessment tool"""
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

@vc_lens_bp.route('/api/portfolio-fit', methods=['POST'])
def api_portfolio_fit():
    """API endpoint to assess portfolio fit based on sustainability metrics"""
    
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Generate sample portfolio fit analysis
    # In real implementation, this would use the uploaded thesis and company data
    
    company_name = data.get('company_name', 'Sample Company')
    sector = data.get('sector', 'Technology')
    
    # Generate mock analysis
    result = {
        "company": company_name,
        "sector": sector,
        "fit_score": random.randint(65, 95),
        "analysis": f"{company_name} shows strong alignment with your investment thesis, particularly in sustainability innovation and carbon reduction technologies.",
        "metrics": {
            "carbon_reduction": random.randint(20, 40),
            "renewable_adoption": random.randint(30, 80),
            "social_impact": random.randint(40, 90),
            "governance_rating": random.randint(50, 95)
        },
        "peer_comparison": [
            {"name": "Peer 1", "score": random.randint(50, 90)},
            {"name": "Peer 2", "score": random.randint(50, 90)},
            {"name": "Peer 3", "score": random.randint(50, 90)}
        ]
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