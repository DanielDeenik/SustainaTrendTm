#!/usr/bin/env python3
"""
Flask frontend with improved FastAPI connection
for Sustainability Intelligence Dashboard
"""
import httpx
import asyncio
import time
import json
from urllib.parse import quote_plus
import redis
import re
from functools import wraps
import os
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request
import requests
from flask_caching import Cache
import logging
from datetime import datetime, timedelta
import random  # For generating mock AI search and trend data

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Starting Sustainability Intelligence Dashboard")

# Initialize Flask
app = Flask(__name__)

# OmniParser API endpoint
OMNIPARSER_API = "https://api.omniparser.com/parse"

# Setup Redis for caching if available
try:
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=0,
        socket_timeout=5,
        decode_responses=True
    )
    # Test connection
    redis_client.ping()
    logger.info("Connected to Redis successfully")
    REDIS_AVAILABLE = True
except (redis.ConnectionError, redis.exceptions.RedisError) as e:
    logger.warning(f"Redis connection failed, using in-memory cache instead: {str(e)}")
    REDIS_AVAILABLE = False

# In-memory cache as fallback
MEMORY_CACHE = {}

# Cache decorator that works with both Redis and in-memory
def cache_result(expire=300):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Create a cache key from function name and arguments
            cache_key = f"{f.__name__}:{str(args)}:{str(kwargs)}"

            # Try to get from cache first
            if REDIS_AVAILABLE:
                cached_result = redis_client.get(cache_key)
                if cached_result:
                    logger.info(f"Cache hit for {cache_key}")
                    return json.loads(cached_result)
            elif cache_key in MEMORY_CACHE:
                result, timestamp = MEMORY_CACHE[cache_key]
                if time.time() - timestamp < expire:
                    logger.info(f"Memory cache hit for {cache_key}")
                    return result

            # Execute function if not in cache
            result = f(*args, **kwargs)

            # Store in cache
            try:
                if REDIS_AVAILABLE:
                    redis_client.setex(cache_key, expire, json.dumps(result))
                else:
                    MEMORY_CACHE[cache_key] = (result, time.time())
            except Exception as e:
                logger.warning(f"Failed to cache result: {str(e)}")

            return result
        return decorated_function
    return decorator

# FastAPI backend URL
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')
logger.info(f"Using FastAPI backend URL: {BACKEND_URL}")


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

# AI-powered query expansion using OpenAI
def expand_query_with_ai(query, context="sustainability"):
    """
    Enhance the search query using OpenAI to make it more relevant to sustainability topics
    """
    try:
        logger.info(f"Expanding query with AI: '{query}'")

        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            logger.warning("No OpenAI API key available, skipping query expansion")
            return query

        # In a synchronous context, use regular requests
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {openai_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": f"You are a sustainability expert. Expand and enhance this search query to find the most relevant sustainability information. Return ONLY the enhanced query, nothing else."},
                    {"role": "user", "content": query}
                ],
                "max_tokens": 100,
                "temperature": 0.3
            },
            timeout=10.0
        )

        if response.status_code == 200:
            result = response.json()
            expanded_query = result["choices"][0]["message"]["content"].strip()
            logger.info(f"AI expanded query: '{expanded_query}'")
            return expanded_query
        else:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            return query
    except Exception as e:
        logger.error(f"Error in AI query expansion: {str(e)}")
        return query  # Return original query if expansion fails

