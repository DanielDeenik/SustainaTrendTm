"""
Simple Mock Service for SustainaTrend™ Intelligence Platform

This module provides a simple service for generating mock sustainability data
for development purposes and testing dashboard functionality.

Note: This is used for UI development only and should be replaced with 
real data services in production.
"""

import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class SimpleMockService:
    """
    Service for generating mock sustainability data
    """
    
    def __init__(self):
        """Initialize the mock service"""
        logger.info("Initializing SimpleMockService")
        
        # Define metrics categories
        self.metrics_categories = [
            "Carbon Emissions",
            "Energy Consumption",
            "Water Usage",
            "Waste Management",
            "Renewable Energy",
            "Employee Diversity",
            "Supply Chain",
            "Biodiversity Impact"
        ]
        
        # Define trend categories
        self.trend_categories = [
            "Climate Transition",
            "Circular Economy",
            "Social Impact",
            "Governance",
            "ESG Reporting",
            "Stakeholder Engagement",
            "Regulatory Compliance",
            "Technology Innovation"
        ]
        
        # Define story categories
        self.story_categories = [
            "Success Stories",
            "Challenges",
            "Innovations",
            "Strategic Initiatives",
            "Risk Management",
            "Stakeholder Value",
            "Regulatory Impact",
            "Future Outlook"
        ]
        
        # Define targets dictionary
        self.targets = {
            "Carbon Emissions": {"unit": "tons CO2e", "direction": "decrease", "annual_target": 0.85},
            "Energy Consumption": {"unit": "MWh", "direction": "decrease", "annual_target": 0.9},
            "Water Usage": {"unit": "gallons", "direction": "decrease", "annual_target": 0.85},
            "Waste Management": {"unit": "tons", "direction": "decrease", "annual_target": 0.8},
            "Renewable Energy": {"unit": "%", "direction": "increase", "annual_target": 1.2},
            "Employee Diversity": {"unit": "%", "direction": "increase", "annual_target": 1.1},
            "Supply Chain": {"unit": "score", "direction": "increase", "annual_target": 1.15},
            "Biodiversity Impact": {"unit": "index", "direction": "decrease", "annual_target": 0.9}
        }
    
    def get_metrics(self, category: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get mock sustainability metrics
        
        Args:
            category: Category to filter by (optional)
            limit: Maximum number of metrics to return
            
        Returns:
            List of metrics
        """
        logger.info(f"Getting mock metrics, category: {category}, limit: {limit}")
        
        metrics = []
        
        # Generate metrics for each category
        for metric_category in self.metrics_categories:
            # Skip if filtering by category and this doesn't match
            if category and category.lower() not in metric_category.lower():
                continue
                
            # Generate time series for this metric
            base_value = random.uniform(80, 120)
            time_series = []
            
            # Generate 12 months of data
            for i in range(12):
                date = (datetime.now() - timedelta(days=30 * (11 - i))).strftime("%Y-%m")
                
                # Determine direction and factor
                direction = self.targets[metric_category]["direction"]
                annual_target = self.targets[metric_category]["annual_target"]
                
                # Calculate monthly factor (smaller changes each month to reach annual target)
                monthly_factor = annual_target ** (1/12)
                
                # Apply cumulative factor based on month
                cumulative_factor = monthly_factor ** i
                
                # For decreasing metrics, we want values to decrease over time
                if direction == "decrease":
                    value = base_value * (2 - cumulative_factor)
                else:
                    value = base_value * cumulative_factor
                
                # Add random noise
                noise = random.uniform(-5, 5)
                value = max(0, value + noise)  # Ensure no negative values
                
                time_series.append({
                    "date": date,
                    "value": round(value, 2),
                    "target": round(base_value * self.targets[metric_category]["annual_target"], 2),
                    "unit": self.targets[metric_category]["unit"]
                })
            
            metrics.append({
                "id": f"metric_{len(metrics) + 1}",
                "name": metric_category,
                "category": metric_category.split()[0],
                "description": f"Tracks {metric_category.lower()} across all operations",
                "unit": self.targets[metric_category]["unit"],
                "time_series": time_series,
                "latest_value": time_series[-1]["value"],
                "target": time_series[-1]["target"],
                "status": "active",
                "regulatory_framework": random.choice(["CSRD", "GRI", "SASB", "TCFD", "None"]),
                "source": random.choice(["Internal", "External", "Calculated", "Estimated"])
            })
            
            # Break if we've reached the limit
            if len(metrics) >= limit:
                break
        
        return metrics
    
    def get_trends(self, category: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get mock sustainability trends
        
        Args:
            category: Category to filter by (optional)
            limit: Maximum number of trends to return
            
        Returns:
            List of trends
        """
        logger.info(f"Getting mock trends, category: {category}, limit: {limit}")
        
        trends = []
        
        # Sample trend titles
        trend_titles = {
            "Climate Transition": [
                "Net Zero Commitments Accelerate",
                "Carbon Pricing Adoption Growth",
                "Climate Risk Disclosure Standards",
                "Green Hydrogen Momentum"
            ],
            "Circular Economy": [
                "Plastic Reduction Strategies",
                "Product-as-Service Models Expansion",
                "Remanufacturing Initiatives Growth",
                "Zero Waste Certification Demand"
            ],
            "Social Impact": [
                "Human Rights Due Diligence",
                "Community Investment Programs",
                "Diversity Reporting Standards",
                "Living Wage Commitments"
            ],
            "Governance": [
                "ESG Board Committee Formation",
                "Sustainability Executive Compensation",
                "Climate Competency Requirements",
                "Transparency in Political Spending"
            ],
            "ESG Reporting": [
                "CSRD Implementation Timeline",
                "AI-Enhanced ESG Analytics",
                "Double Materiality Assessment",
                "Impact Valuation Methodologies"
            ],
            "Stakeholder Engagement": [
                "Investor ESG Expectations",
                "Employee Sustainability Engagement",
                "Customer Sustainability Preferences",
                "Supplier ESG Performance Requirements"
            ],
            "Regulatory Compliance": [
                "EU Deforestation Regulation Impact",
                "Carbon Border Adjustment Mechanism",
                "Human Rights Due Diligence Laws",
                "Plastic Packaging Taxes"
            ],
            "Technology Innovation": [
                "Digital Product Passports",
                "Blockchain for Supply Chain Transparency",
                "Satellite Monitoring of Emissions",
                "AI for Predictive Sustainability Analytics"
            ]
        }
        
        # Generate trends for each category
        for trend_category in self.trend_categories:
            # Skip if filtering by category and this doesn't match
            if category and category.lower() not in trend_category.lower():
                continue
            
            # Get titles for this category
            category_titles = trend_titles.get(trend_category, [f"{trend_category} Trend"])
            
            # Create a trend for each title
            for title in category_titles:
                # Generate random virality score (0-100)
                virality_score = random.uniform(30, 95)
                
                # Higher chance of high virality for regulatory and climate trends
                if "Regulatory" in trend_category or "Climate" in trend_category:
                    virality_score += random.uniform(0, 15)
                    virality_score = min(virality_score, 100)
                
                # Generate momentum (rising or falling)
                momentum = random.choice(["rising", "stable", "falling"])
                momentum_value = random.uniform(-10, 20)
                
                if momentum == "rising":
                    momentum_value = abs(momentum_value)
                elif momentum == "falling":
                    momentum_value = -abs(momentum_value)
                else:
                    momentum_value = momentum_value / 5  # Smaller change for stable
                
                trends.append({
                    "id": f"trend_{len(trends) + 1}",
                    "title": title,
                    "category": trend_category,
                    "description": f"Analysis of {title.lower()} across the industry and its implications",
                    "virality_score": round(virality_score, 1),
                    "momentum": momentum,
                    "momentum_value": round(momentum_value, 1),
                    "impact_level": random.choice(["high", "medium", "low"]),
                    "timeframe": random.choice(["short-term", "medium-term", "long-term"]),
                    "sources": random.randint(1, 5),
                    "mentions": random.randint(5, 500),
                    "created_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
                })
                
                # Break if we've reached the limit
                if len(trends) >= limit:
                    break
            
            # Break if we've reached the limit
            if len(trends) >= limit:
                break
        
        return trends
    
    def get_stories(self, category: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get mock sustainability stories
        
        Args:
            category: Category to filter by (optional)
            limit: Maximum number of stories to return
            
        Returns:
            List of stories
        """
        logger.info(f"Getting mock stories, category: {category}, limit: {limit}")
        
        stories = []
        
        # Sample story titles and content
        story_content = {
            "Success Stories": [
                {
                    "title": "Carbon Reduction Exceeds Targets",
                    "content": "Our carbon emissions reduction program has exceeded its annual target by 15%, demonstrating the effectiveness of our climate strategy. The implementation of energy efficiency measures and renewable energy procurement has been particularly successful, with facility-level improvements significantly outperforming initial projections.",
                    "metric": "Carbon Emissions",
                    "sentiment": "positive"
                },
                {
                    "title": "Water Conservation Initiative Success",
                    "content": "The corporate water conservation program has reduced total water consumption by 22% compared to baseline, surpassing our 15% target. Advanced recycling technologies and process optimizations across manufacturing facilities have contributed to this achievement, particularly in water-stressed regions.",
                    "metric": "Water Usage",
                    "sentiment": "positive"
                }
            ],
            "Challenges": [
                {
                    "title": "Supply Chain Emissions Challenge",
                    "content": "Scope 3 emissions from our supply chain remain a significant challenge, with only 65% of suppliers providing verified emission data. Despite engagement efforts, visibility throughout the value chain remains limited, particularly for smaller tier 2 and tier 3 suppliers operating in regions with less developed reporting infrastructure.",
                    "metric": "Carbon Emissions",
                    "sentiment": "negative"
                },
                {
                    "title": "Regulatory Compliance Complexity",
                    "content": "Meeting divergent sustainability reporting requirements across global markets presents increasing complexity. Our teams are working to align data collection and verification processes with emerging standards like CSRD in Europe and SEC climate disclosure rules in the US, which have different methodological approaches and timelines.",
                    "metric": "ESG Reporting",
                    "sentiment": "negative"
                }
            ],
            "Innovations": [
                {
                    "title": "AI-Powered Energy Optimization",
                    "content": "Implementation of AI-powered energy management systems has reduced energy consumption by 18% in pilot facilities. The machine learning algorithms continuously optimize HVAC, lighting, and production systems based on occupancy, weather conditions, and production schedules, learning and improving over time.",
                    "metric": "Energy Consumption",
                    "sentiment": "positive"
                },
                {
                    "title": "Circular Packaging Breakthrough",
                    "content": "Our R&D team has developed a fully recyclable packaging solution for previously hard-to-recycle products, potentially eliminating 1,200 tons of landfill waste annually. The innovation uses a novel polymer blend that maintains performance while being compatible with existing recycling infrastructure.",
                    "metric": "Waste Management",
                    "sentiment": "positive"
                }
            ],
            "Strategic Initiatives": [
                {
                    "title": "Net Zero Roadmap Implementation",
                    "content": "Implementation of our 2030 Net Zero roadmap is progressing on schedule with 40% of planned initiatives now operational. Capital investments in on-site renewable energy are showing a 4.5-year average payback period, better than the projected 5.5 years, while electrification of our vehicle fleet is advancing with 35% conversion complete.",
                    "metric": "Carbon Emissions",
                    "sentiment": "positive"
                },
                {
                    "title": "Water Stewardship Program Expansion",
                    "content": "Our water stewardship program is expanding to include watershed-level initiatives in three key operating regions identified as high water stress areas. This strategic expansion includes community engagement, infrastructure investment, and collaborative governance approaches designed to address shared water resource challenges.",
                    "metric": "Water Usage",
                    "sentiment": "positive"
                }
            ],
            "Risk Management": [
                {
                    "title": "Climate Risk Scenario Analysis",
                    "content": "Comprehensive climate risk scenario analysis identifies potential financial exposure of $25-40M annually by 2030 under a high-warming scenario. Physical risks to coastal facilities and transition risks related to carbon pricing represent the most significant exposures, with cascading impacts on insurance costs, capital expenditure requirements, and operational continuity.",
                    "metric": "Carbon Emissions",
                    "sentiment": "negative"
                },
                {
                    "title": "Biodiversity Impact Assessment",
                    "content": "Biodiversity impact assessment completed for 75% of high-risk operations, revealing moderate to significant ecosystem impacts at three locations. Mitigation planning is underway with initial focus on habitat restoration, invasive species control, and operational modifications to reduce ongoing impacts to sensitive ecosystems.",
                    "metric": "Biodiversity Impact",
                    "sentiment": "negative"
                }
            ],
            "Stakeholder Value": [
                {
                    "title": "ESG Investor Engagement Results",
                    "content": "Structured ESG investor engagement program has reached 80% of our shareholder base, with positive feedback on climate transition plans. Investors particularly valued the transparency on capital allocation for sustainability initiatives, emissions reduction methodology, and clear connection between sustainability performance and executive compensation.",
                    "metric": "Governance",
                    "sentiment": "positive"
                },
                {
                    "title": "Employee Sustainability Engagement",
                    "content": "Employee sustainability engagement program has achieved 85% participation rate with measurable impact on retention and recruitment. Survey data indicates sustainability performance is now the third most important factor for employee satisfaction, with ambassador programs and innovation challenges generating over 200 implementable improvement ideas.",
                    "metric": "Social Impact",
                    "sentiment": "positive"
                }
            ],
            "Regulatory Impact": [
                {
                    "title": "CSRD Readiness Assessment",
                    "content": "CSRD readiness assessment indicates 65% compliance with forthcoming disclosure requirements, with significant gaps in double materiality assessment and value chain reporting. Implementation timeline and resource allocation have been adjusted to prioritize development of data collection systems for social metrics and upstream scope 3 emissions, which represent the largest compliance gaps.",
                    "metric": "ESG Reporting",
                    "sentiment": "neutral"
                },
                {
                    "title": "Carbon Border Adjustment Mechanism Impact",
                    "content": "Analysis of EU Carbon Border Adjustment Mechanism impact indicates potential cost increase of €3.2M annually for imported materials. Strategic response includes accelerated supplier engagement program, potential reformulation of product lines, and evaluation of localized production options to mitigate border adjustment costs.",
                    "metric": "Carbon Emissions",
                    "sentiment": "negative"
                }
            ],
            "Future Outlook": [
                {
                    "title": "Science-Based Targets Implementation",
                    "content": "Implementation of science-based targets is on track with 30% reduction in absolute emissions achieved against 2018 baseline. Current trajectory supports our 2030 target of 50% reduction, though acceleration is needed in certain business units. The renewable energy transition remains ahead of schedule with 65% of electricity now from renewable sources.",
                    "metric": "Carbon Emissions",
                    "sentiment": "positive"
                },
                {
                    "title": "Circular Economy Transition Progress",
                    "content": "Circular economy transition metrics show 45% of product portfolio now incorporates circular design principles, up from 20% in 2021. Recycled content has increased to an average of 35% across all packaging, while take-back programs have been implemented for 60% of eligible product lines with a 25% customer participation rate.",
                    "metric": "Waste Management",
                    "sentiment": "positive"
                }
            ]
        }
        
        # Generate stories for each category
        for story_category in self.story_categories:
            # Skip if filtering by category and this doesn't match
            if category and category.lower() not in story_category.lower():
                continue
            
            # Get content for this category
            category_stories = story_content.get(story_category, [])
            
            # Create a story for each content item
            for story_item in category_stories:
                # Generate random date in last 90 days
                created_at = datetime.now() - timedelta(days=random.randint(1, 90))
                
                stories.append({
                    "id": f"story_{len(stories) + 1}",
                    "title": story_item["title"],
                    "category": story_category,
                    "metric": story_item.get("metric", "General"),
                    "content": story_item["content"],
                    "sentiment": story_item.get("sentiment", "neutral"),
                    "author": "AI Storytelling Engine",
                    "created_at": created_at.isoformat(),
                    "tags": [story_category, story_item.get("metric", "General")],
                    "status": "published",
                    "visual_type": random.choice(["chart", "table", "infographic", "none"]),
                    "related_frameworks": random.choice(["CSRD", "GRI", "SASB", "TCFD", "None"])
                })
                
                # Break if we've reached the limit
                if len(stories) >= limit:
                    break
            
            # Break if we've reached the limit
            if len(stories) >= limit:
                break
        
        return stories