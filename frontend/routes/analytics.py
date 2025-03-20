"""
Analytics routes for SustainaTrend Intelligence Platform
"""

import json
import logging
from datetime import datetime
from flask import Blueprint, render_template, request

# Import necessary functions from centralized utils module
from navigation_config import get_context_for_template
from utils import get_api_status, get_sustainability_metrics, get_sustainability_stories

# Create blueprint
analytics_bp = Blueprint('analytics', __name__)

# Configure logging
logger = logging.getLogger(__name__)

@analytics_bp.route('/')
def home():
    """Home AI Trends Feed - Main entry point with sustainability trends"""
    logger.info("Home route called")
    
    # Include navigation for the template
    nav_context = get_context_for_template()
    
    # Get current API status for display
    api_status = get_api_status()
    
    # Use finchat_dark_dashboard.html for consistent dark theme UI
    logger.info("Using Finchat dark dashboard template")
    return render_template(
        "finchat_dark_dashboard.html", 
        page_title="SustainaTrend™ Intelligence Platform",
        template_type="home",
        api_status=api_status,
        **nav_context  # Include all navigation context
    )

@analytics_bp.route('/dashboard')
def dashboard():
    """Unified dashboard page combining sustainability metrics and key indicators"""
    logger.info("Dashboard route called")
    
    # Include navigation for the template
    nav_context = get_context_for_template()
    
    # Get sustainability metrics
    metrics = get_sustainability_metrics()
    
    # Format metrics for dashboard display
    formatted_metrics = json.dumps(metrics, default=lambda o: o.isoformat() if isinstance(o, datetime) else str(o))
    
    # Use the dark themed dashboard
    logger.info("Using Finchat dark dashboard template")
    return render_template(
        "finchat_dark_dashboard.html", 
        page_title="Sustainability Intelligence Dashboard",
        template_type="dashboard",
        metrics=metrics,
        metrics_json=formatted_metrics,
        **nav_context  # Include all navigation context
    )

@analytics_bp.route('/monetization-strategies', methods=['GET'])
def monetization_strategies_dashboard():
    """Monetization strategies dashboard - redirects to enhanced strategy hub"""
    from flask import redirect, url_for
    logger.info("Monetization strategies dashboard called - redirecting to enhanced strategy hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

@analytics_bp.route('/story-cards')
def story_cards():
    """Story cards presentation for sustainability storytelling"""
    logger.info("Story cards route called")
    
    # Include navigation for the template
    nav_context = get_context_for_template()
    
    # Get sustainability stories
    stories = get_sustainability_stories()
    
    # Format stories for display
    formatted_stories = json.dumps(stories, default=lambda o: o.isoformat() if isinstance(o, datetime) else str(o))
    
    # Use finchat_dark_dashboard.html with template_type="stories"
    logger.info("Using dark themed story cards template")
    return render_template(
        'finchat_dark_dashboard.html',
        page_title="Sustainability Story Cards",
        template_type="stories",
        stories=stories,
        stories_json=formatted_stories,
        **nav_context  # Include all navigation context
    )