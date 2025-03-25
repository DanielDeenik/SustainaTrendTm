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
    from pinecone import Pinecone
    PINECONE_AVAILABLE = True
    logger.info("Pinecone module loaded successfully")
except ImportError:
    PINECONE_AVAILABLE = False
    logger.warning("Pinecone not available")

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
def generate_embedding(text: str) -> Optional[List[float]]:
    """Generate embedding for text using the best available model"""
    if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
        try:
            # Use text-embedding-3-small for efficiency
            response = openai.Embedding.create(
                model="text-embedding-3-small",
                input=text
            )
            return response["data"][0]["embedding"]
        except Exception as e:
            logger.error(f"Error generating OpenAI embedding: {str(e)}")
    
    if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"):
        try:
            # Note: At the time of writing, Gemini doesn't have a dedicated embeddings API
            # This is a placeholder for when it becomes available
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
    """Retrieval Augmented Generation system"""
    def __init__(self):
        self.ai = get_generative_ai()
        self.pinecone_index = None
        self.initialize_vector_store()
    
    def initialize_vector_store(self):
        """Initialize the vector store (Pinecone)"""
        if not PINECONE_AVAILABLE:
            logger.warning("Pinecone not available for RAG system")
            return False
        
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        if not pinecone_api_key:
            logger.warning("Pinecone API key not found")
            return False
        
        try:
            pc = Pinecone(api_key=pinecone_api_key)
            
            # Create index if it doesn't exist
            index_name = os.getenv("PINECONE_INDEX_NAME", "sustainatrend-rag")
            self.pinecone_index = pc.Index(index_name)
            logger.info(f"Connected to Pinecone index: {index_name}")
            return True
        except Exception as e:
            logger.error(f"Error initializing Pinecone: {str(e)}")
            return False
    
    def add_document(self, document_text: str, metadata: Dict[str, Any]) -> bool:
        """Add document to the vector store"""
        if not self.pinecone_index:
            logger.warning("Vector store not available")
            return False
        
        try:
            # Generate embedding
            embedding = generate_embedding(document_text)
            if not embedding:
                logger.warning("Failed to generate embedding")
                return False
            
            # Create unique ID
            doc_id = str(uuid.uuid4())
            
            # Add to vector store
            self.pinecone_index.upsert(
                vectors=[
                    {
                        "id": doc_id,
                        "values": embedding,
                        "metadata": {
                            "text": document_text[:1000],  # Store first 1000 chars only
                            "timestamp": datetime.now().isoformat(),
                            **metadata
                        }
                    }
                ]
            )
            logger.info(f"Added document to vector store with ID: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding document to vector store: {str(e)}")
            return False
    
    def search_similar_documents(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar documents in the vector store"""
        if not self.pinecone_index:
            logger.warning("Vector store not available")
            return []
        
        try:
            # Generate embedding
            embedding = generate_embedding(query)
            if not embedding:
                logger.warning("Failed to generate embedding")
                return []
            
            # Search
            results = self.pinecone_index.query(
                vector=embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Format results
            formatted_results = []
            for match in results.matches:
                formatted_results.append({
                    "text": match.metadata.get("text", ""),
                    "score": match.score,
                    "metadata": {k: v for k, v in match.metadata.items() if k != "text"}
                })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            return []
    
    def generate_with_context(
        self, 
        query: str, 
        system_prompt: Optional[str] = None,
        top_k: int = 3,
        max_tokens: int = 1024
    ) -> Dict[str, Any]:
        """Generate content with context from the vector store"""
        # Search for similar documents
        similar_docs = self.search_similar_documents(query, top_k=top_k)
        
        # If no similar documents found, just use the query
        if not similar_docs:
            return self.ai.generate_content(query, system_prompt, max_tokens)
        
        # Build context from similar documents
        context = "I'll answer based on the following information:\n\n"
        for i, doc in enumerate(similar_docs):
            context += f"Document {i+1}:\n{doc['text']}\n\n"
        
        # Build final prompt
        final_prompt = f"{context}\nNow, based on this information, {query}"
        
        # Generate content
        return self.ai.generate_content(final_prompt, system_prompt, max_tokens)

# Create RAG system instance
rag_system = None

def get_rag_system() -> RAGSystem:
    """Get or create RAG system"""
    global rag_system
    if rag_system is None:
        rag_system = RAGSystem()
    return rag_system

# Initialize on module import
initialize_ai_services()