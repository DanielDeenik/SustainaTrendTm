"""
AI Connector Module for SustainaTrend™

This module provides a unified interface for connecting to various AI models
and services, supporting the RAG (Retrieval Augmented Generation) system.
"""

import json
import logging
import os
import re
import traceback
from typing import Dict, List, Any, Optional, Union, Tuple
import uuid
from datetime import datetime

# Setup logging
logger = logging.getLogger(__name__)

# Global AI model variables
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GEMINI_AVAILABLE = True
    logger.info("Google Generative AI (Gemini) module loaded successfully")
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI (Gemini) not available")

try:
    import openai
    OPENAI_AVAILABLE = True
    logger.info("OpenAI module loaded successfully")
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available")

try:
    # Try with Pinecone import (supports both V2 and V3 APIs)
    import pinecone
    PINECONE_AVAILABLE = True
    
    # Check if we have V3 API support
    try:
        from pinecone import Pinecone
        PINECONE_V3_AVAILABLE = True
        logger.info("Pinecone module loaded successfully (with V3 API support)")
    except ImportError:
        PINECONE_V3_AVAILABLE = False
        logger.info("Pinecone module loaded successfully (V2 API only)")
except ImportError as e:
    logger.warning(f"Pinecone not available: {str(e)}")
    PINECONE_AVAILABLE = False
    PINECONE_V3_AVAILABLE = False

# Initialize AI services
def initialize_ai_services():
    """Initialize all AI services"""
    logger.info("Initializing AI services")
    
    # Initialize Gemini
    if GEMINI_AVAILABLE:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                logger.info("Gemini AI configured successfully")
                
                # Test model availability
                models = genai.list_models()
                available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
                logger.info(f"Available Gemini models: {len(available_models)}")
                if available_models:
                    return True
            except Exception as e:
                logger.error(f"Error initializing Gemini: {str(e)}")
    
    # Initialize OpenAI
    if OPENAI_AVAILABLE:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            try:
                openai.api_key = openai_api_key
                logger.info("OpenAI configured successfully")
                return True
            except Exception as e:
                logger.error(f"Error initializing OpenAI: {str(e)}")
    
    logger.warning("No AI services available")
    return False

# Generative AI Text Generation
def get_generative_ai():
    """Get the best available generative AI model"""
    if GEMINI_AVAILABLE:
        # Check if Gemini is configured
        if os.getenv("GEMINI_API_KEY"):
            try:
                models = genai.list_models()
                for model_name in ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]:  # Prefer newer models
                    for model in models:
                        if model_name in model.name and 'generateContent' in model.supported_generation_methods:
                            logger.info(f"Using Gemini model: {model.name}")
                            return GeminiAI(model.name)
            except Exception as e:
                logger.error(f"Error getting Gemini model: {str(e)}")
    
    if OPENAI_AVAILABLE:
        # Check if OpenAI is configured
        if os.getenv("OPENAI_API_KEY"):
            try:
                model_name = "gpt-4" if openai_available_models().get("gpt-4") else "gpt-3.5-turbo"
                logger.info(f"Using OpenAI model: {model_name}")
                return OpenAI(model_name)
            except Exception as e:
                logger.error(f"Error getting OpenAI model: {str(e)}")
    
    # Fallback
    logger.warning("No generative AI available, using fallback model")
    return FallbackAI()

def openai_available_models():
    """Get available OpenAI models"""
    if not OPENAI_AVAILABLE:
        return {}
    
    if not os.getenv("OPENAI_API_KEY"):
        return {}
    
    try:
        models = openai.Model.list()
        return {model.id: model for model in models.data}
    except Exception as e:
        logger.error(f"Error getting OpenAI models: {str(e)}")
        return {}

