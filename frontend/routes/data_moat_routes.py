"""
Data Moat Routes for SustainaTrend™

This module provides routes for the data moat functionality, including
enhanced document upload, processing, and analysis interfaces.
"""

import os
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from flask import (
    Blueprint, render_template, request, jsonify, current_app,
    send_from_directory, session, redirect, url_for
)
from werkzeug.utils import secure_filename

# Import our enhanced document processor
try:
    from frontend.data_moat.enhanced_processor import EnhancedDocumentProcessor
    # Create an instance of the processor
    enhanced_processor = EnhancedDocumentProcessor()
    ENHANCED_PROCESSOR_AVAILABLE = True
except ImportError:
    ENHANCED_PROCESSOR_AVAILABLE = False
    enhanced_processor = None
    logging.error("Enhanced document processor not available, check imports")

# Import database connector
try:
    from frontend.data_moat.db_connector import db_connector
    DB_CONNECTOR_AVAILABLE = True
except ImportError:
    DB_CONNECTOR_AVAILABLE = False
    logging.error("Database connector not available, check imports")

# Configure logging
logger = logging.getLogger(__name__)

# Define constants
UPLOAD_FOLDER = os.path.join('frontend', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'csv', 'xlsx'}

# Create blueprint
data_moat_bp = Blueprint('data_moat', __name__, url_prefix='/data-moat')

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename: str) -> bool:
    """
    Check if the file has an allowed extension
    
    Args:
        filename: Name of the file
        
    Returns:
        True if the file has an allowed extension, False otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@data_moat_bp.route('/')
def index():
    """Data Moat Interface dashboard"""
    return render_template('data_moat/index.html')

@data_moat_bp.route('/upload', methods=['GET', 'POST'])
def document_upload():
    """
    Document upload interface with enhanced processing
    
    This route provides a drag-and-drop interface for document upload
    with a checklist-style progress indicator and enhanced processing.
    """
    if request.method == 'GET':
        # Get available frameworks for auto-detection
        frameworks = [
            {'id': 'esrs', 'name': 'European Sustainability Reporting Standards (ESRS)'},
            {'id': 'csrd', 'name': 'Corporate Sustainability Reporting Directive (CSRD)'},
            {'id': 'gri', 'name': 'Global Reporting Initiative (GRI)'},
            {'id': 'tcfd', 'name': 'Task Force on Climate-related Financial Disclosures (TCFD)'},
            {'id': 'sfdr', 'name': 'Sustainable Finance Disclosure Regulation (SFDR)'},
            {'id': 'sdg', 'name': 'Sustainable Development Goals (SDG)'},
            {'id': 'sasb', 'name': 'Sustainability Accounting Standards Board (SASB)'}
        ]
        
        return render_template(
            'data_moat/upload.html',
            frameworks=frameworks,
            enhanced_processing=ENHANCED_PROCESSOR_AVAILABLE
        )
    
    elif request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Process form data
        use_ocr = request.form.get('use_ocr', 'false').lower() == 'true'
        auto_detect_framework = request.form.get('auto_detect_framework', 'true').lower() == 'true'
        document_type = request.form.get('document_type', 'sustainability_report')
        
        # Generate a unique document ID
        document_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        # Secure filename and save to uploads directory
        filename = secure_filename(file.filename)
        saved_name = f"{timestamp}-{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, saved_name)
        
        # Save the file
        file.save(filepath)
        logger.info(f"Saved uploaded file to {filepath}")
        
        # Process the file with enhanced document processor if available
        if ENHANCED_PROCESSOR_AVAILABLE:
            logger.info(f"Processing document with enhanced processor: {filepath}")
            logger.info(f"OCR: {use_ocr}, Auto-detect framework: {auto_detect_framework}, Type: {document_type}")
            
            result = enhanced_processor.process_document(
                filepath,
                use_ocr=use_ocr,
                auto_detect_framework=auto_detect_framework,
                document_type=document_type
            )
            
            if not result.get('success', False):
                logger.error(f"Error processing document: {result.get('error')}")
                
                # Clean up the uploaded file
                if os.path.exists(filepath):
                    os.remove(filepath)
                
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Unknown error during document processing')
                }), 500
            
            # Store result in session for later use
            session['document_data'] = {
                'document_id': result.get('document_id'),
                'filename': saved_name,
                'original_name': filename,
                'timestamp': timestamp,
                'path': filepath,
                'metrics_count': result.get('metrics_count', 0),
                'frameworks_detected': result.get('frameworks_detected', {}),
                'primary_framework': result.get('primary_framework', ''),
                'confidence_score': result.get('confidence_score', 0.0)
            }
            
            # Return processing results
            return jsonify({
                'success': True,
                'document_id': result.get('document_id'),
                'metrics_count': result.get('metrics_count', 0),
                'frameworks_detected': result.get('frameworks_detected', {}),
                'primary_framework': result.get('primary_framework', ''),
                'confidence_score': result.get('confidence_score', 0.0),
                'redirect_url': url_for('data_moat.document_analysis', document_id=result.get('document_id'))
            })
        
        else:
            logger.warning("Enhanced processor not available, using fallback")
            
            # Store basic info in session
            session['document_data'] = {
                'document_id': document_id,
                'filename': saved_name,
                'original_name': filename,
                'timestamp': timestamp,
                'path': filepath
            }
            
            # Return basic processing info
            return jsonify({
                'success': True,
                'document_id': document_id,
                'message': 'Document uploaded successfully, but enhanced processing is not available',
                'redirect_url': url_for('data_moat.document_analysis', document_id=document_id)
            })

@data_moat_bp.route('/analysis/<document_id>')
def document_analysis(document_id):
    """
    Document analysis interface with enriched data
    
    This route provides an interface for viewing the enriched data
    extracted from a document, including metrics, framework mapping,
    and compliance assessment.
    """
    # Check if we have document data in session
    if 'document_data' not in session or session['document_data'].get('document_id') != document_id:
        # Try to get document from database if DB connector is available
        if DB_CONNECTOR_AVAILABLE:
            try:
                document_data = db_connector.get_document_by_id(document_id)
                if document_data:
                    return render_template(
                        'data_moat/analysis.html',
                        document_id=document_id,
                        document_data=document_data
                    )
            except Exception as e:
                logger.error(f"Error retrieving document from database: {str(e)}")
        
        # If we can't find the document, redirect to upload page
        return redirect(url_for('data_moat.document_upload'))
    
    # Render analysis template with document data from session
    return render_template(
        'data_moat/analysis.html',
        document_id=document_id,
        document_data=session['document_data']
    )

@data_moat_bp.route('/api/metrics/<document_id>')
def api_metrics(document_id):
    """
    API endpoint for extracted metrics
    
    Returns standardized sustainability metrics extracted from the document.
    """
    if not DB_CONNECTOR_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Database connector not available'
        }), 500
    
    try:
        # Query metrics from database
        # This would be implemented in the DB connector
        metrics = []  # db_connector.get_metrics_for_document(document_id)
        
        return jsonify({
            'success': True,
            'document_id': document_id,
            'metrics': metrics
        })
    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@data_moat_bp.route('/api/compliance/<document_id>')
def api_compliance(document_id):
    """
    API endpoint for compliance assessment
    
    Returns the compliance assessment results for the document.
    """
    if not DB_CONNECTOR_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Database connector not available'
        }), 500
    
    try:
        # Query compliance assessments from database
        # This would be implemented in the DB connector
        compliance = []  # db_connector.get_compliance_for_document(document_id)
        
        return jsonify({
            'success': True,
            'document_id': document_id,
            'compliance': compliance
        })
    except Exception as e:
        logger.error(f"Error retrieving compliance assessment: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@data_moat_bp.route('/api/document/<document_id>')
def api_document(document_id):
    """
    API endpoint for document data
    
    Returns the document data with enriched information.
    """
    if not DB_CONNECTOR_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Database connector not available'
        }), 500
    
    try:
        # Query document from database
        document = db_connector.get_document_by_id(document_id)
        
        if not document:
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404
        
        return jsonify({
            'success': True,
            'document': document
        })
    except Exception as e:
        logger.error(f"Error retrieving document: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@data_moat_bp.route('/api/process-status/<document_id>')
def api_process_status(document_id):
    """
    API endpoint for document processing status
    
    Returns the current processing status of the document.
    This endpoint is used for the frontend to update the progress indicator.
    """
    if not DB_CONNECTOR_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Database connector not available'
        }), 500
    
    try:
        # Query document from database
        document = db_connector.get_document_by_id(document_id)
        
        if not document:
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404
        
        # Extract processing status
        processing_status = document.get('processing_status', 'unknown')
        
        # Get enrichment history for progress details
        enrichment_history = document.get('enrichment_history', [])
        
        return jsonify({
            'success': True,
            'document_id': document_id,
            'status': processing_status,
            'enrichment_history': enrichment_history
        })
    except Exception as e:
        logger.error(f"Error retrieving processing status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def register_routes(app):
    """Register data moat routes with the Flask application"""
    app.register_blueprint(data_moat_bp)
    logger.info("Data Moat routes registered")