"""
Query Understanding Engine for Sustainability Search

Enhances search queries for better sustainability-related results through:
1. Query expansion with sustainability concepts
2. Entity and intent recognition
3. Query contextualization based on sustainability frameworks
"""
import logging
import re
from typing import Dict, List, Any, Optional, Tuple, Set, Union
import json
from enum import Enum

logger = logging.getLogger(__name__)

class QueryIntent(Enum):
    """Types of query intents that can be detected."""
    INFORMATION = "information_seeking"
    METRICS = "metrics_seeking"
    COMPARISON = "comparison"
    TREND = "trend_analysis"
    REGULATION = "regulation_seeking"
    COMPANY = "company_specific"
    RECOMMENDATION = "recommendation_seeking"

class QueryUnderstandingEngine:
    """
    Engine for understanding and enhancing sustainability search queries.
    
    This class:
    1. Detects entities and intents in queries
    2. Expands queries with relevant sustainability concepts
    3. Contextualizes queries based on ESG frameworks
    """
    
    def __init__(self):
        """Initialize the query understanding engine with relevant knowledge bases."""
        # Load sustainability knowledge base
        self.sustainability_concepts = self._load_sustainability_concepts()
        self.esg_frameworks = self._load_esg_frameworks()
        self.company_database = self._load_company_database()
        self.synonym_mapping = self._load_synonym_mapping()
        
        # Patterns for intent recognition
        self.intent_patterns = {
            QueryIntent.INFORMATION: [
                r"what is", r"how does", r"explain", r"information about", 
                r"details on", r"tell me about", r"definition of"
            ],
            QueryIntent.METRICS: [
                r"metrics for", r"measure", r"kpi", r"indicator", r"performance", 
                r"data on", r"statistics", r"figures", r"numbers"
            ],
            QueryIntent.COMPARISON: [
                r"compare", r"versus", r"vs", r"difference between", r"better than",
                r"compared to", r"against", r"relative to"
            ],
            QueryIntent.TREND: [
                r"trend", r"over time", r"increasing", r"decreasing", r"growing",
                r"evolution of", r"historical", r"forecast", r"projection", r"predict"
            ],
            QueryIntent.REGULATION: [
                r"regulation", r"compliance", r"law", r"policy", r"standard",
                r"framework", r"requirement", r"mandate", r"rule", r"guideline"
            ],
            QueryIntent.COMPANY: [
                r"company", r"corporation", r"corporate", r"business", r"firm",
                r"enterprise", r"organization"
            ],
            QueryIntent.RECOMMENDATION: [
                r"recommend", r"suggestion", r"advice", r"should", r"best practice",
                r"how to", r"improve", r"optimize", r"strategy for"
            ]
        }
    
    def _load_sustainability_concepts(self) -> Dict[str, Dict[str, Any]]:
        """
        Load sustainability concepts knowledge base.
        
        In a production system, this would load from a database or file.
        For now, returns a built-in dictionary of concepts.
        """
        return {
            "carbon emissions": {
                "category": "emissions",
                "synonyms": ["ghg emissions", "greenhouse gas emissions", "co2 emissions"],
                "related": ["carbon footprint", "carbon intensity", "scope 1", "scope 2", "scope 3"],
                "frameworks": ["GHG Protocol", "TCFD", "CDP", "SBTi"]
            },
            "renewable energy": {
                "category": "energy",
                "synonyms": ["clean energy", "green energy", "sustainable energy"],
                "related": ["solar power", "wind power", "energy transition", "energy efficiency"],
                "frameworks": ["RE100", "GRI 302", "SASB"]
            },
            "water usage": {
                "category": "water",
                "synonyms": ["water consumption", "water withdrawal", "water utilization"],
                "related": ["water stress", "water intensity", "water recycling", "wastewater"],
                "frameworks": ["CDP Water", "GRI 303", "AWS"]
            },
            "waste management": {
                "category": "waste",
                "synonyms": ["waste disposal", "waste reduction", "waste handling"],
                "related": ["circular economy", "recycling", "zero waste", "waste to energy"],
                "frameworks": ["GRI 306", "Zero Waste International Alliance"]
            },
            "biodiversity": {
                "category": "biodiversity",
                "synonyms": ["ecosystem health", "species diversity", "natural capital"],
                "related": ["habitat loss", "conservation", "ecosystem services", "deforestation"],
                "frameworks": ["TNFD", "CBD", "GRI 304"]
            },
            "diversity and inclusion": {
                "category": "social",
                "synonyms": ["D&I", "DEI", "workplace diversity"],
                "related": ["gender equality", "racial equity", "inclusive workplace"],
                "frameworks": ["GRI 405", "SASB", "UN Global Compact"]
            },
            "supply chain sustainability": {
                "category": "supply chain",
                "synonyms": ["sustainable procurement", "responsible sourcing"],
                "related": ["supplier engagement", "ethical sourcing", "scope 3 emissions"],
                "frameworks": ["GRI 308", "GRI 414", "UNGP"]
            },
            "corporate governance": {
                "category": "governance",
                "synonyms": ["board governance", "governance structure"],
                "related": ["board diversity", "executive compensation", "ethics", "transparency"],
                "frameworks": ["GRI 2", "OECD Principles", "UK Corporate Governance Code"]
            }
        }
    
    def _load_esg_frameworks(self) -> Dict[str, Dict[str, Any]]:
        """
        Load ESG frameworks knowledge base.
        
        In a production system, this would load from a database or file.
        For now, returns a built-in dictionary of frameworks.
        """
        return {
            "GRI": {
                "full_name": "Global Reporting Initiative",
                "focus": "comprehensive sustainability reporting",
                "key_metrics": ["GRI 305: Emissions", "GRI 302: Energy", "GRI 303: Water"],
                "aliases": ["Global Reporting Initiative", "GRI Standards"]
            },
            "SASB": {
                "full_name": "Sustainability Accounting Standards Board",
                "focus": "industry-specific financial materiality",
                "key_metrics": ["Varies by industry"],
                "aliases": ["Sustainability Accounting Standards Board", "SASB Standards"]
            },
            "TCFD": {
                "full_name": "Task Force on Climate-related Financial Disclosures",
                "focus": "climate risk and opportunity",
                "key_metrics": ["Climate governance", "Climate strategy", "Climate risk management"],
                "aliases": ["Task Force on Climate-related Financial Disclosures"]
            },
            "CDP": {
                "full_name": "Carbon Disclosure Project",
                "focus": "environmental impact disclosure",
                "key_metrics": ["Climate change", "Water security", "Forest risk"],
                "aliases": ["Carbon Disclosure Project"]
            },
            "SDGs": {
                "full_name": "Sustainable Development Goals",
                "focus": "global sustainability agenda",
                "key_metrics": ["17 goals covering social, environmental, and economic development"],
                "aliases": ["UN Sustainable Development Goals", "Global Goals", "SDG"]
            }
        }
    
    def _load_company_database(self) -> Dict[str, Dict[str, Any]]:
        """
        Load company database with sustainability info.
        
        In a production system, this would load from a database.
        For now, returns a small built-in dictionary of companies.
        """
        return {
            "apple": {
                "name": "Apple Inc.",
                "sector": "Technology",
                "ticker": "AAPL",
                "sustainability_initiatives": ["carbon neutral by 2030", "renewable energy"],
                "aliases": ["Apple", "Apple Inc", "Apple Inc."]
            },
            "microsoft": {
                "name": "Microsoft Corporation",
                "sector": "Technology",
                "ticker": "MSFT",
                "sustainability_initiatives": ["carbon negative by 2030", "water positive"],
                "aliases": ["Microsoft", "Microsoft Corp", "MSFT"]
            },
            "walmart": {
                "name": "Walmart Inc.",
                "sector": "Retail",
                "ticker": "WMT",
                "sustainability_initiatives": ["Project Gigaton", "zero waste"],
                "aliases": ["Walmart", "Walmart Inc", "WMT"]
            },
            "unilever": {
                "name": "Unilever PLC",
                "sector": "Consumer Goods",
                "ticker": "UL",
                "sustainability_initiatives": ["Sustainable Living Plan", "climate and nature fund"],
                "aliases": ["Unilever", "Unilever PLC", "UL"]
            }
        }
    
    def _load_synonym_mapping(self) -> Dict[str, List[str]]:
        """
        Load sustainability term synonym mappings.
        
        Maps common terms to their sustainability-specific interpretations.
        """
        return {
            "green": ["sustainable", "environmentally friendly", "eco-friendly"],
            "carbon": ["emissions", "greenhouse gas", "carbon footprint"],
            "energy": ["renewable energy", "energy efficiency", "energy consumption"],
            "water": ["water usage", "water conservation", "water management"],
            "waste": ["waste management", "circular economy", "recycling"],
            "social": ["social impact", "community engagement", "social responsibility"],
            "governance": ["corporate governance", "board diversity", "business ethics"]
        }
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a search query to enhance sustainability relevance.
        
        Args:
            query: Original search query
            
        Returns:
            Dictionary with enhanced query data
        """
        logger.info(f"Processing search query: '{query}'")
        
        # Basic query cleaning
        cleaned_query = self._clean_query(query)
        
        # Extract entities
        entities = self._extract_entities(cleaned_query)
        
        # Detect intents
        intents = self._detect_intents(cleaned_query)
        
        # Expand query with sustainability concepts
        expanded_query = self._expand_query(cleaned_query, entities, intents)
        
        # Generate query variations
        variations = self._generate_query_variations(cleaned_query, entities, intents)
        
        # Return enhanced query data
        return {
            "original_query": query,
            "cleaned_query": cleaned_query,
            "expanded_query": expanded_query,
            "entities": entities,
            "intents": intents,
            "variations": variations
        }
    
    def _clean_query(self, query: str) -> str:
        """
        Clean and normalize a search query.
        
        Args:
            query: Raw search query
            
        Returns:
            Cleaned search query
        """
        # Convert to lowercase
        query = query.lower()
        
        # Remove extra whitespace
        query = " ".join(query.split())
        
        # Remove special characters (keep alphanumeric, spaces, and basic punctuation)
        query = re.sub(r'[^\w\s\-.,?]', '', query)
        
        return query
    
    def _extract_entities(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract sustainability-related entities from a query.
        
        Args:
            query: Cleaned search query
            
        Returns:
            Dictionary of extracted entities by type
        """
        entities = {
            "concepts": [],
            "companies": [],
            "frameworks": []
        }
        
        # Extract sustainability concepts
        for concept, concept_data in self.sustainability_concepts.items():
            # Check for concept name
            if concept in query:
                entities["concepts"].append({
                    "name": concept,
                    "category": concept_data["category"],
                    "matched_text": concept
                })
                continue
                
            # Check for synonyms
            for synonym in concept_data["synonyms"]:
                if synonym in query:
                    entities["concepts"].append({
                        "name": concept,
                        "category": concept_data["category"],
                        "matched_text": synonym
                    })
                    break
        
        # Extract company references
        for company_id, company_data in self.company_database.items():
            # Check company name and aliases
            aliases = company_data.get("aliases", [])
            all_names = [company_data["name"]] + aliases
            
            for name in all_names:
                if name.lower() in query:
                    entities["companies"].append({
                        "id": company_id,
                        "name": company_data["name"],
                        "sector": company_data["sector"],
                        "matched_text": name.lower()
                    })
                    break
        
        # Extract framework references
        for framework_id, framework_data in self.esg_frameworks.items():
            # Check framework ID
            if framework_id.lower() in query:
                entities["frameworks"].append({
                    "id": framework_id,
                    "name": framework_data["full_name"],
                    "focus": framework_data["focus"],
                    "matched_text": framework_id.lower()
                })
                continue
                
            # Check full name and aliases
            all_names = [framework_data["full_name"]] + framework_data.get("aliases", [])
            for name in all_names:
                if name.lower() in query:
                    entities["frameworks"].append({
                        "id": framework_id,
                        "name": framework_data["full_name"],
                        "focus": framework_data["focus"],
                        "matched_text": name.lower()
                    })
                    break
        
        return entities
    
    def _detect_intents(self, query: str) -> List[Dict[str, Any]]:
        """
        Detect user intents in a sustainability search query.
        
        Args:
            query: Cleaned search query
            
        Returns:
            List of detected intents with confidence scores
        """
        intents = []
        
        # Check each intent pattern
        for intent, patterns in self.intent_patterns.items():
            matches = 0
            matched_patterns = []
            
            for pattern in patterns:
                if re.search(r'\b' + pattern + r'\b', query, re.IGNORECASE):
                    matches += 1
                    matched_patterns.append(pattern)
            
            if matches > 0:
                # Calculate confidence based on number of matching patterns
                confidence = min(100, matches * 25)
                
                intents.append({
                    "intent": intent.value,
                    "confidence": confidence,
                    "matched_patterns": matched_patterns
                })
        
        # Sort by confidence (highest first)
        intents.sort(key=lambda x: x["confidence"], reverse=True)
        
        return intents
    
    def _expand_query(self, query: str, entities: Dict[str, List[Dict[str, Any]]],
                     intents: List[Dict[str, Any]]) -> str:
        """
        Expand a query with relevant sustainability concepts.
        
        Args:
            query: Cleaned search query
            entities: Extracted entities
            intents: Detected intents
            
        Returns:
            Expanded search query
        """
        expansion_terms = set()
        
        # Add terms based on detected concepts
        for concept in entities.get("concepts", []):
            concept_name = concept["name"]
            if concept_name in self.sustainability_concepts:
                # Add related concepts
                related = self.sustainability_concepts[concept_name].get("related", [])
                
                # Add most relevant related terms (limit to 2)
                for related_term in related[:2]:
                    expansion_terms.add(related_term)
        
        # Add terms based on detected companies
        for company in entities.get("companies", []):
            company_id = company["id"]
            if company_id in self.company_database:
                # Add company's main sustainability initiatives
                initiatives = self.company_database[company_id].get("sustainability_initiatives", [])
                
                # Add most relevant initiative (just one to avoid over-expansion)
                if initiatives:
                    expansion_terms.add(initiatives[0])
        
        # Add terms based on detected frameworks
        for framework in entities.get("frameworks", []):
            framework_id = framework["id"]
            if framework_id in self.esg_frameworks:
                # Add key metrics from the framework
                metrics = self.esg_frameworks[framework_id].get("key_metrics", [])
                
                # Add most relevant metric (just one to avoid over-expansion)
                if metrics and metrics[0] != "Varies by industry":
                    expansion_terms.add(metrics[0])
        
        # Add terms based on intents
        if intents:
            top_intent = intents[0]["intent"]
            
            # Add intent-specific expansion terms
            if top_intent == QueryIntent.METRICS.value:
                expansion_terms.add("KPI")
                expansion_terms.add("performance indicators")
            elif top_intent == QueryIntent.TREND.value:
                expansion_terms.add("trend analysis")
            elif top_intent == QueryIntent.REGULATION.value:
                expansion_terms.add("compliance requirements")
            elif top_intent == QueryIntent.RECOMMENDATION.value:
                expansion_terms.add("best practices")
        
        # Create expanded query
        if expansion_terms:
            expanded_query = f"{query} {' '.join(expansion_terms)}"
        else:
            expanded_query = query
        
        logger.debug(f"Expanded query: '{expanded_query}'")
        return expanded_query
    
    def _generate_query_variations(self, query: str, entities: Dict[str, List[Dict[str, Any]]],
                                 intents: List[Dict[str, Any]]) -> List[str]:
        """
        Generate variations of the query for better search coverage.
        
        Args:
            query: Cleaned search query
            entities: Extracted entities
            intents: Detected intents
            
        Returns:
            List of query variations
        """
        variations = []
        
        # Generate synonym-based variations
        for term, synonyms in self.synonym_mapping.items():
            if term in query:
                for synonym in synonyms:
                    variation = query.replace(term, synonym)
                    variations.append(variation)
        
        # Generate concept-based variations
        for concept in entities.get("concepts", []):
            concept_name = concept["name"]
            matched_text = concept["matched_text"]
            
            if concept_name in self.sustainability_concepts:
                # Create variations with synonyms
                for synonym in self.sustainability_concepts[concept_name].get("synonyms", []):
                    if synonym != matched_text:  # Avoid duplicating the original match
                        variation = query.replace(matched_text, synonym)
                        variations.append(variation)
        
        # Generate framework-based variations
        for framework in entities.get("frameworks", []):
            framework_id = framework["id"]
            matched_text = framework["matched_text"]
            
            if framework_id in self.esg_frameworks:
                # Create variations with aliases
                for alias in self.esg_frameworks[framework_id].get("aliases", []):
                    if alias.lower() != matched_text:  # Avoid duplicating the original match
                        variation = query.replace(matched_text, alias.lower())
                        variations.append(variation)
        
        # Generate intent-specific variations
        if intents:
            top_intent = intents[0]["intent"]
            
            # Add intent-specific variations
            if top_intent == QueryIntent.INFORMATION.value:
                variations.append(f"explain {query}")
            elif top_intent == QueryIntent.METRICS.value:
                variations.append(f"metrics for {query}")
            elif top_intent == QueryIntent.COMPARISON.value:
                variations.append(f"compare {query}")
            elif top_intent == QueryIntent.TREND.value:
                variations.append(f"{query} trends")
            elif top_intent == QueryIntent.RECOMMENDATION.value:
                variations.append(f"best practices for {query}")
        
        # Remove duplicates and limit number of variations
        unique_variations = list(set(variations))
        return unique_variations[:5]  # Limit to 5 variations