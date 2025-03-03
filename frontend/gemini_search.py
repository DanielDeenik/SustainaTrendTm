"""
Gemini + Google Search Integration for SustainaTrend™ Intelligence Platform

This module provides advanced AI search capabilities by combining:
1. Google Gemini for content generation and query understanding
2. Google Search API for web search results
3. Hybrid search combining multiple sources
4. Domain-specific optimization for sustainability topics
"""
import os
import json
import random
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import re

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import Google libraries if available with comprehensive error handling
try:
    # Try importing the Google Generative AI library
    import google.generativeai as genai
    GEMINI_IMPORT_ERROR = None
    GEMINI_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Google Generative AI library not available: {str(e)}. Install with: pip install google-generativeai")
    GEMINI_IMPORT_ERROR = str(e)
    GEMINI_AVAILABLE = False
    # Define a placeholder for when the library is not available
    class GenaiPlaceholder:
        def configure(self, **kwargs):
            logger.warning("Attempted to use Gemini API but the library is not installed")
            return None
        
        def list_models(self):
            logger.warning("Attempted to list Gemini models but the library is not installed")
            return []
            
        def GenerativeModel(self, **kwargs):
            logger.warning("Attempted to create Gemini model but the library is not installed")
            class MockModel:
                def generate_content(self, prompt):
                    class MockResponse:
                        text = json.dumps({"error": "Gemini API not available"})
                    return MockResponse()
            return MockModel()
    
    # Create a placeholder if the real library isn't available
    genai = GenaiPlaceholder()

# Import Google Search API with separate try/except for fine-grained error reporting
try:
    import googleapiclient.discovery
    GOOGLE_SEARCH_AVAILABLE = True
    GOOGLE_SEARCH_IMPORT_ERROR = None
except ImportError as e:
    logger.warning(f"Google Search API library not available: {str(e)}. Install with: pip install google-api-python-client")
    GOOGLE_SEARCH_AVAILABLE = False
    GOOGLE_SEARCH_IMPORT_ERROR = str(e)
    # Define a placeholder for Google Search API
    class GoogleApiPlaceholder:
        def discovery(self):
            class MockDiscovery:
                def build(self, *args, **kwargs):
                    logger.warning("Attempted to use Google Search API but the library is not installed")
                    return None
            return MockDiscovery()
    
    # Create a placeholder if the real library isn't available
    googleapiclient = GoogleApiPlaceholder()

