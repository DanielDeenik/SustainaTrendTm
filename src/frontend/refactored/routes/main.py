"""
Main routes for the SustainaTrend™ Intelligence Platform.

This module contains the main routes for the application, including the home page,
dashboard, and other core pages.
"""

from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, current_app
import logging
from src.frontend.refactored.services.mongodb_service import mongodb_service
from src.frontend.refactored.services.config_service import config_service

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
        # Use the singleton MongoDB service instance
        mongodb = mongodb_service
        
        # Fetch recent trends
        recent_trends = mongodb.find(
            'trends',
            query={},
            sort=[('created_at', -1)],
            limit=5
        )
        
        # Fetch portfolio companies
        portfolio_companies = mongodb.find(
            'portfolio_companies',
            query={},
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
        # Use the singleton MongoDB service instance
        mongodb = mongodb_service
        
        # Check MongoDB connection
        mongodb_status = 'healthy' if mongodb.is_connected() else 'unhealthy'
        
        return jsonify({
            'status': 'healthy',
            'mongodb_status': mongodb_status,
            'version': config_service.get('VERSION', '1.0.0'),
            'environment': 'development' if config_service.is_debug() else 'production'
        })
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@main_bp.route('/api/metrics')
def get_metrics():
    """API endpoint for application metrics."""
    try:
        # Use the singleton MongoDB service instance
        mongodb = mongodb_service
        
        # Get metrics from MongoDB
        metrics = {
            'trends_count': len(mongodb.find('trends', query={})),
            'companies_count': len(mongodb.find('portfolio_companies', query={})),
            'strategies_count': len(mongodb.find('strategies', query={}))
        }
        
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500

@main_bp.route('/companies')
def companies():
    """Render the companies page."""
    try:
        # Use the singleton MongoDB service instance
        mongodb = mongodb_service
        
        # Fetch all companies
        companies = mongodb.find('portfolio_companies', query={}, sort=[('name', 1)])
        
        return render_template('companies.html', companies=companies)
    except Exception as e:
        logger.error(f"Error rendering companies page: {str(e)}")
        return render_template('errors/500.html'), 500

@main_bp.route('/trends')
def trends():
    """Render the trends page."""
    try:
        # Use the singleton MongoDB service instance
        mongodb = mongodb_service
        
        # Fetch all trends
        trends = mongodb.find('trends', query={}, sort=[('created_at', -1)])
        
        return render_template('trends.html', trends=trends)
    except Exception as e:
        logger.error(f"Error rendering trends page: {str(e)}")
        return render_template('errors/500.html'), 500

@main_bp.route('/strategies')
def strategies():
    """Render the strategies page."""
    try:
        # Use the singleton MongoDB service instance
        mongodb = mongodb_service
        
        # Fetch all strategies
        strategies = mongodb.find('strategies', query={}, sort=[('name', 1)])
        
        return render_template('strategies.html', strategies=strategies)
    except Exception as e:
        logger.error(f"Error rendering strategies page: {str(e)}")
        return render_template('errors/500.html'), 500

@main_bp.route('/company/<string:company_id>')
def company_detail(company_id):
    """Render the company detail page."""
    try:
        # Use the singleton MongoDB service instance
        mongodb = mongodb_service
        
        # Fetch company details
        company = mongodb.find('portfolio_companies', {'_id': company_id}, limit=1)
        if not company:
            logger.warning(f"Company not found: {company_id}")
            return render_template('errors/404.html'), 404
        
        # Fetch related trends
        related_trends = mongodb.find(
            'trends',
            query={'companies': company_id},
            sort=[('created_at', -1)]
        )
        
        return render_template(
            'company_detail.html',
            company=company[0] if company else None,
            related_trends=related_trends
        )
    except Exception as e:
        logger.error(f"Error rendering company detail page: {str(e)}")
        return render_template('errors/500.html'), 500

@main_bp.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    """Render the contact page."""
    return render_template('contact.html') 