# Real-time online search using DuckDuckGo
@cache_result(expire=1800)  # Cache for 30 minutes
def search_duckduckgo(query, max_results=10):
    """
    Perform a real-time online search using DuckDuckGo API
    """
    try:
        logger.info(f"Performing DuckDuckGo search for: '{query}'")

        # Ensure the query focuses on sustainability topics
        if not any(term in query.lower() for term in ["sustainability", "climate", "environment", "green", "eco", "carbon", "renewable", "energy", "water", "waste"]):
            query += " sustainability"

        encoded_query = quote_plus(query)

        # Use synchronous requests instead of async
        response = requests.get(
            f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1",
            headers={"User-Agent": "SustainaTrend Search Agent/1.0"},
            timeout=15.0
        )

        if response.status_code != 200:
            logger.error(f"DuckDuckGo API error: {response.status_code} - {response.text}")
            return []

        data = response.json()
        results = []

        # Extract Abstract (main result)
        if data.get("Abstract"):
            results.append({
                "title": data.get("Heading", "Main Result"),
                "snippet": data.get("Abstract"),
                "url": data.get("AbstractURL", ""),
                "category": "main",
                "date": "",  # DuckDuckGo doesn't provide dates
                "confidence": 95,
                "confidence_level": "high",
                "source": "DuckDuckGo"
            })

        # Extract Related Topics
        for topic in data.get("RelatedTopics", []):
            if len(results) >= max_results:
                break

            if "Text" in topic and "FirstURL" in topic:
                # Extract a title from the text (usually the first few words)
                text = topic["Text"]
                title_match = re.match(r'^(.{10,60}?)(?:\s-\s|\.\s)', text)
                title = title_match.group(1) if title_match else text[:60] + "..."

                results.append({
                    "title": title,
                    "snippet": text,
                    "url": topic.get("FirstURL", ""),
                    "category": "related",
                    "date": "",
                    "confidence": 80,
                    "confidence_level": "medium",
                    "source": "DuckDuckGo"
                })

        # If we still need more results, add from the Infobox if available
        if len(results) < max_results and data.get("Infobox") and data["Infobox"].get("content"):
            for item in data["Infobox"]["content"]:
                if len(results) >= max_results:
                    break

                if "label" in item and "value" in item:
                    results.append({
                        "title": item["label"],
                        "snippet": item["value"],
                        "url": data.get("AbstractURL", ""),
                        "category": "info",
                        "date": "",
                        "confidence": 85,
                        "confidence_level": "medium",
                        "source": "DuckDuckGo"
                    })

        logger.info(f"DuckDuckGo search returned {len(results)} results")
        return results
    except Exception as e:
        logger.error(f"Error in DuckDuckGo search: {str(e)}")
        return []

# Enhanced search function that combines AI-powered query expansion with real-time online search
def perform_enhanced_search(query, model="rag", max_results=15):
    """
    Enhanced search functionality that combines:
    1. AI-powered query expansion
    2. Real-time online search results
    3. Mock sustainability data (as fallback)
    4. Advanced relevance ranking algorithm
    """
    try:
        start_time = time.time()
        logger.info(f"Starting enhanced search for query: '{query}' using model: {model}")

        # Step 1: AI-powered query expansion
        expanded_query = expand_query_with_ai(query)

        # Step 2: Perform online search with expanded query
        online_results = search_duckduckgo(expanded_query, max_results)

        # Step 3: Get local mock results as a fallback or supplement
        mock_results = perform_ai_search(query, model)

        # Step 4: Combine and rank results using our advanced ranking algorithm
        combined_results = rank_and_combine_results(query, online_results, mock_results, max_results)

        # Log performance metrics
        search_time = time.time() - start_time
        logger.info(f"Enhanced search completed in {search_time:.2f}s with {len(combined_results)} results")

        return combined_results
    except Exception as e:
        logger.error(f"Error in enhanced search: {str(e)}")
        # Fallback to mock results if enhanced search fails
        return perform_ai_search(query, model)

# New function for advanced result ranking and combination
def rank_and_combine_results(query, online_results, mock_results, max_results=15):
    """
    Combine online and mock results with advanced ranking considering:
    1. Query relevance (keyword matching)
    2. Source credibility
    3. Recency
    4. Content diversity (across sustainability categories)
    """
    logger.info(f"Ranking and combining {len(online_results)} online results and {len(mock_results)} mock results")

    # Extract query keywords for relevance scoring
    keywords = [kw.lower() for kw in query.split() if len(kw) > 2]

    # Combine all results first
    all_results = []

    # Process online results
    for result in online_results:
        # Make sure the result has all required fields
        if 'confidence' not in result:
            result['confidence'] = 80
        if 'confidence_level' not in result:
            confidence = result.get('confidence', 80)
            if confidence >= 85:
                result['confidence_level'] = 'high'
            elif confidence >= 70:
                result['confidence_level'] = 'medium'
            else:
                result['confidence_level'] = 'low'

        # Add to combined results
        all_results.append(result)

    # Process mock results to avoid duplicates and add diversity
    online_titles = {r['title'].lower() for r in all_results}
    for result in mock_results:
        if result['title'].lower() not in online_titles:
            # Mark the result as coming from our internal AI
            result['source'] = 'Sustainability AI'
            all_results.append(result)

    # Apply advanced ranking algorithm
    for result in all_results:
        # Base score starts with confidence
        base_score = result.get('confidence', 80)

        # 1. Keyword relevance boost (up to +15 points)
        relevance_boost = calculate_keyword_relevance(result, keywords)

        # 2. Source credibility boost (up to +10 points)
        source_boost = 10 if result.get('source') == 'DuckDuckGo' else 5

        # 3. Recency boost (up to +10 points)
        recency_boost = calculate_recency_boost(result)

        # 4. Category diversity boost (5 points for underrepresented categories)
        category_boost = 5 if is_underrepresented_category(result, all_results) else 0

        # Calculate final ranking score
        result['ranking_score'] = base_score + relevance_boost + source_boost + recency_boost + category_boost

        logger.debug(f"Result '{result['title']}' - Base: {base_score}, Relevance: {relevance_boost}, "
                     f"Source: {source_boost}, Recency: {recency_boost}, Category: {category_boost}, "
                     f"Final: {result['ranking_score']}")

    # Sort by ranking score (highest first)
    all_results.sort(key=lambda x: x.get('ranking_score', 0), reverse=True)

    # Ensure result diversity by including top results from each category
    final_results = ensure_category_diversity(all_results, max_results)

    return final_results

