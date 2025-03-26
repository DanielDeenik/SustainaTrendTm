"""
Test script for the Regulatory AI RAG system integration with Pinecone

This script tests the direct functionality of the RAG system with Pinecone,
including document embedding and retrieval capabilities.
"""
import os
import sys
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    # Import RAG system from ai_connector
    from utils.ai_connector import get_rag_system, is_pinecone_available
    from utils.ai_connector import generate_embedding
except ImportError:
    logger.error("Failed to import RAG system, check that utils/ai_connector.py is available")
    sys.exit(1)

def get_test_document() -> str:
    """
    Get test document text from file or generate a simple test document
    """
    # Try to load from a file first
    try:
        with open('static/test-sustainability-report.txt', 'r') as f:
            return f.read()
    except (FileNotFoundError, IOError):
        # Generate a simple test document if file not found
        logger.warning("Test sustainability report file not found, using sample text")
        return """
        Sustainability Report 2024
        
        Executive Summary:
        Our company has made significant progress in reducing our carbon footprint by 15% this year.
        We have also implemented new water conservation measures across all facilities.
        
        Environmental Performance:
        - Carbon emissions reduced from 10,000 to 8,500 metric tons CO2e
        - Water usage reduced by 20% through recycling programs
        - Waste diversion rate increased to 78%
        
        Social Impact:
        - Employee volunteer hours increased by 35%
        - Diversity and inclusion metrics improved across all departments
        - Community investment reached $2.5 million
        
        Governance:
        - Board diversity increased to 45% women and minorities
        - Implemented enhanced ESG oversight committee
        - Established new sustainability-linked executive compensation metrics
        
        TCFD Disclosure:
        We are aligning our climate risk assessment with TCFD recommendations.
        Our scenario analysis considers both physical and transition risks.
        
        EU CSRD Compliance:
        We are preparing for full CSRD compliance by implementing double materiality assessments
        and expanding our data collection to include all required metrics.
        """

def test_pinecone_connection() -> bool:
    """
    Test if Pinecone is available and connected
    """
    is_available = is_pinecone_available()
    if is_available:
        logger.info("Pinecone is available and connected")
    else:
        logger.warning("Pinecone is not available, tests will use in-memory fallback")
    return is_available

def test_document_embedding(doc_text: str) -> str:
    """
    Test embedding a document into the RAG system
    
    Args:
        doc_text: Document text to embed
        
    Returns:
        Document ID if successful, empty string otherwise
    """
    # Get RAG system
    rag_system = get_rag_system()
    
    # Create test metadata
    metadata = {
        "title": "Test Sustainability Report",
        "source": "test_script",
        "category": "ESG",
        "framework": ["CSRD", "TCFD"],
        "timestamp": datetime.now().isoformat()
    }
    
    # Add document to RAG system
    success = rag_system.add_document(doc_text, metadata)
    
    if success:
        logger.info("Successfully added document to RAG system")
        # Since we don't have direct access to the document ID that was generated inside
        # the add_document method, we'll return a placeholder
        return "Document added successfully"
    else:
        logger.error("Failed to add document to RAG system")
        return ""

def test_document_retrieval(query: str) -> List[Dict[str, Any]]:
    """
    Test retrieving similar documents from the RAG system
    
    Args:
        query: Query to search for
        
    Returns:
        List of similar documents
    """
    # Get RAG system
    rag_system = get_rag_system()
    
    # Search for similar documents
    results = rag_system.search_similar_documents(query, top_k=3)
    
    if results:
        logger.info(f"Found {len(results)} similar documents")
        for i, result in enumerate(results):
            logger.info(f"Result {i+1}: Score {result.get('score', 'N/A')}")
            logger.info(f"Text: {result.get('text', '')[:100]}...")
    else:
        logger.warning("No similar documents found")
    
    return results

def test_generate_with_context(query: str) -> Dict[str, Any]:
    """
    Test generating content with context from the RAG system
    
    Args:
        query: Query to generate content for
        
    Returns:
        Generated content
    """
    # Get RAG system
    rag_system = get_rag_system()
    
    # Generate content with context
    result = rag_system.generate_with_context(
        query=query,
        system_prompt="You are a sustainability expert. Provide concise, accurate information.",
        top_k=3,
        max_tokens=500
    )
    
    if result.get("text"):
        logger.info("Successfully generated content with context")
        logger.info(f"Source: {result.get('source', 'unknown')}")
        logger.info(f"Generated text: {result.get('text', '')[:150]}...")
    else:
        logger.error(f"Failed to generate content: {result.get('error', 'Unknown error')}")
    
    return result

def main():
    """
    Main test function
    """
    logger.info("Starting Regulatory AI RAG system tests")
    
    # Test Pinecone connection
    pinecone_available = test_pinecone_connection()
    
    # Get test document
    doc_text = get_test_document()
    logger.info(f"Using test document with {len(doc_text)} characters")
    
    # Test document embedding
    doc_id = test_document_embedding(doc_text)
    if not doc_id:
        logger.error("Document embedding test failed, aborting further tests")
        return
    
    # Test queries
    test_queries = [
        "What are the company's carbon emissions?",
        "How does the company address EU CSRD compliance?",
        "What governance measures are in place for sustainability?",
        "What is the company's approach to TCFD disclosure?"
    ]
    
    # Test document retrieval and generation for each query
    for query in test_queries:
        logger.info(f"\nTesting query: {query}")
        similar_docs = test_document_retrieval(query)
        
        if similar_docs:
            generated_content = test_generate_with_context(query)
            logger.info("Query test completed")
        else:
            logger.warning(f"Skipping generation for query: {query}")
    
    logger.info("All tests completed")

if __name__ == "__main__":
    main()