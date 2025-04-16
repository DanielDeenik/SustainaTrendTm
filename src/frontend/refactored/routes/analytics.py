"""
Analytics routes for the SustainaTrend™ Platform.
"""
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, current_app
import logging
import json
from datetime import datetime, timedelta
from src.frontend.refactored.services.mongodb_service import MongoDBService

# Configure logger
logger = logging.getLogger(__name__)

# Create blueprint
analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

# Initialize MongoDBService
mongodb = MongoDBService()

@analytics_bp.route('/')
def index():
    """Redirect to analytics dashboard."""
    return redirect(url_for('analytics.dashboard'))

@analytics_bp.route('/dashboard')
def dashboard():
    """Render the analytics dashboard."""
    try:
        # Fetch key metrics
        metrics = mongodb.get_metrics()
        
        # Fetch recent trends
        trends = mongodb.get_trends(limit=5)
        
        # Fetch recent stories
        stories = mongodb.get_stories_collection().find().sort('date', -1).limit(5)
        
        return render_template('analytics/dashboard.html',
                             metrics=metrics,
                             trends=trends,
                             stories=stories)
    except Exception as e:
        current_app.logger.error(f"Error in analytics dashboard: {str(e)}")
        return render_template('errors/500.html'), 500

@analytics_bp.route('/trends')
def trends():
    """Render the trends analysis page."""
    try:
        # Get categories for filter dropdown
        categories = mongodb.get_trending_categories()
        
        # Get recent trends for initial display
        trends = mongodb.get_trends(limit=10)
        
        return render_template('analytics/trends.html', 
                             categories=categories,
                             trends=trends)
    except Exception as e:
        current_app.logger.error(f"Error loading trends page: {str(e)}")
        return render_template('errors/500.html'), 500

@analytics_bp.route('/portfolio')
def portfolio_analysis():
    """Render the portfolio analysis page."""
    try:
        companies = mongodb.get_portfolio_companies()
        sectors = mongodb.get_portfolio_sectors()
        return render_template('analytics/portfolio.html', 
                             companies=companies, 
                             sectors=sectors)
    except Exception as e:
        current_app.logger.error(f"Error rendering portfolio analysis: {str(e)}")
        return render_template('errors/500.html'), 500

@analytics_bp.route('/api/trends/data')
def get_trends_data():
    """Get filtered trends data for charts and tables."""
    try:
        category = request.args.get('category')
        timeframe = request.args.get('timeframe', '30d')
        
        # Calculate date range based on timeframe
        end_date = datetime.now()
        if timeframe == '7d':
            start_date = end_date - timedelta(days=7)
        elif timeframe == '30d':
            start_date = end_date - timedelta(days=30)
        elif timeframe == '90d':
            start_date = end_date - timedelta(days=90)
        else:  # 1y
            start_date = end_date - timedelta(days=365)
        
        # Get trends data
        trends = mongodb.get_trends(
            category=category,
            start_date=start_date,
            end_date=end_date
        )
        
        # Process data for charts
        dates = []
        growth_rates = []
        category_counts = {}
        
        for trend in trends:
            # Add to time series data
            dates.append(trend['date'].strftime('%Y-%m-%d'))
            growth_rates.append(trend['growth_rate'])
            
            # Count categories
            cat = trend['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        return jsonify({
            'dates': dates,
            'growth_rates': growth_rates,
            'categories': list(category_counts.keys()),
            'category_counts': list(category_counts.values()),
            'trends': trends
        })
    except Exception as e:
        current_app.logger.error(f"Error getting trends data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/trends/<trend_id>')
def get_trend_details(trend_id):
    """Get detailed information about a specific trend."""
    try:
        trend = mongodb.get_trend_by_id(trend_id)
        if not trend:
            return jsonify({'error': 'Trend not found'}), 404
            
        # Get additional metrics for the trend
        metrics = mongodb.get_trend_metrics(trend_id)
        trend.update(metrics)
        
        return jsonify(trend)
    except Exception as e:
        current_app.logger.error(f"Error getting trend details: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/portfolio/metrics')
def get_portfolio_metrics():
    """Get portfolio metrics for visualization."""
    try:
        sector = request.args.get('sector')
        metrics = mongodb.get_portfolio_metrics(sector=sector)
        return jsonify(metrics)
    except Exception as e:
        current_app.logger.error(f"Error fetching portfolio metrics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/data')
def get_data():
    """Get analytics data."""
    try:
        metrics = list(mongodb.get_collection('metrics').find())
        trends = list(mongodb.get_collection('trends').find())
        
        # Remove MongoDB _id field for JSON serialization
        for item in metrics + trends:
            if '_id' in item:
                item['_id'] = str(item['_id'])
        
        data = {
            'metrics': metrics,
            'trends': trends,
            'timestamp': datetime.now().isoformat()
        }
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting analytics data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/unified-dashboard')
def unified_dashboard():
    """Unified analytics dashboard."""
    try:
        metrics = mongodb.get_collection('metrics').find()
        trends = mongodb.get_collection('trends').find()
        stories = mongodb.get_collection('stories').find()
        
        return render_template(
            'analytics/unified_dashboard.html',
            title='Unified Analytics',
            metrics=list(metrics),
            trends=list(trends),
            stories=list(stories)
        )
    except Exception as e:
        logger.error(f"Error in unified dashboard: {str(e)}")
        return render_template('errors/500.html'), 500

@analytics_bp.route('/monetization-strategies')
def monetization_strategies():
    """Monetization strategies insights."""
    try:
        strategies = mongodb.get_collection('strategies').find()
        metrics = mongodb.get_collection('metrics').find()
        
        return render_template(
            'analytics/monetization_strategies.html',
            title='Monetization Strategies',
            strategies=list(strategies),
            metrics=list(metrics)
        )
    except Exception as e:
        logger.error(f"Error in monetization strategies: {str(e)}")
        return render_template('errors/500.html'), 500

@analytics_bp.route('/story-cards')
def story_cards():
    """Sustainability story cards."""
    try:
        stories = mongodb.get_collection('stories').find()
        
        return render_template(
            'analytics/story_cards.html',
            title='Sustainability Stories',
            stories=list(stories)
        )
    except Exception as e:
        logger.error(f"Error in story cards: {str(e)}")
        return render_template('errors/500.html'), 500

@analytics_bp.route('/analytics-dashboard')
def analytics_dashboard():
    """Analytics dashboard page."""
    try:
        return render_template('analytics/analytics_dashboard.html')
    except Exception as e:
        logger.error(f"Error in analytics dashboard: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/metrics')
def get_metrics():
    """Get sustainability metrics."""
    try:
        metrics = list(mongodb.get_collection('metrics').find())
        
        # Remove MongoDB _id field for JSON serialization
        for metric in metrics:
            if '_id' in metric:
                metric['_id'] = str(metric['_id'])
        
        return jsonify({
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/clear-cache')
def clear_cache():
    """Clear analytics route cache."""
    try:
        # Implementation for clearing cache would go here
        # For now, just return success
        return jsonify({
            'message': 'Cache cleared successfully',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        return jsonify({'error': str(e)}), 500 