# Text embeddings
def generate_embedding(text: str, model: str = None) -> Optional[List[float]]:
    """
    Generate embedding for text using the best available model
    
    Args:
        text: Text to generate embedding for
        model: Optional model name to use
        
    Returns:
        List of floats representing the embedding vector or None if generation fails
    """
    # Get proper embedding model for Regulatory AI
    try:
        from frontend.initialize_pinecone import DIMENSION
        dimension = DIMENSION  # Should be 3072 for the RegulatoryAI index
    except ImportError:
        dimension = 3072  # Default to 3072 dimensions (text-embedding-3-large)
    
    # Determine the right model based on dimensions
    if not model:
        if dimension == 3072:
            # For Regulatory AI with 3072 dimensions
            model = "text-embedding-3-large"
        elif dimension == 1536:
            # For 1536-dimensional indexes
            model = "text-embedding-ada-002"
        else:
            # Default to small model for efficiency
            model = "text-embedding-3-small"
    
    logger.info(f"Generating embedding with model: {model}")
        
    if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
        try:
            # Use OpenAI's embedding models
            response = openai.Embedding.create(
                model=model,
                input=text
            )
            embedding = response["data"][0]["embedding"]
            logger.info(f"Generated embedding with {len(embedding)} dimensions")
            return embedding
        except Exception as e:
            logger.error(f"Error generating OpenAI embedding: {str(e)}")
    
    if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"):
        try:
            # Note: At the time of writing, Gemini doesn't have a dedicated embeddings API
            # This is a placeholder for when it becomes available
            logger.warning("Gemini embeddings not yet supported")
            pass
        except Exception as e:
            logger.error(f"Error generating Gemini embedding: {str(e)}")
    
    logger.warning("No embedding model available")
    return None

# AI Class Implementations
class GeminiAI:
    """Gemini AI implementation"""
    def __init__(self, model_name="gemini-1.5-flash"):
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name=model_name)
        self.history = []
    
    def generate_content(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 1024) -> Dict[str, Any]:
        """Generate content using Gemini"""
        try:
            generation_config = {
                "temperature": 0.4,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": max_tokens,
            }
            
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
            
            # Combine system prompt with user prompt if provided
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            else:
                full_prompt = prompt
            
            # Generate content
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Extract and return text
            if response.text:
                self.history.append({"role": "user", "content": prompt})
                self.history.append({"role": "assistant", "content": response.text})
                return {"text": response.text, "model": self.model_name}
            else:
                return {"error": "No response text", "model": self.model_name}
        except Exception as e:
            logger.error(f"Error generating content with Gemini: {str(e)}")
            logger.error(traceback.format_exc())
            return {"error": str(e), "model": self.model_name}

class OpenAI:
    """OpenAI implementation"""
    def __init__(self, model_name="gpt-3.5-turbo"):
        self.model_name = model_name
        self.history = []
    
    def generate_content(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 1024) -> Dict[str, Any]:
        """Generate content using OpenAI"""
        try:
            messages = []
            
            # Add system prompt if provided
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add chat history for context
            for message in self.history[-10:]:  # Keep context window manageable
                messages.append(message)
            
            # Add user's current prompt
            messages.append({"role": "user", "content": prompt})
            
            # Generate content
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.4,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            # Extract and return text
            if response.choices and response.choices[0].message:
                content = response.choices[0].message.content
                self.history.append({"role": "user", "content": prompt})
                self.history.append({"role": "assistant", "content": content})
                return {"text": content, "model": self.model_name}
            else:
                return {"error": "No response choices", "model": self.model_name}
        except Exception as e:
            logger.error(f"Error generating content with OpenAI: {str(e)}")
            logger.error(traceback.format_exc())
            return {"error": str(e), "model": self.model_name}

class FallbackAI:
    """Fallback AI implementation when no AI services are available"""
    def __init__(self):
        self.model_name = "fallback-model"
    
    def generate_content(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 1024) -> Dict[str, Any]:
        """Generate fallback content"""
        logger.warning("Using fallback AI model for prompt: " + prompt[:100] + "...")
        
        # Extract keywords from prompt
        keywords = re.findall(r'\b[A-Za-z]{3,}\b', prompt.lower())
        keyword_counts = {}
        for keyword in keywords:
            if keyword in keyword_counts:
                keyword_counts[keyword] += 1
            else:
                keyword_counts[keyword] = 1
        
        # Sort keywords by frequency
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        top_keywords = [k for k, v in sorted_keywords[:5] if k not in ['the', 'and', 'for', 'this', 'that', 'with', 'from']]
        
        # Generate structured but limited response
        if 'regulatory' in prompt.lower() or 'compliance' in prompt.lower() or 'regulation' in prompt.lower():
            return {
                "text": "Based on the regulatory framework analysis, there are several compliance areas that need attention. "
                       "Key requirements include transparent reporting, measurable sustainability metrics, and stakeholder engagement. "
                       "I recommend creating a structured compliance program with regular audits.",
                "model": self.model_name
            }
        elif 'carbon' in prompt.lower() or 'emission' in prompt.lower() or 'climate' in prompt.lower():
            return {
                "text": "Carbon emissions analysis suggests opportunities for reduction through operational efficiency, "
                       "renewable energy investment, and supply chain optimization. Consider setting science-based targets "
                       "and implementing a comprehensive carbon management system.",
                "model": self.model_name
            }
        elif 'sustainability' in prompt.lower() or 'esg' in prompt.lower():
            return {
                "text": "The sustainability assessment highlights both strengths and improvement areas. Strengths include "
                       "governance structure and environmental policies. Areas for improvement include supply chain transparency "
                       "and quantitative impact measurement. Recommend developing comprehensive ESG metrics.",
                "model": self.model_name
            }
        else:
            return {
                "text": "I've analyzed the information provided. While detailed AI analysis is currently unavailable, "
                       "I can suggest focusing on structured documentation, quantitative measurement, and systematic "
                       "approaches to address the key topics mentioned. Consider establishing baseline metrics and "
                       "regular review processes.",
                "model": self.model_name
            }

