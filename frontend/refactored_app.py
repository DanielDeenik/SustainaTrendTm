"""
SustainaTrend Intelligence Platform - Refactored Application

This is a refactored, consolidated version of the platform that handles all functionality
on a single port with clean organization and no standalone components.
"""
import os
import sys
import json
import logging
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, g, Blueprint, redirect, url_for, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_consolidated')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# Apply ProxyFix middleware for reverse proxy environments
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# ===========================================================================
# GLOBAL DATA (would normally be served from a database)
# ===========================================================================

# Frameworks
FRAMEWORKS = {
    'CSRD': {'name': 'Corporate Sustainability Reporting Directive', 'regions': ['EU']},
    'ESRS': {'name': 'European Sustainability Reporting Standards', 'regions': ['EU']},
    'SFDR': {'name': 'Sustainable Finance Disclosure Regulation', 'regions': ['EU']},
    'TCFD': {'name': 'Task Force on Climate-related Financial Disclosures', 'regions': ['Global']},
    'GRI': {'name': 'Global Reporting Initiative', 'regions': ['Global']},
    'SASB': {'name': 'Sustainability Accounting Standards Board', 'regions': ['US']},
    'CDP': {'name': 'Carbon Disclosure Project', 'regions': ['Global']},
    'SDG': {'name': 'UN Sustainable Development Goals', 'regions': ['Global']}
}

# Stats for the dashboard
DASHBOARD_STATS = {
    'documents_count': 12,
    'document_growth': '24%',
    'frameworks_count': 7,
    'recent_framework': 'EU CSRD',
    'avg_compliance': '78%',
    'analysis_count': 48,
    'analysis_growth': '18%'
}

# Recent documents
RECENT_DOCUMENTS = [
    {
        'title': 'Company XYZ Sustainability Report 2025',
        'date': 'Mar 24, 2025',
        'framework': 'EU CSRD',
        'score': 92,
        'status': 'Compliant',
        'preview': 'This sustainability report outlines our commitment to environmental stewardship and social responsibility...'
    },
    {
        'title': 'Environmental Impact Statement Q1',
        'date': 'Mar 18, 2025',
        'framework': 'GRI',
        'score': 78,
        'status': 'Needs Review',
        'preview': 'We have made significant progress in reducing our carbon footprint through innovative technologies...'
    },
    {
        'title': 'Climate Risk Disclosure',
        'date': 'Mar 10, 2025',
        'framework': 'TCFD',
        'score': 65,
        'status': 'Incomplete',
        'preview': 'This document presents our comprehensive analysis of climate-related risks and their potential impacts...'
    }
]

# Recent activity
RECENT_ACTIVITY = [
    {
        'action': 'Document Uploaded',
        'details': 'Sustainability Report 2025',
        'time': '2 hours ago',
        'user': 'John D.'
    },
    {
        'action': 'Analysis Completed',
        'details': 'Climate Risk Disclosure',
        'time': '4 hours ago',
        'user': 'System'
    },
    {
        'action': 'Framework Added',
        'details': 'Added ISSB framework support',
        'time': '1 day ago',
        'user': 'Admin'
    }
]

# ===========================================================================
# HELPER FUNCTIONS 
# ===========================================================================

def get_api_status():
    """Get the current status of all API services"""
    # Check if Pinecone API key is available
    pinecone_status = 'online' if os.environ.get('PINECONE_API_KEY') else 'offline'
    
    # API status with real checks where possible
    return {
        'fastapi': {'status': 'online', 'url': 'http://localhost:8080'},
        'flask': {'status': 'online', 'url': 'http://localhost:5000'},
        'pinecone': {'status': pinecone_status, 'url': 'api.pinecone.io'}
    }

def get_theme_preference():
    """Get user's theme preference from cookie or default to 'light'"""
    return request.cookies.get('theme', 'light')

# ===========================================================================
# GLOBAL CONTEXT PROCESSOR - injects variables into all templates
# ===========================================================================

@app.context_processor
def inject_global_vars():
    """Inject global variables into all templates"""
    return {
        'api_status': get_api_status(),
        'theme': get_theme_preference()
    }

# ===========================================================================
# MAIN ROUTES
# ===========================================================================

@app.route('/')
def home():
    """Home page redirects to Regulatory AI Dashboard for simplicity"""
    return redirect('/regulatory/dashboard')

# ===========================================================================
# REGULATORY AI ROUTES
# ===========================================================================

@app.route('/regulatory/dashboard')
def regulatory_dashboard():
    """Regulatory AI Dashboard - the main dashboard for regulatory compliance"""
    logger.info("Regulatory dashboard accessed")
    
    # Create navigation context
    navigation = {
        'main_dashboard': '/',
        'regulatory_dashboard': '/regulatory/dashboard',
        'document_upload': '/regulatory/upload'
    }
    
    return render_template(
        'regulatory/dashboard_refactored.html',
        active_nav='regulatory',
        page_title="Regulatory AI Dashboard",
        stats=DASHBOARD_STATS,
        recent_documents=RECENT_DOCUMENTS,
        recent_activity=RECENT_ACTIVITY,
        navigation=navigation
    )

