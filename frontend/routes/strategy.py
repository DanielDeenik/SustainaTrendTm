"""
Strategy Hub routes for SustainaTrend Intelligence Platform

This module consolidates all strategy, simulation, and monetization routes
into a single cohesive interface.
"""

import json
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import navigation context
from navigation_config import get_context_for_template

# Import monetization functions
from monetization_strategies import (
    analyze_monetization_opportunities,
    generate_monetization_opportunities,
    get_monetization_strategies,
    generate_integrated_strategic_plan,
    MONETIZATION_FRAMEWORK,
    PRELOADED_MONETIZATION_STRATEGIES
)

# Import strategy frameworks (if available) or use fallback
try:
    from strategy_simulation import get_frameworks, analyze_with_framework
    STRATEGY_FRAMEWORKS = get_frameworks()
except (ImportError, AttributeError):
    # Fallback if strategy_simulation module is not available or doesn't have get_frameworks
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
    
    def analyze_with_framework(framework_id, analysis_data, company_name, industry):
        """
        Fallback analyze_with_framework function when the real one is not available
        """
        return {
            "success": True,
            "framework": STRATEGY_FRAMEWORKS.get(framework_id, {"name": "Unknown Framework"}),
            "company": company_name,
            "industry": industry,
            "analysis": {
                "summary": f"Simulated analysis for {company_name} using {framework_id} framework.",
                "strengths": ["Innovative sustainability approach", "Strong data analytics"],
                "opportunities": ["New market segments", "Green financing"],
                "data": analysis_data
            }
        }

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
strategy_bp = Blueprint('strategy', __name__)

@strategy_bp.route('/strategy-hub')
def strategy_hub():
    """
    Unified Strategy Hub page combining all strategy frameworks and monetization options
    """
    logger.info("Strategy Hub route called")
    
    try:
        # Include navigation for the template
        nav_context = get_context_for_template()
        
        # Use the preloaded strategies directly - most reliable option
        try:
            # Create a NEW dictionary by copying the preloaded strategies
            # This ensures we're not passing a function or method reference
            monetization_strategies = dict(PRELOADED_MONETIZATION_STRATEGIES)
            
            # Debug
            logger.info(f"Using PRELOADED_MONETIZATION_STRATEGIES directly")
            logger.info(f"monetization_strategies type: {type(monetization_strategies)}")
            logger.info(f"monetization_strategies has {len(monetization_strategies)} items")
            logger.info(f"monetization_strategies keys: {list(monetization_strategies.keys())}")
                    
        except Exception as e:
            logger.warning(f"Error creating monetization strategies: {str(e)}")
            # Fallback if everything fails
            monetization_strategies = {
                "strategy1": {
                    "name": "Sustainability SaaS",
                    "icon": "cloud",
                    "short_description": "Cloud-based sustainability analytics platform",
                    "default_potential": 85
                },
                "strategy2": {
                    "name": "Consulting Services", 
                    "icon": "handshake",
                    "short_description": "Advisory services for sustainability implementation",
                    "default_potential": 70
                },
                "strategy3": {
                    "name": "Data Marketplace",
                    "icon": "database",
                    "short_description": "Monetize anonymized sustainability datasets",
                    "default_potential": 65
                }
            }
        
        # Debug what we're passing to the template
        logger.info(f"STRATEGY_FRAMEWORKS type: {type(STRATEGY_FRAMEWORKS)}")
        logger.info(f"monetization_strategies type: {type(monetization_strategies)}")
        
        # First try to use the specialized template for the Strategy Hub
        try:
            return render_template(
                "strategy_hub.html", 
                page_title="Strategy Hub",
                frameworks=STRATEGY_FRAMEWORKS,
                monetization_strategies=monetization_strategies,
                **nav_context  # Pass the entire navigation context as kwargs
            )
        except Exception as e:
            logger.warning(f"Strategy hub template error: {str(e)}, falling back to generic template")
            # Fall back to the generic template if there's an issue with the specialized one
            return render_template(
                "finchat_dark_dashboard.html", 
                page_title="Strategy Hub",
                template_type="strategy",
                section="hub",
                frameworks=STRATEGY_FRAMEWORKS,
                monetization_strategies=monetization_strategies,
                **nav_context
            )
    except Exception as e:
        # Ultimate fallback if both navigation context and template fail
        logger.error(f"Critical error in strategy hub: {str(e)}")
        
        # Create a minimal fallback dictionary directly
        monetization_strategies = {
            "strategy1": {
                "name": "Sustainability SaaS",
                "icon": "cloud",
                "short_description": "Cloud-based sustainability analytics platform",
                "default_potential": 85
            },
            "strategy2": {
                "name": "Consulting Services", 
                "icon": "handshake",
                "short_description": "Advisory services for sustainability implementation",
                "default_potential": 70
            },
            "strategy3": {
                "name": "Data Marketplace",
                "icon": "database",
                "short_description": "Monetize anonymized sustainability datasets",
                "default_potential": 65
            }
        }
        
        return render_template(
            "finchat_dark_dashboard.html", 
            page_title="Strategy Hub",
            template_type="strategy",
            section="hub",
            frameworks=STRATEGY_FRAMEWORKS,
            monetization_strategies=monetization_strategies
        )

