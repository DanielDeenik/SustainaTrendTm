"""
Flask frontend with improved FastAPI connection
for Sustainability Intelligence Dashboard
"""
import httpx
import asyncio
import time
import json
import traceback
from urllib.parse import quote_plus
import redis
import re
from functools import wraps
import os
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request, redirect, url_for, abort
import requests
from flask_caching import Cache
import jinja2.exceptions
import logging
from datetime import datetime, timedelta
import random  # For generating mock AI search and trend data
from werkzeug.utils import secure_filename

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import SimpleMockService for data operations
try:
    # Try different import paths to handle various module configurations
    try:
        from services.simple_mock_service import SimpleMockService
    except ImportError:
        # Try relative import
        from .services.simple_mock_service import SimpleMockService
    
    # Create global instance
    mock_service = SimpleMockService()
    MOCK_SERVICE_AVAILABLE = True
    logger.info("SimpleMockService initialized successfully")
except ImportError as e:
    MOCK_SERVICE_AVAILABLE = False
    logger.warning(f"SimpleMockService not available: {e}")
    
# Import enhanced search functionality
try:
    from enhanced_search import initialize_search_engine, perform_search, format_search_results
    ENHANCED_SEARCH_AVAILABLE = True
    logger.info("Enhanced search functionality loaded successfully")
except ImportError as e:
    ENHANCED_SEARCH_AVAILABLE = False
    logger.warning(f"Enhanced search not available: {e}")

# Import Gemini search controller
try:
    from gemini_search import GeminiSearchController
    GEMINI_SEARCH_AVAILABLE = True
    gemini_search_controller = GeminiSearchController()
    logger.info("Gemini search controller initialized successfully")
except ImportError as e:
    GEMINI_SEARCH_AVAILABLE = False
    logger.warning(f"Gemini search not available: {e}")

logger.info("Starting Sustainability Intelligence Dashboard")

# Import AI Development Tools
try:
    from ai_development_tools import register_routes as register_ai_development_routes
    AI_DEVELOPMENT_TOOLS_AVAILABLE = True
    logger.info("AI Development Tools loaded successfully")
except ImportError as e:
    AI_DEVELOPMENT_TOOLS_AVAILABLE = False
    logger.warning(f"AI Development Tools not available: {e}")

# Import Sentiment Analysis Module
try:
    from sentiment_analysis import register_routes as register_sentiment_analysis_routes
    SENTIMENT_ANALYSIS_AVAILABLE = True
    logger.info("Sentiment Analysis module loaded successfully")
except ImportError as e:
    SENTIMENT_ANALYSIS_AVAILABLE = False
    logger.warning(f"Sentiment Analysis module not available: {e}")

# Import Ethical AI Compliance Module
try:
    from ethical_ai import register_routes as register_ethical_ai_routes
    ETHICAL_AI_AVAILABLE = True
    logger.info("Ethical AI Compliance module loaded successfully")
except ImportError as e:
    ETHICAL_AI_AVAILABLE = False
    logger.warning(f"Ethical AI Compliance module not available: {e}")

# Import Document Processor for PDF analysis
try:
    from document_processor import document_processor
    DOCUMENT_PROCESSOR_AVAILABLE = True
    logger.info("Document processor loaded successfully")
except ImportError as e:
    DOCUMENT_PROCESSOR_AVAILABLE = False
    logger.warning(f"Document processor not available: {e}")

# Import ESRS Framework Module
try:
    from esrs_framework import register_routes as register_esrs_framework_routes
    ESRS_FRAMEWORK_AVAILABLE = True
    logger.info("ESRS Framework module loaded successfully")
except ImportError as e:
    ESRS_FRAMEWORK_AVAILABLE = False
    logger.warning(f"ESRS Framework module not available: {e}")

# Import Company Search Module
try:
    from company_search import register_routes as register_company_search_routes
    COMPANY_SEARCH_AVAILABLE = True
    logger.info("Company Search module loaded successfully")
except ImportError as e:
    COMPANY_SEARCH_AVAILABLE = False
    logger.warning(f"Company Search module not available: {e}")

# Import Trend Virality Benchmarking Module
try:
    from trend_virality_benchmarking import register_routes as register_trend_virality_routes
    TREND_VIRALITY_AVAILABLE = True
    logger.info("Trend Virality Benchmarking module loaded successfully")
except ImportError as e:
    TREND_VIRALITY_AVAILABLE = False
    logger.warning(f"Trend Virality Benchmarking module not available: {e}")

# Import Sustainability Storytelling Module
try:
    from sustainability_storytelling import register_routes as register_storytelling_routes
    SUSTAINABILITY_STORYTELLING_AVAILABLE = True
    logger.info("Sustainability Storytelling module loaded successfully")
except ImportError as e:
    SUSTAINABILITY_STORYTELLING_AVAILABLE = False
    logger.warning(f"Sustainability Storytelling module not available: {e}")

# Import Real Estate Sustainability Module
try:
    from realestate_sustainability import register_routes as register_realestate_routes
    REALESTATE_SUSTAINABILITY_AVAILABLE = True
    logger.info("Real Estate Sustainability module loaded successfully")
except ImportError as e:
    REALESTATE_SUSTAINABILITY_AVAILABLE = False

# Import Strategy Simulation Module
try:
    from strategy_simulation import register_routes as register_strategy_simulation_routes
    STRATEGY_SIMULATION_AVAILABLE = True
    logger.info("Strategy Simulation module loaded successfully")
except ImportError as e:
    STRATEGY_SIMULATION_AVAILABLE = False
    logger.warning(f"Strategy Simulation module not available: {e}")

# Import Sustainability Co-Pilot Module
try:
    from sustainability_copilot import register_routes as register_sustainability_copilot_routes
    SUSTAINABILITY_COPILOT_AVAILABLE = True
    logger.info("Sustainability Co-Pilot module loaded successfully")
except ImportError as e:
    SUSTAINABILITY_COPILOT_AVAILABLE = False
    logger.warning(f"Sustainability Co-Pilot module not available: {e}")

# Initialize Flask
app = Flask(__name__)

# Register AI Development Tools routes if available
if AI_DEVELOPMENT_TOOLS_AVAILABLE:
    register_ai_development_routes(app)
    logger.info("AI Development Tools routes registered successfully")

# Register Sentiment Analysis routes if available
if SENTIMENT_ANALYSIS_AVAILABLE:
    register_sentiment_analysis_routes(app)
    logger.info("Sentiment Analysis routes registered successfully")

# Register Ethical AI Compliance routes if available
if ETHICAL_AI_AVAILABLE:
    register_ethical_ai_routes(app)
    logger.info("Ethical AI Compliance routes registered successfully")

# Register ESRS Framework routes if available
if ESRS_FRAMEWORK_AVAILABLE:
    register_esrs_framework_routes(app)
    logger.info("ESRS Framework routes registered successfully")

# Register Company Search routes if available
if COMPANY_SEARCH_AVAILABLE:
    register_company_search_routes(app)
    logger.info("Company Search routes registered successfully")

# Register Trend Virality routes if available
if TREND_VIRALITY_AVAILABLE:
    register_trend_virality_routes(app)
    logger.info("Trend Virality Benchmarking routes registered successfully")

# Register Sustainability Storytelling routes if available
if SUSTAINABILITY_STORYTELLING_AVAILABLE:
    register_storytelling_routes(app)
    logger.info("Sustainability Storytelling routes registered successfully")

# Register Real Estate Sustainability routes if available
if REALESTATE_SUSTAINABILITY_AVAILABLE:
    register_realestate_routes(app)
    logger.info("Real Estate Sustainability routes registered successfully")

# Register Strategy Simulation routes if available
if STRATEGY_SIMULATION_AVAILABLE:
    register_strategy_simulation_routes(app)
    logger.info("Strategy Simulation routes registered successfully")
    
# Register Sustainability Co-Pilot routes if available
if SUSTAINABILITY_COPILOT_AVAILABLE:
    register_sustainability_copilot_routes(app)
    logger.info("Sustainability Co-Pilot routes registered successfully")

