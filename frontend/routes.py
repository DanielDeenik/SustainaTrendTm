"""
Routes Module for SustainaTrend Intelligence Platform

This module provides a clean, minimal structure for all routes in the application,
focusing on AI-driven storytelling with minimal UI and clear data visualization.
"""
import logging
import os
import sys
import json
from datetime import datetime, timedelta

# Add the current directory to the path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Flask-related modules
from flask import render_template, jsonify, request, redirect, url_for, abort, session

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
    Register all routes for the SustainaTrend Intelligence Platform
    
    Args:
        app: Flask application
    """
    logger.info("Registering main application routes")
    
    # Import navigation configuration once
    from navigation_config import get_context_for_template
    
    # -------------------------------------------------------------------------
    # Core Pages - Aligned with the 6 core components in our minimal UI design
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
            
        return render_template(
            "index.html",
            metrics=metrics_data,
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="home"
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
        
        return render_template(
            "dashboard.html",
            metrics=metrics_data,
            categories=list(categories),
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="risk"
        )
    
    @app.route('/pdf-analyzer')
    def pdf_analyzer():
        """PDF Analyzer - Intelligent document processing for sustainability reports"""
        logger.info("PDF Analyzer accessed")
        nav_context = get_context_for_template()
        return render_template(
            "document_upload.html",
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="documents"
        )
    
    @app.route('/story-cards')
    def story_cards():
        """Story Cards - AI-generated sustainability narratives and insights"""
        logger.info("Story Cards Generator accessed")
        nav_context = get_context_for_template()
        stories = get_mock_stories()
        return render_template(
            "sustainability_stories.html", 
            stories=stories,
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="stories"
        )
    
    @app.route('/data-terminal')
    def data_terminal():
        """Data Terminal - Minimal API interface for programmatic data access"""
        logger.info("Data Terminal accessed")
        nav_context = get_context_for_template()
        return render_template(
            "data_terminal.html",
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="terminal"
        )
    
    @app.route('/co-pilot')
    def co_pilot():
        """Sustainability Co-Pilot - Contextual AI assistant for sustainability intelligence"""
        logger.info("Sustainability Co-Pilot accessed")
        nav_context = get_context_for_template()
        query = request.args.get('query', '')
        return render_template(
            "sustainability_copilot.html", 
            query=query,
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
    
    # -------------------------------------------------------------------------
    # Legacy route mappings - Redirects to the new core components
    # -------------------------------------------------------------------------
    
    @app.route('/dashboard')
    def dashboard_redirect():
        """Legacy dashboard redirect"""
        return redirect(url_for('risk_tracker'))
    
    @app.route('/trend-analysis')
    def trend_analysis_redirect():
        """Legacy trend analysis redirect"""
        return redirect(url_for('home'))
    
    @app.route('/search')
    def search_redirect():
        """Legacy search redirect"""
        query = request.args.get('query', '')
        return redirect(url_for('co_pilot', query=query))
    
    @app.route('/document-upload')
    def document_upload_redirect():
        """Legacy document upload redirect"""
        return redirect(url_for('pdf_analyzer'))
    
    @app.route('/sustainability-stories')
    def sustainability_stories_redirect():
        """Legacy stories redirect"""
        return redirect(url_for('story_cards'))
    
    # -------------------------------------------------------------------------
    # Debug Routes
    # -------------------------------------------------------------------------
    
    @app.route('/debug')
    def debug_route():
        """Debug route to check registered routes and app status"""
        logger.info("Debug route accessed")
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        return jsonify({
            "routes": routes,
            "app_status": "running"
        })
    
    # -------------------------------------------------------------------------
    
    # Convert iterator to list before getting its length
    routes_list = list(app.url_map.iter_rules())
    logger.info(f"Successfully registered {len(routes_list)} routes")
    return app