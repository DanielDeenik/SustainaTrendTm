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
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8080')
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

        return render_template("search.html", query=query, results=results, model=model)
    except Exception as e:
        logger.error(f"Error in search route: {str(e)}")
        return f"Error loading search page: {str(e)}", 500

# AI-powered trend analysis endpoint
@app.route('/trend-analysis')
def trend_analysis():
    """
    AI-powered sustainability trend analysis page
    Shows trends, predictions, and insights for sustainability metrics
    """
    try:
        logger.info("Trend analysis page requested")

        # Fetch metrics data
        metrics = get_sustainability_metrics()

        # Get unique categories from metrics
        categories = list(set(metric["category"] for metric in metrics))
        logger.info(f"Available categories for trend analysis: {categories}")

        return render_template("trend_analysis.html", 
                              metrics=metrics, 
                              categories=categories)
    except Exception as e:
        logger.error(f"Error in trend analysis route: {str(e)}")
        return f"Error loading trend analysis: {str(e)}", 500

# API endpoint for trend data
@app.route('/api/trends')
def api_trends():
    """API endpoint for sustainability trend data"""
    try:
        logger.info("Trend API endpoint called")

        # Get category filter if provided
        category = request.args.get('category', None)

        # Get data source preference
        source = request.args.get('source', 'api')  # 'api' or 'mock'

        if source == 'api':
            # Try to get from API first
            try:
                metrics = get_sustainability_metrics()
                logger.info(f"Using API data for trend analysis with {len(metrics)} metrics")
            except Exception as api_error:
                logger.error(f"Error getting API metrics for trends: {str(api_error)}")
                # Fall back to mock data
                metrics = get_mock_sustainability_metrics()
                logger.info(f"Falling back to mock data for trend analysis")
        else:
            # Use mock data as requested
            metrics = get_mock_sustainability_metrics()
            logger.info(f"Using mock data for trend analysis as requested")

        # Filter by category if specified
        if category:
            logger.info(f"Filtering trend data by category: {category}")
            metrics = [m for m in metrics if m.get('category') == category]

        # Group metrics by name and sort by timestamp
        grouped_metrics = {}
        for metric in metrics:
            name = metric.get("name")
            if name not in grouped_metrics:
                grouped_metrics[name] = []
            grouped_metrics[name].append(metric)

        # Sort each group by timestamp
        for name in grouped_metrics:
            grouped_metrics[name].sort(key=lambda x: x.get("timestamp", ""))

        # Format for charting library
        trend_data = []
        for name, metrics_list in grouped_metrics.items():
            trend_series = {
                "name": name,
                "category": metrics_list[0].get("category") if metrics_list else "unknown",
                "unit": metrics_list[0].get("unit") if metrics_list else "",
                "values": [m.get("value") for m in metrics_list],
                "labels": [m.get("timestamp").split("T")[0] if "T" in m.get("timestamp", "") else m.get("timestamp") for m in metrics_list],
            }
            trend_data.append(trend_series)

        logger.info(f"Returning trend data with {len(trend_data)} series")
        return jsonify(trend_data)
    except Exception as e:
        logger.error(f"Error in trend API endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Debug endpoint for checking app status
@app.route('/debug')
def debug_info():
    """Debug endpoint for checking app status and configuration"""
    try:
        logger.info("Debug endpoint called")

        # Get environment information
        env_info = {
            "BACKEND_URL": BACKEND_URL,
            "REDIS_AVAILABLE": REDIS_AVAILABLE,
            "FLASK_ENV": os.environ.get("FLASK_ENV"),
            "PORT": os.environ.get("PORT"),
            "REQUEST_HOST": request.host,
            "SERVER_NAME": app.config.get("SERVER_NAME"),
        }

        # Get routes information
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                "endpoint": rule.endpoint,
                "methods": [m for m in rule.methods if m not in ["HEAD", "OPTIONS"]],
                "path": str(rule)
            })

        # Collect cache information
        cache_info = {
            "type": "Redis" if REDIS_AVAILABLE else "In-memory",
            "keys": len(MEMORY_CACHE) if not REDIS_AVAILABLE else "Unknown",
        }

        # Test API connectivity
        backend_status = "Unknown"
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=2.0)
            if response.status_code == 200:
                backend_status = f"Connected ({response.status_code})"
                backend_data = response.json()
            else:
                backend_status = f"Error ({response.status_code})"
                backend_data = {}
        except requests.exceptions.RequestException as e:
            backend_status = f"Connection Failed: {str(e)}"
            backend_data = {}

        debug_data = {
            "app_name": "Sustainability Intelligence Dashboard",
            "environment": env_info,
            "routes": routes,
            "cache": cache_info,
            "backend_api": {
                "url": BACKEND_URL,
                "status": backend_status,
                "data": backend_data
            },
            "timestamp": datetime.now().isoformat()
        }

        # Log some summary info
        logger.info(f"Debug info: Backend status: {backend_status}, Routes: {len(routes)}")

        return jsonify(debug_data)
    except Exception as e:
        logger.error(f"Error in debug endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Add API endpoint for summarization
@app.route('/api/summarize', methods=['POST'])
def summarize_text():
    """API endpoint to summarize sustainability text using AI"""
    try:
        logger.info("Text summarization API endpoint called")
        data = request.json

        if not data or not data.get('text'):
            logger.warning("Empty request body or missing text in summarization endpoint")
            return jsonify({"error": "Text parameter is required"}), 400

        text = data.get('text')
        max_length = data.get('max_length', 200)  # Default to 200 words max

        logger.info(f"Summarizing text with {len(text)} characters, max_length={max_length}")

        # Try to use OpenAI if available
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            try:
                logger.info("Using OpenAI for summarization")

                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {
                                "role": "system", 
                                "content": f"You are a sustainability expert. Summarize the following text in {max_length} words or less, focusing on key sustainability insights."
                            },
                            {"role": "user", "content": text}
                        ],
                        "max_tokens": 500,
                        "temperature": 0.5
                    },
                    timeout=20.0
                )

                if response.status_code == 200:
                    result = response.json()
                    summary = result["choices"][0]["message"]["content"].strip()
                    logger.info(f"Successfully generated AI summary with {len(summary.split())} words")
                    return jsonify({
                        "original_length": len(text.split()),
                        "summary_length": len(summary.split()),
                        "summary": summary
                    })
                else:
                    logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                    # Fall back to mock summarization
            except Exception as e:
                logger.error(f"Error using OpenAI for summarization: {str(e)}")
                # Fall back to mock summarization
        else:
            logger.warning("No OpenAI API key available, using mock summarization")

        # Mock summarization as fallback
        logger.info("Using mock summarization")

        # Simple extractive summary (just first few sentences depending on desired length)
        sentences = text.split('. ')
        num_sentences = min(5, max(1, max_length // 20))  # Rough heuristic
        mock_summary = '. '.join(sentences[:num_sentences]) + '.'

        if len(mock_summary) > len(text):
            mock_summary = text

        logger.info(f"Generated mock summary with {len(mock_summary.split())} words")

        return jsonify({
            "original_length": len(text.split()),
            "summary_length": len(mock_summary.split()),
            "summary": mock_summary,
            "note": "This is a simplified mock summary as OpenAI API was not available."
        })

    except Exception as e:
        logger.error(f"Error in summarization endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

# New endpoint for AI-powered predictive analytics
@app.route("/api/predictive-analytics", methods=["POST"])
def get_predictive_analytics():
    """API endpoint to proxy predictive analytics requests to the backend"""
    try:
        logger.info("Predictive analytics API endpoint called")
        data = request.json

        if not data:
            logger.warning("Empty request body in predictive analytics endpoint")
            return jsonify({"error": "Request body is required"}), 400

        logger.info(f"Forwarding predictive analytics request: {data}")

        # Forward the request to the backend
        response = requests.post(
            f"{BACKEND_URL}/api/predictive-analytics",
            json=data,
            timeout=30.0  # Longer timeout for AI processing
        )

        response.raise_for_status()
        result = response.json()

        logger.info(f"Successfully received predictive analytics from backend")
        return jsonify(result)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error forwarding predictive analytics request: {str(e)}")
        # Return a mock response with predictive trends
        mock_data = {
            "metrics": data.get("metrics", []),
            "forecast_periods": data.get("forecast_periods", 3),
            "predictions": [
                {
                    "metric_name": "Carbon Emissions",
                    "current_value": 30,
                    "predicted_values": [28.5, 27.2, 26.1],
                    "confidence_intervals": [[27.1, 29.9], [25.3, 29.1], [23.7, 28.5]],
                    "trend": "decreasing",
                    "trend_confidence": 0.85
                },
                {
                    "metric_name": "Energy Consumption",
                    "current_value": 1050,
                    "predicted_values": [1010, 980, 950],
                    "confidence_intervals": [[990, 1030], [950, 1010], [910, 990]],
                    "trend": "decreasing",
                    "trend_confidence": 0.82
                },
                {
                    "metric_name": "Water Usage",
                    "current_value": 300,
                    "predicted_values": [290, 280, 270],
                    "confidence_intervals": [[280, 300], [270, 290], [260, 280]],
                    "trend": "decreasing",
                    "trend_confidence": 0.79
                },
                {
                    "metric_name": "Waste Recycled",
                    "current_value": 82,
                    "predicted_values": [84, 86, 88],
                    "confidence_intervals": [[81, 87], [83, 89], [85, 91]],
                    "trend": "increasing",
                    "trend_confidence": 0.88
                },
                {
                    "metric_name": "ESG Score",
                    "current_value": 82,
                    "predicted_values": [84, 86, 88],
                    "confidence_intervals": [[81, 87], [83, 89], [85, 91]],
                    "trend": "increasing",
                    "trend_confidence": 0.9
                }
            ],
            "overall_sustainability_trend": "positive",
            "trend_drivers": [
                "Continued investments in renewable energy",
                "Implementation of water conservation technologies",
                "Expansion of recycling program across operations",
                "Strengthened ESG reporting and governance"
            ],
            "risk_factors": [
                "Potential supply chain disruptions",
                "Regulatory changes in carbon pricing",
                "Climate change impacts on water availability"
            ]
        }
        return jsonify(mock_data)
    except Exception as e:
        logger.error(f"Unexpected error in predictive analytics endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

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
        logger.error(f"Unexpected error in predictive analytics endpoint: {str(e)}")
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
                "Growth Trends": "25-30% annual growth expected in sustainability data services market"
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
    """Sustainability page for corporate sustainability intelligence"""
    try:
        logger.info("Sustainability page requested")
        return render_template("sustainability.html")
    except Exception as e:
        logger.error(f"Error in sustainability route: {str(e)}")
        return f"Error loading sustainability page: {str(e)}", 500

# Add a route for the stories page
@app.route('/sustainability-stories')
def sustainability_stories():
    """Sustainability stories page using data from FastAPI backend"""
    try:
        logger.info("Sustainability stories page requested")

        # Try to fetch stories from backend
        try:
            response = requests.get(f"{BACKEND_URL}/api/stories", timeout=10.0)
            response.raise_for_status()
            stories = response.json()
            logger.info(f"Successfully fetched {len(stories)} stories from API")
        except Exception as e:
            logger.error(f"Error fetching stories from API: {str(e)}")
            logger.info("Using mock stories data")
            # Mock stories if API fails
            stories = get_mock_stories()

        return render_template("sustainability_stories.html", stories=stories)
    except Exception as e:
        logger.error(f"Error in sustainability stories route: {str(e)}")
        return f"Error loading sustainability stories: {str(e)}", 500

# Helper function to generate mock stories
def get_mock_stories():
    """Generate mock sustainability stories as fallback"""
    logger.info("Generating mock sustainability stories")
    stories = [
        {
            "id": 1,
            "title": "Sustainability Story for EcoTech Solutions",
            "content": {
                "Company": "EcoTech Solutions",
                "Industry": "Technology",
                "Industry_Context": "The technology sector faces growing scrutiny over electronic waste and energy consumption.",
                "Sustainability_Strategy": "EcoTech has implemented a comprehensive circular economy approach to product design and manufacturing.",
                "Competitor_Benchmarking": "Leading the industry with 45% reduction in carbon footprint compared to top 5 competitors.",
                "Monetization_Model": "Premium pricing model justified by extended product lifespan and lower total cost of ownership.",
                "Investment_Pathway": "Investing $50M in renewable energy infrastructure and sustainable material research over 5 years.",
                "Actionable_Recommendations": [
                    "Expand product takeback programs to emerging markets",
                    "Implement blockchain-verified supply chain tracking",
                    "Develop AI-powered energy optimization for data centers",
                    "Launch sustainability impact scoring for products"
                ]
            },
            "company_name": "EcoTech Solutions",
            "industry": "Technology",
            "created_at": (datetime.now() - timedelta(days=7)).isoformat()
        },
        {
            "id": 2,
            "title": "Sustainability Story for GreenLeaf Foods",
            "content": {
                "Company": "GreenLeaf Foods",
                "Industry": "Food & Beverage",
                "Industry_Context": "The food industry is under pressure to reduce emissions, water usage, and packaging waste.",
                "Sustainability_Strategy": "GreenLeaf has adopted regenerative agriculture practices and plastic-free packaging.",
                "Competitor_Benchmarking": "Among top 3 companies for sustainable packaging, but lags in emissions reduction.",
                "Monetization_Model": "Brand premium and reduced costs through packaging optimization and waste reduction.",
                "Investment_Pathway": "Allocating 30% of R&D budget to sustainable packaging and regenerative farming practices.",
                "Actionable_Recommendations": [
                    "Implement comprehensive emissions reduction plan across supply chain",
                    "Expand regenerative agriculture to 80% of supplier network",
                    "Transition to water-neutral manufacturing within 3 years",
                    "Develop compostable packaging for all product lines"
                ]
            },
            "company_name": "GreenLeaf Foods",
            "industry": "Food & Beverage",
            "created_at": (datetime.now() - timedelta(days=14)).isoformat()
        },
        {
            "id": 3,
            "title": "Sustainability Story for EcoMobility",
            "content": {
                "Company": "EcoMobility",
                "Industry": "Transportation",
                "Industry_Context": "Transportation is a major contributor to global emissions, facing regulatory pressure.",
                "Sustainability_Strategy": "Transitioning to all-electric fleet with circular battery supply chain.",
                "Competitor_Benchmarking": "Leading EV transition among peer group, 35% ahead of industry average.",
                "Monetization_Model": "Innovative mobility-as-a-service model with sustainability subscription options.",
                "Investment_Pathway": "Secured $120M green bond for charging infrastructure and fleet electrification.",
                "Actionable_Recommendations": [
                    "Accelerate charging infrastructure deployment in underserved regions",
                    "Implement battery recycling and second-life programs",
                    "Develop carbon offset program for remaining emissions",
                    "Partner with renewable energy providers for charging networks"
                ]
            },
            "company_name": "EcoMobility",
            "industry": "Transportation",
            "created_at": (datetime.now() - timedelta(days=21)).isoformat()
        }
    ]
    return stories

# Add API endpoint for storytelling
@app.route('/api/storytelling', methods=['POST'])
def api_storytelling():
    """API endpoint to proxy storytelling requests to the backend"""
    try:
        logger.info("Storytelling API endpoint called")
        data = request.json

        if not data:
            logger.warning("Empty request body in storytelling endpoint")
            return jsonify({"error": "Request body is required"}), 400

        company_name = data.get('company_name')
        industry = data.get('industry')

        if not company_name or not industry:
            logger.warning("Missing required parameters in storytelling request")
            return jsonify({"error": "company_name and industry are required"}), 400

        logger.info(f"Forwarding storytelling request for {company_name} in {industry} industry")

        # Forward the request to the backend
        response = requests.post(
            f"{BACKEND_URL}/api/sustainability-story",
            params={"company_name": company_name, "industry": industry},
            timeout=45.0  # Longer timeout for AI-generated content
        )

        response.raise_for_status()
        result = response.json()

        logger.info(f"Successfully received sustainability story from backend")
        return jsonify(result)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error forwarding storytelling request: {str(e)}")

        # Generate mock sustainability story if backend is unavailable
        company_name = data.get('company_name', 'Company')
        industry = data.get('industry', 'Industry')

        logger.info(f"Generating mock sustainability story for {company_name}")

        mock_story = {
            "Company": company_name,
            "Industry": industry,
            "Industry_Context": f"The {industry} sector is experiencing rapid transformation due to sustainability pressures, regulatory changes, and evolving consumer preferences.",
            "Sustainability_Strategy": f"{company_name} is implementing a multi-faceted sustainability strategy focused on emissions reduction, resource efficiency, and stakeholder engagement.",
            "Competitor_Benchmarking": f"{company_name} ranks in the top quartile for sustainability reporting transparency but lags competitors in renewable energy adoption and water conservation.",
            "Monetization_Model": "Sustainability initiatives are monetized through premium pricing, operational cost reductions, and new green product lines targeting eco-conscious consumers.",
            "Investment_Pathway": "A phased 5-year investment plan allocates resources to emissions reduction technologies, supply chain optimization, and sustainable product innovation.",
            "Actionable_Recommendations": [
                f"Implement science-based targets for emissions reduction across {company_name}'s operations",
                "Develop comprehensive supplier sustainability program with verification mechanisms",
                "Launch green product innovation lab focused on circular economy principles",
                "Enhance sustainability reporting with quantifiable metrics and third-party verification"
            ]
        }

        return jsonify(mock_story)
    except Exception as e:
        logger.error(f"Unexpected error in storytelling endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Add a new route for the Analytics Dashboard
@app.route('/analytics-dashboard')
def analytics_dashboard():
    """AI-powered sustainability analytics dashboard"""
    try:
        logger.info("Analytics dashboard page requested")
        return render_template("analytics_dashboard.html")
    except Exception as e:
        logger.error(f"Error in analytics dashboard route: {str(e)}")
        return f"Error loading analytics dashboard: {str(e)}", 500

# Add a route for monetization opportunities page
@app.route('/monetization-opportunities')
def monetization_opportunities():
    """Monetization opportunities page"""
    try:
        logger.info("Monetization opportunities page requested")
        return render_template("monetization.html")
    except Exception as e:
        logger.error(f"Error in monetization opportunities route: {str(e)}")
        return f"Error loading monetization opportunities page: {str(e)}", 500

# Add the monetization strategy page route after the other page routes
@app.route('/monetization')
def monetization_strategy():
    """Monetization Strategy page for SustainaTrend 2.0"""
    try:
        logger.info("Monetization strategy page requested")
        return render_template("monetization.html")
    except Exception as e:
        logger.error(f"Error in monetization strategy route: {str(e)}")
        return f"Error loading monetization strategy page: {str(e)}", 500

if __name__ == "__main__":
    # Use the PORT environment variable provided by Replit, or default to 5000
    port = int(os.environ.get("PORT", 5000))

    # Log registered routes for debugging
    routes = [str(rule) for rule in app.url_map.iter_rules()]
    logger.info(f"Registered routes: {routes}")
    logger.info(f"Starting Flask server on port {port}")

    # Start the Flask app with the correct host and port
    app.run(host="0.0.0.0", port=port, debug=True)