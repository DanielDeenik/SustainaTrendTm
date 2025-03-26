"""
Database Connector for Data Moat Functionality

This module provides database connectivity for the data moat functionality,
interacting with PostgreSQL to store and retrieve enhanced document data.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

# Configure logging
logger = logging.getLogger(__name__)

class DatabaseConnector:
    """Database connector for data moat functionality"""
    
    def __init__(self):
        """Initialize the database connector"""
        self.connection = None
        self.connected = False
        
        # Try to connect to the database
        try:
            self.connection = psycopg2.connect(os.environ.get('DATABASE_URL'))
            self.connected = True
            logger.info("Successfully connected to PostgreSQL database")
            
            # Create tables if they don't exist
            self._create_tables()
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL database: {str(e)}")
    
    def _create_tables(self):
        """Create the necessary tables if they don't exist"""
        if not self.connection:
            return
        
        try:
            with self.connection.cursor() as cursor:
                # Create document_store_enhanced table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS document_store_enhanced (
                        id SERIAL PRIMARY KEY,
                        content TEXT NOT NULL,
                        document_type VARCHAR(100) NOT NULL,
                        metadata JSONB DEFAULT '{}',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        processing_status VARCHAR(50) DEFAULT 'pending',
                        document_structure JSONB DEFAULT '{}'
                    )
                """)
                
                # Create metrics_mapping table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS metrics_mapping (
                        id SERIAL PRIMARY KEY,
                        document_id INTEGER REFERENCES document_store_enhanced(id),
                        metrics JSONB DEFAULT '[]',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create regulatory_compliance table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS regulatory_compliance (
                        id SERIAL PRIMARY KEY,
                        document_id INTEGER REFERENCES document_store_enhanced(id),
                        framework_id VARCHAR(100) NOT NULL,
                        overall_score FLOAT DEFAULT 0.0,
                        category_scores JSONB DEFAULT '{}',
                        findings JSONB DEFAULT '{}',
                        recommendations JSONB DEFAULT '{}',
                        evidence_links JSONB DEFAULT '{}',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                self.connection.commit()
                logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
    
    def store_document(self, content: str, document_type: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[int]:
        """
        Store a document in the database
        
        Args:
            content: Document content
            document_type: Type of document
            metadata: Document metadata
            
        Returns:
            Document ID if successful, None otherwise
        """
        if not self.connection:
            return None
        
        try:
            with self.connection.cursor() as cursor:
                # Insert document
                cursor.execute(
                    """
                    INSERT INTO document_store_enhanced (content, document_type, metadata)
                    VALUES (%s, %s, %s)
                    RETURNING id
                    """,
                    (content, document_type, json.dumps(metadata or {}))
                )
                
                document_id = cursor.fetchone()[0]
                self.connection.commit()
                
                logger.info(f"Document stored successfully with ID: {document_id}")
                return document_id
        except Exception as e:
            logger.error(f"Error storing document: {str(e)}")
            return None
    
    def update_document_enrichment(self, document_id: int, 
                                 regulatory_mapping: Optional[Dict[str, Any]] = None,
                                 extracted_metrics: Optional[Dict[str, Any]] = None,
                                 document_structure: Optional[Dict[str, Any]] = None,
                                 confidence_scores: Optional[Dict[str, Any]] = None,
                                 processing_status: str = 'processing') -> bool:
        """
        Update document enrichment data
        
        Args:
            document_id: Document ID
            regulatory_mapping: Regulatory mapping data
            extracted_metrics: Extracted metrics data
            document_structure: Document structure data
            confidence_scores: Confidence scores
            processing_status: Processing status
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connection:
            return False
        
        try:
            with self.connection.cursor() as cursor:
                # Update document with enrichment data
                cursor.execute(
                    """
                    UPDATE document_store_enhanced
                    SET 
                        document_structure = %s,
                        metadata = jsonb_set(
                            coalesce(metadata, '{}'), 
                            '{regulatory_mapping}', 
                            %s
                        ),
                        metadata = jsonb_set(
                            coalesce(metadata, '{}'), 
                            '{confidence_scores}', 
                            %s
                        ),
                        processing_status = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (
                        json.dumps(document_structure or {}),
                        json.dumps(regulatory_mapping or {}),
                        json.dumps(confidence_scores or {}),
                        processing_status,
                        document_id
                    )
                )
                
                self.connection.commit()
                logger.info(f"Document enrichment updated successfully for ID: {document_id}")
                return True
        except Exception as e:
            logger.error(f"Error updating document enrichment: {str(e)}")
            return False
    
    def store_metrics_mapping(self, document_id: int, metrics: List[Dict[str, Any]]) -> bool:
        """
        Store metrics mapping for a document
        
        Args:
            document_id: Document ID
            metrics: Metrics data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connection:
            return False
        
        try:
            with self.connection.cursor() as cursor:
                # Check if metrics mapping already exists for this document
                cursor.execute(
                    """
                    SELECT id FROM metrics_mapping
                    WHERE document_id = %s
                    """,
                    (document_id,)
                )
                
                result = cursor.fetchone()
                
                if result:
                    # Update existing mapping
                    cursor.execute(
                        """
                        UPDATE metrics_mapping
                        SET 
                            metrics = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE document_id = %s
                        """,
                        (json.dumps(metrics), document_id)
                    )
                else:
                    # Insert new mapping
                    cursor.execute(
                        """
                        INSERT INTO metrics_mapping (document_id, metrics)
                        VALUES (%s, %s)
                        """,
                        (document_id, json.dumps(metrics))
                    )
                
                self.connection.commit()
                logger.info(f"Metrics mapping stored successfully for document ID: {document_id}")
                return True
        except Exception as e:
            logger.error(f"Error storing metrics mapping: {str(e)}")
            return False
    
    def store_regulatory_compliance(self, document_id: int, framework_id: str,
                                  overall_score: float,
                                  category_scores: Dict[str, float],
                                  findings: Dict[str, Any],
                                  recommendations: Dict[str, str],
                                  evidence_links: Dict[str, Any]) -> bool:
        """
        Store regulatory compliance assessment for a document
        
        Args:
            document_id: Document ID
            framework_id: Framework ID
            overall_score: Overall compliance score
            category_scores: Category scores
            findings: Compliance findings
            recommendations: Recommendations
            evidence_links: Evidence links
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connection:
            return False
        
        try:
            with self.connection.cursor() as cursor:
                # Check if compliance assessment already exists for this document and framework
                cursor.execute(
                    """
                    SELECT id FROM regulatory_compliance
                    WHERE document_id = %s AND framework_id = %s
                    """,
                    (document_id, framework_id)
                )
                
                result = cursor.fetchone()
                
                if result:
                    # Update existing assessment
                    cursor.execute(
                        """
                        UPDATE regulatory_compliance
                        SET 
                            overall_score = %s,
                            category_scores = %s,
                            findings = %s,
                            recommendations = %s,
                            evidence_links = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE document_id = %s AND framework_id = %s
                        """,
                        (
                            overall_score,
                            json.dumps(category_scores),
                            json.dumps(findings),
                            json.dumps(recommendations),
                            json.dumps(evidence_links),
                            document_id,
                            framework_id
                        )
                    )
                else:
                    # Insert new assessment
                    cursor.execute(
                        """
                        INSERT INTO regulatory_compliance (
                            document_id, framework_id, overall_score, category_scores,
                            findings, recommendations, evidence_links
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            document_id,
                            framework_id,
                            overall_score,
                            json.dumps(category_scores),
                            json.dumps(findings),
                            json.dumps(recommendations),
                            json.dumps(evidence_links)
                        )
                    )
                
                self.connection.commit()
                logger.info(f"Regulatory compliance stored for document ID: {document_id}, framework: {framework_id}")
                return True
        except Exception as e:
            logger.error(f"Error storing regulatory compliance: {str(e)}")
            return False
    
    def get_document_by_id(self, document_id: Union[int, str]) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID
        
        Args:
            document_id: Document ID
            
        Returns:
            Document data if found, None otherwise
        """
        if not self.connection:
            return None
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get document
                cursor.execute(
                    """
                    SELECT * FROM document_store_enhanced
                    WHERE id = %s
                    """,
                    (document_id,)
                )
                
                document = cursor.fetchone()
                
                if not document:
                    return None
                
                # Get metrics mapping
                cursor.execute(
                    """
                    SELECT metrics FROM metrics_mapping
                    WHERE document_id = %s
                    """,
                    (document_id,)
                )
                
                metrics_result = cursor.fetchone()
                metrics = json.loads(metrics_result['metrics']) if metrics_result else []
                
                # Get compliance assessments
                cursor.execute(
                    """
                    SELECT * FROM regulatory_compliance
                    WHERE document_id = %s
                    """,
                    (document_id,)
                )
                
                compliance_results = cursor.fetchall()
                compliance = []
                
                for result in compliance_results:
                    compliance_item = dict(result)
                    
                    # Convert JSON strings to Python objects
                    for key in ['category_scores', 'findings', 'recommendations', 'evidence_links']:
                        if isinstance(compliance_item[key], str):
                            compliance_item[key] = json.loads(compliance_item[key])
                        elif compliance_item[key] is None:
                            compliance_item[key] = {}
                    
                    compliance.append(compliance_item)
                
                # Create complete document data
                document_data = dict(document)
                
                # Convert JSON strings to Python objects
                for key in ['metadata', 'document_structure']:
                    if isinstance(document_data[key], str):
                        document_data[key] = json.loads(document_data[key])
                    elif document_data[key] is None:
                        document_data[key] = {}
                
                # Add metrics and compliance data
                document_data['metrics'] = metrics
                document_data['compliance'] = compliance
                
                return document_data
        except Exception as e:
            logger.error(f"Error getting document by ID: {str(e)}")
            return None
    
    def get_metrics_for_document(self, document_id: Union[int, str]) -> List[Dict[str, Any]]:
        """
        Get metrics for a document
        
        Args:
            document_id: Document ID
            
        Returns:
            List of metrics
        """
        if not self.connection:
            return []
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get metrics mapping
                cursor.execute(
                    """
                    SELECT metrics FROM metrics_mapping
                    WHERE document_id = %s
                    """,
                    (document_id,)
                )
                
                result = cursor.fetchone()
                
                if not result:
                    return []
                
                return json.loads(result['metrics'])
        except Exception as e:
            logger.error(f"Error getting metrics for document: {str(e)}")
            return []
    
    def get_compliance_for_document(self, document_id: Union[int, str]) -> List[Dict[str, Any]]:
        """
        Get compliance assessments for a document
        
        Args:
            document_id: Document ID
            
        Returns:
            List of compliance assessments
        """
        if not self.connection:
            return []
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get compliance assessments
                cursor.execute(
                    """
                    SELECT * FROM regulatory_compliance
                    WHERE document_id = %s
                    """,
                    (document_id,)
                )
                
                results = cursor.fetchall()
                compliance = []
                
                for result in results:
                    compliance_item = dict(result)
                    
                    # Convert JSON strings to Python objects
                    for key in ['category_scores', 'findings', 'recommendations', 'evidence_links']:
                        if isinstance(compliance_item[key], str):
                            compliance_item[key] = json.loads(compliance_item[key])
                        elif compliance_item[key] is None:
                            compliance_item[key] = {}
                    
                    compliance.append(compliance_item)
                
                return compliance
        except Exception as e:
            logger.error(f"Error getting compliance for document: {str(e)}")
            return []
    
    def search_documents(self, query: str, document_type: Optional[str] = None, 
                       limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Search documents by content
        
        Args:
            query: Search query
            document_type: Optional document type filter
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of matching documents
        """
        if not self.connection:
            return []
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                if document_type:
                    # Search with document type filter
                    cursor.execute(
                        """
                        SELECT id, document_type, metadata, processing_status, created_at
                        FROM document_store_enhanced
                        WHERE document_type = %s AND content ILIKE %s
                        ORDER BY created_at DESC
                        LIMIT %s OFFSET %s
                        """,
                        (document_type, f"%{query}%", limit, offset)
                    )
                else:
                    # Search without document type filter
                    cursor.execute(
                        """
                        SELECT id, document_type, metadata, processing_status, created_at
                        FROM document_store_enhanced
                        WHERE content ILIKE %s
                        ORDER BY created_at DESC
                        LIMIT %s OFFSET %s
                        """,
                        (f"%{query}%", limit, offset)
                    )
                
                results = cursor.fetchall()
                documents = []
                
                for result in results:
                    document = dict(result)
                    
                    # Convert JSON strings to Python objects
                    for key in ['metadata']:
                        if isinstance(document[key], str):
                            document[key] = json.loads(document[key])
                        elif document[key] is None:
                            document[key] = {}
                    
                    documents.append(document)
                
                return documents
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []

# Create a singleton instance
db_connector = DatabaseConnector()