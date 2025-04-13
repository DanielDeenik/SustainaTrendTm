"""
Monetization Strategies Module for SustainaTrend™

This module provides functionality for identifying monetization opportunities
and revenue strategies for sustainability intelligence.

Key features:
1. Monetization framework structure and methodologies
2. Strategy scoring and business model analysis 
3. Gap analysis for revenue optimization
4. Visual monetization reporting
"""
import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
import os
from datetime import datetime
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Monetization Strategies Framework Structure
MONETIZATION_FRAMEWORK = {
    "M1": {
        "name": "AI-Driven Sustainability Trend Monetization",
        "description": "Monetization strategies based on AI-powered trend detection and analysis",
        "key_metrics": [
            "Trend prediction accuracy",
            "AI model performance",
            "API call volume",
            "Subscription conversion rate",
            "Customer retention rate",
            "Revenue per API call",
            "New insight generation"
        ],
        "key_terms": [
            "trend analysis", "predictive AI", "subscription model", "API monetization", 
            "sentiment analysis", "virality metrics", "trend forecasting", "social listening"
        ]
    },
    "M2": {
        "name": "Sentiment-Driven Pre-Suasion & Behavioral Shifts",
        "description": "Monetization through behavioral analytics and pre-suasion techniques",
        "key_metrics": [
            "Sentiment prediction accuracy",
            "Behavioral model conversion",
            "Pre-suasion effectiveness",
            "Persuasion ROI metrics",
            "Message optimization rates",
            "Customer behavior shifts"
        ],
        "key_terms": [
            "behavioral analytics", "sentiment analysis", "pre-suasion", "persuasion metrics",
            "nudging techniques", "consumer psychology", "behavioral economics", "message optimization"
        ]
    },
    "M3": {
        "name": "Carbon Credit & Green Financial Instruments",
        "description": "Monetization through carbon markets and sustainable financial products",
        "key_metrics": [
            "Carbon credit volume",
            "Carbon credit pricing",
            "Token transaction volume",
            "Financial product performance",
            "Verification accuracy",
            "Marketplace liquidity",
            "Data licensing revenue"
        ],
        "key_terms": [
            "carbon credits", "carbon market", "sustainable finance", "green bonds", 
            "tokenization", "blockchain verification", "carbon accounting", "emissions trading"
        ]
    },
    "M4": {
        "name": "AI-Powered Sustainability-Linked Consumer Products",
        "description": "Monetization through consumer-facing sustainability applications",
        "key_metrics": [
            "Affiliate conversion rate",
            "Marketplace transaction volume",
            "Premium listing revenue",
            "Consumer app engagement",
            "Brand partnership revenue",
            "Loyalty program adoption",
            "User acquisition cost"
        ],
        "key_terms": [
            "consumer marketplace", "affiliate revenue", "premium listings", "sustainability scoring",
            "green consumer apps", "loyalty programs", "brand partnerships", "sustainable e-commerce"
        ]
    },
    "M5": {
        "name": "Sustainability Intelligence Subscriptions",
        "description": "Subscription-based monetization for sustainability intelligence",
        "key_metrics": [
            "Monthly recurring revenue (MRR)",
            "Annual recurring revenue (ARR)",
            "Subscription tier distribution",
            "User retention rate",
            "Account expansion revenue",
            "Feature usage metrics",
            "Churn rate"
        ],
        "key_terms": [
            "subscription model", "tiered pricing", "enterprise licensing", "SaaS metrics",
            "recurring revenue", "retention strategies", "account expansion", "value metrics"
        ]
    },
    "M6": {
        "name": "Strategic Consulting & Professional Services",
        "description": "Monetization through high-value consulting and professional services",
        "key_metrics": [
            "Consulting engagement value",
            "Billable hours utilization",
            "Client retention rate",
            "Services revenue growth",
            "Project profitability",
            "Client satisfaction score",
            "Cross-selling rate"
        ],
        "key_terms": [
            "consulting services", "professional services", "strategic advisory", "implementation services",
            "value-based pricing", "retainer models", "outcome-based fees", "client success metrics"
        ]
    },
    "M7": {
        "name": "Data Licensing & Sustainability APIs",
        "description": "Monetization through data licensing and API-based services",
        "key_metrics": [
            "Data license revenue",
            "API transaction volume",
            "API revenue per call",
            "Data partner relationships",
            "Integration adoption",
            "Developer community size",
            "Data update frequency"
        ],
        "key_terms": [
            "data licensing", "API monetization", "data partnerships", "developer ecosystem",
            "API pricing models", "data syndication", "sustainability dataset", "integration revenue"
        ]
    },
    "M8": {
        "name": "Educational Content & Certification Programs",
        "description": "Monetization through sustainability education and certification",
        "key_metrics": [
            "Course enrollment revenue",
            "Certification completion rate",
            "Learning materials sales",
            "Workshop attendance",
            "Educational content views",
            "Certification renewal rate",
            "Education partnership revenue"
        ],
        "key_terms": [
            "sustainability education", "certification programs", "online courses", "workshops",
            "educational content", "learning platform", "professional development", "credentials"
        ]
    }
}

