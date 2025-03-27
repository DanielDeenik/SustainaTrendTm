"""
Document routes for the SustainaTrend Intelligence Platform.
Handles document upload, analysis, and visualization.
"""

import os
import json
import uuid
import logging
from typing import Dict, List, Tuple, Any, Optional

# Create logger
logger = logging.getLogger(__name__)

# Flask imports
from flask import Blueprint, render_template, request, jsonify, current_app, send_from_directory, flash, redirect, url_for
from werkzeug.utils import secure_filename

# Create blueprint
document_bp = Blueprint('documents', __name__, url_prefix='/documents')

# Create a root-level blueprint for direct document upload access
# This handles the /document-upload route at the root level
document_root_bp = Blueprint('document_root', __name__)

# Import regulatory AI agent for document analysis
try:
    from regulatory_ai_agent import RegulatoryAIAgent
    regulatory_ai = RegulatoryAIAgent()
    logger.info("Regulatory AI agent initialized successfully")
except Exception as e:
    regulatory_ai = None
    logger.error(f"Failed to initialize Regulatory AI agent: {e}")

# AI service functions
def analyze_document_text(document_text: str, frameworks: List[str] = None) -> Dict[str, Any]:
    """
    Analyze document text for regulatory compliance
    
    Args:
        document_text: The text content of the document
        frameworks: Optional list of regulatory frameworks to analyze against
        
    Returns:
        Dictionary containing analysis results
    """
    if frameworks is None:
        frameworks = ["CSRD", "ESRS", "TCFD", "SFDR"]
    
    try:
        if regulatory_ai:
            return regulatory_ai.analyze_document(document_text, frameworks)
        else:
            # Return simulated data for development
            return {
                "frameworks": {
                    "CSRD": {"score": 78, "level": "high"},
                    "ESRS E4": {"score": 23, "level": "low"},
                    "TCFD": {"score": 65, "level": "medium"},
                    "SFDR": {"score": 86, "level": "high"}
                },
                "summary": "Document has strong CSRD compliance overall, with excellent coverage of social metrics and climate-related disclosures. However, biodiversity reporting falls significantly below industry averages and regulatory requirements.",
                "gaps": ["Biodiversity disclosures", "Ecosystem impact assessment"],
                "recommendations": ["Add biodiversity impact assessments", "Increase species protection metrics"]
            }
    except Exception as e:
        logger.error(f"Error analyzing document: {e}")
        return {"error": str(e)}

def generate_insights(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate insights from document analysis results
    
    Args:
        analysis_results: Results from document analysis
        
    Returns:
        Dictionary containing generated insights
    """
    try:
        # In production, this would use AI to generate insights
        # For now we'll return mock insights
        return {
            "key_findings": [
                "Strong overall CSRD compliance at 78%",
                "Significant biodiversity disclosure gap at only 23% compliance",
                "Climate-related disclosures meet TCFD requirements at 65%"
            ],
            "action_items": [
                "Develop biodiversity impact assessment",
                "Add species protection metrics to sustainability reporting",
                "Enhance climate transition plan with more specific targets"
            ]
        }
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        return {"error": str(e)}

def process_document(file) -> Tuple[bool, str, Optional[str]]:
    """
    Process an uploaded document
    
    Args:
        file: The uploaded file object
        
    Returns:
        Tuple containing (success, message, document_id)
    """
    if not file:
        return False, "No file provided", None
    
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(current_app.root_path, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Secure the filename and save the file
        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Generate a unique ID for the document
        document_id = str(uuid.uuid4())
        
        # In a real implementation, we would process the document,
        # extract text, and store it in a database
        
        return True, "Document uploaded successfully", document_id
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        return False, f"Error processing document: {str(e)}", None

# Routes
@document_bp.route('/')
def document_hub():
    """Render the document hub page"""
    return render_template('document_hub_redesign.html')

@document_bp.route('/document-upload')
def document_upload():
    """Alternative route for document upload page"""
    return render_template('document_hub_redesign.html')
    
# Root-level document upload route
@document_root_bp.route('/document-upload')
def root_document_upload():
    """Root-level route for document upload page"""
    return render_template('document_hub_redesign.html')
    
@document_bp.route('/upload', methods=['GET'])
def upload_page():
    """GET route for document upload page"""
    return render_template('document_hub_redesign.html')

@document_bp.route('/upload', methods=['POST'])
def upload_document():
    """Handle document upload"""
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No selected file"}), 400
    
    success, message, document_id = process_document(file)
    return jsonify({
        "success": success,
        "message": message,
        "document_id": document_id
    })

@document_bp.route('/paste', methods=['POST'])
def paste_document():
    """Handle pasted document text"""
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"success": False, "message": "No text provided"}), 400
    
    document_text = data['text']
    document_id = str(uuid.uuid4())
    
    # In a real implementation, we would store the text in a database
    # For now, just return success
    return jsonify({
        "success": True,
        "message": "Document text processed successfully",
        "document_id": document_id
    })

@document_bp.route('/analyze/<document_id>', methods=['GET'])
def analyze_document(document_id):
    """Analyze a document and return results"""
    # In a real implementation, we would retrieve the document from a database
    # For now, just return simulated analysis
    analysis = analyze_document_text("Sample document text")
    return jsonify(analysis)

@document_bp.route('/insights/<document_id>', methods=['GET'])
def get_document_insights(document_id):
    """Get insights for a document"""
    # In a real implementation, we would retrieve analysis from a database
    # For now, generate insights from simulated analysis
    analysis = analyze_document_text("Sample document text")
    insights = generate_insights(analysis)
    return jsonify(insights)

@document_bp.route('/view/<document_id>', methods=['GET'])
def view_document(document_id):
    """View a document"""
    # In a real implementation, we would retrieve the document from a database
    # and display it in a document viewer
    return render_template('document_viewer.html', document_id=document_id)

# Register blueprint with the application
def register_routes(app):
    """Register document routes with the Flask application"""
    app.register_blueprint(document_bp)
    app.register_blueprint(document_root_bp)
    logger.info("Document routes registered successfully (including root-level routes)")