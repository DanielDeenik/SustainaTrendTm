"""
Unified Routes Module for SustainaTrend Intelligence Platform

This module adds routes for the unified UI templates with consistent design across all pages.
"""
import json
import logging
import sys
import os
import random
from datetime import datetime, timedelta

# Add the current directory to the path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Flask-related modules
try:
    from flask import Flask, render_template, request, jsonify, redirect, url_for
    import jinja2.exceptions
except ImportError as e:
    logging.error(f"Error importing Flask modules: {e}")
    raise

logger = logging.getLogger(__name__)

def generate_mock_trends(limit=15):
    """Generate mock sustainability trend data"""
    # Define categories and sample trends
    categories = ["Energy", "Carbon", "Water", "Waste", "Social", "Governance"]
    trend_templates = [
        "Increased {category} efficiency in corporate operations",
        "New {category} regulations impact reporting requirements",
        "{category} innovation drives competitive advantage",
        "Consumer demand for transparent {category} metrics rises",
        "AI-powered {category} optimization gains momentum",
        "Circular economy approaches to {category} management",
        "Investment in {category} technology accelerates",
        "Supply chain {category} tracking becomes standard",
        "ESG frameworks emphasize {category} disclosure",
        "Small businesses adopt {category} best practices"
    ]
    
    trends = []
    for i in range(limit):
        # Select random category and template
        category = random.choice(categories)
        template = random.choice(trend_templates)
        
        # Calculate random stats
        virality_score = random.randint(35, 98)
        growth_rate = random.randint(-15, 45)
        
        # Random date within last 30 days
        days_ago = random.randint(0, 30)
        trend_date = datetime.now() - timedelta(days=days_ago)
        
        # Create trend
        trends.append({
            "id": f"trend-{i+1}",
            "name": template.format(category=category),
            "category": category,
            "description": f"This sustainability trend focuses on {category.lower()} management and innovation. Companies adopting these practices are seeing improved performance and stakeholder engagement.",
            "virality_score": virality_score,
            "growth_rate": growth_rate,
            "date": trend_date,
            "source": random.choice(["Industry Report", "Academic Research", "News Media", "Corporate Disclosure", "Social Media"])
        })
    
    # Sort by virality score
    return sorted(trends, key=lambda x: x["virality_score"], reverse=True)

def register_unified_routes(app):
    """
    Register unified routes for the SustainaTrend Intelligence Platform
    
    Args:
        app: Flask application
    """
    logger.info("Registering unified routes")
    
    @app.route('/trend-analysis-unified')
    def trend_analysis_unified():
        """Unified version of the trend analysis page with consistent design"""
        # Get category filter if provided
        category = request.args.get('category', None)
        # Get sort parameter if provided (default to virality)
        sort_by = request.args.get('sort', 'virality')
        
        try:
            # Try to use MongoDB service
            from mongo_trends import get_trends
            
            # Get trend data from MongoDB with filtering
            if category and category != 'all':
                trends = get_trends(category=category, limit=30)
            else:
                trends = get_trends(limit=30)
        except ImportError:
            logger.warning("MongoDB service not available, using fallback data")
            
            # Fall back to mock data if MongoDB isn't available
            try:
                # Try to access mock service from direct_app
                mock_service = app.config.get('mock_service')
                if mock_service:
                    trends = mock_service.get_trends(limit=30)
                else:
                    # If mock service is not available, generate synthetic data
                    trends = generate_mock_trends(limit=30)
            except Exception as e:
                logger.error(f"Error accessing mock service: {str(e)}")
                # Generate synthetic data if all else fails
                trends = generate_mock_trends(limit=30)
        
        # Sort trends based on sort parameter
        if sort_by == 'virality':
            trends = sorted(trends, key=lambda x: x.get('virality_score', 0), reverse=True)
        elif sort_by == 'date':
            trends = sorted(trends, key=lambda x: x.get('date', datetime.now()), reverse=True)
        elif sort_by == 'category':
            trends = sorted(trends, key=lambda x: x.get('category', ''))
        
        # Calculate chart data from the actual trends
        categories = ["Energy", "Carbon", "Water", "Waste", "Social", "Governance"]
        
        # Initialize data for each category with zeros
        category_scores = {cat: 0 for cat in categories}
        category_counts = {cat: 0 for cat in categories}
        
        # Calculate average virality score for each category
        for trend in trends:
            cat = trend.get('category', '')
            if cat and cat in categories and 'virality_score' in trend:
                category_scores[cat] += trend['virality_score']
                category_counts[cat] += 1
        
        # Calculate averages, avoiding division by zero
        chart_data_values = []
        for cat in categories:
            if category_counts[cat] > 0:
                chart_data_values.append(round(category_scores[cat] / category_counts[cat]))
            else:
                chart_data_values.append(0)
        
        # Prepare chart data with dynamic values
        chart_data = {
            "labels": categories,
            "datasets": [{
                "label": "Average Virality Score",
                "data": chart_data_values,
                "backgroundColor": "rgba(76, 175, 80, 0.6)"
            }]
        }
        
        # Generate AI insights based on the actual trend data
        insights = []
        
        # Find the top category
        top_category_index = chart_data_values.index(max(chart_data_values))
        top_category = categories[top_category_index]
        
        # Find the category with largest growth
        growth_by_category = {}
        for trend in trends:
            cat = trend.get('category', '')
            growth = trend.get('growth_rate', 0)
            if cat in categories and growth:
                if cat not in growth_by_category:
                    growth_by_category[cat] = []
                growth_by_category[cat].append(growth)
        
        fastest_growing = "Sustainability" # Default
        highest_growth_rate = 0
        for cat, growths in growth_by_category.items():
            if growths and len(growths) > 0:
                avg_growth = sum(growths) / len(growths)
                if avg_growth > highest_growth_rate:
                    highest_growth_rate = avg_growth
                    fastest_growing = cat
        
        # Create insights
        insights = {
            "top_category": top_category,
            "top_score": max(chart_data_values),
            "fastest_growing": fastest_growing,
            "growth_rate": round(highest_growth_rate)
        }
    
        # Now render the unified template with the data
        logger.info("Rendering unified trend analysis dashboard")
        try:
            return render_template(
                "trend_analysis_unified.html",
                trends=trends,
                trend_chart_data=json.dumps(chart_data),
                category=category or 'all',
                sort=sort_by,
                insights=insights
            )
        except jinja2.exceptions.TemplateNotFound:
            logger.warning("Unified template not found, falling back to original template")
            return redirect(url_for('trend_analysis'))
    
    @app.route('/unified-ai-prompt')
    def unified_ai_prompt():
        """Unified AI prompt interface"""
        return render_template("unified_ai_prompt.html")
    
    logger.info("Unified routes registered successfully")
    
    return app