# API Status global middleware
def get_api_status():
    """Get the current status of all API services"""
    try:
        # 1. Gemini API Status Check
        gemini_error = None
        if hasattr(gemini_search_controller, 'api_key') and gemini_search_controller.api_key:
            if GEMINI_SEARCH_AVAILABLE:
                gemini_available = True
            else:
                gemini_available = False
                gemini_error = "Gemini library not installed correctly"
        else:
            gemini_available = False
            gemini_error = "Gemini API key not configured or invalid"
            
        # 2. Google Search API Status Check
        google_error = None
        if hasattr(gemini_search_controller, 'google_api_key') and gemini_search_controller.google_api_key:
            # Validate Google API key format
            if len(gemini_search_controller.google_api_key) < 20:
                google_available = False
                google_error = "Google API key too short (should be 20+ characters)"
            elif ' ' in gemini_search_controller.google_api_key:
                google_available = False
                google_error = "Google API key contains spaces"
            elif hasattr(gemini_search_controller, 'search_service') and gemini_search_controller.search_service:
                google_available = True
            else:
                google_available = False
                google_error = "Google Search API client initialization failed"
        else:
            google_available = False
            google_error = "Google API key not configured"
            
        # 3. Check Google CSE ID
        cse_error = None
        if hasattr(gemini_search_controller, 'cse_id') and gemini_search_controller.cse_id:
            if len(gemini_search_controller.cse_id) < 10:
                cse_error = "Google CSE ID too short"
            elif ":" not in gemini_search_controller.cse_id and not gemini_search_controller.cse_id.startswith("0"):
                cse_error = "Google CSE ID has invalid format"
        else:
            cse_error = "Google CSE ID not configured"
            
        # If we have CSE error but no Google error yet, update the Google error
        if cse_error and not google_error:
            google_error = cse_error
            google_available = False
            
        # 4. Determine overall API status
        using_real_apis = gemini_available or google_available
        fallback_mode = None
        
        if not using_real_apis:
            fallback_mode = "Mock results"
            
        # 5. Create simple API status object
        return {
            "gemini_available": gemini_available,
            "google_available": google_available,
            "using_real_apis": using_real_apis,
            "fallback_active": fallback_mode is not None
        }
    except Exception as e:
        logger.error(f"Error checking API status: {str(e)}")
        return {
            "gemini_available": False,
            "google_available": False,
            "using_real_apis": False,
            "fallback_active": True,
            "error": str(e)
        }

# Inject API status into all templates
@app.context_processor
def inject_api_status():
    """Inject API status into all templates"""
    return {
        "api_status": get_api_status()
    }

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

# Enhanced search function that combines AI-powered query expansion with our advanced search engine
def perform_enhanced_search(query, model="hybrid", max_results=15):
    """
    Enhanced search functionality that combines:
    1. AI-powered query expansion
    2. Advanced search engine capabilities
    3. Real-time online search results
    4. Mock sustainability data (as fallback)
    5. Advanced relevance ranking algorithm
    """
    try:
        start_time = time.time()
        logger.info(f"Starting enhanced search for query: '{query}' using model: {model}")

        # Check if our advanced search engine is available
        if ENHANCED_SEARCH_AVAILABLE:
            try:
                logger.info(f"Using advanced search engine for query: '{query}'")
                
                # Step 1: AI-powered query expansion
                expanded_query = expand_query_with_ai(query)
                
                # Step 2: Use our advanced search engine
                # Create an event loop if one is not already running
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Use our advanced search engine
                search_results = loop.run_until_complete(
                    perform_search(
                        query=expanded_query,
                        mode=model,
                        max_results=max_results
                    )
                )
                
                # Format the results
                formatted_results = format_search_results(search_results)
                
                # Extract the results list from the formatted response
                results = formatted_results.get("results", [])
                
                # Log performance metrics
                search_time = time.time() - start_time
                logger.info(f"Advanced search completed in {search_time:.2f}s with {len(results)} results")
                
                # Always return a dictionary with results and explanation to maintain consistent format
                return {
                    "results": results,
                    "explanation": formatted_results.get("explanation", None)
                }
                
            except Exception as e:
                logger.error(f"Advanced search engine failed, falling back to traditional search: {str(e)}")
                # Continue with traditional search as fallback
        
        # Traditional search as fallback
        logger.info(f"Using traditional enhanced search for query: '{query}'")
        
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
        logger.info(f"Traditional enhanced search completed in {search_time:.2f}s with {len(combined_results)} results")

        # Package in the same dictionary format as the advanced search
        return {
            "results": combined_results,
            "explanation": {
                "query_expansion": f"Original query '{query}' expanded to '{expanded_query}'",
                "sources_used": ["DuckDuckGo", "Sustainability AI"]
            }
        }
    except Exception as e:
        logger.error(f"Error in enhanced search: {str(e)}")
        # Fallback to mock results if enhanced search fails
        ai_search_results = perform_ai_search(query, model)
        # The perform_ai_search function now also returns a dictionary with results and explanation
        return ai_search_results

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
    """Fetch sustainability metrics - now using SimpleMockService"""
    try:
        # Check if SimpleMockService is available and initialized
        if MOCK_SERVICE_AVAILABLE:
            logger.info("Using SimpleMockService for metrics data")
            metrics_data = mock_service.get_metrics()
            logger.info(f"Successfully fetched {len(metrics_data)} metrics from SimpleMockService")
            
            # Log a sample of the metrics data to verify format
            if metrics_data and len(metrics_data) > 0:
                logger.info(f"Sample metric data: {json.dumps(metrics_data[0], indent=2)}")
                logger.info(f"Metrics categories: {set(m['category'] for m in metrics_data)}")
                logger.info(f"Metrics names: {set(m['name'] for m in metrics_data)}")
            
            return metrics_data
            
        # If SimpleMockService is not available, try original API request
        logger.info(f"SimpleMockService not available, fetching from FastAPI backend: {BACKEND_URL}/api/metrics")

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
        
        # Convert metrics to JSON for JavaScript use
        import json
        from datetime import datetime
        
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, datetime):
                    return o.isoformat()
                return super().default(o)
        
        # Process metrics for additional context data
        categories = set()
        trend_metrics_count = 0
        earliest_date = None
        latest_date = None
        
        for metric in metrics:
            categories.add(metric.get('category', 'Uncategorized'))
            
            # Count improving trend metrics
            if metric.get('trend') == 'up' or (metric.get('trend') == 'down' and metric.get('trend_good', False)):
                trend_metrics_count += 1
            
            # Track date range
            timestamp = metric.get('timestamp')
            if timestamp:
                metric_date = timestamp if isinstance(timestamp, datetime) else datetime.fromisoformat(timestamp) if isinstance(timestamp, str) else None
                if metric_date:
                    if earliest_date is None or metric_date < earliest_date:
                        earliest_date = metric_date
                    if latest_date is None or metric_date > latest_date:
                        latest_date = metric_date
        
        # Calculate months of data
        data_range_months = 0
        if earliest_date and latest_date:
            data_range_months = ((latest_date.year - earliest_date.year) * 12 + 
                               latest_date.month - earliest_date.month + 1)
        
        # Convert categories to sorted list
        categories_list = sorted(list(categories))
        categories_json = json.dumps(categories_list)
        
        # Convert metrics to JSON for JavaScript use
        metrics_json = json.dumps(metrics, cls=DateTimeEncoder)
        
        # Set active page for navigation
        active_page = 'dashboard'
        
        # Prepare template context
        context = {
            'metrics': metrics,
            'metrics_json': metrics_json,
            'active_page': active_page,
            'title': 'Sustainability Dashboard',
            'description': 'Monitor and analyze key sustainability metrics',
            'show_actions': True,
            'show_export': True,
            'show_filter': True,
            'categories': categories_list,
            'categories_json': categories_json,
            'total_metrics': len(metrics),
            'category_count': len(categories),
            'data_range_months': data_range_months,
            'trend_metrics': trend_metrics_count
        }
        
        logger.info(f"Rendering dashboard with {len(metrics)} metrics")
        return render_template("dashboard_new.html", **context)
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
    
    # Package in the same dictionary format as other search results
    return {
        "results": results,
        "explanation": {
            "model": model,
            "query_analysis": f"Analyzed query '{query}' using {model} model",
            "matching_categories": categories
        }
    }