def analyze_monetization_opportunities(document_text: str) -> Dict[str, Any]:
    """
    Analyze a business plan or document for monetization opportunities
    
    Args:
        document_text: Text content of the business plan or document
        
    Returns:
        Dictionary with monetization strategy scores and analysis
    """
    if not document_text:
        logger.warning("Empty document provided for monetization analysis")
        return {
            "overall_score": 0,
            "categories": {},
            "coverage": 0,
            "opportunity_areas": ["All monetization categories"],
            "timestamp": datetime.now().isoformat()
        }
    
    text_lower = document_text.lower()
    results = {}
    total_score = 0
    total_categories = len(MONETIZATION_FRAMEWORK)
    categories_with_potential = 0
    
    # Analyze each monetization category
    for category_id, category_data in MONETIZATION_FRAMEWORK.items():
        category_results = _analyze_monetization_category(text_lower, category_id, category_data)
        results[category_id] = category_results
        total_score += category_results["score"]
        
        if category_results["score"] > 0.2:  # Consider categories with at least minimal potential
            categories_with_potential += 1
    
    # Calculate overall metrics
    if total_categories > 0:
        average_score = total_score / total_categories
        coverage_percentage = (categories_with_potential / total_categories) * 100
    else:
        average_score = 0
        coverage_percentage = 0
    
    # Identify opportunity areas (categories with potential)
    opportunity_areas = [
        f"{category_id}: {MONETIZATION_FRAMEWORK[category_id]['name']}" 
        for category_id, category_data in results.items() 
        if category_data["score"] >= 0.5  # Focus on high-potential opportunities
    ]
    
    return {
        "overall_score": round(average_score, 2),
        "categories": results,
        "coverage": round(coverage_percentage, 1),
        "opportunity_areas": opportunity_areas,
        "timestamp": datetime.now().isoformat()
    }