# Helper function to calculate keyword relevance
def calculate_keyword_relevance(result, keywords):
    """Calculate relevance boost based on keyword matches in title and snippet"""
    if not keywords:
        return 0

    boost = 0
    title = result.get('title', '').lower()
    snippet = result.get('snippet', '').lower()

    # Check title for keywords (higher weight)
    for keyword in keywords:
        if keyword in title:
            boost += 5  # Higher boost for title matches

    # Check snippet for keywords
    for keyword in keywords:
        if keyword in snippet:
            boost += 2  # Lower boost for snippet matches

    # Cap the boost at 15 points
    return min(15, boost)

# Helper function to calculate recency boost
def calculate_recency_boost(result):
    """Calculate recency boost based on result date"""
    if not result.get('date'):
        return 0

    try:
        result_date = datetime.fromisoformat(result['date'].replace('Z', '+00:00'))
        now = datetime.now()
        days_old = (now - result_date).days

        if days_old < 7:  # Last week
            return 10
        elif days_old < 30:  # Last month
            return 7
        elif days_old < 90:  # Last quarter
            return 5
        elif days_old < 365:  # Last year
            return 3
        else:
            return 0
    except (ValueError, TypeError):
        return 0

# Helper function to identify underrepresented categories
def is_underrepresented_category(result, all_results):
    """Check if result's category is underrepresented in all_results"""
    category = result.get('category')
    if not category:
        return False

    # Count occurrences of each category
    category_counts = {}
    for r in all_results:
        cat = r.get('category')
        if cat:
            category_counts[cat] = category_counts.get(cat, 0) + 1

    # Calculate average category count
    avg_count = sum(category_counts.values()) / max(1, len(category_counts))

    # If this category appears less than average, consider it underrepresented
    return category_counts.get(category, 0) < avg_count

