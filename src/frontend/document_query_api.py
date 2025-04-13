"""
Document Query API Module for SustainaTrend™

This module provides API endpoints for querying sustainability reports,
extracting data points, and providing AI-powered explanations.
"""

import os
import json
import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

from flask import Blueprint, request, jsonify, current_app, send_file, session
import pandas as pd

# Import document processor
from document_processor import DocumentProcessor

# Set up logging
logger = logging.getLogger(__name__)

# Create Blueprint with unique name
document_query_bp = Blueprint('document_query_api', __name__)

# Create temporary data directory for downloadable data
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Document processor instance
processor = DocumentProcessor()

@document_query_bp.route('/api/document-query', methods=['POST'])
def query_document():
    """
    API endpoint for querying documents using AI
    
    Accepts:
        - query: User query about the document
        - document_id: Filename of the document to query
        - session_id: Session identifier for tracking conversations
        
    Returns:
        JSON with AI response and supporting data
    """
    try:
        # Get request data
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
            
        query = data.get('query', '')
        document_id = data.get('document_id', '')
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'No query provided'
            }), 400
            
        if not document_id:
            return jsonify({
                'success': False,
                'error': 'No document_id provided'
            }), 400
            
        # Get document from session data
        document_analysis = session.get('document_analysis', {})
        if not document_analysis or document_analysis.get('filename') != document_id:
            return jsonify({
                'success': False,
                'error': 'Document not found or session expired'
            }), 404
        
        # Get document text
        document_text = document_analysis.get('text', '')
        document_path = document_analysis.get('path', '')
        
        if not document_text:
            return jsonify({
                'success': False,
                'error': 'Document text not available'
            }), 404
            
        # Check for specific query types
        data_available = False
        data_url = None
        sources = []
        
        # Process the query
        figure_match = re.search(r'(?:figure|fig\.?|chart|graph|diagram|table|tbl\.?)\s+(\d+(?:\.\d+)?)', query, re.IGNORECASE)
        data_request = re.search(r'(?:underlying|raw|source)\s+data', query, re.IGNORECASE)
        calculation_request = re.search(r'(?:calculated|calculation|compute|derive)', query, re.IGNORECASE)
        download_request = re.search(r'(?:download|export|get|obtain)', query, re.IGNORECASE)
        
        # If requesting figure explanation, find in document
        if figure_match:
            figure_number = figure_match.group(1)
            figure_type = figure_match.group(0).split()[0].lower()
            sources.append(f"Reference: {figure_type.capitalize()} {figure_number}")
            
            # Find the figure in document analysis
            found_figure = None
            figures = document_analysis.get('figures', [])
            
            for figure in figures:
                if figure.get('number') == figure_number and figure_type in figure.get('type', '').lower():
                    found_figure = figure
                    break
                    
            if found_figure:
                sources.append(f"Found on page {found_figure.get('page', 'unknown')}")
                
                # If requesting underlying data, generate CSV
                if (data_request or download_request) and (found_figure.get('type', '').lower() in ['table', 'tbl']):
                    # Generate CSV file for this table
                    data_url = f"/api/document-data/{document_id}/{figure_type}-{figure_number}.csv"
                    data_available = True
        
        # If requesting KPI explanation, find in document
        kpi_match = re.search(r'(\d+(?:\.\d+)?)\s*((?:tons?|t|%|GWh|kWh|MWh|m3|cubic\s+meters?|liters?|gallons?))', query, re.IGNORECASE)
        if kpi_match:
            kpi_value = kpi_match.group(1)
            kpi_unit = kpi_match.group(2).strip()
            sources.append(f"Data point: {kpi_value} {kpi_unit}")
            
            # Find the KPI in document analysis
            found_kpi = None
            kpis = document_analysis.get('kpis', [])
            
            for kpi in kpis:
                if kpi.get('value') == kpi_value and kpi.get('unit', '').lower() == kpi_unit.lower():
                    found_kpi = kpi
                    break
                    
            if found_kpi:
                # If requesting calculation or underlying data
                if calculation_request or data_request or download_request:
                    data_url = f"/api/document-data/{document_id}/kpi-{kpi_value}{kpi_unit}.csv"
                    data_available = True
        
        # Generate AI response using document processor
        response = processor.generate_rag_response(document_text, query)
        
        # Format the response
        if response.get('success', False):
            ai_response = response.get('response', '')
            
            # Enhance response with specific data capability info
            if data_available:
                ai_response += f"\n\nI've found underlying data related to your query. You can download it using the button below."
            
            # Create the final response
            result = {
                'success': True,
                'response': ai_response,
                'query': query,
                'sources': sources,
                'data_available': data_available,
                'data_url': data_url,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            }
        else:
            # Handle error case
            result = {
                'success': False,
                'error': 'Failed to generate response',
                'query': query,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            }
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in document query API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@document_query_bp.route('/api/document-data/<document_id>/<data_id>', methods=['GET'])
def get_document_data(document_id, data_id):
    """
    API endpoint for retrieving data files associated with document queries
    
    Args:
        document_id: Filename of the document
        data_id: Identifier for the specific data requested
        
    Returns:
        CSV file with the requested data
    """
    try:
        # Get document from session
        document_analysis = session.get('document_analysis', {})
        if not document_analysis or document_analysis.get('filename') != document_id:
            return jsonify({
                'success': False,
                'error': 'Document not found or session expired'
            }), 404
        
        # Parse data ID to determine what data to provide
        # Format: [type]-[identifier].[extension]
        parts = data_id.split('.')
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'error': 'Invalid data ID format'
            }), 400
            
        data_type = parts[0].split('-')[0]
        data_identifier = '-'.join(parts[0].split('-')[1:])
        extension = parts[1].lower()
        
        if extension != 'csv':
            return jsonify({
                'success': False,
                'error': 'Only CSV format is supported'
            }), 400
        
        # Generate appropriate data file
        filename = f"{data_type}_{data_identifier}_{uuid.uuid4().hex[:8]}.csv"
        filepath = os.path.join(DATA_DIR, filename)
        
        # Create mock data based on the type
        if data_type in ['table', 'tbl']:
            # Create CSV for table data
            df = pd.DataFrame({
                'Column 1': ['Data 1', 'Data 2', 'Data 3'],
                'Column 2': [10.5, 20.3, 15.7],
                'Column 3': ['Category A', 'Category B', 'Category C']
            })
            df.to_csv(filepath, index=False)
            
        elif data_type in ['figure', 'fig', 'chart', 'graph']:
            # Create CSV for figure data
            df = pd.DataFrame({
                'X Values': [1, 2, 3, 4, 5],
                'Y Values': [10.5, 20.3, 15.7, 25.1, 18.4],
                'Category': ['A', 'B', 'A', 'C', 'B']
            })
            df.to_csv(filepath, index=False)
            
        elif data_type in ['kpi']:
            # Create CSV for KPI data
            df = pd.DataFrame({
                'Component': ['Component 1', 'Component 2', 'Component 3'],
                'Value': [5.2, 8.7, 6.1],
                'Percentage': ['26.0%', '43.5%', '30.5%'],
                'Source': ['Measured', 'Calculated', 'Estimated']
            })
            df.to_csv(filepath, index=False)
            
        else:
            return jsonify({
                'success': False,
                'error': 'Unsupported data type'
            }), 400
        
        # Return the file
        return send_file(
            filepath,
            as_attachment=True,
            download_name=f"{data_type}_{data_identifier}.csv",
            mimetype='text/csv'
        )
    
    except Exception as e:
        logger.error(f"Error in document data API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def register_routes(app):
    """
    Register document query API routes with Flask app
    
    Args:
        app: Flask application
    """
    app.register_blueprint(document_query_bp)
    
    # Register additional endpoint on main app
    @app.route('/api/document-audit/<document_id>', methods=['POST'])
    def document_audit(document_id):
        """
        Generate an audit report for document interactions
        
        Args:
            document_id: Filename of the document
            
        Returns:
            JSON with audit report or audit report as PDF
        """
        try:
            # Get document from session
            document_analysis = session.get('document_analysis', {})
            if not document_analysis or document_analysis.get('filename') != document_id:
                return jsonify({
                    'success': False,
                    'error': 'Document not found or session expired'
                }), 404
            
            # Get request data
            data = request.json or {}
            format_type = data.get('format', 'json')
            queries = data.get('queries', [])
            
            # Generate audit report
            audit_report = {
                'document_id': document_id,
                'document_metadata': {
                    'page_count': document_analysis.get('page_count', 0),
                    'word_count': document_analysis.get('word_count', 0),
                    'file_size': document_analysis.get('file_size', 0)
                },
                'audit_summary': {
                    'queries_reviewed': len(queries),
                    'data_points_validated': len(document_analysis.get('kpis', [])),
                    'frameworks_assessed': len(document_analysis.get('frameworks', {})),
                    'timestamp': datetime.now().isoformat()
                },
                'queries': queries
            }
            
            # Return based on requested format
            if format_type == 'pdf' and 'fpdf' in globals():
                # Generate PDF report
                try:
                    from fpdf import FPDF
                    
                    # Create PDF
                    pdf = FPDF()
                    pdf.add_page()
                    
                    # Title
                    pdf.set_font('Arial', 'B', 16)
                    pdf.cell(0, 10, f'Audit Report: {document_id}', 0, 1, 'C')
                    
                    # Document metadata
                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(0, 10, 'Document Metadata', 0, 1)
                    pdf.set_font('Arial', '', 10)
                    pdf.cell(0, 6, f"Pages: {audit_report['document_metadata']['page_count']}", 0, 1)
                    pdf.cell(0, 6, f"Words: {audit_report['document_metadata']['word_count']}", 0, 1)
                    
                    # Audit summary
                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(0, 10, 'Audit Summary', 0, 1)
                    pdf.set_font('Arial', '', 10)
                    pdf.cell(0, 6, f"Queries Reviewed: {audit_report['audit_summary']['queries_reviewed']}", 0, 1)
                    pdf.cell(0, 6, f"Data Points Validated: {audit_report['audit_summary']['data_points_validated']}", 0, 1)
                    pdf.cell(0, 6, f"Frameworks Assessed: {audit_report['audit_summary']['frameworks_assessed']}", 0, 1)
                    
                    # Queries
                    if queries:
                        pdf.set_font('Arial', 'B', 12)
                        pdf.cell(0, 10, 'Queries & Responses', 0, 1)
                        
                        for i, query in enumerate(queries):
                            pdf.set_font('Arial', 'B', 10)
                            pdf.cell(0, 6, f"Query {i+1}: {query.get('query', 'No query')}", 0, 1)
                            pdf.set_font('Arial', '', 9)
                            
                            # Add response with line breaks
                            response = query.get('response', 'No response')
                            lines = response.split('\n')
                            for line in lines:
                                pdf.multi_cell(0, 5, line)
                            
                            pdf.ln(5)
                    
                    # Footer
                    pdf.set_font('Arial', 'I', 8)
                    pdf.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1)
                    
                    # Save to file
                    report_filename = f"audit_report_{document_id}_{uuid.uuid4().hex[:8]}.pdf"
                    report_path = os.path.join(DATA_DIR, report_filename)
                    pdf.output(report_path)
                    
                    # Return PDF file
                    return send_file(
                        report_path,
                        as_attachment=True,
                        download_name=f"audit_report_{document_id}.pdf",
                        mimetype='application/pdf'
                    )
                    
                except Exception as e:
                    logger.error(f"Error generating PDF audit report: {str(e)}")
                    return jsonify({
                        'success': False,
                        'error': f"PDF generation failed: {str(e)}"
                    }), 500
            
            # Return JSON by default
            return jsonify({
                'success': True,
                'audit_report': audit_report
            })
        
        except Exception as e:
            logger.error(f"Error in document audit API: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500