@strategy_bp.route('/strategy-hub/framework/<framework_id>')
def strategy_framework(framework_id):
    """
    Specific Strategy Framework page
    """
    logger.info(f"Strategy framework route called: {framework_id}")
    
    # Get the specific framework
    framework = STRATEGY_FRAMEWORKS.get(framework_id)
    
    if not framework:
        return render_template('error.html', message=f"Framework {framework_id} not found"), 404
    
    try:
        # Include navigation for the template
        nav_context = get_context_for_template()
        
        # Create strategies using the preloaded strategies directly
        try:
            # Create a new dictionary to ensure we're not working with a method reference
            monetization_strategies = dict(PRELOADED_MONETIZATION_STRATEGIES)
            
            # Debug info
            logger.info(f"Framework view - monetization_strategies type: {type(monetization_strategies)}")
            logger.info(f"Framework view - monetization_strategies has {len(monetization_strategies)} items")
            
            # Add frameworks field to each strategy
            for strategy_id, strategy in monetization_strategies.items():
                # Ensure we have frameworks field
                if "frameworks" not in strategy:
                    strategy["frameworks"] = []
            
            # For this example, we'll associate certain frameworks with strategies
            if framework_id == "porters":
                frameworks_to_associate = ["M1", "M4", "M5"]
            elif framework_id == "swot":
                frameworks_to_associate = ["M2", "M3", "M6"]
            else:
                frameworks_to_associate = ["M1", "M2"]
                
            # Add frameworks associations
            for strategy_id in frameworks_to_associate:
                if strategy_id in monetization_strategies:
                    monetization_strategies[strategy_id]["frameworks"] = [framework_id]
                    
            # Extract related strategies
            strategies = [s for s in monetization_strategies.values() 
                        if framework_id in s.get('frameworks', [])]
            
            # If still no related strategies, generate a default
            if not strategies:
                strategies = [{
                    "name": f"{framework_id.capitalize()} Strategy",
                    "icon": "lightbulb",
                    "short_description": f"Strategic approach using {framework_id}",
                    "default_potential": 75
                }]
                
        except Exception as e:
            logger.warning(f"Error creating strategies for framework: {str(e)}")
            # Fallback with a default strategy
            strategies = [{
                "name": f"{framework_id.capitalize()} Strategy",
                "icon": "lightbulb",
                "short_description": f"Strategic approach using {framework_id}",
                "default_potential": 75
            }]
        
        return render_template(
            "finchat_dark_dashboard.html", 
            page_title=f"{framework.get('name')} Framework",
            template_type="strategy",
            section="framework",
            framework_id=framework_id,
            framework=framework,
            strategies=strategies,
            **nav_context
        )
    except Exception as e:
        logger.warning(f"Error in framework page: {str(e)}, using minimal context")
        # Ultimate fallback if navigation fails - use same strategy as above
        strategies = [{
            "name": f"{framework_id.capitalize()} Strategy",
            "icon": "lightbulb", 
            "short_description": f"Strategic approach using {framework_id}",
            "default_potential": 75
        }]
        
        return render_template(
            "finchat_dark_dashboard.html", 
            page_title=f"{framework.get('name')} Framework",
            template_type="strategy",
            section="framework",
            framework_id=framework_id,
            framework=framework,
            strategies=strategies
        )
    

@strategy_bp.route('/strategy-hub/monetization')
def monetization_strategies_view():
    """
    Monetization Strategies page (redirects to Strategy Hub)
    """
    return redirect(url_for('strategy.strategy_hub'))

