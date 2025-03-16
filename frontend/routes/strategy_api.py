"""
Strategy API routes for SustainaTrend Intelligence Platform

This module provides API endpoints for strategy-related functionality including
AI strategy generation, insights, and recommendations.
"""

import json
import logging
import sys
from flask import Blueprint, request, jsonify, current_app
from werkzeug.exceptions import BadRequest

# Set up logging
logger = logging.getLogger(__name__)

# Import strategy AI consultant functionality
try:
    sys.path.append('..')
    from strategy_ai_consultant import StrategyAIConsultant
    STRATEGY_AI_CONSULTANT_AVAILABLE = True
    strategy_ai = StrategyAIConsultant()
    logger.info("Strategy AI Consultant module loaded successfully in API")
except ImportError as e:
    STRATEGY_AI_CONSULTANT_AVAILABLE = False
    logger.warning(f"Strategy AI Consultant module import failed in API: {str(e)}")
    
    # Define fallback class for function signature compatibility
    class FallbackStrategyAI:
        def generate_ai_strategy(self, company_name, industry, focus_areas=None, trends=None):
            return {
                "status": "error",
                "message": "The Strategy AI Consultant module is not available. Please check your installation."
            }
    
    strategy_ai = FallbackStrategyAI()

def register_blueprint(bp):
    """
    Register strategy API routes with the given blueprint
    
    Args:
        bp: Flask blueprint to register routes with
    """
    @bp.route('/api/strategy/generate', methods=['POST'])
    def api_strategy_generate():
        """
        API endpoint to generate AI-powered strategy
        
        Accepts:
            - companyName: Name of the company
            - industry: Industry of the company
            - focusAreas: List of focus areas (optional)
            - trendInput: Trend analysis information (optional)
            
        Returns:
            JSON with strategy information
        """
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    "status": "error",
                    "message": "Please provide company name and industry information."
                }), 400
                
            # Extract required parameters
            company_name = data.get('companyName')
            industry = data.get('industry')
            
            if not company_name or not industry:
                return jsonify({
                    "status": "error",
                    "message": "Please provide both company name and industry."
                }), 400
                
            # Extract optional parameters
            focus_areas = data.get('focusAreas', '')
            trend_input = data.get('trendInput', '')
            
            # Generate strategy using AI consultant
            result = strategy_ai.generate_ai_strategy(
                company_name=company_name,
                industry=industry,
                focus_areas=focus_areas,
                trends=trend_input
            )
            
            return jsonify(result)
            
        except BadRequest as e:
            logger.error(f"Bad request error in strategy generation: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Bad request: {str(e)}"
            }), 400
        except Exception as e:
            logger.error(f"Error generating AI strategy: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "An error occurred while generating the strategy."
            }), 500
            
    @bp.route('/api/strategy/recommendations', methods=['POST'])
    def api_strategy_recommendations():
        """
        API endpoint to get recommendations based on an existing strategy
        
        Accepts:
            - company_name: Name of the company
            - industry: Industry of the company
            - strategy_points: List of existing strategy points
            
        Returns:
            JSON with recommended enhancements and improvements
        """
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    "success": False,
                    "error": "No data provided"
                }), 400
                
            # Extract parameters
            company_name = data.get('company_name')
            industry = data.get('industry')
            strategy_points = data.get('strategy_points', [])
            
            if not company_name or not industry or not strategy_points:
                return jsonify({
                    "success": False,
                    "error": "Missing required parameters"
                }), 400
                
            # Currently redirecting to generate_ai_strategy since we don't have a separate
            # recommendations function yet
            result = strategy_ai.generate_ai_strategy(
                company_name=company_name,
                industry=industry,
                focus_areas=None,
                trends=None
            )
            
            # Add recommendations-specific fields
            if result.get("status") == "success":
                result["recommendations"] = {
                    "enhancements": [
                        "Consider expanding your sustainability initiatives to include scope 3 emissions",
                        "Implement AI-powered analytics for real-time sustainability monitoring",
                        "Develop stakeholder engagement programs focused on sustainability education"
                    ],
                    "opportunities": [
                        "Partner with industry peers on collaborative sustainability initiatives",
                        "Explore green financing options for sustainability projects",
                        "Develop sustainability training programs for employees and suppliers"
                    ]
                }
                
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error generating strategy recommendations: {str(e)}")
            return jsonify({
                "success": False,
                "error": "Internal server error",
                "message": "An error occurred while generating strategy recommendations."
            }), 500
            
    logger.info("Strategy API routes registered successfully")