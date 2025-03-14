"""
Document Processing Routes for SustainaTrend™ Platform

This module provides routes for document upload, processing, and analysis
with a focus on sustainability reports and ESG disclosures.
"""

import os
import traceback
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from flask import Blueprint, render_template, request, jsonify, session, url_for
from werkzeug.utils import secure_filename

# Import document processor
try:
    from document_processor import DocumentProcessor
    DOCUMENT_PROCESSOR_AVAILABLE = True
    document_processor = DocumentProcessor()
    logging.info("Document processor loaded successfully")
except ImportError as e:
    DOCUMENT_PROCESSOR_AVAILABLE = False
    document_processor = None
    logging.warning(f"Document processor not available: {str(e)}")

# For navigation
try:
    from navigation_config import get_context_for_template
except ImportError:
    # Fallback if navigation is not available
    def get_context_for_template():
        return {}

# Create document processing blueprint
document_bp = Blueprint('document', __name__)

# Configure logging
logger = logging.getLogger(__name__)

# Configure uploads
ALLOWED_EXTENSIONS = {'pdf'}
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')

# Create upload directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Check if a file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@document_bp.route('/document-hub')
def document_hub():
    """
    Document Hub page - central access point for document-related features
    """
    logger.info("Document Hub route called")
    
    try:
        # Include navigation for the template
        nav_context = get_context_for_template()
        
        # Get document processing status
        processing_status = {
            "document_processor_available": DOCUMENT_PROCESSOR_AVAILABLE,
            "upload_folder_exists": os.path.exists(UPLOAD_FOLDER),
            "allowed_extensions": list(ALLOWED_EXTENSIONS)
        }
        
        # Try to get previously processed documents from session
        processed_documents = session.get('processed_documents', [])
        
        return render_template(
            "document_hub.html", 
            page_title="Document Hub",
            processing_status=processing_status,
            processed_documents=processed_documents,
            **nav_context
        )
    except Exception as e:
        logger.error(f"Error in document hub route: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Fallback rendering with minimal dependencies
        return render_template(
            "document_upload_dark.html", 
            error=str(e)
        )

@document_bp.route('/document-upload')
def document_upload():
    """Document upload page for AI-powered sustainability document analysis"""
    try:
        logger.info("Document upload page requested")
        
        # Include navigation for the template
        nav_context = get_context_for_template()
        
        # Use dark themed template
        logger.info("Using Finchat dark document upload template")
        return render_template(
            "document_upload_dark.html",
            page_title="Upload Sustainability Document",
            **nav_context
        )
    except Exception as e:
        logger.error(f"Error in document upload route: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Fallback rendering with minimal dependencies
        return render_template("404.html", error=str(e)), 500

@document_bp.route('/upload-sustainability-document', methods=['POST'])
def upload_sustainability_document():
    """Handle document upload and processing"""
    try:
        logger.info("Document upload requested")
        
        # Check if document processor is available
        if not DOCUMENT_PROCESSOR_AVAILABLE:
            logger.error("Document processor not available")
            return jsonify({
                'success': False,
                'error': 'Document processing service is currently unavailable'
            }), 500
            
        # Check if file was included in request
        if 'file' not in request.files:
            logger.warning("No file part in request")
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
            
        file = request.files['file']
        
        # Check if a file was selected
        if file.filename == '':
            logger.warning("No file selected")
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
            
        # Check if file is allowed
        if not allowed_file(file.filename):
            logger.warning(f"Invalid file type: {file.filename}")
            return jsonify({
                'success': False,
                'error': 'Invalid file format. Only PDF files are supported.'
            }), 400
            
        # Get OCR option
        use_ocr = request.form.get('use_ocr', 'false').lower() == 'true'
        logger.info(f"Processing document with OCR: {use_ocr}")
        
        # Secure filename and save to uploads directory
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        saved_name = f"{timestamp}-{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, saved_name)
        
        # Save the file
        file.save(filepath)
        logger.info(f"Saved uploaded file to {filepath}")
        
        # Process the file with document processor
        result = document_processor.process_document(filepath, use_ocr=use_ocr)
        
        if not result['success']:
            logger.error(f"Error processing document: {result.get('error')}")
            # Clean up the uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error during document processing')
            }), 500
        
        # Store document analysis in session for later use
        session['document_analysis'] = {
            'filename': saved_name,
            'original_name': filename,
            'timestamp': timestamp,
            'path': filepath,
            'text': result.get('text', ''),
            'page_count': result.get('page_count', 0),
            'word_count': result.get('word_count', 0),
            'file_size': result.get('file_size', 0),
            'preview': result.get('preview', ''),
            'metrics': result.get('metrics', {}),
            'frameworks': result.get('frameworks', {}),
            'kpis': result.get('kpis', []),
            'tables': result.get('tables', []),
            'figures': result.get('figures', [])
        }
        
        # Add to processed documents list in session
        processed_documents = session.get('processed_documents', [])
        processed_documents.append({
            'filename': saved_name,
            'original_name': filename,
            'timestamp': timestamp,
            'page_count': result.get('page_count', 0),
            'word_count': result.get('word_count', 0)
        })
        session['processed_documents'] = processed_documents
        
        # Return success response with document details
        return jsonify({
            'success': True,
            'document_id': saved_name,
            'page_count': result.get('page_count', 0),
            'word_count': result.get('word_count', 0),
            'text_preview': result.get('preview', '')
        })
        
    except Exception as e:
        logger.error(f"Error in document upload endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@document_bp.route('/document-analysis/<document_id>')
def document_analysis(document_id):
    """Document analysis page for an uploaded document"""
    try:
        logger.info(f"Document analysis requested for {document_id}")
        
        # Check if document exists in session
        document_analysis = session.get('document_analysis', {})
        if not document_analysis or document_analysis.get('filename') != document_id:
            logger.warning(f"Document {document_id} not found in session")
            return render_template('error.html', 
                                  message="Document not found or session expired. Please upload the document again."), 404
        
        # Include navigation for the template
        nav_context = get_context_for_template()
        
        # Render document analysis page
        return render_template(
            "document_analysis.html",
            page_title="Document Analysis",
            document=document_analysis,
            **nav_context
        )
    except Exception as e:
        logger.error(f"Error in document analysis route: {str(e)}")
        logger.error(traceback.format_exc())
        return render_template("error.html", error=str(e)), 500

def register_routes(app):
    """
    Register document routes with Flask app
    
    Args:
        app: Flask application
    """
    app.register_blueprint(document_bp, url_prefix='/documents')
    
    # Register document query API if available
    try:
        from document_query_api import register_routes as register_query_routes
        register_query_routes(app)
        logger.info("Document query API routes registered successfully")
    except ImportError as e:
        logger.warning(f"Document query API not available: {str(e)}")