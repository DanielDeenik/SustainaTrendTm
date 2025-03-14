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

# Import storytelling functionality
try:
    from sustainability_storytelling import get_enhanced_stories
    logging.info("Sustainability storytelling module loaded successfully")
except ImportError:
    logging.warning("Could not import get_enhanced_stories from sustainability_storytelling. Using fallback function.")
    def get_enhanced_stories(audience='all', category='all'):
        """Fallback function for getting enhanced stories"""
        return get_mock_stories()

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
        """AI Storytelling Engine - Data-driven sustainability narratives with Gartner-inspired methodology"""
        logger.info("AI Storytelling Engine accessed")
        nav_context = get_context_for_template()
        
        # Get audience filter if provided
        audience = request.args.get('audience', 'all')
        category = request.args.get('category', 'all')
        
        # Get enhanced stories with the three core elements:
        # Context, Narrative, and Visual data
        stories = get_enhanced_stories(audience=audience, category=category)
        
        # Get metrics and trends for AI storytelling
        metrics = get_sustainability_metrics()
        
        # Ensure consistent metrics format
        if isinstance(metrics, list):
            metrics_data = {"metrics": metrics}
        else:
            metrics_data = metrics
            
        # Get trending topics for context
        try:
            from services.simple_mock_service import SimpleMockService
            mock_service = SimpleMockService()
            trends = mock_service.get_trends(limit=10)
        except ImportError:
            logger.warning("SimpleMockService not available for trends")
            trends = []
            
        # Get storytelling templates for different stakeholders
        stakeholder_templates = {
            "board": {
                "title": "Board-Level Narratives",
                "description": "High-level risk, opportunity, strategic next steps",
                "prompt_example": "Generate a board-level CSRD story from our current data, focusing on top 3 risks and recommendations."
            },
            "sustainability_team": {
                "title": "Sustainability Team Insights",
                "description": "Root causes, detailed action plans, implementation metrics",
                "prompt_example": "Create a sustainability team analysis of our current emissions trend, focusing on root cause and tactical improvements."
            },
            "investors": {
                "title": "Investor-Focused Storytelling",
                "description": "Risk analysis, peer comparison, compliance status, ROI metrics",
                "prompt_example": "Present our water conservation initiatives as an investor narrative highlighting competitive advantage and risk mitigation."
            }
        }
        
        # Using the specialized storytelling engine template
        return render_template(
            "storytelling_engine_dark.html", 
            stories=stories,
            metrics=metrics_data,
            trends=trends,
            audience=audience,
            category=category,
            stakeholder_templates=stakeholder_templates,
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
    
    @app.route('/sustainability-strategies')
    def sustainability_strategies():
        """Sustainability Strategies - Strategic frameworks and implementation plans"""
        logger.info("Sustainability Strategies accessed")
        nav_context = get_context_for_template()
        
        # Get metrics for context
        metrics = get_sustainability_metrics()
        
        # Ensure consistent metrics format
        if isinstance(metrics, list):
            metrics_data = {"metrics": metrics}
        else:
            metrics_data = metrics
        
        # Using the unified dark analytics dashboard template
        return render_template(
            "analytics_dashboard_dark.html",
            template_type="strategies",
            metrics=metrics_data,
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="strategies"
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
        """API endpoint for AI storytelling generation with Gartner-inspired methodology"""
        logger.info("API storytelling endpoint accessed")
        data = request.json
        
        # Get parameters for storytelling
        metric = data.get('metric', 'Carbon Emissions')
        time_period = data.get('time_period', 'Last Quarter')
        narrative_focus = data.get('narrative_focus', 'Performance Analysis')
        audience = data.get('audience', 'Executive Leadership')
        context = data.get('context', '')
        
        logger.info(f"Generating story for metric: {metric}, focus: {narrative_focus}, audience: {audience}")
        
        try:
            # Get underlying data
            metrics = get_sustainability_metrics()
            
            # Get stories and select the most relevant one
            stories = get_mock_stories()
            
            if stories and len(stories) > 0:
                # Select relevant story based on parameters
                for story in stories:
                    if story.get('category', '').lower() in metric.lower() or metric.lower() in story.get('title', '').lower():
                        selected_story = story
                        break
                else:
                    # Default to first story if no match
                    selected_story = stories[0]
                
                # Enhance the story with Gartner-inspired narrative elements
                selected_story['narrative_focus'] = narrative_focus
                selected_story['audience'] = audience
                selected_story['time_period'] = time_period
                selected_story['context'] = context
                selected_story['augmented_analytics'] = True
                selected_story['gartner_inspired'] = True
                
                # Generate recommendations based on narrative focus
                if narrative_focus == 'Performance Analysis':
                    selected_story['recommendations'] = [
                        "Focus on the key performance indicators that show the most significant change",
                        "Correlate sustainability metrics with financial performance for executive context",
                        "Highlight year-over-year trends to demonstrate continuous improvement"
                    ]
                elif narrative_focus == 'Risk Assessment':
                    selected_story['recommendations'] = [
                        "Quantify potential financial impacts of sustainability risks",
                        "Map sustainability metrics to specific risk categories (regulatory, market, physical)",
                        "Present risk mitigation strategies alongside risk assessment"
                    ]
                elif narrative_focus == 'CSRD/ESG Compliance':
                    selected_story['recommendations'] = [
                        "Structure narrative according to CSRD disclosure requirements",
                        "Emphasize double materiality in the analysis",
                        "Include forward-looking sustainability targets and roadmaps"
                    ]
                else:
                    selected_story['recommendations'] = [
                        "Focus on clear, data-driven insights for maximum stakeholder impact",
                        "Use visualization to support key narrative points",
                        "Include specific, actionable recommendations"
                    ]
                
                return jsonify(selected_story)
            else:
                return jsonify({"error": "No stories available"})
                
        except Exception as e:
            logger.error(f"Error generating AI story: {str(e)}")
            return jsonify({"error": f"Failed to generate story: {str(e)}"}), 500
    
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
    def trend_analysis():
        """AI-powered Trend Analysis with Virality Metrics"""
        logger.info("Trend Analysis accessed")
        nav_context = get_context_for_template()
        metrics = get_sustainability_metrics()
        
        # Ensure consistent metrics format
        if isinstance(metrics, list):
            metrics_data = {"metrics": metrics}
        else:
            metrics_data = metrics
        
        # Get trending topics
        try:
            from services.simple_mock_service import SimpleMockService
            mock_service = SimpleMockService()
            trends = mock_service.get_trends(limit=15)
        except ImportError:
            logger.warning("SimpleMockService not available")
            trends = []
            
        # Using the unified dark analytics dashboard template
        return render_template(
            "analytics_dashboard_dark.html",
            metrics=metrics_data,
            trends=trends,
            template_type="trends",
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="trends"
        )
    
    @app.route('/virality-metrics')
    def virality_metrics():
        """Virality Metrics Dashboard - Analyze sustainability trend virality and social impact"""
        logger.info("Virality Metrics Dashboard accessed")
        nav_context = get_context_for_template()
        
        # Get trending topics with virality metrics
        try:
            from services.simple_mock_service import SimpleMockService
            mock_service = SimpleMockService()
            trends = mock_service.get_trends(limit=30)
            
            # Sort by virality score (highest first)
            trends = sorted(trends, key=lambda x: x.get('virality_score', 0), reverse=True)
        except ImportError:
            logger.warning("SimpleMockService not available")
            trends = []
            
        # Using the unified dark analytics dashboard template
        return render_template(
            "analytics_dashboard_dark.html",
            trends=trends,
            template_type="virality",
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="virality"
        )
    
    @app.route('/search')
    def search_redirect():
        """Search redirect to Co-Pilot"""
        query = request.args.get('query', '')
        return redirect(url_for('co_pilot', query=query))
    
    @app.route('/document-upload')
    def document_upload_redirect():
        """Document upload with Ethical AI Assessment"""
        logger.info("Document upload with Ethical AI Assessment accessed")
        nav_context = get_context_for_template()
        return render_template(
            "ethical_ai_assessment_dark.html",
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="documents"
        )
    
    @app.route('/sustainability')
    def sustainability_redirect():
        """Sustainability page redirect to unified dashboard"""
        return redirect(url_for('dashboard'))
    
    @app.route('/sustainability-stories')
    def sustainability_stories_redirect():
        """Stories redirect to story cards"""
        return redirect(url_for('story_cards'))
    
    @app.route('/real-estate')
    def real_estate_redirect():
        """Real Estate Sustainability redirect to real estate trend analysis"""
        logger.info("Real Estate route accessed")
        # Redirect to the realestate_trend_analysis from realestate_sustainability.py
        return redirect('/realestate-trends')
    
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