"""
Data Ingestion Manager

Manages the collection and processing of sustainability data from various sources.
"""
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum

from backend.search_engine.data_ingestion.scrapers.web_scraper import WebScraper
from backend.search_engine.data_ingestion.processors.nlp_processor import SustainabilityNLPProcessor
from backend.search_engine.data_ingestion.sources.filings_collector import ESGFilingsCollector

logger = logging.getLogger(__name__)

class DataSourceType(Enum):
    WEB = "web"
    FILINGS = "filings"
    NEWS = "news"
    RESEARCH = "research"
    SOCIAL = "social"

class DataIngestionManager:
    """
    Manages the ingestion of sustainability data from multiple sources.
    
    This class:
    1. Coordinates data collection from various sources
    2. Preprocesses and cleans the data
    3. Extracts sustainability entities and metrics
    4. Prepares the data for indexing
    """
    
    def __init__(self):
        self.web_scraper = WebScraper()
        self.nlp_processor = SustainabilityNLPProcessor()
        self.filings_collector = ESGFilingsCollector()
        self.data_cache = {}
        
    async def ingest_data_from_source(self, 
                                     source_type: DataSourceType, 
                                     parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Ingest data from a specific source.
        
        Args:
            source_type: Type of data source to collect from
            parameters: Parameters for the data collection
            
        Returns:
            List of processed documents from the source
        """
        logger.info(f"Starting data ingestion from {source_type.value} source")
        
        try:
            raw_data = await self._collect_raw_data(source_type, parameters)
            processed_data = await self._process_raw_data(raw_data, source_type)
            
            # Cache the processed data
            cache_key = f"{source_type.value}:{parameters.get('query', 'general')}"
            self.data_cache[cache_key] = {
                "data": processed_data,
                "timestamp": datetime.now()
            }
            
            logger.info(f"Successfully ingested {len(processed_data)} documents from {source_type.value}")
            return processed_data
            
        except Exception as e:
            logger.error(f"Error ingesting data from {source_type.value}: {str(e)}")
            return []
    
    async def _collect_raw_data(self, 
                               source_type: DataSourceType, 
                               parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Collect raw data from the specified source.
        """
        if source_type == DataSourceType.WEB:
            return await self.web_scraper.scrape_sustainability_data(
                query=parameters.get("query", ""),
                max_results=parameters.get("max_results", 10)
            )
        elif source_type == DataSourceType.FILINGS:
            return await self.filings_collector.collect_esg_filings(
                company=parameters.get("company", ""),
                filing_type=parameters.get("filing_type", "all"),
                date_range=parameters.get("date_range", None)
            )
        # Implement other source types as needed
        else:
            logger.warning(f"Source type {source_type.value} not implemented yet")
            return []
    
    async def _process_raw_data(self, 
                               raw_data: List[Dict[str, Any]], 
                               source_type: DataSourceType) -> List[Dict[str, Any]]:
        """
        Process raw data with NLP to extract sustainability entities and metrics.
        """
        processed_documents = []
        
        for document in raw_data:
            # Apply NLP processing
            processed_document = await self.nlp_processor.process_document(document, source_type)
            
            if processed_document:
                # Add metadata
                processed_document["source_type"] = source_type.value
                processed_document["processed_at"] = datetime.now().isoformat()
                processed_documents.append(processed_document)
        
        return processed_documents
    
    async def run_scheduled_ingestion(self, schedule_config: Dict[str, Any]):
        """
        Run scheduled data ingestion based on configuration.
        """
        logger.info("Starting scheduled data ingestion")
        
        tasks = []
        
        for source_config in schedule_config.get("sources", []):
            source_type = DataSourceType(source_config.get("type"))
            parameters = source_config.get("parameters", {})
            
            task = asyncio.create_task(
                self.ingest_data_from_source(source_type, parameters)
            )
            tasks.append(task)
        
        # Run all ingestion tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        total_documents = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error in scheduled ingestion for source {i}: {str(result)}")
            else:
                total_documents += len(result)
        
        logger.info(f"Scheduled ingestion complete: {total_documents} documents processed")
        return total_documents