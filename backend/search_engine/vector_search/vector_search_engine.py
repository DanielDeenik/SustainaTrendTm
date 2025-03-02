"""
Vector Search Engine for Sustainability Data

Implements semantic search using vector embeddings, allowing for 
finding content based on meaning rather than exact keyword matches.
"""
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
import os
import json
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class VectorSearchEngine:
    """
    Vector-based semantic search engine for sustainability data.
    
    Provides semantic search capabilities by converting text to vector 
    embeddings and finding similar vectors in the embedding space.
    """
    
    def __init__(self, 
                embedding_dimension: int = 768, 
                index_path: Optional[str] = None):
        """
        Initialize the vector search engine.
        
        Args:
            embedding_dimension: Dimension of the embedding vectors
            index_path: Optional path to save/load the vector index
        """
        self.dimension = embedding_dimension
        self.document_store = {}  # doc_id -> document mapping
        self.vector_store = {}    # doc_id -> vector mapping
        self.metadata_store = {}  # doc_id -> metadata mapping
        self.index_path = index_path
        
        # Track index stats
        self.document_count = 0
        self.last_updated = None
        
        # Load index if path is provided and file exists
        if index_path and os.path.exists(index_path):
            self._load_index()
    
    def add_document(self, 
                     doc_id: str, 
                     document: Dict[str, Any], 
                     vector: Optional[np.ndarray] = None) -> None:
        """
        Add a document to the vector search index.
        
        Args:
            doc_id: Unique document identifier
            document: Document data
            vector: Document embedding vector (optional, will be generated if not provided)
        """
        # Generate vector if not provided
        if vector is None:
            vector = self._generate_vector(document)
        
        # Normalize the vector
        vector = vector / np.linalg.norm(vector)
        
        # Store document and its vector
        self.document_store[doc_id] = document
        self.vector_store[doc_id] = vector
        
        # Extract and store metadata
        metadata = self._extract_metadata(document)
        self.metadata_store[doc_id] = metadata
        
        # Update stats
        self.document_count += 1
        self.last_updated = datetime.now()
        
        logger.debug(f"Added document {doc_id} to vector index")
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Add multiple documents to the vector search index.
        
        Args:
            documents: List of documents to index
            
        Returns:
            List of document IDs
        """
        doc_ids = []
        
        for document in documents:
            # Create document ID if not present
            if '_id' not in document:
                doc_id = self._generate_document_id(document)
            else:
                doc_id = document['_id']
            
            # Add document to index
            self.add_document(doc_id, document)
            doc_ids.append(doc_id)
        
        # Save index if path is provided
        if self.index_path:
            self._save_index()
        
        return doc_ids
    
    def search(self, 
               query: Union[str, np.ndarray], 
               filter_criteria: Optional[Dict[str, Any]] = None,
               max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for semantically similar documents.
        
        Args:
            query: Search query (text string or vector)
            filter_criteria: Optional criteria to filter results (e.g., {"category": "emissions"})
            max_results: Maximum number of results to return
            
        Returns:
            List of similar documents with similarity scores
        """
        # Generate query vector if input is a string
        if isinstance(query, str):
            query_vector = self._generate_vector({"text": query})
        else:
            query_vector = query
        
        # Normalize the query vector
        query_vector = query_vector / np.linalg.norm(query_vector)
        
        # Calculate similarity scores for all documents
        scores = {}
        for doc_id, doc_vector in self.vector_store.items():
            # Calculate cosine similarity
            similarity = np.dot(query_vector, doc_vector)
            scores[doc_id] = similarity
        
        # Get all results sorted by score
        results = []
        for doc_id, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            # Apply filters if provided
            if filter_criteria and not self._matches_filter(doc_id, filter_criteria):
                continue
            
            # Add to results
            document = self.document_store[doc_id].copy()
            document['score'] = float(score)
            document['doc_id'] = doc_id
            results.append(document)
            
            # Stop once we have enough results
            if len(results) >= max_results:
                break
        
        return results
    
    def _generate_vector(self, document: Dict[str, Any]) -> np.ndarray:
        """
        Generate a vector embedding for a document.
        
        In a production system, this would use a proper embedding model.
        For now, it generates a deterministic mock vector based on content.
        
        Args:
            document: Document to vectorize
            
        Returns:
            Document vector embedding
        """
        # Extract text for embedding
        text = ""
        if "title" in document:
            text += document["title"] + " "
        if "content" in document:
            text += document["content"] + " "
        if "description" in document:
            text += document["description"] + " "
        if "text" in document:
            text += document["text"]
        
        # If no text was found, use the entire document as a string
        if not text:
            text = str(document)
        
        # Generate deterministic vector based on text hash
        hash_obj = hashlib.md5(text.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        
        # Use hash as seed for random vector (for consistency)
        np.random.seed(hash_int)
        vector = np.random.randn(self.dimension)
        
        return vector
    
    def _extract_metadata(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract searchable metadata from a document.
        
        Args:
            document: Document to extract metadata from
            
        Returns:
            Document metadata
        """
        metadata = {}
        
        # Extract common fields
        for field in ["category", "source", "date", "author", "company", "industry"]:
            if field in document:
                metadata[field] = document[field]
        
        # Extract sustainability-specific metadata
        if "sustainability_categories" in document:
            metadata["sustainability_categories"] = document["sustainability_categories"]
        
        if "esg_topics" in document:
            metadata["esg_topics"] = document["esg_topics"]
        
        if "entities" in document and isinstance(document["entities"], dict):
            entities = document["entities"]
            
            # Extract company mentions
            if "companies" in entities:
                metadata["mentioned_companies"] = [
                    company["name"] for company in entities["companies"]
                ]
            
            # Extract framework mentions
            if "frameworks" in entities:
                metadata["frameworks"] = [
                    framework["name"] for framework in entities["frameworks"]
                ]
        
        return metadata
    
    def _matches_filter(self, doc_id: str, filter_criteria: Dict[str, Any]) -> bool:
        """
        Check if a document matches filter criteria.
        
        Args:
            doc_id: Document ID to check
            filter_criteria: Filter criteria to apply
            
        Returns:
            True if document matches all filters, False otherwise
        """
        # Get document metadata
        metadata = self.metadata_store.get(doc_id, {})
        
        # Check each filter criterion
        for key, value in filter_criteria.items():
            # Special handling for date ranges
            if key == "date_range" and isinstance(value, tuple) and len(value) == 2:
                doc_date = metadata.get("date")
                if not doc_date or not (value[0] <= doc_date <= value[1]):
                    return False
            
            # List-based filtering (any match)
            elif key.endswith("_any") and isinstance(value, list):
                field = key[:-4]  # Remove "_any" suffix
                field_value = metadata.get(field)
                
                if not field_value:
                    return False
                
                # Check if any value matches
                if isinstance(field_value, list):
                    if not any(v in field_value for v in value):
                        return False
                elif field_value not in value:
                    return False
            
            # List-based filtering (all required)
            elif key.endswith("_all") and isinstance(value, list):
                field = key[:-4]  # Remove "_all" suffix
                field_value = metadata.get(field)
                
                if not field_value:
                    return False
                
                # Check if all values match
                if isinstance(field_value, list):
                    if not all(v in field_value for v in value):
                        return False
                else:
                    # Single value must match all criteria (not typically useful)
                    if not all(v == field_value for v in value):
                        return False
            
            # Regular equality check
            elif metadata.get(key) != value:
                return False
        
        # All criteria matched
        return True
    
    def _generate_document_id(self, document: Dict[str, Any]) -> str:
        """
        Generate a unique document ID based on content.
        
        Args:
            document: Document to generate ID for
            
        Returns:
            Unique document ID
        """
        # Create a string representation of important fields
        id_text = ""
        for field in ["title", "url", "content"]:
            if field in document:
                id_text += str(document[field])
        
        # Generate hash-based ID
        hash_obj = hashlib.md5(id_text.encode())
        return f"doc_{hash_obj.hexdigest()[:16]}"
    
    def _save_index(self) -> None:
        """Save the vector index to disk."""
        if not self.index_path:
            return
        
        # Create index data structure
        index_data = {
            "metadata": {
                "dimension": self.dimension,
                "document_count": self.document_count,
                "last_updated": self.last_updated.isoformat() if self.last_updated else None
            },
            "documents": self.document_store,
            "metadata_store": self.metadata_store
        }
        
        # Save vectors separately (convert to lists for JSON serialization)
        vector_data = {
            doc_id: vector.tolist() for doc_id, vector in self.vector_store.items()
        }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        # Save index data
        with open(self.index_path, 'w') as f:
            json.dump(index_data, f)
        
        # Save vectors
        vector_path = f"{os.path.splitext(self.index_path)[0]}_vectors.json"
        with open(vector_path, 'w') as f:
            json.dump(vector_data, f)
        
        logger.info(f"Saved vector index to {self.index_path}")
    
    def _load_index(self) -> None:
        """Load the vector index from disk."""
        if not self.index_path or not os.path.exists(self.index_path):
            return
        
        try:
            # Load index data
            with open(self.index_path, 'r') as f:
                index_data = json.load(f)
            
            # Load vectors
            vector_path = f"{os.path.splitext(self.index_path)[0]}_vectors.json"
            with open(vector_path, 'r') as f:
                vector_data = json.load(f)
            
            # Set index metadata
            metadata = index_data.get("metadata", {})
            self.dimension = metadata.get("dimension", self.dimension)
            self.document_count = metadata.get("document_count", 0)
            
            last_updated = metadata.get("last_updated")
            if last_updated:
                self.last_updated = datetime.fromisoformat(last_updated)
            
            # Load documents and metadata
            self.document_store = index_data.get("documents", {})
            self.metadata_store = index_data.get("metadata_store", {})
            
            # Load vectors (convert from lists back to numpy arrays)
            self.vector_store = {
                doc_id: np.array(vector) for doc_id, vector in vector_data.items()
            }
            
            logger.info(f"Loaded vector index from {self.index_path} with {self.document_count} documents")
            
        except Exception as e:
            logger.error(f"Error loading vector index: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector index.
        
        Returns:
            Dictionary with index statistics
        """
        return {
            "document_count": self.document_count,
            "dimension": self.dimension,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "index_size_bytes": sum(vector.nbytes for vector in self.vector_store.values()) if self.vector_store else 0,
            "categories": self._get_category_stats()
        }
    
    def _get_category_stats(self) -> Dict[str, int]:
        """
        Get statistics about document categories in the index.
        
        Returns:
            Dictionary mapping categories to document counts
        """
        category_counts = {}
        
        for doc_id in self.document_store:
            metadata = self.metadata_store.get(doc_id, {})
            category = metadata.get("category")
            
            if category:
                if isinstance(category, list):
                    for cat in category:
                        category_counts[cat] = category_counts.get(cat, 0) + 1
                else:
                    category_counts[category] = category_counts.get(category, 0) + 1
        
        return category_counts