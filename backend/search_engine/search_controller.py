"""
Search Controller for Sustainability Intelligence Platform

Coordinates between data ingestion, query understanding, and search components
to provide intelligent sustainability search.
"""
import logging
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from backend.search_engine.data_ingestion import DataIngestionManager
from backend.search_engine.data_ingestion.ingestion_manager import DataSourceType
from backend.search_engine.query_understanding import QueryUnderstandingEngine
from backend.search_engine.indexing import SearchIndex
from backend.search_engine.vector_search import VectorSearchEngine

logger = logging.getLogger(__name__)

class SearchController:
    """
    Coordinates the sustainability search process across all components.
    
    This class:
    1. Receives search queries
    2. Processes and enhances queries using the query understanding engine
    3. Retrieves data from appropriate sources
    4. Executes searches against multiple indexes
    5. Consolidates and ranks results
    """
    
    def __init__(self):
        """Initialize the search controller with necessary components."""
        self.query_engine = QueryUnderstandingEngine()
        self.data_manager = DataIngestionManager()
        self.search_index = SearchIndex()
        self.vector_search = VectorSearchEngine()
        
        # Cache for recently processed queries
        self.query_cache = {}
        
        # Initialize a counter for search requests
        self.search_count = 0
        self.last_search_time = None
    
    async def search(self, 
                     query: str, 
                     search_mode: str = "hybrid",
                     filters: Optional[Dict[str, Any]] = None,
                     max_results: int = 20,
                     use_cache: bool = True) -> Dict[str, Any]:
        """
        Execute a sustainability-focused search.
        
        Args:
            query: User search query
            search_mode: Search mode (hybrid, keyword, vector, realtime)
            filters: Optional filters to apply to results
            max_results: Maximum number of results to return
            use_cache: Whether to use cached results when available
            
        Returns:
            Search results with metadata
        """
        logger.info(f"Executing search: '{query}' with mode: {search_mode}")
        
        # Update stats
        self.search_count += 1
        self.last_search_time = datetime.now()
        
        # Check cache if enabled
        cache_key = f"{query}:{search_mode}:{json.dumps(filters) if filters else 'no_filters'}"
        if use_cache and cache_key in self.query_cache:
            cache_entry = self.query_cache[cache_key]
            # Only use cache if it's less than 10 minutes old
            cache_age = (datetime.now() - cache_entry["timestamp"]).total_seconds()
            if cache_age < 600:  # 10 minutes
                logger.info(f"Returning cached results for query: '{query}'")
                return cache_entry["results"]
        
        # Process query through query understanding engine
        query_data = self.query_engine.process_query(query)
        
        # Determine search strategy based on mode
        if search_mode == "realtime":
            # For realtime searches, fetch fresh data from the web
            results = await self._execute_realtime_search(query_data, filters, max_results)
        else:
            # For index-based searches, use the appropriate index
            results = await self._execute_index_search(query_data, search_mode, filters, max_results)
        
        # Cache results
        self.query_cache[cache_key] = {
            "results": results,
            "timestamp": datetime.now()
        }
        
        return results
    
    async def _execute_realtime_search(self, 
                                      query_data: Dict[str, Any],
                                      filters: Optional[Dict[str, Any]],
                                      max_results: int) -> Dict[str, Any]:
        """
        Execute a real-time search by fetching fresh data.
        
        Args:
            query_data: Processed query data
            filters: Optional filters to apply to results
            max_results: Maximum number of results to return
            
        Returns:
            Real-time search results
        """
        # Use the expanded query for better coverage
        expanded_query = query_data["expanded_query"]
        
        # Initialize search parameters
        search_params = {"query": expanded_query, "max_results": max_results}
        
        # Add filters to search parameters
        if filters:
            search_params.update(filters)
        
        # Fetch web data
        web_results = await self.data_manager.ingest_data_from_source(
            DataSourceType.WEB, search_params
        )
        
        # If we have company entities, also fetch company-specific data
        company_results = []
        for company in query_data.get("entities", {}).get("companies", []):
            company_data = await self.data_manager.ingest_data_from_source(
                DataSourceType.FILINGS, 
                {"company": company["name"], "max_results": 5}
            )
            company_results.extend(company_data)
        
        # Combine results
        all_results = web_results + company_results
        
        # Rank results by relevance to the original query
        ranked_results = self._rank_results(all_results, query_data["original_query"])
        
        # Prepare response
        return {
            "query": query_data["original_query"],
            "query_analysis": {
                "entities": query_data["entities"],
                "intents": query_data["intents"]
            },
            "mode": "realtime",
            "result_count": len(ranked_results),
            "results": ranked_results[:max_results],
            "search_time": datetime.now().isoformat()
        }
    
    async def _execute_index_search(self, 
                                   query_data: Dict[str, Any],
                                   search_mode: str,
                                   filters: Optional[Dict[str, Any]],
                                   max_results: int) -> Dict[str, Any]:
        """
        Execute a search against the index.
        
        Args:
            query_data: Processed query data
            search_mode: Search mode (hybrid, keyword, vector)
            filters: Optional filters to apply to results
            max_results: Maximum number of results to return
            
        Returns:
            Index search results
        """
        # Use the expanded query for better coverage
        expanded_query = query_data["expanded_query"]
        
        # Execute search with appropriate index
        results = self.search_index.search(expanded_query, mode=search_mode, max_results=max_results)
        
        # Apply filters if provided
        if filters:
            results = self._apply_filters(results, filters)
        
        # Prepare response
        return {
            "query": query_data["original_query"],
            "query_analysis": {
                "entities": query_data["entities"],
                "intents": query_data["intents"]
            },
            "mode": search_mode,
            "result_count": len(results),
            "results": results[:max_results],
            "search_time": datetime.now().isoformat()
        }
    
    def _rank_results(self, 
                     results: List[Dict[str, Any]], 
                     query: str) -> List[Dict[str, Any]]:
        """
        Rank search results by relevance to the query.
        
        Args:
            results: List of search results
            query: Original query string
            
        Returns:
            Ranked list of search results
        """
        query_terms = query.lower().split()
        
        # Calculate relevance scores
        for result in results:
            score = result.get("relevance_score", 0)
            
            # Boost score based on title matches
            title = result.get("title", "").lower()
            title_matches = sum(term in title for term in query_terms)
            score += title_matches * 10
            
            # Boost score based on content matches
            content = result.get("content", "").lower()
            content_matches = sum(content.count(term) for term in query_terms)
            score += min(content_matches, 10) * 2
            
            # Boost based on sustainability relevance
            if result.get("is_sustainability_report", False):
                score += 20
            
            if "sustainability_relevance" in result:
                sustainability_score = result["sustainability_relevance"].get("score", 0)
                score += sustainability_score * 0.5
            
            # Update score
            result["score"] = score
        
        # Sort by score
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return results
    
    def _apply_filters(self, 
                      results: List[Dict[str, Any]], 
                      filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply filters to search results.
        
        Args:
            results: List of search results
            filters: Filters to apply
            
        Returns:
            Filtered list of search results
        """
        filtered_results = results.copy()
        
        # Apply category filter
        if "category" in filters:
            category = filters["category"]
            filtered_results = [
                r for r in filtered_results 
                if self._matches_category(r, category)
            ]
        
        # Apply date range filter
        if "date_range" in filters and isinstance(filters["date_range"], list) and len(filters["date_range"]) == 2:
            start_date, end_date = filters["date_range"]
            filtered_results = [
                r for r in filtered_results 
                if self._matches_date_range(r, start_date, end_date)
            ]
        
        # Apply source filter
        if "source" in filters:
            source = filters["source"]
            filtered_results = [
                r for r in filtered_results 
                if r.get("source") == source
            ]
        
        # Apply company filter
        if "company" in filters:
            company = filters["company"]
            filtered_results = [
                r for r in filtered_results 
                if self._matches_company(r, company)
            ]
        
        return filtered_results
    
    def _matches_category(self, result: Dict[str, Any], category: str) -> bool:
        """Check if result matches a category filter."""
        # Check direct category field
        if "category" in result and result["category"] == category:
            return True
        
        # Check sustainability_categories list
        if "sustainability_categories" in result and category in result["sustainability_categories"]:
            return True
        
        # Check ESG topics
        if "esg_topics" in result and category in result["esg_topics"]:
            return True
        
        # Check entities
        if "entities" in result and "metrics" in result["entities"]:
            for metric in result["entities"]["metrics"]:
                if metric.get("category") == category:
                    return True
        
        return False
    
    def _matches_date_range(self, result: Dict[str, Any], start_date: str, end_date: str) -> bool:
        """Check if result matches a date range filter."""
        # Get date from result
        date = result.get("date") or result.get("filing_date") or result.get("scraped_at")
        
        if not date:
            return False
        
        # Compare with range
        return start_date <= date <= end_date
    
    def _matches_company(self, result: Dict[str, Any], company: str) -> bool:
        """Check if result matches a company filter."""
        # Check direct company field
        if "company" in result and result["company"].lower() == company.lower():
            return True
        
        # Check title for company name
        if "title" in result and company.lower() in result["title"].lower():
            return True
        
        # Check mentioned companies in entities
        if "entities" in result and "companies" in result["entities"]:
            for comp in result["entities"]["companies"]:
                if comp.get("name", "").lower() == company.lower():
                    return True
        
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the search engine.
        
        Returns:
            Dictionary with search engine statistics
        """
        return {
            "search_count": self.search_count,
            "last_search_time": self.last_search_time.isoformat() if self.last_search_time else None,
            "index_stats": self.search_index.get_stats(),
            "cache_size": len(self.query_cache)
        }