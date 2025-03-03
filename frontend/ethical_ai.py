"""
Ethical AI & Transparency Compliance Module

This module provides Flask routes for the Ethical AI compliance features
of the Sustainability Intelligence Platform.
"""

import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional, Union
from functools import wraps

# Flask will be imported in the register_routes function to avoid import errors
# when the module is initially loaded

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
ETHICAL_AI_AVAILABLE = True
FASTAPI_BASE_URL = os.getenv('FASTAPI_BASE_URL', 'http://localhost:8080')

def get_api_endpoint(endpoint: str) -> str:
    """Get the full URL for an API endpoint"""
    return f"{FASTAPI_BASE_URL}{endpoint}"

def handle_api_error(response):
    """Handle API error responses"""
    try:
        error_data = response.json()
        error_message = error_data.get('detail', 'Unknown error')
    except:
        error_message = f"Error: {response.status_code} - {response.text}"
    
    return {
        "status": "error",
        "message": error_message
    }

def configure_routes(app):
    """
    Configure Flask routes for Ethical AI compliance
    
    Args:
        app: Flask application
    """
    # Import Flask-specific functions within the function to avoid import errors
    from flask import render_template, request, jsonify
    
    @app.route('/ethical-ai')
    def ethical_ai_dashboard():
        """Ethical AI & Transparency Compliance Dashboard"""
        try:
            return render_template('ethical_ai.html')
        except Exception as e:
            logger.error(f"Error loading ethical AI dashboard: {str(e)}")
            return render_template('error.html', message=f"Error loading ethical AI dashboard: {str(e)}")
    
    @app.route('/api/ethical-ai/explain', methods=['POST'])
    def api_ethical_ai_explain():
        """API endpoint for generating explanations for AI-driven analysis"""
        try:
            data = request.get_json()
            
            # Forward the request to the backend
            response = requests.post(
                get_api_endpoint('/api/ethical-ai/explain'),
                json=data,
                timeout=30  # Longer timeout for AI processing
            )
            
            if response.status_code != 200:
                return jsonify(handle_api_error(response)), response.status_code
            
            return jsonify(response.json())
            
        except Exception as e:
            logger.error(f"Error in explain AI API: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Error processing request: {str(e)}"
            }), 500
    
    @app.route('/api/ethical-ai/detect-bias', methods=['POST'])
    def api_ethical_ai_detect_bias():
        """API endpoint for detecting bias in AI-generated analysis"""
        try:
            data = request.get_json()
            
            # Forward the request to the backend
            response = requests.post(
                get_api_endpoint('/api/ethical-ai/detect-bias'),
                json=data,
                timeout=30  # Longer timeout for AI processing
            )
            
            if response.status_code != 200:
                return jsonify(handle_api_error(response)), response.status_code
            
            return jsonify(response.json())
            
        except Exception as e:
            logger.error(f"Error in detect bias API: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Error processing request: {str(e)}"
            }), 500
    
    @app.route('/api/ethical-ai/check-compliance', methods=['POST'])
    def api_ethical_ai_check_compliance():
        """API endpoint for checking regulatory compliance"""
        try:
            data = request.get_json()
            
            # Forward the request to the backend
            response = requests.post(
                get_api_endpoint('/api/ethical-ai/check-compliance'),
                json=data,
                timeout=30  # Longer timeout for AI processing
            )
            
            if response.status_code != 200:
                return jsonify(handle_api_error(response)), response.status_code
            
            return jsonify(response.json())
            
        except Exception as e:
            logger.error(f"Error in check compliance API: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Error processing request: {str(e)}"
            }), 500
    
    @app.route('/api/ethical-ai/analyze-report', methods=['POST'])
    def api_ethical_ai_analyze_report():
        """API endpoint for analyzing sustainability report compliance"""
        try:
            data = request.get_json()
            
            # Forward the request to the backend
            response = requests.post(
                get_api_endpoint('/api/ethical-ai/analyze-report'),
                json=data,
                timeout=45  # Longer timeout for report analysis
            )
            
            if response.status_code != 200:
                return jsonify(handle_api_error(response)), response.status_code
            
            return jsonify(response.json())
            
        except Exception as e:
            logger.error(f"Error in analyze report API: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Error processing request: {str(e)}"
            }), 500
    
    @app.route('/api/ethical-ai/generate-documentation', methods=['POST'])
    def api_ethical_ai_generate_documentation():
        """API endpoint for generating compliance documentation"""
        try:
            data = request.get_json()
            
            # Forward the request to the backend
            response = requests.post(
                get_api_endpoint('/api/ethical-ai/generate-documentation'),
                json=data,
                timeout=30  # Longer timeout for documentation generation
            )
            
            if response.status_code != 200:
                return jsonify(handle_api_error(response)), response.status_code
            
            return jsonify(response.json())
            
        except Exception as e:
            logger.error(f"Error in generate documentation API: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Error processing request: {str(e)}"
            }), 500

def register_routes(app):
    """
    Register the Ethical AI compliance routes with a Flask application
    
    Args:
        app: Flask application
    """
    try:
        # Try to import Flask-specific modules here to avoid import errors
        from flask import render_template, request, jsonify
        
        # Configure routes
        configure_routes(app)
        
        logger.info("Ethical AI compliance routes configured")
        return True
    except Exception as e:
        logger.error(f"Failed to register Ethical AI compliance routes: {str(e)}")
        global ETHICAL_AI_AVAILABLE
        ETHICAL_AI_AVAILABLE = False
        return False