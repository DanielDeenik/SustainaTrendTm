"""
Monetization Strategies routes for SustainaTrend Intelligence Platform
"""

import json
import logging
from flask import Blueprint, render_template, request, jsonify

# Import necessary functions from centralized utils module
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from navigation_config import get_context_for_template
from monetization_strategies import (
    analyze_monetization_opportunities,
    generate_monetization_opportunities,
    get_monetization_strategies,
    generate_integrated_strategic_plan
)

# Import strategy frameworks
try:
    from strategy_simulation import STRATEGY_FRAMEWORKS
except ImportError:
    # Fallback if the strategy_simulation module is not available
    STRATEGY_FRAMEWORKS = {
        "porters": {
            "id": "porters",
            "name": "Porter's Five Forces",
            "description": "Analyze competitive forces shaping sustainability positioning",
            "icon": "chart-bar"
        },
        "swot": {
            "id": "swot",
            "name": "SWOT Analysis",
            "description": "Evaluate strengths, weaknesses, opportunities and threats",
            "icon": "grid-2x2"
        },
        "bcg": {
            "id": "bcg",
            "name": "BCG Growth-Share Matrix",
            "description": "Prioritize investments based on market growth and share",
            "icon": "pie-chart"
        }
    }

# Create blueprint
monetization_bp = Blueprint('monetization', __name__)

# Configure logging
logger = logging.getLogger(__name__)

@monetization_bp.route('/monetization-strategies')
@monetization_bp.route('/monetization-opportunities')  # Added route to match navigation
def monetization_strategies_dashboard():
    """Monetization Strategies Dashboard"""
    logger.info("Monetization strategies dashboard route called")
    
    # Include navigation for the template
    nav_context = get_context_for_template()
    
    # Get monetization strategies data
    strategies = get_monetization_strategies()
    
    # Format for JSON serialization
    formatted_strategies = json.dumps(strategies)
    
    # Use the consolidated dark themed template
    logger.info("Using consolidated dark themed template for monetization strategies")
    return render_template(
        "finchat_dark_dashboard.html", 
        page_title="Strategies",
        template_type="monetization",
        strategies=strategies,
        strategies_json=formatted_strategies,
        **nav_context  # Include all navigation context
    )

@monetization_bp.route('/api/monetization/analyze', methods=['POST'])
def api_monetization_analyze():
    """API endpoint for analyzing monetization opportunities"""
    data = request.get_json()
    
    if not data or 'document_text' not in data:
        return jsonify({
            'success': False,
            'error': 'Missing document_text parameter'
        }), 400
    
    document_text = data['document_text']
    result = analyze_monetization_opportunities(document_text)
    
    return jsonify({
        'success': True,
        'analysis': result
    })

@monetization_bp.route('/api/monetization/opportunities', methods=['POST'])
def api_monetization_opportunities():
    """API endpoint for generating monetization opportunities"""
    data = request.get_json()
    
    if not data or 'document_text' not in data:
        return jsonify({
            'success': False,
            'error': 'Missing document_text parameter'
        }), 400
    
    document_text = data['document_text']
    result = generate_monetization_opportunities(document_text)
    
    return jsonify({
        'success': True,
        'opportunities': result
    })

@monetization_bp.route('/monetization-opportunities/strategic-plan')
def integrated_strategy_plan():
    """Integrated Strategy Plan combining monetization with consulting frameworks"""
    logger.info("Monetization strategic plan route called")
    
    company_name = request.args.get('company', 'Your Company')
    industry = request.args.get('industry', 'Technology')
    
    # Include navigation for the template
    nav_context = get_context_for_template()
    
    return render_template(
        "finchat_dark_dashboard.html", 
        page_title="Strategic Plan",
        template_type="monetization",
        section="strategic-plan",
        company_name=company_name,
        industry=industry,
        frameworks=STRATEGY_FRAMEWORKS,
        **nav_context
    )

@monetization_bp.route('/api/monetization/strategic-plan', methods=['POST'])
def api_strategic_plan():
    """API endpoint for generating strategic monetization plan"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'Missing request data'
        }), 400
    
    company_name = data.get('company_name', 'Your Company')
    industry = data.get('industry', 'Technology')
    document_text = data.get('document_text', '')
    
    # Generate strategic plan using the imported function
    plan = generate_integrated_strategic_plan(company_name, industry, document_text)
    
    return jsonify({
        'success': True,
        'plan': plan
    })

@monetization_bp.route('/monetization-strategy-consulting')
def monetization_strategy_consulting():
    """Monetization Strategy Consulting Dashboard"""
    logger.info("Monetization strategy consulting route called")
    
    # Include navigation for the template
    nav_context = get_context_for_template()
    
    return render_template(
        "finchat_dark_dashboard.html", 
        page_title="Strategy Consulting",
        template_type="monetization",
        section="consulting",
        frameworks=STRATEGY_FRAMEWORKS,
        **nav_context
    )

@monetization_bp.route('/monetization-strategy/framework/<framework_id>')
def monetization_strategy_framework(framework_id):
    """Specific Monetization Strategy Framework"""
    logger.info(f"Monetization strategy framework route called: {framework_id}")
    
    # Include navigation for the template
    nav_context = get_context_for_template()
    
    # Get the specific framework
    framework = STRATEGY_FRAMEWORKS.get(framework_id)
    
    if not framework:
        return render_template('error.html', message=f"Framework {framework_id} not found"), 404
    
    # Get related strategies
    strategies = [s for s in get_monetization_strategies().values() 
                 if framework_id in s.get('frameworks', [])]
    
    return render_template(
        "finchat_dark_dashboard.html", 
        page_title=f"{framework.get('name')} Framework",
        template_type="monetization",
        section="framework",
        framework_id=framework_id,
        framework=framework,
        strategies=strategies,
        **nav_context
    )

@monetization_bp.route('/api/monetization/strategy-frameworks')
def api_strategy_frameworks():
    """API endpoint for getting available strategy frameworks"""
    
    return jsonify({
        'success': True,
        'frameworks': STRATEGY_FRAMEWORKS
    })