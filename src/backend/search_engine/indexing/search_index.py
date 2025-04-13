"""
Search Index for Sustainability Data

This module implements a hybrid search index combining:
1. Traditional inverted index for keyword search
2. Vector embeddings for semantic search
"""
import logging
import json
import os
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from datetime import datetime
import numpy as np
from collections import defaultdict
import re

logger = logging.getLogger(__name__)

class InMemoryInvertedIndex:
    """Simple in-memory inverted index implementation"""
    
    def __init__(self):
        self.index = defaultdict(list)
        self.document_store = {}
        self.document_count = 0
    
    def add_document(self, doc_id: str, document: Dict[str, Any], fields: List[str] = None) -> None:
        """
        Add a document to the inverted index.
        
        Args:
            doc_id: Unique document identifier
            document: Document data
            fields: List of fields to index (if None, index all text fields)
        """
        self.document_store[doc_id] = document
        self.document_count += 1
        
        if fields is None:
            # Default to indexing standard text fields
            fields = ['title', 'content', 'description', 'summary']
        
        # Extract terms from specified fields
        all_terms = set()
        for field in fields:
            if field in document and isinstance(document[field], str):
                field_text = document[field].lower()
                # Extract terms (simple tokenization)
                terms = set(re.findall(r'\b\w+\b', field_text))
                for term in terms:
                    if len(term) > 1:  # Skip single-character terms
                        self.index[term].append((doc_id, field))
                all_terms.update(terms)
        
        # Store the document terms for TF-IDF calculations
        document['_terms'] = list(all_terms)
    
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search the index using a keyword query.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of matching documents with relevance scores
        """
        if not query:
            return []
        
        # Tokenize query
        query_terms = set(re.findall(r'\b\w+\b', query.lower()))
        
        # Calculate document scores using TF-IDF like approach
        scores = defaultdict(float)
        
        for term in query_terms:
            if term in self.index:
                # Inverse document frequency (IDF) - terms in fewer docs get higher weight
                matching_docs = set(doc_id for doc_id, _ in self.index[term])
                idf = np.log(self.document_count / (1 + len(matching_docs)))
                
                # For each document containing the term
                for doc_id, field in self.index[term]:
                    # Field boost - title matches worth more than content
                    field_boost = 3.0 if field == 'title' else 1.0
                    
                    # Add to document score
                    scores[doc_id] += idf * field_boost
        
        # Get top scoring documents
        ranked_docs = sorted(
            [(doc_id, score) for doc_id, score in scores.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Return results with scores
        results = []
        for doc_id, score in ranked_docs[:max_results]:
            doc = self.document_store[doc_id].copy()
            doc['score'] = float(score)
            doc['doc_id'] = doc_id
            results.append(doc)
        
        return results


class SimpleVectorIndex:
    """Simple vector index for semantic similarity search"""
    
    def __init__(self, vector_dimension: int = 768):
        self.vectors = {}  # doc_id -> vector mapping
        self.document_store = {}  # doc_id -> document mapping
        self.dimension = vector_dimension
    
    def add_document(self, doc_id: str, document: Dict[str, Any], vector: np.ndarray) -> None:
        """
        Add a document with its vector embedding to the index.
        
        Args:
            doc_id: Unique document identifier
            document: Document data
            vector: Document vector embedding
        """
        self.document_store[doc_id] = document
        self.vectors[doc_id] = vector / np.linalg.norm(vector)  # Normalize vector
    
    def search(self, query_vector: np.ndarray, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents similar to the query vector.
        
        Args:
            query_vector: Query vector embedding
            max_results: Maximum number of results to return
            
        Returns:
            List of similar documents with similarity scores
        """
        if len(self.vectors) == 0:
            return []
        
        # Normalize query vector
        query_vector = query_vector / np.linalg.norm(query_vector)
        
        # Calculate cosine similarity with all document vectors
        similarities = {}
        for doc_id, doc_vector in self.vectors.items():
            similarity = np.dot(query_vector, doc_vector)
            similarities[doc_id] = similarity
        
        # Rank by similarity
        ranked_docs = sorted(
            [(doc_id, score) for doc_id, score in similarities.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Return results
        results = []
        for doc_id, score in ranked_docs[:max_results]:
            doc = self.document_store[doc_id].copy()
            doc['score'] = float(score)
            doc['doc_id'] = doc_id
            results.append(doc)
        
        return results


class MockVectorEncoder:
    """Mock vector encoder for development/testing"""
    
    def __init__(self, vector_dimension: int = 768):
        self.dimension = vector_dimension
    
    def encode_text(self, text: str) -> np.ndarray:
        """
        Generate a mock vector representation for text.
        
        In production, this would use an actual embedding model.
        """
        # Generate deterministic but unique vector based on text hash
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        
        # Generate vector based on hash (for consistent results)
        np.random.seed(hash_int)
        vector = np.random.randn(self.dimension)
        
        return vector / np.linalg.norm(vector)  # Return normalized vector


class SearchIndex:
    """
    Hybrid search index for sustainability data.
    
    Combines keyword-based search with vector similarity search
    for improved results.
    """
    
    def __init__(self, vector_dimension: int = 768):
        self.keyword_index = InMemoryInvertedIndex()
        self.vector_index = SimpleVectorIndex(vector_dimension)
        self.vector_encoder = MockVectorEncoder(vector_dimension)
        self.document_count = 0
        self.last_indexed = None
    
    def index_document(self, document: Dict[str, Any]) -> str:
        """
        Index a document in both keyword and vector indexes.
        
        Args:
            document: Document to index
            
        Returns:
            Document ID
        """
        # Create document ID if not present
        if '_id' not in document:
            self.document_count += 1
            doc_id = f"doc_{self.document_count}"
        else:
            doc_id = document['_id']
        
        # Add to keyword index
        self.keyword_index.add_document(doc_id, document)
        
        # Create vector embedding and add to vector index
        text_to_encode = f"{document.get('title', '')} {document.get('description', '')} {document.get('content', '')[:1000]}"
        vector = self.vector_encoder.encode_text(text_to_encode)
        self.vector_index.add_document(doc_id, document, vector)
        
        # Mark indexing time
        self.last_indexed = datetime.now()
        
        return doc_id
    
    def index_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Index multiple documents.
        
        Args:
            documents: List of documents to index
            
        Returns:
            List of document IDs
        """
        doc_ids = []
        for document in documents:
            doc_id = self.index_document(document)
            doc_ids.append(doc_id)
        
        return doc_ids
    
    def search(self, 
               query: str, 
               mode: str = "hybrid", 
               max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search the index.
        
        Args:
            query: Search query string
            mode: Search mode - "hybrid", "keyword", or "vector"
            max_results: Maximum number of results to return
            
        Returns:
            List of matching documents with relevance scores
        """
        if not query:
            return []
        
        logger.info(f"Searching for '{query}' using {mode} mode")
        
        if mode == "keyword":
            # Only use keyword search
            return self.keyword_index.search(query, max_results)
            
        elif mode == "vector":
            # Only use vector search
            query_vector = self.vector_encoder.encode_text(query)
            return self.vector_index.search(query_vector, max_results)
            
        else:
            # Hybrid search (default)
            # Get results from both indexes
            keyword_results = self.keyword_index.search(query, max_results * 2)
            query_vector = self.vector_encoder.encode_text(query)
            vector_results = self.vector_index.search(query_vector, max_results * 2)
            
            # Combine and re-rank results
            return self._combine_search_results(keyword_results, vector_results, max_results)
    
    def _combine_search_results(self, 
                               keyword_results: List[Dict[str, Any]], 
                               vector_results: List[Dict[str, Any]], 
                               max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Combine and re-rank results from keyword and vector searches.
        
        Args:
            keyword_results: Results from keyword search
            vector_results: Results from vector search
            max_results: Maximum number of results to return
            
        Returns:
            Combined and re-ranked results
        """
        # Create a mapping of doc_id to result
        combined_map = {}
        
        # Process keyword results
        for result in keyword_results:
            doc_id = result['doc_id']
            combined_map[doc_id] = {
                **result,
                'keyword_score': result['score'],
                'vector_score': 0.0,
                'combined_score': result['score'] * 0.4  # Weight for keyword search
            }
        
        # Process vector results
        for result in vector_results:
            doc_id = result['doc_id']
            if doc_id in combined_map:
                # Document already in results, update scores
                combined_map[doc_id]['vector_score'] = result['score']
                combined_map[doc_id]['combined_score'] += result['score'] * 0.6  # Weight for vector search
            else:
                # New document
                combined_map[doc_id] = {
                    **result,
                    'keyword_score': 0.0,
                    'vector_score': result['score'],
                    'combined_score': result['score'] * 0.6  # Weight for vector search
                }
        
        # Convert map to list and sort by combined score
        combined_results = list(combined_map.values())
        combined_results.sort(key=lambda x: x['combined_score'], reverse=True)
        
        # Return top results
        return combined_results[:max_results]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the index.
        
        Returns:
            Dictionary with index statistics
        """
        return {
            'document_count': self.document_count,
            'last_indexed': self.last_indexed.isoformat() if self.last_indexed else None,
            'keyword_index_size': self.keyword_index.document_count,
            'vector_index_size': len(self.vector_index.vectors)
        }