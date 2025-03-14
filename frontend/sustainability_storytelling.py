"""
Sustainability Storytelling Module for SustainaTrend™

This module provides functionality for generating data-driven storytelling content
based on sustainability metrics and trends. It focuses on creating compelling narratives
for different stakeholder audiences with proper context, narrative, and visual elements.

Key features:
1. Enhanced data storytelling with the three core elements (Context, Narrative, Visual)
2. Stakeholder-specific storytelling options (Board, Sustainability Teams, Investors)
3. Interactive story card generation with AI-driven insights
4. CSRD/ESG compliance narrative integration
"""
import random
import logging
import json
import re
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    from flask import Blueprint, request, jsonify, render_template, current_app, redirect, url_for
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    logging.warning("Flask not available. Web routes will not be registered.")

try:
    import numpy as np
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    logging.warning("Visualization libraries not available. Chart generation will be limited.")

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint for routes
storytelling_bp = Blueprint('storytelling', __name__) if FLASK_AVAILABLE else None

def get_data_driven_stories():
    """Generate data-driven sustainability stories based on sustainability metrics"""
    stories = []
    
    # Generate stories based on sustainability categories
    categories = ["emissions", "water", "waste", "energy", "social"]
    impacts = ["positive", "negative", "neutral"]
    authors = ["Sustainability Team", "Operations Team", "Facilities Management", "Executive Team"]
    
    # Create one story for each category for consistent coverage
    for category in categories:
        story_id = str(uuid.uuid4())
        impact = random.choice(impacts)
        author = random.choice(authors)
        
        # Generate appropriate title and content based on category and impact
        if category == "emissions":
            if impact == "positive":
                title = "Carbon Emissions Reduction Progress"
                content = "Carbon reduction initiatives are showing measurable results with emissions down compared to the previous reporting period."
            else:
                title = "Carbon Emissions Challenge"
                content = "Recent data indicates challenges in meeting emissions targets due to increased production and operational changes."
        
        elif category == "water":
            if impact == "positive":
                title = "Water Conservation Efficiency"
                content = "Water efficiency measures have reduced consumption rates across facilities while maintaining operational capacity."
            else:
                title = "Water Usage Management"
                content = "Increasing water usage requires attention and refined water management practices to meet sustainability goals."
        
        elif category == "waste":
            if impact == "positive":
                title = "Waste Reduction Success"
                content = "Our waste reduction and circular economy initiatives are demonstrating measurable improvements in diversion rates."
            else:
                title = "Waste Stream Analysis"
                content = "Analysis of waste streams indicates opportunities for improved sorting and recycling processes."
        
        elif category == "energy":
            if impact == "positive":
                title = "Energy Efficiency Gains"
                content = "Energy optimization programs have resulted in reduced consumption despite operational growth."
            else:
                title = "Energy Performance Review"
                content = "Review of energy consumption patterns indicates areas requiring efficiency improvements and potential for renewable integration."
        
        elif category == "social":
            if impact == "positive":
                title = "Social Impact Progress"
                content = "Our diversity, equity and inclusion initiatives are showing positive trends based on latest metrics."
            else:
                title = "Social Metric Assessment"
                content = "Assessment of social sustainability metrics highlights areas for strategic improvement and stakeholder engagement."
        
        # Create the story with standardized fields
        story = {
            "id": story_id,
            "title": title,
            "content": content,
            "category": category,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "author": author,
            "impact": impact,
            "recommendations": [
                f"Review {category} strategies and targets",
                f"Enhance data collection for {category} metrics",
                f"Develop stakeholder communication on {category} performance"
            ]
        }
        
        stories.append(story)
    
    return stories

