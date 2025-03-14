"""
Real Estate Sustainability routes for SustainaTrend Intelligence Platform
"""

import json
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, render_template, request, jsonify, Response, stream_with_context
from navigation_config import get_context_for_template
from realestate_sustainability import (
    get_real_estate_metrics,
    calculate_realestate_trends,
    get_realestate_trend_analysis,
    REALESTATE_CATEGORIES,
    NumPyJSONEncoder
)

# Create blueprint
realestate_bp = Blueprint('realestate', __name__)

# Configure logging
logger = logging.getLogger(__name__)

@realestate_bp.route('/realestate-trends')
def realestate_trends():
    """Real Estate Sustainability Trends Dashboard"""
    logger.info("Real Estate Sustainability Trends route called")
    
    # Include navigation for the template
    nav_context = get_context_for_template()
    
    # Get sustainability metrics
    metrics = get_real_estate_metrics()
    
    # Calculate trends
    trends = calculate_realestate_trends(metrics)
    
    # Use the consolidated dark themed template
    logger.info("Using consolidated dark themed template for real estate trends")
    return render_template(
        "finchat_dark_dashboard.html", 
        page_title="Real Estate Trends",
        template_type="realestate",
        section="trends",
        metrics=metrics,
        trends=trends,
        **nav_context  # Include all navigation context
    )

@realestate_bp.route('/realestate/dashboard')
@realestate_bp.route('/realestate-unified-dashboard')  # Keep for backward compatibility
def realestate_dashboard():
    """Unified Real Estate Sustainability Dashboard with BREEAM & Extended Metrics"""
    logger.info("Real Estate Sustainability Dashboard route called")
    
    # Get category filter if provided
    category = request.args.get('category', None)
    
    # Get trend data
    trend_data = get_realestate_trend_analysis(category)
    
    # Get metrics data for the dashboard
    metrics = get_real_estate_metrics()
    
    # Include navigation for the template
    nav_context = get_context_for_template()
    
    logger.info("Rendering unified real estate dashboard in consolidated template")
    
    return render_template(
        "finchat_dark_dashboard.html",
        page_title="Real Estate Dashboard",
        template_type="realestate",
        trends=trend_data['trends'],
        trend_chart_data=json.dumps(trend_data['chart_data'], cls=NumPyJSONEncoder),
        metrics=metrics,  # Add metrics to the template context
        category=category or 'all',
        categories=REALESTATE_CATEGORIES,
        sort="virality",
        view_mode="unified",
        **nav_context  # Include all navigation context
    )

@realestate_bp.route('/api/realestate-trends')
def api_realestate_trends():
    """API endpoint for real estate sustainability trends data"""
    # Get category filter if provided
    category = request.args.get('category', None)
    
    # Get trend data using the function we have available
    trend_data = get_realestate_trend_analysis(category)
    
    # Use a custom JSON encoder that handles numpy types
    response_data = {
        'success': True,
        'trends': trend_data['trends'],
        'chart_data': trend_data['chart_data']
    }
    
    return Response(
        json.dumps(response_data, cls=NumPyJSONEncoder),
        mimetype='application/json'
    )