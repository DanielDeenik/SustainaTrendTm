"""
VC Benchmark Service

Handles storage, retrieval, and analysis of web search sustainability data for venture capital partners.
Provides functionality to build hybrid benchmarks from publicly available data.
"""

import os
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
import requests
from bs4 import BeautifulSoup
from ..config.database import get_mongodb_client, get_vector_db_client

# Configure logging
logger = logging.getLogger(__name__)

class VCBenchmarkService:
    """Service for VC Benchmark data collection and analysis"""
    
    def __init__(self):
        """Initialize VC Benchmark service"""
        self.mongodb = get_mongodb_client()
        self.db = self.mongodb[os.getenv('MONGODB_DATABASE', 'trendsense')]
        self.vector_db = get_vector_db_client()
        
        # Create collections if they don't exist
        self.vc_partners_collection = self.db.vc_partners
        self.sustainability_data_collection = self.db.sustainability_data
        self.benchmark_collection = self.db.vc_benchmarks
        
        # Create vector collection for semantic search
        self.vector_collection = self.vector_db.get_or_create_collection(
            name="vc_sustainability_vectors",
            metadata={"description": "VC sustainability data embeddings"}
        )
        
        logger.info("VC Benchmark Service initialized")
    
    def store_web_search_data(self, partner_name: str, search_query: str, 
                             data: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Store web search sustainability data for a VC partner
        
        Args:
            partner_name: Name of the VC partner
            search_query: The search query used
            data: List of data items from web search
            metadata: Additional metadata about the search
            
        Returns:
            Dictionary containing storage results
        """
        try:
            # Generate unique ID for this search data
            search_id = str(uuid.uuid4())
            
            # Prepare document for storage
            document = {
                "search_id": search_id,
                "partner_name": partner_name,
                "search_query": search_query,
                "data": data,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            # Store in MongoDB
            result = self.sustainability_data_collection.insert_one(document)
            
            # Extract text for vector storage
            for item in data:
                if "text" in item:
                    # Generate embedding for the text
                    # In a real implementation, this would use a proper embedding model
                    # For now, we'll just store the text
                    item_id = str(uuid.uuid4())
                    self.vector_collection.add(
                        ids=[item_id],
                        documents=[item["text"]],
                        metadatas=[{
                            "search_id": search_id,
                            "partner_name": partner_name,
                            "source": item.get("source", "unknown"),
                            "date": item.get("date", datetime.now().isoformat())
                        }]
                    )
            
            return {
                "success": True,
                "search_id": search_id,
                "items_stored": len(data)
            }
            
        except Exception as e:
            logger.error(f"Error storing web search data: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def add_vc_partner(self, partner_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new VC partner to the database
        
        Args:
            partner_data: Data about the VC partner
            
        Returns:
            Dictionary containing operation results
        """
        try:
            # Generate unique ID if not provided
            if "partner_id" not in partner_data:
                partner_data["partner_id"] = str(uuid.uuid4())
            
            # Add timestamps
            partner_data["created_at"] = datetime.now().isoformat()
            partner_data["updated_at"] = datetime.now().isoformat()
            
            # Store in MongoDB
            result = self.vc_partners_collection.insert_one(partner_data)
            
            return {
                "success": True,
                "partner_id": partner_data["partner_id"]
            }
            
        except Exception as e:
            logger.error(f"Error adding VC partner: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_vc_partner(self, partner_id: str) -> Dict[str, Any]:
        """
        Get VC partner data by ID
        
        Args:
            partner_id: ID of the VC partner
            
        Returns:
            Dictionary containing partner data
        """
        try:
            partner = self.vc_partners_collection.find_one({"partner_id": partner_id})
            
            if partner:
                # Convert ObjectId to string for JSON serialization
                partner["_id"] = str(partner["_id"])
                return {
                    "success": True,
                    "partner": partner
                }
            else:
                return {
                    "success": False,
                    "error": "Partner not found"
                }
                
        except Exception as e:
            logger.error(f"Error getting VC partner: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_sustainability_data(self, partner_name: Optional[str] = None, 
                               limit: int = 100) -> Dict[str, Any]:
        """
        Get sustainability data for VC partners
        
        Args:
            partner_name: Optional filter by partner name
            limit: Maximum number of results to return
            
        Returns:
            Dictionary containing sustainability data
        """
        try:
            # Build query
            query = {}
            if partner_name:
                query["partner_name"] = partner_name
            
            # Get data from MongoDB
            cursor = self.sustainability_data_collection.find(query).limit(limit)
            data = list(cursor)
            
            # Convert ObjectId to string for JSON serialization
            for item in data:
                item["_id"] = str(item["_id"])
            
            return {
                "success": True,
                "data": data,
                "count": len(data)
            }
            
        except Exception as e:
            logger.error(f"Error getting sustainability data: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_benchmark(self, benchmark_name: str, 
                        criteria: Dict[str, Any],
                        description: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new benchmark for VC sustainability
        
        Args:
            benchmark_name: Name of the benchmark
            criteria: Criteria for the benchmark
            description: Optional description of the benchmark
            
        Returns:
            Dictionary containing benchmark data
        """
        try:
            # Generate unique ID
            benchmark_id = str(uuid.uuid4())
            
            # Prepare benchmark document
            benchmark = {
                "benchmark_id": benchmark_id,
                "name": benchmark_name,
                "description": description or f"Benchmark for {benchmark_name}",
                "criteria": criteria,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Store in MongoDB
            result = self.benchmark_collection.insert_one(benchmark)
            
            return {
                "success": True,
                "benchmark_id": benchmark_id
            }
            
        except Exception as e:
            logger.error(f"Error creating benchmark: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def evaluate_partner_against_benchmark(self, partner_id: str, 
                                         benchmark_id: str) -> Dict[str, Any]:
        """
        Evaluate a VC partner against a benchmark
        
        Args:
            partner_id: ID of the VC partner
            benchmark_id: ID of the benchmark
            
        Returns:
            Dictionary containing evaluation results
        """
        try:
            # Get partner data
            partner_result = self.get_vc_partner(partner_id)
            if not partner_result["success"]:
                return partner_result
            
            partner = partner_result["partner"]
            
            # Get benchmark data
            benchmark = self.benchmark_collection.find_one({"benchmark_id": benchmark_id})
            if not benchmark:
                return {
                    "success": False,
                    "error": "Benchmark not found"
                }
            
            # Get sustainability data for the partner
            data_result = self.get_sustainability_data(partner_name=partner["name"])
            if not data_result["success"]:
                return data_result
            
            sustainability_data = data_result["data"]
            
            # Evaluate against benchmark criteria
            # This is a simplified evaluation - in a real implementation,
            # this would use more sophisticated analysis
            evaluation = {
                "partner_id": partner_id,
                "partner_name": partner["name"],
                "benchmark_id": benchmark_id,
                "benchmark_name": benchmark["name"],
                "evaluated_at": datetime.now().isoformat(),
                "overall_score": 0,
                "criteria_scores": {},
                "recommendations": []
            }
            
            # Calculate scores for each criterion
            total_score = 0
            criteria_count = 0
            
            for criterion, weight in benchmark["criteria"].items():
                # Simple scoring logic - in a real implementation,
                # this would use more sophisticated analysis
                score = self._evaluate_criterion(criterion, sustainability_data)
                evaluation["criteria_scores"][criterion] = score
                
                total_score += score * weight
                criteria_count += 1
            
            # Calculate overall score
            if criteria_count > 0:
                evaluation["overall_score"] = total_score / criteria_count
            
            # Generate recommendations
            evaluation["recommendations"] = self._generate_recommendations(
                evaluation["criteria_scores"], 
                benchmark["criteria"]
            )
            
            # Store evaluation
            self.db.vc_evaluations.insert_one(evaluation)
            
            return {
                "success": True,
                "evaluation": evaluation
            }
            
        except Exception as e:
            logger.error(f"Error evaluating partner against benchmark: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _evaluate_criterion(self, criterion: str, data: List[Dict[str, Any]]) -> float:
        """
        Evaluate a single criterion against sustainability data
        
        Args:
            criterion: The criterion to evaluate
            data: Sustainability data to evaluate against
            
        Returns:
            Score between 0 and 1
        """
        # This is a simplified implementation
        # In a real system, this would use more sophisticated analysis
        
        # For now, just return a random score
        import random
        return random.uniform(0.3, 0.9)
    
    def _generate_recommendations(self, scores: Dict[str, float], 
                                criteria: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on evaluation scores
        
        Args:
            scores: Dictionary of criterion scores
            criteria: Dictionary of benchmark criteria
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Generate recommendations based on low scores
        for criterion, score in scores.items():
            if score < 0.6:
                recommendations.append(f"Improve {criterion} performance")
        
        # Add some generic recommendations
        if len(recommendations) < 3:
            recommendations.append("Consider publishing more sustainability data")
            recommendations.append("Set specific sustainability targets")
            recommendations.append("Engage with portfolio companies on sustainability")
        
        return recommendations[:3]  # Return top 3 recommendations 