def get_enhanced_stories(audience='all', category='all', prompt=None, document_data=None):
    """
    Generate enhanced stories with the three core elements of data storytelling:
    - Context: Why does this matter now?
    - Narrative: What is happening?
    - Visual: How does the data look?
    
    Each story is designed for specific stakeholder audiences and includes
    actionable insights based on Gartner's data storytelling methodology.
    
    Args:
        audience: Target audience filter ('board', 'sustainability_team', 'investors', or 'all')
        category: Category filter ('emissions', 'water', 'energy', 'waste', 'social', or 'all')
        prompt: Optional custom prompt to guide story generation with specific details
        document_data: Optional document data to use as source for storytelling
        
    Returns:
        List of enhanced story dictionaries
    """
    logger.info(f"Generating enhanced stories for audience: {audience}, category: {category}, prompt: {prompt}, document_data: {'provided' if document_data else 'not provided'}")
    
    # Base stories to enhance
    base_stories = get_data_driven_stories()
    enhanced_stories = []
    
    # Apply document data if provided
    if document_data:
        logger.info(f"Using document data for story generation")
        
        # Extract relevant information from document data
        document_title = document_data.get('title', 'Sustainability Document')
        document_content = document_data.get('content', '')
        document_insights = document_data.get('insights', [])
        document_metrics = document_data.get('metrics', [])
        
        # Determine document categories based on content
        # This would use more sophisticated NLP in production
        document_categories = []
        category_keywords = {
            'emissions': ['carbon', 'emission', 'ghg', 'greenhouse', 'scope 1', 'scope 2', 'scope 3'],
            'water': ['water', 'effluent', 'discharge', 'consumption'],
            'energy': ['energy', 'electricity', 'power', 'renewable', 'kwh', 'megawatt'],
            'waste': ['waste', 'circular', 'recycl', 'landfill', 'compost'],
            'social': ['diversity', 'inclusion', 'employee', 'community', 'human rights'],
            'governance': ['governance', 'board', 'compliance', 'ethics', 'transparency']
        }
        
        content_lower = document_content.lower()
        for cat, keywords in category_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                document_categories.append(cat)
        
        # Default category if none detected
        if not document_categories:
            document_categories = ['emissions']
        
        # Create a title from the document
        title = f"Story from Document: {document_title}"
        
        # Create story content and insights from document
        content_preview = document_content[:500] + "..." if len(document_content) > 500 else document_content
        
        # Create insights from document
        insights = []
        if document_insights:
            insights = document_insights[:3]  # Use top 3 insights
        else:
            insights = [
                f"Document analysis reveals key sustainability information",
                f"The document contains information about {', '.join(document_categories)}",
                f"Further analysis can provide deeper insights"
            ]
        
        # Create recommendations based on document categories
        recommendations = []
        for cat in document_categories[:3]:  # Use top 3 categories
            if cat == 'emissions':
                recommendations.append("Develop carbon reduction strategies based on document insights")
            elif cat == 'water':
                recommendations.append("Implement water conservation initiatives based on document findings")
            elif cat == 'energy':
                recommendations.append("Enhance energy efficiency programs as suggested in the document")
            elif cat == 'waste':
                recommendations.append("Expand circular economy practices mentioned in the document")
            elif cat == 'social':
                recommendations.append("Strengthen social impact programs outlined in the document")
            elif cat == 'governance':
                recommendations.append("Improve governance mechanisms detailed in the document")
        
        # Create a document-based story
        document_story = {
            "id": str(uuid.uuid4()),
            "title": title,
            "content": f"This sustainability story is derived from document analysis. {content_preview}",
            "category": document_categories[0],  # Use first category as primary
            "impact": "positive",
            "audience": audience if audience != 'all' else "board",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "document_generated": True,
            "document_title": document_title,
            "document_categories": document_categories,
            "insights": insights,
            "recommendations": recommendations,
            "source": "document"
        }
        
        # Use document story as base
        base_stories = [document_story]
        
    # Apply custom prompt if provided
    elif prompt:
        # Log that we're using a custom prompt for story generation
        logger.info(f"Using custom prompt for story generation: {prompt}")
        
        # In a production environment, we would use an AI service here
        # For now, we'll create a more sophisticated custom story based on the prompt
        
        # Create a title from the prompt
        if len(prompt) > 50:
            title = f"{prompt[:47]}..."
        else:
            title = prompt
            
        # Clean up title and capitalize
        title = title.strip()
        if not title.endswith(('.', '!', '?')):
            title = f"{title}."
        title = f"Custom Story: {title}"
        
        # Create a more detailed story content based on audience and category
        audience_focus = {
            'board': "strategic implications and financial impacts",
            'investors': "long-term value creation and competitive advantages",
            'sustainability_team': "implementation details and technical metrics",
            'employees': "workplace impacts and employee engagement opportunities",
            'customers': "product benefits and brand reputation",
            'regulators': "compliance measures and risk mitigation",
            'all': "organizational impacts across all stakeholders"
        }
        
        category_focus = {
            'emissions': "carbon emissions and climate action",
            'water': "water management and conservation",
            'energy': "energy efficiency and renewable sources",
            'waste': "waste reduction and circular economy principles",
            'social': "social impact and community engagement",
            'governance': "leadership practices and ethical standards",
            'biodiversity': "ecosystem health and biodiversity protection",
            'climate': "climate resilience and adaptation strategies",
            'all': "comprehensive sustainability performance"
        }
        
        # Generate a content template
        audience_text = audience_focus.get(audience, audience_focus['all'])
        category_text = category_focus.get(category, category_focus['all'])
        
        # Create a custom story with the prompt embedded
        custom_story = {
            "id": str(uuid.uuid4()),
            "title": title,
            "content": f"This sustainability story focuses on {category_text} with emphasis on {audience_text}. {prompt}",
            "category": category if category != 'all' else "emissions",
            "impact": "positive",
            "audience": audience if audience != 'all' else "board",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "custom_prompt_generated": True,
            "prompt": prompt,
            "insights": [
                f"Analysis of {category_text} reveals opportunities for improvement.",
                f"Stakeholder analysis shows {audience_text} is a key consideration.",
                f"Custom insights based on prompt: {prompt[:50]}..."
            ],
            "recommendations": [
                f"Develop targeted {category_text} strategies.",
                f"Communicate results effectively to {audience_text}.",
                f"Implement a measurement system to track progress."
            ]
        }
        
        # Use the custom story as our base if a prompt is provided
        base_stories = [custom_story]
    
    # Define audience-specific elements
    audience_elements = {
        "board": {
            "focus": "Strategic impact and risk",
            "metrics_highlight": "Financial implications",
            "action_orientation": "Executive decisions",
            "time_horizon": "Quarterly and annual",
            "depth": "High-level overview"
        },
        "sustainability_team": {
            "focus": "Implementation details and root causes",
            "metrics_highlight": "Technical sustainability KPIs",
            "action_orientation": "Tactical implementation",
            "time_horizon": "Weekly and monthly",
            "depth": "Detailed analysis"
        },
        "investors": {
            "focus": "Competitive positioning and compliance",
            "metrics_highlight": "ROI and risk mitigation",
            "action_orientation": "Investment rationale",
            "time_horizon": "Annual and multi-year",
            "depth": "Benchmark comparison"
        }
    }
    
    for story in base_stories:
        # Filter by category if specified
        if category != 'all' and story['category'] != category:
            continue
            
        # Create enhanced version of each story
        enhanced_story = story.copy()
        
        # If prompt is provided and this isn't already a custom prompt story, enhance it
        if prompt and not story.get('custom_prompt_generated', False):
            # Create a more sophisticated prompt enhancement
            story_content = story.get('content', '')
            
            # Generate a contextual connector between the story and the prompt
            connectors = [
                "This directly relates to",
                "This connects with",
                "Additionally, consider that",
                "This insight is complemented by",
                "This finding is especially relevant when considering",
                "To put this in perspective"
            ]
            
            connector = random.choice(connectors)
            enhanced_content = f"{story_content} {connector} {prompt}"
            
            enhanced_story['content'] = enhanced_content
            enhanced_story['prompt'] = prompt
            enhanced_story['prompt_enhanced'] = True
            
            # Add insights from the prompt
            if 'insights' not in enhanced_story:
                enhanced_story['insights'] = []
                
            enhanced_story['insights'].append(f"Custom insight: {prompt[:50]}...")
            
            # Add a recommendation based on the prompt
            if 'recommendations' not in enhanced_story:
                enhanced_story['recommendations'] = []
                
            enhanced_story['recommendations'].append(f"Consider {prompt[:50]}... in your sustainability strategy.")
        
        # Add the three core elements of data storytelling
        enhanced_story["storytelling_elements"] = {
            "context": generate_context_element(story),
            "narrative": generate_narrative_element(story),
            "visual": generate_visual_element(story)
        }
        
        # Add stakeholder-specific versions
        enhanced_story["stakeholder_versions"] = {}
        
        for audience_key, audience_attributes in audience_elements.items():
            enhanced_story["stakeholder_versions"][audience_key] = {
                "title": adapt_title_for_audience(story["title"], audience_key),
                "summary": generate_audience_summary(story, audience_key),
                "key_points": generate_audience_key_points(story, audience_key, audience_attributes),
                "recommendations": generate_audience_recommendations(story, audience_key),
                "metrics_focus": audience_attributes["metrics_highlight"]
            }
        
        # Add enhanced metadata
        enhanced_story["augmented_analytics"] = True
        enhanced_story["gartner_inspired"] = True
        enhanced_story["date_generated"] = datetime.now().strftime("%Y-%m-%d")
        enhanced_story["story_type"] = "interactive"
        
        # Add to results
        if audience == 'all' or audience in enhanced_story["stakeholder_versions"]:
            enhanced_stories.append(enhanced_story)
    
    logger.info(f"Generated {len(enhanced_stories)} enhanced stories")
    
    # If no stories were generated, create a default one to ensure there's always content
    if not enhanced_stories:
        logger.info(f"No matching stories found, generating a default story")
        
        default_story = {
            "id": str(uuid.uuid4()),
            "title": f"Sustainability Report: {category.capitalize() if category != 'all' else 'Overview'} for {audience.capitalize() if audience != 'all' else 'All Stakeholders'}",
            "content": f"This sustainability analysis focuses on {category if category != 'all' else 'all sustainability topics'} with emphasis on {audience if audience != 'all' else 'all audiences'}. " + 
                      (prompt if prompt else "Our organization continues to make progress toward sustainability goals through dedicated initiatives and stakeholder engagement."),
            "category": category if category != 'all' else "general",
            "impact": "positive",
            "audience": audience if audience != 'all' else "general",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "custom_prompt_generated": True if prompt else False,
            "prompt": prompt if prompt else None,
            "recommendations": [
                f"Review {category if category != 'all' else 'sustainability'} metrics regularly",
                f"Engage with {audience if audience != 'all' else 'all stakeholders'} on progress",
                "Implement a data-driven sustainability strategy"
            ]
        }
        
        enhanced_stories = [default_story]
        logger.info(f"Generated default story with ID: {default_story['id']}")
    
    return enhanced_stories