# RAG (Retrieval Augmented Generation) Implementation
class RAGSystem:
    """Retrieval Augmented Generation system with in-memory fallback"""
    def __init__(self):
        self.ai = get_generative_ai()
        self.pinecone_index = None
        self.in_memory_docs = []  # In-memory fallback storage
        self.use_fallback = True  # Default to fallback mode, change if Pinecone works
        self.initialize_vector_store()
    
    def initialize_vector_store(self):
        """Initialize the vector store (Pinecone)"""
        if not PINECONE_AVAILABLE:
            logger.warning("Pinecone not available for RAG system, using in-memory fallback")
            self.use_fallback = True
            return False
        
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        if not pinecone_api_key:
            logger.warning("Pinecone API key not found, using in-memory fallback")
            self.use_fallback = True
            return False
        
        # Import Pinecone configuration from initialize_pinecone.py
        try:
            from frontend.initialize_pinecone import DEFAULT_INDEX_NAME, PINECONE_HOST, REGION, DIMENSION
            index_name = DEFAULT_INDEX_NAME  # Should be 'regulatoryai'
            region = REGION  # Should be 'us-east-1'
            host = PINECONE_HOST  # Should be the provided host URL
            dimension = DIMENSION  # Should be 3072
            logger.info(f"Using RegulatoryAI Pinecone configuration: index={index_name}, region={region}, dimension={dimension}")
        except ImportError:
            # Fallback to default values if import fails
            index_name = os.getenv("PINECONE_INDEX_NAME", "regulatoryai")
            region = "us-east-1"
            host = "https://regulatoryai-lk1ck8e.svc.aped-4627-b74a.pinecone.io"
            dimension = 3072
            logger.warning(f"Using fallback Pinecone configuration: index={index_name}, region={region}")
        
        # Use Pinecone V3 API (preferred with pinecone-client>=3.0.0)
        if PINECONE_V3_AVAILABLE:
            try:
                from pinecone import Pinecone
                pc = Pinecone(api_key=pinecone_api_key)
                
                # Check if index exists
                indexes = pc.list_indexes()
                index_exists = any(idx.name == index_name for idx in indexes)
                
                if not index_exists:
                    logger.warning(f"Index {index_name} does not exist yet, attempting to create it")
                    try:
                        pc.create_index(
                            name=index_name,
                            dimension=dimension,
                            metric="cosine"
                        )
                        logger.info(f"Created new Pinecone index: {index_name}")
                    except Exception as e:
                        logger.warning(f"Could not create index: {str(e)}")
                
                # Connect to the index
                self.pinecone_index = pc.Index(index_name)
                logger.info(f"Successfully connected to Pinecone index '{index_name}' with V3 API")
                self.use_fallback = False
                return True
            except Exception as e2:
                logger.warning(f"Pinecone V3 client failed: {str(e2)}, trying V2 API")
        
        # Try with Pinecone V2 API as fallback
        try:
            # Try to use Pinecone client V2 API
            import pinecone
            
            # Try to initialize with API key and environment
            try:
                pinecone.init(api_key=pinecone_api_key, environment=region)
                
                # First check if the index exists
                if index_name not in pinecone.list_indexes():
                    logger.warning(f"Index {index_name} does not exist yet, attempting to create it")
                    # Create it
                    try:
                        pinecone.create_index(
                            name=index_name,
                            dimension=dimension,
                            metric="cosine"
                        )
                        logger.info(f"Created new Pinecone index: {index_name}")
                    except Exception as e:
                        logger.warning(f"Could not create index: {str(e)}")
                
                # Connect to the index
                self.pinecone_index = pinecone.Index(index_name)
                logger.info(f"Successfully connected to Pinecone index '{index_name}' in {region} with V2 API")
                self.use_fallback = False
                return True
            except AttributeError:
                logger.warning(f"Pinecone V2 client failed: module 'pinecone' has no attribute 'init', using in-memory fallback")
                self.use_fallback = True
                return False
        except Exception as e1:
            logger.warning(f"Pinecone V2 client failed: {str(e1)}, using in-memory fallback")
            self.use_fallback = True
            return False
        
        # If we get here, all attempts have failed
        logger.error("All Pinecone connection attempts failed, using in-memory fallback")
        self.use_fallback = True
        return False
    
    def _add_to_memory(self, doc_id: str, document_text: str, metadata: Dict[str, Any]) -> bool:
        """Add document to in-memory storage"""
        try:
            # Store document text and metadata in memory
            self.in_memory_docs.append({
                "id": doc_id,
                "text": document_text[:1000],  # Store first 1000 chars only for consistency
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata
            })
            logger.info(f"Added document to in-memory fallback with ID: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding document to in-memory fallback: {str(e)}")
            return False
    
    def add_document(self, document_text: str, metadata: Dict[str, Any]) -> bool:
        """Add document to the vector store or in-memory fallback"""
        # Create unique ID
        doc_id = str(uuid.uuid4())
        
        # If Pinecone is available, try to use it
        if not self.use_fallback and self.pinecone_index:
            try:
                # Generate embedding
                embedding = generate_embedding(document_text)
                if not embedding:
                    logger.warning("Failed to generate embedding, falling back to in-memory storage")
                    return self._add_to_memory(doc_id, document_text, metadata)
                
                # Prepare the document with metadata
                doc_metadata = {
                    "text": document_text[:1000],  # Store first 1000 chars only
                    "timestamp": datetime.now().isoformat(),
                    **metadata
                }
                
                # Try to add document to Pinecone with proper vector format based on API version
                try:
                    # First try V3 API format
                    self.pinecone_index.upsert(
                        vectors=[
                            {
                                "id": doc_id,
                                "values": embedding,
                                "metadata": doc_metadata
                            }
                        ]
                    )
                    logger.info(f"Added document to Pinecone with ID: {doc_id} (V3 API format)")
                    return True
                except (TypeError, AttributeError) as e:
                    # If that fails, try V2 API format
                    logger.warning(f"V3 API upsert format failed: {str(e)}, trying V2 API format")
                    
                    # V2 API sometimes expects (id, vector, metadata) tuples
                    self.pinecone_index.upsert(
                        vectors=[(doc_id, embedding, doc_metadata)]
                    )
                    logger.info(f"Added document to Pinecone with ID: {doc_id} (V2 API format)")
                    return True
                    
            except Exception as e:
                logger.error(f"Error adding document to Pinecone: {str(e)}")
                logger.error(traceback.format_exc())
                # Fall back to in-memory storage
                return self._add_to_memory(doc_id, document_text, metadata)
        else:
            # Use in-memory fallback
            return self._add_to_memory(doc_id, document_text, metadata)
    
    def _search_in_memory(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for documents in in-memory storage"""
        try:
            if not self.in_memory_docs:
                return []
                
            # Simple keyword-based relevance ranking
            query_terms = query.lower().split()
            results = []
            
            for doc in self.in_memory_docs:
                text = doc.get("text", "").lower()
                
                # Calculate a simple relevance score based on term frequency
                score = 0
                for term in query_terms:
                    score += text.count(term)
                
                if score > 0:
                    results.append({
                        "text": doc.get("text", ""),
                        "score": score / len(query_terms),  # Normalize score
                        "metadata": doc.get("metadata", {})
                    })
            
            # Sort by score and limit to top_k
            results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)[:top_k]
            return results
        except Exception as e:
            logger.error(f"Error searching in-memory: {str(e)}")
            return []
    
    def search_similar_documents(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar documents in the vector store or in-memory fallback"""
        # If Pinecone is available, try to use it
        if not self.use_fallback and self.pinecone_index:
            try:
                # Generate embedding
                embedding = generate_embedding(query)
                if not embedding:
                    logger.warning("Failed to generate embedding, falling back to in-memory search")
                    return self._search_in_memory(query, top_k)
                
                # Search in Pinecone
                results = self.pinecone_index.query(
                    vector=embedding,
                    top_k=top_k,
                    include_metadata=True
                )
                
                # Format results - handle both V2 and V3 API response formats
                formatted_results = []
                
                # Check if we have a V3 API response (has 'matches' attribute as a list)
                if hasattr(results, 'matches'):
                    # V2 API format or compatible V3 format
                    for match in results.matches:
                        formatted_results.append({
                            "text": match.metadata.get("text", ""),
                            "score": match.score,
                            "metadata": {k: v for k, v in match.metadata.items() if k != "text"}
                        })
                elif isinstance(results, dict) and 'matches' in results:
                    # V3 API might return a dict with 'matches' key
                    for match in results['matches']:
                        formatted_results.append({
                            "text": match['metadata'].get("text", ""),
                            "score": match['score'],
                            "metadata": {k: v for k, v in match['metadata'].items() if k != "text"}
                        })
                elif isinstance(results, list):
                    # Another possible V3 API format where results is a list of matches directly
                    for match in results:
                        metadata = match.get('metadata', {})
                        formatted_results.append({
                            "text": metadata.get("text", ""),
                            "score": match.get('score', 0),
                            "metadata": {k: v for k, v in metadata.items() if k != "text"}
                        })
                else:
                    logger.warning(f"Unexpected Pinecone response format: {type(results)}")
                    
                logger.info(f"Found {len(formatted_results)} results from Pinecone")
                
                if formatted_results:
                    return formatted_results
                else:
                    logger.info("No results from Pinecone, trying in-memory search")
                    return self._search_in_memory(query, top_k)
            except Exception as e:
                logger.error(f"Error searching Pinecone: {str(e)}, falling back to in-memory search")
                logger.error(traceback.format_exc())
                return self._search_in_memory(query, top_k)
        else:
            # Use in-memory fallback
            return self._search_in_memory(query, top_k)
    
    def generate_with_context(
        self, 
        query: str, 
        system_prompt: Optional[str] = None,
        top_k: int = 3,
        max_tokens: int = 1024
    ) -> Dict[str, Any]:
        """Generate content with context from vector store or in-memory fallback"""
        try:
            # Search for similar documents
            similar_docs = self.search_similar_documents(query, top_k=top_k)
            
            # If no similar documents found, just use the query
            if not similar_docs:
                response = self.ai.generate_content(query, system_prompt, max_tokens)
                response['source'] = 'no_context'
                return response
            
            # Build context from similar documents
            context = "I'll answer based on the following information:\n\n"
            for i, doc in enumerate(similar_docs):
                context += f"Document {i+1}:\n{doc['text']}\n\n"
            
            # Build final prompt
            final_prompt = f"{context}\nNow, based on this information, {query}"
            
            # Generate content
            response = self.ai.generate_content(final_prompt, system_prompt, max_tokens)
            
            # Add source information
            response['source'] = 'pinecone' if not self.use_fallback else 'in_memory'
            response['context_used'] = True
            
            return response
        except Exception as e:
            logger.error(f"Error in generate_with_context: {str(e)}")
            # Fallback to direct generation
            response = self.ai.generate_content(query, system_prompt, max_tokens)
            response['error'] = str(e)
            response['source'] = 'direct_fallback'
            return response

# Create RAG system instance
rag_system = None

def get_rag_system() -> RAGSystem:
    """Get or create RAG system"""
    global rag_system
    if rag_system is None:
        rag_system = RAGSystem()
    return rag_system

def is_pinecone_available() -> bool:
    """
    Check if Pinecone is actually available and connected.
    This checks not just if the module is imported, but if we can 
    actually use it for vector storage.
    
    Returns:
        bool: True if Pinecone is available and connected, False otherwise
    """
    # Check if module is imported
    if not PINECONE_AVAILABLE:
        return False
    
    # Check if we have the API key
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    if not pinecone_api_key:
        return False
    
    # Check if RAG system is initialized and not using fallback
    global rag_system
    if rag_system is None:
        # Initialize it now
        rag_system = RAGSystem()
    
    # If RAG system is using fallback, Pinecone is not actually available
    return not rag_system.use_fallback

# Initialize on module import
initialize_ai_services()