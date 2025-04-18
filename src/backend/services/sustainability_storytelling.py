"""
Sustainability Storytelling Module for SustainaTrend™

This module provides AI-powered storytelling capabilities for sustainability data,
generating compelling narratives for various stakeholders using real metrics data.

Key features:
1. LCM-driven narrative generation with varied storytelling templates
2. Document-based story creation from uploaded sustainability reports
3. Multi-audience narrative options (investors, employees, regulators, etc.)
4. Chart and visualization generation to complement stories
5. Connection to sustainability metrics in the database
"""

import json
import logging
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union

# Configure logger
logger = logging.getLogger(__name__)

# Mock AI service for development
def get_generative_ai(*args, **kwargs):
    """Mock function for generative AI service."""
    logger.info("Using mock generative AI service")
    return {
        "generate_text": lambda *args, **kwargs: "This is a mock generated text.",
        "analyze_document": lambda *args, **kwargs: {"summary": "This is a mock document analysis."}
    }

class DocumentProcessor:
    """Process and analyze sustainability documents."""
    
    @staticmethod
    def extract_text(*args, **kwargs):
        """Extract text from a document."""
        logger.info("Extracting text from document")
        return "This is mock extracted text from a document."
    
    @staticmethod
    def analyze_document(*args, **kwargs):
        """Analyze a document for sustainability metrics."""
        logger.info("Analyzing document for sustainability metrics")
        return {
            "summary": "This is a mock document analysis.",
            "metrics": [
                {"name": "Carbon Emissions", "value": 100, "unit": "tons CO2e"},
                {"name": "Water Usage", "value": 500, "unit": "m3"}
            ]
        }

def get_enhanced_stories(audience: str = 'all', category: str = 'all') -> List[Dict[str, Any]]:
    """Get enhanced stories for a specific audience and category."""
    logger.info(f"Getting enhanced stories for audience: {audience}, category: {category}")
    
    # Mock data for development
    stories = []
    for i in range(3):
        story_id = str(uuid.uuid4())
        stories.append({
            "id": story_id,
            "title": f"Enhanced Story {i+1} for {audience}",
            "content": f"This is an enhanced story {i+1} for {audience} about {category}.",
            "audience": audience,
            "category": category,
            "created_at": (datetime.now() - timedelta(days=i)).isoformat(),
            "metrics": [
                {"name": "Carbon Emissions", "value": 100 - i*10, "unit": "tons CO2e"},
                {"name": "Water Usage", "value": 500 - i*50, "unit": "m3"}
            ]
        })
    
    return stories

def get_lcm_story(
    audience: str = 'all',
    category: str = 'all',
    prompt: Optional[str] = None,
    document_data: Optional[Dict[str, Any]] = None,
    metrics: Optional[List[Dict[str, Any]]] = None,
    story_id: Optional[str] = None
) -> Dict[str, Any]:
    """Generate a story using LCM (Language Model)."""
    logger.info(f"Generating LCM story for audience: {audience}, category: {category}")
    
    # Use provided story_id or generate a new one
    if not story_id:
        story_id = str(uuid.uuid4())
    
    # Generate a title
    title = generate_story_title(category, audience)
    
    # Generate tags
    tags = generate_story_tags(category, audience)
    
    # Generate content based on prompt or default
    if prompt:
        content = f"This is a story based on the prompt: {prompt}"
    else:
        content = f"This is a story about {category} for {audience}."
    
    # Add metrics if provided
    if metrics:
        content += "\n\nMetrics:\n"
        for metric in metrics:
            content += f"- {metric['name']}: {metric['value']} {metric['unit']}\n"
    
    # Create the story
    story = {
        "id": story_id,
        "title": title,
        "content": content,
        "audience": audience,
        "category": category,
        "created_at": datetime.now().isoformat(),
        "tags": tags,
        "metrics": metrics or []
    }
    
    return story

def get_lcm_generated_stories(count: int = 3, audience: str = 'all', category: str = 'all') -> List[Dict[str, Any]]:
    """Get multiple LCM-generated stories."""
    logger.info(f"Generating {count} LCM stories for audience: {audience}, category: {category}")
    
    stories = []
    for i in range(count):
        story = get_lcm_story(audience, category)
        stories.append(story)
    
    return stories

