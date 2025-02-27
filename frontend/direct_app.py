#!/usr/bin/env python3
"""
Flask frontend with improved FastAPI connection
for Sustainability Intelligence Dashboard
"""
from flask import Flask, render_template, jsonify, request
import requests
from flask_caching import Cache
import os
import logging
from datetime import datetime, timedelta
import json
import random  # For generating mock AI search and trend data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Starting Sustainability Intelligence Dashboard")

# Initialize Flask
app = Flask(__name__)

# Setup Simple Cache instead of Redis to avoid connection errors
cache = Cache(app, config={
    'CACHE_TYPE': 'SimpleCache'
})

# FastAPI backend URL
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')
logger.info(f"Using FastAPI backend URL: {BACKEND_URL}")

# OmniParser API endpoint
OMNIPARSER_API = "https://api.omniparser.com/parse"

# Utility function to call OmniParser dynamically
def get_ui_suggestions(query: str):
    """Get dynamic UI suggestions from OmniParser API"""
    try:
        logger.info(f"Calling OmniParser API for query: '{query}'")
        response = requests.get(f"{OMNIPARSER_API}?query={query}", timeout=5.0)
        response.raise_for_status()
        suggestions = response.json().get("suggestions", [])
        logger.info(f"Received {len(suggestions)} suggestions from OmniParser")
        return suggestions
    except requests.exceptions.RequestException as e:
        logger.error(f"OmniParser API failed: {str(e)}")
        return {"error": f"OmniParser API failed: {str(e)}"}

