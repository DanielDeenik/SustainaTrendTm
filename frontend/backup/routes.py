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
    
    @app.route('/analytics-dashboard')
    def analytics_dashboard():
        """Analytics Dashboard - Advanced visualization of sustainability metrics"""
        logger.info("Analytics Dashboard accessed")
        nav_context = get_context_for_template()
        return render_template(
            "analytics_dashboard_dark.html",
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="analytics"
        )
        
    @app.route('/monetization-opportunities')
    def monetization_opportunities():
        """Monetization Opportunities - Strategic insights for sustainable business models"""
        logger.info("Monetization Opportunities accessed")
        nav_context = get_context_for_template()
        return render_template(
            "monetization.html",
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="monetization"
        )
        
    @app.route('/sustainability')
    def sustainability():
        """Sustainability - Corporate sustainability intelligence dashboard"""
        logger.info("Sustainability page accessed")
        nav_context = get_context_for_template()
        
        # Try the collapsible template first, then fall back to the standard template
        use_collapsible = request.args.get('collapsible', 'true').lower() == 'true'
        
        if use_collapsible:
            try:
                logger.info("Using collapsible sustainability template")
                return render_template(
                    "sustainability_collapsible.html",
                    nav_sections=nav_context["nav_sections"],
                    user_menu=nav_context["user_menu"],
                    active_nav="sustainability"
                )
            except Exception as e:
                logger.warning(f"Error using collapsible template: {str(e)}, falling back to standard")
                use_collapsible = False
        
        # Fall back to standard template
        logger.info("Using standard sustainability template")
        return render_template(
            "sustainability.html",
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="sustainability"
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
        
        try:
            # Sample predictive analytics data
            data = {
                "predictions": [
                    {
                        "metric": "Carbon Emissions",
                        "current_value": 235.6,
                        "predicted_value": 198.2,
                        "prediction_date": (datetime.now() + timedelta(days=90)).isoformat(),
                        "confidence": 0.87,
                        "trend": "decreasing"
                    },
                    {
                        "metric": "Water Usage",
                        "current_value": 1250.3,
                        "predicted_value": 1180.5,
                        "prediction_date": (datetime.now() + timedelta(days=90)).isoformat(),
                        "confidence": 0.82,
                        "trend": "decreasing"
                    },
                    {
                        "metric": "Renewable Energy Percentage",
                        "current_value": 48.2,
                        "predicted_value": 62.7,
                        "prediction_date": (datetime.now() + timedelta(days=90)).isoformat(), 
                        "confidence": 0.91,
                        "trend": "increasing"
                    }
                ],
                "analysis": "Based on current trends and initiatives, we anticipate a significant reduction in carbon emissions and water usage over the next quarter. Renewable energy adoption is projected to increase by approximately 14%, driven primarily by the scheduled completion of solar installations."
            }
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error in predictive analytics endpoint: {str(e)}")
            return jsonify({"error": str(e)}), 500
            
    @app.route('/api/sustainability-analysis', methods=['POST'])
    def api_sustainability_analysis():
        """API endpoint for sustainability analysis of business data"""
        logger.info("API sustainability analysis endpoint accessed")
        
        try:
            if not request.json:
                return jsonify({"error": "No data provided for analysis"}), 400
                
            # Sample sustainability analysis response
            data = {
                "analysis": {
                    "overall_score": 72.5,
                    "strengths": [
                        "Strong renewable energy adoption (54% of total energy)",
                        "Comprehensive waste reduction program",
                        "Transparent ESG reporting mechanisms"
                    ],
                    "areas_for_improvement": [
                        "Supply chain emissions still above industry average",
                        "Water usage intensity higher than peer companies",
                        "Limited social impact metrics tracking"
                    ],
                    "recommendations": [
                        "Implement supplier emissions tracking program",
                        "Establish water reduction targets of 15% over 3 years",
                        "Develop comprehensive social impact measurement framework"
                    ]
                },
                "industry_comparison": {
                    "percentile": 68,
                    "leaders": ["CompanyA", "CompanyB", "CompanyC"],
                    "industry_avg_score": 59.2
                }
            }
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error in sustainability analysis endpoint: {str(e)}")
            return jsonify({"error": str(e)}), 500
            
    @app.route('/api/monetization-strategy', methods=['POST'])
    def api_monetization_strategy():
        """API endpoint for monetization strategy based on sustainability initiatives"""
        logger.info("API monetization strategy endpoint accessed")
        
        try:
            if not request.json:
                return jsonify({"error": "No data provided for monetization strategy"}), 400
                
            # Sample monetization strategy response
            data = {
                "monetization_strategies": [
                    {
                        "strategy": "Premium Sustainable Product Line",
                        "potential_revenue": "High",
                        "implementation_complexity": "Medium",
                        "timeframe": "6-12 months",
                        "description": "Develop premium product line with enhanced sustainability features commanding 15-20% price premium."
                    },
                    {
                        "strategy": "Carbon Credit Generation",
                        "potential_revenue": "Medium",
                        "implementation_complexity": "High",
                        "timeframe": "12-18 months",
                        "description": "Generate and sell carbon credits from documented emissions reductions."
                    },
                    {
                        "strategy": "Sustainability Consulting Services",
                        "potential_revenue": "Medium",
                        "implementation_complexity": "Low",
                        "timeframe": "3-6 months",
                        "description": "Leverage internal expertise to provide sustainability consulting to smaller companies."
                    }
                ],
                "recommended_approach": "Begin with Sustainability Consulting Services for quick revenue generation while developing Premium Product Line for long-term growth."
            }
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error in monetization strategy endpoint: {str(e)}")
            return jsonify({"error": str(e)}), 500
            
    @app.route('/api/apa-strategy', methods=['POST'])
    def api_apa_strategy():
        """API endpoint for Assess-Plan-Act (APA) sustainability strategy"""
        logger.info("API APA strategy endpoint accessed")
        
        try:
            if not request.json:
                return jsonify({"error": "No data provided for APA strategy"}), 400
                
            # Sample APA strategy response
            data = {
                "assess": {
                    "current_status": "Your organization has made initial progress in sustainability with ad-hoc initiatives but lacks a comprehensive strategy.",
                    "strengths": [
                        "Executive team commitment to sustainability",
                        "Initial data collection systems in place",
                        "Early product innovations with eco-friendly materials"
                    ],
                    "gaps": [
                        "No formal sustainability governance",
                        "Limited measurement of Scope 3 emissions",
                        "Fragmented sustainability initiatives"
                    ]
                },
                "plan": {
                    "strategic_priorities": [
                        "Establish formal sustainability governance structure",
                        "Implement comprehensive carbon accounting",
                        "Integrate sustainability into product development process"
                    ],
                    "timeline": "12-18 months implementation roadmap",
                    "resource_requirements": "Dedicated sustainability team (2-3 FTEs), data management system, external verification"
                },
                "act": {
                    "immediate_actions": [
                        "Appoint Chief Sustainability Officer",
                        "Begin Scope 1 & 2 emissions baseline",
                        "Launch pilot circular packaging initiative"
                    ],
                    "medium_term_actions": [
                        "Implement supplier sustainability program",
                        "Develop science-based targets",
                        "Launch pilot circular packaging initiative"
                    ],
                    "long_term_actions": [
                        "Achieve carbon neutrality for operations",
                        "Launch pilot circular packaging initiative"
                    ]
                }
            }
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error in APA strategy endpoint: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    # -------------------------------------------------------------------------
    # Route redirects for consolidated pages
    # -------------------------------------------------------------------------
    
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
        
        return render_template(
            "dashboard_unified.html",
            metrics=metrics_data,
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="dashboard"
        )
    
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