# Fix for real-time search API endpoint
@app.route("/api/realtime-search")
def api_realtime_search():
    """API endpoint for real-time search results"""
    try:
        query = request.args.get('query', '')
        model = request.args.get('model', 'hybrid')  # Default to hybrid model for new search engine
        logger.info(f"Real-time search API called with query: '{query}', model: {model}")

        if not query:
            logger.warning("Real-time search API called with empty query")
            return jsonify({"error": "Query parameter is required"}), 400

        # Use our enhanced search engine which now always returns a dictionary with results and explanation
        search_data = perform_enhanced_search(query, model)
        
        # Extract results from the standardized format
        if isinstance(search_data, dict) and 'results' in search_data:
            results = search_data.get('results', [])
            explanation = search_data.get('explanation', None)
        else:
            # Fallback for backward compatibility
            results = search_data
            explanation = None
            
        # Prepare response
        response_data = {
            "query": query,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add explanation if we have it
        if explanation:
            response_data['explanation'] = explanation

        logger.info(f"Real-time search returned {len(results) if isinstance(results, list) else 'unknown number of'} results")
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"Error in real-time search API: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Update the search route to use the enhanced search
@app.route('/search')
def search():
    """Redirects users to the enhanced Sustainability Co-Pilot interface"""
    try:
        query = request.args.get('query', '')
        model = request.args.get('model', 'copilot')  # Default to Co-Pilot mode
        
        logger.info(f"Search requested with query: '{query}', redirecting to Co-Pilot interface")
        
        # Initialize variables needed for template rendering
        results = []
        explanation = None
        
        # If query was provided, store it for the Co-Pilot to access
        if query:
            # Store the query in session for the Co-Pilot to use
            session_data = session.get('copilot_context', {})
            session_data['last_search_query'] = query
            session_data['last_search_time'] = datetime.now().isoformat()
            session['copilot_context'] = session_data
            
            logger.info(f"Stored query '{query}' in session for Co-Pilot")
            
        # Render the search template which now promotes the Co-Pilot
        return render_template(
            "search.html", 
            query=query, 
            results=results, 
            model=model, 
            enhanced_search_available=ENHANCED_SEARCH_AVAILABLE,
            explanation=explanation
        )
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

        # Check if the new standardized template exists, otherwise fall back to the original
        try:
            return render_template("trend_analysis_new.html", 
                                metrics=metrics, 
                                categories=categories)
        except jinja2.exceptions.TemplateNotFound:
            logger.warning("New standardized template not found, using original template")
            return render_template("trend_analysis.html", 
                                metrics=metrics, 
                                categories=categories)
    except Exception as e:
        logger.error(f"Error in trend analysis route: {str(e)}")
        return f"Error loading trend analysis: {str(e)}", 500

# API endpoint for trend data
@app.route('/api/trends')
def api_trends():
    """API endpoint for sustainability trend data for React dashboard"""
    try:
        logger.info("Trend API endpoint called")

        # Get category filter if provided
        category = request.args.get('category', None)

        # Get data source preference
        source = request.args.get('source', 'mock_service')  # 'api', 'mock', or 'mock_service'

        # Get the trends data based on the source preference
        if source == 'mock_service' and MOCK_SERVICE_AVAILABLE:
            # Use the SimpleMockService for trend data
            if category and category != 'all':
                trends_data = mock_service.get_trends(category=category)
                logger.info(f"Using SimpleMockService for trend analysis with category={category}")
            else:
                trends_data = mock_service.get_trends()
                logger.info(f"Using SimpleMockService for trend analysis (all categories)")
                
            # Get metrics for supplementary data
            metrics = get_sustainability_metrics()
            logger.info(f"Using metrics data for additional trend context")
            
            # We already have the trend data, so we'll use these later to supplement the metrics data
            has_trend_data = True
            
        elif source == 'api':
            # Try to get from API first
            try:
                metrics = get_sustainability_metrics()
                logger.info(f"Using API data for trend analysis with {len(metrics)} metrics")
                has_trend_data = False
            except Exception as api_error:
                logger.error(f"Error getting API metrics for trends: {str(api_error)}")
                # Fall back to mock data
                metrics = get_mock_sustainability_metrics()
                logger.info(f"Falling back to mock data for trend analysis")
                has_trend_data = False
        else:
            # Use mock data as requested
            metrics = get_mock_sustainability_metrics()
            logger.info(f"Using mock data for trend analysis as requested")
            has_trend_data = False

        # Filter metrics by category if specified
        if category and category != 'all':
            logger.info(f"Filtering metrics data by category: {category}")
            metrics = [m for m in metrics if m.get('category') == category]

        # Process metrics into trend cards format
        if source == 'mock_service' and MOCK_SERVICE_AVAILABLE and has_trend_data:
            # We already have the trend data from the mock service
            trends = trends_data
            logger.info(f"Using trend data directly from SimpleMockService ({len(trends)} trends)")
        else:
            # Use the calculate_trend_virality function to generate trends from metrics
            from sustainability_trend import calculate_trend_virality
            trends = calculate_trend_virality(metrics, category)
            logger.info(f"Generated {len(trends)} trends from metrics data using calculate_trend_virality")
        
        # Ensure trends are sorted by virality score (high to low)
        trends = sorted(trends, key=lambda x: x.get("virality_score", 0), reverse=True)
        
        # Format chart data for visualization with timestamps
        trend_chart_data = []
        
        # Get unique categories 
        categories = list(set(trend["category"] for trend in trends))
        
        # Get unique timestamps from the metrics data
        all_timestamps = []
        for metric in metrics:
            if metric.get("timestamp"):
                all_timestamps.append(metric.get("timestamp"))
        all_timestamps = sorted(list(set(all_timestamps)))
        
        # For each timestamp, get the virality score for each category
        for timestamp in all_timestamps:
            # Create a formatted timestamp for chart labels (YYYY-MM-DD)
            formatted_timestamp = timestamp.split("T")[0] if "T" in timestamp else timestamp
            
            # Find all trends at this timestamp by category
            chart_point = {"timestamp": formatted_timestamp}
            
            # Add category data
            for cat in categories:
                cat_trends = [t for t in trends if 
                              t.get("category") == cat and 
                              t.get("timestamp") == timestamp]
                
                if cat_trends:
                    # Use the highest virality score for this category
                    chart_point[cat] = max(t.get("virality_score", 0) for t in cat_trends)
                else:
                    chart_point[cat] = 0
                    
            trend_chart_data.append(chart_point)
        
        # Helper function to convert numpy numeric types to Python native types
        def convert_numeric_types(obj):
            if hasattr(obj, 'item'):  # Handle numpy numeric types (int64, float64)
                return obj.item()  # Converts numpy types to Python native types
            elif isinstance(obj, dict):
                return {k: convert_numeric_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numeric_types(i) for i in obj]
            else:
                return obj
        
        # Clean the trends data to ensure all values are JSON serializable
        cleaned_trends = []
        for trend in trends:
            cleaned_trend = {}
            for key, value in trend.items():
                cleaned_trend[key] = convert_numeric_types(value)
            cleaned_trends.append(cleaned_trend)
        
        # Clean chart data
        cleaned_chart_data = []
        for point in trend_chart_data:
            cleaned_point = {}
            for key, value in point.items():
                cleaned_point[key] = convert_numeric_types(value)
            cleaned_chart_data.append(cleaned_point)
        
        # Format response with trend data (both cards and chart data)
        response = {
            "success": True, 
            "trends": cleaned_trends,
            "chart_data": cleaned_chart_data,
            "category_counts": {}
        }
        
        # Count trends by category for distribution charts
        for cat in categories:
            count = len([t for t in trends if t["category"] == cat])
            response["category_counts"][cat] = int(count)  # Ensure count is a Python int
            
        logger.info(f"Returning trend data with {len(trends)} trends across {len(categories)} categories")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in trend API endpoint: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

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

@app.route('/api/mongodb-test')
def test_mongodb_connection():
    """Test the MongoDB connection and service layer"""
    try:
        # Create a Simple Mock Service manually without importing from another module
        class InlineMockService:
            """Inline mock service class for data operations"""
            
            @staticmethod
            def get_categories():
                """Get mock categories"""
                logger.info("Generating mock categories")
                return ["environmental", "social", "governance", "economic", "climate"]
                
            @staticmethod
            def get_metrics(limit: int = 5):
                """Get mock metrics data"""
                logger.info(f"Generating {limit} mock metrics")
                
                categories = ["environmental", "social", "governance", "economic"]
                metrics = []
                
                for i in range(limit):
                    category = random.choice(categories)
                    metric = {
                        "id": f"metric_{i+1}",
                        "name": f"Sample Metric {i+1}",
                        "category": category,
                        "value": round(random.uniform(10, 100), 1),
                        "unit": random.choice(["tons", "%", "score", "index"]),
                        "timestamp": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
                    }
                    metrics.append(metric)
                    
                return metrics
            
            @staticmethod
            def get_trends(limit: int = 5):
                """Get mock trends data"""
                logger.info(f"Generating {limit} mock trends")
                
                categories = ["environmental", "social", "governance", "economic"]
                trends = []
                
                for i in range(limit):
                    category = random.choice(categories)
                    trend = {
                        "id": f"trend_{i+1}",
                        "name": f"Sample Trend {i+1}",
                        "category": category,
                        "virality_score": round(random.uniform(0.3, 0.9), 2),
                        "timestamp": (datetime.now() - timedelta(days=random.randint(1, 14))).isoformat(),
                        "momentum": random.choice(["rising", "steady", "falling"])
                    }
                    trends.append(trend)
                    
                return trends
            
            @staticmethod
            def get_stories(limit: int = 5):
                """Get mock stories data"""
                logger.info(f"Generating {limit} mock stories")
                
                categories = ["environmental", "social", "governance", "economic"]
                stories = []
                
                for i in range(limit):
                    category = random.choice(categories)
                    story = {
                        "id": f"story_{i+1}",
                        "title": f"Sample Sustainability Story {i+1}",
                        "content": f"This is sample content for story {i+1}. It discusses important sustainability topics in the {category} category.",
                        "category": category,
                        "tags": random.sample(["innovation", "best practice", "case study", "leadership"], 2),
                        "publication_date": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
                    }
                    stories.append(story)
                    
                return stories
        
        # Create local instance of the inline service
        mock_service = InlineMockService()
        
        # Log the request
        logger.info("MongoDB test endpoint called (using inline mock service)")
        
        # Get data from mock service
        categories = mock_service.get_categories()
        metrics = mock_service.get_metrics(limit=5)
        trends = mock_service.get_trends(limit=5)
        stories = mock_service.get_stories(limit=5)
        
        # Prepare response
        result = {
            "status": "success",
            "message": "Mock data service working correctly",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "categories": categories,
                "metrics_count": len(metrics),
                "metrics_sample": metrics[:2] if metrics else [],
                "trends_count": len(trends),
                "trends_sample": trends[:2] if trends else [],
                "stories_count": len(stories),
                "stories_sample": stories[:2] if stories else []
            }
        }
        
        logger.info(f"Mock data test successful: {len(metrics)} metrics, {len(trends)} trends, {len(stories)} stories found")
        return jsonify(result)
    except Exception as e:
        # Log the error
        logger.error(f"MongoDB connection test failed: {str(e)}")
        
        # Return error response
        return jsonify({
            "status": "error",
            "message": f"MongoDB connection or service layer error: {str(e)}",
            "error_type": str(type(e).__name__),
            "timestamp": datetime.now().isoformat()
        }), 500

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

