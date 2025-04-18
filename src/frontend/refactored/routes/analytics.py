"""
Analytics routes for the SustainaTrend™ Platform.
"""
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, current_app
import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict
from src.frontend.refactored.services.mongodb_service import mongodb_service
from src.frontend.refactored.services.config_service import config_service

# Configure logger
logger = logging.getLogger(__name__)

# Create blueprint
analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/')
def index():
    """Redirect to analytics dashboard."""
    return redirect(url_for('analytics.dashboard'))

@analytics_bp.route('/dashboard')
def dashboard():
    """Render the analytics dashboard."""
    try:
        # Use the singleton MongoDB service instance
        mongodb = mongodb_service
        
        # Fetch key metrics
        metrics = {
            'trends_count': len(mongodb.find_many('trends', query={})),
            'companies_count': len(mongodb.find_many('portfolio_companies', query={})),
            'strategies_count': len(mongodb.find_many('strategies', query={}))
        }
        
        # Fetch recent trends
        try:
            trends = mongodb.get_trends(limit=5)
        except Exception as e:
            logger.warning(f"Error fetching trends: {str(e)}")
            trends = []
        
        # Fetch recent stories
        try:
            stories = mongodb.find_many('stories', query={}, sort=[('date', -1)], limit=5)
        except Exception as e:
            logger.warning(f"Error fetching stories: {str(e)}")
            stories = []
        
        return render_template('analytics/dashboard.html',
                             metrics=metrics,
                             trends=trends,
                             stories=stories)
    except Exception as e:
        logger.error(f"Error in analytics dashboard: {str(e)}")
        return render_template('errors/500.html'), 500

@analytics_bp.route('/trends')
def trends():
    """Render the trends analysis page."""
    try:
        # Use the singleton MongoDB service instance
        mongodb = mongodb_service
        
        # Get categories for filter dropdown
        categories = mongodb.get_trending_categories()
        
        # Get date range for filter
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Get trends for the date range
        trends_data = mongodb.get_trends(
            start_date=start_date,
            end_date=end_date,
            limit=20
        )
        
        return render_template('analytics/trends.html',
                             categories=categories,
                             trends=trends_data,
                             start_date=start_date.strftime('%Y-%m-%d'),
                             end_date=end_date.strftime('%Y-%m-%d'))
    except Exception as e:
        logger.error(f"Error in trends analysis: {str(e)}")
        return render_template('errors/500.html'), 500

@analytics_bp.route('/portfolio')
def portfolio_analysis():
    """Render the portfolio analysis page."""
    try:
        # Use the singleton MongoDB service instance
        mongodb = mongodb_service
        
        # Fetch portfolio companies
        companies = mongodb.find_many('portfolio_companies', query={}, sort=[('name', 1)])
        
        # Fetch portfolio metrics
        metrics = {
            'total_companies': len(companies),
            'total_investment': sum(company.get('investment_amount', 0) for company in companies),
            'average_roi': sum(company.get('roi', 0) for company in companies) / len(companies) if companies else 0
        }
        
        return render_template('analytics/portfolio.html',
                             companies=companies,
                             metrics=metrics)
    except Exception as e:
        logger.error(f"Error in portfolio analysis: {str(e)}")
        return render_template('errors/500.html'), 500

