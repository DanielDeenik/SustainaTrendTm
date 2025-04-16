"""
Main routes for the SustainaTrend™ Intelligence Platform.

This module contains the main routes for the application, including the home page,
dashboard, and other core pages.
"""

from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, current_app
import logging
from src.frontend.refactored.services.mongodb_service import MongoDBService

# Configure logger
logger = logging.getLogger(__name__)

# Create blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Redirect to the dashboard."""
    return redirect(url_for('main.dashboard'))

@main_bp.route('/dashboard')
def dashboard():
    """Render the main dashboard page."""
    try:
        # Get MongoDB service
        mongodb = current_app.mongodb
        
        # Fetch recent trends
        recent_trends = mongodb.find_many(
            'trends',
            sort=[('created_at', -1)],
            limit=5
        )
        
        # Fetch portfolio companies
        portfolio_companies = mongodb.find_many(
            'portfolio_companies',
            sort=[('name', 1)]
        )
        
        return render_template(
            'dashboard.html',
            recent_trends=recent_trends,
            portfolio_companies=portfolio_companies
        )
    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}")
        return render_template('errors/500.html'), 500

@main_bp.route('/api/health')
def health_check():
    """API endpoint for health check."""
    try:
        # Check MongoDB connection
        mongodb = current_app.mongodb
        mongodb.client.server_info()
        
        return jsonify({
            'status': 'healthy',
            'mongodb': 'connected',
            'version': current_app.config['VERSION']
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@main_bp.route('/api/metrics')
def get_metrics():
    """API endpoint for fetching key metrics."""
    try:
        mongodb = current_app.mongodb
        
        # Fetch metrics from different collections
        portfolio_metrics = mongodb.find_many('portfolio_companies')
        trend_metrics = mongodb.find_many('trends')
        story_metrics = mongodb.find_many('stories')
        
        return jsonify({
            'portfolio_count': len(portfolio_metrics),
            'trend_count': len(trend_metrics),
            'story_count': len(story_metrics)
        })
    except Exception as e:
        logger.error(f"Error fetching metrics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@main_bp.route('/companies')
def companies():
    """Render the companies page."""
    try:
        mongodb = MongoDBService()
        companies = mongodb.get_collection('companies').find()
        return render_template('companies.html', title='Companies', companies=list(companies))
    except Exception as e:
        logger.error(f"Error rendering companies page: {str(e)}")
        return render_template('errors/500.html'), 500

@main_bp.route('/trends')
def trends():
    """Render the trends page."""
    try:
        mongodb = MongoDBService()
        trends = mongodb.get_collection('trends').find()
        return render_template('trends.html', title='Sustainability Trends', trends=list(trends))
    except Exception as e:
        logger.error(f"Error rendering trends page: {str(e)}")
        return render_template('errors/500.html'), 500

@main_bp.route('/strategies')
def strategies():
    """Render the strategies page."""
    try:
        mongodb = MongoDBService()
        strategies = mongodb.get_collection('strategies').find()
        return render_template('strategies.html', title='Monetization Strategies', strategies=list(strategies))
    except Exception as e:
        logger.error(f"Error rendering strategies page: {str(e)}")
        return render_template('errors/500.html'), 500

@main_bp.route('/company/<string:company_id>')
def company_detail(company_id):
    """Render the company detail page."""
    try:
        mongodb = MongoDBService()
        company = mongodb.get_collection('companies').find_one({'_id': company_id})
        if not company:
            flash('Company not found', 'error')
            return redirect(url_for('main.companies'))
            
        metrics = mongodb.get_collection('metrics').find({'company_id': company_id})
        stories = mongodb.get_collection('stories').find({'company_id': company_id})
        
        return render_template(
            'company_detail.html',
            title=f'Company - {company["name"]}',
            company=company,
            metrics=list(metrics),
            stories=list(stories)
        )
    except Exception as e:
        logger.error(f"Error rendering company detail page: {str(e)}")
        return render_template('errors/500.html'), 500

@main_bp.route('/about')
def about():
    """Render the about page."""
    try:
        return render_template('about.html', title='About SustainaTrend™')
    except Exception as e:
        logger.error(f"Error rendering about page: {str(e)}")
        return render_template('errors/500.html'), 500

@main_bp.route('/contact')
def contact():
    """Render the contact page."""
    try:
        return render_template('contact.html', title='Contact Us')
    except Exception as e:
        logger.error(f"Error rendering contact page: {str(e)}")
        return render_template('errors/500.html'), 500 