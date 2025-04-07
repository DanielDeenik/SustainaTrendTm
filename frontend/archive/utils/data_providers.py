"""
Data Provider Module for SustainaTrend Intelligence Platform

This module centralizes all data-related functions that were previously scattered
across multiple files, reducing redundancy and improving maintainability.
"""

import json
import logging
import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

def get_api_status() -> Dict[str, Any]:
    """
    Get the current status of all API services
    
    Returns:
        Dict with API status information
    """
    try:
        # Check MongoDB status if available
        mongo_status = "online"
        try:
            from mongo_client import verify_connection
            mongo_connected = verify_connection()
            mongo_status = "online" if mongo_connected else "offline"
        except (ImportError, Exception) as e:
            logger.warning(f"MongoDB connection check failed: {e}")
            mongo_status = "unavailable"
            
        # Mock service status check for other components
        services = {
            "mongodb": mongo_status,
            "search_engine": "online",
            "gemini": "online",
            "storytelling": "online",
            "trends": "online",
            "metrics": "online"
        }
        
        # Return formatted status
        return {
            "status": "operational",
            "services": services,
            "timestamp": datetime.now().isoformat(),
            "message": "All systems operational"
        }
    except Exception as e:
        logger.error(f"Error getting API status: {e}")
        return {
            "status": "degraded",
            "message": f"Error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

def get_sustainability_metrics(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get sustainability metrics data
    Uses MongoDB if available, otherwise falls back to generated metrics
    
    Args:
        category: Optional category to filter metrics by (e.g., "real_estate")
        
    Returns:
        List of sustainability metrics
    """
    try:
        # Try to use MongoDB if available
        try:
            from mongo_metrics import get_metrics
            metrics = get_metrics(limit=100)
            if metrics and len(metrics) > 0:
                logger.info(f"Retrieved {len(metrics)} metrics from MongoDB")
                
                # Apply category filter if specified
                if category:
                    if category == "real_estate":
                        # For real estate, filter to relevant categories
                        real_estate_categories = ["Energy Efficiency", "Water Usage", "Waste Management"]
                        metrics = [m for m in metrics if m.get("category") in real_estate_categories]
                    else:
                        # Filter by exact category
                        metrics = [m for m in metrics if m.get("category") == category]
                    
                    logger.info(f"Filtered to {len(metrics)} metrics for category: {category}")
                
                return metrics
        except (ImportError, Exception) as e:
            logger.warning(f"MongoDB metrics retrieval failed: {e}")
        
        # Generate metrics data as fallback
        categories = ["Carbon Emissions", "Water Usage", "Energy Efficiency", 
                     "Waste Management", "Renewable Energy", "Social Impact"]
        
        # If category is real_estate, adjust categories
        if category == "real_estate":
            categories = ["Building Energy Efficiency", "Water Usage", "Waste Management", 
                         "Green Building Certification", "Tenant Comfort"]
        # Otherwise if a specific category is requested, filter to just that
        elif category:
            # Handle any special mapping here
            category_map = {
                "carbon": "Carbon Emissions",
                "water": "Water Usage",
                "energy": "Energy Efficiency",
                "waste": "Waste Management",
                "renewable": "Renewable Energy",
                "social": "Social Impact"
            }
            # Try to map the category or use it directly if no mapping exists
            mapped_category = category_map.get(category.lower(), category)
            # Filter to just the requested category
            categories = [c for c in categories if c.lower() == mapped_category.lower()]
        
        metrics = []
        
        # Generate multiple metrics for each category
        for cat in categories:
            for i in range(4):  # 4 metrics per category
                # Base value with some randomness
                base_value = random.uniform(10, 100)
                
                # Create metric with trend data
                metric = {
                    "name": f"{cat} {i+1}",
                    "category": cat,
                    "value": round(base_value, 2),
                    "unit": "tons" if "Carbon" in cat else "%" if "Energy" in cat or "Renewable" in cat or "Certification" in cat else "kL" if "Water" in cat else "kg",
                    "timestamp": datetime.now() - timedelta(days=random.randint(0, 30)),
                    "trend": []
                }
                
                # Add historical trend data
                for j in range(12):
                    month_value = base_value + random.uniform(-10, 10)
                    trend_point = {
                        "date": (datetime.now() - timedelta(days=30 * (11-j))).strftime("%Y-%m-%d"),
                        "value": round(month_value, 2)
                    }
                    metric["trend"].append(trend_point)
                
                # Calculate change percentage
                first_val = metric["trend"][0]["value"]
                last_val = metric["trend"][-1]["value"]
                change = ((last_val - first_val) / first_val) * 100
                
                metric["change"] = round(change, 1)
                metric["change_type"] = "positive" if (change < 0 and ("Carbon" in cat or "Water" in cat or "Waste" in cat)) or (change > 0 and ("Energy" in cat or "Renewable" in cat or "Social" in cat or "Certification" in cat or "Comfort" in cat)) else "negative"
                
                metrics.append(metric)
        
        logger.info(f"Generated {len(metrics)} mock sustainability metrics")
        return metrics
    except Exception as e:
        logger.error(f"Error getting sustainability metrics: {e}")
        return []

def get_sustainability_stories() -> List[Dict[str, Any]]:
    """
    Get sustainability stories data
    Uses MongoDB if available, otherwise falls back to generated stories
    
    Returns:
        List of sustainability stories
    """
    try:
        # Try to use MongoDB if available
        try:
            from mongo_stories import get_stories
            stories = get_stories(limit=50)
            if stories and len(stories) > 0:
                logger.info(f"Retrieved {len(stories)} stories from MongoDB")
                return stories
        except (ImportError, Exception) as e:
            logger.warning(f"MongoDB stories retrieval failed: {e}")
        
        # Generate stories data as fallback
        story_templates = [
            {
                "title": "Carbon Emissions Reduction Initiative",
                "content": "Our organization has successfully reduced carbon emissions by 15% through implementation of energy-efficient technologies and practices.",
                "category": "Carbon Emissions",
                "tags": ["climate action", "carbon reduction", "energy efficiency"],
                "metrics": ["Carbon Emissions 1", "Energy Efficiency 2"]
            },
            {
                "title": "Water Conservation Program",
                "content": "Through our comprehensive water conservation program, we've managed to reduce water usage by 20% across all operations.",
                "category": "Water Usage",
                "tags": ["water conservation", "resource management", "sustainability"],
                "metrics": ["Water Usage 1", "Water Usage 3"]
            },
            {
                "title": "Renewable Energy Transition",
                "content": "We've increased our renewable energy sourcing from 15% to 45% in the past year, significantly reducing our environmental footprint.",
                "category": "Renewable Energy",
                "tags": ["renewable energy", "solar power", "sustainability"],
                "metrics": ["Renewable Energy 1", "Carbon Emissions 2"]
            },
            {
                "title": "Waste Reduction Initiative",
                "content": "Our waste reduction program has successfully diverted 80% of waste from landfills through recycling and composting efforts.",
                "category": "Waste Management",
                "tags": ["zero waste", "recycling", "circular economy"],
                "metrics": ["Waste Management 1", "Waste Management 2"]
            },
            {
                "title": "Community Engagement Program",
                "content": "Our community engagement program has reached over 10,000 individuals, providing education on sustainable practices and environmental stewardship.",
                "category": "Social Impact",
                "tags": ["community engagement", "education", "social responsibility"],
                "metrics": ["Social Impact 1", "Social Impact 3"]
            }
        ]
        
        stories = []
        
        # Generate multiple stories with variations
        for template in story_templates:
            for i in range(2):  # 2 stories per template
                story = template.copy()
                story["id"] = f"story-{len(stories) + 1}"
                story["title"] = f"{template['title']} - Case Study {i+1}"
                story["content"] = f"{template['content']} {random.choice(['This demonstrates our commitment to sustainability.', 'This initiative has received positive feedback from stakeholders.', 'We plan to expand this program in the coming year.'])}"
                story["timestamp"] = (datetime.now() - timedelta(days=random.randint(1, 60))).isoformat()
                story["author"] = random.choice(["Sustainability Team", "ESG Department", "Operations Team", "Executive Leadership"])
                story["image_url"] = f"/static/images/story-{random.randint(1, 10)}.jpg"
                story["impact_score"] = random.uniform(60, 95)
                
                stories.append(story)
        
        logger.info(f"Generated {len(stories)} mock sustainability stories")
        return stories
    except Exception as e:
        logger.error(f"Error getting sustainability stories: {e}")
        return []

def get_sustainability_trends() -> List[Dict[str, Any]]:
    """
    Get sustainability trend data
    Uses MongoDB if available, otherwise falls back to generated trends
    
    Returns:
        List of sustainability trends
    """
    try:
        # Try to use MongoDB if available
        try:
            from mongo_trends import get_trends
            trends = get_trends(limit=50)
            if trends and len(trends) > 0:
                logger.info(f"Retrieved {len(trends)} trends from MongoDB")
                return trends
        except (ImportError, Exception) as e:
            logger.warning(f"MongoDB trends retrieval failed: {e}")
        
        # Generate trends data as fallback
        trend_templates = [
            {
                "name": "Carbon Neutrality Pledges",
                "category": "Climate Action",
                "virality_score": 87,
                "sentiment": 0.78,
                "mentions": 1458,
                "description": "Companies pledging to achieve carbon neutrality by 2030",
                "impact_statement": "High potential for emissions reduction",
                "category_display": "Climate Action",
                "timeframe": "Long-term trend"
            },
            {
                "name": "ESG Reporting Standards",
                "category": "Governance",
                "virality_score": 92,
                "sentiment": 0.65,
                "mentions": 2104,
                "description": "Standardization of ESG reporting frameworks",
                "impact_statement": "Improved comparability of sustainability metrics",
                "category_display": "ESG Governance",
                "timeframe": "Current trend"
            },
            {
                "name": "Circular Economy Initiatives",
                "category": "Resource Efficiency",
                "virality_score": 76,
                "sentiment": 0.81,
                "mentions": 873,
                "description": "Business models focused on reuse and recycling",
                "impact_statement": "Reduction in waste and resource consumption",
                "category_display": "Resource Efficiency",
                "timeframe": "Growing trend"
            },
            {
                "name": "Science-Based Targets",
                "category": "Climate Action",
                "virality_score": 83,
                "sentiment": 0.72,
                "mentions": 1267,
                "description": "Emissions targets aligned with climate science",
                "impact_statement": "Credible pathway to emissions reduction",
                "category_display": "Climate Action",
                "timeframe": "Established trend"
            },
            {
                "name": "Sustainable Finance",
                "category": "Finance",
                "virality_score": 89,
                "sentiment": 0.68,
                "mentions": 1845,
                "description": "Financial products tied to sustainability outcomes",
                "impact_statement": "Mobilization of capital for sustainability",
                "category_display": "Sustainable Finance",
                "timeframe": "Accelerating trend"
            }
        ]
        
        trends = []
        
        # Generate multiple trends with variations
        for template in trend_templates:
            for i in range(1, 3):  # 2 trends per template with variations
                trend = template.copy()
                trend["id"] = f"trend-{len(trends) + 1}"
                
                if i == 2:
                    trend["name"] = f"{template['name']} - Regional Focus"
                    trend["virality_score"] = max(50, template["virality_score"] - random.randint(5, 15))
                    trend["mentions"] = int(template["mentions"] * 0.7)
                    trend["sentiment"] = max(0, min(1, template["sentiment"] - random.uniform(0.05, 0.15)))
                
                trend["timestamp"] = (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
                trend["sources"] = random.sample(["News Articles", "Corporate Reports", "Social Media", "Regulatory Updates", "Academic Research"], k=random.randint(2, 4))
                trend["momentum"] = random.choice(["increasing", "stable", "increasing", "rapidly growing"])  # Bias toward positive momentum
                
                trends.append(trend)
        
        logger.info(f"Generated {len(trends)} mock sustainability trends")
        return trends
    except Exception as e:
        logger.error(f"Error getting sustainability trends: {e}")
        return []

def get_ui_suggestions(query: str) -> Dict[str, List[str]]:
    """
    Get dynamic UI search suggestions based on the query string
    
    Args:
        query: User's search query
        
    Returns:
        Dictionary with suggestion lists
    """
    try:
        # If we had a real AI service, it would provide suggestions here
        # For now, we'll create simple template-based suggestions
        suggestions = {
            "suggestions": [
                f"{query} in sustainability reports",
                f"{query} carbon impact",
                f"{query} ESG metrics",
                f"{query} sustainability trend"
            ]
        }
        
        if "carbon" in query.lower():
            suggestions["suggestions"].extend([
                "Carbon neutral strategies",
                "Carbon offset programs",
                "Carbon footprint calculation"
            ])
        elif "water" in query.lower():
            suggestions["suggestions"].extend([
                "Water conservation methods",
                "Water usage reporting",
                "Water footprint reduction"
            ])
        elif "energy" in query.lower():
            suggestions["suggestions"].extend([
                "Renewable energy adoption",
                "Energy efficiency metrics",
                "Energy management systems"
            ])
        elif "waste" in query.lower():
            suggestions["suggestions"].extend([
                "Zero waste initiatives",
                "Waste reduction strategies",
                "Circular economy practices"
            ])
        elif "social" in query.lower() or "community" in query.lower():
            suggestions["suggestions"].extend([
                "Social impact measurement",
                "Community engagement programs",
                "Social responsibility initiatives"
            ])
        
        logger.info(f"Generated {len(suggestions['suggestions'])} UI suggestions for query: {query}")
        return suggestions
    except Exception as e:
        logger.error(f"Error generating UI suggestions: {e}")
        return {"suggestions": []}