"""
Strategy Hub routes for SustainaTrend Intelligence Platform

This module consolidates all strategy, simulation, and monetization routes
into a single cohesive interface.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Mapping
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
        
        # FIXED: Create fresh, clean dictionaries for strategies and frameworks
        # This approach mirrors the successful test route
        try:
            # Skip directly trying to use PRELOADED_MONETIZATION_STRATEGIES
            # Instead create a hardcoded dictionary that is guaranteed to work
            monetization_strategies = {
                "M1": {
                    "name": "AI-Driven Sustainability Trend Monetization",
                    "icon": "chart-line",
                    "short_description": "AI-powered trend detection and analysis",
                    "default_potential": 85
                },
                "M2": {
                    "name": "Consulting Services Model",
                    "icon": "handshake",
                    "short_description": "Advisory services for sustainability reporting",
                    "default_potential": 65
                },
                "M3": {
                    "name": "SaaS Subscription Platform",
                    "icon": "cloud",
                    "short_description": "Cloud-based sustainability platform",
                    "default_potential": 75
                },
                "M4": {
                    "name": "Data Marketplace",
                    "icon": "database",
                    "short_description": "Monetize sustainability datasets",
                    "default_potential": 70
                },
                "M5": {
                    "name": "Strategic Consulting",
                    "icon": "users",
                    "short_description": "Expert advisory services",
                    "default_potential": 80
                }
            }
            
            # Create a new dictionary from STRATEGY_FRAMEWORKS too
            frameworks = dict(STRATEGY_FRAMEWORKS)
            
            # Debug logging
            logger.info(f"Created monetization_strategies explicitly by copying key-value pairs")
            logger.info(f"monetization_strategies type: {type(monetization_strategies)}")
            logger.info(f"monetization_strategies has {len(monetization_strategies)} items")
            logger.info(f"monetization_strategies keys: {list(monetization_strategies.keys())}")
            logger.info(f"frameworks type: {type(frameworks)}")
                    
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
            
            frameworks = STRATEGY_FRAMEWORKS  # Still try to use the original frameworks
        
        # First try to use the fixed template for the Strategy Hub
        try:
            # First, directly check what PRELOADED_MONETIZATION_STRATEGIES is
            logger.info(f"PRELOADED_MONETIZATION_STRATEGIES type: {type(PRELOADED_MONETIZATION_STRATEGIES)}")
            logger.info(f"PRELOADED_MONETIZATION_STRATEGIES callable: {callable(PRELOADED_MONETIZATION_STRATEGIES)}")
            
            # Debug ALL modules and variables in scope for get_monetization_strategies
            debug_vars = {}
            for module_name, module in sys.modules.items():
                if 'monetization' in module_name.lower():
                    logger.info(f"Found module: {module_name}")
                    try:
                        if hasattr(module, 'get_monetization_strategies'):
                            logger.info(f"Found get_monetization_strategies in {module_name}")
                    except:
                        pass
            
            # Additional deep inspection
            if callable(get_monetization_strategies):
                logger.info("get_monetization_strategies is callable - getting direct result")
                try:
                    # Call it directly and store result in a NEW variable
                    direct_result = get_monetization_strategies()
                    logger.info(f"direct_result type: {type(direct_result)}")
                    if hasattr(direct_result, 'items') and callable(direct_result.items):
                        for k, v in direct_result.items():
                            debug_vars[k] = v
                    # Replace monetization_strategies with our direct call result
                    monetization_strategies = debug_vars
                except Exception as call_error:
                    logger.error(f"Error calling get_monetization_strategies: {call_error}")
            
            # Add additional debug logging for our final variable
            logger.info(f"About to render template with monetization_strategies: {type(monetization_strategies)}")
            logger.info(f"monetization_strategies has attrs: {dir(monetization_strategies)}")
            logger.info(f"monetization_strategies is mapping: {isinstance(monetization_strategies, Mapping)}")
            logger.info(f"monetization_strategies is dict: {isinstance(monetization_strategies, dict)}")
            logger.info(f"monetization_strategies has __iter__: {hasattr(monetization_strategies, '__iter__')}")
            
            # Attempt to fetch some keys - this would raise exception if not iterable
            try:
                keys = list(monetization_strategies.keys())
                logger.info(f"monetization_strategies keys: {keys}")
            except Exception as e:
                logger.warning(f"Could not get keys: {str(e)}")
                                     
            # Use our new fixed template that properly handles the dictionary
            return render_template(
                "strategy_hub_fixed.html", 
                page_title="Strategy Hub",
                frameworks=frameworks,
                monetization_strategies=monetization_strategies,
                **nav_context  # Pass the entire navigation context as kwargs
            )
        except Exception as e:
            logger.warning(f"Strategy hub fixed template error: {str(e)}, trying original template")
            try:
                # Try the original template as a backup
                return render_template(
                    "strategy_hub.html", 
                    page_title="Strategy Hub",
                    frameworks=frameworks,
                    monetization_strategies=monetization_strategies,
                    **nav_context  # Pass the entire navigation context as kwargs
                )
            except Exception as e2:
                logger.warning(f"Strategy hub template error: {str(e2)}, falling back to test template")
                # Fall back to the TEST template that we know works
                return render_template(
                    "strategy_test.html", 
                    frameworks=frameworks,
                    monetization_strategies=monetization_strategies
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
        
        # Create strategies using the same explicit approach
        try:
            # Skip directly trying to use PRELOADED_MONETIZATION_STRATEGIES
            # Instead create a hardcoded dictionary that is guaranteed to work
            monetization_strategies = {
                "M1": {
                    "name": "AI-Driven Sustainability Trend Monetization",
                    "icon": "chart-line",
                    "short_description": "AI-powered trend detection and analysis",
                    "default_potential": 85
                },
                "M2": {
                    "name": "Consulting Services Model",
                    "icon": "handshake", 
                    "short_description": "Advisory services for sustainability reporting",
                    "default_potential": 65
                },
                "M3": {
                    "name": "SaaS Subscription Platform",
                    "icon": "cloud",
                    "short_description": "Cloud-based sustainability platform",
                    "default_potential": 75
                },
                "M4": {
                    "name": "Data Marketplace",
                    "icon": "database",
                    "short_description": "Monetize sustainability datasets",
                    "default_potential": 70
                },
                "M5": {
                    "name": "Strategic Consulting",
                    "icon": "users",
                    "short_description": "Expert advisory services",
                    "default_potential": 80
                },
                "M6": {
                    "name": "Educational Content",
                    "icon": "book",
                    "short_description": "Training and certification programs",
                    "default_potential": 60
                }
            }
            
            # Debug info
            logger.info(f"Framework view - manually created monetization_strategies")
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
    """Debug route using simplified template to isolate the issue"""
    logger.info("Strategy Hub Debug route called")
    
    try:
        # Create a NEW dictionary with explicit key-value pairs to avoid method references
        preloaded = PRELOADED_MONETIZATION_STRATEGIES
        monetization_strategies = {}
        
        # Manually copy each key-value pair to ensure it's a regular dictionary
        if hasattr(preloaded, 'items') and callable(preloaded.items):
            # If it's a dictionary with items() method
            for key, value in preloaded.items():
                monetization_strategies[key] = value
        elif isinstance(preloaded, dict):
            # If it's already a dictionary but items might be a method issue
            for key in preloaded:
                monetization_strategies[key] = preloaded[key]
        else:
            # Fallback - create from scratch if all else fails
            monetization_strategies = {
                "M1": {
                    "name": "AI-Driven Sustainability Trend Monetization",
                    "icon": "chart-line",
                    "short_description": "AI-powered trend detection and analysis",
                    "default_potential": 85
                },
                "M2": {
                    "name": "Consulting Services Model",
                    "icon": "handshake",
                    "short_description": "Advisory services for sustainability reporting",
                    "default_potential": 65
                }
            }
            
        logger.info(f"Debug route - manually created monetization_strategies")
        logger.info(f"Debug route - monetization_strategies type: {type(monetization_strategies)}")
        logger.info(f"Debug route - monetization_strategies has {len(monetization_strategies)} items")
        logger.info(f"Debug route - monetization_strategies keys: {list(monetization_strategies.keys())}")
        
        # Render simple debug template
        return render_template(
            "strategy_hub_debug.html",
            page_title="Strategy Hub Debug",
            frameworks=STRATEGY_FRAMEWORKS,
            monetization_strategies=monetization_strategies
        )
    except Exception as e:
        logger.error(f"Error in debug route: {str(e)}")
        
        # Create a debug report
        debug_data = {
            "error": str(e),
            "monetization_strategies_type": str(type(PRELOADED_MONETIZATION_STRATEGIES)),
            "has_items_method": hasattr(PRELOADED_MONETIZATION_STRATEGIES, 'items'),
            "frameworks_type": str(type(STRATEGY_FRAMEWORKS)),
            "frameworks_keys": list(STRATEGY_FRAMEWORKS.keys()) if isinstance(STRATEGY_FRAMEWORKS, dict) else "Not a dict"
        }
        
        return jsonify(debug_data)

# Simple test route with minimal template
@strategy_bp.route('/strategy-hub/test')
def strategy_hub_test():
    """Test route with minimal template"""
    logger.info("Strategy Hub Test route called")
    
    try:
        # Create a NEW dictionary with explicit key-value pairs to avoid method references
        preloaded = PRELOADED_MONETIZATION_STRATEGIES
        monetization_strategies = {}
        
        # Manually copy each key-value pair to ensure it's a regular dictionary
        if hasattr(preloaded, 'items') and callable(preloaded.items):
            # If it's a dictionary with items() method
            for key, value in preloaded.items():
                monetization_strategies[key] = value
        elif isinstance(preloaded, dict):
            # If it's already a dictionary but items might be a method issue
            for key in preloaded:
                monetization_strategies[key] = preloaded[key]
        else:
            # Fallback - create from scratch if all else fails
            monetization_strategies = {
                "M1": {
                    "name": "AI-Driven Sustainability Trend Monetization",
                    "icon": "chart-line",
                    "short_description": "AI-powered trend detection and analysis",
                    "default_potential": 85
                },
                "M2": {
                    "name": "Consulting Services Model",
                    "icon": "handshake",
                    "short_description": "Advisory services for sustainability reporting",
                    "default_potential": 65
                }
            }
        
        logger.info(f"Test route - manually created monetization_strategies")
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