@app.route('/regulatory/upload')
def regulatory_upload():
    """Document upload page for regulatory compliance"""
    logger.info("Document upload page accessed")
    
    # Check if Pinecone is available for RAG functionality
    pinecone_available = bool(os.environ.get('PINECONE_API_KEY'))
    
    return render_template(
        'regulatory/upload_refactored.html',
        active_nav='regulatory',
        page_title="Document Upload",
        frameworks=FRAMEWORKS,
        is_rag_available=pinecone_available
    )

@app.route('/regulatory/api/upload', methods=['POST'])
def regulatory_upload_api():
    """API endpoint for document upload"""
    try:
        # Check if file is in the request
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Generate a unique ID for the document
        document_id = str(uuid.uuid4())
        
        # Get framework selection
        framework = request.form.get('framework', 'unknown')
        
        # Create uploads directory if it doesn't exist
        uploads_dir = os.path.join(app.static_folder, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(uploads_dir, f"{document_id}_{file.filename}")
        file.save(file_path)
        
        logger.info(f"File uploaded: {file.filename}, ID: {document_id}, Framework: {framework}")
        
        # Return success with document ID
        return jsonify({
            "success": True,
            "document_id": document_id,
            "filename": file.filename,
            "framework": framework,
            "next_url": f"/regulatory/analysis?document_id={document_id}"
        })
    
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        return jsonify({"error": f"Error uploading document: {str(e)}"}), 500

@app.route('/regulatory/analysis')
def regulatory_analysis():
    """Document analysis page"""
    document_id = request.args.get('document_id')
    if not document_id:
        return redirect('/regulatory/upload')
    
    # In a real app, we would retrieve document info from database
    # For now, just use mock data
    document_info = {
        'id': document_id,
        'title': 'Uploaded Document',
        'framework': request.args.get('framework', 'CSRD'),
        'upload_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'Processing'
    }
    
    return render_template(
        'regulatory/analysis.html',
        active_nav='regulatory',
        page_title="Document Analysis",
        document=document_info
    )

# ===========================================================================
# API ROUTES
# ===========================================================================

@app.route('/api/frameworks')
def api_frameworks():
    """API endpoint for supported frameworks"""
    frameworks_list = [
        {"id": key, "name": value['name'], "regions": value['regions']} 
        for key, value in FRAMEWORKS.items()
    ]
    return jsonify(frameworks_list)

@app.route('/api/compliance-data')
def api_compliance_data():
    """API endpoint for compliance data"""
    compliance_data = {
        "labels": ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar"],
        "datasets": [
            {
                "label": "EU CSRD",
                "data": [65, 68, 70, 72, 75, 78]
            },
            {
                "label": "TCFD",
                "data": [55, 59, 65, 70, 73, 76]
            },
            {
                "label": "GRI",
                "data": [60, 62, 65, 68, 70, 74]
            }
        ]
    }
    return jsonify(compliance_data)

@app.route('/api/analysis-data')
def api_analysis_data():
    """API endpoint for analysis data"""
    analysis_data = {
        "labels": ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar"],
        "datasets": [
            {
                "label": "Gap Analyses",
                "data": [8, 12, 15, 18, 22, 28]
            },
            {
                "label": "RAG Queries",
                "data": [15, 18, 22, 30, 35, 42]
            }
        ]
    }
    return jsonify(analysis_data)

# ===========================================================================
# STATIC FILES
# ===========================================================================

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory(app.static_folder, path)

# ===========================================================================
# ERROR HANDLERS
# ===========================================================================

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('error.html', error_code=404, error_message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('error.html', error_code=500, error_message="Internal server error"), 500

# ===========================================================================
# MAIN ENTRY POINT
# ===========================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))  # Changed to 3000 to avoid conflict
    logger.info(f"Starting consolidated application on port {port}")
    logger.info(f"Template folder: {app.template_folder}")
    logger.info(f"Static folder: {app.static_folder}")
    
    # Handle Werkzeug server FD error
    if 'WERKZEUG_SERVER_FD' in os.environ:
        try:
            app.run(debug=True)
        except Exception as e:
            logger.error(f"Error using WERKZEUG_SERVER_FD: {str(e)}")
            # Remove the environment variable and try again
            del os.environ['WERKZEUG_SERVER_FD']
            app.run(host='0.0.0.0', port=port, debug=True)
    else:
        # Normal startup
        app.run(host='0.0.0.0', port=port, debug=True)