def generate_chart_data(story_category="emissions", time_period="quarterly", chart_type=None):
    """
    Generate chart data for a sustainability story visualization
    
    Args:
        story_category: Category of sustainability story (emissions, water, energy, etc.)
        time_period: Time period for data (quarterly, monthly, yearly)
        chart_type: Optional specific chart type or None for auto-selection
        
    Returns:
        Dictionary with chart data and metadata
    """
    logger.info(f"Generating chart data for {story_category}, period: {time_period}, chart type: {chart_type}")
    
    # Generate time periods based on specified frequency
    if time_period == "quarterly":
        periods = ["Q1", "Q2", "Q3", "Q4"]
        year = datetime.now().year
        labels = [f"{year-1} {p}" for p in periods] + [f"{year} {p}" for p in periods[:2]]
    elif time_period == "monthly":
        periods = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        year = datetime.now().year
        labels = [f"{p} {year-1}" for p in periods[-6:]] + [f"{p} {year}" for p in periods[:6]]
    else:  # yearly
        year = datetime.now().year
        labels = [str(y) for y in range(year-5, year+1)]
    
    # Create appropriate data based on category
    if story_category == "emissions":
        # Generate realistic-looking emissions data with a reduction trend
        values = [100, 95, 92, 88, 84, 79, 75, 72]
        target_values = [100, 90, 80, 70, 60, 50, 40, 30]
        industry_avg = [100, 98, 96, 94, 92, 90, 88, 86]
        
        # Auto-select an appropriate chart type if not specified
        if not chart_type:
            chart_type = "line"
            
        return {
            "chart_type": chart_type,
            "title": "Carbon Emissions Reduction Progress",
            "labels": labels[-8:],
            "datasets": [
                {
                    "label": "Actual Emissions",
                    "data": values[-len(labels):],
                    "borderColor": "#36A2EB",
                    "backgroundColor": "rgba(54, 162, 235, 0.2)",
                    "tension": 0.3
                },
                {
                    "label": "Reduction Target",
                    "data": target_values[-len(labels):],
                    "borderColor": "#FF6384",
                    "backgroundColor": "rgba(255, 99, 132, 0.1)",
                    "borderDash": [5, 5],
                    "tension": 0.1
                },
                {
                    "label": "Industry Average",
                    "data": industry_avg[-len(labels):],
                    "borderColor": "#4BC0C0",
                    "backgroundColor": "rgba(75, 192, 192, 0.1)",
                    "borderDash": [2, 2],
                    "tension": 0.1
                }
            ],
            "axes": {
                "y": {
                    "title": "CO2e (tons, indexed to base year)",
                    "min": 0
                },
                "x": {
                    "title": "Time Period"
                }
            }
        }
    elif story_category == "water":
        # Water usage efficiency data with improvement trend
        values = [120, 118, 115, 110, 102, 95, 90, 85]
        target_values = [120, 110, 100, 90, 80, 70, 60, 50]
        
        # Auto-select an appropriate chart type if not specified
        if not chart_type:
            chart_type = "bar"
            
        return {
            "chart_type": chart_type,
            "title": "Water Usage Efficiency",
            "labels": labels[-8:],
            "datasets": [
                {
                    "label": "Actual Usage",
                    "data": values[-len(labels):],
                    "backgroundColor": "rgba(54, 162, 235, 0.6)",
                    "borderColor": "#36A2EB",
                    "borderWidth": 1
                },
                {
                    "label": "Target Usage",
                    "data": target_values[-len(labels):],
                    "backgroundColor": "rgba(255, 99, 132, 0.2)",
                    "borderColor": "#FF6384",
                    "borderWidth": 1,
                    "type": "line"
                }
            ],
            "axes": {
                "y": {
                    "title": "Water usage (kL per unit production)",
                    "min": 0
                },
                "x": {
                    "title": "Time Period"
                }
            }
        }
    else:
        # Generic sustainability metric with improvement trend
        values = [50, 55, 60, 65, 70, 75, 77, 80]
        
        # Auto-select an appropriate chart type if not specified
        if not chart_type:
            chart_type = "line"
            
        return {
            "chart_type": chart_type,
            "title": f"{story_category.capitalize()} Performance",
            "labels": labels[-8:],
            "datasets": [
                {
                    "label": f"{story_category.capitalize()} Score",
                    "data": values[-len(labels):],
                    "borderColor": "#36A2EB",
                    "backgroundColor": "rgba(54, 162, 235, 0.2)",
                    "tension": 0.4
                }
            ],
            "axes": {
                "y": {
                    "title": "Performance Score",
                    "min": 0,
                    "max": 100
                },
                "x": {
                    "title": "Time Period"
                }
            }
        }

