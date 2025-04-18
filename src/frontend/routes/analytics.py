"""
Analytics Routes

This module contains the analytics routes for the frontend application.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List
from flask import Blueprint, render_template, jsonify, current_app, request
from ..utils import get_context_for_template
from ..utils.data_providers import (
    get_metrics,
    get_trends,
    get_stories,
    get_monetization_strategies
)
from .base import BaseRoute

logger = logging.getLogger(__name__)

class AnalyticsRoute(BaseRoute):
    """Analytics route handler."""
    
    def __init__(self):
        """Initialize the analytics route."""
        super().__init__('analytics', __name__)
        self.register_routes()
        
    def register_routes(self) -> None:
        """Register all routes for the analytics blueprint."""
        
        @self.blueprint.route('/')
        @self.handle_errors
        def analytics():
            """Main analytics dashboard"""
            try:
                logger.info("Analytics route called")
                nav_context = get_context_for_template()
                metrics = get_metrics()
                formatted_metrics = self.format_metrics(metrics)
                return self.render_template(
                    "analytics.html",
                    page_title="Analytics Dashboard",
                    template_type="analytics",
                    metrics=metrics,
                    metrics_json=formatted_metrics,
                    **nav_context
                )
            except Exception as e:
                logger.error(f"Error in analytics route: {e}")
                return self.render_error("Failed to load analytics dashboard")
            
        @self.blueprint.route('/data')
        @self.handle_errors
        def get_analytics_data():
            """Get analytics data in JSON format"""
            try:
                logger.info("Analytics data route called")
                metrics = get_metrics()
                trends = get_trends()
                return jsonify({
                    'metrics': self.format_metrics(metrics),
                    'trends': trends,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error in analytics data route: {e}")
                return self.json_error("Failed to load analytics data")
            
        @self.blueprint.route('/dashboard')
        @self.handle_errors
def dashboard():
    """Unified dashboard page combining sustainability metrics and key indicators"""
            try:
    logger.info("Dashboard route called")
    nav_context = get_context_for_template()
                metrics = get_metrics()
                formatted_metrics = self.format_metrics(metrics)
                trends = get_trends()
                stories = get_stories()
                
                return self.render_template(
        "finchat_dark_dashboard.html", 
        page_title="Sustainability Intelligence Dashboard",
        template_type="dashboard",
        metrics=metrics,
        metrics_json=formatted_metrics,
                    trends=trends,
                    stories=stories,
                    timestamp=datetime.now(),
                    **nav_context
    )
            except Exception as e:
                logger.error(f"Error in dashboard route: {e}")
                return self.render_template("errors/500.html", error=str(e)), 500

        @self.blueprint.route('/monetization-strategies')
        @self.handle_errors
def monetization_strategies_dashboard():
            """Enhanced strategy hub with monetization insights"""
            try:
                logger.info("Monetization strategies dashboard route called")
                nav_context = get_context_for_template()
                strategies = get_monetization_strategies()
                
                return self.render_template(
                    "strategy_hub.html",
                    page_title="Monetization Strategy Hub",
                    template_type="strategy",
                    strategies=strategies,
                    **nav_context
                )
            except Exception as e:
                logger.error(f"Error in monetization strategies route: {e}")
                return self.render_error("Failed to load monetization strategies")

        @self.blueprint.route('/story-cards')
        @self.handle_errors
def story_cards():
            """Present sustainability storytelling"""
            try:
    logger.info("Story cards route called")
    nav_context = get_context_for_template()
                stories = get_stories()
                
                return self.render_template(
                    "story_cards.html",
                    page_title="Sustainability Stories",
        template_type="stories",
        stories=stories,
                    **nav_context
                )
            except Exception as e:
                logger.error(f"Error in story cards route: {e}")
                return self.render_error("Failed to load sustainability stories")
            
        @self.blueprint.route('/analytics-dashboard')
        @self.handle_errors
        def analytics_dashboard():
            """Analytics dashboard with metrics and trends"""
            try:
                logger.info("Analytics dashboard route called")
                nav_context = get_context_for_template()
                metrics = get_metrics()
                trends = get_trends()
                
                return self.render_template(
                    "analytics_dashboard.html",
                    page_title="Analytics Dashboard",
                    template_type="analytics",
                    metrics=metrics,
                    trends=trends,
                    **nav_context
                )
            except Exception as e:
                logger.error(f"Error in analytics dashboard route: {e}")
                return self.render_error("Failed to load analytics dashboard")
            
        @self.blueprint.route('/metrics')
        @self.handle_errors
        def get_metrics_route():
            """Get sustainability metrics in JSON format"""
            try:
                logger.info("Metrics route called")
                metrics = get_metrics()
                return jsonify(self.format_metrics(metrics))
            except Exception as e:
                logger.error(f"Error in metrics route: {e}")
                return self.json_error("Failed to load metrics")
            
        @self.blueprint.route('/clear-cache', methods=['POST'])
        @self.handle_errors
        def clear_cache():
            """Clear the analytics route cache."""
            try:
                self.clear_cache()
                return self.json_response({
                    'status': 'success',
                    'message': 'Cache cleared successfully',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error clearing cache: {e}")
                return self.json_error("Failed to clear cache")
            
    def format_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Format metrics for JSON serialization"""
        try:
            return {
                'environmental': {
                    'carbon_emissions': float(metrics['environmental']['carbon_emissions']),
                    'renewable_energy': float(metrics['environmental']['renewable_energy']),
                    'waste_reduction': float(metrics['environmental']['waste_reduction'])
                },
                'social': {
                    'employee_satisfaction': float(metrics['social']['employee_satisfaction']),
                    'community_engagement': float(metrics['social']['community_engagement']),
                    'diversity_score': float(metrics['social']['diversity_score'])
                },
                'governance': {
                    'board_diversity': float(metrics['governance']['board_diversity']),
                    'transparency_score': float(metrics['governance']['transparency_score']),
                    'ethics_compliance': float(metrics['governance']['ethics_compliance'])
                },
                'timestamp': metrics.get('timestamp', datetime.now()).isoformat()
            }
        except Exception as e:
            logger.error(f"Error formatting metrics: {e}")
            raise
        
    def format_stories(self, stories: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format stories for JSON serialization"""
        try:
            formatted_stories = []
            for story_type, story in stories.items():
                formatted_stories.append({
                    'type': story_type,
                    'title': story.get('title', ''),
                    'content': story.get('content', ''),
                    'metrics': story.get('metrics', {}),
                    'timestamp': story.get('timestamp', datetime.now()).isoformat()
                })
            return formatted_stories
        except Exception as e:
            logger.error(f"Error formatting stories: {e}")
            raise

# Create the analytics route instance
analytics_route = AnalyticsRoute()