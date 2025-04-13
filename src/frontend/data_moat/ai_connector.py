"""
AI Connector for Data Moat Functionality

This module provides AI connectivity for the data moat functionality,
interacting with OpenAI and Pinecone for document processing and RAG capabilities.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)

# Try to import AI libraries
try:
    import openai
    OPENAI_AVAILABLE = True
    logger.info("OpenAI package is available")
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI package is not available")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    logger.info("Google Generative AI package is available")
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI package is not available")

try:
    from pinecone import Pinecone, PodSpec
    PINECONE_AVAILABLE = True
    logger.info("Pinecone package is available")
except ImportError:
    PINECONE_AVAILABLE = False
    logger.warning("Pinecone package is not available")

# Try to import from the parent services directory
try:
    from ..services.ai_connector import (
        query_openai as parent_query_openai,
        generate_embeddings as parent_generate_embeddings,
        store_embeddings_in_pinecone as parent_store_embeddings_in_pinecone,
        is_openai_available as parent_is_openai_available,
        is_pinecone_available as parent_is_pinecone_available
    )
    PARENT_AI_CONNECTOR_AVAILABLE = True
    logger.info("Parent AI connector package is available")
except ImportError:
    PARENT_AI_CONNECTOR_AVAILABLE = False
    logger.warning("Parent AI connector package is not available")

class DataMoatAIConnector:
    """AI connector for data moat functionality"""
    
    def __init__(self):
        """Initialize the AI connector"""
        self.openai_available = OPENAI_AVAILABLE
        self.gemini_available = GEMINI_AVAILABLE
        self.pinecone_available = PINECONE_AVAILABLE
        
        # Initialize OpenAI if available
        if self.openai_available:
            openai.api_key = os.environ.get('OPENAI_API_KEY')
        
        # Initialize Gemini if available
        if self.gemini_available:
            gemini_api_key = os.environ.get('GEMINI_API_KEY')
            if gemini_api_key:
                genai.configure(api_key=gemini_api_key)
        
        # Initialize Pinecone if available
        self.pc = None
        self.index = None
        
        if self.pinecone_available:
            try:
                pinecone_api_key = os.environ.get('PINECONE_API_KEY')
                if pinecone_api_key:
                    self.pc = Pinecone(api_key=pinecone_api_key)
                    
                    # Get list of indexes
                    indexes = self.pc.list_indexes()
                    index_name = os.environ.get('PINECONE_INDEX_NAME', 'sustainatrend')
                    
                    if index_name in [idx for idx in indexes]:
                        self.index = self.pc.Index(index_name)
                        logger.info(f"Connected to Pinecone index: {index_name}")
                    else:
                        logger.warning(f"Pinecone index {index_name} not found")
            except Exception as e:
                logger.error(f"Error connecting to Pinecone: {str(e)}")
                self.pinecone_available = False
    
    def is_openai_available(self) -> bool:
        """
        Check if OpenAI is available
        
        Returns:
            True if OpenAI is available, False otherwise
        """
        if PARENT_AI_CONNECTOR_AVAILABLE:
            return parent_is_openai_available()
        
        return self.openai_available and os.environ.get('OPENAI_API_KEY') is not None
    
    def is_gemini_available(self) -> bool:
        """
        Check if Gemini is available
        
        Returns:
            True if Gemini is available, False otherwise
        """
        return self.gemini_available and os.environ.get('GEMINI_API_KEY') is not None
    
    def is_pinecone_available(self) -> bool:
        """
        Check if Pinecone is available
        
        Returns:
            True if Pinecone is available, False otherwise
        """
        if PARENT_AI_CONNECTOR_AVAILABLE:
            return parent_is_pinecone_available()
        
        return self.pinecone_available and self.pc is not None and self.index is not None
    
    def query_openai(self, prompt: str, model: str = "gpt-3.5-turbo") -> Optional[Dict[str, Any]]:
        """
        Query OpenAI with a prompt
        
        Args:
            prompt: Prompt to send to OpenAI
            model: OpenAI model to use
            
        Returns:
            OpenAI response or None if unavailable
        """
        if PARENT_AI_CONNECTOR_AVAILABLE:
            return parent_query_openai(prompt, model)
        
        if not self.is_openai_available():
            logger.warning("OpenAI is not available")
            return None
        
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant specialized in sustainability document analysis."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                'content': response.choices[0].message.content,
                'model': model
            }
        except Exception as e:
            logger.error(f"Error querying OpenAI: {str(e)}")
            return None
    
    def query_gemini(self, prompt: str, model: str = "gemini-pro") -> Optional[Dict[str, Any]]:
        """
        Query Gemini with a prompt
        
        Args:
            prompt: Prompt to send to Gemini
            model: Gemini model to use
            
        Returns:
            Gemini response or None if unavailable
        """
        if not self.is_gemini_available():
            logger.warning("Gemini is not available")
            return None
        
        try:
            gemini_model = genai.GenerativeModel(model)
            response = gemini_model.generate_content(prompt)
            
            return {
                'content': response.text,
                'model': model
            }
        except Exception as e:
            logger.error(f"Error querying Gemini: {str(e)}")
            return None
    
    def generate_embeddings(self, text: str, model: str = "text-embedding-ada-002") -> Optional[List[float]]:
        """
        Generate embeddings for a text using OpenAI
        
        Args:
            text: Text to generate embeddings for
            model: OpenAI embedding model to use
            
        Returns:
            Text embeddings or None if unavailable
        """
        if PARENT_AI_CONNECTOR_AVAILABLE:
            return parent_generate_embeddings(text, model)
        
        if not self.is_openai_available():
            logger.warning("OpenAI is not available for generating embeddings")
            return None
        
        try:
            response = openai.Embedding.create(
                input=text,
                model=model
            )
            
            return response['data'][0]['embedding']
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            return None
    
    def store_embeddings_in_pinecone(self, id: str, embeddings: List[float], metadata: Dict[str, Any]) -> bool:
        """
        Store embeddings in Pinecone
        
        Args:
            id: Record ID
            embeddings: Vector embeddings
            metadata: Metadata to store with the embeddings
            
        Returns:
            True if successful, False otherwise
        """
        if PARENT_AI_CONNECTOR_AVAILABLE:
            return parent_store_embeddings_in_pinecone(id, embeddings, metadata)
        
        if not self.is_pinecone_available():
            logger.warning("Pinecone is not available for storing embeddings")
            return False
        
        try:
            self.index.upsert(
                vectors=[{
                    'id': id,
                    'values': embeddings,
                    'metadata': metadata
                }]
            )
            
            return True
        except Exception as e:
            logger.error(f"Error storing embeddings in Pinecone: {str(e)}")
            return False
    
    def query_pinecone(self, query_embeddings: List[float], top_k: int = 5) -> Optional[List[Dict[str, Any]]]:
        """
        Query Pinecone with embeddings
        
        Args:
            query_embeddings: Query vector embeddings
            top_k: Number of results to return
            
        Returns:
            List of matches or None if unavailable
        """
        if not self.is_pinecone_available():
            logger.warning("Pinecone is not available for querying")
            return None
        
        try:
            results = self.index.query(
                vector=query_embeddings,
                top_k=top_k,
                include_metadata=True
            )
            
            return results.matches
        except Exception as e:
            logger.error(f"Error querying Pinecone: {str(e)}")
            return None

# Create a singleton instance
ai_connector = DataMoatAIConnector()