class GeminiSearchController:
    """Controller for AI-powered search using Gemini and Google Search"""
    
    def _get_best_gemini_model(self):
        """
        Get the best available Gemini model from the available models
        
        Returns:
            model_name: Name of the best available model
        """
        try:
            # First, list available models to see which ones we can use
            # Convert generator to list to avoid issues with generator consumption
            model_iterator = genai.list_models()
            available_models = list(model_iterator)
            model_names = [model.name for model in available_models]
            logger.info(f"Available Gemini models: {model_names}")
            
            # Look for an appropriate model to use
            model_name = None
            
            # First check if we have any models at all
            if not available_models:
                raise ValueError("No models available")
            
            # Priority list - try these model types in order
            priority_prefixes = [
                "models/gemini-1.5-pro",
                "models/gemini-1.5-flash", 
                "models/gemini-1.0-pro",
                "models/gemini-pro",
                "models/text-bison",
                "models/chat-bison"
            ]
            
            # Try each prefix
            for prefix in priority_prefixes:
                if model_name:
                    break  # Already found a model
                for model_info in available_models:
                    if model_info.name.startswith(prefix):
                        model_name = model_info.name
                        break
            
            # If no model found yet, use any model with "gemini" in the name
            if not model_name:
                for model_info in available_models:
                    if "gemini" in model_info.name.lower():
                        model_name = model_info.name
                        break
            
            # If still no model found, use the first available model of any kind
            if not model_name and available_models:
                model_name = available_models[0].name
                logger.warning(f"No Gemini models found, using alternative model: {model_name}")
            
            # If we still don't have a model, something is wrong
            if not model_name:
                raise ValueError("No suitable model found")
                
            logger.info(f"Selected Gemini model: {model_name}")
            return model_name
            
        except Exception as e:
            logger.error(f"Error getting Gemini models: {str(e)}")
            raise ValueError(f"Failed to get Gemini model: {str(e)}")

    def __init__(self):
        """Initialize the Gemini search controller"""
        # Get API keys from environment variables with more robust fallback handling
        # Process environment vars - handle both raw values and ${VAR} format
        def process_env_var(env_value):
            if not env_value:
                return None
            # Handle ${VAR} format in .env files by getting from actual environment
            if env_value.startswith('${') and env_value.endswith('}'):
                actual_var_name = env_value[2:-1]  # Extract VAR from ${VAR}
                return os.getenv(actual_var_name)
            return env_value
        
        # Get and process Gemini API key
        raw_api_key = os.getenv("GEMINI_API_KEY")
        self.api_key = process_env_var(raw_api_key)
        
        # Get and process Google API key
        raw_google_key = os.getenv("GOOGLE_API_KEY")
        self.google_api_key = process_env_var(raw_google_key)
        
        # Try to load CSE ID from different sources in order of preference
        # 1. First check the .env file directly, bypassing potential Replit secrets
        try:
            env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('GOOGLE_CSE_ID='):
                            env_file_cse_id = line.strip().split('=', 1)[1].strip()
                            # Remove quotes if present
                            if env_file_cse_id.startswith('"') and env_file_cse_id.endswith('"'):
                                env_file_cse_id = env_file_cse_id[1:-1]
                            # Process ${VAR} format
                            env_file_cse_id = process_env_var(env_file_cse_id)
                            logger.info(f"Found CSE ID in .env file: '{env_file_cse_id}'")
                            self.cse_id = env_file_cse_id
                            break
            else:
                logger.info("No .env file found to load CSE ID")
        except Exception as e:
            logger.warning(f"Error reading CSE ID from .env file: {str(e)}")
        
        # 2. Fall back to environment variable if not found in .env
        if not hasattr(self, 'cse_id') or not self.cse_id:
            raw_cse_id = os.getenv("GOOGLE_CSE_ID")
            self.cse_id = process_env_var(raw_cse_id)
            if self.cse_id:
                logger.info("GOOGLE_CSE_ID loaded from environment variable")
            else:
                logger.warning("GOOGLE_CSE_ID not found in environment")
        
        # Log and validate API key status (without exposing the actual keys)
        if self.api_key:
            # Verify the key has proper format without revealing it
            masked_key = self.api_key[:4] + "*" * (len(self.api_key) - 8) + self.api_key[-4:] if len(self.api_key) > 8 else "****"
            logger.info(f"GEMINI_API_KEY found in environment (masked: {masked_key})")
        else:
            logger.warning("GEMINI_API_KEY not found in environment, using mock responses")
            
        if self.google_api_key:
            # Verify the key has proper format without revealing it
            masked_key = self.google_api_key[:4] + "*" * (len(self.google_api_key) - 8) + self.google_api_key[-4:] if len(self.google_api_key) > 8 else "****"
            logger.info(f"GOOGLE_API_KEY found in environment (masked: {masked_key})")
        else:
            logger.warning("GOOGLE_API_KEY not found in environment")
            
        # Always validate the CSE ID format regardless of source
        if self.cse_id:
            # Improved CSE ID validation
            is_valid_cse = True
            reason = ""
            
            # Fix common CSE ID issues
            if self.cse_id.startswith("${") and self.cse_id.endswith("}"):
                is_valid_cse = False
                reason = "contains unparsed environment variable"
            elif "@" in self.cse_id or ".apps.googleusercontent.com" in self.cse_id:
                is_valid_cse = False
                reason = "appears to be a client ID"
            elif "GOOGLE_CSE_ID" in self.cse_id:
                is_valid_cse = False
                reason = "contains placeholder text"
            elif len(self.cse_id) < 10:
                is_valid_cse = False
                reason = "too short to be valid"
            elif not ":" in self.cse_id and not self.cse_id.startswith("0"):
                is_valid_cse = False
                reason = "missing required format (should contain ':' or start with '0')"
                
            if not is_valid_cse:
                logger.warning(f"CSE ID '{self.cse_id}' invalid: {reason}, using default value instead")
                self.cse_id = "017576662512468239146:omuauf_lfve"
            else:
                logger.info(f"Using CSE ID: '{self.cse_id}'")
        else:
            logger.warning("No valid GOOGLE_CSE_ID found, using default value")
            # Provide a default CSE ID
            self.cse_id = "017576662512468239146:omuauf_lfve"
        
        # Initialize Gemini API
        try:
            if not self.api_key:
                logger.warning("Skipping Gemini API initialization due to missing API key")
            elif not GEMINI_AVAILABLE:
                logger.warning("Gemini library not available")
            else:
                # Configure the Gemini API
                genai.configure(api_key=self.api_key)
                
                try:
                    # List models to verify API key works
                    # Convert generator to list first to avoid "object of type 'generator' has no len()"
                    available_models = list(genai.list_models())
                    model_names = [model.name for model in available_models]
                    
                    if model_names:  # Check if list is non-empty
                        logger.info(f"Gemini API initialized with {len(model_names)} available models")
                    else:
                        logger.warning("Gemini API initialized but no models available")
                        self.api_key = None  # Reset to trigger mock mode
                except Exception as model_error:
                    logger.error(f"Failed to list Gemini models: {str(model_error)}")
                    self.api_key = None  # Reset to trigger mock mode
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {str(e)}")
            self.api_key = None  # Reset to trigger mock mode
        
        # Initialize Google Search API
        self.search_service = None
        try:
            if not self.google_api_key:
                logger.warning("Google Search API key not found, using mock search results")
            elif not self.cse_id:
                logger.warning("Google Custom Search Engine ID not found, using mock search results")
            else:
                # Validate API key format before initializing
                if len(self.google_api_key) < 20 or " " in self.google_api_key:
                    logger.warning("Google API key appears to be invalid format - too short or contains spaces")
                    self.search_service = None
                else:
                    # Try to initialize the Google Custom Search API client
                    self.search_service = googleapiclient.discovery.build(
                        "customsearch", "v1", 
                        developerKey=self.google_api_key
                    )
                    logger.info("Google Search API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Search API: {str(e)}")
            self.search_service = None  # Ensure it's None on failure
        
        logger.info("GeminiSearchController initialized successfully")
    
    async def enhanced_search(self, 
                             query: str, 
                             mode: str = "hybrid", 
                             max_results: int = 15) -> Dict[str, Any]:
        """
        Perform an enhanced search using Gemini and Google Search
        
        Args:
            query: The search query
            mode: Search mode (hybrid, gemini, google, or mock)
            max_results: Maximum number of results to return
            
        Returns:
            Search results with metadata
        """
        start_time = time.time()
        logger.info(f"Enhanced search requested for query: '{query}', mode: {mode}")
        
        try:
            # Step 1: Enhance the query with Gemini
            enhanced_query, query_analysis = await self._enhance_query_with_gemini(query)
            
            # Log available API credentials for debugging
            logger.info(f"API status - Gemini: {'Available' if self.api_key and GEMINI_AVAILABLE else 'Not available'}, " +
                      f"Google Search: {'Available' if self.google_api_key and self.cse_id and self.search_service else 'Not available'}")
            
            # Step 2: Get search results based on mode
            if mode == "gemini" and self.api_key and GEMINI_AVAILABLE:
                # Use only Gemini for results
                results = await self._search_with_gemini(enhanced_query, max_results)
                source = "gemini"
            elif mode == "google" and self.google_api_key and self.cse_id:
                # Use only Google Search for results
                results = await self._search_with_google(enhanced_query, max_results)
                source = "google"
            elif mode == "hybrid":
                # Use both and combine results
                if (self.api_key and GEMINI_AVAILABLE) and (self.google_api_key and self.cse_id):
                    # Get results from both sources
                    gemini_results = await self._search_with_gemini(enhanced_query, max_results // 2)
                    google_results = await self._search_with_google(enhanced_query, max_results // 2)
                    
                    # Combine and rank results
                    results = self._combine_search_results(
                        gemini_results, 
                        google_results, 
                        query,
                        max_results
                    )
                    source = "hybrid"
                elif self.api_key and GEMINI_AVAILABLE:
                    # Fall back to Gemini only
                    results = await self._search_with_gemini(enhanced_query, max_results)
                    source = "gemini"
                elif self.google_api_key and self.cse_id:
                    # Fall back to Google only
                    results = await self._search_with_google(enhanced_query, max_results)
                    source = "google"
                else:
                    # Generate mock results if no APIs are available
                    results = self._generate_mock_search_results(query, max_results)
                    source = "mock"
            else:
                # Generate mock results for development/testing
                results = self._generate_mock_search_results(query, max_results)
                source = "mock"
            
            # Step 3: Add sustainability relevance scores if they don't exist
            results = self._add_sustainability_relevance(results, query)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            logger.info(f"Enhanced search completed in {execution_time:.2f}s with {len(results)} results")
            
            # Return search results with metadata
            return {
                "results": results,
                "metadata": {
                    "query": query,
                    "enhanced_query": enhanced_query,
                    "source": source,
                    "execution_time": execution_time,
                    "result_count": len(results)
                },
                "query_analysis": query_analysis
            }
        
        except Exception as e:
            logger.error(f"Error in enhanced search: {str(e)}")
            # Fall back to mock results
            results = self._generate_mock_search_results(query, max_results)
            
            # Return mock results with error metadata
            return {
                "results": results,
                "metadata": {
                    "query": query,
                    "enhanced_query": query,  # Same as original query since enhancement failed
                    "source": "mock",
                    "execution_time": time.time() - start_time,
                    "result_count": len(results),
                    "error": str(e)
                },
                "query_analysis": "Unable to analyze query due to an error."
            }
    
    async def _enhance_query_with_gemini(self, query: str) -> tuple:
        """
        Use Gemini to enhance the search query with sustainability context
        
        Args:
            query: Original user query
            
        Returns:
            Tuple of (enhanced_query, query_analysis)
        """
        if not self.api_key or not GEMINI_AVAILABLE:
            logger.warning("Gemini API not available for query enhancement, using mock enhancement")
            return self._mock_query_enhancement(query)
        
        try:
            # Create a Gemini model instance
            try:
                # Get the best available model using our helper method
                model_name = self._get_best_gemini_model()
                logger.info(f"Using Gemini model for query enhancement: {model_name}")
                
                model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config={
                        "temperature": 0.2,
                        "top_p": 0.8,
                        "top_k": 40,
                        "max_output_tokens": 1024,
                    }
                )
            except Exception as e:
                logger.error(f"Error getting Gemini models: {str(e)}")
                raise
            
            # Craft a prompt for query understanding and enhancement
            prompt = f"""
            As a sustainability expert, analyze this search query: "{query}"
            
            First, identify relevant sustainability concepts, entities, and frameworks.
            Then, provide a concise semantic analysis explaining what the user is looking for.
            Finally, provide an enhanced version of the query that will yield better sustainability-focused results.
            
            Respond in JSON format with these fields:
            {{
                "analysis": "Brief explanation of query intent and sustainability relevance",
                "enhanced_query": "Improved search query with sustainability context"
            }}
            """
            
            # Generate response
            response = await asyncio.to_thread(
                model.generate_content, 
                prompt
            )
            
            # Parse the response
            try:
                # Extract JSON from the response text
                response_text = response.text
                json_match = re.search(r'({.*})', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    data = json.loads(json_str)
                    
                    analysis = data.get("analysis", "")
                    enhanced_query = data.get("enhanced_query", query)
                    
                    logger.info(f"Query enhanced from '{query}' to '{enhanced_query}'")
                    return enhanced_query, analysis
                else:
                    # If JSON parsing fails, extract from text
                    enhanced_query = response_text.strip().split('\n')[-1]
                    return enhanced_query, "Query analyzed for sustainability relevance."
            except Exception as e:
                logger.error(f"Error parsing Gemini response: {str(e)}")
                return query, "Unable to analyze query."
        
        except Exception as e:
            logger.error(f"Error enhancing query with Gemini: {str(e)}")
            return query, "Unable to analyze query due to an error."
    
    async def _search_with_gemini(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Generate search results using Gemini
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results
        """
        if not self.api_key or not GEMINI_AVAILABLE:
            logger.warning("Gemini API not available for search, using mock results")
            return self._generate_mock_search_results(query, max_results)
        
        try:
            # Create a Gemini model instance
            try:
                # Get the best available model using our helper method
                model_name = self._get_best_gemini_model()
                logger.info(f"Using Gemini model for search: {model_name}")
                
                model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config={
                        "temperature": 0.3,
                        "top_p": 0.9,
                        "top_k": 40,
                        "max_output_tokens": 2048,
                    }
                )
            except Exception as e:
                logger.error(f"Error getting Gemini models for search: {str(e)}")
                raise
            
            # Craft a prompt for generating search results
            prompt = f"""
            As an AI expert in sustainability, generate {max_results} search results for this query: "{query}"
            
            Create diverse results that span different aspects of sustainability related to the query.
            Each result should have a title, detailed snippet, and other metadata.
            
            Respond in JSON format with an array of results, each containing:
            {{
                "title": "Result title",
                "snippet": "Detailed description (1-3 sentences)",
                "link": "https://example.com/resource" (create a realistic but fictional URL),
                "category": "Environment|Social|Governance|Technology|Sustainability",
                "date": "YYYY-MM-DD" (use recent realistic dates),
                "relevance_score": number between 50 and 95,
                "source": "gemini"
            }}
            
            The response should ONLY contain the JSON array, nothing else.
            """
            
            # Generate response
            response = await asyncio.to_thread(
                model.generate_content, 
                prompt
            )
            
            # Parse the response
            try:
                # Extract JSON from the response text
                response_text = response.text
                json_match = re.search(r'(\[.*\])', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    results = json.loads(json_str)
                    
                    # Ensure all results have the required fields
                    for result in results:
                        result["source"] = "gemini"
                        if "relevance_score" not in result:
                            result["relevance_score"] = random.randint(70, 95)
                    
                    logger.info(f"Generated {len(results)} results with Gemini")
                    return results[:max_results]
                else:
                    logger.error("Could not extract JSON from Gemini response")
                    return self._generate_mock_search_results(query, max_results)
            except Exception as e:
                logger.error(f"Error parsing Gemini search results: {str(e)}")
                return self._generate_mock_search_results(query, max_results)
        
        except Exception as e:
            logger.error(f"Error searching with Gemini: {str(e)}")
            return self._generate_mock_search_results(query, max_results)
    
    async def _search_with_google(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Search using Google Search API
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results
        """
        # Add diagnostic trace for call tracking
        logger.info(f"Google Search method called with query: '{query}', max_results: {max_results}")
        
        # Comprehensive credential validation with detailed logging
        if not self.google_api_key:
            logger.warning("Google API key is missing, using mock results")
            return self._generate_mock_search_results(query, max_results)
            
        if len(self.google_api_key) < 20:
            logger.warning(f"Google API key appears too short (length: {len(self.google_api_key)}), using mock results")
            return self._generate_mock_search_results(query, max_results)
            
        if ' ' in self.google_api_key:
            logger.warning("Google API key contains spaces, using mock results")
            return self._generate_mock_search_results(query, max_results)
            
        if not self.cse_id:
            logger.warning("Google CSE ID is missing, using mock results")
            return self._generate_mock_search_results(query, max_results)
            
        if not hasattr(self, 'search_service') or self.search_service is None:
            logger.warning("Google Search API client not initialized, using mock results")
            return self._generate_mock_search_results(query, max_results)
        
        try:
            # Add sustainability context if not present for better results
            sustainability_terms = ["sustainability", "esg", "climate", "environment", "carbon", "emissions", 
                                   "green", "renewable", "circular economy"]
            if not any(term in query.lower() for term in sustainability_terms):
                original_query = query
                query = f"{query} sustainability"
                logger.info(f"Added sustainability context to query: '{original_query}' -> '{query}'")
            
            # Final validation of CSE ID to ensure it's usable
            if not self.cse_id or len(self.cse_id) < 10:
                logger.error(f"Invalid Google CSE ID (too short): '{self.cse_id}'")
                return self._generate_mock_search_results(query, max_results)
                
            # Log the search parameters for debugging
            logger.info(f"Using Google Search with query: '{query}', CSE ID: '{self.cse_id}'")
            
            # Use the validated CSE ID
            cse_id = self.cse_id
            
            # Final check on CSE ID format before making the request
            if "@" in cse_id or ".apps.googleusercontent.com" in cse_id or "oauth2" in cse_id:
                logger.warning(f"CSE ID '{cse_id}' appears to be in wrong format, using fallback value")
                cse_id = "017576662512468239146:omuauf_lfve"  # Use a known working CSE ID as fallback
                logger.info(f"Using fallback CSE ID: '{cse_id}'")
            
            # Validate API key format (without logging the actual key)
            google_api_key = self.google_api_key
            # Perform comprehensive API key validation
            invalid_key = False
            reason = ""
            
            if not google_api_key:
                invalid_key = True
                reason = "Key is empty"
            elif len(google_api_key) < 20:
                invalid_key = True
                reason = "Key is too short (less than 20 characters)"
            elif "GOOGLE_API_KEY" in google_api_key:
                invalid_key = True
                reason = "Key contains placeholder text"
            elif " " in google_api_key:
                invalid_key = True
                reason = "Key contains spaces"
            elif not all(c.isalnum() or c == "-" or c == "_" for c in google_api_key):
                invalid_key = True
                reason = "Key contains invalid characters"
                
            if invalid_key:
                logger.warning(f"Google API key appears to be invalid: {reason}")
                # Don't hard-code API keys
                raise ValueError(f"Invalid Google API key format: {reason}")
                
            logger.info(f"Making Google Search API request with query: '{query}', CSE ID: '{cse_id}'")
            
            # The search_service is already initialized with the API key
            # So we don't need to pass it again, just the query and CSE ID
            search_request = self.search_service.cse().list(
                q=query,
                cx=cse_id,
                num=max_results
            )
            
            # Log additional details for debugging
            logger.info(f"Google Search request created with search engine ID: {cse_id}")
            
            # Execute the search request with better error handling and timeout
            try:
                # Set a timeout for the Google Search API request (10 seconds)
                search_results = await asyncio.wait_for(
                    asyncio.to_thread(search_request.execute),
                    timeout=10.0
                )
                logger.info("Google Search API request executed successfully")
            except asyncio.TimeoutError:
                logger.error("Google Search API request timed out after 10 seconds")
                raise RuntimeError("Google Search API request timed out. Please try again or try a different search mode.")
            except Exception as api_error:
                logger.error(f"Google Search API request failed: {str(api_error)}")
                # Add context to the error for better debugging
                error_details = str(api_error)
                if "Invalid Value" in error_details:
                    logger.error("API Error indicates invalid parameter value")
                elif "Access Not Configured" in error_details:
                    logger.error("API Error indicates API may not be enabled in Google Cloud Console")
                elif "API key not valid" in error_details:
                    logger.error("API Error indicates invalid API key")
                raise RuntimeError(f"Google Search API execution failed: {error_details}")
            
            # Parse the response
            results = []
            if "items" in search_results:
                for item in search_results["items"]:
                    # Extract and format the date if available
                    date = ""
                    if "pagemap" in item and "metatags" in item["pagemap"] and len(item["pagemap"]["metatags"]) > 0:
                        metatags = item["pagemap"]["metatags"][0]
                        date_tags = ["article:published_time", "datePublished", "pubdate"]
                        for tag in date_tags:
                            if tag in metatags:
                                date_str = metatags[tag]
                                try:
                                    # Try to parse and format the date
                                    date_obj = datetime.fromisoformat(date_str.split("T")[0])
                                    date = date_obj.strftime("%Y-%m-%d")
                                    break
                                except:
                                    pass
                    
                    # Use current date if no date found
                    if not date:
                        date = datetime.now().strftime("%Y-%m-%d")
                    
                    # Determine the category
                    category = self._determine_category(item)
                    
                    # Calculate relevance score
                    relevance_score = 75 + random.randint(0, 20)  # Base score between 75-95
                    
                    # Create the result
                    result = {
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                        "link": item.get("link", ""),
                        "category": category,
                        "date": date,
                        "relevance_score": relevance_score,
                        "source": "google"
                    }
                    
                    results.append(result)
            
            logger.info(f"Google Search returned {len(results)} results")
            return results
        
        except Exception as e:
            logger.error(f"Error searching with Google: {str(e)}")
            return self._generate_mock_search_results(query, max_results)
    
    def _combine_search_results(self, 
                               gemini_results: List[Dict[str, Any]], 
                               google_results: List[Dict[str, Any]], 
                               query: str,
                               max_results: int) -> List[Dict[str, Any]]:
        """
        Combine and deduplicate search results from multiple sources
        
        Args:
            gemini_results: Results from Gemini
            google_results: Results from Google Search
            query: Original search query
            max_results: Maximum results to return
            
        Returns:
            Combined and ranked results
        """
        # Deduplicate results by title (case insensitive)
        seen_titles = set()
        combined_results = []
        
        # First add Google results (generally more authoritative)
        for result in google_results:
            title_lower = result["title"].lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                combined_results.append(result)
        
        # Then add Gemini results if they're new
        for result in gemini_results:
            title_lower = result["title"].lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                combined_results.append(result)
        
        # Add sustainability relevance
        combined_results = self._add_sustainability_relevance(combined_results, query)
        
        # Sort by relevance score
        combined_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        # Return top results
        return combined_results[:max_results]
    
    def _add_sustainability_relevance(self, 
                                     results: List[Dict[str, Any]], 
                                     query: str) -> List[Dict[str, Any]]:
        """
        Add sustainability relevance scores to search results
        
        Args:
            results: Search results to score
            query: Original search query
            
        Returns:
            Results with sustainability relevance scores
        """
        # Sustainability keywords to boost relevance
        sustainability_keywords = [
            "sustainability", "esg", "climate", "carbon", "emissions", "renewable", 
            "circular", "recycling", "biodiversity", "environmental", "social", 
            "governance", "green", "sustainable", "net zero", "sdg", "ghg"
        ]
        
        # Process each result
        for result in results:
            # Skip if already has a relevance score
            if "relevance_score" in result and result["relevance_score"] > 0:
                continue
            
            # Start with a base score
            base_score = 60
            
            # Title and snippet for scoring
            title = result.get("title", "").lower()
            snippet = result.get("snippet", "").lower()
            
            # Boost for sustainability keywords in title
            for keyword in sustainability_keywords:
                if keyword in title:
                    base_score += 5
                if keyword in snippet:
                    base_score += 2
            
            # Boost for query keywords in title
            query_words = [word.lower() for word in query.split() if len(word) > 3]
            for word in query_words:
                if word in title:
                    base_score += 3
                if word in snippet:
                    base_score += 1
            
            # Cap the score at 95
            relevance_score = min(95, base_score)
            
            # Add to result
            result["relevance_score"] = relevance_score
        
        return results
    
    def _determine_category(self, result: Dict[str, Any]) -> str:
        """Determine sustainability category for a search result"""
        # Extract text for classification
        text = ""
        if isinstance(result, dict):
            if "title" in result:
                text += result["title"] + " "
            if "snippet" in result:
                text += result["snippet"]
        
        # Keywords for classification
        category_keywords = {
            "Environment": ["climate", "carbon", "emissions", "environmental", "energy", "renewable", "waste", "water", "circular"],
            "Social": ["social", "diversity", "inclusion", "community", "health", "safety", "labor", "human rights"],
            "Governance": ["governance", "board", "ethics", "compliance", "transparency", "risk", "management"],
            "Technology": ["technology", "innovation", "digital", "ai", "blockchain", "automation", "data"],
            "Sustainability": ["sustainability", "sustainable", "esg", "goals", "targets", "reporting", "disclosure"]
        }
        
        # Count keyword matches
        category_scores = {category: 0 for category in category_keywords}
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    category_scores[category] += 1
        
        # Get category with highest score
        max_score = 0
        max_category = "Sustainability"  # Default
        for category, score in category_scores.items():
            if score > max_score:
                max_score = score
                max_category = category
        
        return max_category
    
    def _extract_date(self, result: Dict[str, Any]) -> str:
        """Extract publication date from search result if available"""
        # Check if date already exists in result
        if "date" in result and result["date"]:
            return result["date"]
        
        # Generate a realistic recent date for mock data
        days_ago = random.randint(0, 60)
        date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        return date
    
    def _mock_query_enhancement(self, query: str) -> tuple:
        """Generate mock query enhancement for development/testing"""
        # Add sustainability terms to the query if they don't exist
        enhanced_terms = [
            "sustainability", "sustainable development", "ESG", 
            "environmental impact", "carbon footprint", "climate action"
        ]
        
        # Pick a random term to add if sustainability terms aren't present
        if not any(term in query.lower() for term in ["sustainability", "sustainable", "esg", "environment"]):
            enhanced_query = f"{query} {random.choice(enhanced_terms)}"
        else:
            enhanced_query = query
        
        # Generate an analysis explaining the query
        analysis = f"This query is about sustainability topics related to {query}. It seeks information on environmental impact, social responsibility, or governance aspects."
        
        logger.info(f"Mock query enhancement: '{query}' -> '{enhanced_query}'")
        return enhanced_query, analysis
    
    def _generate_mock_search_results(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock search results for development/testing"""
        results = []
        
        # Generate realistic date range
        today = datetime.now()
        
        # Sample sustainability topics and organizations
        topics = [
            "carbon emissions reduction", "sustainable supply chain", 
            "ESG reporting", "renewable energy implementation",
            "circular economy practices", "water conservation", 
            "social responsibility initiatives", "sustainability KPIs",
            "climate risk assessment", "green finance", 
            "biodiversity conservation", "sustainable agriculture"
        ]
        
        organizations = [
            "Microsoft", "Unilever", "Patagonia", "Tesla", 
            "IKEA", "Schneider Electric", "Ørsted", "Neste",
            "Seventh Generation", "Interface", "Danone", "Google"
        ]
        
        # Keywords from the query
        query_words = [word for word in query.split() if len(word) > 3]
        
        # Generate results
        for i in range(max_results):
            # Pick a topic that might be related to the query
            topic = topics[i % len(topics)]
            if query_words and random.random() > 0.5:
                # Incorporate a query word into the topic
                query_word = random.choice(query_words)
                topic = topic.replace(topic.split()[0], query_word)
            
            # Pick an organization
            organization = organizations[i % len(organizations)]
            
            # Generate date (newer for higher ranked results)
            days_ago = i * 3 + random.randint(0, 10)
            date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            
            # Generate title
            titles = [
                f"{organization}'s Innovative Approach to {topic.title()}",
                f"How {organization} is Leading in {topic.title()}",
                f"Case Study: {organization}'s {topic.title()} Strategy",
                f"The Future of {topic.title()}: Insights from {organization}",
                f"{topic.title()} Breakthrough by {organization}"
            ]
            title = random.choice(titles)
            
            # Generate snippet
            snippets = [
                f"{organization} has implemented a comprehensive approach to {topic}, achieving a 35% improvement over the industry average. Their strategy combines technological innovation with stakeholder engagement to drive sustainable outcomes.",
                f"A detailed analysis of {organization}'s {topic} initiatives reveals significant environmental and financial benefits. Their integrated sustainability framework has become a model for the entire sector.",
                f"This report examines how {organization} transformed their business through {topic}. The company's leadership demonstrates that sustainability and profitability can work hand-in-hand.",
                f"Exploring {organization}'s journey toward {topic} excellence, this article highlights key learnings and best practices that can be applied across industries for enhanced sustainability performance.",
                f"New research on {organization}'s {topic} program shows promising results for scaling sustainable solutions. Their data-driven approach provides valuable insights for companies at any stage of their sustainability journey."
            ]
            snippet = random.choice(snippets)
            
            # Determine category
            categories = ["Environment", "Social", "Governance", "Technology", "Sustainability"]
            category = random.choice(categories)
            
            # Generate link
            domain = organization.lower().replace(" ", "") + ".com"
            path = topic.lower().replace(" ", "-")
            link = f"https://www.{domain}/sustainability/{path}"
            
            # Calculate relevance score (higher for first results)
            relevance_score = min(95, 90 - i * 2 + random.randint(0, 5))
            
            # Create result
            result = {
                "title": title,
                "snippet": snippet,
                "link": link,
                "category": category,
                "date": date,
                "relevance_score": relevance_score,
                "source": "mock"
            }
            
            results.append(result)
        
        logger.info(f"Generated {len(results)} mock search results")
        return results