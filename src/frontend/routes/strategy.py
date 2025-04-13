"""
Strategy routes for the SustainaTrend™ Intelligence Platform.

This module provides both web routes and API endpoints for strategy-related functionality,
including AI strategy generation, insights, and recommendations.
"""

import json
import logging
import sys
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, current_app
from werkzeug.exceptions import BadRequest

# Set up logging
logger = logging.getLogger(__name__)

# Create Blueprint
strategy_bp = Blueprint('strategy', __name__)

# Import strategy AI consultant functionality
try:
    sys.path.append('..')
    from strategy_ai_consultant import StrategyAIConsultant
    STRATEGY_AI_CONSULTANT_AVAILABLE = True
    strategy_ai = StrategyAIConsultant()
    logger.info("Strategy AI Consultant module loaded successfully")
except ImportError as e:
    STRATEGY_AI_CONSULTANT_AVAILABLE = False
    logger.warning(f"Strategy AI Consultant module import failed: {str(e)}")
    
    class FallbackStrategyAI:
        def generate_ai_strategy(self, company_name, industry, focus_areas=None, trend_analysis=None):
            return {
                "status": "error",
                "message": "The Strategy AI Consultant module is not available. Please check your installation."
            }
    
    strategy_ai = FallbackStrategyAI()

# Web Routes
@strategy_bp.route('/strategy')
def strategy_dashboard():
    """Render the strategy dashboard."""
    try:
        return render_template('strategy/dashboard.html')
    except Exception as e:
        logger.error(f"Error rendering strategy dashboard: {str(e)}")
        return render_template('errors/500.html'), 500

@strategy_bp.route('/strategy/recommendations')
def get_recommendations():
    """Get sustainability strategy recommendations."""
    return jsonify({
        'status': 'success',
        'recommendations': []
    })

@strategy_bp.route('/strategy/data')
def get_strategy_data():
    """Get strategy data."""
    try:
        return jsonify({
            'strategies': [
                {
                    'name': 'Carbon Reduction',
                    'status': 'active',
                    'progress': 75,
                    'metrics': {
                        'emissions_reduced': 120,
                        'target': 150,
                        'unit': 'tonnes CO2e'
                    }
                },
                {
                    'name': 'Renewable Energy',
                    'status': 'active',
                    'progress': 60,
                    'metrics': {
                        'energy_generated': 250,
                        'target': 400,
                        'unit': 'MWh'
                    }
                }
            ]
        })
    except Exception as e:
        logger.error(f"Error getting strategy data: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# API Routes
@strategy_bp.route('/api/strategy/generate', methods=['POST'])
def api_strategy_generate():
    """Generate a sustainability strategy."""
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("No data provided")
            
        company_name = data.get('company_name')
        industry = data.get('industry')
        focus_areas = data.get('focus_areas', [])
        trend_analysis = data.get('trend_analysis')
        
        if not company_name or not industry:
            raise BadRequest("Company name and industry are required")
            
        strategy = strategy_ai.generate_ai_strategy(
            company_name=company_name,
            industry=industry,
            focus_areas=focus_areas,
            trend_analysis=trend_analysis
        )
        
        return jsonify(strategy)
    except BadRequest as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Error generating strategy: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@strategy_bp.route('/api/strategy/recommendations', methods=['POST'])
def api_strategy_recommendations():
    """Get AI-powered strategy recommendations."""
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("No data provided")
            
        company_name = data.get('company_name')
        industry = data.get('industry')
        current_strategies = data.get('current_strategies', [])
        
        if not company_name or not industry:
            raise BadRequest("Company name and industry are required")
            
        recommendations = strategy_ai.generate_recommendations(
            company_name=company_name,
            industry=industry,
            current_strategies=current_strategies
        )
        
        return jsonify({
            'status': 'success',
            'recommendations': recommendations
        })
    except BadRequest as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500