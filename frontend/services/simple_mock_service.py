"""
SimpleMockService

A lightweight mock service that provides static data for the Sustainability Intelligence Platform.
This eliminates external dependencies on MongoDB while providing realistic test data.
"""

import random
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union

# Setup logging
logger = logging.getLogger("services.simple_mock_service")

class SimpleMockService:
    """
    Simple mock service that provides static data for all service layer operations.
    This implementation is self-contained and doesn't rely on external databases.
    """
    
    def __init__(self):
        """Initialize the mock service with pre-generated data"""
        logger.info("Initializing SimpleMockService")
        
        # Generate mock data
        self._metrics = self._generate_metrics(30)
        self._trends = self._generate_trends(15)
        self._stories = self._generate_stories(10)
        
        # Create lookups for faster access
        self._metrics_by_id = {m["id"]: m for m in self._metrics}
        self._trends_by_id = {t["id"]: t for t in self._trends}
        self._stories_by_id = {s["id"]: s for s in self._stories}
        
        logger.info(f"Mock service initialized with {len(self._metrics)} metrics, "
                   f"{len(self._trends)} trends, and {len(self._stories)} stories")
    
    def get_categories(self) -> List[str]:
        """
        Get the list of available metric categories
        
        Returns:
            List of category names
        """
        categories = ["emissions", "energy", "water", "waste", "social"]
        return categories
    
    def get_metrics(self, 
                    category: Optional[str] = None, 
                    start_date: Optional[Union[str, datetime]] = None,
                    end_date: Optional[Union[str, datetime]] = None,
                    limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get sustainability metrics with optional filtering
        
        Args:
            category: Filter by category name
            start_date: Filter by minimum date (string or datetime)
            end_date: Filter by maximum date (string or datetime)
            limit: Maximum number of records to return
            
        Returns:
            List of metric dictionaries
        """
        # Convert string dates to datetime if provided
        start_dt = self._parse_date(start_date) if start_date else None
        end_dt = self._parse_date(end_date) if end_date else None
        
        # Apply filters
        filtered_metrics = self._metrics.copy()
        
        if category:
            filtered_metrics = [m for m in filtered_metrics if m.get("category") == category]
            
        if start_dt:
            filtered_metrics = [m for m in filtered_metrics 
                               if self._parse_date(m.get("timestamp")) is not None and 
                               self._parse_date(m.get("timestamp")) >= start_dt]
            
        if end_dt:
            filtered_metrics = [m for m in filtered_metrics 
                               if self._parse_date(m.get("timestamp")) is not None and 
                               self._parse_date(m.get("timestamp")) <= end_dt]
        
        # Apply limit and return
        return filtered_metrics[:limit]
    
    def get_trends(self,
                   category: Optional[str] = None,
                   min_virality: Optional[float] = None,
                   limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get sustainability trends with optional filtering
        
        Args:
            category: Filter by category name
            min_virality: Minimum virality score
            limit: Maximum number of records to return
            
        Returns:
            List of trend dictionaries
        """
        # Apply filters
        filtered_trends = self._trends.copy()
        
        if category:
            filtered_trends = [t for t in filtered_trends if t.get("category") == category]
            
        if min_virality is not None:
            filtered_trends = [t for t in filtered_trends 
                              if t.get("virality_score", 0) >= min_virality]
        
        # Sort by virality score (high to low)
        filtered_trends.sort(key=lambda t: t.get("virality_score", 0), reverse=True)
        
        # Apply limit and return
        return filtered_trends[:limit]
    
    def get_stories(self,
                    category: Optional[str] = None,
                    tags: Optional[List[str]] = None,
                    limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get sustainability stories with optional filtering
        
        Args:
            category: Filter by category name
            tags: Filter by one or more tags
            limit: Maximum number of records to return
            
        Returns:
            List of story dictionaries
        """
        # Apply filters
        filtered_stories = self._stories.copy()
        
        if category:
            filtered_stories = [s for s in filtered_stories if s.get("category") == category]
            
        if tags:
            filtered_stories = [s for s in filtered_stories 
                               if any(tag in s.get("tags", []) for tag in tags)]
        
        # Sort by publication date (newest first)
        # Using a custom sorting key function to handle None values
        def publication_date_key(story):
            date = self._parse_date(story.get("publication_date"))
            # If date is None, return a very old date to sort at the end
            return date if date is not None else datetime(1900, 1, 1)
            
        filtered_stories.sort(key=publication_date_key, reverse=True)
        
        # Apply limit and return
        return filtered_stories[:limit]
    
    def get_metric_by_id(self, metric_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """
        Get a single metric by ID
        
        Args:
            metric_id: The ID of the metric to retrieve
            
        Returns:
            Metric dictionary or None if not found
        """
        # Handle both string and integer IDs
        str_id = str(metric_id)
        if str_id in self._metrics_by_id:
            return self._metrics_by_id[str_id]
        
        # Also try with integer ID
        try:
            int_id = int(metric_id)
            return self._metrics_by_id.get(int_id)
        except (ValueError, TypeError):
            pass
            
        return None
    
    def get_trend_by_id(self, trend_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """
        Get a single trend by ID
        
        Args:
            trend_id: The ID of the trend to retrieve
            
        Returns:
            Trend dictionary or None if not found
        """
        # Handle both string and integer IDs
        str_id = str(trend_id)
        if str_id in self._trends_by_id:
            return self._trends_by_id[str_id]
            
        # Also try with integer ID
        try:
            int_id = int(trend_id)
            return self._trends_by_id.get(int_id)
        except (ValueError, TypeError):
            pass
            
        return None
    
    def get_story_by_id(self, story_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """
        Get a single story by ID
        
        Args:
            story_id: The ID of the story to retrieve
            
        Returns:
            Story dictionary or None if not found
        """
        # Handle both string and integer IDs
        str_id = str(story_id)
        if str_id in self._stories_by_id:
            return self._stories_by_id[str_id]
            
        # Also try with integer ID
        try:
            int_id = int(story_id)
            return self._stories_by_id.get(int_id)
        except (ValueError, TypeError):
            pass
            
        return None
    
    def _generate_metrics(self, count: int = 30) -> List[Dict[str, Any]]:
        """
        Generate mock sustainability metrics data
        
        Args:
            count: Number of metrics to generate
            
        Returns:
            List of metric dictionaries
        """
        categories = ["emissions", "energy", "water", "waste", "social"]
        units = {
            "emissions": "tons CO2e",
            "energy": "MWh",
            "water": "kiloliters",
            "waste": "tons",
            "social": "score"
        }
        metrics_per_category = count // len(categories)
        result = []
        
        for cat_index, category in enumerate(categories):
            # Generate multiple data points for the same metric over time
            if category == "emissions":
                # Carbon emissions with decreasing trend
                for i in range(metrics_per_category):
                    # Start at 50 tons CO2e and decrease by ~5% each month
                    base_value = 50
                    reduction_factor = 0.95
                    
                    value = base_value * (reduction_factor ** i)
                    # Add some noise (±10%)
                    value = value * random.uniform(0.9, 1.1)
                    
                    metric = {
                        "id": cat_index * metrics_per_category + i + 1,
                        "name": "Carbon Emissions",
                        "category": category,
                        "value": round(value),
                        "unit": units[category],
                        "timestamp": (datetime.now() - timedelta(days=30 * i)).isoformat()
                    }
                    result.append(metric)
            
            elif category == "energy":
                # Energy consumption with seasonal variations
                for i in range(metrics_per_category):
                    # Base value of 120 MWh with seasonal pattern
                    month = i % 12
                    # Higher in winter (months 0,1,2,10,11), lower in summer
                    seasonal_factor = 1.2 if month in [0, 1, 2, 10, 11] else 0.8
                    
                    base_value = 120
                    value = base_value * seasonal_factor
                    # Add some noise (±15%)
                    value = value * random.uniform(0.85, 1.15)
                    
                    metric = {
                        "id": cat_index * metrics_per_category + i + 1,
                        "name": "Energy Consumption",
                        "category": category,
                        "value": round(value),
                        "unit": units[category],
                        "timestamp": (datetime.now() - timedelta(days=30 * i)).isoformat()
                    }
                    result.append(metric)
            
            elif category == "water":
                # Water usage with slight upward trend
                for i in range(metrics_per_category):
                    # Start at 250 kiloliters and increase slightly
                    base_value = 250
                    increase_factor = 1.02
                    
                    value = base_value * (increase_factor ** i)
                    # Add some noise (±8%)
                    value = value * random.uniform(0.92, 1.08)
                    
                    metric = {
                        "id": cat_index * metrics_per_category + i + 1,
                        "name": "Water Usage",
                        "category": category,
                        "value": round(value),
                        "unit": units[category],
                        "timestamp": (datetime.now() - timedelta(days=30 * i)).isoformat()
                    }
                    result.append(metric)
            
            elif category == "waste":
                # Waste generation with decreasing trend
                for i in range(metrics_per_category):
                    # Start at 85 tons and decrease gradually
                    base_value = 85
                    reduction_factor = 0.97
                    
                    value = base_value * (reduction_factor ** i)
                    # Add some noise (±12%)
                    value = value * random.uniform(0.88, 1.12)
                    
                    metric = {
                        "id": cat_index * metrics_per_category + i + 1,
                        "name": "Waste Generation",
                        "category": category,
                        "value": round(value),
                        "unit": units[category],
                        "timestamp": (datetime.now() - timedelta(days=30 * i)).isoformat()
                    }
                    result.append(metric)
            
            elif category == "social":
                # ESG score with improving trend
                for i in range(metrics_per_category):
                    # Start at 65 and improve gradually
                    base_value = 65
                    improvement_factor = 1.03
                    
                    value = base_value * (improvement_factor ** i)
                    # Cap at 100
                    value = min(100, value)
                    # Add some noise (±5%)
                    value = value * random.uniform(0.95, 1.05)
                    
                    metric = {
                        "id": cat_index * metrics_per_category + i + 1,
                        "name": "ESG Score",
                        "category": category,
                        "value": round(value),
                        "unit": units[category],
                        "timestamp": (datetime.now() - timedelta(days=30 * i)).isoformat()
                    }
                    result.append(metric)
        
        return result
    
    def _generate_trends(self, count: int = 15) -> List[Dict[str, Any]]:
        """
        Generate mock sustainability trend data
        
        Args:
            count: Number of trends to generate
            
        Returns:
            List of trend dictionaries
        """
        categories = ["emissions", "energy", "water", "waste", "social"]
        trends_data = []
        
        # Predefined trend topics by category for more realistic data
        trend_topics = {
            "emissions": [
                "Carbon Neutrality Pledges",
                "Scope 3 Emissions Tracking",
                "Net-Zero Building Standards",
                "Carbon Offset Verification"
            ],
            "energy": [
                "Renewable Energy Integration",
                "Energy Efficiency Measures",
                "Green Building Certification",
                "Heat Pump Technology Adoption"
            ],
            "water": [
                "Water Conservation Techniques",
                "Rainwater Harvesting Systems",
                "Greywater Recycling Solutions",
                "Water Risk Assessment"
            ],
            "waste": [
                "Circular Economy Implementation",
                "Zero Waste Certification",
                "Biodegradable Packaging Adoption",
                "Compost Integration Programs"
            ],
            "social": [
                "Community Impact Measurement",
                "Diversity & Inclusion Metrics",
                "Supply Chain Ethical Standards",
                "Employee Well-being Programs"
            ]
        }
        
        # Generate trends with realistic data distribution
        for i in range(count):
            # Select category with weighted distribution
            # More trends in emissions and energy categories
            category_weights = {
                "emissions": 0.3,
                "energy": 0.25,
                "social": 0.2,
                "waste": 0.15,
                "water": 0.1
            }
            category = random.choices(
                list(category_weights.keys()),
                weights=list(category_weights.values()),
                k=1
            )[0]
            
            # Select a topic from the predefined list for this category
            topic = random.choice(trend_topics[category])
            
            # Generate a timestamp within the last 3 months
            days_ago = random.randint(1, 90)
            timestamp = (datetime.now() - timedelta(days=days_ago)).isoformat()
            
            # Generate virality score with realistic distribution
            # Most trends have moderate virality (0.3-0.6)
            # Few trends have high virality (0.7-0.9)
            virality_base = random.random()
            if virality_base < 0.7:  # 70% of trends
                virality_score = random.uniform(0.3, 0.6)
            else:  # 30% of trends
                virality_score = random.uniform(0.7, 0.9)
                
            # Newer trends tend to have higher virality
            recency_boost = max(0, 0.2 * (1 - days_ago / 90))
            virality_score = min(0.95, virality_score + recency_boost)
            
            # Determine momentum based on virality and recency
            if days_ago < 30 and virality_score > 0.6:
                momentum = "rising"
            elif days_ago > 60 or virality_score < 0.4:
                momentum = "falling"
            else:
                momentum = "steady"
                
            # Create the trend object
            trend = {
                "id": i + 1,
                "name": topic,
                "category": category,
                "virality_score": round(virality_score, 2),
                "timestamp": timestamp,
                "momentum": momentum,
                "mentions_count": random.randint(int(virality_score * 100), int(virality_score * 500)),
                "sentiment_score": random.uniform(0.3, 0.8),
                "key_sources": random.sample([
                    "industry_reports", "news_articles", "social_media", 
                    "regulatory_updates", "research_papers"
                ], k=random.randint(1, 3))
            }
            
            trends_data.append(trend)
            
        return trends_data
    
    def _generate_stories(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Generate mock sustainability storytelling data
        
        Args:
            count: Number of stories to generate
            
        Returns:
            List of story dictionaries
        """
        categories = ["emissions", "energy", "water", "waste", "social"]
        stories_data = []
        
        # Predefined story templates for more realistic data
        story_templates = {
            "emissions": [
                {
                    "title": "Carbon Reduction Success Story",
                    "content": "This organization achieved a 30% reduction in carbon emissions through innovative building management and renewable energy integration."
                },
                {
                    "title": "Net-Zero Building Case Study",
                    "content": "A detailed analysis of how this commercial property achieved net-zero carbon emissions through a combination of design, technology, and operational excellence."
                }
            ],
            "energy": [
                {
                    "title": "Renewable Energy Transformation",
                    "content": "How this portfolio transitioned to 100% renewable energy, overcoming technical challenges and achieving significant cost savings."
                },
                {
                    "title": "Energy Efficiency Innovation",
                    "content": "A case study of innovative energy efficiency measures that reduced consumption by 40% across multiple properties."
                }
            ],
            "water": [
                {
                    "title": "Water Conservation Excellence",
                    "content": "This organization implemented comprehensive water conservation measures, reducing consumption by 25% and setting new industry standards."
                },
                {
                    "title": "Integrated Water Management",
                    "content": "A holistic approach to water management across multiple properties, including rainwater harvesting, greywater recycling, and smart irrigation systems."
                }
            ],
            "waste": [
                {
                    "title": "Zero Waste Certification Journey",
                    "content": "The challenges and successes encountered on the path to achieving Zero Waste certification across a diverse property portfolio."
                },
                {
                    "title": "Circular Economy Implementation",
                    "content": "How this organization embedded circular economy principles into its operations, reducing waste by 60% and creating new value streams."
                }
            ],
            "social": [
                {
                    "title": "Community Impact Initiative",
                    "content": "This development project created significant positive impact through innovative community engagement and local economic development initiatives."
                },
                {
                    "title": "Inclusive Design Excellence",
                    "content": "A case study of how inclusive design principles were applied to create accessible, equitable spaces that serve diverse community needs."
                }
            ]
        }
        
        # Generate stories with realistic data
        for i in range(count):
            # Select category
            category = random.choice(categories)
            
            # Select a story template
            template = random.choice(story_templates[category])
            
            # Generate publication date within the last 6 months
            days_ago = random.randint(1, 180)
            pub_date = (datetime.now() - timedelta(days=days_ago)).isoformat()
            
            # Select random tags appropriate for the category
            all_tags = [
                "best_practice", "case_study", "innovation", "leadership",
                "technology", "policy", "award_winning", "community",
                "investment", "performance", "certification"
            ]
            
            tag_count = random.randint(2, 4)
            tags = random.sample(all_tags, k=tag_count)
            
            # Create the story object
            story = {
                "id": i + 1,
                "title": template["title"],
                "content": template["content"],
                "category": category,
                "tags": tags,
                "publication_date": pub_date,
                "reading_time": random.randint(3, 10),  # minutes
                "impact_score": round(random.uniform(6.5, 9.5), 1),  # 1-10 scale
                "sources": random.sample([
                    "customer_interview", "industry_report", 
                    "internal_data", "third_party_verification"
                ], k=random.randint(1, 2))
            }
            
            stories_data.append(story)
            
        return stories_data
    
    def _parse_date(self, date_value: Optional[Union[str, datetime]]) -> Optional[datetime]:
        """
        Parse a date value from string or datetime
        
        Args:
            date_value: Date as string or datetime object
            
        Returns:
            Parsed datetime object or None if invalid
        """
        if not date_value:
            return None
            
        if isinstance(date_value, datetime):
            return date_value
            
        try:
            return datetime.fromisoformat(date_value.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            logger.warning(f"Invalid date format: {date_value}")
            return None