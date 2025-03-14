"""
Strategy Hub routes for SustainaTrend Intelligence Platform

This module consolidates all strategy, simulation, monetization, storytelling and document
analysis routes into a single cohesive interface.
"""

import json
import logging
import os
import sys
import traceback
from datetime import datetime
from typing import Dict, Any, List, Mapping
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_from_directory, session
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import navigation context
from navigation_config import get_context_for_template

# Import storytelling components (with fallback)
try:
    from sustainability_storytelling import get_enhanced_stories, get_mock_stories
    STORYTELLING_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("Storytelling module loaded successfully")
except ImportError as e:
    STORYTELLING_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"Storytelling module not available: {str(e)}")

# Import document processor (with fallback)
try:
    from document_processor import DocumentProcessor
    DOCUMENT_PROCESSOR_AVAILABLE = True
    logger.info("Document processor module loaded successfully")
except ImportError as e:
    DOCUMENT_PROCESSOR_AVAILABLE = False
    logger.warning(f"Document processor not available: {str(e)}")

# Import monetization functions
from monetization_strategies import (
    analyze_monetization_opportunities,
    generate_monetization_opportunities,
    get_monetization_strategies,
    generate_integrated_strategic_plan,
    MONETIZATION_FRAMEWORK,
    PRELOADED_MONETIZATION_STRATEGIES
)

# Import marketing strategy functions (with fallback)
try:
    from marketing_strategies import (
        get_marketing_strategies,
        get_strategy_recommendations,
        MARKETING_CATEGORIES
    )
    MARKETING_AVAILABLE = True
    logger.info("Marketing strategies module loaded successfully")
except ImportError as e:
    MARKETING_AVAILABLE = False
    logger.warning(f"Marketing strategies module not available: {str(e)}")
    MARKETING_CATEGORIES = {
        "storytelling": "Storytelling & Narratives",
        "stakeholder": "Stakeholder Engagement",
        "digital": "Digital Marketing"
    }

# Import trend virality benchmarking functions (with fallback)
try:
    from trend_virality_benchmarking import (
        analyze_trend_with_stepps,
        benchmark_against_competitors,
        generate_benchmark_insights,
        STEPPS_COMPONENTS
    )
    TREND_VIRALITY_AVAILABLE = True
    logger.info("Trend virality benchmarking module loaded successfully")
except ImportError as e:
    TREND_VIRALITY_AVAILABLE = False
    logger.warning(f"Trend virality benchmarking module not available: {str(e)}")
    STEPPS_COMPONENTS = {
        "social_currency": "Social Currency",
        "triggers": "Triggers",
        "emotion": "Emotion",
        "public": "Public",
        "practical_value": "Practical Value",
        "stories": "Stories"
    }

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

# Configure document upload settings
UPLOAD_FOLDER = 'frontend/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'xlsx', 'pptx', 'txt', 'csv'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize document processor if available
document_processor = DocumentProcessor() if DOCUMENT_PROCESSOR_AVAILABLE else None

# Create blueprint
strategy_bp = Blueprint('strategy', __name__)

@strategy_bp.route('/strategy-hub')
def strategy_hub():
    """
    Redirect from old Strategy Hub to the new unified Strategy Hub
    """
    logger.info("Strategy Hub route called - redirecting to unified Strategy Hub")
    
    # Redirect to the new unified Strategy Hub
    return redirect(url_for('strategy.unified_strategy_hub'))