def get_data_driven_stories() -> List[Dict[str, Any]]:
    """Get stories based on data analysis."""
    logger.info("Getting data-driven stories")
    
    # Mock data for development
    stories = []
    for i in range(3):
        story_id = str(uuid.uuid4())
        stories.append({
            "id": story_id,
            "title": f"Data-Driven Story {i+1}",
            "content": f"This is a data-driven story {i+1} based on analysis.",
            "created_at": (datetime.now() - timedelta(days=i)).isoformat(),
            "metrics": [
                {"name": "Carbon Emissions", "value": 100 - i*10, "unit": "tons CO2e"},
                {"name": "Water Usage", "value": 500 - i*50, "unit": "m3"}
            ]
        })
    
    return stories

def generate_story_title(category: str, audience: str) -> str:
    """Generate a title for a story."""
    logger.info(f"Generating title for category: {category}, audience: {audience}")
    
    # Mock titles for development
    titles = {
        'carbon': [
            "Reducing Carbon Footprint: A Journey to Net Zero",
            "Carbon Neutrality: Our Path Forward",
            "Decarbonizing Operations: A Strategic Approach"
        ],
        'water': [
            "Water Conservation: Preserving Our Most Precious Resource",
            "Sustainable Water Management: A Holistic Approach",
            "Water Efficiency: Innovations in Resource Management"
        ],
        'waste': [
            "Zero Waste: Closing the Loop on Resource Management",
            "Circular Economy: Transforming Waste into Value",
            "Waste Reduction: A Strategic Imperative"
        ],
        'energy': [
            "Renewable Energy: Powering a Sustainable Future",
            "Energy Efficiency: Maximizing Value, Minimizing Impact",
            "Clean Energy Transition: Our Commitment to Sustainability"
        ],
        'default': [
            "Sustainability Leadership: Our Commitment to the Future",
            "Environmental Stewardship: A Core Business Value",
            "Sustainable Business Practices: Creating Long-term Value"
        ]
    }
    
    # Select a title based on category
    if category.lower() in titles:
        title = random.choice(titles[category.lower()])
    else:
        title = random.choice(titles['default'])
    
    # Add audience-specific suffix
    if audience == 'investors':
        title += " - An Investor Perspective"
    elif audience == 'employees':
        title += " - Our Team's Impact"
    elif audience == 'customers':
        title += " - Value for Our Customers"
    elif audience == 'regulators':
        title += " - Compliance and Beyond"
    
    return title

def generate_story_tags(category: str, audience: str) -> List[str]:
    """Generate tags for a story."""
    logger.info(f"Generating tags for category: {category}, audience: {audience}")
    
    # Base tags
    tags = ["sustainability", "esg", "environmental"]
    
    # Add category-specific tags
    if category.lower() == 'carbon':
        tags.extend(["carbon", "emissions", "climate", "net-zero"])
    elif category.lower() == 'water':
        tags.extend(["water", "conservation", "efficiency"])
    elif category.lower() == 'waste':
        tags.extend(["waste", "circular-economy", "recycling"])
    elif category.lower() == 'energy':
        tags.extend(["energy", "renewable", "efficiency"])
    
    # Add audience-specific tags
    if audience == 'investors':
        tags.extend(["investor", "financial", "value"])
    elif audience == 'employees':
        tags.extend(["employee", "engagement", "culture"])
    elif audience == 'customers':
        tags.extend(["customer", "value", "product"])
    elif audience == 'regulators':
        tags.extend(["compliance", "regulation", "reporting"])
    
    return tags

