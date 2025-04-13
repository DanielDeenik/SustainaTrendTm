"""
Data Service Module
Provides data operations using MongoDB and vector database
"""
import logging
import json
from datetime import datetime
from bson import ObjectId
from config.database import get_mongodb_db, get_vector_db

# Configure logging
logger = logging.getLogger(__name__)

class DataService:
    """Service for data operations using MongoDB and vector database"""
    
    def __init__(self):
        """Initialize data service with database connections"""
        self.db = get_mongodb_db()
        self.vector_db = get_vector_db()
        
        if not self.db:
            logger.warning("MongoDB connection not available. Some features may be limited.")
        
        if not self.vector_db:
            logger.warning("Vector database connection not available. Semantic search features will be disabled.")
    
    # MongoDB Operations
    
    def save_document(self, collection, document):
        """Save a document to MongoDB"""
        if not self.db:
            return {"success": False, "error": "MongoDB connection not available"}
        
        try:
            # Add timestamp if not present
            if "created_at" not in document:
                document["created_at"] = datetime.now()
            
            # Update timestamp
            document["updated_at"] = datetime.now()
            
            # Insert document
            result = self.db[collection].insert_one(document)
            
            return {
                "success": True,
                "document_id": str(result.inserted_id)
            }
        except Exception as e:
            logger.error(f"Error saving document to {collection}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_document(self, collection, document_id):
        """Get a document from MongoDB by ID"""
        if not self.db:
            return {"success": False, "error": "MongoDB connection not available"}
        
        try:
            document = self.db[collection].find_one({"_id": ObjectId(document_id)})
            
            if document:
                # Convert ObjectId to string for JSON serialization
                document["_id"] = str(document["_id"])
                return {"success": True, "document": document}
            else:
                return {"success": False, "error": "Document not found"}
        except Exception as e:
            logger.error(f"Error getting document from {collection}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def update_document(self, collection, document_id, updates):
        """Update a document in MongoDB"""
        if not self.db:
            return {"success": False, "error": "MongoDB connection not available"}
        
        try:
            # Add update timestamp
            updates["updated_at"] = datetime.now()
            
            result = self.db[collection].update_one(
                {"_id": ObjectId(document_id)},
                {"$set": updates}
            )
            
            if result.modified_count > 0:
                return {"success": True, "modified_count": result.modified_count}
            else:
                return {"success": False, "error": "Document not found or no changes made"}
        except Exception as e:
            logger.error(f"Error updating document in {collection}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def delete_document(self, collection, document_id):
        """Delete a document from MongoDB"""
        if not self.db:
            return {"success": False, "error": "MongoDB connection not available"}
        
        try:
            result = self.db[collection].delete_one({"_id": ObjectId(document_id)})
            
            if result.deleted_count > 0:
                return {"success": True, "deleted_count": result.deleted_count}
            else:
                return {"success": False, "error": "Document not found"}
        except Exception as e:
            logger.error(f"Error deleting document from {collection}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def find_documents(self, collection, query=None, limit=100, skip=0, sort_by=None):
        """Find documents in MongoDB"""
        if not self.db:
            return {"success": False, "error": "MongoDB connection not available"}
        
        try:
            # Default query if none provided
            if query is None:
                query = {}
            
            # Create cursor
            cursor = self.db[collection].find(query)
            
            # Apply sorting if specified
            if sort_by:
                cursor = cursor.sort(sort_by)
            
            # Apply pagination
            cursor = cursor.skip(skip).limit(limit)
            
            # Convert to list and handle ObjectId serialization
            documents = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                documents.append(doc)
            
            return {"success": True, "documents": documents}
        except Exception as e:
            logger.error(f"Error finding documents in {collection}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # Vector Database Operations
    
    def add_vector(self, vector_id, vector, metadata=None):
        """Add a vector to the vector database"""
        if not self.vector_db:
            return {"success": False, "error": "Vector database connection not available"}
        
        try:
            # Ensure metadata is a dictionary
            if metadata is None:
                metadata = {}
            
            # Add timestamp
            metadata["timestamp"] = datetime.now().isoformat()
            
            # Upsert vector
            self.vector_db.upsert(vectors=[(vector_id, vector, metadata)])
            
            return {"success": True, "vector_id": vector_id}
        except Exception as e:
            logger.error(f"Error adding vector: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def query_vectors(self, query_vector, top_k=10, filter=None):
        """Query vectors from the vector database"""
        if not self.vector_db:
            return {"success": False, "error": "Vector database connection not available"}
        
        try:
            # Query vectors
            results = self.vector_db.query(
                vector=query_vector,
                top_k=top_k,
                filter=filter
            )
            
            return {"success": True, "results": results}
        except Exception as e:
            logger.error(f"Error querying vectors: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def delete_vector(self, vector_id):
        """Delete a vector from the vector database"""
        if not self.vector_db:
            return {"success": False, "error": "Vector database connection not available"}
        
        try:
            # Delete vector
            self.vector_db.delete(ids=[vector_id])
            
            return {"success": True, "vector_id": vector_id}
        except Exception as e:
            logger.error(f"Error deleting vector: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # Combined Operations
    
    def save_document_with_vector(self, collection, document, vector, vector_id=None):
        """Save a document to MongoDB and its vector to the vector database"""
        # Generate vector ID if not provided
        if vector_id is None:
            vector_id = str(ObjectId())
        
        # Save document to MongoDB
        document_result = self.save_document(collection, document)
        
        if not document_result["success"]:
            return document_result
        
        # Save vector to vector database
        vector_result = self.add_vector(vector_id, vector, {"document_id": document_result["document_id"]})
        
        if not vector_result["success"]:
            # Log warning but don't fail the operation
            logger.warning(f"Failed to save vector for document {document_result['document_id']}: {vector_result['error']}")
        
        return {
            "success": True,
            "document_id": document_result["document_id"],
            "vector_id": vector_id
        }
    
    def semantic_search(self, collection, query_vector, filter=None, top_k=10):
        """Perform semantic search using vector database and return full documents from MongoDB"""
        if not self.vector_db:
            return {"success": False, "error": "Vector database connection not available"}
        
        try:
            # Query vectors
            vector_results = self.vector_db.query(
                vector=query_vector,
                top_k=top_k,
                filter=filter
            )
            
            # Extract document IDs from vector results
            document_ids = []
            for match in vector_results.matches:
                if "document_id" in match.metadata:
                    document_ids.append(ObjectId(match.metadata["document_id"]))
            
            if not document_ids:
                return {"success": True, "documents": []}
            
            # Fetch documents from MongoDB
            documents = []
            for doc in self.db[collection].find({"_id": {"$in": document_ids}}):
                doc["_id"] = str(doc["_id"])
                documents.append(doc)
            
            return {"success": True, "documents": documents}
        except Exception as e:
            logger.error(f"Error performing semantic search: {str(e)}")
            return {"success": False, "error": str(e)} 