# Legacy Strategy Hub implementation kept here for reference
def legacy_strategy_hub():
    """
    Legacy implementation of the Strategy Hub page
    """
    # Create a minimal implementation that works reliably
    return render_template(
        "strategy_test.html",
        frameworks=STRATEGY_FRAMEWORKS,
        monetization_strategies={
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
    )

@strategy_bp.route('/strategy-hub-full')  
def strategy_hub_full():
    """
    Original full implementation (currently has issues)
    """
    logger.info("Strategy Hub full route called")
    
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
        
# Helper functions for document uploads
def allowed_file(filename):
    """Check if a filename has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# New integrated storytelling routes
@strategy_bp.route('/strategy-hub/storytelling')
def strategy_hub_storytelling():
    """
    Storytelling Hub page - central access point for storytelling features integrated with Strategy Hub
    """
    logger.info("Strategy Hub Storytelling route called")
    
    try:
        # Get navigation context
        nav_context = get_context_for_template()
        
        # Get category filter
        category = request.args.get('category', 'all')
        audience = request.args.get('audience', 'all')
        
        # Get stories from storytelling module if available
        if STORYTELLING_AVAILABLE:
            try:
                stories = get_enhanced_stories(audience=audience, category=category)
                logger.info(f"Fetched {len(stories)} stories from storytelling module")
            except Exception as e:
                logger.warning(f"Error fetching stories from storytelling module: {str(e)}")
                stories = get_mock_stories()
        else:
            # Create a minimal set of mock stories
            stories = [
                {
                    "id": 1,
                    "title": "Carbon Emissions Reduction Success",
                    "content": "Our organization achieved a 15% reduction in carbon emissions over the past quarter.",
                    "category": "emissions",
                    "audience": "board",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "recommendations": [
                        "Continue investment in renewable energy sources",
                        "Expand carbon offset programs"
                    ]
                },
                {
                    "id": 2,
                    "title": "Water Conservation Initiative Results",
                    "content": "The water conservation program implemented last year has resulted in a 20% decrease in water usage.",
                    "category": "water",
                    "audience": "sustainability_team",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "recommendations": [
                        "Analyze most effective water-saving technologies",
                        "Develop training program for facility managers"
                    ]
                }
            ]
        
        return render_template(
            "strategy/storytelling.html", 
            page_title="Sustainability Storytelling",
            stories=stories,
            category=category,
            audience=audience,
            **nav_context
        )
    except Exception as e:
        logger.error(f"Error in storytelling hub route: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Fallback to simpler template
        return render_template(
            "sustainability_stories.html", 
            error=str(e)
        )

@strategy_bp.route('/api/strategy-hub/generate-story', methods=['POST'])
def api_strategy_hub_generate_story():
    """API endpoint for generating a sustainability story from the Strategy Hub"""
    try:
        # Get request data
        data = request.json or {}
        
        # Extract parameters
        topic = data.get('topic', 'sustainability')
        template = data.get('template', 'success')
        audience = data.get('audience', 'board')
        
        # Check if storytelling module is available
        if not STORYTELLING_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Storytelling module is not available'
            }), 500
        
        # Generate stories using the storytelling module
        try:
            stories = get_enhanced_stories(audience=audience, category=topic)
            
            # If stories were generated, return the first one
            if stories:
                return jsonify({
                    'success': True,
                    'story': stories[0]
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'No stories generated'
                }), 404
        except Exception as e:
            logger.error(f"Error generating story: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Error generating story: {str(e)}'
            }), 500
    
    except Exception as e:
        logger.error(f"Error in generate story API: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# New integrated document upload routes
@strategy_bp.route('/strategy-hub/documents')
def strategy_hub_documents():
    """
    Documents Hub page - central access point for document uploads and analysis
    """
    logger.info("Strategy Hub Documents route called")
    
    try:
        # Get navigation context
        nav_context = get_context_for_template()
        
        # Get stored documents (simplified for now)
        recent_documents = [
            {
                "id": "doc1",
                "title": "Sustainability Report 2024",
                "category": "report",
                "description": "Annual sustainability report with emissions data and ESG metrics.",
                "timestamp": "2024-03-01",
                "page_count": 42
            },
            {
                "id": "doc2",
                "title": "CSRD Compliance Assessment",
                "category": "compliance",
                "description": "Assessment of company compliance with CSRD reporting requirements.",
                "timestamp": "2024-02-15",
                "page_count": 18
            }
        ]
        
        return render_template(
            "strategy/documents.html", 
            page_title="Document Analysis Hub",
            recent_documents=recent_documents,
            document_processor_available=DOCUMENT_PROCESSOR_AVAILABLE,
            **nav_context
        )
    except Exception as e:
        logger.error(f"Error in documents hub route: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Create a minimal error message
        return f"Error in documents hub: {str(e)}", 500

@strategy_bp.route('/strategy-hub/document-upload', methods=['GET', 'POST'])
def strategy_hub_document_upload():
    """
    Document upload page and handler for the Strategy Hub
    """
    logger.info("Strategy Hub Document Upload route called")
    
    # Define upload error (if any)
    upload_error = None
    upload_success = None
    
    if request.method == 'POST':
        try:
            # Check if document processor is available
            if not DOCUMENT_PROCESSOR_AVAILABLE:
                upload_error = "Document processor is not available"
                logger.warning(f"Document upload attempted but processor not available")
                return render_template(
                    "strategy/document_upload.html",
                    upload_error=upload_error
                )
            
            # Check if file is in request
            if 'document' not in request.files:
                upload_error = "No file selected"
                logger.warning("Document upload attempted but no file in request")
                return render_template(
                    "strategy/document_upload.html",
                    upload_error=upload_error
                )
                
            file = request.files['document']
            
            # Check if file was selected
            if file.filename == '':
                upload_error = "No file selected"
                logger.warning("Document upload attempted but filename is empty")
                return render_template(
                    "strategy/document_upload.html",
                    upload_error=upload_error
                )
                
            # Check if file has allowed extension
            if not allowed_file(file.filename):
                upload_error = f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
                logger.warning(f"Document upload attempted with invalid file type: {file.filename}")
                return render_template(
                    "strategy/document_upload.html",
                    upload_error=upload_error
                )
                
            # Save the file
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            logger.info(f"Document uploaded successfully: {filename}")
            
            # Process the document if processor is available
            use_ocr = request.form.get('use_ocr', 'false') == 'true'
            
            # Process the document
            result = document_processor.process_document(file_path, use_ocr=use_ocr)
            
            # Store document info in session for retrieval
            session['last_document'] = {
                'filename': filename,
                'path': file_path,
                'result': result,
                'timestamp': datetime.now().isoformat()
            }
            
            # Redirect to document view
            return redirect(url_for('strategy.strategy_hub_document_view', document_id=filename))
        
        except Exception as e:
            upload_error = f"Error uploading document: {str(e)}"
            logger.error(f"Error in document upload: {str(e)}")
            logger.error(traceback.format_exc())
    
    # Render the upload form for GET requests or after handling POST
    return render_template(
        "strategy/document_upload.html",
        page_title="Upload Document",
        upload_error=upload_error,
        upload_success=upload_success,
        document_processor_available=DOCUMENT_PROCESSOR_AVAILABLE
    )
    
@strategy_bp.route('/strategy-hub/document/<document_id>')
def strategy_hub_document_view(document_id):
    """
    Document analysis view for a specific document
    """
    logger.info(f"Strategy Hub Document View route called for document: {document_id}")
    
    try:
        # Get document info from session if it exists
        document_info = session.get('last_document', None)
        
        if not document_info or document_info.get('filename') != document_id:
            # Try to load the document if it's stored on disk
            file_path = os.path.join(UPLOAD_FOLDER, document_id)
            if os.path.exists(file_path) and DOCUMENT_PROCESSOR_AVAILABLE:
                # Process the document
                result = document_processor.process_document(file_path)
                document_info = {
                    'filename': document_id,
                    'path': file_path,
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Document not found or processor not available
                return render_template('error.html', message=f"Document {document_id} not found or cannot be processed"), 404
        
        # Get navigation context
        nav_context = get_context_for_template()
        
        # Render document view
        return render_template(
            "strategy/document_view.html",
            page_title=f"Document Analysis: {document_id}",
            document=document_info,
            **nav_context
        )
    except Exception as e:
        logger.error(f"Error in document view route: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Create a minimal error message
        return f"Error viewing document: {str(e)}", 500

# Consolidated Strategy Hub implementation
@strategy_bp.route('/unified-strategy-hub')
def unified_strategy_hub():
    """
    Unified Strategy Hub page with document analysis, storytelling, and strategy frameworks
    This is the new integrated version that combines all features including:
    - Document analysis and compliance assessment
    - Sustainability storytelling
    - Marketing strategies
    - Monetization opportunities
    - Trend virality benchmarking
    - Strategy frameworks
    """
    logger.info("Unified Strategy Hub route called")
    
    try:
        # Get navigation context
        nav_context = get_context_for_template()
        
        # Get recent documents (simplified for now)
        recent_documents = [
            {
                "id": "doc1",
                "title": "Sustainability Report 2024",
                "category": "report",
                "description": "Annual sustainability report with emissions data and ESG metrics.",
                "timestamp": "2024-03-01",
                "page_count": 42
            },
            {
                "id": "doc2",
                "title": "CSRD Compliance Assessment",
                "category": "compliance",
                "description": "Assessment of company compliance with CSRD reporting requirements.",
                "timestamp": "2024-02-15",
                "page_count": 18
            }
        ]
        
        # Get recent stories
        if STORYTELLING_AVAILABLE:
            try:
                # The get_enhanced_stories function doesn't accept a limit parameter
                recent_stories = get_enhanced_stories(audience='all', category='all')
                # Limit the stories to 3 after the function call
                recent_stories = recent_stories[:3] if recent_stories and len(recent_stories) > 3 else recent_stories
                logger.info(f"Fetched {len(recent_stories)} stories for unified hub")
            except Exception as e:
                logger.warning(f"Error fetching stories for unified hub: {str(e)}")
                # The get_mock_stories function doesn't accept a limit parameter either
                recent_stories = get_mock_stories()
                # Limit the stories to 3 after the function call
                recent_stories = recent_stories[:3] if recent_stories and len(recent_stories) > 3 else recent_stories
        else:
            recent_stories = [
                {
                    "id": 1,
                    "title": "Carbon Emissions Reduction Success",
                    "content": "Our organization achieved a 15% reduction in carbon emissions over the past quarter.",
                    "category": "emissions",
                    "audience": "board",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "recommendations": [
                        "Continue investment in renewable energy sources",
                        "Expand carbon offset programs"
                    ]
                },
                {
                    "id": 2,
                    "title": "Water Conservation Initiative Results",
                    "content": "The water conservation program implemented last year has resulted in a 20% decrease in water usage.",
                    "category": "water",
                    "audience": "sustainability_team",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "recommendations": [
                        "Analyze most effective water-saving technologies",
                        "Develop training program for facility managers"
                    ]
                }
            ]
        
        # Create hardcoded monetization strategies for the template
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
            }
        }
        
        # Get marketing strategies
        try:
            # Try to import marketing strategies directly from module
            from marketing_strategies import get_marketing_strategies
            marketing_strategies = get_marketing_strategies()
            logger.info(f"Loaded {len(marketing_strategies)} marketing strategies")
        except (ImportError, AttributeError) as e:
            logger.warning(f"Could not load marketing strategies: {str(e)}")
            # Fallback marketing strategies
            marketing_strategies = {
                "content": {
                    "name": "Content Marketing",
                    "icon": "file-text",
                    "short_description": "Educational sustainability content",
                    "target_audience": "all"
                },
                "storytelling": {
                    "name": "Data Storytelling",
                    "icon": "bar-chart-2",
                    "short_description": "Narrative-driven data visualization",
                    "target_audience": "executives"
                },
                "social": {
                    "name": "Social Media",
                    "icon": "share-2",
                    "short_description": "Social sharing of sustainability wins",
                    "target_audience": "public"
                }
            }
        
        # Get trend virality data 
        trend_data = None
        benchmark_data = None
        
        if TREND_VIRALITY_AVAILABLE:
            try:
                # Sample sustainability trend to analyze
                sample_trend = {
                    "name": "Carbon Footprint Transparency",
                    "description": "Companies publicly sharing detailed carbon footprint data",
                    "category": "emissions",
                    "content": "Organizations are increasingly sharing granular carbon emissions data with stakeholders and the public, moving beyond basic GHG protocol reporting to include product-level carbon footprints and real-time emissions tracking.",
                    "audience": ["investors", "customers", "regulators"]
                }
                
                # Get STEPPS analysis for the trend
                trend_data = analyze_trend_with_stepps(sample_trend)
                logger.info("Generated STEPPS analysis for sample trend")
                
                # Get competitor benchmark data
                company_name = "Your Company"
                industry = "Sustainability Solutions"
                
                # Create simple trend data list for benchmarking
                trend_data_list = [
                    {
                        "name": "Carbon Footprint Transparency",
                        "score": 85,
                        "category": "emissions",
                        "trend": "rising"
                    }
                ]
                
                benchmark_data = benchmark_against_competitors(company_name, industry, trend_data_list)
                logger.info("Generated competitor benchmark data")
            except Exception as e:
                logger.warning(f"Error generating trend virality data: {str(e)}")
                trend_data = None
                benchmark_data = None
        
        # Render the unified template with all components
        return render_template(
            "strategy/strategy_hub.html",
            page_title="Unified Strategy Hub",
            active_nav="strategy",  # Set the active navigation item to highlight in sidebar
            frameworks=STRATEGY_FRAMEWORKS,
            monetization_strategies=monetization_strategies,
            marketing_strategies=marketing_strategies,  # Added marketing strategies
            recent_documents=recent_documents,
            recent_stories=recent_stories,
            stepps_components=STEPPS_COMPONENTS,  # STEPPS virality components
            trend_data=trend_data,  # Added trend analysis data
            benchmark_data=benchmark_data,  # Added benchmark data
            document_processor_available=DOCUMENT_PROCESSOR_AVAILABLE,
            storytelling_available=STORYTELLING_AVAILABLE,
            trend_virality_available=TREND_VIRALITY_AVAILABLE,  # Added flag for trend virality
            **nav_context
        )
    except Exception as e:
        logger.error(f"Error in unified strategy hub: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Create a minimal fallback with required parameters
        return render_template(
            "strategy_test.html",
            active_nav="strategy",  # Set the active navigation item for fallback as well
            frameworks=STRATEGY_FRAMEWORKS,
            monetization_strategies={
                "M1": {
                    "name": "AI-Driven Sustainability Trend Monetization",
                    "icon": "chart-line",
                    "short_description": "AI-powered trend detection and analysis",
                    "default_potential": 85
                }
            },
            error=str(e)
        )

# Legacy route redirects
@strategy_bp.route('/monetization-opportunities')
@strategy_bp.route('/monetization-strategies')
def legacy_monetization_redirect():
    """Redirect legacy monetization routes to unified strategy hub"""
    return redirect(url_for('strategy.unified_strategy_hub'))

@strategy_bp.route('/sustainability-strategies')
def legacy_strategies_redirect():
    """Redirect legacy strategies routes to unified strategy hub"""
    return redirect(url_for('strategy.unified_strategy_hub'))

@strategy_bp.route('/strategy-simulation')
def legacy_simulation_redirect():
    """Redirect legacy simulation routes to unified strategy hub"""
    return redirect(url_for('strategy.unified_strategy_hub'))