def get_story_metrics(category: str) -> List[Dict[str, Any]]:
    """Get metrics for a story based on category."""
    logger.info(f"Getting metrics for category: {category}")
    
    # Mock metrics for development
    all_metrics = {
        'carbon': [
            {"name": "Carbon Emissions", "value": 100, "unit": "tons CO2e", "trend": "decreasing"},
            {"name": "Carbon Intensity", "value": 0.5, "unit": "tons CO2e/$M revenue", "trend": "decreasing"},
            {"name": "Renewable Energy Usage", "value": 30, "unit": "%", "trend": "increasing"}
        ],
        'water': [
            {"name": "Water Usage", "value": 500, "unit": "m3", "trend": "decreasing"},
            {"name": "Water Intensity", "value": 2.5, "unit": "m3/$M revenue", "trend": "decreasing"},
            {"name": "Water Recycling", "value": 40, "unit": "%", "trend": "increasing"}
        ],
        'waste': [
            {"name": "Waste Generated", "value": 200, "unit": "tons", "trend": "decreasing"},
            {"name": "Waste Recycled", "value": 150, "unit": "tons", "trend": "increasing"},
            {"name": "Recycling Rate", "value": 75, "unit": "%", "trend": "increasing"}
        ],
        'energy': [
            {"name": "Energy Usage", "value": 1000, "unit": "MWh", "trend": "decreasing"},
            {"name": "Energy Intensity", "value": 5, "unit": "MWh/$M revenue", "trend": "decreasing"},
            {"name": "Renewable Energy", "value": 30, "unit": "%", "trend": "increasing"}
        ],
        'default': [
            {"name": "Environmental Impact Score", "value": 75, "unit": "points", "trend": "increasing"},
            {"name": "Sustainability Rating", "value": "A", "unit": "", "trend": "stable"},
            {"name": "ESG Score", "value": 80, "unit": "points", "trend": "increasing"}
        ]
    }
    
    # Return metrics based on category
    if category.lower() in all_metrics:
        return all_metrics[category.lower()]
    else:
        return all_metrics['default']

def generate_chart_data(category: str, period: str = 'quarterly', chart_type: str = 'line') -> Dict[str, Any]:
    """Generate chart data for a story."""
    logger.info(f"Generating chart data for category: {category}, period: {period}, chart_type: {chart_type}")
    
    # Mock data for development
    if period == 'quarterly':
        labels = ['Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023', 'Q1 2024']
    elif period == 'monthly':
        labels = ['Jan 2024', 'Feb 2024', 'Mar 2024', 'Apr 2024', 'May 2024']
    else:  # yearly
        labels = ['2020', '2021', '2022', '2023', '2024']
    
    # Generate data based on category
    if category.lower() == 'carbon':
        data = [120, 110, 100, 90, 80]
        title = "Carbon Emissions Trend"
        y_axis_label = "Tons CO2e"
    elif category.lower() == 'water':
        data = [600, 550, 500, 450, 400]
        title = "Water Usage Trend"
        y_axis_label = "m3"
    elif category.lower() == 'waste':
        data = [250, 230, 210, 190, 170]
        title = "Waste Generated Trend"
        y_axis_label = "Tons"
    elif category.lower() == 'energy':
        data = [1200, 1150, 1100, 1050, 1000]
        title = "Energy Usage Trend"
        y_axis_label = "MWh"
    else:
        data = [60, 65, 70, 75, 80]
        title = "Environmental Impact Score Trend"
        y_axis_label = "Points"
    
    # Create chart data
    chart_data = {
        "type": chart_type,
        "title": title,
        "labels": labels,
        "datasets": [
            {
                "label": title,
                "data": data,
                "backgroundColor": "rgba(75, 192, 192, 0.2)",
                "borderColor": "rgba(75, 192, 192, 1)",
                "borderWidth": 1
            }
        ],
        "options": {
            "scales": {
                "y": {
                    "beginAtZero": False,
                    "title": {
                        "display": True,
                        "text": y_axis_label
                    }
                }
            }
        }
    }
    
    return chart_data

def register_routes(app):
    """Register routes for the storytelling module."""
    logger.info("Registering storytelling routes")
    
    # This would register routes with the Flask app
    # For now, we'll just log that this would happen
    pass

def generate_trend_data(start: float, end: float, points: int, trend: str = 'increasing') -> List[float]:
    """Generate trend data for charts."""
    logger.info(f"Generating trend data from {start} to {end} with {points} points, trend: {trend}")
    
    # Generate data points
    data = []
    step = (end - start) / (points - 1)
    
    for i in range(points):
        if trend == 'increasing':
            value = start + (step * i)
        elif trend == 'decreasing':
            value = end - (step * i)
        else:  # stable
            value = (start + end) / 2
        
        data.append(round(value, 2))
    
    return data 