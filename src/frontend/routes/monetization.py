"""
Monetization Strategies routes for SustainaTrend Intelligence Platform

This module now redirects all routes to the consolidated Strategy Hub,
maintaining the API endpoints for backward compatibility.
"""

import json
import logging
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, send_file

# Import necessary functions from centralized utils module
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from navigation_config import get_context_for_template
from monetization_strategies import (
    analyze_monetization_opportunities,
    generate_monetization_opportunities,
    get_monetization_strategies,
    generate_integrated_strategic_plan
)

# Import strategy frameworks for API endpoints (if available) or use fallback
try:
    from strategy_simulation import STRATEGY_FRAMEWORKS
except ImportError:
    # Fallback if the strategy_simulation module is not available
    STRATEGY_FRAMEWORKS = {
        "porters": {
            "name": "Porter's Five Forces",
            "description": "Analyze competitive forces shaping sustainability positioning",
            "icon": "chart-bar"
        },
        "swot": {
            "name": "SWOT Analysis",
            "description": "Evaluate strengths, weaknesses, opportunities and threats",
            "icon": "grid-2x2"
        },
        "bcg": {
            "name": "BCG Growth-Share Matrix",
            "description": "Prioritize investments based on market growth and share",
            "icon": "pie-chart"
        }
    }

# Create blueprint
monetization_bp = Blueprint('monetization', __name__)

# Configure logging
logger = logging.getLogger(__name__)

@monetization_bp.route('/monetization-strategies')
@monetization_bp.route('/monetization-opportunities')  # Added route to match navigation
def monetization_strategies_dashboard():
    """
    Monetization Strategies Dashboard - Redirects to Enhanced Strategy Hub
    All monetization functionality is now consolidated in the Enhanced Strategy Hub
    """
    logger.info("Redirecting monetization route to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@monetization_bp.route('/api/monetization/analyze', methods=['POST', 'GET'])
def api_monetization_analyze():
    """API endpoint for analyzing monetization opportunities"""
    if request.method == 'POST':
        data = request.get_json()
        
        if not data or 'document_text' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing document_text parameter'
            }), 400
        
        document_text = data['document_text']
        result = analyze_monetization_opportunities(document_text)
        
        return jsonify({
            'success': True,
            'analysis': result
        })
    else:  # GET method
        # Get strategy_id from query parameters
        strategy_id = request.args.get('strategy_id')
        
        if not strategy_id:
            return jsonify({
                'success': False,
                'error': 'Missing strategy_id parameter'
            }), 400
        
        # Get available strategies
        strategies = get_monetization_strategies()
        
        # Check if strategy exists
        if strategy_id not in strategies:
            return jsonify({
                'success': False,
                'error': f'Strategy with ID {strategy_id} not found'
            }), 404
        
        # Get the strategy
        strategy = strategies[strategy_id]
        
        # Calculate potential score (simulated for now)
        potential_score = 75  # This would be calculated based on actual data
        
        return jsonify({
            'success': True,
            'strategy_id': strategy_id,
            'strategy_name': strategy['name'],
            'potential_score': potential_score,
            'recommendation': f"This {strategy['name']} strategy has strong potential for your sustainability initiatives."
        })

@monetization_bp.route('/api/monetization/opportunities', methods=['POST'])
def api_monetization_opportunities():
    """API endpoint for generating monetization opportunities"""
    data = request.get_json()
    
    if not data or 'document_text' not in data:
        return jsonify({
            'success': False,
            'error': 'Missing document_text parameter'
        }), 400
    
    document_text = data['document_text']
    result = generate_monetization_opportunities(document_text)
    
    return jsonify({
        'success': True,
        'opportunities': result
    })

@monetization_bp.route('/monetization-opportunities/strategic-plan')
def integrated_strategy_plan():
    """
    Integrated Strategy Plan - Redirects to Enhanced Strategy Hub
    All strategic planning is now consolidated in the Enhanced Strategy Hub
    """
    logger.info("Redirecting monetization strategic plan to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@monetization_bp.route('/api/monetization/strategic-plan', methods=['POST'])
def api_strategic_plan():
    """API endpoint for generating strategic monetization plan"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'Missing request data'
        }), 400
    
    company_name = data.get('company_name', 'Your Company')
    industry = data.get('industry', 'Technology')
    document_text = data.get('document_text', '')
    
    # Generate strategic plan using the imported function
    plan = generate_integrated_strategic_plan(company_name, industry, document_text)
    
    return jsonify({
        'success': True,
        'plan': plan
    })

@monetization_bp.route('/monetization-strategy-consulting')
def monetization_strategy_consulting():
    """
    Monetization Strategy Consulting Dashboard - Redirects to Enhanced Strategy Hub
    All consulting functionality is now consolidated in the Enhanced Strategy Hub
    """
    logger.info("Redirecting monetization strategy consulting to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@monetization_bp.route('/monetization-strategy/framework/<framework_id>')
def monetization_strategy_framework(framework_id):
    """
    Specific Monetization Strategy Framework - Redirects to Enhanced Strategy Hub
    All framework analysis is now consolidated in the Enhanced Strategy Hub
    """
    logger.info(f"Redirecting monetization framework {framework_id} to Enhanced Strategy Hub")
    return redirect(url_for('enhanced_strategy.framework_selection_guide'))

@monetization_bp.route('/api/monetization/export-plan', methods=['POST'])
def api_export_strategic_plan():
    """API endpoint for exporting strategic monetization plan as PDF"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Missing request data'
            }), 400
        
        company_name = data.get('company_name', 'Your Company')
        plan_html = data.get('plan_html', '')
        
        # In a production environment, this would use a PDF generation library
        # like FPDF, WeasyPrint, or another HTML-to-PDF converter
        try:
            from fpdf import FPDF
            
            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Set font
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, f'Strategic Plan for {company_name}', 0, 1, 'C')
            
            # Add content (simplified - in production would parse HTML properly)
            pdf.set_font('Arial', '', 12)
            pdf.multi_cell(0, 10, 'This strategic plan outlines monetization opportunities based on your sustainability initiatives.')
            pdf.ln(10)
            
            # Export as bytes
            pdf_bytes = pdf.output(dest='S').encode('latin1')
            
            # Return PDF file
            from io import BytesIO
            
            return send_file(
                BytesIO(pdf_bytes),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"{company_name.replace(' ', '_')}_Strategic_Plan.pdf"
            )
            
        except ImportError:
            # If FPDF is not available, return a JSON response indicating the PDF would be generated
            logger.warning("FPDF not available for PDF generation - returning success message only")
            return jsonify({
                'success': True,
                'message': 'PDF would be generated here in production environment'
            })
            
    except Exception as e:
        logger.error(f"Error exporting strategic plan: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500

@monetization_bp.route('/api/monetization/strategy-frameworks')
def api_strategy_frameworks():
    """
    API endpoint for getting available strategy frameworks
    This endpoint is maintained for backward compatibility
    """
    # Forward the request to the Enhanced Strategy Hub API endpoint
    logger.info("Redirecting strategy frameworks API request to Enhanced Strategy Hub API")
    return redirect(url_for('enhanced_strategy.api_framework_recommendation'))