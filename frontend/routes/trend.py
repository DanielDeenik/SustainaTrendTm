"""
Trend Analysis routes for SustainaTrend Intelligence Platform
"""

import json
import logging
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request

# Import necessary functions from centralized utils module
from navigation_config import get_context_for_template
from utils import get_sustainability_trends, get_sustainability_metrics

# Create blueprint
trend_bp = Blueprint('trend', __name__)

# Configure logging
logger = logging.getLogger(__name__)

@trend_bp.route('/trend-analysis')
def trend_analysis():
    """
    AI-powered sustainability trend analysis page
    Shows trends, predictions, and insights for sustainability metrics
    """
    logger.info("Trend analysis route called")
    category = request.args.get('category', 'all')
    sort = request.args.get('sort', 'virality')
    
    # Include navigation for the template
    nav_context = get_context_for_template()
    
    # Get trend data using the centralized utility function
    trends = get_sustainability_trends()
    
    # Format trends for JSON serialization
    formatted_trends = json.dumps(trends, default=lambda o: o.isoformat() if isinstance(o, datetime) else str(o))
    
    # Use the consolidated dark themed template
    logger.info("Using consolidated dark themed template for trend analysis")
    return render_template(
        "finchat_dark_dashboard.html", 
        page_title="Sustainability Trend Analysis",
        template_type="trends",
        category=category,
        sort=sort,
        trends=trends,
        trends_json=formatted_trends,
        **nav_context  # Include all navigation context
    )

# Route removed to consolidate real estate functionality in realestate_bp blueprint
# Users should use /realestate/dashboard instead