def _analyze_monetization_category(text: str, category_id: str, category_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze document text against a specific monetization category
    
    Args:
        text: Document text (lowercase)
        category_id: Monetization category ID (e.g., "M1", "M2")
        category_data: Category definition data
        
    Returns:
        Category analysis results
    """
    key_terms = category_data["key_terms"]
    key_metrics = category_data["key_metrics"]
    
    # Count term occurrences
    term_matches = {}
    for term in key_terms:
        count = text.count(term)
        if count > 0:
            term_matches[term] = count
    
    # Check for metrics coverage
    metrics_found = []
    for metric in key_metrics:
        if any(term.lower() in text for term in metric.split()):
            metrics_found.append(metric)
    
    # Calculate coverage scores
    term_coverage = len(term_matches) / len(key_terms) if key_terms else 0
    metric_coverage = len(metrics_found) / len(key_metrics) if key_metrics else 0
    
    # Weight the score (60% terms, 40% metrics)
    score = (term_coverage * 0.6) + (metric_coverage * 0.4)
    
    # Map score to potential level
    potential_level = _map_score_to_potential(score)
    
    return {
        "score": round(score, 2),
        "potential_level": potential_level,
        "term_coverage": round(term_coverage * 100, 1),
        "metric_coverage": round(metric_coverage * 100, 1),
        "terms_found": list(term_matches.keys()),
        "metrics_found": metrics_found,
        "opportunity_metrics": [m for m in key_metrics if m not in metrics_found]
    }

def _map_score_to_potential(score: float) -> str:
    """
    Map numerical score to monetization potential level description
    
    Args:
        score: Numerical potential score (0-1)
        
    Returns:
        Potential level description
    """
    if score >= 0.8:
        return "Exceptional"
    elif score >= 0.6:
        return "High"
    elif score >= 0.4:
        return "Moderate"
    elif score >= 0.2:
        return "Limited"
    else:
        return "Minimal"

def generate_monetization_opportunities(document_text: str) -> Dict[str, Any]:
    """
    Generate monetization opportunities analysis based on business plan or document
    
    Args:
        document_text: Text content of the business plan or document
        
    Returns:
        Dictionary with monetization opportunities and recommendations
    """
    # Analyze document for monetization opportunities
    analysis_results = analyze_monetization_opportunities(document_text)
    categories = analysis_results["categories"]
    
    # Identify the top 3 most promising opportunities
    sorted_categories = sorted(
        [(cat_id, data) for cat_id, data in categories.items()],
        key=lambda x: x[1]["score"],
        reverse=True  # Sort by highest score first for best opportunities
    )
    
    # Get the 3 highest scoring categories
    top_opportunities = sorted_categories[:3] if len(sorted_categories) >= 3 else sorted_categories
    
    # Generate recommendations for each opportunity
    recommendations = []
    for cat_id, data in top_opportunities:
        category_name = MONETIZATION_FRAMEWORK[cat_id]["name"]
        key_metrics = data["metrics_found"][:3]  # Top 3 key metrics
        
        # Generate recommendation
        recommendation = {
            "category": f"{cat_id}: {category_name}",
            "potential_score": data["score"],
            "potential_level": data["potential_level"],
            "key_metrics": key_metrics,
            "implementation_steps": [
                f"Implement {metric} tracking and optimization" for metric in key_metrics
            ],
            "opportunity_description": MONETIZATION_FRAMEWORK[cat_id]["description"]
        }
        recommendations.append(recommendation)
    
    return {
        "overall_potential": analysis_results["overall_score"],
        "coverage_percentage": analysis_results["coverage"],
        "top_opportunities": recommendations,
        "timestamp": datetime.now().isoformat()
    }

# Export monetization strategies for UI display
# Create a direct dictionary constant with strategies for reliability
PRELOADED_MONETIZATION_STRATEGIES = {
    "M1": {
        "name": "AI-Driven Sustainability Trend Monetization",
        "description": "Monetization strategies based on AI-powered trend detection and analysis",
        "icon": "chart-line",
        "short_description": "Monetization strategies based on AI-powered trend detection and analysis...",
        "default_potential": 85
    },
    "M2": {
        "name": "Consulting Services Model",
        "description": "Advisory and implementation services for sustainability reporting and improvements",
        "icon": "handshake",
        "short_description": "Advisory and implementation services for sustainability reporting and improvements...",
        "default_potential": 65
    },
    "M3": {
        "name": "SaaS Subscription Platform",
        "description": "Cloud-based sustainability intelligence platform with tiered subscription options",
        "icon": "cloud",
        "short_description": "Cloud-based sustainability intelligence platform with tiered subscription options...",
        "default_potential": 85
    },
    "M4": {
        "name": "Sustainability Data Marketplace",
        "description": "Platform for buying and selling anonymized sustainability datasets and metrics",
        "icon": "database",
        "short_description": "Platform for buying and selling anonymized sustainability datasets and metrics...",
        "default_potential": 65
    },
    "M5": {
        "name": "Certification and Verification",
        "description": "Revenue from verifying sustainability claims and certifying compliance",
        "icon": "certificate",
        "short_description": "Revenue from verifying sustainability claims and certifying compliance...",
        "default_potential": 45
    },
    "M6": {
        "name": "AI-Generated Reporting as a Service",
        "description": "Automated generation of sustainability reports and regulatory filings",
        "icon": "file-chart-line",
        "short_description": "Automated generation of sustainability reports and regulatory filings...",
        "default_potential": 85
    }
}

def get_monetization_strategies() -> Dict[str, Dict[str, Any]]:
    """
    Get monetization strategies for UI display
    
    Returns:
        Dictionary with monetization strategies information and default potential values
    """
    # Create a NEW dictionary with explicit key-value pairs to avoid method references
    # This ensures we always return a concrete dictionary, not a callable method
    strategies = {}
    
    # First try to use the preloaded strategies for reliability
    if PRELOADED_MONETIZATION_STRATEGIES:
        preloaded = PRELOADED_MONETIZATION_STRATEGIES
        
        # Manually copy each key-value pair to ensure it's a regular dictionary
        if hasattr(preloaded, 'items') and callable(preloaded.items):
            # If it's a dictionary with items() method
            for key, value in preloaded.items():
                strategies[key] = value
            return strategies
        elif isinstance(preloaded, dict):
            # If it's already a dictionary but items might be a method issue
            for key in preloaded:
                strategies[key] = preloaded[key] 
            return strategies
                
    # This is now a fallback if the preloaded strategies are somehow empty or not a proper dict
    strategies = {}
    
    for strategy_id, strategy_data in MONETIZATION_FRAMEWORK.items():
        strategy = {
            "name": strategy_data["name"],
            "description": strategy_data["description"],
            "icon": strategy_data.get("icon", "chart-line"),
            "short_description": strategy_data.get("description", "")[:100] + "..."
        }
        
        # Add default potential value based on strategy ID
        if strategy_id in ['M1', 'M3', 'M6']:
            strategy['default_potential'] = 85  # High potential
        elif strategy_id in ['M2', 'M4', 'M7']:
            strategy['default_potential'] = 65  # Medium potential
        else:
            strategy['default_potential'] = 45  # Lower potential
            
        strategies[strategy_id] = strategy
    
    return strategies

def configure_routes(app):
    """
    Configure Flask routes for Monetization Strategies
    
    This function is kept for backward compatibility but no longer registers routes directly.
    All routes are now registered via the monetization blueprint in routes/monetization.py
    
    Args:
        app: Flask application
    """
    # Routes have been moved to routes/monetization.py
    pass

def generate_strategy_consulting_insights(document_text: str, industry: str = "General") -> Dict[str, Any]:
    """
    Generate integrated strategy consulting insights based on monetization analysis
    
    Args:
        document_text: Text content of the business plan or document
        industry: Industry for context
        
    Returns:
        Dictionary with strategic consulting analysis and recommendations
    """
    # Analyze monetization opportunities
    monetization_analysis = analyze_monetization_opportunities(document_text)
    
    # Identify top monetization categories
    top_categories = sorted(
        [(cat_id, data) for cat_id, data in monetization_analysis.get("categories", {}).items()],
        key=lambda x: x[1]["score"],
        reverse=True
    )[:3]
    
    # Map each monetization category to relevant strategic frameworks
    framework_recommendations = []
    for cat_id, data in top_categories:
        category_name = MONETIZATION_FRAMEWORK[cat_id]["name"]
        
        # Determine the best strategic frameworks for this monetization category
        recommended_frameworks = []
        
        if cat_id == "M1":  # AI-Driven Sustainability Trend Monetization
            recommended_frameworks = ["blue_ocean", "mckinsey"]
        elif cat_id == "M2":  # Sentiment-Driven Pre-Suasion & Behavioral Shifts
            recommended_frameworks = ["swot", "strategy_pyramid"]
        elif cat_id == "M3":  # Carbon Credit & Green Financial Instruments
            recommended_frameworks = ["porters", "bcg"]
        elif cat_id == "M4":  # AI-Powered Sustainability-Linked Consumer Products
            recommended_frameworks = ["blue_ocean", "mckinsey"]
        elif cat_id == "M5":  # Sustainability Intelligence Subscriptions
            recommended_frameworks = ["strategy_pyramid", "bcg"]
        elif cat_id == "M6":  # Strategic Consulting & Professional Services
            recommended_frameworks = ["swot", "mckinsey"]
        elif cat_id == "M7":  # Data Licensing & Sustainability APIs
            recommended_frameworks = ["porters", "bcg"]
        elif cat_id == "M8":  # Educational Content & Certification Programs
            recommended_frameworks = ["swot", "strategy_pyramid"]
        else:
            recommended_frameworks = ["swot", "porters"]  # Default frameworks
        
        # For each monetization category, recommend strategic frameworks
        for framework_id in recommended_frameworks:
            framework_recommendation = {
                "monetization_category": {
                    "id": cat_id,
                    "name": category_name,
                    "score": data["score"],
                    "potential_level": data["potential_level"],
                },
                "strategic_framework": {
                    "id": framework_id,
                    "name": STRATEGY_FRAMEWORKS.get(framework_id, {}).get("name", "Unknown Framework"),
                    "description": STRATEGY_FRAMEWORKS.get(framework_id, {}).get("description", ""),
                },
                "implementation_considerations": [
                    f"Align {category_name} with competitive positioning strategy",
                    f"Integrate {STRATEGY_FRAMEWORKS.get(framework_id, {}).get('name', 'strategic')} analysis into monetization roadmap",
                    f"Develop metrics to track success of integrated approach"
                ],
                "strategic_advantage": "Competitive differentiation through integrated sustainability strategy and monetization"
            }
            framework_recommendations.append(framework_recommendation)
    
    # Generate comprehensive strategic recommendations
    strategic_recommendations = []
    for i, recommendation in enumerate(framework_recommendations[:5]):  # Limit to top 5
        strategic_recommendations.append({
            "title": f"Strategy {i+1}: {recommendation['monetization_category']['name']} with {recommendation['strategic_framework']['name']}",
            "description": f"Implement {recommendation['monetization_category']['name']} through {recommendation['strategic_framework']['name']} framework",
            "potential_level": recommendation['monetization_category']['potential_level'],
            "implementation_steps": recommendation['implementation_considerations'],
            "strategic_advantage": recommendation['strategic_advantage']
        })
    
    return {
        "overall_potential": monetization_analysis.get("overall_score", 0),
        "strategic_recommendations": strategic_recommendations,
        "integrated_approach": "Combined Monetization & Strategic Framework Analysis",
        "industry_context": industry,
        "timestamp": datetime.now().isoformat()
    }

# Define mapping to strategic frameworks - imported from strategy_simulation.py
STRATEGY_FRAMEWORKS = {
    "porters": {
        "name": "Porter's Five Forces",
        "description": "Assess competitive sustainability positioning by analyzing supplier power, buyer power, competitive rivalry, threat of substitution, and threat of new entry.",
        "dimensions": ["supplier_power", "buyer_power", "competitive_rivalry", "threat_of_substitution", "threat_of_new_entry"],
        "icon": "chart-bar",
    },
    "swot": {
        "name": "SWOT Analysis",
        "description": "Evaluate internal strengths and weaknesses alongside external opportunities and threats for sustainability initiatives.",
        "dimensions": ["strengths", "weaknesses", "opportunities", "threats"],
        "icon": "grid-2x2",
    },
    "bcg": {
        "name": "BCG Growth-Share Matrix",
        "description": "Prioritize green investments and assets based on market growth rate and relative market share.",
        "dimensions": ["market_growth", "market_share"],
        "icon": "pie-chart",
    },
    "mckinsey": {
        "name": "McKinsey 9-Box Matrix",
        "description": "Rank real estate assets based on market attractiveness and competitive position for sustainability ROI.",
        "dimensions": ["market_attractiveness", "competitive_position"],
        "icon": "layout-grid",
    },
    "strategy_pyramid": {
        "name": "Strategy Pyramid",
        "description": "Define sustainability mission, objectives, strategies, and tactical plans in a hierarchical framework.",
        "dimensions": ["mission", "objectives", "strategies", "tactics"],
        "icon": "pyramid",
    },
    "blue_ocean": {
        "name": "Blue Ocean Strategy",
        "description": "Create uncontested market space by focusing on sustainable innovation and differentiation.",
        "dimensions": ["eliminate", "reduce", "raise", "create"],
        "icon": "waves",
    }
}

def generate_integrated_strategic_plan(company_name: str, industry: str, document_text: str = None) -> Dict[str, Any]:
    """
    Generate an integrated strategic plan combining monetization strategies with consulting frameworks
    
    Args:
        company_name: Name of the company
        industry: Industry sector
        document_text: Optional document text for analysis
        
    Returns:
        Dictionary with comprehensive strategic plan
    """
    try:
        # Import strategy simulation module
        from strategy_simulation import analyze_with_framework, get_frameworks
        
        # Generate monetization analysis
        monetization_analysis = analyze_monetization_opportunities(document_text or f"Strategic plan for {company_name} in {industry} sector")
        
        # Get top monetization categories
        top_categories = sorted(
            [(cat_id, data) for cat_id, data in monetization_analysis.get("categories", {}).items()],
            key=lambda x: x[1]["score"],
            reverse=True
        )[:3]
        
        # Map to suitable strategy frameworks based on monetization score
        strategic_analyses = {}
        
        # Framework selection logic based on monetization categories
        framework_mapping = {
            "M1": "porters",     # AI-Driven Trend Monetization -> Porter's Five Forces
            "M2": "swot",        # Sentiment-Driven Pre-Suasion -> SWOT Analysis
            "M3": "bcg",         # Carbon Credit & Financial -> BCG Matrix
            "M4": "blue_ocean",  # Consumer Products -> Blue Ocean
            "M5": "strategy_pyramid",  # Subscriptions -> Strategy Pyramid
            "M6": "mckinsey",    # Consulting Services -> McKinsey Matrix
            "M7": "porters",     # Data Licensing -> Porter's Five Forces
            "M8": "swot"         # Educational Content -> SWOT
        }
        
        # Generate analyses for top monetization categories
        for cat_id, cat_data in top_categories:
            framework_id = framework_mapping.get(cat_id, "swot")  # Default to SWOT if no mapping
            
            # Create a mock data structure - in a production app, this would use real data
            mock_data = {
                "category": cat_id,
                "score": cat_data["score"],
                "terms_found": cat_data.get("terms_found", []),
                "potential_level": cat_data.get("potential_level", "Moderate")
            }
            
            # Run the framework analysis
            strategic_analysis = analyze_with_framework(
                framework_id=framework_id,
                data=mock_data,
                company_name=company_name,
                industry=industry
            )
            
            strategic_analyses[cat_id] = {
                "framework": framework_id,
                "framework_name": get_frameworks()[framework_id]["name"],
                "analysis": strategic_analysis
            }
        
        # Integration plan summary
        integration_plan = {
            "company_name": company_name,
            "industry": industry,
            "monetization_overview": {
                "overall_score": monetization_analysis.get("overall_score", 0),
                "coverage": monetization_analysis.get("coverage", 0),
                "top_categories": [
                    {
                        "id": cat_id,
                        "name": MONETIZATION_FRAMEWORK[cat_id]["name"],
                        "potential_level": cat_data["potential_level"],
                        "score": cat_data["score"]
                    }
                    for cat_id, cat_data in top_categories
                ]
            },
            "strategic_frameworks": strategic_analyses,
            "implementation_roadmap": {
                "phase_1": {
                    "title": "Analysis & Planning",
                    "duration": "1-2 months",
                    "key_activities": [
                        "Comprehensive data gathering and analysis",
                        "Stakeholder interviews and workshops",
                        "Benchmark against industry leaders",
                        "Detailed opportunity sizing"
                    ]
                },
                "phase_2": {
                    "title": "Strategy Development",
                    "duration": "2-3 months",
                    "key_activities": [
                        "Define monetization strategy and pricing models",
                        "Technology enablement planning",
                        "Organizational alignment assessment",
                        "Financial modelling and ROI analysis"
                    ]
                },
                "phase_3": {
                    "title": "Pilot & Implementation",
                    "duration": "3-6 months",
                    "key_activities": [
                        "Launch focused pilot programs",
                        "Technology build and integration",
                        "Go-to-market strategy execution",
                        "Early adopter onboarding"
                    ]
                },
                "phase_4": {
                    "title": "Scale & Optimization",
                    "duration": "6-12 months",
                    "key_activities": [
                        "Full-scale rollout across markets",
                        "Continuous performance monitoring",
                        "Optimization based on market feedback",
                        "Expansion planning for additional monetization approaches"
                    ]
                }
            },
            "financial_projections": {
                "development_costs": "$250,000 - $500,000",
                "time_to_market": "6-9 months",
                "revenue_potential": f"$2-5M annual recurring revenue potential for {company_name}",
                "time_to_breakeven": "18-24 months",
                "roi_5_year": "250-350%"
            }
        }
        
        return integration_plan
    
    except Exception as e:
        logger.error(f"Error generating integrated strategic plan: {e}")
        return {
            "company_name": company_name,
            "industry": industry,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def register_routes(app):
    """
    Register the Monetization Strategies routes with a Flask application
    
    This function is kept for backward compatibility but no longer registers routes directly.
    All routes are now registered via the monetization blueprint in routes/monetization.py
    
    Args:
        app: Flask application
    """
    configure_routes(app)
    
    # Routes have been moved to routes/monetization.py blueprint
    
    logger.info("Integrated Strategy Consulting routes registered in Monetization module")
    
    # Import additional strategy framework data
    try:
        from strategy_simulation import STRATEGY_FRAMEWORKS
    except ImportError:
        # Define a fallback if strategy_simulation is not available
        STRATEGY_FRAMEWORKS = {
            "porters": {
                "name": "Porter's Five Forces",
                "description": "Analyze competitive forces shaping sustainability positioning",
                "icon": "chart-bar",
            },
            "swot": {
                "name": "SWOT Analysis",
                "description": "Evaluate strengths, weaknesses, opportunities and threats",
                "icon": "grid-2x2",
            }
        }
    
    # All routes have been moved to routes/monetization.py blueprint
    # Keeping this comment here to indicate where routes used to be
    pass