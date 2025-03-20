"""
Monetization Strategies routes for SustainaTrend Intelligence Platform

This module now redirects all routes to the consolidated Strategy Hub,
maintaining the API endpoints for backward compatibility.
"""

import json
import logging
from flask import Blueprint, render_template, request, jsonify, redirect, url_for

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

@monetization_bp.route('/api/monetization/analyze', methods=['POST'])
def api_monetization_analyze():
    """API endpoint for analyzing monetization opportunities"""
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

@monetization_bp.route('/api/monetization/strategy-frameworks')
def api_strategy_frameworks():
    """
    API endpoint for getting available strategy frameworks
    This endpoint is maintained for backward compatibility
    """
    # Forward the request to the Enhanced Strategy Hub API endpoint
    logger.info("Redirecting strategy frameworks API request to Enhanced Strategy Hub API")
    return redirect(url_for('enhanced_strategy.api_framework_recommendation'))