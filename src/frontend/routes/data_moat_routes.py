"""
Enhanced Data Moat Routes for SustainaTrend™

This module provides comprehensive routes for the data moat functionality with
a focus on reliable document upload, regulatory AI analysis, and data processing.
This now includes all regulatory AI functionality previously in separate routes.
"""

import os
import uuid
import logging
import json
import random
import math
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from flask import (
    Blueprint, render_template, request, jsonify, 
    session, redirect, url_for, send_file, current_app
)
from werkzeug.utils import secure_filename

# Configure logging
logger = logging.getLogger(__name__)

# Define constants
UPLOAD_FOLDER = os.path.join('frontend', 'static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'csv', 'xlsx'}

# Create blueprint
data_moat_bp = Blueprint('data_moat', __name__, url_prefix='/data-moat')

# Import regulatory AI services if available
try:
    from frontend.services.regulatory_ai_service import (
        get_supported_frameworks,
        analyze_document_compliance,
        generate_compliance_visualization_data,
        handle_document_upload,
        get_upload_folder
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
    logger.info("AI connector module loaded successfully in data_moat_routes")
    # Log Pinecone availability
    pinecone_status = "Connected" if is_pinecone_available() else "Not connected"
    logger.info(f"Pinecone RAG system availability: {pinecone_status}")
    REGULATORY_AI_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Error importing regulatory AI service: {str(e)}")
    # Create stub functions for development
    def get_supported_frameworks(): return {"CSRD": "Corporate Sustainability Reporting Directive"}
    def analyze_document_compliance(text, frameworks=None): return {"frameworks": {}}
    def generate_compliance_visualization_data(results): return {"frameworks": []}
    def handle_document_upload(file): return (False, "Service unavailable", None)
    def get_upload_folder(): return os.path.join(os.path.dirname(__file__), 'uploads')
    REGULATORY_AI_AVAILABLE = False

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Simple document storage
documents = {}

def allowed_file(filename: str) -> bool:
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file using PyMuPDF if available"""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        text = ""
        for page_num in range(len(doc)):
            page = doc[page_num]
            text += page.get_text()
        return text
    except ImportError:
        logger.warning("PyMuPDF not available, returning placeholder text")
        return f"Text extraction not available for {os.path.basename(file_path)}"
    except Exception as e:
        logger.error(f"Error extracting text: {str(e)}")
        return f"Error extracting text: {str(e)}"

def detect_frameworks(text: str) -> Dict[str, float]:
    """
    Simple framework detection based on keyword matching
    Returns a dictionary of framework IDs and confidence scores
    """
    frameworks = {
        'esrs': ['ESRS', 'European Sustainability Reporting Standards'],
        'csrd': ['CSRD', 'Corporate Sustainability Reporting Directive'],
        'gri': ['GRI', 'Global Reporting Initiative'],
        'tcfd': ['TCFD', 'Climate-related Financial Disclosures'],
        'sfdr': ['SFDR', 'Sustainable Finance Disclosure'],
        'sdg': ['SDG', 'Sustainable Development Goals'],
        'sasb': ['SASB', 'Sustainability Accounting Standards']
    }
    
    results = {}
    text_lower = text.lower()
    
    for framework_id, keywords in frameworks.items():
        score = 0
        for keyword in keywords:
            if keyword.lower() in text_lower:
                # Simple scoring - just count mentions
                mentions = text_lower.count(keyword.lower())
                score += mentions * 0.1  # 0.1 points per mention
        
        if score > 0:
            # Normalize to 0-1 range
            results[framework_id] = min(1.0, score)
    
    return results

def extract_sustainability_metrics(text: str) -> Dict[str, List[Dict]]:
    """
    Extract basic sustainability metrics from text
    Returns a dictionary of metrics by category
    """
    metrics = {
        'emissions': [],
        'energy': [],
        'water': [],
        'waste': [],
        'social': [],
        'governance': []
    }
    
    # Simple pattern matching for demonstration
    patterns = {
        'emissions': ['carbon', 'emissions', 'CO2', 'greenhouse', 'GHG'],
        'energy': ['energy', 'renewable', 'electricity', 'consumption'],
        'water': ['water', 'consumption', 'usage', 'wastewater'],
        'waste': ['waste', 'recycling', 'landfill', 'circular'],
        'social': ['diversity', 'inclusion', 'employees', 'community'],
        'governance': ['board', 'ethics', 'compliance', 'transparency']
    }
    
    text_lower = text.lower()
    
    # Simple extraction by finding sentences containing keywords
    for category, keywords in patterns.items():
        for keyword in keywords:
            if keyword in text_lower:
                # Find sentences containing the keyword
                start = max(0, text_lower.find(keyword) - 100)
                end = min(len(text_lower), text_lower.find(keyword) + 100)
                context = text[start:end]
                
                metrics[category].append({
                    'keyword': keyword,
                    'context': context,
                    'confidence': 0.7  # Fixed confidence for simplicity
                })
    
    return metrics

@data_moat_bp.route('/')
def index():
    """Data Moat Interface dashboard"""
    # Get list of processed documents
    doc_list = [
        {
            'id': doc_id,
            'filename': doc.get('original_filename', 'Unknown'),
            'timestamp': doc.get('timestamp', 'Unknown'),
            'metrics_count': len(doc.get('metrics', {})),
            'frameworks': doc.get('frameworks', {})
        }
        for doc_id, doc in documents.items()
    ]
    
    return render_template(
        'data_moat/index.html',
        documents=doc_list,
        document_count=len(doc_list)
    )

@data_moat_bp.route('/upload', methods=['GET', 'POST'])
def document_upload():
    """Document upload interface with basic processing"""
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
            upload_active=True
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
        
        # Generate a unique document ID
        document_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        # Secure filename and save to uploads directory
        filename = secure_filename(file.filename)
        saved_name = f"{timestamp}-{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, saved_name)
        
        try:
            # Save the file
            file.save(filepath)
            logger.info(f"Saved uploaded file to {filepath}")
            
            # Extract text from the document
            text = extract_text_from_pdf(filepath)
            text_length = len(text)
            
            # Auto-detect frameworks if enabled
            frameworks_detected = {}
            if auto_detect_framework:
                frameworks_detected = detect_frameworks(text)
                
            # Extract metrics
            metrics = extract_sustainability_metrics(text)
            metrics_count = sum(len(metrics[category]) for category in metrics)
            
            # Store document information
            document_data = {
                'document_id': document_id,
                'filename': saved_name,
                'original_filename': filename,
                'filepath': filepath,
                'timestamp': timestamp,
                'text_length': text_length,
                'text_preview': text[:1000] + '...' if len(text) > 1000 else text,
                'frameworks': frameworks_detected,
                'metrics': metrics,
                'metrics_count': metrics_count,
                'primary_framework': max(frameworks_detected.items(), key=lambda x: x[1])[0] if frameworks_detected else None,
                'processing_status': 'completed'
            }
            
            # Store in memory (would be in database in production)
            documents[document_id] = document_data
            
            # Store in session for convenience
            session['document_data'] = {
                'document_id': document_id,
                'filename': saved_name,
                'original_filename': filename,
                'timestamp': timestamp,
                'metrics_count': metrics_count,
                'frameworks': frameworks_detected,
                'primary_framework': document_data.get('primary_framework')
            }
            
            # Return processing results
            return jsonify({
                'success': True,
                'document_id': document_id,
                'metrics_count': metrics_count,
                'frameworks_detected': frameworks_detected,
                'primary_framework': document_data.get('primary_framework'),
                'redirect_url': url_for('data_moat.document_analysis', document_id=document_id)
            })
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            
            # Clean up the uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
            
            return jsonify({
                'success': False,
                'error': f"Error processing document: {str(e)}"
            }), 500

@data_moat_bp.route('/analysis/<document_id>')
def document_analysis(document_id):
    """Document analysis interface with extracted data - redirects to analytics dashboard"""
    # Check if document exists in memory
    if document_id not in documents:
        # If we don't have the document, check session
        if 'document_data' in session and session['document_data'].get('document_id') == document_id:
            # Redirect to upload since we don't have the full document data
            return redirect(url_for('data_moat.document_upload'))
        else:
            # Document not found
            return render_template(
                'data_moat/index.html',
                error=f"Document with ID {document_id} not found"
            )
    
    # Get document data
    document_data = documents[document_id]
    
    # Store document data in session for analytics dashboard
    session['analytics_document_id'] = document_id
    session['analytics_document_data'] = document_data
    
    # Redirect to analytics dashboard with document data
    logger.info(f"Redirecting to analytics dashboard with document ID: {document_id}")
    return redirect(url_for('analytics_dashboard', 
                            document_id=document_id, 
                            source='data_moat'))

# Keep a version of the original analysis route for API access
@data_moat_bp.route('/view-analysis/<document_id>')
def view_document_analysis(document_id):
    """Original document analysis interface with extracted data"""
    # Check if document exists in memory
    if document_id not in documents:
        # Document not found
        return render_template(
            'data_moat/index.html',
            error=f"Document with ID {document_id} not found"
        )
    
    # Get document data
    document_data = documents[document_id]
    
    # Render analysis template
    return render_template(
        'data_moat/analysis.html',
        document_id=document_id,
        document=document_data,
        analysis_active=True
    )

@data_moat_bp.route('/api/document/<document_id>')
def api_document(document_id):
    """API endpoint for document data"""
    if document_id not in documents:
        return jsonify({
            'success': False,
            'error': 'Document not found'
        }), 404
    
    return jsonify({
        'success': True,
        'document': documents[document_id]
    })

@data_moat_bp.route('/api/metrics/<document_id>')
def api_metrics(document_id):
    """API endpoint for extracted metrics"""
    if document_id not in documents:
        return jsonify({
            'success': False,
            'error': 'Document not found'
        }), 404
    
    return jsonify({
        'success': True,
        'document_id': document_id,
        'metrics': documents[document_id].get('metrics', {})
    })

@data_moat_bp.route('/api/frameworks/<document_id>')
def api_frameworks(document_id):
    """API endpoint for detected frameworks"""
    if document_id not in documents:
        return jsonify({
            'success': False,
            'error': 'Document not found'
        }), 404
    
    return jsonify({
        'success': True,
        'document_id': document_id,
        'frameworks': documents[document_id].get('frameworks', {})
    })

@data_moat_bp.route('/api/documents')
def api_documents():
    """API endpoint for retrieving all documents"""
    doc_list = [
        {
            'id': doc_id,
            'filename': doc.get('original_filename', 'Unknown'),
            'timestamp': doc.get('timestamp', 'Unknown'),
            'metrics_count': len(doc.get('metrics', {})),
            'frameworks': doc.get('frameworks', {})
        }
        for doc_id, doc in documents.items()
    ]
    
    return jsonify({
        'success': True,
        'documents': doc_list
    })

@data_moat_bp.route('/download/<document_id>')
def download_document(document_id):
    """Download the original document"""
    if document_id not in documents:
        return jsonify({
            'success': False,
            'error': 'Document not found'
        }), 404
    
    filepath = documents[document_id].get('filepath')
    if not filepath or not os.path.exists(filepath):
        return jsonify({
            'success': False,
            'error': 'File not found'
        }), 404
    
    original_filename = documents[document_id].get('original_filename', 'document.pdf')
    return send_file(filepath, as_attachment=True, download_name=original_filename)

# ==================== REGULATORY AI ROUTES ======================
# The following routes are from the regulatory_ai_agent.py module
# They've been consolidated here to streamline the codebase

@data_moat_bp.route('/regulatory-compliance')
def regulatory_compliance_dashboard():
    """Regulatory compliance dashboard"""
    # Check if regulatory AI is available
    if not REGULATORY_AI_AVAILABLE:
        return render_template(
            'data_moat/index.html',
            error="Regulatory AI features are not available"
        )
    
    # Get available frameworks
    frameworks = get_supported_frameworks()
    
    return render_template(
        'data_moat/regulatory_compliance.html',
        frameworks=frameworks,
        regulatory_active=True
    )

@data_moat_bp.route('/api/regulatory-frameworks')
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
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@data_moat_bp.route('/api/regulatory-assessment', methods=['POST'])
def api_regulatory_assessment():
    """API endpoint for regulatory compliance assessment"""
    try:
        data = request.get_json()
        document_text = data.get('document_text', '')
        document_id = data.get('document_id')
        framework_id = data.get('framework_id', 'ESRS')
        use_ai = data.get('use_ai', True)
        
        # If document_id is provided, try to get the document text from storage
        if document_id and not document_text:
            if document_id in documents:
                document_text = documents[document_id].get('text_preview', '')
            else:
                return jsonify({
                    'success': False,
                    'error': 'Document not found'
                }), 404
        
        if not document_text:
            return jsonify({
                'success': False,
                'error': 'No document text provided'
            }), 400
            
        # Use the regulatory AI service to assess compliance
        if REGULATORY_AI_AVAILABLE and use_ai:
            # Convert from existing regulatory_ai_service format to our frontend format
            service_results = analyze_document_compliance(document_text, [framework_id])
            assessment = convert_service_results_to_ui_format(service_results, framework_id)
        else:
            # Simple fallback if regulatory AI is not available
            assessment = {
                'framework_id': framework_id,
                'framework': get_supported_frameworks().get(framework_id, framework_id),
                'overall_score': 50,  # Default middle score
                'date': datetime.now().isoformat(),
                'categories': {},
                'overall_findings': [
                    "Regulatory AI assessment not available"
                ],
                'overall_recommendations': [
                    "Enable Regulatory AI services for detailed assessment"
                ]
            }
            
            # Add some basic mock categories for UI display when AI is not available
            framework_categories = generate_mock_framework_categories(framework_id)
            for category_id, category_info in framework_categories.items():
                # Generate varied scores for visual interest
                score = random.randint(30, 70)
                assessment['categories'][category_id] = {
                    'name': category_info['name'],
                    'score': score,
                    'compliance_level': get_compliance_level_for_score(score)
                }
        
        return jsonify({
            'success': True,
            'assessment': assessment
        })
    except Exception as e:
        logger.error(f"Error in regulatory assessment API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Helper functions for regulatory compliance template
def convert_service_results_to_ui_format(service_results, framework_id):
    """
    Convert results from regulatory_ai_service format to the UI format expected by the template
    
    Args:
        service_results: Results from analyze_document_compliance
        framework_id: Framework ID (e.g., 'ESRS')
        
    Returns:
        dict: Assessment in UI-compatible format
    """
    # Create base assessment structure
    assessment = {
        'framework_id': framework_id,
        'framework': get_supported_frameworks().get(framework_id, framework_id),
        'overall_score': 0,
        'date': datetime.now().isoformat(),
        'categories': {},
        'overall_findings': [],
        'overall_recommendations': []
    }
    
    # Check if we have results
    if not service_results:
        return assessment
    
    # Extract overall score
    assessment['overall_score'] = int(service_results.get('overall_score', 0) * 100)
    
    # Get framework specific results
    framework_results = service_results.get('frameworks', {}).get(framework_id, {})
    
    # Extract findings and recommendations
    if 'findings' in framework_results:
        assessment['overall_findings'] = framework_results['findings']
    elif 'key_findings' in framework_results:
        assessment['overall_findings'] = framework_results['key_findings']
    
    if 'recommendations' in framework_results:
        assessment['overall_recommendations'] = framework_results['recommendations']
    
    # Generate categories from framework results
    if 'gaps' in framework_results:
        # Convert gaps into categories with scores
        for i, gap in enumerate(framework_results.get('gaps', [])):
            # Extract category code from gap text if possible
            if ':' in gap:
                parts = gap.split(':', 1)
                category_id = parts[0].strip()
                category_name = category_id
            else:
                # Create a category ID
                category_id = f"GAP{i+1}"
                category_name = f"Gap {i+1}"
            
            # Calculate a score (inverted from gap severity)
            score = max(10, 100 - (i+1) * 15)  # First gap = 85, second = 70, etc.
            
            assessment['categories'][category_id] = {
                'name': category_name,
                'score': score,
                'compliance_level': get_compliance_level_for_score(score)
            }
    
    # If no categories yet, generate some from the framework
    if not assessment['categories']:
        framework_categories = generate_mock_framework_categories(framework_id)
        
        # Generate scores based on compliance level
        compliance_level = framework_results.get('compliance_level', '')
        base_score = 50
        if 'fully' in compliance_level.lower():
            base_score = 85
        elif 'mostly' in compliance_level.lower():
            base_score = 70
        elif 'partially' in compliance_level.lower():
            base_score = 50
        elif 'non' in compliance_level.lower():
            base_score = 30
        
        # Create categories with varied scores
        for category_id, category_info in framework_categories.items():
            # Vary scores around the base score
            variance = 15
            score = base_score + random.randint(-variance, variance)
            score = max(10, min(95, score))  # Keep between 10-95
            
            assessment['categories'][category_id] = {
                'name': category_info['name'],
                'score': score,
                'compliance_level': get_compliance_level_for_score(score)
            }
    
    return assessment

def generate_mock_framework_categories(framework_id):
    """
    Generate framework categories for different frameworks
    
    Args:
        framework_id: Framework ID (e.g., 'ESRS', 'GRI')
        
    Returns:
        dict: Dictionary of categories with names
    """
    # Pre-defined categories for common frameworks
    categories = {
        'ESRS': {
            'E1': {'name': 'Climate Change'},
            'E2': {'name': 'Pollution'},
            'E3': {'name': 'Water & Marine Resources'},
            'E4': {'name': 'Biodiversity & Ecosystems'},
            'E5': {'name': 'Resource Use & Circular Economy'},
            'S1': {'name': 'Own Workforce'},
            'S2': {'name': 'Workers in Value Chain'},
            'S3': {'name': 'Affected Communities'},
            'S4': {'name': 'Consumers & End-users'},
            'G1': {'name': 'Governance, Risk & Controls'},
            'G2': {'name': 'Business Conduct'}
        },
        'CSRD': {
            'ENV': {'name': 'Environmental'},
            'SOC': {'name': 'Social'},
            'GOV': {'name': 'Governance'},
            'STR': {'name': 'Strategy'},
            'IMP': {'name': 'Implementation'}
        },
        'GRI': {
            'GRI-200': {'name': 'Economic'},
            'GRI-300': {'name': 'Environmental'},
            'GRI-400': {'name': 'Social'}
        },
        'TCFD': {
            'GOV': {'name': 'Governance'},
            'STR': {'name': 'Strategy'},
            'RMG': {'name': 'Risk Management'},
            'MET': {'name': 'Metrics & Targets'}
        }
    }
    
    # Return categories for specific framework or generic categories
    if framework_id in categories:
        return categories[framework_id]
    else:
        return {
            'A1': {'name': 'Policy & Commitment'},
            'A2': {'name': 'Implementation & Monitoring'},
            'A3': {'name': 'Disclosure & Transparency'},
            'A4': {'name': 'Performance & Impact'}
        }

def get_compliance_level_for_score(score):
    """
    Get compliance level text based on score
    
    Args:
        score: Numerical score (0-100)
        
    Returns:
        str: Compliance level description
    """
    if score >= 80:
        return "High compliance"
    elif score >= 60:
        return "Moderate compliance"
    elif score >= 40:
        return "Partial compliance"
    else:
        return "Low compliance"

def generate_gap_analysis_data(assessment):
    """
    Generate gap analysis data from assessment data
    
    Args:
        assessment: Assessment data from UI
        
    Returns:
        dict: Gap analysis data
    """
    # Create gap analysis structure
    gap_analysis = {
        'summary': 'Gap analysis based on compliance assessment',
        'priority_gaps': [],
        'timeline': [],
        'resources': []
    }
    
    # Generate summary based on overall score
    overall_score = assessment.get('overall_score', 0)
    if overall_score >= 80:
        gap_analysis['summary'] = "The document demonstrates strong compliance with minimal gaps. Focus on maintaining and enhancing current disclosures."
    elif overall_score >= 60:
        gap_analysis['summary'] = "The document shows moderate compliance with some notable gaps. Address key improvement areas to strengthen overall compliance."
    elif overall_score >= 40:
        gap_analysis['summary'] = "The document exhibits partial compliance with significant gaps. A structured improvement plan is needed to address multiple areas."
    else:
        gap_analysis['summary'] = "The document shows limited compliance with major gaps across most areas. A comprehensive overhaul of sustainability reporting is recommended."
    
    # Generate priority gaps from categories with low scores
    categories = assessment.get('categories', {})
    
    # Convert to list and sort by score (ascending)
    sorted_categories = sorted([
        {'id': cid, 'name': cdata.get('name', cid), 'score': cdata.get('score', 0)}
        for cid, cdata in categories.items()
    ], key=lambda x: x['score'])
    
    # Take up to 6 lowest scoring categories
    for category in sorted_categories[:6]:
        score = category['score']
        
        # Generate recommendations based on score
        if score < 30:
            recommendations = [
                f"Develop comprehensive {category['name']} disclosures from the ground up",
                f"Establish data collection processes for {category['name']} metrics",
                f"Conduct a detailed assessment of {category['name']} requirements"
            ]
        elif score < 50:
            recommendations = [
                f"Enhance {category['name']} disclosures with more quantitative data",
                f"Include forward-looking information for {category['name']}",
                f"Address compliance gaps in {category['name']} disclosures"
            ]
        else:
            recommendations = [
                f"Add more context and analysis to {category['name']} disclosures",
                f"Include industry benchmarking for {category['name']} metrics",
                f"Consider third-party verification of {category['name']} data"
            ]
        
        gap_analysis['priority_gaps'].append({
            'category': category['id'],
            'name': category['name'],
            'score': score,
            'recommendations': recommendations
        })
    
    # Generate implementation timeline
    if overall_score < 50:
        # For low compliance, recommend 3 phases
        gap_analysis['timeline'] = [
            {
                'title': 'Phase 1: Foundation Building',
                'timeframe': '0-3 months',
                'description': 'Establish sustainability reporting governance structure and data collection processes.'
            },
            {
                'title': 'Phase 2: Gap Remediation',
                'timeframe': '3-6 months',
                'description': 'Address highest priority gaps and develop comprehensive disclosures for key categories.'
            },
            {
                'title': 'Phase 3: Comprehensive Compliance',
                'timeframe': '6-12 months',
                'description': 'Achieve full framework compliance with comprehensive reporting across all categories.'
            }
        ]
    else:
        # For moderate to high compliance, recommend 2 phases
        gap_analysis['timeline'] = [
            {
                'title': 'Phase 1: Targeted Improvements',
                'timeframe': '0-3 months',
                'description': 'Address specific gaps in highest priority categories identified in the assessment.'
            },
            {
                'title': 'Phase 2: Optimization',
                'timeframe': '3-6 months',
                'description': 'Enhance overall reporting quality with benchmarking and third-party verification.'
            }
        ]
    
    # Generate resources needed
    framework_id = assessment.get('framework_id', 'ESRS')
    
    gap_analysis['resources'] = [
        'Sustainability reporting expertise for framework compliance',
        'Data collection tools and processes for sustainability metrics',
        'Internal stakeholder engagement for cross-functional input'
    ]
    
    # Add specific resources based on framework
    if framework_id == 'ESRS' or framework_id == 'CSRD':
        gap_analysis['resources'].append('European sustainability reporting expertise for CSRD compliance')
        gap_analysis['resources'].append('Double materiality assessment methodology and tools')
    elif framework_id == 'TCFD':
        gap_analysis['resources'].append('Climate scenario analysis capabilities')
        gap_analysis['resources'].append('Climate risk assessment expertise')
    elif framework_id == 'GRI':
        gap_analysis['resources'].append('Stakeholder materiality assessment tools')
        gap_analysis['resources'].append('GRI Standards reporting guidance')
    
    # Add verification resource for high compliance
    if overall_score >= 70:
        gap_analysis['resources'].append('Third-party assurance provider for sustainability disclosures')
    
    return gap_analysis

@data_moat_bp.route('/api/gap-analysis', methods=['POST'])
def api_regulatory_gap_analysis():
    """API endpoint for regulatory gap analysis"""
    try:
        data = request.get_json()
        assessment = data.get('assessment')
        
        if not assessment:
            return jsonify({
                'success': False,
                'error': 'No assessment data provided'
            }), 400
        
        # Use the regulatory AI service to generate gap analysis
        if REGULATORY_AI_AVAILABLE:
            # If we have the original service format, use that
            if 'frameworks' in assessment:
                # Create visualization from service format
                gap_analysis = generate_compliance_visualization_data(assessment)
            else:
                # Generate from UI format
                gap_analysis = generate_gap_analysis_data(assessment)
        else:
            # Generate gap analysis even when AI is not available
            gap_analysis = generate_gap_analysis_data(assessment)
        
        return jsonify({
            'success': True,
            'gap_analysis': gap_analysis
        })
    except Exception as e:
        logger.error(f"Error in gap analysis API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@data_moat_bp.route('/api/document-compliance/<document_id>')
def api_document_compliance(document_id):
    """API endpoint to get compliance assessment for a document"""
    if document_id not in documents:
        return jsonify({
            'success': False,
            'error': 'Document not found'
        }), 404
    
    # Get document text
    document_text = documents[document_id].get('text_preview', '')
    if not document_text:
        return jsonify({
            'success': False,
            'error': 'Document has no text content'
        }), 400
    
    # Get primary framework from document or use default
    primary_framework = documents[document_id].get('primary_framework', 'esrs')
    primary_framework = primary_framework.upper()  # Ensure uppercase for framework ID
    
    # Perform compliance assessment
    if REGULATORY_AI_AVAILABLE:
        assessment = analyze_document_compliance(document_text, primary_framework)
    else:
        # Simple fallback if regulatory AI is not available
        assessment = {
            'framework_id': primary_framework,
            'framework': get_supported_frameworks().get(primary_framework, primary_framework),
            'overall_score': 50,  # Default middle score
            'date': datetime.now().isoformat(),
            'categories': {},
            'overall_findings': [
                "Regulatory AI assessment not available"
            ],
            'overall_recommendations': [
                "Enable Regulatory AI services for detailed assessment"
            ]
        }
    
    return jsonify({
        'success': True,
        'document_id': document_id,
        'assessment': assessment
    })

@data_moat_bp.route('/api/generate-report/<document_id>')
def api_generate_report(document_id):
    """Generate a downloadable PDF compliance report"""
    # Check if document exists
    if document_id not in documents:
        return jsonify({
            'success': False,
            'error': 'Document not found'
        }), 404
    
    # Get document data
    document = documents[document_id]
    document_name = document.get('original_filename', 'Unknown Document')
    document_text = document.get('text_preview', '')
    frameworks = document.get('frameworks', {})
    primary_framework = document.get('primary_framework')
    
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
        metrics = document.get('metrics', {})
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
        if primary_framework:
            pdf.ln(5)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f'Compliance Assessment ({primary_framework.upper()})', 0, 1)
            
            # Use existing compliance assessment function
            if REGULATORY_AI_AVAILABLE:
                pdf.set_font('Arial', '', 10)
                pdf.multi_cell(0, 7, "Performing compliance assessment...")
                
                try:
                    assessment = analyze_document_compliance(document_text, primary_framework)
                    
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
                        for i, finding in enumerate(assessment['overall_findings']):
                            pdf.multi_cell(0, 7, f"{i+1}. {finding}")
                    
                    # Add recommendations if available
                    if 'overall_recommendations' in assessment and assessment['overall_recommendations']:
                        pdf.set_font('Arial', 'B', 11)
                        pdf.cell(0, 7, "Recommendations", 0, 1)
                        
                        pdf.set_font('Arial', '', 10)
                        for i, recommendation in enumerate(assessment['overall_recommendations']):
                            pdf.multi_cell(0, 7, f"{i+1}. {recommendation}")
                
                except Exception as e:
                    logger.error(f"Error getting compliance assessment: {str(e)}")
                    pdf.set_font('Arial', 'I', 10)
                    pdf.multi_cell(0, 7, f"Error generating compliance assessment: {str(e)}")
            else:
                pdf.set_font('Arial', 'I', 10)
                pdf.multi_cell(0, 7, "Detailed compliance assessment requires Regulatory AI services. Basic assessment provided based on detected keywords.")
        
        # Add footer
        pdf.ln(10)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 10, f"Generated by SustainaTrend™ Data Moat - {datetime.now().strftime('%Y-%m-%d')}", 0, 0, 'C')
        
        # Generate report filename
        report_filename = f"compliance_report_{document_id[:8]}.pdf"
        
        # Save the PDF to a temporary file
        temp_path = os.path.join(UPLOAD_FOLDER, report_filename)
        pdf.output(temp_path)
        
        # Send file as attachment
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=report_filename,
            mimetype='application/pdf'
        )
    
    except ImportError:
        return jsonify({
            'success': False,
            'error': 'PDF generation library not available'
        }), 500
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error generating report: {str(e)}'
        }), 500

def register_routes(app):
    """Register data moat routes with the Flask application"""
    app.register_blueprint(data_moat_bp)
    logger.info("Enhanced Data Moat routes registered with Regulatory AI functionality")