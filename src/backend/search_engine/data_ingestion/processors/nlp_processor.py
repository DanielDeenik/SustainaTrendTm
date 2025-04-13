"""
NLP Processor for Sustainability Data

Specialized NLP processing for sustainability content, including:
- Entity extraction for sustainability metrics, companies, and initiatives
- Topic modeling and classification for sustainability content
- Sentiment analysis for ESG topics
"""
import logging
import re
from typing import Dict, List, Any, Optional, Tuple, Set
import json
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class SustainabilityEntityType(Enum):
    """Types of sustainability entities that can be extracted."""
    COMPANY = "company"
    METRIC = "metric"
    INITIATIVE = "initiative"
    REGULATION = "regulation"
    FRAMEWORK = "framework"
    TOPIC = "topic"

class SustainabilityNLPProcessor:
    """
    NLP processor specialized for sustainability content.
    
    This class:
    1. Processes documents to extract sustainability-related entities
    2. Performs topic modeling and classification
    3. Analyzes sentiment around ESG topics
    """
    
    def __init__(self):
        """Initialize the processor with sustainability-specific NLP resources."""
        # Load sustainability entity dictionaries
        self.companies = self._load_entity_dict("companies")
        self.metrics = self._load_entity_dict("metrics")
        self.initiatives = self._load_entity_dict("initiatives")
        self.regulations = self._load_entity_dict("regulations")
        self.frameworks = self._load_entity_dict("frameworks")
        
        # Topic models and classifiers
        self.sustainability_topics = {
            "emissions": ["carbon", "emissions", "greenhouse gas", "ghg", "climate", "co2", "methane", "carbon footprint"],
            "energy": ["renewable", "energy efficiency", "solar", "wind", "energy consumption", "fossil fuel"],
            "water": ["water usage", "water stress", "water conservation", "water quality", "water management"],
            "waste": ["waste", "recycling", "circular economy", "landfill", "waste reduction", "zero waste"],
            "biodiversity": ["biodiversity", "ecosystem", "habitat", "species", "conservation", "nature", "wildlife"],
            "social_diversity": ["diversity", "inclusion", "gender", "equality", "minority", "representation"],
            "social_labor": ["labor", "workers rights", "supply chain", "working conditions", "human rights"],
            "social_community": ["community", "engagement", "philanthropy", "donation", "volunteer", "social impact"],
            "governance_ethics": ["ethics", "business conduct", "corruption", "bribery", "transparency"],
            "governance_board": ["board", "directors", "executive", "compensation", "leadership", "governance structure"]
        }
        
        # Initialize sentiment analysis terms for ESG contexts
        self.sentiment_terms = {
            "positive": ["improve", "reduce", "decrease", "increase", "benefit", "effective", "success", 
                         "sustainable", "renewable", "responsible", "efficient", "innovative", "progress"],
            "negative": ["risk", "threat", "concern", "violate", "hazard", "fail", "issue", "problem", 
                         "controversy", "pollute", "waste", "damage", "harmful", "breach"]
        }
    
    def _load_entity_dict(self, entity_type: str) -> Dict[str, Any]:
        """
        Load entity dictionary from file or return mock data if file doesn't exist.
        
        In a production system, this would load from a database or well-maintained file.
        """
        # For now, return mock data based on entity type
        if entity_type == "companies":
            return {
                "apple": {"id": "AAPL", "sector": "Technology"},
                "microsoft": {"id": "MSFT", "sector": "Technology"},
                "amazon": {"id": "AMZN", "sector": "Retail/Technology"},
                "walmart": {"id": "WMT", "sector": "Retail"},
                "exxon": {"id": "XOM", "sector": "Energy"},
                "bp": {"id": "BP", "sector": "Energy"},
                "jpmorgan": {"id": "JPM", "sector": "Finance"}
            }
        elif entity_type == "metrics":
            return {
                "carbon emissions": {"unit": "tCO2e", "category": "emissions"},
                "energy consumption": {"unit": "MWh", "category": "energy"},
                "water usage": {"unit": "m3", "category": "water"},
                "waste generated": {"unit": "metric tons", "category": "waste"},
                "renewable energy": {"unit": "%", "category": "energy"},
                "gender diversity": {"unit": "%", "category": "social"}
            }
        elif entity_type == "initiatives":
            return {
                "science based targets": {"id": "SBTi", "type": "emissions"},
                "re100": {"id": "RE100", "type": "energy"},
                "carbon neutral": {"id": "CN", "type": "emissions"},
                "net zero": {"id": "NZ", "type": "emissions"},
                "circular economy": {"id": "CE", "type": "waste"}
            }
        elif entity_type == "regulations":
            return {
                "eu taxonomy": {"region": "EU", "focus": "sustainable finance"},
                "sfdr": {"region": "EU", "focus": "sustainable finance disclosure"},
                "csrd": {"region": "EU", "focus": "corporate sustainability reporting"},
                "tcfd": {"region": "global", "focus": "climate financial disclosure"},
                "sec climate disclosure": {"region": "US", "focus": "climate disclosure"}
            }
        elif entity_type == "frameworks":
            return {
                "gri": {"full_name": "Global Reporting Initiative", "focus": "general sustainability"},
                "sasb": {"full_name": "Sustainability Accounting Standards Board", "focus": "industry-specific"},
                "cdp": {"full_name": "Carbon Disclosure Project", "focus": "environmental"},
                "djsi": {"full_name": "Dow Jones Sustainability Indices", "focus": "investment"},
                "issb": {"full_name": "International Sustainability Standards Board", "focus": "disclosure standards"}
            }
        return {}
    
    async def process_document(self, 
                               document: Dict[str, Any], 
                               source_type: Any) -> Dict[str, Any]:
        """
        Process a document with NLP techniques to extract sustainability entities and insights.
        
        Args:
            document: Document to process
            source_type: Type of source the document came from
            
        Returns:
            Processed document with extracted entities and insights
        """
        try:
            # Get document content
            content = document.get("content", "")
            title = document.get("title", "")
            
            if not content:
                logger.warning("Empty document content, skipping NLP processing")
                return document
            
            # Process the document
            document["entities"] = self._extract_sustainability_entities(title, content)
            document["topics"] = self._classify_sustainability_topics(content)
            document["summary"] = self._generate_sustainability_summary(title, content)
            document["sentiment"] = self._analyze_esg_sentiment(content)
            
            # Run relevance evaluation - add a flag if document seems highly relevant
            document["sustainability_relevance"] = self._evaluate_sustainability_relevance(document)
            
            logger.debug(f"Processed document: {document.get('title', 'Untitled')}")
            return document
            
        except Exception as e:
            logger.error(f"Error processing document with NLP: {str(e)}")
            # Return original document if processing fails
            return document
    
    def _extract_sustainability_entities(self, 
                                         title: str, 
                                         content: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract sustainability-related entities from document content.
        
        This includes:
        - Companies mentioned
        - Sustainability metrics
        - Sustainability initiatives
        - Regulations and frameworks
        """
        entities = {
            "companies": [],
            "metrics": [],
            "initiatives": [],
            "regulations": [],
            "frameworks": []
        }
        
        # Combine title and content for entity extraction, with title weighted more
        text = f"{title} {title} {content}"
        text_lower = text.lower()
        
        # Extract companies
        for company, details in self.companies.items():
            if company.lower() in text_lower:
                entities["companies"].append({
                    "name": company,
                    "id": details.get("id", ""),
                    "sector": details.get("sector", ""),
                    "mentions": len(re.findall(r"\b" + re.escape(company) + r"\b", text_lower, re.IGNORECASE))
                })
        
        # Extract metrics
        for metric, details in self.metrics.items():
            if metric.lower() in text_lower:
                # Try to extract values associated with the metric
                value_pattern = f"{metric}.*?(\d+[\d,.]*)\\s*({details.get('unit', '')})"
                value_matches = re.findall(value_pattern, text_lower, re.IGNORECASE)
                
                value = None
                unit = details.get("unit", "")
                if value_matches:
                    value = value_matches[0][0]
                    if value_matches[0][1]:
                        unit = value_matches[0][1]
                
                entities["metrics"].append({
                    "name": metric,
                    "category": details.get("category", ""),
                    "value": value,
                    "unit": unit,
                    "mentions": len(re.findall(r"\b" + re.escape(metric) + r"\b", text_lower, re.IGNORECASE))
                })
        
        # Extract initiatives
        for initiative, details in self.initiatives.items():
            if initiative.lower() in text_lower:
                entities["initiatives"].append({
                    "name": initiative,
                    "id": details.get("id", ""),
                    "type": details.get("type", ""),
                    "mentions": len(re.findall(r"\b" + re.escape(initiative) + r"\b", text_lower, re.IGNORECASE))
                })
        
        # Extract regulations
        for regulation, details in self.regulations.items():
            if regulation.lower() in text_lower:
                entities["regulations"].append({
                    "name": regulation,
                    "region": details.get("region", ""),
                    "focus": details.get("focus", ""),
                    "mentions": len(re.findall(r"\b" + re.escape(regulation) + r"\b", text_lower, re.IGNORECASE))
                })
        
        # Extract frameworks
        for framework, details in self.frameworks.items():
            if framework.lower() in text_lower or details.get("full_name", "").lower() in text_lower:
                entities["frameworks"].append({
                    "name": framework,
                    "full_name": details.get("full_name", ""),
                    "focus": details.get("focus", ""),
                    "mentions": len(re.findall(r"\b" + re.escape(framework) + r"\b", text_lower, re.IGNORECASE))
                })
        
        return entities
    
    def _classify_sustainability_topics(self, content: str) -> List[Dict[str, Any]]:
        """
        Classify the document into sustainability topics based on keyword presence.
        """
        content_lower = content.lower()
        topics = []
        
        for topic, keywords in self.sustainability_topics.items():
            matches = 0
            for keyword in keywords:
                matches += len(re.findall(r"\b" + re.escape(keyword) + r"\b", content_lower, re.IGNORECASE))
            
            if matches > 0:
                # Calculate confidence based on number of keyword matches
                confidence = min(100, matches * 10)
                
                topics.append({
                    "topic": topic,
                    "confidence": confidence,
                    "matches": matches
                })
        
        # Sort by confidence (highest first)
        topics.sort(key=lambda x: x["confidence"], reverse=True)
        return topics
    
    def _generate_sustainability_summary(self, title: str, content: str) -> str:
        """
        Generate a summary focused on sustainability aspects of the document.
        
        This would use more advanced NLP in a production system, but for now
        we'll use a simple approach that extracts sentences containing 
        sustainability keywords.
        """
        # Get sentences from content
        sentences = re.split(r'(?<=[.!?])\s+', content)
        
        # Score sentences based on sustainability keywords
        scored_sentences = []
        for sentence in sentences:
            score = 0
            # Count sustainability keywords
            for topic_keywords in self.sustainability_topics.values():
                for keyword in topic_keywords:
                    if keyword.lower() in sentence.lower():
                        score += 1
            
            if score > 0:
                scored_sentences.append((sentence, score))
        
        # Sort by score (highest first)
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # Take top sentences (at most 5)
        top_sentences = [sentence for sentence, _ in scored_sentences[:5]]
        
        if not top_sentences:
            return "No significant sustainability content found."
        
        return " ".join(top_sentences)
    
    def _analyze_esg_sentiment(self, content: str) -> Dict[str, Any]:
        """
        Analyze sentiment specifically for ESG topics.
        """
        content_lower = content.lower()
        
        # Count positive and negative sentiment terms
        positive_count = sum(content_lower.count(term) for term in self.sentiment_terms["positive"])
        negative_count = sum(content_lower.count(term) for term in self.sentiment_terms["negative"])
        
        total_count = positive_count + negative_count
        if total_count == 0:
            sentiment_score = 0
        else:
            sentiment_score = (positive_count - negative_count) / total_count
            # Normalize to -100 to 100 scale
            sentiment_score = int(sentiment_score * 100)
        
        # Determine sentiment category
        if sentiment_score > 30:
            sentiment = "positive"
        elif sentiment_score < -30:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "score": sentiment_score,
            "sentiment": sentiment,
            "positive_terms": positive_count,
            "negative_terms": negative_count
        }
    
    def _evaluate_sustainability_relevance(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate how relevant the document is to sustainability topics.
        """
        # Calculate an overall relevance score based on:
        # 1. Number of sustainability entities extracted
        # 2. Topic classification confidence
        # 3. Presence of sustainability metrics
        
        relevance_score = 0
        
        # 1. Count entities
        entities = document.get("entities", {})
        entity_count = sum(len(entity_list) for entity_list in entities.values())
        relevance_score += min(50, entity_count * 5)  # Cap at 50 points
        
        # 2. Consider topic classification confidence
        topics = document.get("topics", [])
        if topics:
            # Use the confidence of the top topic
            relevance_score += min(30, topics[0].get("confidence", 0) * 0.3)  # Cap at 30 points
        
        # 3. Bonus for having actual metrics
        metrics = entities.get("metrics", [])
        has_values = any(metric.get("value") for metric in metrics)
        if has_values:
            relevance_score += 20  # Bonus 20 points for having numeric metrics
        
        # Determine relevance category
        if relevance_score >= 70:
            relevance = "high"
        elif relevance_score >= 40:
            relevance = "medium"
        else:
            relevance = "low"
        
        return {
            "score": relevance_score,
            "relevance": relevance,
            "entity_count": entity_count,
            "has_metrics": has_values
        }