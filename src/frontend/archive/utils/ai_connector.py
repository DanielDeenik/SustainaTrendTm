"""
AI Connector Module for SustainaTrend™

This module provides a unified interface for AI services used across the platform,
including generative AI models, embeddings, and vector databases for RAG systems.
"""

import json
import logging
import os
import sys
from typing import Dict, List, Any, Optional, Tuple, Union
import time
import uuid

# Set up logging
logger = logging.getLogger(__name__)

#############################################
# Generative AI Configuration
#############################################

# Gemini API
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GEMINI_AVAILABLE = True
    
    # Configure Gemini API (best-effort)
    api_key = os.environ.get('GOOGLE_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        logger.info("Configured Google Generative AI with provided API key")
    else:
        logger.warning("Google API key not found in environment, Gemini features will be limited")
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI package not available, using fallback")

# OpenAI API
try:
    import openai
    OPENAI_AVAILABLE = True
    
    # Configure OpenAI API (best-effort)
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key:
        openai.api_key = api_key
        logger.info("Configured OpenAI with provided API key")
    else:
        logger.warning("OpenAI API key not found in environment, OpenAI features will be limited")
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI package not available, using fallback")

#############################################
# Vector Database Configuration
#############################################

# Pinecone for vector storage
try:
    # Try to import Pinecone
    import pinecone
    PINECONE_AVAILABLE = True
    
    # Configure Pinecone (best-effort)
    api_key = os.environ.get('PINECONE_API_KEY')
    if api_key:
        try:
            # Try initializing with Pinecone V3 API
            from pinecone import Pinecone, ServerlessSpec
            pc = Pinecone(api_key=api_key)
            # Check if we have an index
            indexes = pc.list_indexes()
            logger.info(f"Successfully connected to Pinecone with V3 API")
            logger.info(f"Available indexes: {[idx.name for idx in indexes]}")
            PINECONE_V3 = True
        except (ImportError, AttributeError) as e:
            # Fall back to Pinecone V2 API
            logger.info(f"Falling back to Pinecone V2 API: {e}")
            pinecone.init(api_key=api_key)
            indexes = pinecone.list_indexes()
            logger.info(f"Successfully connected to Pinecone with V2 API")
            logger.info(f"Available indexes: {indexes}")
            PINECONE_V3 = False
    else:
        logger.warning("Pinecone API key not found in environment, vector search features will be limited")
except ImportError:
    PINECONE_AVAILABLE = False
    logger.warning("Pinecone package not available, using in-memory vector search fallback")

# In-memory vector database fallback
class InMemoryVectorDB:
    """Simple in-memory vector database for fallback when Pinecone is not available"""
    
    def __init__(self):
        """Initialize in-memory vector database"""
        self.vectors = {}  # Dictionary to store vectors
        self.metadata = {}  # Dictionary to store metadata
    
    def upsert(self, vectors: List[Tuple[str, List[float], Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Insert or update vectors in the database
        
        Args:
            vectors: List of tuples with (id, vector, metadata)
            
        Returns:
            Status dictionary
        """
        for vec_id, vector, metadata in vectors:
            self.vectors[vec_id] = vector
            self.metadata[vec_id] = metadata
        
        return {"upserted_count": len(vectors)}
    
    def query(self, vector: List[float], filter: Optional[Dict[str, Any]] = None, 
              top_k: int =.5, include_metadata: bool = True) -> Any:
        """
        Query the database with a vector
        
        Args:
            vector: Query vector
            filter: Filter dictionary
            top_k: Number of results to return
            include_metadata: Whether to include metadata
            
        Returns:
            Query results
        """
        # Simple cosine similarity implementation
        def cosine_similarity(vec1, vec2):
            # Dot product
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            # Magnitudes
            mag1 = sum(a * a for a in vec1) ** 0.5
            mag2 = sum(b * b for b in vec2) ** 0.5
            # Avoid division by zero
            if mag1 * mag2 == 0:
                return 0
            return dot_product / (mag1 * mag2)
        
        # Calculate similarities
        similarities = []
        for vec_id, stored_vector in self.vectors.items():
            # Skip if doesn't match filter
            if filter:
                metadata = self.metadata.get(vec_id, {})
                match = True
                for key, value in filter.items():
                    if key not in metadata or metadata[key] != value:
                        match = False
                        break
                if not match:
                    continue
            
            # Calculate similarity
            similarity = cosine_similarity(vector, stored_vector)
            similarities.append((vec_id, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top k results
        class ResultMatch:
            def __init__(self, id, score, metadata=None):
                self.id = id
                self.score = score
                self.metadata = metadata
        
        class QueryResult:
            def __init__(self, matches):
                self.matches = matches
        
        matches = []
        for i, (vec_id, score) in enumerate(similarities[:top_k]):
            match = ResultMatch(vec_id, score)
            if include_metadata:
                match.metadata = self.metadata.get(vec_id, {})
            matches.append(match)
        
        return QueryResult(matches)
    
    def delete(self, ids: Optional[List[str]] = None, filter: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Delete vectors from the database
        
        Args:
            ids: List of vector ids to delete
            filter: Filter dictionary
            
        Returns:
            Status dictionary
        """
        deleted_count = 0
        
        if ids:
            for vec_id in ids:
                if vec_id in self.vectors:
                    del self.vectors[vec_id]
                    del self.metadata[vec_id]
                    deleted_count += 1
        
        if filter:
            to_delete = []
            for vec_id, metadata in self.metadata.items():
                match = True
                for key, value in filter.items():
                    if key not in metadata or metadata[key] != value:
                        match = False
                        break
                if match:
                    to_delete.append(vec_id)
            
            for vec_id in to_delete:
                del self.vectors[vec_id]
                del self.metadata[vec_id]
                deleted_count += 1
        
        return {"deleted_count": deleted_count}

# Singleton instance of in-memory vector DB
in_memory_vectordb = InMemoryVectorDB()

#############################################
# Core Functions
#############################################

def get_generative_ai() -> Any:
    """
    Get the best available generative AI model
    
    Returns:
        AI model interface
    """
    if GEMINI_AVAILABLE:
        try:
            # List available models
            try:
                models = genai.list_models()
                model_names = [m.name for m in models]
                logger.info(f"Available Gemini models: {model_names}")
                
                # Choose the best available model
                preferred_models = [
                    "models/gemini-1.5-pro", 
                    "models/gemini-1.5-flash", 
                    "models/gemini-pro", 
                    "models/gemini-1.0-pro"
                ]
                
                # Try to use models with latest suffix first
                for base_model in preferred_models:
                    for model_name in model_names:
                        if model_name.startswith(base_model):
                            logger.info(f"Using Gemini model: {model_name}")
                            return genai.GenerativeModel(model_name)
                
                # Fall back to regular models if not found
                for model in preferred_models:
                    if model in model_names:
                        logger.info(f"Using Gemini model: {model}")
                        return genai.GenerativeModel(model)
                
                # Default to any generative model
                logger.info(f"Using default Gemini model: gemini-pro")
                return genai.GenerativeModel("gemini-pro")
                
            except Exception as e:
                logger.warning(f"Error listing Gemini models: {str(e)}")
                logger.info("Using default Gemini model: gemini-pro")
                return genai.GenerativeModel("gemini-pro")
        
        except Exception as e:
            logger.warning(f"Error initializing Gemini: {str(e)}")
    
    if OPENAI_AVAILABLE:
        try:
            logger.info("Using OpenAI as fallback")
            
            class OpenAIWrapper:
                def generate_content(self, prompt):
                    response = openai.Completion.create(
                        model="gpt-3.5-turbo-instruct",
                        prompt=prompt,
                        max_tokens=1000
                    )
                    # Wrap response to match Gemini format
                    class TextResponse:
                        def __init__(self, text):
                            self.text = text
                    
                    return TextResponse(response.choices[0].text)
            
            return OpenAIWrapper()
            
        except Exception as e:
            logger.warning(f"Error initializing OpenAI: {str(e)}")
    
    # Fallback to mock AI
    logger.warning("No AI services available, using mock AI")
    
    class MockAI:
        def generate_content(self, prompt):
            class MockResponse:
                def __init__(self):
                    self.text = json.dumps({
                        "message": "Mock AI response - no AI service available",
                        "prompt_length": len(prompt),
                        "error": "No AI service is currently available. Please configure a valid API key."
                    })
            
            return MockResponse()
    
    return MockAI()

def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for text
    
    Args:
        text: Text to embed
        
    Returns:
        Embedding vector
    """
    if OPENAI_AVAILABLE:
        try:
            # OpenAI embeddings
            response = openai.Embedding.create(
                model="text-embedding-3-small",
                input=text
            )
            return response['data'][0]['embedding']
        except Exception as e:
            logger.warning(f"Error generating OpenAI embedding: {str(e)}")
    
    if GEMINI_AVAILABLE:
        try:
            # Try to use Embeddings API if available
            embedding_model = "models/embedding-001"
            result = genai.embed_content(
                model=embedding_model,
                content=text,
                task_type="retrieval_document"
            )
            return result["embedding"]
        except Exception as e:
            logger.warning(f"Error generating Gemini embedding: {str(e)}")
    
    # Fallback to simple hashing-based vector
    logger.warning("No embedding service available, using fallback hash-based embedding")
    return simple_hash_embedding(text)

def simple_hash_embedding(text: str, dim: int = 1536) -> List[float]:
    """
    Generate a simple hash-based embedding for fallback use
    
    Args:
        text: Text to embed
        dim: Dimensionality of the embedding
        
    Returns:
        A simple embedding vector
    """
    import hashlib
    from math import sin, cos
    
    # Normalize the text
    text = text.lower().strip()
    
    # Generate a base hash
    text_hash = hashlib.sha256(text.encode()).digest()
    
    # Create a vector of the specified dimension
    vector = []
    for i in range(dim):
        # Use different parts of the hash for different dimensions
        byte_idx = i % len(text_hash)
        value = text_hash[byte_idx] / 255.0  # Normalize to 0-1
        
        # Apply a transformation to distribute values
        if i % 3 == 0:
            value = sin(value * 6.28)
        elif i % 3 == 1:
            value = cos(value * 6.28)
        
        vector.append(value)
    
    # Normalize the vector to unit length
    magnitude = sum(v*v for v in vector) ** 0.5
    if magnitude > 0:
        vector = [v/magnitude for v in vector]
    
    return vector

def get_rag_system():
    """
    Get RAG system interface
    
    Returns:
        RAG system interface
    """
    if PINECONE_AVAILABLE:
        api_key = os.environ.get('PINECONE_API_KEY')
        if api_key:
            try:
                index_name = get_index_name()
                
                if PINECONE_V3:
                    # Pinecone V3 API
                    from pinecone import Pinecone
                    pc = Pinecone(api_key=api_key)
                    
                    # Check if index exists
                    indexes = pc.list_indexes()
                    if index_name not in [idx.name for idx in indexes]:
                        # Create the index
                        logger.info(f"Creating Pinecone index {index_name} with V3 API")
                        from pinecone import ServerlessSpec
                        pc.create_index(
                            name=index_name,
                            dimension=3072,  # OpenAI text-embedding-3-small
                            metric="cosine",
                            spec=ServerlessSpec(cloud="aws", region="us-east-1")
                        )
                        # Wait for index to be ready
                        while index_name not in [idx.name for idx in pc.list_indexes()]:
                            time.sleep(1)
                    
                    # Get the index
                    index = pc.Index(index_name)
                    logger.info(f"Successfully connected to Pinecone index '{index_name}' with V3 API")
                    return index
                
                else:
                    # Pinecone V2 API
                    # Check if index exists
                    if index_name not in pinecone.list_indexes():
                        # Create the index
                        logger.info(f"Creating Pinecone index {index_name} with V2 API")
                        pinecone.create_index(
                            name=index_name,
                            dimension=3072,  # OpenAI text-embedding-3-small
                            metric="cosine"
                        )
                        # Wait for index to be ready
                        while not pinecone.describe_index(index_name).status['ready']:
                            time.sleep(1)
                    
                    # Get the index
                    index = pinecone.Index(index_name)
                    logger.info(f"Successfully connected to Pinecone index '{index_name}' with V2 API")
                    return index
            
            except Exception as e:
                logger.error(f"Error connecting to Pinecone: {str(e)}")
    
    # Fallback to in-memory vector database
    logger.warning("Using in-memory vector database fallback")
    return in_memory_vectordb

def get_index_name() -> str:
    """Get the name of the current Pinecone index"""
    return os.environ.get('PINECONE_INDEX', 'regulatoryai')

def is_pinecone_available() -> bool:
    """
    Check if Pinecone is available
    
    Returns:
        Boolean indicating if Pinecone is available
    """
    if not PINECONE_AVAILABLE:
        return False
    
    api_key = os.environ.get('PINECONE_API_KEY')
    if not api_key:
        return False
    
    try:
        index_name = get_index_name()
        
        if PINECONE_V3:
            # Pinecone V3 API
            from pinecone import Pinecone
            pc = Pinecone(api_key=api_key)
            indexes = pc.list_indexes()
            index_names = [idx.name for idx in indexes]
            logger.info(f"Successfully connected to Pinecone index '{index_name}' with V3 API")
            return True
        else:
            # Pinecone V2 API
            pinecone.init(api_key=api_key)
            indexes = pinecone.list_indexes()
            logger.info(f"Successfully connected to Pinecone with V2 API")
            return True
            
    except Exception as e:
        logger.error(f"Error checking Pinecone availability: {str(e)}")
        return False