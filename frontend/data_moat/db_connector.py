"""
Data Moat Database Connector for SustainaTrend™

This module provides database connectivity for the enhanced document processing pipeline
that creates a defensible data moat through enriched document analysis and storage.
"""

import os
import logging
import json
import psycopg2
from psycopg2.extras import Json, DictCursor
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

# Configure logging
logger = logging.getLogger(__name__)

class DataMoatDBConnector:
    """Database connector for the data moat implementation"""
    
    def __init__(self):
        """Initialize the database connector"""
        self.connection = None
        self.connect()
    
    def connect(self):
        """Connect to the PostgreSQL database"""
        try:
            db_url = os.environ.get('DATABASE_URL')
            if not db_url:
                logger.error("DATABASE_URL not found in environment variables")
                return False
                
            self.connection = psycopg2.connect(db_url)
            logger.info("Successfully connected to PostgreSQL database")
            return True
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
            return False
    
    def store_document(self, 
                      content: str, 
                      document_type: str,
                      company_id: int = 1,  # Default company ID if not specified
                      metadata: Dict[str, Any] = None,
                      embeddings: Dict[str, Any] = None) -> Optional[int]:
        """
        Store a document in the document_store table
        
        Args:
            content: Document content (extracted text)
            document_type: Type of document (e.g., 'sustainability_report', 'esg_disclosure')
            company_id: ID of the company the document belongs to
            metadata: Document metadata
            embeddings: Document embeddings
            
        Returns:
            ID of the inserted document or None if insertion failed
        """
        try:
            if self.connection is None or self.connection.closed:
                if not self.connect():
                    return None
            
            cursor = self.connection.cursor()
            
            # Insert the document
            query = """
            INSERT INTO document_store 
            (company_id, document_type, content, metadata, embeddings, processing_status, last_processed) 
            VALUES (%s, %s, %s, %s, %s, %s, %s) 
            RETURNING id
            """
            
            # Prepare values
            metadata = metadata or {}
            embeddings = embeddings or {}
            
            values = (
                company_id,
                document_type,
                content,
                Json(metadata),
                Json(embeddings),
                'processing',  # Initial status
                datetime.now()
            )
            
            cursor.execute(query, values)
            document_id = cursor.fetchone()[0]
            
            self.connection.commit()
            cursor.close()
            
            logger.info(f"Document stored with ID: {document_id}")
            return document_id
            
        except Exception as e:
            logger.error(f"Error storing document: {str(e)}")
            if self.connection:
                self.connection.rollback()
            return None
    
    def update_document_enrichment(self, 
                                  document_id: int,
                                  regulatory_mapping: Dict[str, Any] = None,
                                  extracted_metrics: Dict[str, Any] = None,
                                  document_structure: Dict[str, Any] = None,
                                  confidence_scores: Dict[str, Any] = None,
                                  processing_status: str = 'processed') -> bool:
        """
        Update a document with enrichment data
        
        Args:
            document_id: ID of the document to update
            regulatory_mapping: Mapping to regulatory frameworks
            extracted_metrics: Extracted sustainability metrics
            document_structure: Document structure information
            confidence_scores: Confidence scores for extracted data
            processing_status: Processing status ('processing', 'processed', 'failed')
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            if self.connection is None or self.connection.closed:
                if not self.connect():
                    return False
            
            cursor = self.connection.cursor()
            
            # Build the enrichment history record
            enrichment_entry = {
                'timestamp': datetime.now().isoformat(),
                'enrichment_type': 'comprehensive',
                'enrichment_version': '1.0',
                'status': processing_status
            }
            
            # Update the document
            query = """
            UPDATE document_store 
            SET regulatory_mapping = COALESCE(regulatory_mapping, '{}') || %s,
                extracted_metrics = COALESCE(extracted_metrics, '{}') || %s,
                document_structure = COALESCE(document_structure, '{}') || %s,
                confidence_scores = COALESCE(confidence_scores, '{}') || %s,
                enrichment_history = COALESCE(enrichment_history, '[]') || %s,
                processing_status = %s,
                last_processed = %s
            WHERE id = %s
            """
            
            # Prepare values
            regulatory_mapping = regulatory_mapping or {}
            extracted_metrics = extracted_metrics or {}
            document_structure = document_structure or {}
            confidence_scores = confidence_scores or {}
            
            values = (
                Json(regulatory_mapping),
                Json(extracted_metrics),
                Json(document_structure),
                Json(confidence_scores),
                Json([enrichment_entry]),  # Add to enrichment history array
                processing_status,
                datetime.now(),
                document_id
            )
            
            cursor.execute(query, values)
            self.connection.commit()
            cursor.close()
            
            logger.info(f"Document {document_id} updated with enrichment data")
            return True
            
        except Exception as e:
            logger.error(f"Error updating document enrichment: {str(e)}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def store_metrics_mapping(self, 
                             document_id: int,
                             metrics: List[Dict[str, Any]]) -> bool:
        """
        Store extracted metrics in the metrics_mapping table
        
        Args:
            document_id: ID of the document
            metrics: List of extracted metrics
            
        Returns:
            True if storage was successful, False otherwise
        """
        try:
            if self.connection is None or self.connection.closed:
                if not self.connect():
                    return False
            
            cursor = self.connection.cursor()
            
            # Prepare the base query
            query = """
            INSERT INTO metrics_mapping 
            (document_id, metric_name, metric_value, normalized_value, unit, confidence, 
             context, page_reference, framework_reference, extraction_timestamp) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Execute batch insertion
            for metric in metrics:
                values = (
                    document_id,
                    metric.get('name', ''),
                    metric.get('value', ''),
                    metric.get('normalized_value', None),
                    metric.get('unit', ''),
                    metric.get('confidence', 0.0),
                    metric.get('context', ''),
                    metric.get('page', 0),
                    Json(metric.get('frameworks', {})),
                    datetime.now()
                )
                
                cursor.execute(query, values)
            
            self.connection.commit()
            cursor.close()
            
            logger.info(f"Stored {len(metrics)} metrics for document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing metrics mapping: {str(e)}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def store_regulatory_compliance(self, 
                                  document_id: int,
                                  framework_id: str,
                                  overall_score: float,
                                  category_scores: Dict[str, Any],
                                  findings: Dict[str, Any],
                                  recommendations: Dict[str, Any],
                                  evidence_links: Dict[str, Any] = None) -> bool:
        """
        Store regulatory compliance assessment results
        
        Args:
            document_id: ID of the document
            framework_id: ID of the regulatory framework
            overall_score: Overall compliance score
            category_scores: Scores for individual categories
            findings: Compliance findings
            recommendations: Improvement recommendations
            evidence_links: Links to evidence in the document
            
        Returns:
            True if storage was successful, False otherwise
        """
        try:
            if self.connection is None or self.connection.closed:
                if not self.connect():
                    return False
            
            cursor = self.connection.cursor()
            
            # Insert the compliance assessment
            query = """
            INSERT INTO regulatory_compliance 
            (document_id, framework_id, overall_score, category_scores, findings, recommendations, evidence_links) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                document_id,
                framework_id,
                overall_score,
                Json(category_scores),
                Json(findings),
                Json(recommendations),
                Json(evidence_links or {})
            )
            
            cursor.execute(query, values)
            self.connection.commit()
            cursor.close()
            
            logger.info(f"Stored compliance assessment for document {document_id}, framework {framework_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing regulatory compliance: {str(e)}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def get_document_by_id(self, document_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID
        
        Args:
            document_id: ID of the document to retrieve
            
        Returns:
            Document data or None if retrieval failed
        """
        try:
            if self.connection is None or self.connection.closed:
                if not self.connect():
                    return None
            
            cursor = self.connection.cursor(cursor_factory=DictCursor)
            
            query = """
            SELECT * FROM document_store WHERE id = %s
            """
            
            cursor.execute(query, (document_id,))
            result = cursor.fetchone()
            
            if result:
                # Convert to dictionary
                document = dict(result)
                cursor.close()
                return document
            else:
                cursor.close()
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving document: {str(e)}")
            return None
    
    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

# Create a singleton instance
db_connector = DataMoatDBConnector()