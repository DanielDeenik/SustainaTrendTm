"""
Benchmarking Engine Routes for SustainaTrend™ Platform
Provides AI-powered benchmarking tools with intelligent peer comparison and regulatory framework mapping
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import os
import json
from datetime import datetime, timedelta
import random
import logging
from werkzeug.utils import secure_filename

# Configure logging
logger = logging.getLogger(__name__)

# Import MongoDB connections
try:
    # Try direct import first
    from mongo_client import get_db, get_database, serialize_document
except ImportError:
    try:
        # Try with full path
        from frontend.mongo_client import get_db, get_database, serialize_document
    except ImportError:
        # Define fallback functions if mongo_client.py is not found
        def get_db():
            return None
        
        def get_database():
            return None
            
        def serialize_document(doc):
            return doc

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

# Import LangChain components if available
try:
    from langchain.chains import LLMChain
    from langchain.memory import ConversationBufferMemory
    from langchain.prompts import PromptTemplate
    langchain_available = True
except ImportError:
    langchain_available = False
    logger.warning("LangChain not available. Some AI features will be limited.")

# Create blueprint
benchmarking_bp = Blueprint('benchmarking', __name__, url_prefix='/benchmarking')

# Initialize Gemini controller if available
gemini_controller = None
if gemini_available:
    try:
        gemini_controller = GeminiSearchController()
        logger.info("Gemini controller initialized for Benchmarking Engine")
    except Exception as e:
        logger.error(f"Error initializing Gemini controller: {e}")

# Supported regulatory frameworks for benchmarking
REGULATORY_FRAMEWORKS = {
    "CSRD": {
        "name": "Corporate Sustainability Reporting Directive",
        "description": "European framework requiring companies to report on environmental and social impacts",
        "region": "EU",
        "company_types": ["Public", "Large Private"],
        "key_metrics": ["emissions", "energy", "water", "biodiversity", "social", "governance"]
    },
    "TCFD": {
        "name": "Task Force on Climate-related Financial Disclosures",
        "description": "Framework for climate-related financial risk disclosures",
        "region": "Global",
        "company_types": ["Public", "Private"],
        "key_metrics": ["emissions", "energy", "climate_risk", "governance"]
    },
    "SDG": {
        "name": "Sustainable Development Goals",
        "description": "UN framework with 17 goals for sustainable development",
        "region": "Global",
        "company_types": ["All"],
        "key_metrics": ["emissions", "energy", "water", "biodiversity", "social", "governance", "economic"]
    },
    "VC_METRICS": {
        "name": "VC Sustainability Metrics",
        "description": "Customized metrics for venture capital portfolio companies",
        "region": "Global",
        "company_types": ["Startup", "Scale-up"],
        "key_metrics": ["emissions_intensity", "renewable_percent", "diversity", "esg_risk_score", "green_revenue"]
    }
}

# Sample industry sectors for benchmarking
INDUSTRY_SECTORS = [
    "Technology", "Energy", "Manufacturing", "Consumer Goods", "Healthcare", 
    "Financial Services", "Food & Agriculture", "Transportation & Logistics",
    "Chemicals", "Construction", "Retail", "Media & Entertainment"
]

# Sample regions for benchmarking
REGIONS = [
    "EU", "North America", "Asia Pacific", "Middle East & Africa", "Latin America",
    "Nordic", "Western Europe", "Eastern Europe", "Southeast Asia", "Oceania"
]

# Sample company sizes for benchmarking
COMPANY_SIZES = [
    "Startup (1-50)", "Small (51-250)", "Medium (251-1000)", "Large (1001-5000)", "Enterprise (5000+)"
]

# Import benchmark MongoDB connector
try:
    from benchmark_db import (
        initialize_benchmarking_collection,
        save_benchmark_data,
        get_benchmark_data,
        get_peer_companies as db_get_peer_companies,
        get_framework_benchmarks,
        save_benchmark_assessment
    )
    logger.info("Benchmark MongoDB connector imported successfully")
    db_available = True
except ImportError:
    try:
        from frontend.benchmark_db import (
            initialize_benchmarking_collection,
            save_benchmark_data,
            get_benchmark_data,
            get_peer_companies as db_get_peer_companies,
            get_framework_benchmarks,
            save_benchmark_assessment
        )
        logger.info("Benchmark MongoDB connector imported successfully from frontend")
        db_available = True
    except ImportError:
        logger.warning("Benchmark MongoDB connector not found, using fallback functions")
        db_available = False
        
        # Define fallback functions if MongoDB module not available
        def initialize_benchmarking_collection():
            logger.warning("MongoDB not available, benchmarking collection not initialized")
            return False
            
        def save_benchmark_data(data):
            logger.warning("MongoDB not available, benchmark data not saved")
            return None
            
        def get_benchmark_data(company_id=None, framework=None, limit=100):
            logger.warning("MongoDB not available, returning empty benchmark data")
            return []
            
        def db_get_peer_companies(sector, region, size=None, limit=5):
            logger.warning("MongoDB not available, returning empty peer companies list")
            return []
            
        def get_framework_benchmarks(framework_id, sector=None, limit=50):
            logger.warning("MongoDB not available, returning empty framework benchmarks")
            return []
            
        def save_benchmark_assessment(company_id, assessment_data):
            logger.warning("MongoDB not available, assessment data not saved")
            return None

# Initialize benchmarking collection
try:
    if db_available:
        initialize_benchmarking_collection()
except Exception as e:
    logger.error(f"Error initializing benchmarking collection: {str(e)}")

# Create benchmarking collection function (for backward compatibility)
def benchmarking_collection():
    """
    Get the benchmarking collection from MongoDB
    
    Returns:
        Collection: MongoDB collection for benchmarking data
    """
    db = get_database()
    if db:
        return db.benchmarking
    return None

# Helper function to determine appropriate benchmarking framework
def determine_benchmarking_framework(company_data):
    """
    Determine the most appropriate benchmarking framework based on company data
    
    Args:
        company_data (dict): Company information including region, size, sector
        
    Returns:
        dict: Recommended frameworks with relevance scores
    """
    frameworks = {}
    
    # Get company attributes
    region = company_data.get('region', '').lower()
    size = company_data.get('size', '').lower()
    sector = company_data.get('sector', '').lower()
    
    # Check for EU region for CSRD relevance
    if 'eu' in region or 'europe' in region:
        frameworks["CSRD"] = {
            "relevance": 0.9 if 'large' in size or 'enterprise' in size else 0.6,
            "reason": "EU-based companies are subject to CSRD requirements"
        }
    else:
        frameworks["CSRD"] = {
            "relevance": 0.3,
            "reason": "Non-EU companies may need to align with CSRD for EU market access"
        }
    
    # TCFD relevant for all regions but especially financial sector
    if 'financial' in sector or 'banking' in sector or 'insurance' in sector:
        frameworks["TCFD"] = {
            "relevance": 0.95,
            "reason": "Financial institutions have specific TCFD disclosure requirements"
        }
    else:
        frameworks["TCFD"] = {
            "relevance": 0.7,
            "reason": "Climate-related financial disclosures relevant across sectors"
        }
    
    # SDG relevant for all companies
    frameworks["SDG"] = {
        "relevance": 0.8,
        "reason": "SDGs provide a universal framework for sustainability goals"
    }
    
    # VC Metrics more relevant for smaller companies and startups
    if 'startup' in size or 'small' in size:
        frameworks["VC_METRICS"] = {
            "relevance": 0.9,
            "reason": "Startup-focused metrics for early-stage sustainability reporting"
        }
    else:
        frameworks["VC_METRICS"] = {
            "relevance": 0.5,
            "reason": "VC metrics can complement other frameworks for established companies"
        }
    
    return frameworks

# Helper function to identify peer companies
def identify_peer_companies(company_data):
    """
    Identify peer companies for benchmarking comparison
    
    Args:
        company_data (dict): Company information including region, size, sector
        
    Returns:
        list: Peer companies with similarity scores
    """
    # In a real implementation, this would query a database of companies
    # For demo purposes, we'll generate sample peer companies
    
    sector = company_data.get('sector', 'Technology')
    region = company_data.get('region', 'EU')
    size = company_data.get('size', 'Medium (251-1000)')
    
    # Sample peer companies for each sector
    peer_companies = {
        "Technology": [
            {"name": "GreenTech Solutions", "similarity": 0.92, "region": "EU", "size": "Medium (251-1000)"},
            {"name": "EcoSoft Systems", "similarity": 0.87, "region": "EU", "size": "Medium (251-1000)"},
            {"name": "SustainableTech", "similarity": 0.85, "region": "North America", "size": "Medium (251-1000)"},
            {"name": "EnviroSystems", "similarity": 0.81, "region": "EU", "size": "Large (1001-5000)"},
            {"name": "GreenCode", "similarity": 0.79, "region": "Asia Pacific", "size": "Small (51-250)"}
        ],
        "Energy": [
            {"name": "RenewPower", "similarity": 0.94, "region": "EU", "size": "Large (1001-5000)"},
            {"name": "SolarFuture", "similarity": 0.90, "region": "EU", "size": "Medium (251-1000)"},
            {"name": "WindEnergy Co", "similarity": 0.88, "region": "North America", "size": "Large (1001-5000)"},
            {"name": "GreenGrid", "similarity": 0.85, "region": "EU", "size": "Medium (251-1000)"},
            {"name": "SustainPower", "similarity": 0.82, "region": "Asia Pacific", "size": "Medium (251-1000)"}
        ],
        "Manufacturing": [
            {"name": "EcoManufacturing", "similarity": 0.93, "region": "EU", "size": "Large (1001-5000)"},
            {"name": "GreenProduction", "similarity": 0.89, "region": "EU", "size": "Medium (251-1000)"},
            {"name": "SustainableMakers", "similarity": 0.87, "region": "North America", "size": "Medium (251-1000)"},
            {"name": "CircularFactory", "similarity": 0.84, "region": "EU", "size": "Large (1001-5000)"},
            {"name": "EcoFab", "similarity": 0.81, "region": "Asia Pacific", "size": "Small (51-250)"}
        ]
    }
    
    # Default to Technology if sector not found
    selected_peers = peer_companies.get(sector, peer_companies["Technology"])
    
    # Filter and adjust similarity based on region and size
    for peer in selected_peers:
        # Reduce similarity if region doesn't match
        if peer["region"] != region:
            peer["similarity"] -= 0.05
        
        # Reduce similarity if size doesn't match
        if peer["size"] != size:
            peer["similarity"] -= 0.03
            
        # Ensure similarity is between 0 and 1
        peer["similarity"] = max(0, min(1, peer["similarity"]))
        
        # Format similarity as percentage
        peer["similarity"] = round(peer["similarity"] * 100)
    
    # Sort by similarity (highest first)
    selected_peers = sorted(selected_peers, key=lambda x: x["similarity"], reverse=True)
    
    return selected_peers

# Helper function to generate required data points for a framework
def get_required_data_points(framework_id):
    """
    Get the required data points for a benchmarking framework
    
    Args:
        framework_id (str): Framework identifier
        
    Returns:
        list: Required data points for the framework
    """
    framework = REGULATORY_FRAMEWORKS.get(framework_id)
    if not framework:
        return []
    
    # Map framework key metrics to specific data points
    data_points_map = {
        "emissions": [
            {"id": "scope1_emissions", "name": "Scope 1 Emissions", "unit": "tCO2e", "category": "Environmental"},
            {"id": "scope2_emissions", "name": "Scope 2 Emissions", "unit": "tCO2e", "category": "Environmental"},
            {"id": "scope3_emissions", "name": "Scope 3 Emissions", "unit": "tCO2e", "category": "Environmental"}
        ],
        "energy": [
            {"id": "energy_consumption", "name": "Total Energy Consumption", "unit": "MWh", "category": "Environmental"},
            {"id": "renewable_energy", "name": "Renewable Energy Percentage", "unit": "%", "category": "Environmental"}
        ],
        "water": [
            {"id": "water_consumption", "name": "Water Consumption", "unit": "m³", "category": "Environmental"},
            {"id": "water_recycled", "name": "Water Recycled", "unit": "%", "category": "Environmental"}
        ],
        "biodiversity": [
            {"id": "biodiversity_impact", "name": "Biodiversity Impact Assessment", "unit": "Score", "category": "Environmental"}
        ],
        "social": [
            {"id": "diversity_score", "name": "Workforce Diversity", "unit": "Score", "category": "Social"},
            {"id": "gender_pay_gap", "name": "Gender Pay Gap", "unit": "%", "category": "Social"},
            {"id": "employee_turnover", "name": "Employee Turnover", "unit": "%", "category": "Social"}
        ],
        "governance": [
            {"id": "board_diversity", "name": "Board Diversity", "unit": "%", "category": "Governance"},
            {"id": "ethics_violations", "name": "Ethics Violations", "unit": "Count", "category": "Governance"}
        ],
        "economic": [
            {"id": "green_revenue", "name": "Green Revenue", "unit": "%", "category": "Economic"},
            {"id": "sustainable_investments", "name": "Sustainable Investments", "unit": "Currency", "category": "Economic"}
        ],
        "climate_risk": [
            {"id": "physical_risk_exposure", "name": "Physical Climate Risk Exposure", "unit": "Score", "category": "Risk"},
            {"id": "transition_risk_exposure", "name": "Transition Risk Exposure", "unit": "Score", "category": "Risk"}
        ],
        "emissions_intensity": [
            {"id": "emissions_per_revenue", "name": "Emissions per Revenue", "unit": "tCO2e/Currency", "category": "Environmental"},
            {"id": "emissions_per_employee", "name": "Emissions per Employee", "unit": "tCO2e/FTE", "category": "Environmental"}
        ],
        "renewable_percent": [
            {"id": "renewable_percentage", "name": "Renewable Energy Percentage", "unit": "%", "category": "Environmental"}
        ],
        "diversity": [
            {"id": "gender_diversity", "name": "Gender Diversity", "unit": "%", "category": "Social"},
            {"id": "ethnic_diversity", "name": "Ethnic Diversity", "unit": "%", "category": "Social"}
        ],
        "esg_risk_score": [
            {"id": "esg_risk_rating", "name": "ESG Risk Rating", "unit": "Score", "category": "Risk"}
        ],
        "green_revenue": [
            {"id": "green_revenue_percentage", "name": "Green Revenue Percentage", "unit": "%", "category": "Economic"}
        ]
    }
    
    # Collect all required data points for the framework's key metrics
    required_data_points = []
    for metric in framework.get("key_metrics", []):
        required_data_points.extend(data_points_map.get(metric, []))
    
    return required_data_points

# Helper function to generate sample benchmarking data
def generate_sample_benchmark_data(company_data, framework_id):
    """
    Generate sample benchmarking data for visualization
    
    Args:
        company_data (dict): Company information
        framework_id (str): Framework identifier
        
    Returns:
        dict: Benchmark data for visualization
    """
    company_name = company_data.get('name', 'Your Company')
    sector = company_data.get('sector', 'Technology')
    region = company_data.get('region', 'EU')
    
    # Get data points for this framework
    data_points = get_required_data_points(framework_id)
    
    # Generate random values for company and benchmark
    benchmark_data = {
        "company_name": company_name,
        "framework": REGULATORY_FRAMEWORKS.get(framework_id, {}).get("name", framework_id),
        "timestamp": datetime.now().isoformat(),
        "metrics": []
    }
    
    for data_point in data_points:
        # Generate random values for company and benchmarks
        your_value = random.randint(30, 100)
        industry_median = random.randint(30, 100)
        top_quartile = max(industry_median + random.randint(5, 20), 100)
        
        benchmark_data["metrics"].append({
            "id": data_point["id"],
            "name": data_point["name"],
            "unit": data_point["unit"],
            "category": data_point["category"],
            "your_value": your_value,
            "industry_median": industry_median,
            "top_quartile": top_quartile,
            "percentile": random.randint(1, 100)
        })
    
    return benchmark_data

# Helper function to generate insights from benchmarking data
def generate_benchmark_insights(benchmark_data):
    """
    Generate insights from benchmarking data
    
    Args:
        benchmark_data (dict): Benchmark data
        
    Returns:
        list: Insights from benchmark comparison
    """
    insights = []
    
    # Analyze metrics to generate insights
    for metric in benchmark_data.get("metrics", []):
        your_value = metric.get("your_value")
        industry_median = metric.get("industry_median")
        top_quartile = metric.get("top_quartile")
        percentile = metric.get("percentile")
        
        if your_value > top_quartile:
            insights.append({
                "metric": metric["name"],
                "type": "strength",
                "description": f"You are in the top quartile for {metric['name']}, outperforming most peers.",
                "recommendation": "Consider showcasing this strength in sustainability marketing materials."
            })
        elif your_value < industry_median:
            insights.append({
                "metric": metric["name"],
                "type": "gap",
                "description": f"Your {metric['name']} is below the industry median.",
                "recommendation": f"Consider developing strategies to improve {metric['name']}."
            })
        elif percentile > 70:
            insights.append({
                "metric": metric["name"],
                "type": "strength",
                "description": f"You are at the {percentile}th percentile for {metric['name']}.",
                "recommendation": "Maintain this strong performance."
            })
    
    # Limit to top 5 insights
    return insights[:5]

@benchmarking_bp.route('/')
def index():
    """Benchmarking Engine main page"""
    
    # Check if Gemini AI is available
    ai_available = gemini_controller is not None
    
    return render_template(
        'benchmarking/index.html',
        active_nav='benchmarking',
        ai_available=ai_available,
        regulatory_frameworks=REGULATORY_FRAMEWORKS,
        industry_sectors=INDUSTRY_SECTORS,
        regions=REGIONS,
        company_sizes=COMPANY_SIZES
    )

@benchmarking_bp.route('/framework-selector')
def framework_selector():
    """AI-powered framework selector"""
    
    return render_template(
        'benchmarking/framework_selector.html',
        active_nav='benchmarking',
        regulatory_frameworks=REGULATORY_FRAMEWORKS
    )

@benchmarking_bp.route('/peer-comparison')
def peer_comparison():
    """Peer comparison dashboard"""
    
    # Get framework parameter if provided
    framework_id = request.args.get('framework', 'CSRD')
    
    # Check if company data exists in session
    company_data = session.get('company_data', {})
    if not company_data:
        # Redirect to main page if no company data
        return redirect(url_for('benchmarking.index'))
    
    # Identify peer companies
    peer_companies = identify_peer_companies(company_data)
    
    # Generate benchmark data
    benchmark_data = generate_sample_benchmark_data(company_data, framework_id)
    
    # Generate insights
    insights = generate_benchmark_insights(benchmark_data)
    
    return render_template(
        'benchmarking/peer_comparison.html',
        active_nav='benchmarking',
        company_data=company_data,
        peer_companies=peer_companies,
        benchmark_data=benchmark_data,
        insights=insights,
        framework=REGULATORY_FRAMEWORKS.get(framework_id, {})
    )

@benchmarking_bp.route('/data-needs')
def data_needs():
    """Data needs panel for selected framework"""
    
    # Get framework parameter if provided
    framework_id = request.args.get('framework', 'CSRD')
    
    # Get required data points for the framework
    data_points = get_required_data_points(framework_id)
    
    return render_template(
        'benchmarking/data_needs.html',
        active_nav='benchmarking',
        framework=REGULATORY_FRAMEWORKS.get(framework_id, {}),
        data_points=data_points
    )

@benchmarking_bp.route('/document-upload', methods=['GET', 'POST'])
def document_upload():
    """Document upload for benchmarking data extraction"""
    
    if request.method == 'POST':
        # Process file upload
        if 'benchmark_file' not in request.files:
            return jsonify({"error": "No file part"}), 400
            
        file = request.files['benchmark_file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        if file:
            # Save file
            filename = secure_filename(file.filename)
            save_path = os.path.join('uploads', 'benchmarking', filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            file.save(save_path)
            
            # Store file info in session
            session['benchmark_file'] = {
                'filename': filename,
                'path': save_path,
                'uploaded_at': datetime.now().isoformat()
            }
            
            # Redirect to data extraction page
            return redirect(url_for('benchmarking.extract_data'))
    
    return render_template(
        'benchmarking/document_upload.html',
        active_nav='benchmarking'
    )

@benchmarking_bp.route('/extract-data')
def extract_data():
    """Data extraction from uploaded documents"""
    
    # Check if document file exists in session
    if 'benchmark_file' not in session:
        return redirect(url_for('benchmarking.document_upload'))
    
    # Get document file info
    benchmark_file = session['benchmark_file']
    
    # In a real implementation, this would extract data from the document
    # For demo purposes, we'll use sample data
    
    # Store extracted data in session
    if 'extracted_data' not in session:
        session['extracted_data'] = {
            'scope1_emissions': random.randint(1000, 5000),
            'scope2_emissions': random.randint(5000, 10000),
            'renewable_energy': random.randint(10, 50),
            'gender_diversity': random.randint(30, 50),
            'board_diversity': random.randint(20, 40),
            'esg_risk_rating': random.randint(10, 40)
        }
    
    return render_template(
        'benchmarking/extract_data.html',
        active_nav='benchmarking',
        benchmark_file=benchmark_file,
        extracted_data=session['extracted_data']
    )

@benchmarking_bp.route('/api/suggest-framework', methods=['POST'])
def api_suggest_framework():
    """API endpoint to suggest appropriate benchmarking framework"""
    
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Store company data in session
    session['company_data'] = {
        'name': data.get('company_name', 'Your Company'),
        'sector': data.get('sector', 'Technology'),
        'region': data.get('region', 'EU'),
        'size': data.get('size', 'Medium (251-1000)')
    }
    
    # Determine appropriate frameworks
    frameworks = determine_benchmarking_framework(session['company_data'])
    
    # Sort frameworks by relevance
    sorted_frameworks = sorted(
        [{"id": k, **v, **REGULATORY_FRAMEWORKS.get(k, {})} for k, v in frameworks.items()],
        key=lambda x: x["relevance"],
        reverse=True
    )
    
    return jsonify({
        "company": session['company_data'],
        "frameworks": sorted_frameworks
    })

@benchmarking_bp.route('/api/peer-companies', methods=['POST'])
def api_peer_companies():
    """API endpoint to identify peer companies for benchmarking"""
    
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    company_data = {
        'name': data.get('company_name', 'Your Company'),
        'sector': data.get('sector', 'Technology'),
        'region': data.get('region', 'EU'),
        'size': data.get('size', 'Medium (251-1000)')
    }
    
    # Identify peer companies
    peer_companies = identify_peer_companies(company_data)
    
    return jsonify({
        "company": company_data,
        "peers": peer_companies
    })

@benchmarking_bp.route('/api/benchmark-data', methods=['POST'])
def api_benchmark_data():
    """API endpoint to generate benchmark data for visualization"""
    
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    company_data = {
        'name': data.get('company_name', 'Your Company'),
        'sector': data.get('sector', 'Technology'),
        'region': data.get('region', 'EU'),
        'size': data.get('size', 'Medium (251-1000)')
    }
    
    framework_id = data.get('framework', 'CSRD')
    
    # Check if we should generate data or use existing data
    use_existing = data.get('use_existing', False)
    company_id = data.get('company_id', None)
    
    # Try to get existing benchmark data from MongoDB
    if use_existing and company_id:
        existing_data = get_benchmark_data(company_id=company_id, framework=framework_id, limit=1)
        if existing_data and len(existing_data) > 0:
            logger.info(f"Using existing benchmark data for company ID {company_id}")
            benchmark_data = existing_data[0]
            # Generate insights from existing data
            insights = generate_benchmark_insights(benchmark_data)
            return jsonify({
                "company": company_data,
                "benchmark_data": benchmark_data,
                "insights": insights,
                "source": "database"
            })
    
    # Generate new benchmark data
    benchmark_data = generate_sample_benchmark_data(company_data, framework_id)
    
    # Generate insights
    insights = generate_benchmark_insights(benchmark_data)
    
    # Save benchmark data to MongoDB
    if db_available:
        # Prepare document for storage
        storage_doc = {
            "company_id": data.get('company_id', str(uuid.uuid4())),
            "company_profile": company_data,
            "framework": framework_id,
            "benchmark_data": benchmark_data,
            "insights": insights
        }
        
        # Save to MongoDB
        doc_id = save_benchmark_data(storage_doc)
        if doc_id:
            logger.info(f"Benchmark data saved to MongoDB with ID: {doc_id}")
            benchmark_data["id"] = doc_id
    
    return jsonify({
        "company": company_data,
        "benchmark_data": benchmark_data,
        "insights": insights,
        "source": "generated"
    })

@benchmarking_bp.route('/api/framework-data-needs', methods=['GET'])
def api_framework_data_needs():
    """API endpoint to get data needs for a framework"""
    
    framework_id = request.args.get('framework', 'CSRD')
    
    # Get required data points for the framework
    data_points = get_required_data_points(framework_id)
    
    return jsonify({
        "framework": REGULATORY_FRAMEWORKS.get(framework_id, {}),
        "data_points": data_points
    })

@benchmarking_bp.route('/api/extract-document-data', methods=['POST'])
def api_extract_document_data():
    """API endpoint to extract data from uploaded documents"""
    
    # Check if file is included in request
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # In a real implementation, this would extract data from the document
    # For demo purposes, we'll return sample data
    
    extracted_data = {
        'scope1_emissions': random.randint(1000, 5000),
        'scope2_emissions': random.randint(5000, 10000),
        'renewable_energy': random.randint(10, 50),
        'gender_diversity': random.randint(30, 50),
        'board_diversity': random.randint(20, 40),
        'esg_risk_rating': random.randint(10, 40)
    }
    
    return jsonify({
        "status": "success",
        "filename": file.filename,
        "extracted_data": extracted_data
    })

@benchmarking_bp.route('/api/vc-benchmark-match', methods=['POST'])
def api_vc_benchmark_match():
    """API endpoint to match startup profile to VC expectations"""
    
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    company_name = data.get('company_name', 'Sample Startup')
    sector = data.get('sector', 'Technology')
    
    # Generate VC fit scores
    vc_matches = [
        {
            "vc_name": "Mentha Capital",
            "fit_score": random.randint(70, 95),
            "strengths": [
                "Mid-cap positioning",
                "Circular economy focus",
                "CSRD readiness"
            ],
            "gaps": [
                "Limited global expansion strategy",
                "Moderate social impact metrics"
            ]
        },
        {
            "vc_name": "IK Partners",
            "fit_score": random.randint(60, 90),
            "strengths": [
                "Strong governance framework",
                "Carbon reduction initiatives",
                "Nordic market experience"
            ],
            "gaps": [
                "Limited diversity metrics",
                "Modest innovation pipeline"
            ]
        },
        {
            "vc_name": "Sustainable Growth Fund",
            "fit_score": random.randint(50, 85),
            "strengths": [
                "Renewable technology focus",
                "Circular economy initiatives",
                "Strong stakeholder engagement"
            ],
            "gaps": [
                "Incomplete Scope 3 emissions data",
                "Limited water stress management"
            ]
        }
    ]
    
    return jsonify({
        "company": company_name,
        "sector": sector,
        "timestamp": datetime.now().isoformat(),
        "vc_matches": vc_matches
    })

def register_blueprint(app):
    """
    Register benchmarking routes with the application
    
    Args:
        app: Flask application
    """
    app.register_blueprint(benchmarking_bp)
    logger.info("Benchmarking Engine blueprint registered successfully")