@strategy_bp.route('/strategy-hub/simulation')
def strategy_simulation_view():
    """
    Strategy Simulation page (redirects to Strategy Hub)
    """
    return redirect(url_for('strategy.strategy_hub'))

# API Routes

@strategy_bp.route('/api/strategy/frameworks')
def api_strategy_frameworks():
    """API endpoint for getting available strategy frameworks"""
    return jsonify({
        'success': True,
        'frameworks': STRATEGY_FRAMEWORKS
    })

@strategy_bp.route('/api/strategy/framework-analysis', methods=['POST'])
def api_framework_analysis():
    """API endpoint for framework analysis"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        framework_id = data.get('framework_id')
        company_name = data.get('company_name', 'Sample Company')
        industry = data.get('industry', 'Real Estate')
        analysis_data = data.get('data', {})
        
        if not framework_id:
            return jsonify({"error": "No framework_id provided"}), 400
            
        result = analyze_with_framework(framework_id, analysis_data, company_name, industry)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in framework analysis API: {str(e)}")
        return jsonify({"error": str(e)}), 500

@strategy_bp.route('/api/strategy/monetization', methods=['POST'])
def api_monetization_analysis():
    """API endpoint for monetization analysis"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Missing request data'
            }), 400
        
        company_name = data.get('company_name', 'Your Company')
        industry = data.get('industry', 'Technology')
        document_text = data.get('document_text', '')
        
        if document_text:
            opportunities = analyze_monetization_opportunities(document_text)
        else:
            # Generate analysis based on company and industry
            opportunities = analyze_monetization_opportunities(
                f"Strategic plan for {company_name} in {industry} sector"
            )
        
        return jsonify({
            'success': True,
            'opportunities': opportunities
        })
    except Exception as e:
        logger.error(f"Error in monetization analysis API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@strategy_bp.route('/api/strategy/strategic-plan', methods=['POST'])
def api_strategic_plan():
    """API endpoint for generating strategic monetization plan"""
    try:
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
    except Exception as e:
        logger.error(f"Error in strategic plan API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Debug route to check the data structures
@strategy_bp.route('/strategy-hub/debug')
def strategy_hub_debug():
    """Debug route to examine the monetization_strategies object"""
    logger.info("Strategy Hub Debug route called")
    
    # Get monetization strategies directly
    monetization_strategies = PRELOADED_MONETIZATION_STRATEGIES
    
    # Create a debug report
    debug_data = {
        "monetization_strategies_type": str(type(monetization_strategies)),
        "monetization_strategies_keys": list(monetization_strategies.keys()) if isinstance(monetization_strategies, dict) else "Not a dict",
        "has_items_method": hasattr(monetization_strategies, 'items'),
        "frameworks_type": str(type(STRATEGY_FRAMEWORKS)),
        "frameworks_keys": list(STRATEGY_FRAMEWORKS.keys())
    }
    
    return jsonify(debug_data)

# Simple test route with minimal template
@strategy_bp.route('/strategy-hub/test')
def strategy_hub_test():
    """Test route with minimal template"""
    logger.info("Strategy Hub Test route called")
    
    try:
        # Get monetization strategies directly - create a copy
        monetization_strategies = dict(PRELOADED_MONETIZATION_STRATEGIES)
        
        logger.info(f"Test route - monetization_strategies type: {type(monetization_strategies)}")
        logger.info(f"Test route - monetization_strategies has {len(monetization_strategies)} items")
        logger.info(f"Test route - monetization_strategies keys: {list(monetization_strategies.keys())}")
        
        # Render simple test template
        return render_template(
            "strategy_test.html",
            frameworks=STRATEGY_FRAMEWORKS,
            monetization_strategies=monetization_strategies
        )
    except Exception as e:
        logger.error(f"Error in test route: {str(e)}")
        return f"Test route error: {str(e)}", 500

# Legacy route redirects
@strategy_bp.route('/monetization-opportunities')
@strategy_bp.route('/monetization-strategies')
def legacy_monetization_redirect():
    """Redirect legacy monetization routes to strategy hub"""
    return redirect(url_for('strategy.strategy_hub'))

@strategy_bp.route('/sustainability-strategies')
def legacy_strategies_redirect():
    """Redirect legacy strategies routes to strategy hub"""
    return redirect(url_for('strategy.strategy_hub'))

@strategy_bp.route('/strategy-simulation')
def legacy_simulation_redirect():
    """Redirect legacy simulation routes to strategy hub"""
    return redirect(url_for('strategy.strategy_hub'))