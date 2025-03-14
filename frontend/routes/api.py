"""
API routes for SustainaTrend Intelligence Platform
"""

import json
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify

# Import necessary functions from centralized utils module
from navigation_config import get_context_for_template
from utils import (
    get_api_status, 
    get_sustainability_metrics, 
    get_sustainability_trends,
    get_sustainability_stories,
    get_ui_suggestions
)

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Configure logging
logger = logging.getLogger(__name__)

@api_bp.route('/metrics')
def api_metrics():
    """API endpoint for metrics data"""
    logger.info("API metrics endpoint called")
    
    try:
        # Get metrics using centralized utility
        metrics = get_sustainability_metrics()
        
        # Handle datetime serialization
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, datetime):
                    return o.isoformat()
                return super().default(o)
        
        return jsonify({
            "success": True,
            "data": metrics,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in API metrics: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/trends')
def api_trends():
    """API endpoint for sustainability trend data for React dashboard"""
    logger.info("API trends endpoint called")
    
    try:
        # Get trends using centralized utility
        trends = get_sustainability_trends()
        
        # Convert any non-serializable objects
        def convert_numeric_types(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return str(obj)
                
        return jsonify({
            "success": True,
            "data": json.loads(json.dumps(trends, default=convert_numeric_types)),
            "timestamp": datetime.now().isoformat(),
            "categories": list(set(t["category"] for t in trends if "category" in t))
        })
    except Exception as e:
        logger.error(f"Error in API trends: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/storytelling', methods=['POST'])
def api_storytelling_generate():
    """API endpoint to generate sustainability stories"""
    logger.info("API storytelling endpoint called")
    
    try:
        # Get request data
        request_data = request.json
        metrics = request_data.get('metrics', [])
        
        # If no metrics provided, get default metrics
        if not metrics:
            metrics = get_sustainability_metrics()
        
        # Get stories using centralized utility
        stories = get_sustainability_stories()
        
        return jsonify({
            "success": True,
            "stories": stories,
            "metrics_used": len(metrics),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in API storytelling: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/monetization-strategy', methods=['POST'])
def api_monetization_strategy():
    """API endpoint for monetization strategy requests"""
    logger.info("API monetization strategy endpoint called")
    
    try:
        # Get request data
        request_data = request.json
        
        # Generate monetization strategy
        result = {
            "success": True,
            "strategies": [
                {
                    "name": "ESG Data Subscription",
                    "description": "Subscription-based access to premium ESG data and metrics",
                    "potential": "High",
                    "implementation_timeline": "3-6 months",
                    "roi_estimate": "25-35%"
                },
                {
                    "name": "Sustainability Reporting as a Service",
                    "description": "Automated generation of compliance-ready sustainability reports",
                    "potential": "Medium-High",
                    "implementation_timeline": "6-12 months",
                    "roi_estimate": "20-30%"
                },
                {
                    "name": "AI-Powered ESG Consulting",
                    "description": "Premium consulting services backed by AI analytics",
                    "potential": "High",
                    "implementation_timeline": "Immediate",
                    "roi_estimate": "40-50%"
                }
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in API monetization strategy: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route("/omniparser/suggestions", methods=["GET"])
def omniparser_suggestions_flask():
    """API endpoint for dynamic search suggestions"""
    logger.info("API omniparser suggestions endpoint called")
    
    query = request.args.get("q", "")
    
    if not query:
        return jsonify({"suggestions": []})
    
    try:
        # Get suggestions using centralized utility
        suggestions = get_ui_suggestions(query)
        return jsonify(suggestions)
    except Exception as e:
        logger.error(f"Error in API omniparser suggestions: {str(e)}")
        return jsonify({"suggestions": []})

# Non-API routes that still belong in this blueprint
api_views_bp = Blueprint('api_views', __name__)

@api_views_bp.route("/api-status")
def api_status():
    """View for API status dashboard"""
    logger.info("API status route called")
    
    # Include navigation for the template
    nav_context = get_context_for_template()
    
    # Get API status using centralized utility
    status = get_api_status()
    
    # Use the dark themed dashboard with different template_type
    logger.info("Using dark themed dashboard for API status")
    return render_template(
        "finchat_dark_dashboard.html", 
        page_title="API Status Dashboard",
        template_type="api-status",
        api_status=status,
        **nav_context  # Include all navigation context
    )

@api_views_bp.route("/debug")
def debug_info():
    """Debug endpoint for checking app status and configuration"""
    logger.info("Debug route called")
    
    # Include navigation for the template
    nav_context = get_context_for_template()
    
    # Use the dark themed dashboard with different template_type
    logger.info("Using dark themed dashboard for debug info")
    return render_template(
        "finchat_dark_dashboard.html", 
        page_title="Debug Information",
        template_type="debug",
        app_routes=[r.endpoint for r in request.app.url_map.iter_rules()],
        **nav_context  # Include all navigation context
    )