"""
Analytics Routes

This module contains the analytics routes for the frontend application.
"""

from datetime import datetime
from typing import Dict, Any
from flask import Blueprint, render_template, jsonify, current_app, request
from ..utils import get_context_for_template
from ..utils.data_providers import (
    get_metrics,
    get_trends,
    get_stories,
    get_monetization_strategies
)
from .base import BaseRoute

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
            self.logger.info("Analytics route called")
            nav_context = get_context_for_template()
            return self.render_template(
                "analytics.html",
                page_title="Analytics Dashboard",
                template_type="analytics",
                **nav_context
            )
            
        @self.blueprint.route('/data')
        @self.handle_errors
        def get_analytics_data():
            """Get analytics data in JSON format"""
            self.logger.info("Analytics data route called")
            metrics = get_metrics()
            trends = get_trends()
            return jsonify({
                'metrics': self.format_metrics(metrics),
                'trends': trends
            })
            
        @self.blueprint.route('/dashboard')
        @self.handle_errors
        def dashboard():
            """Unified dashboard page combining sustainability metrics and key indicators"""
            self.logger.info("Dashboard route called")
            nav_context = get_context_for_template()
            metrics = get_metrics()
            formatted_metrics = self.format_metrics(metrics)
            self.logger.info("Using Finchat dark dashboard template")
            return self.render_template(
                "finchat_dark_dashboard.html", 
                page_title="Sustainability Intelligence Dashboard",
                template_type="dashboard",
                metrics=metrics,
                metrics_json=formatted_metrics,
                timestamp=datetime.now(),
                **nav_context
            )

        @self.blueprint.route('/monetization-strategies')
        @self.handle_errors
        def monetization_strategies_dashboard():
            """Enhanced strategy hub with monetization insights"""
            self.logger.info("Monetization strategies dashboard route called")
            nav_context = get_context_for_template()
            return self.render_template(
                "strategy_hub.html",
                page_title="Monetization Strategy Hub",
                template_type="strategy",
                **nav_context
            )

        @self.blueprint.route('/story-cards')
        @self.handle_errors
        def story_cards():
            """Present sustainability storytelling"""
            self.logger.info("Story cards route called")
            nav_context = get_context_for_template()
            stories = get_stories()
            return self.render_template(
                "story_cards.html",
                page_title="Sustainability Stories",
                template_type="stories",
                stories=stories,
                **nav_context
            )
            
        @self.blueprint.route('/analytics-dashboard')
        @self.handle_errors
        def analytics_dashboard():
            """Analytics dashboard with metrics and trends"""
            self.logger.info("Analytics dashboard route called")
            nav_context = get_context_for_template()
            metrics = get_metrics()
            return self.render_template(
                "analytics_dashboard.html",
                page_title="Analytics Dashboard",
                template_type="analytics",
                metrics=metrics,
                **nav_context
            )
            
        @self.blueprint.route('/metrics')
        @self.handle_errors
        def get_metrics_route():
            """Get sustainability metrics in JSON format"""
            self.logger.info("Metrics route called")
            metrics = get_metrics()
            return jsonify(self.format_metrics(metrics))
            
        @self.blueprint.route('/clear-cache', methods=['POST'])
        @self.handle_errors
        def clear_cache():
            """Clear the analytics route cache."""
            self.clear_cache()
            return self.json_response({
                'status': 'success',
                'message': 'Cache cleared successfully',
                'timestamp': datetime.now()
            })
            
    def format_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Format metrics for JSON serialization"""
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
            }
        }
        
    def format_stories(self, stories: list) -> list:
        """Format stories for JSON serialization"""
        return [{
            'title': story['title'],
            'content': story['content'],
            'metrics': story['metrics'],
            'timestamp': story['timestamp'].isoformat() if isinstance(story['timestamp'], datetime) else story['timestamp']
        } for story in stories]

# Create the analytics route instance
analytics_route = AnalyticsRoute()