@analytics_bp.route('/api/trends/data')
def get_trends_data():
    """API endpoint for trends data."""
    try:
        # Get filter parameters
        category = request.args.get('category')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        limit = int(request.args.get('limit', 20))
        
        # Build aggregation pipeline
        pipeline = []
        
        # Add match stage for filters
        match_stage = {}
        if category:
            match_stage['category'] = category
        if start_date_str:
            match_stage['created_at'] = {'$gte': datetime.strptime(start_date_str, '%Y-%m-%d')}
        if end_date_str:
            match_stage['created_at'] = {'$lte': datetime.strptime(end_date_str, '%Y-%m-%d')}
        
        if match_stage:
            pipeline.append({'$match': match_stage})
        
        # Add sort and limit stages
        pipeline.extend([
            {'$sort': {'created_at': -1}},
            {'$limit': limit}
        ])
        
        # Execute aggregation
        trends = mongodb_service.aggregate('trends', pipeline)
        
        # Format data for chart
        chart_data = {
            'labels': [trend.get('title', '') for trend in trends],
            'datasets': [
                {
                    'label': 'Engagement Score',
                    'data': [trend.get('engagement_score', 0) for trend in trends],
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'borderWidth': 1
                }
            ]
        }
        
        return jsonify(chart_data)
    except Exception as e:
        logger.error(f"Error getting trends data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/trends/<trend_id>')
def get_trend_details(trend_id):
    """API endpoint for trend details."""
    try:
        # Use the singleton MongoDB service instance
        mongodb = mongodb_service
        
        # Get trend details
        trend = mongodb.get_trend_by_id(trend_id)
        
        if not trend:
            return jsonify({'error': 'Trend not found'}), 404
        
        # Get trend metrics
        metrics = mongodb.get_trend_metrics(trend_id)
        
        return jsonify({
            'trend': trend,
            'metrics': metrics
        })
    except Exception as e:
        logger.error(f"Error getting trend details: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/portfolio/metrics')
def get_portfolio_metrics():
    """API endpoint for portfolio metrics."""
    try:
        # Use aggregation pipeline for better performance
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'total_companies': {'$sum': 1},
                    'total_investment': {'$sum': '$investment_amount'},
                    'average_roi': {'$avg': '$roi'},
                    'sector_distribution': {
                        '$push': {
                            'sector': {'$ifNull': ['$sector', 'Unknown']},
                            'count': 1
                        }
                    }
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'total_companies': 1,
                    'total_investment': 1,
                    'average_roi': 1,
                    'sector_distribution': {
                        '$reduce': {
                            'input': '$sector_distribution',
                            'initialValue': {},
                            'in': {
                                '$mergeObjects': [
                                    '$$value',
                                    {
                                        '$literal': {
                                            '$concat': [
                                                {'$toString': '$$this.sector'},
                                                ': ',
                                                {'$toString': '$$this.count'}
                                            ]
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        ]
        
        result = mongodb_service.aggregate('portfolio_companies', pipeline)
        metrics = result[0] if result else {
            'total_companies': 0,
            'total_investment': 0,
            'average_roi': 0,
            'sector_distribution': {}
        }
        
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Error getting portfolio metrics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/data')
def get_data():
    """API endpoint for raw data."""
    try:
        # Use the singleton MongoDB service instance
        mongodb = mongodb_service
        
        # Get collection name from query parameter
        collection = request.args.get('collection', 'trends')
        
        # Get filter parameters
        limit = int(request.args.get('limit', 100))
        
        # Get data from collection
        data = mongodb.find_many(collection, query={}, limit=limit)
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/unified-dashboard')
def unified_dashboard():
    """Render the unified analytics dashboard."""
    try:
        # Use the singleton MongoDB service instance
        mongodb = mongodb_service
        
        # Fetch key metrics
        metrics = {
            'trends_count': len(mongodb.find_many('trends', query={})),
            'companies_count': len(mongodb.find_many('portfolio_companies', query={})),
            'strategies_count': len(mongodb.find_many('strategies', query={}))
        }
        
        # Fetch recent trends
        trends = mongodb.get_trends(limit=5)
        
        # Fetch portfolio companies
        companies = mongodb.find_many('portfolio_companies', query={}, sort=[('name', 1)], limit=5)
        
        return render_template('analytics/unified_dashboard.html',
                             metrics=metrics,
                             trends=trends,
                             companies=companies)
    except Exception as e:
        logger.error(f"Error in unified dashboard: {str(e)}")
        return render_template('errors/500.html'), 500

@analytics_bp.route('/monetization-strategies')
def monetization_strategies():
    """Render the monetization strategies page."""
    try:
        # Use the singleton MongoDB service instance
        mongodb = mongodb_service
        
        # Fetch monetization strategies
        strategies = mongodb.find_many('strategies', query={}, sort=[('name', 1)])
        
        # Fetch related trends
        trends = mongodb.get_trends(limit=10)
        
        return render_template('analytics/monetization_strategies.html',
                             strategies=strategies,
                             trends=trends)
    except Exception as e:
        logger.error(f"Error in monetization strategies: {str(e)}")
        return render_template('errors/500.html'), 500

@analytics_bp.route('/story-cards')
def story_cards():
    """Render the story cards page."""
    try:
        # Use the singleton MongoDB service instance
        mongodb = mongodb_service
        
        # Fetch stories
        stories = mongodb.find_many('stories', query={}, sort=[('date', -1)], limit=10)
        
        return render_template('analytics/story_cards.html',
                             stories=stories)
    except Exception as e:
        logger.error(f"Error in story cards: {str(e)}")
        return render_template('errors/500.html'), 500

@analytics_bp.route('/analytics-dashboard')
def analytics_dashboard():
    """Render the analytics dashboard."""
    return redirect(url_for('analytics.dashboard'))

@analytics_bp.route('/metrics')
def get_metrics():
    """API endpoint for application metrics."""
    try:
        # Use the singleton MongoDB service instance
        mongodb = mongodb_service
        
        # Get metrics from MongoDB
        metrics = {
            'trends_count': len(mongodb.find_many('trends', query={})),
            'companies_count': len(mongodb.find_many('portfolio_companies', query={})),
            'strategies_count': len(mongodb.find_many('strategies', query={}))
        }
        
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500

@analytics_bp.route('/clear-cache')
def clear_cache():
    """Clear the application cache."""
    try:
        # This is a placeholder for cache clearing functionality
        # In a real application, you would implement cache clearing logic here
        
        flash('Cache cleared successfully', 'success')
        return redirect(url_for('analytics.dashboard'))
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        flash('Error clearing cache', 'error')
        return redirect(url_for('analytics.dashboard')) 