# Helper function to ensure category diversity
def ensure_category_diversity(results, max_results):
    """Ensure diversity by including top results from each category"""
    if len(results) <= max_results:
        return results

    # Group results by category
    category_results = {}
    for result in results:
        category = result.get('category', 'uncategorized')
        if category not in category_results:
            category_results[category] = []
        category_results[category].append(result)

    # Determine how many results to take from each category
    categories = list(category_results.keys())
    results_per_category = max(1, max_results // len(categories))

    # Take top N results from each category
    diverse_results = []
    for category in categories:
        diverse_results.extend(category_results[category][:results_per_category])

    # If we need more results to reach max_results, take them from the overall ranking
    remaining_slots = max_results - len(diverse_results)
    if remaining_slots > 0:
        # Create a set of already included results
        included_results = {r['title'] for r in diverse_results}
        # Add more results that aren't already included
        for result in results:
            if result['title'] not in included_results and remaining_slots > 0:
                diverse_results.append(result)
                remaining_slots -= 1

    # Final sort by ranking score
    diverse_results.sort(key=lambda x: x.get('ranking_score', 0), reverse=True)

    return diverse_results[:max_results]


# Fetch sustainability metrics from FastAPI backend with improved error handling
@cache_result(expire=300)
def get_sustainability_metrics():
    """Fetch sustainability metrics from FastAPI backend"""
    try:
        logger.info(f"Fetching metrics from FastAPI backend: {BACKEND_URL}/api/metrics")

        # Use synchronous requests instead of async
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

# Fix for real-time search API endpoint
@app.route("/api/realtime-search")
def api_realtime_search():
    """API endpoint for real-time search results"""
    try:
        query = request.args.get('query', '')
        model = request.args.get('model', 'rag')
        logger.info(f"Real-time search API called with query: '{query}', model: {model}")

        if not query:
            logger.warning("Real-time search API called with empty query")
            return jsonify({"error": "Query parameter is required"}), 400

        # Use synchronous function instead of async
        results = perform_enhanced_search(query, model)

        logger.info(f"Real-time search returned {len(results)} results")
        return jsonify({
            "query": query,
            "results": results,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in real-time search API: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Update the search route to use the enhanced search
@app.route('/search')
def search():
    """Enhanced AI-powered search interface"""
    try:
        query = request.args.get('query', '')
        model = request.args.get('model', 'rag')  # Default to RAG model

        logger.info(f"Search requested with query: '{query}', model: {model}")

        results = []
        if query:
            # For the initial page load, use the synchronous mock search to avoid delay
            # The UI will then fetch real-time results via AJAX
            results = perform_ai_search(query, model)
            logger.info(f"Initial search returned {len(results)} results for query: '{query}'")

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
            "name":"Zero Waste Initiatives",
            "current_value": 78.0,
            "trend_direction": "increasing",
            "virality_score": 72.4,
            "keywords": "zerowaste, circular economy, waste reduction",
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

# New API endpoint for AI-powered summarization
@app.route("/api/summarize", methods=["POST"])
def api_summarize_results():
    """API endpoint for AI-powered summarization of search results"""
    try:
        data = request.get_json()
        if not data or 'results' not in data or not data['results']:
            logger.warning("Summarize API called with no results")
            return jsonify({"error": "No results provided for summarization"}), 400

        query = data.get('query', '')
        results = data['results']
        logger.info(f"Summarize API called for query: '{query}' with {len(results)} results")

        # Extract content from results
        content = ""
        for result in results:
            content += f"Title: {result['title']}\n"
            content += f"Content: {result['snippet']}\n"
            if 'category' in result:
                content += f"Category: {result['category']}\n"
            content += "\n"

        # Generate summary using OpenAI API if available, otherwise use a mock summary
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            try:
                summary = generate_ai_summary(query, content, openai_api_key)
                logger.info(f"Generated AI summary for query: '{query}'")
            except Exception as e:
                logger.error(f"Error generating AI summary: {str(e)}")
                summary = generate_mock_summary(query, results)
        else:
            logger.warning("No OpenAI API key available, using mock summary")
            summary = generate_mock_summary(query, results)

        return jsonify({
            "query": query,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in summarize API: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Function to generate an AI-powered summary using OpenAI
def generate_ai_summary(query, content, api_key):
    """Generate a summary of search results using OpenAI API"""
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system", 
                        "content": """You are a sustainability expert. Create a concise, insightful summary 
                        of the search results provided. Focus on key sustainability themes, important trends, 
                        and actionable insights. Format your response with HTML tags for better readability:
                        - Use <h4> for section headings
                        - Use <p> for paragraphs
                        - Use <ul> and <li> for lists
                        - Use <strong> for emphasis
                        Include sections for: Key Themes, Important Findings, and Recommended Actions.
                        """
                    },
                    {
                        "role": "user", 
                        "content": f"Query: {query}\n\nSearch Results:\n{content}\n\nPlease provide a summary focusing on sustainability aspects."
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.5
            },
            timeout=15.0
        )

        if response.status_code == 200:
            result = response.json()
            summary = result["choices"][0]["message"]["content"].strip()
            return summary
        else:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            return generate_mock_summary(query, content)
    except Exception as e:
        logger.error(f"Error in AI summary generation: {str(e)}")
        return generate_mock_summary(query, content)

# Function to generate a mock summary when OpenAI is not available
def generate_mock_summary(query, results):
    """Generate a mock summary based on the query and results"""
    # Extract query keywords
    keywords = query.lower().split()

    # Determine the main sustainability themes based on keywords
    themes = []
    if any(k in keywords for k in ["carbon", "emission", "climate", "ghg", "greenhouse"]):
        themes.append("emissions reduction")
        themes.append("climate action")
    if any(k in keywords for k in ["energy", "renewable", "solar", "wind", "power"]):
        themes.append("renewable energy")
        themes.append("energy efficiency")
    if any(k in keywords for k in ["water", "resource", "conservation"]):
        themes.append("water conservation")
        themes.append("resource management")
    if any(k in keywords for k in ["waste", "recycle", "circular", "plastic"]):
        themes.append("waste reduction")
        themes.append("circular economy")
    if any(k in keywords for k in ["social", "governance", "esg", "ethical", "diversity"]):
        themes.append("social responsibility")
        themes.append("ESG performance")

    # Use general sustainability themes if no specific ones are identified
    if not themes:
        themes = [
            "sustainability practices",
            "environmental impact",
            "corporate sustainability",
            "sustainable development",
            "sustainability reporting"
        ]

    # Randomly select themes to highlight
    selected_themes = random.sample(themes, min(3, len(themes)))

    # Generate a formatted summary with HTML tags
    summary = f"""
    <h4>Key Themes: {query.title()}</h4>
    <p>Based on the analysis of multiple sustainability sources, the following key themes emerged:</p>
    <ul>
        <li><strong>{selected_themes[0].title()}</strong>: Multiple sources emphasize the importance of {selected_themes[0]} in addressing sustainability challenges.</li>
    """

    # Add more theme items if available
    if len(selected_themes) > 1:
        summary += f"<li><strong>{selected_themes[1].title()}</strong>: Organizations are increasingly focusing on {selected_themes[1]} as a critical component of their sustainability strategies.</li>\n"
    if len(selected_themes) > 2:
        summary += f"<li><strong>{selected_themes[2].title()}</strong>: There is growing evidence for the business value of implementing {selected_themes[2]} initiatives.</li>\n"

    summary += """
    </ul>

    <h4>Important Findings</h4>
    <p>The search results highlight several important sustainability trends:</p>
    <ul>
        <li>Organizations are increasingly adopting science-based targets for measuring and reducing environmental impacts</li>
        <li>Stakeholder engagement is becoming a crucial aspect of successful sustainability programs</li>
        <li>There is a growing focus on data-driven approaches to sustainability management</li>
    </ul>

    <h4>Recommended Actions</h4>
    <p>Based on the search results, the following actions are recommended:</p>
    <ul>
        <li>Establish clear metrics and targets for measuring sustainability progress</li>
        <li>Integrate sustainability considerations into core business strategies</li>
        <li>Engage with stakeholders to understand their priorities and concerns</li>
        <li>Stay informed about emerging sustainability trends and best practices</li>
    </ul>
    """

    return summary

# Add these new routes to proxy to the sustainability API endpoints
# Insert after the last defined API route, before if __name__ == "__main__"

# New API endpoints for AI-powered analytics
@app.route("/api/predictive-analytics", methods=["POST"])
def api_predictive_analytics():
    """API endpoint to proxy predictive analytics requests to the backend"""
    try:
        logger.info("Predictive analytics API endpoint called")
        data = request.json

        if not data:
            logger.warning("Empty request body in predictive analytics endpoint")
            return jsonify({"error": "Request body is required"}), 400

        # Extract parameters
        company_name = data.get('company_name')
        industry = data.get('industry')
        forecast_periods = data.get('forecast_periods', 3)
        metrics = data.get('metrics', [])

        if not company_name or not industry:
            logger.warning("Missing required fields in predictive analytics request")
            return jsonify({"error": "Company name and industry are required"}), 400

        logger.info(f"Generating predictive analytics for {company_name} in {industry} industry with {forecast_periods} forecast periods")

        # Forward the request to the FastAPI backend
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/predictive-analytics",
                params={
                    "company_name": company_name,
                    "industry": industry,
                    "forecast_periods": forecast_periods
                },
                json=metrics,
                timeout=30.0  # Longer timeout for AI processing
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"Successfully generated predictive analytics for {company_name}")
            return jsonify(result)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling predictive analytics API: {str(e)}")
            # Generate mock data as fallback
            current_date = datetime.now().isoformat()
            mock_data = {
                "forecast_date": current_date,
                "company": company_name,
                "industry": industry,
                "forecast_periods": forecast_periods,
                "predictions": [
                    {
                        "name": "Carbon Emissions",
                        "category": "emissions",
                        "current_value": 78.5,
                        "unit": "tCO2e",
                        "predicted_values": [75.2, 72.1, 69.3],
                        "confidence_intervals": [[73.1, 77.3], [69.5, 74.8], [65.2, 73.4]],
                        "trend_direction": "decreasing",
                        "trend_strength": "strong"
                    },
                    {
                        "name": "Energy Consumption",
                        "category": "energy",
                        "current_value": 1240,
                        "unit": "MWh",
                        "predicted_values": [1180, 1120, 1075],
                        "confidence_intervals": [[1150, 1210], [1080, 1160], [1020, 1130]],
                        "trend_direction": "decreasing",
                        "trend_strength": "moderate"
                    },
                    {
                        "name": "Water Usage",
                        "category": "water",
                        "current_value": 430,
                        "unit": "m³",
                        "predicted_values": [410, 395, 385],
                        "confidence_intervals": [[395, 425], [375, 415], [360, 410]],
                        "trend_direction": "decreasing",
                        "trend_strength": "moderate"
                    }
                ],
                "ai_insights": [
                    "Based on current trajectory, carbon emissions are expected to decrease by 11.7% over the forecast period",
                    "Energy efficiency improvements show diminishing returns after period 2",
                    "Water conservation efforts are showing steady improvement but at a slower rate than emissions reduction"
                ]
            }
            return jsonify(mock_data)

    except Exception as e:
        logger.error(f"Unexpected error in predictive analytics endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/materiality-assessment", methods=["POST"])
def api_materiality_assessment():
    """API endpoint to proxy materiality assessment requests to the backend"""
    try:
        logger.info("Materiality assessment API endpoint called")
        data = request.json

        if not data:
            logger.warning("Empty request body in materiality assessment endpoint")
            return jsonify({"error": "Request body is required"}), 400

        # Extract parameters
        company_name = data.get('company_name')
        industry = data.get('industry')
        metrics = data.get('metrics', [])

        if not company_name or not industry:
            logger.warning("Missing required fields in materiality assessment request")
            return jsonify({"error": "Company name and industry are required"}), 400

        logger.info(f"Performing materiality assessment for {company_name} in {industry} industry")

        # Forward the request to the FastAPI backend
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/materiality-assessment",
                params={
                    "company_name": company_name,
                    "industry": industry
                },
                json=metrics,
                timeout=30.0  # Longer timeout for AI processing
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"Successfully performed materiality assessment for {company_name}")
            return jsonify(result)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling materiality assessment API: {str(e)}")
            # Generate mock data as fallback
            mock_data = {
                "company": company_name,
                "industry": industry,
                "assessment_date": datetime.now().isoformat(),
                "material_topics": [
                    {
                        "topic": "Carbon Emissions",
                        "business_impact_score": 4.7,
                        "stakeholder_concern_score": 4.5,
                        "materiality_score": 4.6,
                        "financial_impact": "High potential regulatory costs and market access limitations",
                        "recommended_metrics": ["Scope 1-3 emissions (tCO2e)", "Carbon intensity (tCO2e/revenue)"]
                    },
                    {
                        "topic": "Energy Management",
                        "business_impact_score": 4.2,
                        "stakeholder_concern_score": 3.8,
                        "materiality_score": 4.0,
                        "financial_impact": "Operational cost savings and enhanced resilience",
                        "recommended_metrics": ["Energy intensity (MWh/revenue)", "Renewable energy (%)"]
                    },
                    {
                        "topic": "Water Management",
                        "business_impact_score": 3.8,
                        "stakeholder_concern_score": 3.5,
                        "materiality_score": 3.65,
                        "financial_impact": "Operational continuity and regulatory compliance costs",
                        "recommended_metrics": ["Water withdrawal (m³)", "Water recycling rate (%)"]
                    },
                    {
                        "topic": "Waste Management",
                        "business_impact_score": 3.2,
                        "stakeholder_concern_score": 3.7,
                        "materiality_score": 3.45,
                        "financial_impact": "Disposal costs and circular economy opportunities",
                        "recommended_metrics": ["Waste diverted from landfill (%)", "Hazardous waste (tonnes)"]
                    },
                    {
                        "topic": "Supply Chain Sustainability",
                        "business_impact_score": 4.0,
                        "stakeholder_concern_score": 3.9,
                        "materiality_score": 3.95,
                        "financial_impact": "Reputational risk and potential supply disruptions",
                        "recommended_metrics": ["Supplier ESG assessment coverage (%)", "Critical suppliers with science-based targets (%)"]
                    }
                ],
                "materiality_matrix": {
                    "x_axis": "Business Impact",
                    "y_axis": "Stakeholder Concern",
                    "quadrants": [
                        {"name": "Focus", "topics": ["Carbon Emissions", "Energy Management", "Supply Chain Sustainability"]},
                        {"name": "Monitor", "topics": ["Water Management", "Waste Management"]},
                        {"name": "Low Priority", "topics": ["Community Relations", "Biodiversity"]}
                    ]
                }
            }
            return jsonify(mock_data)

    except Exception as e:
        logger.error(f"Unexpected error in materiality assessment endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Add a new route for the analytics dashboard
@app.route('/analytics-dashboard')
def analytics_dashboard():
    """AI-powered sustainability analytics dashboard"""
    try:
        logger.info("Analytics dashboard page requested")
        return render_template("analytics_dashboard.html")
    except Exception as e:
        logger.error(f"Error in analytics dashboard route: {str(e)}")
        return f"Error loading analytics dashboard: {str(e)}", 500

@app.route("/api/sustainability-analysis", methods=["POST"])
def api_sustainability_analysis():
    """API endpoint to proxy sustainability analysis requests to the backend"""
    try:
        logger.info("Sustainability analysis API endpoint called")
        data = request.json

        if not data:
            logger.warning("Empty request body in sustainability analysis endpoint")
            return jsonify({"error": "Request body is required"}), 400

        logger.info(f"Forwarding sustainability analysis request: {data}")

        # Forward the request to the backend
        response = requests.post(
            f"{BACKEND_URL}/api/sustainability-analysis",
            json=data,
            timeout=30.0  # Longer timeout for AI processing
        )

        response.raise_for_status()
        result = response.json()

        logger.info(f"Successfully received sustainability analysis from backend")
        return jsonify(result)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error forwarding sustainability analysis request: {str(e)}")
        # Generate mock data if backend is unavailable
        company_name = data.get('company_name', 'Company')
        industry = data.get('industry', 'General')
        mock_data = {
            'Company': company_name,
            'Industry': industry,
            'Sustainability Score': 72,
            'Benchmarking Insights': [
                f"{company_name} is performing above industry average in renewable energy adoption",
                f"Water conservation metrics are 15% better than {industry} peers",
                "Supply chain sustainability needs improvement compared to industry leaders"
            ],
            'Recommended Sustainability Initiatives': [
                "Implement science-based emissions reduction targets",
                "Develop a circular economy program for waste reduction",
                "Enhance ESG reporting with quantifiable metrics",
                "Invest in renewable energy infrastructure"
            ],
            'Strategic Fit Score': 68
        }
        return jsonify(mock_data)
    except Exception as e:
        logger.error(f"Unexpected error in sustainability analysis endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/monetization-strategy", methods=["POST"])
def api_monetization_strategy():
    """API endpoint to proxy monetization strategy requests to the backend"""
    try:
        logger.info("Monetization strategy API endpoint called")
        data = request.json

        if not data:
            logger.warning("Empty request body in monetization strategy endpoint")
            return jsonify({"error": "Request body is required"}), 400

        logger.info(f"Forwarding monetization strategy request: {data}")

        # Forward the request to the backend
        response = requests.post(
            f"{BACKEND_URL}/api/monetization-strategy",
            json=data,
            timeout=30.0  # Longer timeout for AI processing
        )

        response.raise_for_status()
        result = response.json()

        logger.info(f"Successfully received monetization strategy from backend")
        return jsonify(result)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error forwarding monetization strategy request: {str(e)}")
        # Return a simplified mock response if the backend is unavailable
        company_name = data.get('company_name', 'Company')
        mock_data = {
            "Data Assets": [
                {
                    "Asset": "Carbon Emissions Data",
                    "Value Proposition": "Granular, verified emissions data across operations and supply chain",
                    "Potential Customers": ["ESG Rating Agencies", "Sustainability Consultants", "Carbon Offset Developers"]
                }
            ],
            "Monetization Models": [
                {
                    "Model": "Sustainability Analytics-as-a-Service",
                    "Description": "Subscription service providing insights and benchmarking from sustainability data",
                    "Revenue Potential": "$3-7M annually",
                    "Implementation Complexity": "Medium"
                }
            ],
            "Market Analysis": {
                "Total Addressable Market": "$4.5B globally for sustainability data services",
                "Competitive Landscape": "Emerging market with mix of startups and established sustainability consultancies",
                "Growth Trends": "25-30% annual growth expected in sustainability data servicesmarket"
            }
        }
        return jsonify(mock_data)
    except Exception as e:
        logger.error(f"Unexpected error in monetization strategy endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/apa-strategy", methods=["POST"])
def api_apa_strategy():
    """API endpoint to proxy APA strategy requests to the backend"""
    try:
        logger.info("APA strategy API endpoint called")
        data = request.json

        if not data:
            logger.warning("Empty request body in APA strategy endpoint")
            return jsonify({"error": "Request body is required"}), 400

        logger.info(f"Forwarding APA strategy request: {data}")

        # Forward the request to the backend
        response = requests.post(
            f"{BACKEND_URL}/api/apa-strategy",
            json=data,
            timeout=30.0  # Longer timeout for AI processing
        )

        response.raise_for_status()
        result = response.json()

        logger.info(f"Successfully received APA strategy from backend")
        return jsonify(result)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error forwarding APA strategy request: {str(e)}")
        # Return a simplified mock response if the backend is unavailable
        company_name = data.get('company_name', 'Company')
        mock_data = {
            "Executive Summary": f"{company_name} has significant opportunities to leverage sustainability as a competitive advantage and drive new revenue streams through ESG-focused initiatives.",
            "Strategic Assessment": {
                "Market Alignment": "Strong alignment with emerging sustainability trends in the industry.",
                "Competitive Position": "Currently middle-tier among sustainability leaders, with opportunity to advance.",
                "Growth Opportunities": [
                    "Expansion into sustainable product lines",
                    "Development of carbon offset marketplace",
                    "Sustainability consulting services for supply chain partners"
                ]
            },
            "Recommended Actions": [
                "Develop an integrated sustainability strategy aligned with business goals",
                "Invest in ESG data collection and analytics infrastructure",
                "Launch pilot monetization program in highest-potential area"
            ]
        }
        return jsonify(mock_data)
    except Exception as e:
        logger.error(f"Unexpected error in APA strategy endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Add this route to render the sustainability.html template
# Add after the other page routes (like /, /dashboard, /search, /trend-analysis)
@app.route('/sustainability')
def sustainability():
    """Sustainability analysis page using McKinsey frameworks"""
    try:
        logger.info("Sustainability analysis page requested")
        return render_template("sustainability.html")
    except Exception as e:
        logger.error(f"Error in sustainability route: {str(e)}")
        return f"Error loading sustainability page: {str(e)}", 500

# Add this route to render the sustainability_stories.html template
@app.route('/sustainability-stories')
def sustainability_stories():
    """Sustainability storytelling page using McKinsey frameworks"""
    try:
        logger.info("Sustainability storytelling page requested")
        return render_template("sustainability_stories.html")
    except Exception as e:
        logger.error(f"Error in sustainability storytelling route: {str(e)}")
        return f"Error loading sustainability storytelling page: {str(e)}", 500

# Add this API endpoint to proxy to our FastAPI storytelling backend
@app.route("/api/storytelling", methods=["POST"])
def api_storytelling():
    """API endpoint to proxy storytelling requests to the FastAPI backend"""
    try:
        logger.info("Storytelling API endpoint called")
        data = request.json

        if not data:
            logger.warning("Empty request body in storytelling endpoint")
            return jsonify({"error": "Request body is required"}), 400

        company_name = data.get('company_name')
        industry = data.get('industry')

        if not company_name or not industry:
            logger.warning("Missing required fields in storytelling request")
            return jsonify({"error": "Company name and industry are required"}), 400

        logger.info(f"Generating sustainability story for {company_name} in {industry} industry")

        # Forward the request to the FastAPI backend
        # The URL would be adjusted based on your deployment
        storytelling_api_url = os.getenv('STORYTELLING_API_URL', 'http://localhost:8080')

        try:
            response = requests.post(
                f"{storytelling_api_url}/api/sustainability-story",
                params={"company_name": company_name, "industry": industry},
                timeout=30.0  # Longer timeout for AI processing
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"Successfully generated sustainability story for {company_name}")
            return jsonify(result)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling storytelling API: {str(e)}")
            # If the API call fails, use our local storytelling AI as fallback

            # Import the storytelling AI function (assuming it's available)
            try:
                from services.storytelling_ai import generate_sustainability_story
                story = generate_sustainability_story(company_name, industry)
                return jsonify(story)
            except ImportError:
                logger.error("Could not import storytelling_ai module")
                # Generate a very simple mock story as a last resort
                mock_story = {
                    "Company": company_name,
                    "Industry": industry,
                    "Sustainability Strategy": f"A sustainable transformation strategy for {company_name} focusing on emission reductions, resource efficiency, and stakeholder engagement.",
                    "Monetization Model": f"Sustainability data analytics platform enabling {company_name} to monetize insights and benchmarking.",
                    "Investment Pathway": "Green bonds and sustainability-linked loans to finance initiatives with favorable terms.",
                    "Actionable Recommendations": [
                        "Implement science-based targets for emissions reduction",
                        "Develop comprehensive ESG data management system",
                        "Invest in renewable energy infrastructure"
                    ]
                }
                return jsonify(mock_story)

    except Exception as e:
        logger.error(f"Unexpected error in storytelling endpoint: {str(e)}")
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