"""
VC/PE Analysis Routes
"""
from flask import Blueprint, render_template, jsonify
from services.trendsense.vc_pe.data_manager import DataManager
from services.trendsense.vc_pe.data import generate_portfolio_metrics, generate_company_benchmarks, generate_sustainability_insights

# Create blueprint
vc_pe_bp = Blueprint('vc_pe', __name__)

# Initialize data manager
data_manager = DataManager()

@vc_pe_bp.route('/')
def index():
    """Render the VC/PE analysis dashboard"""
    return render_template('vc_pe/dashboard.html')

@vc_pe_bp.route('/api/metrics')
def get_metrics():
    """Get portfolio metrics"""
    metrics = generate_portfolio_metrics()
    return jsonify(metrics)

@vc_pe_bp.route('/api/benchmarks')
def get_benchmarks():
    """Get company benchmarks"""
    benchmarks = generate_company_benchmarks()
    return jsonify(benchmarks)

@vc_pe_bp.route('/api/insights')
def get_insights():
    """Get sustainability insights"""
    insights = generate_sustainability_insights()
    return jsonify(insights)

# Core VC/PE Pages
@vc_pe_bp.route('/portfolio')
def portfolio_analysis():
    """Portfolio company sustainability analysis"""
    return render_template('vc_pe/portfolio.html',
                         metrics=generate_portfolio_metrics(),
                         insights=generate_sustainability_insights())

@vc_pe_bp.route('/pipeline')
def investment_pipeline():
    """Sustainability-focused deal pipeline"""
    return render_template('vc_pe/pipeline.html')

# Specialized Tools
@vc_pe_bp.route('/pdf-analyzer')
def vc_pe_pdf_analyzer():
    """VC/PE specific document analysis tool"""
    return render_template('vc_pe/pdf_analyzer.html')

@vc_pe_bp.route('/co-pilot')
def vc_pe_copilot():
    """VC/PE specific AI assistant"""
    return render_template('vc_pe/copilot.html')

# Debug Routes
@vc_pe_bp.route('/debug/vc-pe')
def debug_vc_pe():
    """Debug route for VC/PE features"""
    return jsonify({
        "status": "ok",
        "routes": [
            "/dashboard",
            "/portfolio",
            "/pipeline",
            "/api/metrics",
            "/api/benchmarks",
            "/api/insights"
        ]
    }) 