def generate_context_element(story):
    """Generate the context element for a story (why it matters now)"""
    context_templates = {
        "emissions": [
            "Due to new EU CSRD regulations requiring detailed carbon reporting",
            "As global climate targets tighten following COP26 agreements",
            "With carbon pricing mechanisms being implemented in your market"
        ],
        "water": [
            "As water scarcity becomes a material risk in key operation regions",
            "With water-related ESG metrics now influencing investor decisions",
            "As water usage efficiency becomes a competitive advantage in your industry"
        ],
        "energy": [
            "Amid rising energy costs and volatility in the energy market",
            "As renewable energy transitions become central to climate strategies",
            "With energy efficiency directly impacting operational costs"
        ],
        "waste": [
            "As circular economy principles become regulatory requirements",
            "With waste management costs increasing due to stricter disposal regulations",
            "As zero-waste initiatives gain traction among industry leaders"
        ],
        "social": [
            "As diversity reporting becomes mandatory under new regulations",
            "With talent attraction increasingly linked to social performance metrics",
            "Amid growing scrutiny of social aspects of ESG from investors"
        ]
    }
    
    templates = context_templates.get(story["category"], ["As sustainability becomes increasingly important"])
    
    return {
        "headline": "Why This Matters Now",
        "content": random.choice(templates),
        "significance": "high" if story["impact"] == "positive" else "medium"
    }

def generate_narrative_element(story):
    """Generate the narrative element for a story (what is happening)"""
    impact_descriptors = {
        "positive": ["improvement", "success", "achievement", "advancement", "progress"],
        "negative": ["challenge", "issue", "decline", "problem", "concern"],
        "neutral": ["change", "shift", "development", "transition", "adjustment"]
    }
    
    descriptor = random.choice(impact_descriptors.get(story["impact"], ["change"]))
    
    narrative = {
        "headline": f"The {story['category'].title()} {descriptor.title()}",
        "content": story["content"],
        "data_point": {
            "value": extract_percentage(story["content"]) if extract_percentage(story["content"]) else "15%",
            "trend": story["impact"],
            "comparison": "year-over-year"
        }
    }
    
    return narrative

def generate_visual_element(story):
    """Generate the visual element description for a story (how the data looks)"""
    chart_types = {
        "emissions": ["area chart", "line chart", "bar chart"],
        "water": ["bar chart", "area chart", "waterfall chart"],
        "energy": ["line chart", "heat map", "stacked bar chart"],
        "waste": ["pie chart", "stacked area chart", "tree map"],
        "social": ["radar chart", "doughnut chart", "column chart"]
    }
    
    chart_type = random.choice(chart_types.get(story["category"], ["bar chart"]))
    
    return {
        "chart_type": chart_type,
        "title": f"{story['category'].title()} {story['impact'].title()} Visualization",
        "data_series": [
            {
                "name": "Current Period",
                "color": "#4CAF50" if story["impact"] == "positive" else "#F44336"
            },
            {
                "name": "Previous Period",
                "color": "#9E9E9E"
            },
            {
                "name": "Industry Benchmark",
                "color": "#2196F3"
            }
        ],
        "annotations": [
            {
                "type": "threshold",
                "value": extract_percentage(story["content"]) if extract_percentage(story["content"]) else "15%",
                "label": "Target"
            }
        ]
    }

def adapt_title_for_audience(title, audience):
    """Adapt the story title for a specific audience"""
    if audience == "board":
        return f"Executive Brief: {title}"
    elif audience == "sustainability_team":
        return f"Technical Analysis: {title}"
    elif audience == "investors":
        return f"Investor Insight: {title}"
    else:
        return title

def generate_audience_summary(story, audience):
    """Generate an audience-specific summary of the story"""
    if audience == "board":
        return f"Strategic overview of {story['category']} performance with financial and risk implications highlighted."
    elif audience == "sustainability_team":
        return f"Detailed analysis of {story['category']} metrics with root causes and technical implementation guidance."
    elif audience == "investors":
        return f"Investment perspective on {story['category']} performance with competitive benchmarking and compliance status."
    else:
        return story["content"]

def generate_audience_key_points(story, audience, attributes):
    """Generate audience-specific key points for the story"""
    key_points = []
    
    if audience == "board":
        key_points = [
            f"Strategic Impact: {story['category'].title()} performance directly affects our market position",
            f"Financial Implications: {extract_percentage(story['content'])} change in {story['category']} metrics",
            f"Risk Profile: {story['impact'].title()} impact on overall sustainability risk exposure"
        ]
    elif audience == "sustainability_team":
        key_points = [
            f"Technical Detail: {story['content']}",
            "Implementation Focus: Key areas for operational adjustment",
            f"Measurement: Detailed KPIs for tracking {story['category']} performance"
        ]
    elif audience == "investors":
        key_points = [
            f"Competitive Position: Our {story['category']} performance versus industry peers",
            f"ROI Metrics: Financial return on {story['category']} initiatives",
            "Compliance Status: Regulatory alignment and future-proofing"
        ]
    
    return key_points

def generate_audience_recommendations(story, audience):
    """Generate audience-specific recommendations for the story"""
    recommendations = []
    
    if audience == "board":
        if story["impact"] == "positive":
            recommendations = [
                "Highlight this success in next investor communications",
                f"Consider expanding {story['category']} initiatives to other areas",
                "Review resource allocation to maintain momentum"
            ]
        else:
            recommendations = [
                f"Allocate additional resources to address {story['category']} challenges",
                "Review risk mitigation strategies at next board meeting",
                "Consider external expertise to guide improvement"
            ]
    elif audience == "sustainability_team":
        if story["impact"] == "positive":
            recommendations = [
                "Document successful approaches for knowledge sharing",
                "Identify opportunities to further optimize performance",
                "Develop case study for internal learning"
            ]
        else:
            recommendations = [
                "Conduct root cause analysis with technical team",
                "Develop 30-60-90 day improvement plan",
                "Implement weekly monitoring of key metrics"
            ]
    elif audience == "investors":
        if story["impact"] == "positive":
            recommendations = [
                "Feature this success in next ESG disclosure",
                "Quantify financial benefits for investor presentations",
                "Benchmark against competition to highlight leadership"
            ]
        else:
            recommendations = [
                "Prepare transparent communication strategy for investors",
                "Develop clear remediation timeline with milestones",
                "Quantify resource requirements and expected outcomes"
            ]
    
    return recommendations

def extract_percentage(text):
    """Extract percentage from text if present"""
    import re
    match = re.search(r'(\d+)%', text)
    if match:
        return match.group(0)
    return None