# Flask Endpoint: Dynamic Search Suggestions
@app.route("/api/omniparser/suggestions", methods=["GET"])
def omniparser_suggestions_flask():
    """API endpoint for dynamic search suggestions"""
    try:
        query = request.args.get("query", "")
        logger.info(f"Search suggestions requested with query: '{query}'")

        if not query:
            logger.warning("Search suggestions requested with empty query")
            return jsonify({"error": "Query parameter is required"}), 400

        suggestions = get_ui_suggestions(query)
        if isinstance(suggestions, dict) and "error" in suggestions:
            logger.error(f"Error getting suggestions: {suggestions['error']}")
            return jsonify({"error": suggestions["error"]}), 500

        logger.info(f"Returning {len(suggestions)} suggestions for query: '{query}'")
        return jsonify({"suggestions": suggestions})
    except Exception as e:
        logger.error(f"Error in suggestions endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Fetch sustainability metrics from FastAPI backend with improved error handling
@cache.memoize(timeout=300)
def get_sustainability_metrics():
    """Fetch sustainability metrics from FastAPI backend"""
    try:
        logger.info(f"Fetching metrics from FastAPI backend: {BACKEND_URL}/api/metrics")
        response = requests.get(f"{BACKEND_URL}/api/metrics", timeout=10.0)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses

        metrics_data = response.json()
        logger.info(f"Successfully fetched {len(metrics_data)} metrics from API")

        # Log a sample of the metrics data to verify format
        if metrics_data and len(metrics_data) > 0:
            logger.info(f"Sample metric data: {json.dumps(metrics_data[0], indent=2)}")
            logger.info(f"Metrics categories: {set(m['category'] for m in metrics_data)}")
            logger.info(f"Metrics names: {set(m['name'] for m in metrics_data)}")

        return metrics_data

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching metrics from API: {str(e)}")
        logger.info("Falling back to mock data")
        # Fallback to mock data if API fails
        return get_mock_sustainability_metrics()
    except Exception as e:
        logger.error(f"Unexpected error fetching metrics: {str(e)}")
        return get_mock_sustainability_metrics()


# Fallback mock data function (unchanged)
def get_mock_sustainability_metrics():
    """Generate mock sustainability metrics data as fallback"""
    logger.info("Generating mock sustainability metrics data")
    # Generate dates for the past 6 months
    dates = []
    for i in range(6):
        dates.append((datetime.now() - timedelta(days=30 * (5 - i))).isoformat())

    # Carbon emissions data (decreasing trend - good)
    emissions_data = [
        {"id": 1, "name": "Carbon Emissions", "category": "emissions", "value": 45, "unit": "tons CO2e", "timestamp": dates[0]},
        {"id": 2, "name": "Carbon Emissions", "category": "emissions", "value": 42, "unit": "tons CO2e", "timestamp": dates[1]},
        {"id": 3, "name": "Carbon Emissions", "category": "emissions", "value": 38, "unit": "tons CO2e", "timestamp": dates[2]},
        {"id": 4, "name": "Carbon Emissions", "category": "emissions", "value": 35, "unit": "tons CO2e", "timestamp": dates[3]},
        {"id": 5, "name": "Carbon Emissions", "category": "emissions", "value": 32, "unit": "tons CO2e", "timestamp": dates[4]},
        {"id": 6, "name": "Carbon Emissions", "category": "emissions", "value": 30, "unit": "tons CO2e", "timestamp": dates[5]}
    ]

    # Energy consumption data (decreasing trend - good)
    energy_data = [
        {"id": 7, "name": "Energy Consumption", "category": "energy", "value": 1250, "unit": "MWh", "timestamp": dates[0]},
        {"id": 8, "name": "Energy Consumption", "category": "energy", "value": 1200, "unit": "MWh", "timestamp": dates[1]},
        {"id": 9, "name": "Energy Consumption", "category": "energy", "value": 1150, "unit": "MWh", "timestamp": dates[2]},
        {"id": 10, "name": "Energy Consumption", "category": "energy", "value": 1100, "unit": "MWh", "timestamp": dates[3]},
        {"id": 11, "name": "Energy Consumption", "category": "energy", "value": 1075, "unit": "MWh", "timestamp": dates[4]},
        {"id": 12, "name": "Energy Consumption", "category": "energy", "value": 1050, "unit": "MWh", "timestamp": dates[5]}
    ]

    # Water usage data (decreasing trend - good)
    water_data = [
        {"id": 13, "name": "Water Usage", "category": "water", "value": 350, "unit": "kiloliters", "timestamp": dates[0]},
        {"id": 14, "name": "Water Usage", "category": "water", "value": 340, "unit": "kiloliters", "timestamp": dates[1]},
        {"id": 15, "name": "Water Usage", "category": "water", "value": 330, "unit": "kiloliters", "timestamp": dates[2]},
        {"id": 16, "name": "Water Usage", "category": "water", "value": 320, "unit": "kiloliters", "timestamp": dates[3]},
        {"id": 17, "name": "Water Usage", "category": "water", "value": 310, "unit": "kiloliters", "timestamp": dates[4]},
        {"id": 18, "name": "Water Usage", "category": "water", "value": 300, "unit": "kiloliters", "timestamp": dates[5]}
    ]

    # Waste reduction data (increasing trend - good)
    waste_data = [
        {"id": 19, "name": "Waste Recycled", "category": "waste", "value": 65, "unit": "percent", "timestamp": dates[0]},
        {"id": 20, "name": "Waste Recycled", "category": "waste", "value": 68, "unit": "percent", "timestamp": dates[1]},
        {"id": 21, "name": "Waste Recycled", "category": "waste", "value": 72, "unit": "percent", "timestamp": dates[2]},
        {"id": 22, "name": "Waste Recycled", "category": "waste", "value": 76, "unit": "percent", "timestamp": dates[3]},
        {"id": 23, "name": "Waste Recycled", "category": "waste", "value": 80, "unit": "percent", "timestamp": dates[4]},
        {"id": 24, "name": "Waste Recycled", "category": "waste", "value": 82, "unit": "percent", "timestamp": dates[5]}
    ]

    # ESG score data (increasing trend - good)
    esg_data = [
        {"id": 25, "name": "ESG Score", "category": "social", "value": 72, "unit": "score", "timestamp": dates[0]},
        {"id": 26, "name": "ESG Score", "category": "social", "value": 74, "unit": "score", "timestamp": dates[1]},
        {"id": 27, "name": "ESG Score", "category": "social", "value": 76, "unit": "score", "timestamp": dates[2]},
        {"id": 28, "name": "ESG Score", "category": "social", "value": 78, "unit": "score", "timestamp": dates[3]},
        {"id": 29, "name": "ESG Score", "category": "social", "value": 80, "unit": "score", "timestamp": dates[4]},
        {"id": 30, "name": "ESG Score", "category": "social", "value": 82, "unit": "score", "timestamp": dates[5]}
    ]

    # Combine all data
    all_data = emissions_data + energy_data + water_data + waste_data + esg_data

    logger.info(f"Generated mock sustainability metrics with {len(all_data)} records")
    return all_data

# Routes
@app.route('/')
def home():
    """Home page"""
    try:
        logger.info("Home page requested")
        return render_template("index.html")
    except Exception as e:
        logger.error(f"Error in home route: {str(e)}")
        return f"Error loading home page: {str(e)}", 500

@app.route('/dashboard')
def dashboard():
    """Dashboard page using data from FastAPI backend"""
    try:
        logger.info("Dashboard page requested, fetching metrics...")
        metrics = get_sustainability_metrics()
        logger.info(f"Rendering dashboard with {len(metrics)} metrics")
        return render_template("dashboard.html", metrics=metrics)
    except Exception as e:
        logger.error(f"Error in dashboard route: {str(e)}")
        return f"Error loading dashboard: {str(e)}", 500

@app.route('/api/metrics')
def api_metrics():
    """API endpoint for metrics data"""
    try:
        logger.info("API metrics endpoint called")
        metrics = get_sustainability_metrics()
        logger.info(f"Returning {len(metrics)} metrics from API endpoint")
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Error in API metrics endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

# AI Search functionality
def perform_ai_search(query: str, model="rag"):
    """
    Perform AI-powered search on sustainability data
    Using simulated results for now, would connect to OpenAI or other AI service in production
    """
    logger.info(f"Performing AI search for query: '{query}' using model: {model}")

    # In a real implementation, this would call an AI service
    # For now, generate simulated results with chain-of-thought reasoning

    # Step 1: Generate mock search results based on query keywords
    keywords = query.lower().split()
    logger.info(f"Search keywords: {keywords}")

    # Step 2: Mock categories that might match the search
    categories = []
    if any(k in keywords for k in ["carbon", "emission", "emissions", "co2", "greenhouse", "ghg"]):
        categories.append("emissions")
    if any(k in keywords for k in ["energy", "electricity", "power", "consumption", "renewable"]):
        categories.append("energy")
    if any(k in keywords for k in ["water", "hydro", "resource", "usage", "consumption"]):
        categories.append("water")
    if any(k in keywords for k in ["waste", "recycle", "recycling", "circular", "reuse"]):
        categories.append("waste")
    if any(k in keywords for k in ["social", "esg", "governance", "ethical", "responsibility"]):
        categories.append("social")

    # If no specific categories match, include all
    if not categories:
        categories = ["emissions", "energy", "water", "waste", "social"]

    logger.info(f"Matched categories: {categories}")

    # Step 3: Generate mock search results
    results = []
    result_count = min(5, 1 + len(categories))  # Generate between 1-5 results

    titles = {
        "emissions": [
            "Carbon Emissions Reduction Strategies",
            "Scope 3 Emissions Analysis Report",
            "GHG Protocol Implementation Guide",
            "Carbon Neutrality Framework",
            "Emissions Trading and Offset Mechanisms"
        ],
        "energy": [
            "Renewable Energy Transition Plan",
            "Energy Efficiency Best Practices",
            "Green Energy Procurement Strategy",
            "Energy Consumption Optimization Guide",
            "Sustainable Power Generation Analysis"
        ],
        "water": [
            "Water Conservation Implementation Guide",
            "Water Footprint Reduction Strategies",
            "Sustainable Water Management Framework",
            "Water Resource Optimization Toolkit",
            "Watershed Protection and Management Plan"
        ],
        "waste": [
            "Zero Waste Management Strategy",
            "Circular Economy Implementation Guide",
            "Waste Reduction and Recycling Program",
            "Materials Recovery and Reuse Framework",
            "Sustainable Packaging Initiatives"
        ],
        "social": [
            "ESG Reporting Standards Guide",
            "Corporate Social Responsibility Framework",
            "Stakeholder Engagement Best Practices",
            "Diversity, Equity, and Inclusion Metrics",
            "Sustainable Supply Chain Management"
        ]
    }

    for i in range(result_count):
        category = random.choice(categories)
        title = random.choice(titles[category])

        # Generate a snippet with highlighted search terms
        snippet_template = "This comprehensive guide provides {keyword1} strategies for {keyword2} within your organization's sustainability program. Key areas include {keyword3} and implementation of {keyword4} with focus on {keyword5}."
        keyword_options = {
            "emissions": ["emissions reduction", "carbon offsetting", "GHG inventory", "climate action", "science-based targets"],
            "energy": ["renewable energy", "energy efficiency", "clean power", "sustainable energy", "carbon-free energy"],
            "water": ["water conservation", "water footprint", "resource optimization", "water quality", "efficiency measures"],
            "waste": ["waste reduction", "circular economy", "recycling programs", "material recovery", "zero waste"],
            "social": ["ESG metrics", "social impact", "governance standards", "ethical practices", "stakeholder engagement"]
        }

        keywords = keyword_options[category]
        snippet = snippet_template.format(
            keyword1=random.choice(keywords),
            keyword2=random.choice(keywords),
            keyword3=random.choice(keywords),
            keyword4=random.choice(keywords),
            keyword5=random.choice(keywords)
        )

        # Apply different confidence levels based on match quality
        if any(k in query.lower() for k in keyword_options[category]):
            confidence = random.randint(80, 98)
            confidence_level = "high"
        else:
            confidence = random.randint(50, 79)
            confidence_level = "medium"

        # Generate a recent date
        date = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d")

        results.append({
            "title": title,
            "snippet": snippet,
            "category": category,
            "date": date,
            "confidence": confidence,
            "confidence_level": confidence_level
        })

    # Sort by confidence (highest first)
    results.sort(key=lambda x: x["confidence"], reverse=True)

    logger.info(f"Generated {len(results)} search results")
    return results

@app.route('/search')
def search():
    """AI-powered search interface"""
    try:
        query = request.args.get('query', '')
        model = request.args.get('model', 'rag')  # Default to RAG model

        logger.info(f"Search requested with query: '{query}', model: {model}")

        results = []
        if query:
            # Perform AI search with the query
            results = perform_ai_search(query, model)
            logger.info(f"Search returned {len(results)} results for query: '{query}'")

        return render_template("search.html", query=query, model=model, results=results)
    except Exception as e:
        logger.error(f"Error in search route: {str(e)}")
        return f"Error in search: {str(e)}", 500

# Trend analysis functionality
def get_sustainability_trends(category=None):
    """
    Fetches and processes sustainability trends data using chain-of-thought reasoning.

    This function simulates the AI-powered trend analysis. In production, this would
    connect to an AI service like OpenAI's GPT model to perform real trend analysis.
    """
    logger.info(f"Generating sustainability trends data for category: {category}")

    # Step 1: Generate base trend data
    all_trends = []

    # Current date for our simulated data
    current_date = datetime.now()

    # Carbon emissions trends
    emissions_trends = [
        {
            "trend_id": 1,
            "category": "emissions",
            "name": "Carbon Emissions",
            "current_value": 30.0,
            "trend_direction": "decreasing",
            "virality_score": 78.5,
            "keywords": "carbon neutral, emissions reduction, climate impact",
            "trend_duration": "long-term",
            "timestamp": current_date.isoformat()
        },
        {
            "trend_id": 2,
            "category": "emissions",
            "name": "Science-Based Targets",
            "current_value": 45.0,
            "trend_direction": "increasing",
            "virality_score": 92.3,
            "keywords": "SBTi, net-zero, climate goals, Paris Agreement",
            "trend_duration": "long-term",
            "timestamp": current_date.isoformat()
        }
    ]

    # Energy consumption trends
    energy_trends = [
        {
            "trend_id": 3,
            "category": "energy",
            "name": "Renewable Energy",
            "current_value": 1050.0,
            "trend_direction": "increasing",
            "virality_score": 85.7,
            "keywords": "renewable energy, solar, wind, clean power",
            "trend_duration": "medium-term",
            "timestamp": current_date.isoformat()
        },
        {
            "trend_id": 4,
            "category": "energy",
            "name": "Energy Efficiency",
            "current_value": 880.0,
            "trend_direction": "decreasing",
            "virality_score": 65.2,
            "keywords": "efficiency, consumption reduction, power management",
            "trend_duration": "medium-term",
            "timestamp": current_date.isoformat()
        }
    ]

    # Water usage trends
    water_trends = [
        {
            "trend_id": 5,
            "category": "water",
            "name": "Water Conservation",
            "current_value": 320.0,
            "trend_direction": "decreasing",
            "virality_score": 45.8,
            "keywords": "water stewardship, conservation, usage reduction",
            "trend_duration": "medium-term",
            "timestamp": current_date.isoformat()
        }
    ]

    # Waste management trends
    waste_trends = [
        {
            "trend_id": 6,
            "category": "waste",
            "name": "Zero Waste Initiatives",
            "current_value": 78.0,
            "trend_direction": "increasing",
            "virality_score": 72.4,
            "keywords": "zero waste, circular economy, waste reduction",
            "trend_duration": "short-term",
            "timestamp": current_date.isoformat()
        },
        {
            "trend_id": 7,
            "category": "waste",
            "name": "Plastic Reduction",
            "current_value": 65.0,
            "trend_direction": "increasing",
            "virality_score": 94.5,
            "keywords": "plastic-free, reduction, single-use plastic",
            "trend_duration": "long-term",
            "timestamp": current_date.isoformat()
        }
    ]

    # ESG and social trends
    social_trends = [
        {
            "trend_id": 8,
            "category": "social",
            "name": "ESG Reporting Standards",
            "current_value": 82.0,
            "trend_direction": "increasing",
            "virality_score": 89.7,
            "keywords": "ESG reporting, sustainability metrics, corporate responsibility",
            "trend_duration": "long-term",
            "timestamp": current_date.isoformat()
        },
        {
            "trend_id": 9,
            "category": "social",
            "name": "Supply Chain Transparency",
            "current_value": 56.0,
            "trend_direction": "increasing",
            "virality_score": 76.3,
            "keywords": "supply chain, transparency, ethical sourcing",
            "trend_duration": "medium-term",
            "timestamp": current_date.isoformat()
        }
    ]

    # Combine all trends
    all_trends = emissions_trends + energy_trends + water_trends + waste_trends + social_trends

    logger.info(f"Generated {len(all_trends)} total trend records")

    # Step 2: Apply category filter if provided
    if category and category != 'all':
        filtered_trends = [trend for trend in all_trends if trend["category"] == category]
        logger.info(f"Filtered to {len(filtered_trends)} trends for category: {category}")
    else:
        filtered_trends = all_trends
        logger.info(f"Using all {len(filtered_trends)} trends (no category filter)")

    # Step 3: Generate chart data for trends over time (simulated)
    trend_chart_data = []
    for trend in filtered_trends:
        # Generate 6 data points over the past 6 months for each trend
        for i in range(6):
            timestamp = (current_date - timedelta(days=30 * (5 - i))).isoformat()

            # Simulate virality scores that evolve over time
            base_virality = trend["virality_score"] * 0.7  # Start lower
            growth_factor = 1 + (i * 0.1)  # Gradually increase

            # Add some randomness
            random_factor = random.uniform(0.9, 1.1)

            virality = min(base_virality * growth_factor * random_factor, 100)

            trend_chart_data.append({
                "category": trend["category"],
                "name": trend["name"],
                "virality_score": virality,
                "timestamp": timestamp
            })

    logger.info(f"Generated {len(trend_chart_data)} chart data points")

    return filtered_trends, trend_chart_data

@app.route('/trend-analysis')
def trend_analysis():
    """Sustainability trend analysis page"""
    try:
        logger.info("Trend analysis page requested")

        # Get category and sort filters from request args
        category = request.args.get('category', 'all')
        sort = request.args.get('sort', 'virality')

        logger.info(f"Trend analysis request with category={category}, sort={sort}")

        # Get trend analysis data
        trends, trend_chart_data = get_sustainability_trends(category)

        logger.info(f"Successfully generated {len(trends)} trends and {len(trend_chart_data)} chart data points")

        # Sort the trends based on user preference
        if sort == 'virality':
            trends.sort(key=lambda x: x['virality_score'], reverse=True)
        elif sort == 'date':
            trends.sort(key=lambda x: x['timestamp'], reverse=True)
        elif sort == 'name':
            trends.sort(key=lambda x: x['name'])

        logger.info(f"Rendering trend analysis with {len(trends)} trends")

        # Return a simple response for debugging if requested
        if request.args.get('debug') == 'true':
            return jsonify({
                'trends': trends,
                'trend_chart_data': trend_chart_data,
                'category': category,
                'sort': sort
            })

        return render_template("trend_analysis.html", 
                            trends=trends, 
                            trend_chart_data=trend_chart_data,
                            category=category,
                            sort=sort)
    except Exception as e:
        logger.error(f"Error in trend analysis: {str(e)}")
        # Return a simple response for debugging
        return f"Error in trend analysis: {str(e)}", 500

@app.route('/api/trends')
def api_trends():
    """API endpoint for sustainability trend data"""
    try:
        logger.info("API trends endpoint called")

        # Get category filter from request args if provided
        category = request.args.get('category')

        # Get trend analysis data
        trends, _ = get_sustainability_trends(category)

        logger.info(f"Returning {len(trends)} trends from API endpoint")
        return jsonify(trends)
    except Exception as e:
        logger.error(f"Error in API trends endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/debug')
def debug_route():
    """Debug route to check registered routes and connections"""
    try:
        logger.info("Debug route called")
        routes = [str(rule) for rule in app.url_map.iter_rules()]

        # Also check FastAPI connection
        try:
            logger.info(f"Testing connection to FastAPI backend: {BACKEND_URL}/health")
            response = requests.get(f"{BACKEND_URL}/health", timeout=5.0)
            response.raise_for_status()
            backend_status = response.json()
            logger.info(f"FastAPI backend health check: {backend_status}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to FastAPI backend: {str(e)}")
            backend_status = {"status": "error", "message": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error during backend health check: {str(e)}")
            backend_status = {"status": "error", "message": str(e)}

        debug_info = {
            "routes": routes,
            "backend_url": BACKEND_URL,
            "backend_status": backend_status
        }

        return jsonify(debug_info)
    except Exception as e:
        logger.error(f"Error in debug route: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Use port 5000 to match Replit's expected configuration
    port = 5000

    # Log registered routes for debugging
    routes = [str(rule) for rule in app.url_map.iter_rules()]
    logger.info(f"Registered routes: {routes}")
    logger.info(f"Starting Flask server on port {port}")

    # Start Flask server - use host 0.0.0.0 to make it accessible from outside the container
    app.run(host="0.0.0.0", port=port, debug=True)