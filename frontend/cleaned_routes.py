"""
Streamlined Routes Module for SustainaTrend™ Intelligence Platform

This module provides a clean, minimal structure for all routes in the application,
focusing on AI-driven storytelling with minimal UI and clear data visualization.
"""
import logging
import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add the current directory to the path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Ensure Flask is available
try:
    # Import Flask-related modules
    from flask import Flask, render_template, jsonify, request, redirect, url_for, abort, session
except ImportError:
    logging.error("Flask is not available. Make sure it's installed.")
    raise

# Import functions from direct_app
from direct_app import (
    get_sustainability_metrics,
    perform_enhanced_search,
    perform_ai_search,
    get_mock_stories
)

# Configure logging
logger = logging.getLogger(__name__)

def register_routes(app):
    """
    Register all routes for the SustainaTrend™ Intelligence Platform
    
    Args:
        app: Flask application
    """
    logger.info("Registering main application routes")
    
    # Import navigation configuration once
    from navigation_config import get_context_for_template, get_navigation_structure
    
    # -------------------------------------------------------------------------
    # Core Pages - Aligned with the new streamlined structure
    # -------------------------------------------------------------------------
    
    @app.route('/')
    def home():
        """Home AI Trends Feed - Entry point with AI-curated sustainability trends"""
        logger.info("Home AI Trends Feed accessed")
        nav_context = get_context_for_template()
        metrics = get_sustainability_metrics()
        
        # Ensure consistent metrics format
        if isinstance(metrics, list):
            metrics_data = {"metrics": metrics}
        else:
            metrics_data = metrics
            
        # Using the unified dark analytics dashboard template
        return render_template(
            "analytics_dashboard_dark.html",
            template_type="home",
            metrics=metrics_data,
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="home"
        )
    
    @app.route('/dashboard')
    def dashboard():
        """Unified dashboard page combining sustainability metrics and key indicators"""
        logger.info("Unified Dashboard accessed")
        nav_context = get_context_for_template()
        metrics = get_sustainability_metrics()
        
        # Ensure consistent metrics format
        if isinstance(metrics, list):
            metrics_data = {"metrics": metrics}
        else:
            metrics_data = metrics
        
        # Using the unified dark analytics dashboard template
        return render_template(
            "analytics_dashboard_dark.html",
            metrics=metrics_data,
            template_type="dashboard",
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="dashboard"
        )
    
    @app.route('/risk-tracker')
    def risk_tracker():
        """Risk Tracker - Real-time sustainability risk monitoring dashboard"""
        logger.info("Risk Tracker accessed")
        nav_context = get_context_for_template()
        metrics = get_sustainability_metrics()
        
        # Ensure consistent metrics format
        if isinstance(metrics, list):
            metrics_data = {"metrics": metrics}
        else:
            metrics_data = metrics
        
        categories = set()
        if metrics_data and "metrics" in metrics_data:
            for metric in metrics_data["metrics"]:
                if "category" in metric:
                    categories.add(metric["category"])
        
        # Using the unified dark analytics dashboard template
        return render_template(
            "analytics_dashboard_dark.html",
            metrics=metrics_data,
            categories=list(categories),
            template_type="risk_tracker",
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="risk"
        )
    
    @app.route('/analytics-dashboard')
    def analytics_dashboard():
        """Analytics Dashboard - Advanced visualization of sustainability metrics"""
        logger.info("Analytics Dashboard accessed")
        nav_context = get_context_for_template()
        # Using the unified dark analytics dashboard template
        return render_template(
            "analytics_dashboard_dark.html",
            template_type="analytics",
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="analytics"
        )
    
    @app.route('/story-cards')
    def story_cards():
        """Story Cards - AI-generated sustainability narratives and insights"""
        logger.info("Story Cards Generator accessed")
        nav_context = get_context_for_template()
        stories = get_mock_stories()
        # Using the unified dark analytics dashboard template
        return render_template(
            "analytics_dashboard_dark.html", 
            stories=stories,
            template_type="stories",
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="stories"
        )
    
    @app.route('/pdf-analyzer')
    def pdf_analyzer():
        """PDF Analyzer - Intelligent document processing for sustainability reports"""
        logger.info("PDF Analyzer accessed")
        nav_context = get_context_for_template()
        # Using the unified dark analytics dashboard template
        return render_template(
            "analytics_dashboard_dark.html",
            template_type="documents",
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="documents"
        )
    
    @app.route('/data-terminal')
    def data_terminal():
        """Data Terminal - Minimal API interface for programmatic data access"""
        logger.info("Data Terminal accessed")
        nav_context = get_context_for_template()
        # Using the unified dark analytics dashboard template
        return render_template(
            "analytics_dashboard_dark.html",
            template_type="terminal",
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="terminal"
        )
    
    @app.route('/monetization-opportunities')
    def monetization_opportunities():
        """Monetization Opportunities - Strategic insights for sustainable business models"""
        logger.info("Monetization Opportunities accessed")
        nav_context = get_context_for_template()
        # Using the unified dark analytics dashboard template
        return render_template(
            "analytics_dashboard_dark.html",
            template_type="monetization",
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="monetization"
        )
    
    @app.route('/co-pilot')
    def co_pilot():
        """Sustainability Co-Pilot - Contextual AI assistant for sustainability intelligence"""
        logger.info("Sustainability Co-Pilot accessed")
        nav_context = get_context_for_template()
        query = request.args.get('query', '')
        # Using the unified dark analytics dashboard template
        return render_template(
            "analytics_dashboard_dark.html", 
            query=query,
            template_type="copilot",
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="copilot"
        )
    
    # -------------------------------------------------------------------------
    # API Routes - Minimal, unified API endpoints for data access
    # -------------------------------------------------------------------------
    
    @app.route('/api/metrics')
    def api_metrics():
        """API endpoint for metrics data"""
        logger.info("API metrics endpoint accessed")
        metrics = get_sustainability_metrics()
        return jsonify(metrics)
    
    @app.route('/api/trends')
    def api_trends():
        """API endpoint for trend data"""
        logger.info("API trends endpoint accessed")
        category = request.args.get('category')
        try:
            from services.simple_mock_service import SimpleMockService
            mock_service = SimpleMockService()
            trends = mock_service.get_trends(limit=30)
            if category and category != 'all':
                # Filter trends by category
                trends = [t for t in trends if t.get('category') == category]
            return jsonify(trends)
        except ImportError:
            logger.warning("SimpleMockService not available")
            return jsonify([])
    
    @app.route('/api/storytelling', methods=['POST'])
    def api_storytelling():
        """API endpoint for AI storytelling generation"""
        logger.info("API storytelling endpoint accessed")
        data = request.json
        stories = get_mock_stories()
        if stories and len(stories) > 0:
            return jsonify(stories[0])
        else:
            return jsonify({"error": "No stories available"})
    
    @app.route('/api/search', methods=['GET', 'POST'])
    def api_search():
        """Unified search API endpoint"""
        logger.info("API search endpoint accessed")
        if request.method == 'POST':
            data = request.json
            query = data.get('query', '')
        else:
            query = request.args.get('query', '')
            
        mode = request.args.get('mode', 'hybrid')
        results = perform_enhanced_search(query, mode)
        return jsonify(results)
    
    @app.route('/api/copilot', methods=['POST'])
    def api_copilot():
        """API endpoint for Co-Pilot AI assistant"""
        logger.info("API Co-Pilot endpoint accessed")
        data = request.json
        query = data.get('query', '')
        context = data.get('context', {})
        
        # Use AI search as the backend for Co-Pilot
        results = perform_ai_search(query)
        return jsonify(results)
    
    @app.route('/api/summarize', methods=['POST'])
    def api_summarize():
        """API endpoint to summarize sustainability text using AI"""
        logger.info("API summarize endpoint accessed")
        
        if not request.json or 'text' not in request.json:
            return jsonify({"error": "No text provided for summarization"}), 400
            
        text = request.json.get('text', '')
        max_length = request.json.get('max_length', 200)
        
        try:
            # Simple summarization logic (this would use AI in production)
            if len(text) > max_length:
                summary = text[:max_length] + "..."
            else:
                summary = text
                
            return jsonify({
                "summary": summary,
                "original_length": len(text),
                "summary_length": len(summary)
            })
        except Exception as e:
            logger.error(f"Error in summarize endpoint: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/predictive-analytics', methods=['POST'])
    def api_predictive_analytics():
        """API endpoint for predictive analytics of sustainability metrics"""
        logger.info("API predictive analytics endpoint accessed")
        return jsonify({"results": "Predictive analytics data would be returned here"})
    
    @app.route('/api/sustainability-analysis', methods=['POST'])
    def api_sustainability_analysis():
        """API endpoint for sustainability analysis"""
        logger.info("API sustainability analysis endpoint accessed")
        return jsonify({"results": "Sustainability analysis data would be returned here"})
    
    @app.route('/api/monetization-strategy', methods=['POST'])
    def api_monetization_strategy():
        """API endpoint for monetization strategy recommendations"""
        logger.info("API monetization strategy endpoint accessed")
        return jsonify({"results": "Monetization strategy recommendations would be returned here"})
    
    @app.route('/api/apa-strategy', methods=['POST'])
    def api_apa_strategy():
        """API endpoint for Assess-Plan-Act (APA) sustainability strategy"""
        logger.info("API APA strategy endpoint accessed")
        return jsonify({"results": "APA strategy data would be returned here"})
    
    # -------------------------------------------------------------------------
    # Route redirects for deprecated pages
    # -------------------------------------------------------------------------
    
    @app.route('/trend-analysis')
    def trend_analysis_redirect():
        """Trend analysis redirect to home page"""
        return redirect(url_for('home'))
    
    @app.route('/search')
    def search_redirect():
        """Search redirect to Co-Pilot"""
        query = request.args.get('query', '')
        return redirect(url_for('co_pilot', query=query))
    
    @app.route('/document-upload')
    def document_upload_redirect():
        """Document upload redirect to PDF analyzer"""
        return redirect(url_for('pdf_analyzer'))
    
    @app.route('/sustainability')
    def sustainability_redirect():
        """Sustainability page redirect to unified dashboard"""
        return redirect(url_for('dashboard'))
    
    @app.route('/sustainability-stories')
    def sustainability_stories_redirect():
        """Stories redirect to story cards"""
        return redirect(url_for('story_cards'))
    
    # -------------------------------------------------------------------------
    # Debug Routes - Utility for developers
    # -------------------------------------------------------------------------
    
    @app.route('/debug')
    def debug_route():
        """Debug route to check registered routes and app status"""
        logger.info("Debug route accessed")
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        
        # Get navigation structure for debugging
        nav_structure = get_navigation_structure()
        nav_context = get_context_for_template()
        
        # Using the unified dark analytics dashboard template
        return render_template(
            "analytics_dashboard_dark.html",
            routes=routes,
            nav_structure=nav_structure,
            template_type="debug",
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="debug"
        )
    
    # -------------------------------------------------------------------------
    
    # Convert iterator to list before getting its length
    routes_list = list(app.url_map.iter_rules())
    logger.info(f"Successfully registered {len(routes_list)} routes")
    return app