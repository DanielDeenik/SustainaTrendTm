"""
Document Processing Routes for SustainaTrend™ Platform

This module provides routes for document upload, processing, and analysis
with a focus on sustainability reports and ESG disclosures.
"""

import os
import traceback
import uuid
import logging
import json
import random
import math
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from flask import Blueprint, render_template, request, jsonify, session, url_for, send_file, current_app, redirect
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

# Import regulatory AI services if available
try:
    from frontend.services.regulatory_ai_service import (
        get_supported_frameworks,
        analyze_document_compliance,
        generate_compliance_visualization_data,
        handle_document_upload,
        get_upload_folder as get_regulatory_upload_folder
    )
    from frontend.services.ai_connector import (
        connect_to_ai_services,
        is_pinecone_available,
        generate_embedding,
        semantic_search,
        get_completion
    )
    # Initialize AI connector
    connect_to_ai_services()
    logger = logging.getLogger(__name__)
    logger.info("AI connector module loaded successfully in document_routes")
    # Log Pinecone availability
    pinecone_status = "Connected" if is_pinecone_available() else "Not connected"
    logger.info(f"Pinecone RAG system availability: {pinecone_status}")
    REGULATORY_AI_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Error importing regulatory AI service: {str(e)}")
    # Create stub functions for development
    def get_supported_frameworks(): return {"CSRD": "Corporate Sustainability Reporting Directive"}
    def analyze_document_compliance(text, frameworks=None): return {"frameworks": {}}
    def generate_compliance_visualization_data(results): return {"frameworks": []}
    def handle_document_upload(file): return (False, "Service unavailable", None)
    def get_regulatory_upload_folder(): return os.path.join(os.path.dirname(__file__), 'uploads')
    REGULATORY_AI_AVAILABLE = False

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
        
        # Use integrated document hub template
        logger.info("Using integrated document hub template")
        return render_template(
            "integrated_document_hub.html",
            page_title="Document & Regulatory Intelligence Hub",
            processing_status=processing_status,
            processed_documents=processed_documents,
            **nav_context
        )
    except Exception as e:
        logger.error(f"Error in document hub route: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Fallback rendering with minimal dependencies
        return render_template(
            "integrated_document_hub.html", 
            error=str(e)
        )

@document_bp.route('/document-upload')
def document_upload():
    """Document upload page for AI-powered sustainability document analysis"""
    try:
        logger.info("Document upload page requested")
        
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
        
        # Use integrated document hub template
        logger.info("Using integrated document hub template")
        return render_template(
            "integrated_document_hub.html",
            page_title="Document & Regulatory Intelligence Hub",
            processing_status=processing_status,
            processed_documents=processed_documents,
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

@document_bp.route('/api/regulatory-frameworks')
def api_regulatory_frameworks():
    """API endpoint for supported regulatory frameworks"""
    try:
        frameworks = get_supported_frameworks()
        return jsonify({
            'success': True,
            'frameworks': frameworks
        })
    except Exception as e:
        logger.error(f"Error in regulatory frameworks API: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@document_bp.route('/api/regulatory-assessment', methods=['POST'])
def api_regulatory_assessment():
    """API endpoint for regulatory compliance assessment"""
    try:
        # Get request data
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
            
        # Get document text
        text = data.get('text', '')
        if not text:
            return jsonify({
                'success': False,
                'error': 'No document text provided'
            }), 400
            
        # Get frameworks to check against
        frameworks = data.get('frameworks', None)
        
        # Perform assessment
        if REGULATORY_AI_AVAILABLE:
            results = analyze_document_compliance(text, frameworks)
            return jsonify({
                'success': True,
                'assessment': results
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Regulatory AI service is not available'
            }), 503
    except Exception as e:
        logger.error(f"Error in regulatory assessment API: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@document_bp.route('/api/regulatory-gap-analysis', methods=['POST'])
def api_regulatory_gap_analysis():
    """API endpoint for regulatory gap analysis"""
    try:
        # Get request data
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
            
        # Get assessment data
        assessment = data.get('assessment', {})
        if not assessment:
            return jsonify({
                'success': False,
                'error': 'No assessment data provided'
            }), 400
            
        # Generate gap analysis
        gap_analysis = generate_gap_analysis_data(assessment)
        
        return jsonify({
            'success': True,
            'gap_analysis': gap_analysis
        })
    except Exception as e:
        logger.error(f"Error in regulatory gap analysis API: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_compliance_level_for_score(score):
    """
    Get compliance level text based on score
    
    Args:
        score: Numerical score (0-100)
        
    Returns:
        str: Compliance level description
    """
    if score >= 90:
        return "Excellent"
    elif score >= 75:
        return "Good"
    elif score >= 60:
        return "Adequate"
    elif score >= 40:
        return "Needs Improvement"
    else:
        return "Insufficient"

def generate_gap_analysis_data(assessment):
    """
    Generate gap analysis data from assessment data
    
    Args:
        assessment: Assessment data from UI
        
    Returns:
        dict: Gap analysis data
    """
    gaps = []
    recommendations = []
    
    # Extract gaps and recommendations from assessment
    if 'categories' in assessment:
        for category in assessment['categories']:
            category_name = category.get('name', 'Unknown Category')
            
            # Add low-scoring criteria as gaps
            for criterion in category.get('criteria', []):
                score = criterion.get('score', 0)
                if score < 60:  # Consider scores below 60% as gaps
                    gaps.append({
                        'category': category_name,
                        'criterion': criterion.get('name', 'Unknown Criterion'),
                        'score': score,
                        'level': get_compliance_level_for_score(score),
                        'description': criterion.get('description', '')
                    })
    
    # Generate recommendations for gaps
    for gap in gaps[:5]:  # Limit to top 5 gaps
        recommendations.append({
            'gap': gap['criterion'],
            'recommendation': f"Improve disclosure on {gap['criterion']} in the {gap['category']} section.",
            'priority': 'High' if gap['score'] < 40 else 'Medium'
        })
    
    return {
        'gaps': gaps,
        'recommendations': recommendations,
        'summary': f"Found {len(gaps)} areas needing improvement.",
        'priority_areas': [gap['criterion'] for gap in gaps[:3]]  # Top 3 priority areas
    }

@document_bp.route('/view-document/<document_id>')
def view_document(document_id):
    """View detailed document analysis"""
    try:
        # Convert document_id to int (from URL) if it's a string
        doc_id = int(document_id) if document_id.isdigit() else document_id
        
        # Try to get previously processed documents from session
        processed_documents = session.get('processed_documents', [])
        
        # Check if document exists in the session
        if 0 <= doc_id < len(processed_documents):
            document = processed_documents[doc_id]
        else:
            logger.warning(f"Document {document_id} not found in session")
            return render_template("error.html", error="Document not found or session expired"), 404
        
        # Include navigation for the template
        nav_context = get_context_for_template()
        
        # Render document detail template
        return render_template(
            "document_analysis.html",
            page_title=f"Document Analysis: {document.get('filename', 'Unknown')}",
            document=document,
            document_id=doc_id,
            **nav_context
        )
    except Exception as e:
        logger.error(f"Error viewing document: {str(e)}")
        logger.error(traceback.format_exc())
        return render_template("error.html", error=str(e)), 500

@document_bp.route('/download-report/<document_id>')
def download_report(document_id):
    """Download document compliance report"""
    try:
        # Convert document_id to int (from URL) if it's a string
        doc_id = int(document_id) if document_id.isdigit() else document_id
        
        # Try to get previously processed documents from session
        processed_documents = session.get('processed_documents', [])
        
        # Check if document exists in the session
        if 0 <= doc_id < len(processed_documents):
            document = processed_documents[doc_id]
            # Redirect to API endpoint that generates the report
            return redirect(url_for('document_routes.api_generate_report', document_id=document.get('filename', doc_id)))
        else:
            logger.warning(f"Document {document_id} not found in session")
            return render_template("error.html", error="Document not found or session expired"), 404
    except Exception as e:
        logger.error(f"Error downloading report: {str(e)}")
        logger.error(traceback.format_exc())
        return render_template("error.html", error=str(e)), 500

@document_bp.route('/api/generate-report/<document_id>')
def api_generate_report(document_id):
    """Generate a downloadable PDF compliance report"""
    try:
        # Check if document exists in session
        document_analysis = session.get('document_analysis', {})
        if not document_analysis or document_analysis.get('filename') != document_id:
            logger.warning(f"Document {document_id} not found in session")
            return jsonify({
                'success': False,
                'error': 'Document not found or session expired'
            }), 404
        
        # Get document data
        document_name = document_analysis.get('original_name', 'Unknown Document')
        document_text = document_analysis.get('text', '')
        frameworks = document_analysis.get('frameworks', {})
        
        # Determine primary framework (highest confidence)
        primary_framework = None
        max_confidence = 0
        for framework, confidence in frameworks.items():
            if confidence > max_confidence:
                max_confidence = confidence
                primary_framework = framework
        
        try:
            # Import PDF generation library
            from fpdf import FPDF
            
            # Create PDF document
            pdf = FPDF()
            pdf.add_page()
            
            # Add header
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Sustainability Compliance Report', 0, 1, 'C')
            pdf.ln(5)
            
            # Add document info
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f'Document: {document_name}', 0, 1)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 10, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1)
            pdf.cell(0, 10, f'Document ID: {document_id}', 0, 1)
            pdf.ln(5)
            
            # Add frameworks section
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Detected Frameworks', 0, 1)
            
            if frameworks:
                pdf.set_font('Arial', '', 10)
                for framework, confidence in frameworks.items():
                    confidence_pct = int(confidence * 100)
                    is_primary = framework == primary_framework
                    framework_text = f"{framework.upper()}: {confidence_pct}% confidence"
                    if is_primary:
                        framework_text += " (Primary Framework)"
                    pdf.cell(0, 7, framework_text, 0, 1)
            else:
                pdf.set_font('Arial', 'I', 10)
                pdf.cell(0, 10, 'No frameworks detected', 0, 1)
            
            pdf.ln(5)
            
            # Add metrics section if available
            metrics = document_analysis.get('metrics', {})
            if metrics:
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, 'Extracted Sustainability Metrics', 0, 1)
                
                for category, category_metrics in metrics.items():
                    pdf.set_font('Arial', 'B', 11)
                    pdf.cell(0, 7, category.title(), 0, 1)
                    
                    pdf.set_font('Arial', '', 10)
                    for i, metric in enumerate(category_metrics[:5]):  # Limit to 5 metrics per category
                        keyword = metric.get('keyword', 'Unknown')
                        pdf.cell(0, 7, f"{i+1}. {keyword}", 0, 1)
                    
                    if len(category_metrics) > 5:
                        pdf.set_font('Arial', 'I', 10)
                        pdf.cell(0, 7, f"...and {len(category_metrics) - 5} more", 0, 1)
                    
                    pdf.ln(3)
            
            # Get compliance assessment
            if primary_framework and REGULATORY_AI_AVAILABLE:
                pdf.ln(5)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, f'Compliance Assessment ({primary_framework.upper()})', 0, 1)
                
                try:
                    assessment = analyze_document_compliance(document_text, [primary_framework])
                    
                    # Add overall assessment
                    pdf.set_font('Arial', 'B', 11)
                    pdf.cell(0, 7, "Overall Assessment", 0, 1)
                    
                    if 'overall_score' in assessment:
                        score = assessment['overall_score']
                        pdf.set_font('Arial', '', 10)
                        pdf.cell(0, 7, f"Compliance Score: {score}%", 0, 1)
                    
                    # Add findings if available
                    if 'overall_findings' in assessment and assessment['overall_findings']:
                        pdf.set_font('Arial', 'B', 11)
                        pdf.cell(0, 7, "Key Findings", 0, 1)
                        
                        pdf.set_font('Arial', '', 10)
                        for i, finding in enumerate(assessment['overall_findings'][:5]):  # Limit to 5 findings
                            pdf.multi_cell(0, 7, f"{i+1}. {finding}")
                            
                        if len(assessment['overall_findings']) > 5:
                            pdf.set_font('Arial', 'I', 10)
                            pdf.cell(0, 7, f"...and {len(assessment['overall_findings']) - 5} more findings", 0, 1)
                    
                    # Add gap analysis
                    gap_analysis = generate_gap_analysis_data(assessment)
                    if gap_analysis.get('gaps'):
                        pdf.ln(5)
                        pdf.set_font('Arial', 'B', 12)
                        pdf.cell(0, 10, "Gap Analysis", 0, 1)
                        
                        pdf.set_font('Arial', 'B', 11)
                        pdf.cell(0, 7, "Priority Areas for Improvement", 0, 1)
                        
                        pdf.set_font('Arial', '', 10)
                        for i, gap in enumerate(gap_analysis['gaps'][:3]):  # Top 3 gaps
                            level = get_compliance_level_for_score(gap['score'])
                            pdf.multi_cell(0, 7, f"{i+1}. {gap['criterion']} ({level}: {gap['score']}%)")
                except Exception as assessment_err:
                    logger.error(f"Error performing compliance assessment for report: {str(assessment_err)}")
                    pdf.set_font('Arial', 'I', 10)
                    pdf.cell(0, 7, "Unable to perform compliance assessment for this document", 0, 1)
            
            # Add recommendations section
            pdf.ln(5)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, "Next Steps", 0, 1)
            
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 7, "1. Review the identified gaps in your sustainability reporting")
            pdf.multi_cell(0, 7, "2. Enhance disclosures in low-scoring areas")
            pdf.multi_cell(0, 7, "3. Consider conducting a more detailed assessment with SustainaTrend™ specialists")
            
            # Save the PDF to a temporary file
            report_filename = f"sustainability_report_{document_id}.pdf"
            report_path = os.path.join(UPLOAD_FOLDER, report_filename)
            pdf.output(report_path)
            
            # Send the file
            return send_file(
                report_path,
                as_attachment=True,
                download_name=f"SustainaTrend_Compliance_Report_{document_name}.pdf",
                mimetype='application/pdf'
            )
            
        except ImportError as pdf_err:
            logger.error(f"PDF generation library not available: {str(pdf_err)}")
            return jsonify({
                'success': False,
                'error': 'PDF generation capability not available'
            }), 500
            
    except Exception as e:
        logger.error(f"Error generating compliance report: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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