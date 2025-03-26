"""
Standalone Dashboard Module for Regulatory AI

This module provides a standalone dashboard for the Regulatory AI module
designed to overcome routing issues in Replit's environment.
"""

import os
import sys
import logging
from flask import Flask, render_template, send_from_directory, request, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
logger = logging.getLogger(__name__)

# Set the current directory as part of Python's path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)  # Add the current directory to Python's path
root_dir = os.path.dirname(current_dir)  # Get the parent directory
sys.path.insert(0, root_dir)  # Add the parent directory to Python's path

logger.info(f"Current directory: {current_dir}")
logger.info(f"Root directory: {root_dir}")
logger.info(f"Python path: {sys.path}")
logger.info(f"Current working directory: {os.getcwd()}")

# Initialize Flask app
app = Flask(__name__, 
           template_folder=os.path.join(current_dir, 'templates'),
           static_folder=os.path.join(current_dir, 'static'))

logger.info(f"Template folder: {os.path.join(current_dir, 'templates')}")
logger.info(f"Static folder: {os.path.join(current_dir, 'static')}")

# Sample data for the dashboard
stats = {
    'documents_count': 12,
    'document_growth': '24%',
    'frameworks_count': 7,
    'recent_framework': 'EU CSRD',
    'avg_compliance': '74%',
    'analysis_count': 48,
    'analysis_growth': '18%'
}

recent_documents = [
    {
        'id': '001',
        'name': 'SustainaCorp Annual Report 2024',
        'type': 'PDF',
        'size': '12.3 MB',
        'date_added': '2025-03-18',
        'framework': 'CSRD'
    },
    {
        'id': '002',
        'name': 'GreenTech Sustainability Report',
        'type': 'PDF',
        'size': '8.7 MB',
        'date_added': '2025-03-15',
        'framework': 'GRI'
    },
    {
        'id': '003',
        'name': 'EcoFinance TCFD Disclosure',
        'type': 'DOCX',
        'size': '4.2 MB',
        'date_added': '2025-03-10',
        'framework': 'TCFD'
    }
]

recent_activity = [
    {
        'id': '001',
        'type': 'analysis',
        'name': 'CSRD Gap Analysis',
        'date': '2025-03-20',
        'user': 'AI System',
        'status': 'Completed'
    },
    {
        'id': '002',
        'type': 'upload',
        'name': 'GreenTech Sustainability Report',
        'date': '2025-03-15',
        'user': 'System',
        'status': 'Processed'
    },
    {
        'id': '003',
        'type': 'query',
        'name': 'Emissions Reduction Target Query',
        'date': '2025-03-12',
        'user': 'AI System',
        'status': 'Answered'
    }
]

def get_api_status():
    """Get the current status of all API services"""
    # Check if Pinecone API key is available
    pinecone_status = 'online' if os.environ.get('PINECONE_API_KEY') else 'offline'
    
    # Mock API status for standalone dashboard
    return {
        'fastapi': {'status': 'online', 'url': 'http://localhost:8080'},
        'flask': {'status': 'online', 'url': 'http://localhost:5000'},
        'storytelling': {'status': 'online', 'url': 'http://localhost:8081'},
        'mongodb': {'status': 'offline', 'url': 'mongodb://localhost:27017'},
        'pinecone': {'status': pinecone_status, 'url': 'api.pinecone.io'},
        'redis': {'status': 'offline', 'url': 'redis://localhost:6379'},
        'standalone_dashboard': {'status': 'online', 'url': f'http://localhost:{port}'},
    }

@app.route('/')
def index():
    """Render the dashboard page"""
    logger.info("Dashboard accessed")
    # Mock theme preference for standalone dashboard
    theme_preference = 'dark'
    
    # Create navigation context for standalone mode
    navigation = {
        'main_dashboard': 'http://localhost:5000/',
        'strategy_hub': 'http://localhost:5000/strategy-hub',
        'regulatory_dashboard': 'http://localhost:6000/',
        'document_upload': 'http://localhost:5000/regulatory-ai-refactored/upload',
        'standalone': True
    }
    
    return render_template(
        'regulatory/dashboard_refactored.html',
        active_nav='regulatory-ai-refactored',
        page_title="Regulatory AI Dashboard (Standalone)",
        stats=stats,
        recent_documents=recent_documents,
        recent_activity=recent_activity,
        api_status=get_api_status(),
        theme=theme_preference,
        navigation=navigation
    )

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    logger.info(f"Serving static file: {path}")
    return send_from_directory(os.path.join(current_dir, 'static'), path)

@app.route('/api/frameworks')
def api_frameworks():
    """API endpoint for supported frameworks"""
    frameworks = [
        {"id": "CSRD", "name": "EU Corporate Sustainability Reporting Directive", "count": 5},
        {"id": "TCFD", "name": "Task Force on Climate-related Financial Disclosures", "count": 3},
        {"id": "GRI", "name": "Global Reporting Initiative", "count": 4},
        {"id": "SASB", "name": "Sustainability Accounting Standards Board", "count": 2},
        {"id": "SFDR", "name": "Sustainable Finance Disclosure Regulation", "count": 1},
        {"id": "SDG", "name": "UN Sustainable Development Goals", "count": 3},
        {"id": "CDP", "name": "Carbon Disclosure Project", "count": 2}
    ]
    return jsonify(frameworks)

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6000))
    app.run(host='0.0.0.0', port=port, debug=True)