def generate_data_storytelling_elements(trend_data: List[Dict[str, Any]], 
                                       framework_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate data-driven storytelling elements based on trend analysis and framework insights.
    
    Args:
        trend_data: List of trend data dictionaries
        framework_analysis: Results from applying a consulting framework
        
    Returns:
        Dictionary with storytelling elements for strategic positioning
    """
    # Core story elements
    storytelling_elements = {
        "narrative": {
            "headline": "Sustainability Performance Narrative",
            "summary": "Key insights from sustainability performance data",
            "story_arcs": []
        },
        "context": {
            "market_relevance": "How this relates to market conditions",
            "regulatory_implications": "Regulatory context and requirements",
            "stakeholder_impact": "Impact on key stakeholders"
        },
        "visual": {
            "recommended_charts": [],
            "data_highlights": [],
            "annotation_suggestions": []
        }
    }
    
    # Extract key trends for narrative
    if trend_data:
        # Find positive trends
        positive_trends = [t for t in trend_data if t.get("trend_direction") == "positive"]
        # Find negative trends
        negative_trends = [t for t in trend_data if t.get("trend_direction") == "negative"]
        
        # Create story arcs
        if positive_trends:
            storytelling_elements["narrative"]["story_arcs"].append({
                "arc_type": "success",
                "headline": "Sustainability Success Story",
                "metrics": [t["name"] for t in positive_trends[:2]],
                "narrative": f"Success in {', '.join([t['category'] for t in positive_trends[:2]])} demonstrates sustainability progress."
            })
            
        if negative_trends:
            storytelling_elements["narrative"]["story_arcs"].append({
                "arc_type": "challenge",
                "headline": "Sustainability Challenge Identified",
                "metrics": [t["name"] for t in negative_trends[:2]],
                "narrative": f"Challenges in {', '.join([t['category'] for t in negative_trends[:2]])} require attention."
            })
    
    # Add framework insights to context
    if framework_analysis:
        for key, value in framework_analysis.items():
            if key in storytelling_elements["context"]:
                storytelling_elements["context"][key] = value
    
    # Visual recommendations
    storytelling_elements["visual"]["recommended_charts"] = [
        {
            "chart_type": "line",
            "purpose": "Trend visualization",
            "metrics": ["Carbon Emissions", "Energy Usage"]
        },
        {
            "chart_type": "bar",
            "purpose": "Comparative performance",
            "metrics": ["Water Usage", "Waste Generation"]
        },
        {
            "chart_type": "radar",
            "purpose": "Balanced scorecard approach",
            "metrics": ["ESG Score", "Social Impact", "Governance Rating"]
        }
    ]
    
    return storytelling_elements

def generate_story_from_metrics(metrics_data: List[Dict[str, Any]], 
                               audience: str = "general") -> Dict[str, Any]:
    """
    Generate a complete sustainability story from metrics data.
    
    Args:
        metrics_data: List of metrics data dictionaries
        audience: Target audience ('board', 'sustainability_team', 'investors', or 'general')
        
    Returns:
        Complete story dictionary with all elements
    """
    if not metrics_data:
        return {
            "error": "No metrics data provided for story generation"
        }
    
    # Categorize metrics
    metrics_by_category = {}
    for metric in metrics_data:
        category = metric.get("category", "other")
        if category not in metrics_by_category:
            metrics_by_category[category] = []
        metrics_by_category[category].append(metric)
    
    # Find most significant metrics (largest values or changes)
    significant_metrics = []
    for category, metrics in metrics_by_category.items():
        if metrics:
            # Sort by value (descending)
            sorted_metrics = sorted(metrics, key=lambda x: x.get("value", 0), reverse=True)
            significant_metrics.append(sorted_metrics[0])
    
    if not significant_metrics:
        return {
            "error": "Could not identify significant metrics for storytelling"
        }
    
    # Select primary metric for story focus
    primary_metric = significant_metrics[0]
    
    # Create basic story
    story = {
        "id": random.randint(1000, 9999),
        "title": f"{primary_metric.get('name', 'Sustainability')} Performance Analysis",
        "content": f"Analysis of {primary_metric.get('name', 'sustainability')} metrics shows a value of {primary_metric.get('value', 0)} {primary_metric.get('unit', '')}.",
        "category": primary_metric.get("category", "sustainability"),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "author": "SustainaTrend AI",
        "impact": determine_impact(primary_metric)
    }
    
    # Enhance with storytelling elements
    enhanced_story = story.copy()
    enhanced_story["storytelling_elements"] = {
        "context": generate_context_from_metrics(metrics_data),
        "narrative": generate_narrative_from_metrics(primary_metric, metrics_data),
        "visual": generate_visual_from_metrics(primary_metric, metrics_data)
    }
    
    # Add audience-specific version
    audience_elements = {
        "board": {
            "focus": "Strategic impact and risk",
            "metrics_highlight": "Financial implications",
            "action_orientation": "Executive decisions",
            "time_horizon": "Quarterly and annual",
            "depth": "High-level overview"
        },
        "sustainability_team": {
            "focus": "Implementation details and root causes",
            "metrics_highlight": "Technical sustainability KPIs",
            "action_orientation": "Tactical implementation",
            "time_horizon": "Weekly and monthly",
            "depth": "Detailed analysis"
        },
        "investors": {
            "focus": "Competitive positioning and compliance",
            "metrics_highlight": "ROI and risk mitigation",
            "action_orientation": "Investment rationale",
            "time_horizon": "Annual and multi-year",
            "depth": "Benchmark comparison"
        }
    }
    
    attributes = audience_elements.get(audience, audience_elements["general"] if "general" in audience_elements else {})
    
    enhanced_story["stakeholder_versions"] = {
        audience: {
            "title": adapt_title_for_audience(story["title"], audience),
            "summary": generate_audience_summary_from_metrics(primary_metric, audience),
            "key_points": generate_audience_key_points_from_metrics(primary_metric, metrics_data, audience, attributes),
            "recommendations": generate_audience_recommendations_from_metrics(primary_metric, metrics_data, audience),
            "metrics_focus": attributes.get("metrics_highlight", "Key sustainability metrics")
        }
    }
    
    # Add enhanced metadata
    enhanced_story["augmented_analytics"] = True
    enhanced_story["gartner_inspired"] = True
    enhanced_story["date_generated"] = datetime.now().strftime("%Y-%m-%d")
    enhanced_story["story_type"] = "interactive"
    
    return enhanced_story

def determine_impact(metric):
    """Determine if a metric represents positive or negative impact"""
    positive_indicators = ['reduction', 'decrease', 'improved', 'increased efficiency']
    negative_indicators = ['increase', 'growth', 'higher', 'elevated']
    
    # Some metrics are positive when they increase (like ESG score)
    positive_when_increase = ['score', 'rating', 'efficiency', 'diversity', 'renewable']
    
    metric_name = metric.get('name', '').lower()
    
    # Check if this is a metric that's positive when increasing
    is_positive_when_increase = any(term in metric_name for term in positive_when_increase)
    
    # Default to neutral impact
    impact = "neutral"
    
    # If we have trend information
    if 'trend_direction' in metric:
        trend = metric['trend_direction']
        if trend == 'positive':
            impact = 'positive'
        elif trend == 'negative':
            impact = 'negative'
    # If we can determine from the metric name and value trend
    elif 'previous_value' in metric and 'value' in metric:
        value_change = metric['value'] - metric['previous_value']
        if value_change > 0:  # Value increased
            impact = 'positive' if is_positive_when_increase else 'negative'
        elif value_change < 0:  # Value decreased
            impact = 'negative' if is_positive_when_increase else 'positive'
    
    return impact

def generate_context_from_metrics(metrics_data):
    """Generate context element from metrics data"""
    # Find relevant regulatory context based on metrics categories
    categories = set(m.get('category', 'other') for m in metrics_data)
    
    regulatory_contexts = {
        'emissions': 'carbon reporting requirements under CSRD',
        'water': 'water scarcity risks and reporting',
        'energy': 'energy efficiency and renewable targets',
        'waste': 'circular economy regulations',
        'social': 'social metrics in ESG reporting frameworks'
    }
    
    relevant_contexts = []
    for category in categories:
        if category in regulatory_contexts:
            relevant_contexts.append(regulatory_contexts[category])
    
    context_content = "Within the context of " + ", ".join(relevant_contexts) if relevant_contexts else "As sustainability reporting becomes increasingly important"
    
    return {
        "headline": "Why This Matters Now",
        "content": context_content,
        "significance": "high"
    }

def generate_narrative_from_metrics(primary_metric, metrics_data):
    """Generate narrative element from metrics data"""
    # Determine the main story based on the primary metric
    metric_name = primary_metric.get('name', 'Sustainability metric')
    metric_value = primary_metric.get('value', 0)
    metric_unit = primary_metric.get('unit', '')
    
    # Check if we have previous values for comparison
    if 'previous_value' in primary_metric:
        previous_value = primary_metric['previous_value']
        change = metric_value - previous_value
        percent_change = (change / previous_value) * 100 if previous_value != 0 else 0
        
        comparison_text = f"a {abs(percent_change):.1f}% {'increase' if change > 0 else 'decrease'} compared to the previous period"
    else:
        comparison_text = f"current value of {metric_value} {metric_unit}"
    
    return {
        "headline": f"{metric_name} Analysis",
        "content": f"The {metric_name.lower()} shows {comparison_text}, indicating significant sustainability impact.",
        "data_point": {
            "value": f"{metric_value} {metric_unit}",
            "trend": determine_impact(primary_metric),
            "comparison": "period-over-period"
        }
    }

def generate_visual_from_metrics(primary_metric, metrics_data):
    """Generate visual element from metrics data"""
    category = primary_metric.get('category', 'sustainability')
    
    chart_types = {
        "emissions": ["area chart", "line chart", "bar chart"],
        "water": ["bar chart", "area chart", "waterfall chart"],
        "energy": ["line chart", "heat map", "stacked bar chart"],
        "waste": ["pie chart", "stacked area chart", "tree map"],
        "social": ["radar chart", "doughnut chart", "column chart"]
    }
    
    chart_type = random.choice(chart_types.get(category, ["bar chart"]))
    
    # Find related metrics for comparison
    related_metrics = [m for m in metrics_data if m.get('category') == category and m.get('id') != primary_metric.get('id')]
    
    data_series = [
        {
            "name": primary_metric.get('name', 'Current Metric'),
            "color": "#4CAF50" if determine_impact(primary_metric) == "positive" else "#F44336"
        }
    ]
    
    # Add related metrics if available
    for i, metric in enumerate(related_metrics[:2]):
        data_series.append({
            "name": metric.get('name', f'Related Metric {i+1}'),
            "color": ["#2196F3", "#FFC107"][i]
        })
    
    return {
        "chart_type": chart_type,
        "title": f"{category.title()} Performance Visualization",
        "data_series": data_series,
        "annotations": [
            {
                "type": "threshold",
                "value": str(primary_metric.get('value', 0)) + " " + primary_metric.get('unit', ''),
                "label": "Current"
            }
        ]
    }

def generate_audience_summary_from_metrics(primary_metric, audience):
    """Generate audience-specific summary from metrics"""
    category = primary_metric.get('category', 'sustainability')
    
    if audience == "board":
        return f"Strategic overview of {category} performance with financial and risk implications highlighted."
    elif audience == "sustainability_team":
        return f"Detailed analysis of {category} metrics with root causes and technical implementation guidance."
    elif audience == "investors":
        return f"Investment perspective on {category} performance with competitive benchmarking and compliance status."
    else:
        return f"Analysis of {category} sustainability performance with key insights."

def generate_audience_key_points_from_metrics(primary_metric, metrics_data, audience, attributes):
    """Generate audience-specific key points from metrics"""
    category = primary_metric.get('category', 'sustainability')
    value = primary_metric.get('value', 0)
    unit = primary_metric.get('unit', '')
    
    key_points = []
    
    if audience == "board":
        key_points = [
            f"Strategic Impact: {category.title()} performance directly affects our market position",
            f"Financial Implications: Current {category} value of {value} {unit}",
            f"Risk Profile: {determine_impact(primary_metric).title()} impact on overall sustainability risk exposure"
        ]
    elif audience == "sustainability_team":
        key_points = [
            f"Technical Detail: Current {category} value is {value} {unit}",
            f"Implementation Focus: Detailed analysis of {category} performance factors",
            f"Measurement: Key metrics for tracking {category} progress"
        ]
    elif audience == "investors":
        key_points = [
            f"Competitive Position: Our {category} performance versus industry peers",
            f"ROI Metrics: Financial implications of {category} initiatives",
            "Compliance Status: Regulatory alignment and future-proofing"
        ]
    else:
        key_points = [
            f"{category.title()} Performance: Current value of {value} {unit}",
            "Key Insights: Analysis of sustainability metrics",
            "Next Steps: Recommended actions based on current performance"
        ]
    
    return key_points

def generate_audience_recommendations_from_metrics(primary_metric, metrics_data, audience):
    """Generate audience-specific recommendations from metrics"""
    category = primary_metric.get('category', 'sustainability')
    impact = determine_impact(primary_metric)
    
    recommendations = []
    
    if audience == "board":
        if impact == "positive":
            recommendations = [
                "Highlight this success in next investor communications",
                f"Consider expanding {category} initiatives to other areas",
                "Review resource allocation to maintain momentum"
            ]
        else:
            recommendations = [
                f"Allocate additional resources to address {category} challenges",
                "Review risk mitigation strategies at next board meeting",
                "Consider external expertise to guide improvement"
            ]
    elif audience == "sustainability_team":
        if impact == "positive":
            recommendations = [
                "Document successful approaches for knowledge sharing",
                "Identify opportunities to further optimize performance",
                "Develop case study for internal learning"
            ]
        else:
            recommendations = [
                "Conduct root cause analysis with technical team",
                "Develop 30-60-90 day improvement plan",
                "Implement weekly monitoring of key metrics"
            ]
    elif audience == "investors":
        if impact == "positive":
            recommendations = [
                "Feature this success in next ESG disclosure",
                "Quantify financial benefits for investor presentations",
                "Benchmark against competition to highlight leadership"
            ]
        else:
            recommendations = [
                "Prepare transparent communication strategy for investors",
                "Develop clear remediation timeline with milestones",
                "Quantify resource requirements and expected outcomes"
            ]
    else:
        if impact == "positive":
            recommendations = [
                "Continue current successful strategies",
                "Share best practices across the organization",
                "Set more ambitious targets for next period"
            ]
        else:
            recommendations = [
                "Identify root causes of underperformance",
                "Develop an action plan with clear ownership",
                "Increase monitoring frequency"
            ]
    
    return recommendations

def story_satisfies_criteria(story, criteria):
    """Check if a story satisfies given filter criteria"""
    # Example criteria: {"categories": ["emissions"], "impact": "positive", "date_range": {"start": "2025-01-01", "end": "2025-12-31"}}
    
    if "categories" in criteria and criteria["categories"]:
        if story.get("category") not in criteria["categories"]:
            return False
    
    if "impact" in criteria and criteria["impact"]:
        if story.get("impact") != criteria["impact"]:
            return False
            
    if "date_range" in criteria and criteria["date_range"]:
        story_date = datetime.strptime(story.get("date", "2025-01-01"), "%Y-%m-%d")
        
        if "start" in criteria["date_range"] and criteria["date_range"]["start"]:
            start_date = datetime.strptime(criteria["date_range"]["start"], "%Y-%m-%d")
            if story_date < start_date:
                return False
                
        if "end" in criteria["date_range"] and criteria["date_range"]["end"]:
            end_date = datetime.strptime(criteria["date_range"]["end"], "%Y-%m-%d")
            if story_date > end_date:
                return False
    
    return True

def filter_stories(stories, criteria):
    """Filter stories based on criteria"""
    return [story for story in stories if story_satisfies_criteria(story, criteria)]

def generate_thematic_story_collection(metrics_data, theme):
    """Generate a collection of stories around a specific sustainability theme"""
    thematic_stories = []
    
    # Theme-specific metrics filtering
    theme_categories = {
        "climate_action": ["emissions", "energy"],
        "resource_efficiency": ["water", "waste", "energy"],
        "social_impact": ["social", "diversity"],
        "governance": ["governance", "compliance"],
        "innovation": ["innovation", "technology"]
    }
    
    categories = theme_categories.get(theme, ["emissions", "energy", "water", "waste", "social"])
    
    # Filter metrics by relevant categories
    relevant_metrics = [m for m in metrics_data if m.get("category") in categories]
    
    # Generate one story per category
    for category in set(m.get("category") for m in relevant_metrics):
        category_metrics = [m for m in relevant_metrics if m.get("category") == category]
        if category_metrics:
            story = generate_story_from_metrics(category_metrics, "general")
            thematic_stories.append(story)
    
    return {
        "theme": theme,
        "title": format_theme_title(theme),
        "stories": thematic_stories,
        "summary": generate_theme_summary(theme, thematic_stories)
    }

def format_theme_title(theme):
    """Format a theme identifier into a readable title"""
    theme_titles = {
        "climate_action": "Climate Action & Emissions Reduction",
        "resource_efficiency": "Resource Efficiency & Circular Economy",
        "social_impact": "Social Impact & Community Engagement",
        "governance": "Governance & Ethical Business Practices",
        "innovation": "Sustainability Innovation & Technology"
    }
    
    return theme_titles.get(theme, theme.replace("_", " ").title())

def generate_theme_summary(theme, stories):
    """Generate a summary of the thematic story collection"""
    theme_summaries = {
        "climate_action": "Analysis of our climate action initiatives and emissions reduction performance",
        "resource_efficiency": "Overview of resource efficiency measures and circular economy progress",
        "social_impact": "Examination of our social impact programs and community engagement",
        "governance": "Review of governance structures and ethical business practices",
        "innovation": "Exploration of sustainability innovations and technology implementation"
    }
    
    base_summary = theme_summaries.get(theme, f"Analysis of {theme.replace('_', ' ')} metrics and performance")
    
    # Count positive and negative stories
    positive_count = sum(1 for story in stories if story.get("impact") == "positive")
    negative_count = sum(1 for story in stories if story.get("impact") == "negative")
    
    if positive_count > negative_count:
        sentiment = "positive"
        trend_text = "showing overall improvements"
    elif negative_count > positive_count:
        sentiment = "concerning"
        trend_text = "indicating areas needing attention"
    else:
        sentiment = "mixed"
        trend_text = "with varied results across metrics"
    
def extract_percentage(text):
    """
    Extract percentage values from text
    
    Args:
        text: Text to extract percentages from
        
    Returns:
        First percentage found or None
    """
    import re
    
    # Look for percentages in text (e.g., 15%, 3.5%)
    percentage_pattern = r'(\d+\.?\d*)%'
    matches = re.findall(percentage_pattern, text)
    
    if matches:
        return matches[0] + '%'
    
    # If no explicit percentage is found, look for numbers with context
    number_pattern = r'(\d+\.?\d*)\s*(percent|percentage)'
    matches = re.findall(number_pattern, text.lower())
    
    if matches:
        return matches[0][0] + '%'
    
    return None

def generate_story_chart(story_id, chart_type='line'):
    """
    Generate chart data for a specific story
    
    Args:
        story_id: ID of the story to generate chart for
        chart_type: Type of chart to generate
        
    Returns:
        Chart data in format suitable for Plotly.js rendering
    """
    # Get all stories
    stories = get_enhanced_stories()
    story = None
    
    # Find the requested story
    for s in stories:
        if s.get('id') == int(story_id) if isinstance(story_id, str) and story_id.isdigit() else story_id:
            story = s
            break
    
    if not story:
        return {"error": "Story not found"}
    
    # Extract category for coloring
    category = story.get('category', 'emissions')
    
    # Define color schemes by category
    color_schemes = {
        'emissions': ['#1a237e', '#283593', '#3949ab', '#5c6bc0'],
        'water': ['#006064', '#00838f', '#0097a7', '#00acc1'],
        'energy': ['#e65100', '#ef6c00', '#f57c00', '#fb8c00'],
        'waste': ['#33691e', '#558b2f', '#689f38', '#7cb342'],
        'social': ['#4a148c', '#6a1b9a', '#7b1fa2', '#8e24aa']
    }
    
    # Get colors for this category
    colors = color_schemes.get(category, ['#3949ab', '#5c6bc0', '#7986cb'])
    
    # Generate time periods (months)
    months = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ]
    
    # Extract percentage from story for scale
    percentage = extract_percentage(story.get('content', ''))
    target_value = int(percentage.replace('%', '')) if percentage else 15
    
    # Create trend data based on story impact and category
    if story.get('impact') == 'positive':
        current_data = [target_value * 0.7, target_value * 0.8, target_value * 0.85, 
                       target_value * 0.9, target_value * 0.95, target_value]
    else:
        current_data = [target_value * 1.3, target_value * 1.2, target_value * 1.15, 
                       target_value * 1.10, target_value * 1.05, target_value]
    
    # Create comparison data
    benchmark_data = [target_value * 1.1, target_value * 1.08, target_value * 1.05, 
                     target_value * 1.03, target_value * 1.01, target_value * 0.99]
    
    # Previous period data
    previous_data = [target_value * 1.2, target_value * 1.15, target_value * 1.12, 
                    target_value * 1.1, target_value * 1.05, target_value * 1.02]
    
    # Generate chart data based on chart type
    chart_data = {}
    
    if chart_type == 'line' or chart_type == 'area':
        # Line chart data
        chart_data = {
            'type': 'line' if chart_type == 'line' else 'area',
            'data': {
                'labels': months[-6:],
                'datasets': [
                    {
                        'label': 'Current Period',
                        'data': current_data,
                        'borderColor': colors[0],
                        'backgroundColor': colors[0] + '20',
                        'fill': chart_type == 'area'
                    },
                    {
                        'label': 'Previous Period',
                        'data': previous_data,
                        'borderColor': colors[1],
                        'backgroundColor': colors[1] + '20',
                        'fill': chart_type == 'area'
                    },
                    {
                        'label': 'Industry Benchmark',
                        'data': benchmark_data,
                        'borderColor': colors[2],
                        'backgroundColor': colors[2] + '20',
                        'fill': chart_type == 'area',
                        'borderDash': [5, 5]
                    }
                ]
            },
            'options': {
                'title': story.get('title'),
                'category': category,
                'impact': story.get('impact'),
                'target': target_value,
                'annotations': [
                    {
                        'type': 'line',
                        'value': target_value,
                        'label': 'Target'
                    }
                ]
            }
        }
    elif chart_type == 'bar' or chart_type == 'column':
        # Bar chart data
        chart_data = {
            'type': chart_type,
            'data': {
                'labels': months[-6:],
                'datasets': [
                    {
                        'label': 'Current Period',
                        'data': current_data,
                        'backgroundColor': colors[0]
                    },
                    {
                        'label': 'Previous Period',
                        'data': previous_data,
                        'backgroundColor': colors[1]
                    },
                    {
                        'label': 'Industry Benchmark',
                        'data': benchmark_data,
                        'backgroundColor': colors[2]
                    }
                ]
            },
            'options': {
                'title': story.get('title'),
                'category': category,
                'impact': story.get('impact'),
                'target': target_value
            }
        }
    elif chart_type == 'pie' or chart_type == 'doughnut':
        # Create components that add up to the target value
        component_names = {
            'emissions': ['Scope 1', 'Scope 2', 'Scope 3'],
            'water': ['Process', 'Cooling', 'Domestic'],
            'energy': ['Electricity', 'Gas', 'Renewables'],
            'waste': ['Recycled', 'Landfill', 'Composted'],
            'social': ['Diversity', 'Training', 'Safety']
        }
        
        names = component_names.get(category, ['Component A', 'Component B', 'Component C'])
        
        # Calculate values that add up to target
        values = [
            target_value * 0.3,
            target_value * 0.45,
            target_value * 0.25
        ]
        
        chart_data = {
            'type': chart_type,
            'data': {
                'labels': names,
                'datasets': [
                    {
                        'data': values,
                        'backgroundColor': colors[0:3]
                    }
                ]
            },
            'options': {
                'title': story.get('title'),
                'category': category,
                'impact': story.get('impact'),
                'cutout': '50%' if chart_type == 'doughnut' else '0%'
            }
        }
    
    return chart_data

def register_routes(app):
    """
    Register Sustainability Storytelling routes with Flask app
    
    Args:
        app: Flask application
    """
    if not FLASK_AVAILABLE:
        logger.warning("Flask not available. Sustainability Storytelling routes will not be registered.")
        return False
    
    app.register_blueprint(storytelling_bp)
    
    # Register the view routes - redirect to the new endpoint for backward compatibility
    @app.route('/story-cards')
    def story_cards():
        """AI Storytelling Engine - Redirect to new storytelling endpoint for backward compatibility"""
        logger.info("Legacy sustainability stories route accessed - redirecting to new blueprint")
        audience = request.args.get('audience', 'all')
        category = request.args.get('category', 'all')
        
        # Redirect to the new blueprint route with parameters
        return redirect(url_for('storytelling.storytelling_hub', audience=audience, category=category))
    
    # Register the API endpoints
    @app.route('/api/storytelling')
    def api_storytelling():
        """API endpoint for AI storytelling generation with Gartner-inspired methodology"""
        audience = request.args.get('audience', 'all')
        category = request.args.get('category', 'all')
        format_type = request.args.get('format', 'json')
        
        stories = get_enhanced_stories(audience, category)
        
        if format_type == 'html':
            # Generate HTML story cards
            html_content = render_template(
                'partials/story_cards_content.html',
                stories=stories
            )
            return jsonify({
                'success': True,
                'html': html_content,
                'count': len(stories)
            })
        else:
            # Return JSON data
            return jsonify({
                'success': True,
                'stories': stories,
                'count': len(stories),
                'filters': {
                    'audience': audience,
                    'category': category
                }
            })
    
    # Register API endpoint for chart generation
    @app.route('/api/storytelling/chart', methods=['POST'])
    def api_storytelling_chart():
        """API endpoint for generating charts for storytelling"""
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Invalid request format'}), 400
            
        data = request.json
        story_id = data.get('story_id')
        chart_type = data.get('chart_type', 'line')
        
        if not story_id:
            return jsonify({'success': False, 'error': 'Missing story_id parameter'}), 400
            
        # Generate chart based on story data
        chart_data = generate_story_chart(story_id, chart_type)
        
        return jsonify({
            'success': True,
            'chart_data': chart_data
        })
    
    logger.info("Sustainability Storytelling routes registered successfully")
    return True