# Add a test endpoint to check routing issues
@app.route('/test-route')
def test_route():
    """Test route to diagnose routing issues"""
    try:
        logger.info("Test route requested")
        return jsonify({
            "status": "success",
            "message": "Test route is working correctly",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        logger.error(f"Error in test route: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Add atomic navigation demo page
@app.route('/atomic-navigation-demo')
def atomic_navigation_demo():
    """Demo page for atomic navigation components with SimCorp One inspiration"""
    try:
        logger.info("Atomic navigation demo page requested")
        return render_template("atomic_navigation_demo.html")
    except Exception as e:
        logger.error(f"Error in atomic navigation demo: {str(e)}")
        return f"Error loading atomic navigation demo: {str(e)}", 500

# Add Finchat-inspired real estate minimal dashboard
@app.route('/realestate-minimal')
def realestate_minimal_dashboard():
    """Minimalist Finchat-inspired Real Estate Dashboard"""
    try:
        logger.info("Minimal Finchat-inspired real estate dashboard requested")
        return render_template("realestate_unified_minimal.html")
    except Exception as e:
        logger.error(f"Error in minimal real estate dashboard: {str(e)}")
        return f"Error loading minimal real estate dashboard: {str(e)}", 500

# AI Prompt API endpoint for Finchat-inspired interface
@app.route('/api/ai-prompt', methods=['POST'])
def ai_prompt_endpoint():
    """Process AI prompts for the Finchat-inspired interface"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        logger.info(f"AI prompt received: '{prompt}'")
        
        # Process the prompt to determine the appropriate action
        prompt_lower = prompt.lower()
        
        # Check if this is a navigation request
        if any(keyword in prompt_lower for keyword in ['show', 'go to', 'navigate', 'open']):
            if 'real estate' in prompt_lower or 'property' in prompt_lower:
                return jsonify({"redirect": "/realestate-minimal"})
            elif 'trend' in prompt_lower or 'analysis' in prompt_lower:
                return jsonify({"redirect": "/trend-analysis"})
            elif 'dashboard' in prompt_lower:
                return jsonify({"redirect": "/dashboard"})
            elif 'search' in prompt_lower:
                return jsonify({"redirect": "/search"})
        
        # For testing and development, always use predefined insights
        # In production with API keys, you would use the real Gemini API
        use_predefined_insights = True
            
        if use_predefined_insights:
            # Fallback to predefined insights based on keywords
            logger.info(f"Using predefined insights for prompt: '{prompt_lower}'")
            
            # Check for keyword matches with simple wordlist approach
            if any(word in prompt_lower for word in ['carbon', 'emission', 'emissions', 'co2']):
                insight = "Properties with the lowest carbon emissions show a 23% higher occupancy rate in your portfolio."
            elif any(word in prompt_lower for word in ['energy', 'electricity', 'power']):
                insight = "Installing smart energy management systems could reduce energy costs by up to 31% across your portfolio."
            elif any(word in prompt_lower for word in ['water', 'usage', 'consumption']):
                insight = "Your properties with rainwater harvesting systems use 42% less municipal water than similar properties."
            elif any(word in prompt_lower for word in ['certification', 'breeam', 'rating', 'certified']):
                insight = "BREEAM Excellent properties command 15% higher rental rates than non-certified properties in the same area."
            elif any(word in prompt_lower for word in ['trend', 'market', 'future']):
                insight = "Recent market trends show increasing demand for properties with renewable energy infrastructure, with premiums growing by 8% annually."
            else:
                insight = "I notice your portfolio's sustainability score is 17% above the industry average, primarily due to strong energy efficiency measures."
            
            logger.info(f"Selected insight: '{insight}'")
        else:
            # In a production app, this would make an actual API call to Gemini
            insight = "I'd need to connect to the Gemini API to provide a detailed insight on that topic."
                
        return jsonify({"insight": insight})
    except Exception as e:
        logger.error(f"Error processing AI prompt: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Add a simple monetization page for troubleshooting
@app.route('/monetization-simple')
def monetization_simple():
    """Simple monetization page without complex HTML for troubleshooting"""
    try:
        logger.info("Simple monetization page requested")
        content = """
        <html>
        <head>
            <title>Monetization Strategy (Simple)</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #2c7744; }
                .card { border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>Monetization Strategy - Simple View</h1>
            
            <div class="card">
                <h2>Strategy 1: Data-as-a-Service</h2>
                <p>Provide subscription access to sustainability metrics and insights.</p>
            </div>
            
            <div class="card">
                <h2>Strategy 2: AI-Powered Analytics</h2>
                <p>Offer premium AI analysis of sustainability trends and recommendations.</p>
            </div>
            
            <div class="card">
                <h2>Strategy 3: Consulting Services</h2>
                <p>Leverage platform insights to deliver tailored sustainability consulting.</p>
            </div>
            
            <p><a href="/">Return to Home</a></p>
        </body>
        </html>
        """
        return content
    except Exception as e:
        logger.error(f"Error in simple monetization route: {str(e)}")
        return f"Error loading simple monetization page: {str(e)}", 500

# Add the monetization strategy page route after the other page routes
@app.route('/monetization')
def monetization_strategy():
    """Monetization Strategy page for SustainaTrend 2.0"""
    try:
        logger.info("Monetization strategy page requested")
        
        # Check if this is a request from Replit's webview by examining headers
        is_replit_webview = 'X-Forwarded-For' in request.headers or 'X-Replit-User-Id' in request.headers
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Is Replit webview: {is_replit_webview}")
        
        # Option to force text response for debugging in Replit
        force_text = request.args.get('format') == 'text'
        
        # Add debug information to the template context
        debug_info = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "route": "monetization",
            "template": "monetization.html",
            "server": "Flask/Python",
            "headers": dict(request.headers),
            "is_replit_webview": is_replit_webview
        }
        logger.info(f"Serving monetization page with debug info: {debug_info}")
        
        if force_text:
            # Return a simple text response for debugging
            return f"Monetization Strategy Page\n\nDebug Info: {json.dumps(debug_info, indent=2)}", 200, {'Content-Type': 'text/plain'}
        else:
            return render_template("monetization.html", debug_info=debug_info)
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error in monetization strategy route: {str(e)}")
        logger.error(f"Error traceback: {error_details}")
        return f"Error loading monetization strategy page: {str(e)}\n\nDetails: {error_details}", 500

# Gemini-powered Search Routes
@app.route("/api-status")
def api_status_dashboard():
    """API Status Dashboard showing all API service statuses and configurations"""
    try:
        # 1. Gemini API Status Check
        gemini_error = None
        if hasattr(gemini_search_controller, 'api_key') and gemini_search_controller.api_key:
            if GEMINI_SEARCH_AVAILABLE:
                gemini_available = True
            else:
                gemini_available = False
                gemini_error = "Gemini library not installed correctly"
        else:
            gemini_available = False
            gemini_error = "Gemini API key not configured or invalid"
            
        # 2. Google Search API Status Check
        google_error = None
        if hasattr(gemini_search_controller, 'google_api_key') and gemini_search_controller.google_api_key:
            # Validate Google API key format
            if len(gemini_search_controller.google_api_key) < 20:
                google_available = False
                google_error = "Google API key too short (should be 20+ characters)"
            elif ' ' in gemini_search_controller.google_api_key:
                google_available = False
                google_error = "Google API key contains spaces"
            elif hasattr(gemini_search_controller, 'search_service') and gemini_search_controller.search_service:
                google_available = True
            else:
                google_available = False
                google_error = "Google Search API client initialization failed"
        else:
            google_available = False
            google_error = "Google API key not configured"
            
        # 3. Check Google CSE ID
        cse_error = None
        if hasattr(gemini_search_controller, 'cse_id') and gemini_search_controller.cse_id:
            if len(gemini_search_controller.cse_id) < 10:
                cse_error = "Google CSE ID too short"
            elif ":" not in gemini_search_controller.cse_id and not gemini_search_controller.cse_id.startswith("0"):
                cse_error = "Google CSE ID has invalid format"
        else:
            cse_error = "Google CSE ID not configured"
            
        # If we have CSE error but no Google error yet, update the Google error
        if cse_error and not google_error:
            google_error = cse_error
            google_available = False
            
        # 4. Determine overall API status
        using_real_apis = gemini_available or google_available
        fallback_mode = None
        
        if not using_real_apis:
            fallback_mode = "Mock results"
            
        # 5. Comprehensive status message
        status_message = None
        if not using_real_apis:
            status_message = "Using mock results as both APIs are unavailable"
            
        # 6. Create API status object
        api_status = {
            "gemini_available": gemini_available,
            "google_available": google_available,
            "using_real_apis": using_real_apis,
            "fallback_active": fallback_mode is not None,
            "fallback_mode": fallback_mode,
            "gemini_error": gemini_error,
            "google_error": google_error,
            "status_message": status_message
        }
        
        # 7. Add mock API logs for demonstration
        gemini_logs = [
            {"timestamp": "2025-03-02 20:15:32", "status": "200 OK", "success": True, "latency": 450},
            {"timestamp": "2025-03-02 20:14:21", "status": "200 OK", "success": True, "latency": 425},
            {"timestamp": "2025-03-02 20:12:55", "status": "200 OK", "success": True, "latency": 512},
            {"timestamp": "2025-03-02 20:10:11", "status": "429 Rate Limited", "success": False, "latency": 320},
            {"timestamp": "2025-03-02 20:08:45", "status": "200 OK", "success": True, "latency": 475}
        ]
        
        google_logs = [
            {"timestamp": "2025-03-02 20:15:44", "status": "200 OK", "success": True, "latency": 320},
            {"timestamp": "2025-03-02 20:14:32", "status": "200 OK", "success": True, "latency": 345},
            {"timestamp": "2025-03-02 20:12:21", "status": "200 OK", "success": True, "latency": 310},
            {"timestamp": "2025-03-02 20:10:55", "status": "200 OK", "success": True, "latency": 330},
            {"timestamp": "2025-03-02 20:09:11", "status": "400 Bad Request", "success": False, "latency": 125}
        ]
        
        # 8. Get Gemini model count if available
        gemini_models = 37  # Default to 37
        if hasattr(gemini_search_controller, '_best_model'):
            gemini_models = len(gemini_search_controller._best_model)
            
        return render_template(
            'api_status_dashboard.html',
            api_status=api_status,
            gemini_logs=gemini_logs,
            google_logs=google_logs,
            gemini_models=gemini_models
        )
        
    except Exception as e:
        logger.error(f"Error in API status dashboard: {str(e)}")
        return f"Error loading API status dashboard: {str(e)}", 500

@app.route("/gemini-search")
def gemini_search():
    """
    Gemini-powered enhanced AI search interface with Google Search integration
    """
    try:
        query = request.args.get('query', '')
        mode = request.args.get('mode', 'hybrid')  # hybrid, gemini, google
        
        logger.info(f"Gemini search requested with query: '{query}', mode: {mode}")
        
        # Check API status with enhanced, detailed information from our controller
        # 1. Gemini API Status Check
        gemini_error = None
        if hasattr(gemini_search_controller, 'api_key') and gemini_search_controller.api_key:
            if GEMINI_SEARCH_AVAILABLE:
                gemini_available = True
            else:
                gemini_available = False
                gemini_error = "Gemini library not installed correctly"
        else:
            gemini_available = False
            gemini_error = "Gemini API key not configured or invalid"
            
        # 2. Google Search API Status Check
        google_error = None
        if hasattr(gemini_search_controller, 'google_api_key') and gemini_search_controller.google_api_key:
            # Validate Google API key format
            if len(gemini_search_controller.google_api_key) < 20:
                google_available = False
                google_error = "Google API key too short (should be 20+ characters)"
            elif ' ' in gemini_search_controller.google_api_key:
                google_available = False
                google_error = "Google API key contains spaces"
            elif hasattr(gemini_search_controller, 'search_service') and gemini_search_controller.search_service:
                google_available = True
            else:
                google_available = False
                google_error = "Google Search API client initialization failed"
        else:
            google_available = False
            google_error = "Google API key not configured"
            
        # 3. Check Google CSE ID
        cse_error = None
        if hasattr(gemini_search_controller, 'cse_id') and gemini_search_controller.cse_id:
            if len(gemini_search_controller.cse_id) < 10:
                cse_error = "Google CSE ID too short"
            elif ":" not in gemini_search_controller.cse_id and not gemini_search_controller.cse_id.startswith("0"):
                cse_error = "Google CSE ID has invalid format"
        else:
            cse_error = "Google CSE ID not configured"
            
        # If we have CSE error but no Google error yet, update the Google error
        if cse_error and not google_error:
            google_error = cse_error
            google_available = False
            
        # 4. Determine overall API status
        using_real_apis = gemini_available or google_available
        fallback_mode = None
        
        if using_real_apis:
            if mode == "hybrid":
                if gemini_available and google_available:
                    fallback_mode = None  # Both APIs available for hybrid search
                elif gemini_available:
                    fallback_mode = "Gemini only"  # Fall back to Gemini only
                elif google_available:
                    fallback_mode = "Google only"  # Fall back to Google only
            elif mode == "gemini" and not gemini_available:
                fallback_mode = "Mock results"  # Gemini requested but unavailable
            elif mode == "google" and not google_available:
                fallback_mode = "Mock results"  # Google requested but unavailable
        else:
            fallback_mode = "Mock results"  # No real APIs available
            
        # 5. Comprehensive status message
        status_message = None
        if not using_real_apis:
            status_message = "Using mock results as both APIs are unavailable"
        elif fallback_mode:
            if fallback_mode == "Gemini only":
                status_message = "Google Search API unavailable, using Gemini API only"
            elif fallback_mode == "Google only":
                status_message = "Gemini API unavailable, using Google Search API only"
            else:
                status_message = f"Using fallback mode: {fallback_mode}"
                
        # 6. Create comprehensive API status object
        api_status = {
            "gemini_available": gemini_available,
            "google_available": google_available,
            "using_real_apis": using_real_apis,
            "fallback_active": fallback_mode is not None,
            "fallback_mode": fallback_mode,
            "gemini_error": gemini_error,
            "google_error": google_error,
            "status_message": status_message,
            "search_mode": mode,
            "effective_mode": fallback_mode if fallback_mode else mode
        }
        
        results = []
        enhanced_query = query
        query_analysis = None
        
        if query:
            if GEMINI_SEARCH_AVAILABLE:
                try:
                    # Use Gemini search controller
                    # Create an event loop if one is not already running
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    # Perform the search with Gemini
                    search_response = loop.run_until_complete(
                        gemini_search_controller.enhanced_search(
                            query=query,
                            mode=mode,
                            max_results=15
                        )
                    )
                    
                    # Extract results and metadata
                    results = search_response.get("results", [])
                    metadata = search_response.get("metadata", {})
                    enhanced_query = metadata.get("enhanced_query", query)
                    query_analysis = search_response.get("query_analysis", "")
                    
                    logger.info(f"Gemini search returned {len(results)} results for query: '{query}'")
                except Exception as e:
                    logger.error(f"Error in Gemini search: {str(e)}")
                    # Fall back to standard enhanced search
                    search_results = perform_enhanced_search(query, model="hybrid")
                    results = search_results.get("results", [])
            else:
                # Fall back to standard enhanced search
                logger.warning(f"Gemini search not available, falling back to standard search")
                search_results = perform_enhanced_search(query, model="hybrid")
                results = search_results.get("results", [])
        
        # Render the search template with results and API status
        return render_template('gemini_search.html', 
                              query=query,
                              mode=mode,
                              results=results,
                              enhanced_query=enhanced_query,
                              query_analysis=query_analysis,
                              api_status=api_status)
    
    except Exception as e:
        logger.error(f"Error in Gemini search route: {str(e)}")
        # Create an enhanced fallback API status for error case
        error_api_status = {
            "gemini_available": False,
            "google_available": False,
            "using_real_apis": False,
            "fallback_active": True,
            "fallback_mode": "Error mode",
            "gemini_error": "Search route encountered an error",
            "google_error": "Search route encountered an error",
            "status_message": "An error occurred in the search process",
            "search_mode": mode if 'mode' in locals() else "hybrid",
            "effective_mode": "Error fallback",
            "error_message": str(e)
        }
        
        # Return an error message but still render the template
        return render_template('gemini_search.html', 
                              query=query if 'query' in locals() else "",
                              mode=mode if 'mode' in locals() else "hybrid",
                              results=[],
                              error=str(e),
                              api_status=error_api_status)

@app.route("/api-gemini-search", methods=['GET', 'POST'])
def api_gemini_search():
    """
    API endpoint for Gemini-powered search
    Used for AJAX requests from the search page
    Supports both GET and POST requests
    """
    try:
        # Handle both GET and POST requests
        if request.method == 'POST':
            # Check if request is JSON
            if request.is_json:
                data = request.get_json()
                query = data.get('query', '')
                mode = data.get('mode', 'hybrid')
                context = data.get('context', 'general')  # New context parameter for specialized searches
            else:
                # Handle form data
                query = request.form.get('query', '')
                mode = request.form.get('mode', 'hybrid')
                context = request.form.get('context', 'general')
        else:
            # GET request
            query = request.args.get('query', '')
            mode = request.args.get('mode', 'hybrid')
            context = request.args.get('context', 'general')
        
        logger.info(f"API Gemini search requested with query: '{query}', mode: {mode}, context: {context}")
        
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
        
        # Use the same enhanced API status check as in the main route
        # 1. Gemini API Status Check
        gemini_error = None
        if hasattr(gemini_search_controller, 'api_key') and gemini_search_controller.api_key:
            if GEMINI_SEARCH_AVAILABLE:
                gemini_available = True
            else:
                gemini_available = False
                gemini_error = "Gemini library not installed correctly"
        else:
            gemini_available = False
            gemini_error = "Gemini API key not configured or invalid"
            
        # 2. Google Search API Status Check
        google_error = None
        if hasattr(gemini_search_controller, 'google_api_key') and gemini_search_controller.google_api_key:
            # Validate Google API key format
            if len(gemini_search_controller.google_api_key) < 20:
                google_available = False
                google_error = "Google API key too short (should be 20+ characters)"
            elif ' ' in gemini_search_controller.google_api_key:
                google_available = False
                google_error = "Google API key contains spaces"
            elif hasattr(gemini_search_controller, 'search_service') and gemini_search_controller.search_service:
                google_available = True
            else:
                google_available = False
                google_error = "Google Search API client initialization failed"
        else:
            google_available = False
            google_error = "Google API key not configured"
            
        # 3. Check Google CSE ID
        cse_error = None
        if hasattr(gemini_search_controller, 'cse_id') and gemini_search_controller.cse_id:
            if len(gemini_search_controller.cse_id) < 10:
                cse_error = "Google CSE ID too short"
            elif ":" not in gemini_search_controller.cse_id and not gemini_search_controller.cse_id.startswith("0"):
                cse_error = "Google CSE ID has invalid format"
        else:
            cse_error = "Google CSE ID not configured"
            
        # If we have CSE error but no Google error yet, update the Google error
        if cse_error and not google_error:
            google_error = cse_error
            google_available = False
            
        # 4. Determine overall API status
        using_real_apis = gemini_available or google_available
        fallback_mode = None
        
        if using_real_apis:
            if mode == "hybrid":
                if gemini_available and google_available:
                    fallback_mode = None  # Both APIs available for hybrid search
                elif gemini_available:
                    fallback_mode = "Gemini only"  # Fall back to Gemini only
                elif google_available:
                    fallback_mode = "Google only"  # Fall back to Google only
            elif mode == "gemini" and not gemini_available:
                fallback_mode = "Mock results"  # Gemini requested but unavailable
            elif mode == "google" and not google_available:
                fallback_mode = "Mock results"  # Google requested but unavailable
        else:
            fallback_mode = "Mock results"  # No real APIs available
            
        # 5. Comprehensive status message
        status_message = None
        if not using_real_apis:
            status_message = "Using mock results as both APIs are unavailable"
        elif fallback_mode:
            if fallback_mode == "Gemini only":
                status_message = "Google Search API unavailable, using Gemini API only"
            elif fallback_mode == "Google only":
                status_message = "Gemini API unavailable, using Google Search API only"
            else:
                status_message = f"Using fallback mode: {fallback_mode}"
                
        # 6. Create comprehensive API status object
        api_status = {
            "gemini_available": gemini_available,
            "google_available": google_available,
            "using_real_apis": using_real_apis,
            "fallback_active": fallback_mode is not None,
            "fallback_mode": fallback_mode,
            "gemini_error": gemini_error,
            "google_error": google_error,
            "status_message": status_message,
            "search_mode": mode,
            "effective_mode": fallback_mode if fallback_mode else mode
        }
            
        if gemini_available:
            try:
                # Use Gemini search controller
                # Create an event loop if one is not already running
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Perform the search with Gemini
                search_response = loop.run_until_complete(
                    gemini_search_controller.enhanced_search(
                        query=query,
                        mode=mode,
                        max_results=15
                    )
                )
                
                # Add API status to the response
                search_response["api_status"] = api_status
                
                # Return the search response
                return jsonify(search_response)
            
            except Exception as e:
                logger.error(f"Error in API Gemini search: {str(e)}")
                return jsonify({"error": str(e), "results": [], "api_status": api_status}), 500
        else:
            # Fall back to standard enhanced search
            logger.warning(f"Gemini search not available for API, falling back to standard search")
            search_results = perform_enhanced_search(query, model="hybrid")
            return jsonify({
                "results": search_results.get("results", []),
                "metadata": {
                    "query": query,
                    "enhanced_query": query,
                    "source": "traditional",
                    "result_count": len(search_results.get("results", [])),
                    "api_status": "fallback"
                },
                "query_analysis": "Standard search analysis (Gemini not available)",
                "api_status": api_status
            })
    
    except Exception as e:
        logger.error(f"Error in API Gemini search route: {str(e)}")
        # Create an enhanced API error status
        error_api_status = {
            "gemini_available": False,
            "google_available": False,
            "using_real_apis": False,
            "fallback_active": True,
            "fallback_mode": "Error mode",
            "gemini_error": "API Search route encountered an error",
            "google_error": "API Search route encountered an error",
            "status_message": "An error occurred in the API search process",
            "search_mode": mode if 'mode' in locals() else "hybrid",
            "effective_mode": "Error fallback",
            "error_message": str(e)
        }
        return jsonify({
            "error": str(e), 
            "results": [], 
            "api_status": error_api_status,
            "metadata": {
                "query": query if 'query' in locals() else "",
                "source": "error",
                "execution_time": 0,
                "result_count": 0
            }
        }), 500

# Add a special error handler for 404 errors to help diagnose routing issues
@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 handler with detailed debugging info"""
    logger.error(f"404 error: {str(e)}")
    logger.error(f"Request path: {request.path}")
    logger.error(f"Request headers: {dict(request.headers)}")
    
    # Create a debug response with helpful information
    debug_info = {
        "error": "Page not found",
        "path": request.path,
        "available_routes": [str(rule) for rule in app.url_map.iter_rules()],
        "headers": dict(request.headers),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Return a more helpful 404 page
    return render_template("404.html", debug_info=debug_info), 404

# Set up document upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20MB

def allowed_file(filename):
    """Check if a file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/document-upload')
def document_upload():
    """Document upload page for AI-powered sustainability document analysis"""
    try:
        logger.info("Document upload page requested")
        return render_template("document_upload.html")
    except Exception as e:
        logger.error(f"Error in document upload route: {str(e)}")
        return f"Error loading document upload page: {str(e)}", 500

@app.route('/upload-sustainability-document', methods=['POST'])
def upload_sustainability_document():
    """Handle document upload and processing"""
    try:
        logger.info("Document upload requested")
        
        # Check if document processor is available
        if not DOCUMENT_PROCESSOR_AVAILABLE:
            logger.error("Document processor not available")
            return jsonify({
                'success': False,
                'error': 'Document processing service is currently unavailable'
            }), 500
            
        # Check if file was included in request
        if 'file' not in request.files:
            logger.warning("No file part in request")
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
            
        file = request.files['file']
        
        # Check if a file was selected
        if file.filename == '':
            logger.warning("No file selected")
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
            
        # Check if file is allowed
        if not allowed_file(file.filename):
            logger.warning(f"Invalid file type: {file.filename}")
            return jsonify({
                'success': False,
                'error': 'Invalid file format. Only PDF files are supported.'
            }), 400
            
        # Get OCR option
        use_ocr = request.form.get('use_ocr', 'false').lower() == 'true'
        logger.info(f"Processing document with OCR: {use_ocr}")
        
        # Process the file with our document processor
        result = document_processor.save_uploaded_file(file, use_ocr)
        
        if not result['success']:
            logger.error(f"Error processing document: {result.get('error')}")
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error during document processing')
            }), 500
            
        # Return success response with document ID for the frontend
        return jsonify({
            'success': True,
            'document_id': result['file_info']['saved_name'],
            'page_count': result.get('page_count', 0),
            'word_count': result.get('word_count', 0),
            'text_preview': result.get('preview', '')
        })
        
    except Exception as e:
        logger.error(f"Error in document upload endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/analyze-sustainability-document/<document_id>')
def analyze_sustainability_document(document_id):
    """Analyze a previously uploaded sustainability document"""
    try:
        logger.info(f"Document analysis requested for document: {document_id}")
        
        # Check if document processor is available
        if not DOCUMENT_PROCESSOR_AVAILABLE:
            logger.error("Document processor not available")
            return jsonify({
                'success': False,
                'error': 'Document analysis service is currently unavailable'
            }), 500
            
        # Check if document exists
        filepath = os.path.join(UPLOAD_FOLDER, document_id)
        if not os.path.exists(filepath):
            logger.warning(f"Document not found: {document_id}")
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404
            
        # Get document content (in a real implementation this would be retrieved from a database)
        try:
            result = document_processor.process_document(filepath, use_ocr=False)
            if not result['success']:
                raise Exception(result.get('error', 'Unknown error'))
                
            document_text = result['text']
        except Exception as e:
            logger.error(f"Error retrieving document content: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Error retrieving document content: {str(e)}'
            }), 500
            
        # Analyze the document
        analysis_results = document_processor.analyze_document(document_text)
        
        # Add success flag
        analysis_results['success'] = True
        
        # Extract KPIs for visualization
        kpis = analysis_results.get('numerical_kpis', [])
        if kpis:
            # Generate visualizations for the KPIs
            viz_results = document_processor.generate_sustainability_visualization(kpis)
            if viz_results['success']:
                analysis_results['visualizations'] = viz_results
        
        # Log success
        logger.info(f"Document analysis successful for document: {document_id}")
        logger.info(f"Found {sum(len(metrics) for metrics in analysis_results['metrics_identified'].values())} metrics, " + 
                   f"{sum(analysis_results['frameworks_mentioned'].values())} framework mentions, " +
                   f"{len(analysis_results['numerical_kpis'])} KPIs")
        
        return jsonify(analysis_results)
        
    except Exception as e:
        logger.error(f"Error in document analysis endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
@app.route('/generate-compliance-report/<document_id>', methods=['GET'])
def generate_compliance_report(document_id):
    """Generate a downloadable PDF compliance report for a document"""
    try:
        logger.info(f"Generating compliance report for document {document_id}")
        
        # Create a mock document info if session is not available
        # In a production environment, this would come from a database
        document_info = {
            'id': document_id,
            'name': f'Document {document_id}',
            'page_count': 25,
            'upload_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'file_type': 'PDF'
        }
        
        # In a real implementation, we would retrieve the saved compliance assessment
        # Here we generate a mock one for demo purposes
        compliance_assessment = {
            'overall_compliance': 'Partially compliant',
            'overall_score': 68.5,
            'framework_scores': {
                'CSRD': 75.0,
                'SEC': 62.5,
                'IFRS': 80.0,
                'GRI': 85.0,
                'GDPR': 40.0
            },
            'key_recommendations': [
                'Enhance CSRD compliance with more detailed metrics on double materiality',
                'Improve climate risk disclosures to meet SEC requirements',
                'Add data privacy protection measures in sustainability reporting',
                'Include more quantitative metrics for biodiversity impacts'
            ],
            'full_report': {
                'compliance_results': {
                    'CSRD': {
                        'compliance_level': 'Moderate',
                        'risk_level': 'Medium',
                        'requirements': [
                            {'description': 'Double materiality assessment', 'satisfied': True},
                            {'description': 'Scope 3 emissions reporting', 'satisfied': False},
                            {'description': 'Biodiversity impact disclosure', 'satisfied': False}
                        ]
                    },
                    'SEC': {
                        'compliance_level': 'Partial',
                        'risk_level': 'Medium-High',
                        'requirements': [
                            {'description': 'Climate risk disclosure', 'satisfied': True},
                            {'description': 'Financial impact assessment', 'satisfied': False}
                        ]
                    }
                }
            }
        }
            
        # Generate the PDF report
        from frontend.document_processor import DocumentProcessor
        document_processor = DocumentProcessor()
        report_path = document_processor.generate_compliance_report(
            compliance_assessment, 
            document_info
        )
        
        if not report_path:
            return jsonify({
                'success': False,
                'error': 'Failed to generate compliance report. Please try again.'
            }), 500
            
        return jsonify({
            'success': True,
            'report_url': report_path,
            'filename': os.path.basename(report_path)
        })
        
    except Exception as e:
        logger.error(f"Error generating compliance report: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error generating report: {str(e)}'
        }), 500

@app.route('/api/integrated-search', methods=['GET', 'POST'])
def api_integrated_search():
    """
    API endpoint for integrated search within the dashboard
    Used for AJAX requests from the unified dashboard's search functionality
    Provides contextual search results for different dashboard components
    """
    try:
        # Handle both GET and POST requests
        if request.method == 'POST':
            if request.is_json:
                data = request.get_json()
                query = data.get('query', '')
                context = data.get('context', 'realestate')
                component = data.get('component', 'all') # Which dashboard component to update
            else:
                query = request.form.get('query', '')
                context = request.form.get('context', 'realestate')
                component = request.form.get('component', 'all')
        else:
            query = request.args.get('query', '')
            context = request.args.get('context', 'realestate')
            component = request.args.get('component', 'all')
        
        logger.info(f"Integrated search requested with query: '{query}', context: {context}, component: {component}")
        
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
            
        # Use Gemini search with real estate context
        try:
            # Create an event loop if one is not already running
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Use special mode for real estate context
            mode = "hybrid"
            
            # Perform the search with Gemini
            if GEMINI_SEARCH_AVAILABLE:
                search_response = loop.run_until_complete(
                    gemini_search_controller.enhanced_search(
                        query=query,
                        mode=mode,
                        max_results=15
                    )
                )
            else:
                # Fallback to standard search
                search_results = perform_enhanced_search(query, model="hybrid")
                search_response = {
                    "results": search_results.get("results", []),
                    "metadata": {
                        "query": query,
                        "enhanced_query": query,
                        "source": "traditional",
                        "result_count": len(search_results.get("results", [])),
                    },
                    "query_analysis": "Standard search analysis"
                }
                
            # Process results based on context and component
            # Prepare appropriate updates for each dashboard component
            updates = prepare_dashboard_updates(query, search_response, context, component)
            
            # Return the integrated response with UI updates
            return jsonify({
                "success": True,
                "query": query,
                "updates": updates,
                "results_count": len(search_response.get("results", [])),
                "timestamp": datetime.now().isoformat()
            })
        
        except Exception as e:
            logger.error(f"Error in integrated search: {str(e)}")
            return jsonify({"error": str(e), "success": False}), 500
    
    except Exception as e:
        logger.error(f"Error in integrated search route: {str(e)}")
        return jsonify({"error": str(e), "success": False}), 500

def prepare_dashboard_updates(query, search_response, context, component):
    """
    Process search results and prepare UI updates for dashboard components
    """
    updates = {}
    results = search_response.get("results", [])
    
    # Process results based on components requested
    if component == "all" or component == "breeam":
        # Prepare BREEAM metrics updates
        breeam_updates = process_breeam_results(query, results)
        updates["breeam"] = breeam_updates
    
    if component == "all" or component == "energy":
        # Prepare energy metrics updates
        energy_updates = process_energy_results(query, results)
        updates["energy"] = energy_updates
    
    if component == "all" or component == "carbon":
        # Prepare carbon footprint updates
        carbon_updates = process_carbon_results(query, results)
        updates["carbon"] = carbon_updates
    
    if component == "all" or component == "financial":
        # Prepare financial impact updates
        financial_updates = process_financial_results(query, results)
        updates["financial"] = financial_updates
    
    if component == "all" or component == "ai":
        # Prepare AI insights updates
        ai_updates = process_ai_insights(query, results, search_response.get("query_analysis", ""))
        updates["ai_insights"] = ai_updates
    
    # Always include a summary update
    summary = process_summary_updates(query, results, context)
    updates["summary"] = summary
    
    return updates

def process_breeam_results(query, results):
    """Process search results for BREEAM metrics updates"""
    # Extract relevant BREEAM information from results
    breeam_relevant = [r for r in results if "breeam" in r.get("title", "").lower() or "breeam" in r.get("description", "").lower()]
    
    if not breeam_relevant:
        return {
            "has_updates": False,
            "message": "No BREEAM-specific information found for your query."
        }
    
    # In a real implementation, this would extract structured data
    categories = ["management", "health", "energy", "transport", "water", "materials", "waste", "landuse", "pollution", "innovation"]
    highlighted_categories = []
    
    for result in breeam_relevant[:3]:
        content = result.get("description", "").lower()
        for category in categories:
            if category in content and category not in highlighted_categories:
                highlighted_categories.append(category)
    
    return {
        "has_updates": True,
        "highlighted_categories": highlighted_categories,
        "results": breeam_relevant[:3]
    }

def process_energy_results(query, results):
    """Process search results for energy efficiency updates"""
    energy_relevant = [r for r in results if any(term in r.get("title", "").lower() or term in r.get("description", "").lower() 
                                               for term in ["energy", "efficiency", "epc", "consumption", "power", "electricity"])]
    
    if not energy_relevant:
        return {
            "has_updates": False,
            "message": "No energy efficiency information found for your query."
        }
    
    return {
        "has_updates": True,
        "results": energy_relevant[:3]
    }

def process_carbon_results(query, results):
    """Process search results for carbon footprint updates"""
    carbon_relevant = [r for r in results if any(term in r.get("title", "").lower() or term in r.get("description", "").lower() 
                                               for term in ["carbon", "co2", "emission", "greenhouse", "climate", "footprint"])]
    
    if not carbon_relevant:
        return {
            "has_updates": False,
            "message": "No carbon footprint information found for your query."
        }
    
    return {
        "has_updates": True,
        "results": carbon_relevant[:3]
    }

def process_financial_results(query, results):
    """Process search results for financial impact updates"""
    financial_relevant = [r for r in results if any(term in r.get("title", "").lower() or term in r.get("description", "").lower() 
                                                  for term in ["financial", "cost", "investment", "roi", "return", "value", "saving"])]
    
    if not financial_relevant:
        return {
            "has_updates": False,
            "message": "No financial impact information found for your query."
        }
    
    return {
        "has_updates": True,
        "results": financial_relevant[:3]
    }

def process_ai_insights(query, results, query_analysis):
    """Process search results to generate AI insights"""
    # Determine the insight type based on query
    insight_type = "high"  # Default to high importance
    
    if query and len(results) > 0:
        insight_html = generate_ai_insight_html(query, results, query_analysis)
        return {
            "has_updates": True,
            "insight_html": insight_html,
            "insight_type": insight_type
        }
    else:
        return {
            "has_updates": False,
            "message": "Not enough information to generate AI insights for your query."
        }

def generate_ai_insight_html(query, results, query_analysis):
    """Generate HTML for AI insights based on query and results"""
    # This is a simplified version - in production, this would use more sophisticated AI generation
    
    if "breeam" in query.lower() or any("breeam" in r.get("title", "").lower() for r in results):
        return """
            <div class="ai-insight-card high">
                <div class="ai-insight-header">
                    <div class="ai-insight-title">BREEAM Certification Analysis</div>
                    <span class="badge bg-success">AI-Generated</span>
                </div>
                <div class="ai-insight-body">
                    <p>Your portfolio currently has <strong>28%</strong> of properties with BREEAM certification, with an average score of <strong>72</strong> (Very Good rating).</p>
                    <p>Based on your search for BREEAM information, I've identified these key insights:</p>
                    <ul>
                        <li>Your energy performance is 15% above sector average</li>
                        <li>Water efficiency has potential for 20% improvement</li>
                        <li>Material sustainability scores are in the top quartile</li>
                    </ul>
                    <p>Focusing on water conservation measures could yield the most significant certification improvement.</p>
                </div>
            </div>
        """
    elif any(term in query.lower() for term in ["energy", "efficiency", "epc"]):
        return """
            <div class="ai-insight-card medium">
                <div class="ai-insight-header">
                    <div class="ai-insight-title">Energy Efficiency Analysis</div>
                    <span class="badge bg-success">AI-Generated</span>
                </div>
                <div class="ai-insight-body">
                    <p>Based on your energy efficiency query, our analysis shows:</p>
                    <ul>
                        <li>Your portfolio's average EPC rating is <strong>B</strong>, which is better than 65% of comparable properties</li>
                        <li>Energy consumption has decreased by 12% year-over-year</li>
                        <li>Potential for 15-20% further reduction through targeted upgrades</li>
                    </ul>
                    <p>The most cost-effective improvements would be LED lighting retrofits and HVAC optimization, with average payback periods of 2.5 and 3.7 years respectively.</p>
                </div>
            </div>
        """
    elif any(term in query.lower() for term in ["carbon", "emission", "climate"]):
        return """
            <div class="ai-insight-card high">
                <div class="ai-insight-header">
                    <div class="ai-insight-title">Carbon Footprint Assessment</div>
                    <span class="badge bg-success">AI-Generated</span>
                </div>
                <div class="ai-insight-body">
                    <p>Based on your carbon footprint query, our analysis shows:</p>
                    <ul>
                        <li>Your portfolio's carbon intensity is <strong>32 kgCO₂e/m²</strong>, which is 18% below industry average</li>
                        <li>You've achieved a 23% reduction over the past 3 years</li>
                        <li>Current trajectory aligns with 2030 science-based targets</li>
                    </ul>
                    <p>To further reduce emissions, focus on renewable energy integration (potential 40% reduction) and embodied carbon in renovation materials.</p>
                </div>
            </div>
        """
    else:
        return """
            <div class="ai-insight-card medium">
                <div class="ai-insight-header">
                    <div class="ai-insight-title">Real Estate Sustainability Summary</div>
                    <span class="badge bg-success">AI-Generated</span>
                </div>
                <div class="ai-insight-body">
                    <p>Based on your search, I've analyzed your portfolio's sustainability performance:</p>
                    <ul>
                        <li>Overall sustainability score: <strong>76/100</strong> (top 25% of market)</li>
                        <li>Strongest areas: Energy efficiency, material sustainability</li>
                        <li>Improvement opportunities: Water management, waste reduction</li>
                    </ul>
                    <p>Market trends indicate increasing tenant preference for sustainable properties, with premium rental rates of 8-12% for top-performing buildings.</p>
                </div>
            </div>
        """

def process_summary_updates(query, results, context):
    """Process search results for overall summary updates"""
    # Always return a summary of the search
    return {
        "query": query,
        "result_count": len(results),
        "context": context,
        "top_result": results[0] if results else None
    }

@app.route('/api/sustainability-document-query', methods=['POST'])
def sustainability_document_query():
    """Use RAG to query a sustainability document using natural language"""
    try:
        data = request.json
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No request data provided'
            }), 400
            
        document_id = data.get('document_id')
        query = data.get('query')
        
        # Validate inputs
        if not document_id:
            return jsonify({
                'success': False,
                'error': 'Document ID is required'
            }), 400
            
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
            
        logger.info(f"Document query requested for document: {document_id}, query: {query}")
        
        # Check if document processor is available
        if not DOCUMENT_PROCESSOR_AVAILABLE:
            logger.error("Document processor not available")
            return jsonify({
                'success': False,
                'error': 'Document analysis service is currently unavailable'
            }), 500
            
        # Check if document exists
        filepath = os.path.join(UPLOAD_FOLDER, document_id)
        if not os.path.exists(filepath):
            logger.warning(f"Document not found: {document_id}")
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404
            
        # Get document content
        try:
            result = document_processor.process_document(filepath, use_ocr=False)
            if not result['success']:
                raise Exception(result.get('error', 'Unknown error'))
                
            document_text = result['text']
        except Exception as e:
            logger.error(f"Error retrieving document content: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Error retrieving document content: {str(e)}'
            }), 500
            
        # Generate RAG response
        rag_result = document_processor.generate_rag_response(document_text, query)
        
        # Log success
        logger.info(f"Document query successful for document: {document_id}")
        
        return jsonify(rag_result)
        
    except Exception as e:
        logger.error(f"Error in document query endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == "__main__":
    # Use the PORT environment variable provided by Replit, or default to 5000
    port = int(os.environ.get("PORT", 5000))

    # Log registered routes for debugging
    routes = [str(rule) for rule in app.url_map.iter_rules()]
    logger.info(f"Registered routes: {routes}")
    logger.info(f"Starting Flask server on port {port}")

    # Start the Flask app with the correct host and port
    app.run(host="0.0.0.0", port=port, debug=True)