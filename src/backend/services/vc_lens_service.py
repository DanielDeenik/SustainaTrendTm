"""
VC Lens Service

Handles document processing, vector storage, and analysis for the VC Lens module.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
from ..config.database import get_vc_lens_collection, get_mongodb_client

# Configure logging
logger = logging.getLogger(__name__)

class VCLensService:
    """Service for VC Lens document processing and analysis"""
    
    def __init__(self):
        """Initialize VC Lens service"""
        self.collection = get_vc_lens_collection()
        self.mongodb = get_mongodb_client()
        self.db = self.mongodb[os.getenv('MONGODB_DATABASE', 'trendsense')]
    
    def process_document(self, document_path: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a document and store its vector representation
        
        Args:
            document_path: Path to the document file
            metadata: Optional metadata about the document
            
        Returns:
            Dictionary containing processing results
        """
        try:
            # Generate unique ID for the document
            doc_id = str(uuid.uuid4())
            
            # Read document content
            with open(document_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract text and generate embeddings
            # Note: In a real implementation, this would use a proper text extraction
            # and embedding generation model
            text_chunks = self._chunk_text(content)
            
            # Store document metadata in MongoDB
            doc_metadata = {
                'doc_id': doc_id,
                'filename': os.path.basename(document_path),
                'processed_at': datetime.now().isoformat(),
                'chunk_count': len(text_chunks),
                **(metadata or {})
            }
            
            self.db.vc_documents.insert_one(doc_metadata)
            
            # Store vectors in ChromaDB
            for i, chunk in enumerate(text_chunks):
                chunk_id = f"{doc_id}_chunk_{i}"
                self.collection.add(
                    ids=[chunk_id],
                    documents=[chunk],
                    metadatas=[{
                        'doc_id': doc_id,
                        'chunk_index': i,
                        'total_chunks': len(text_chunks)
                    }]
                )
            
            return {
                'success': True,
                'doc_id': doc_id,
                'chunks_processed': len(text_chunks)
            }
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_similar(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents using vector similarity
        
        Args:
            query: Search query text
            limit: Maximum number of results to return
            
        Returns:
            List of similar documents with scores
        """
        try:
            # Query the vector database
            results = self.collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                doc_id = results['metadatas'][0][i]['doc_id']
                chunk_index = results['metadatas'][0][i]['chunk_index']
                
                # Get full document metadata from MongoDB
                doc_metadata = self.db.vc_documents.find_one({'doc_id': doc_id})
                
                formatted_results.append({
                    'doc_id': doc_id,
                    'chunk_index': chunk_index,
                    'score': float(results['distances'][0][i]),
                    'text': results['documents'][0][i],
                    'metadata': doc_metadata
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching similar documents: {str(e)}")
            return []
    
    def _chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """
        Split text into chunks for processing
        
        Args:
            text: Text to chunk
            chunk_size: Maximum size of each chunk
            
        Returns:
            List of text chunks
        """
        # Simple chunking by size
        # In a real implementation, this would use more sophisticated
        # text chunking strategies
        chunks = []
        current_chunk = ""
        
        for paragraph in text.split('\n\n'):
            if len(current_chunk) + len(paragraph) > chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n"
                current_chunk += paragraph
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks 