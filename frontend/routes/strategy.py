"""
Strategy Hub routes for SustainaTrend Intelligence Platform - REDIRECT VERSION

This module redirects all legacy strategy routes to the new Enhanced Strategy Hub
for backward compatibility. All strategy functionality is now consolidated in
the enhanced_strategy.py module.
"""

import logging
from flask import Blueprint, redirect, url_for

# Create blueprint
strategy_bp = Blueprint('strategy', __name__, url_prefix='/strategy')
logger = logging.getLogger(__name__)

logger.info("Strategy blueprint initialized (redirect mode)")

@strategy_bp.route('/hub')
def strategy_hub():
    """Redirect to enhanced strategy hub"""
    return redirect(url_for('enhanced_strategy.strategy_hub'))

@strategy_bp.route('/modeling-tool')
def strategy_modeling_tool():
    """Redirect to enhanced strategy hub"""
    return redirect(url_for('enhanced_strategy.strategy_hub'))

@strategy_bp.route('/full')
def strategy_hub_full():
    """Redirect to enhanced strategy hub"""
    return redirect(url_for('enhanced_strategy.strategy_hub'))

@strategy_bp.route('/framework/<framework_id>')
def strategy_framework(framework_id):
    """Redirect to framework analysis in enhanced strategy hub"""
    return redirect(url_for('enhanced_strategy.strategy_hub'))

@strategy_bp.route('/simulation')
def strategy_simulation_view():
    """Redirect to enhanced strategy hub"""
    return redirect(url_for('enhanced_strategy.strategy_hub'))

@strategy_bp.route('/debug')
def strategy_hub_debug():
    """Redirect to enhanced strategy hub"""
    return redirect(url_for('enhanced_strategy.strategy_hub'))

@strategy_bp.route('/test')
def strategy_hub_test():
    """Redirect to enhanced strategy hub"""
    return redirect(url_for('enhanced_strategy.strategy_hub'))

@strategy_bp.route('/storytelling')
def strategy_hub_storytelling():
    """Redirect to enhanced strategy hub"""
    return redirect(url_for('enhanced_strategy.strategy_hub'))

@strategy_bp.route('/documents')
def strategy_hub_documents():
    """Redirect to enhanced strategy hub"""
    return redirect(url_for('enhanced_strategy.strategy_hub'))

@strategy_bp.route('/document/upload')
def strategy_hub_document_upload():
    """Redirect to enhanced strategy hub"""
    return redirect(url_for('enhanced_strategy.strategy_hub'))

@strategy_bp.route('/document/<document_id>')
def strategy_hub_document_view(document_id):
    """Redirect to enhanced strategy hub"""
    return redirect(url_for('enhanced_strategy.strategy_hub'))

@strategy_bp.route('/document/<document_id>/story')
def strategy_hub_generate_story(document_id):
    """Redirect to enhanced strategy hub"""
    return redirect(url_for('enhanced_strategy.strategy_hub'))

@strategy_bp.route('/data-analysis/<file_id>')
def strategy_hub_data_analysis(file_id):
    """Redirect to enhanced strategy hub"""
    return redirect(url_for('enhanced_strategy.strategy_hub'))

# Add a test endpoint to verify redirects
@strategy_bp.route('/test-redirect')
def test_redirect():
    """Test redirect functionality"""
    logger.info("Testing strategy redirect functionality")
    return redirect(url_for('enhanced_strategy.strategy_hub'))

# Register the blueprint with the app
def register_blueprint(app):
    """Register the strategy blueprint with Flask app"""
    app.register_blueprint(strategy_bp)
    logger.info("Strategy blueprint registered (redirect mode)")