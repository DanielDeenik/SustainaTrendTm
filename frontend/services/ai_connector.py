"""
AI Connector Service for SustainaTrend™

This module provides unified access to AI services including:
1. OpenAI for text generation and embeddings
2. Google's Generative AI for content generation
3. Pinecone for vector storage and retrieval

The service handles authentication, fallbacks, and unified interfaces.
"""

import json
import logging
import os
import sys
from typing import Dict, List, Any, Optional, Union, Tuple

# Set up logging
logger = logging.getLogger(__name__)

# Global flags for service availability
OPENAI_AVAILABLE = False
GOOGLE_AI_AVAILABLE = False
PINECONE_AVAILABLE = False
PINECONE_INDEX = None

# Try to import OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
    logger.info("OpenAI package is available")
except ImportError:
    logger.warning("OpenAI package not available")

# Try to import Google Generative AI
try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
    logger.info("Google Generative AI package is available")
except ImportError:
    logger.warning("Google Generative AI package not available")

# Try to import Pinecone
try:
    import pinecone
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
    logger.info("Pinecone package is available")
except ImportError:
    logger.warning("Pinecone package not available")

def connect_to_ai_services() -> bool:
    """
    Connect to all available AI services
    
    Returns:
        bool: True if at least one service connected successfully
    """
    global OPENAI_AVAILABLE, GOOGLE_AI_AVAILABLE, PINECONE_AVAILABLE, PINECONE_INDEX
    
    success = False
    
    # Connect to OpenAI if available
    if OPENAI_AVAILABLE:
        try:
            # Use trendsense_openai_api environment variable for consistency
            openai_api_key = os.environ.get("trendsense_openai_api")
            if not openai_api_key:
                # Fall back to OPENAI_API_KEY for backward compatibility
                openai_api_key = os.environ.get("OPENAI_API_KEY")
                
            if openai_api_key:
                openai.api_key = openai_api_key
                # Test the connection
                models = openai.models.list().data
                logger.info("Configured OpenAI with provided API key")
                success = True
            else:
                logger.warning("OpenAI API key not found in environment variables (trendsense_openai_api or OPENAI_API_KEY)")
                OPENAI_AVAILABLE = False
        except Exception as e:
            logger.error(f"Error connecting to OpenAI: {str(e)}")
            OPENAI_AVAILABLE = False
    
    # Connect to Google Generative AI if available
    if GOOGLE_AI_AVAILABLE:
        try:
            google_api_key = os.environ.get("GOOGLE_API_KEY")
            if google_api_key:
                genai.configure(api_key=google_api_key)
                # Test the connection by listing models
                models = genai.list_models()
                logger.info("Configured Google Generative AI with provided API key")
                success = True
            else:
                logger.warning("Google API key not found in environment variables")
                GOOGLE_AI_AVAILABLE = False
        except Exception as e:
            logger.error(f"Error connecting to Google Generative AI: {str(e)}")
            GOOGLE_AI_AVAILABLE = False
    
    # Connect to Pinecone if available
    if PINECONE_AVAILABLE:
        try:
            pinecone_api_key = os.environ.get("PINECONE_API_KEY")
            if pinecone_api_key:
                # Initialize Pinecone with the API key
                pc = Pinecone(api_key=pinecone_api_key)
                
                # List available indexes
                indexes = pc.list_indexes()
                index_names = [index.name for index in indexes]
                logger.info(f"Successfully connected to Pinecone with V3 API")
                logger.info(f"Available indexes: {index_names}")
                
                # Check for the RegulatoryAI index
                if 'regulatoryai' in index_names:
                    PINECONE_INDEX = pc.Index('regulatoryai')
                    logger.info(f"Successfully connected to Pinecone index 'regulatoryai' with V3 API")
                    success = True
                else:
                    logger.warning("Pinecone index 'regulatoryai' not found")
            else:
                logger.warning("Pinecone API key not found in environment variables")
                PINECONE_AVAILABLE = False
        except Exception as e:
            logger.error(f"Error connecting to Pinecone: {str(e)}")
            PINECONE_AVAILABLE = False
    
    return success

def is_openai_available() -> bool:
    """
    Check if OpenAI services are available
    
    Returns:
        bool: True if OpenAI is available
    """
    return OPENAI_AVAILABLE

def is_google_ai_available() -> bool:
    """
    Check if Google Generative AI services are available
    
    Returns:
        bool: True if Google AI is available
    """
    return GOOGLE_AI_AVAILABLE

def is_pinecone_available() -> bool:
    """
    Check if Pinecone services are available
    
    Returns:
        bool: True if Pinecone is available
    """
    return PINECONE_AVAILABLE and PINECONE_INDEX is not None

def get_completion(prompt: str, model: str = "gpt-3.5-turbo") -> Dict[str, Any]:
    """
    Get AI completion for a prompt
    
    Args:
        prompt: The prompt text
        model: Model to use (default: gpt-3.5-turbo)
        
    Returns:
        Dict[str, Any]: Response with text and metadata
    """
    # Try OpenAI first
    if OPENAI_AVAILABLE:
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            return {
                "text": response.choices[0].message.content,
                "provider": "openai",
                "model": model,
                "tokens": response.usage.total_tokens
            }
        except Exception as e:
            logger.error(f"Error getting OpenAI completion: {str(e)}")
    
    # Fall back to Google Generative AI
    if GOOGLE_AI_AVAILABLE:
        try:
            generation_config = {
                "temperature": 0.6,
                "top_p": 0.9,
                "max_output_tokens": 1024,
            }
            
            # Use Gemini Pro model
            model = genai.GenerativeModel(
                model_name="gemini-pro",
                generation_config=generation_config
            )
            
            response = model.generate_content(prompt)
            return {
                "text": response.text,
                "provider": "google",
                "model": "gemini-pro"
            }
        except Exception as e:
            logger.error(f"Error getting Google AI completion: {str(e)}")
    
    # Return an empty response if both failed
    return {
        "text": "AI services are currently unavailable. Please check your API configuration.",
        "provider": "none",
        "error": True
    }

def generate_embedding(text: str) -> List[float]:
    """
    Generate an embedding vector for text
    
    Args:
        text: The text to embed
        
    Returns:
        List[float]: Embedding vector
    """
    if OPENAI_AVAILABLE:
        try:
            response = openai.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating OpenAI embedding: {str(e)}")
    
    # Return a zero vector if embedding fails
    return [0.0] * 1536  # Standard OpenAI embedding size

def semantic_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Perform semantic search using Pinecone
    
    Args:
        query: Search query
        top_k: Number of results to return
        
    Returns:
        List[Dict[str, Any]]: Search results
    """
    if not is_pinecone_available():
        logger.warning("Pinecone is not available for semantic search")
        return []
    
    try:
        # Generate query embedding
        query_embedding = generate_embedding(query)
        
        # Search Pinecone index
        query_response = PINECONE_INDEX.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Format results
        results = []
        for match in query_response.matches:
            results.append({
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata
            })
        
        return results
    except Exception as e:
        logger.error(f"Error performing semantic search: {str(e)}")
        return []

def get_best_ai_model() -> Dict[str, Any]:
    """
    Get the best available AI model across providers
    
    Returns:
        Dict[str, Any]: Best model information
    """
    if OPENAI_AVAILABLE:
        return {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "capabilities": ["completion", "embedding", "chat"]
        }
    elif GOOGLE_AI_AVAILABLE:
        return {
            "provider": "google",
            "model": "gemini-pro",
            "capabilities": ["completion", "chat"]
        }
    else:
        return {
            "provider": "none",
            "model": "none",
            "capabilities": []
        }