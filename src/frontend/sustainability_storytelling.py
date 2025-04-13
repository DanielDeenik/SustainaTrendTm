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

# Import AI connector for storytelling
try:
    from frontend.utils.ai_connector import get_generative_ai
except ImportError:
    # Define a fallback function when AI connector is not available
    def get_generative_ai(*args, **kwargs):
        return None

# Import document processing capabilities
try:
    from frontend.document_processor import DocumentProcessor
except ImportError:
    # Define a fallback DocumentProcessor when not available
    class DocumentProcessor:
        @staticmethod
        def extract_text(*args, **kwargs):
            return "Document text extraction unavailable"
        
        @staticmethod
        def analyze_document(*args, **kwargs):
            return {"error": "Document processing unavailable"}

# Configure logging
logger = logging.getLogger(__name__)

# Initialize document processor
document_processor = DocumentProcessor()

def get_enhanced_stories(audience: str = 'all', category: str = 'all') -> List[Dict[str, Any]]:
    """
    Get enhanced stories based on audience and category filters
    
    Args:
        audience: Target audience filter (executives, investors, employees, etc.)
        category: Category filter (emissions, water, diversity, etc.)
        
    Returns:
        List of story objects with metadata
    """
    try:
        # Get stories from database
        stories = get_data_driven_stories()
        
        # Filter by audience if specified
        if audience and audience != 'all':
            stories = [s for s in stories if s.get('audience', '').lower() == audience.lower()]
        
        # Filter by category if specified
        if category and category != 'all':
            stories = [s for s in stories if s.get('category', '').lower() == category.lower()]
        
        # Always return at least 3 stories for display
        if len(stories) < 3:
            additional_stories = get_lcm_generated_stories(3 - len(stories), audience, category)
            stories.extend(additional_stories)
        
        return stories
    except Exception as e:
        logger.error(f"Error in get_enhanced_stories: {str(e)}")
        # Return generated stories as fallback
        return get_lcm_generated_stories(5, audience, category)

def get_lcm_story(
    audience: str = 'all',
    category: str = 'all',
    prompt: Optional[str] = None,
    document_data: Optional[Dict[str, Any]] = None,
    metrics: Optional[List[Dict[str, Any]]] = None,
    story_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a single sustainability story using LCM
    
    Args:
        audience: Target audience (executives, investors, employees, etc.)
        category: Story category (emissions, water, diversity, etc.)
        prompt: Custom prompt or specific story requirements
        document_data: Additional data from uploaded document
        metrics: Optional list of specific metrics to include in the story
        story_id: Optional story ID for retrieving/regenerating a specific story
        
    Returns:
        Story object with all metadata and content
    """
    # Use provided ID or generate new one
    story_id = story_id or str(uuid.uuid4())
    
    try:
        # Build prompt for LCM
        system_message = """You are SustainaTrend™, an AI storytelling expert specializing in transforming sustainability data into compelling narratives. Create a detailed, engaging story that highlights key sustainability metrics and achievements. Follow these guidelines:
1. Use a professional, engaging tone appropriate for the specified audience
2. Include specific metrics and data points with realistic values
3. Structure the story with clear sections including introduction, key achievements, challenges, and future outlook
4. Focus on the specified sustainability category and include relevant metrics
5. Add quotes from fictional stakeholders to enhance credibility
6. Format using Markdown with headings, bullet points, and emphasis
7. Keep content authentic, ethical, and fact-based (no greenwashing)
8. Include specific industry best practices and realistic improvement areas
"""
        
        # Customize based on audience
        audience_guidance = {
            "executives": "Create a concise, strategic narrative focused on business impact, ROI, and competitive advantage. Use technical financial terms and high-level KPIs relevant for C-suite decision-making.",
            "investors": "Focus on financial materiality, risk management, and long-term value creation. Include sector benchmarking and investment-relevant metrics with quantitative data.",
            "employees": "Create an engaging, purpose-driven narrative connecting sustainability to company culture. Focus on personal impact, pride points, and ways employees contribute.",
            "regulators": "Emphasize compliance details, measurement methodologies, and alignment with specific frameworks (CSRD, SFDR, ISSB). Use formal, precise language with technical details.",
            "customers": "Create an accessible, impact-focused narrative highlighting product sustainability and customer benefits. Use conversational language with emotional connection points.",
            "general-public": "Create an accessible, impact-focused narrative with clear explanations of sustainability concepts. Use storytelling techniques and visual elements to engage a broad audience."
        }
        
        # Customize based on category
        category_guidance = {
            "emissions": "Focus on carbon emissions reduction, climate action, and energy efficiency with specific GHG metrics (Scope 1, 2, 3), targets, and reduction initiatives.",
            "water": "Focus on water stewardship, watershed protection, and water efficiency with metrics on withdrawal, consumption, recycling, and water stress areas.",
            "waste": "Focus on waste management, circular economy principles, and materials efficiency with metrics on waste reduction, recycling rates, and product lifecycle.",
            "biodiversity": "Focus on nature protection, ecosystem restoration, and biodiversity impact with metrics on land use, habitat restoration, and species protection.",
            "social": "Focus on social impact, community engagement, and workforce diversity with metrics on DEI progress, community investment, and social value creation.",
            "governance": "Focus on ethical business practices, board diversity, and sustainability governance with metrics on ESG oversight, ethical standards, and transparency."
        }
        
        # Build user prompt based on parameters
        user_message = f"Please create a sustainability story for audience: {audience} with focus on category: {category}."
        
        # Add specific audience guidance
        if audience != 'all' and audience in audience_guidance:
            user_message += f"\n\nAudience guidance: {audience_guidance[audience]}"
        
        # Add specific category guidance
        if category != 'all' and category in category_guidance:
            user_message += f"\n\nCategory guidance: {category_guidance[category]}"
        
        # Add custom prompt if provided
        if prompt:
            user_message += f"\n\nAdditional requirements: {prompt}"
        
        # Add document insights if available
        if document_data:
            doc_summary = f"Document insights:\n- Title: {document_data.get('title', 'Sustainability Report')}\n"
            if 'metrics' in document_data:
                doc_summary += "- Key metrics found:\n"
                for metric in document_data['metrics'][:5]:  # Include up to 5 metrics
                    doc_summary += f"  * {metric['name']}: {metric['value']} {metric.get('unit', '')}\n"
            if 'frameworks' in document_data:
                doc_summary += "- Frameworks mentioned: " + ", ".join(document_data['frameworks']) + "\n"
            user_message += f"\n\n{doc_summary}"
        
        # Add selected metrics if provided
        if metrics and len(metrics) > 0:
            metrics_summary = "Selected metrics to include in the story:\n"
            for metric in metrics:
                metrics_summary += f"- {metric['name']}: {metric['value']} {metric.get('unit', '')}\n"
            user_message += f"\n\n{metrics_summary}\nPlease feature these specific metrics prominently in the sustainability story."
        
        # Get response from AI
        ai = get_generative_ai()
        response = ai.generate_content(prompt=user_message, system_prompt=system_message, max_tokens=1500)
        
        # Process response
        if 'error' in response:
            raise Exception(f"AI Error: {response['error']}")
            
        story_content = response.get('text', '').strip()
        
        # Generate story metadata
        created_at = datetime.now().isoformat()
        
        # Determine story title
        title_parts = story_content.split('\n', 1)
        if title_parts[0].startswith('# '):
            title = title_parts[0][2:].strip()
            content = title_parts[1] if len(title_parts) > 1 else ""
        else:
            # Generate a title based on content
            title = generate_story_title(category, audience)
            content = story_content
        
        # Use provided metrics if available, otherwise generate example metrics
        story_metrics = metrics if metrics and len(metrics) > 0 else get_story_metrics(category)
        
        # Create and return the story object
        return {
            "id": story_id,
            "title": title,
            "content": content,
            "audience": audience,
            "category": category,
            "created_at": created_at,
            "metrics": story_metrics,
            "tags": generate_story_tags(category, audience)
        }
    except Exception as e:
        logger.error(f"Error in get_lcm_story: {str(e)}")
        # Return error story with error message for debugging
        return {
            "id": story_id,
            "title": f"Story Generation Error ({category})",
            "content": f"There was an error generating your sustainability story. Please try again.\n\nError details: {str(e)}",
            "audience": audience,
            "category": category,
            "created_at": datetime.now().isoformat(),
            "metrics": [],
            "tags": [category, "error"]
        }

def get_lcm_generated_stories(count: int = 3, audience: str = 'all', category: str = 'all') -> List[Dict[str, Any]]:
    """
    Generate multiple sustainability stories using LCM
    
    Args:
        count: Number of stories to generate
        audience: Target audience filter
        category: Category filter
        
    Returns:
        List of story objects
    """
    stories = []
    
    # Map of categories to use if 'all' is specified
    all_categories = ['emissions', 'water', 'waste', 'biodiversity', 'social', 'governance']
    
    # Map of audiences to use if 'all' is specified
    all_audiences = ['executives', 'investors', 'employees', 'regulators', 'customers']
    
    # Generate multiple stories with different categories or audiences
    for i in range(count):
        try:
            # Select a category - either the specified one or randomly from the list
            story_category = category
            if category == 'all':
                story_category = random.choice(all_categories)
            
            # Select an audience - either the specified one or randomly from the list
            story_audience = audience
            if audience == 'all':
                story_audience = random.choice(all_audiences)
            
            # Generate a story with specified parameters
            story = get_lcm_story(story_audience, story_category)
            
            # Add to the list
            stories.append(story)
        except Exception as e:
            logger.error(f"Error generating story {i+1}: {str(e)}")
    
    return stories

def get_data_driven_stories() -> List[Dict[str, Any]]:
    """Get data-driven sustainability stories from the database"""
    try:
        # Return an empty list initially
        return []
    except Exception as e:
        logger.error(f"Error in get_data_driven_stories: {str(e)}")
        return []

def generate_story_title(category: str, audience: str) -> str:
    """Generate a title for a story based on category and audience"""
    # Base title templates
    title_templates = {
        "emissions": [
            "Carbon Progress Report: Advancing Toward Net Zero",
            "Climate Action Journey: Our Emissions Reduction Story",
            "Decarbonization in Action: Our Climate Strategy"
        ],
        "water": [
            "Water Stewardship: Preserving Our Most Precious Resource",
            "Blue Future: Our Water Conservation Strategy",
            "Watershed Moments: Progress in Water Management"
        ],
        "waste": [
            "Circular Economy in Practice: Our Waste Reduction Story",
            "Zero Waste Journey: Transforming Our Material Footprint",
            "Waste Not, Want Not: Our Circular Economy Achievements"
        ],
        "biodiversity": [
            "Nature Positive: Our Biodiversity Protection Strategy",
            "Restoring Balance: Our Biodiversity Commitments",
            "Nature's Guardians: Our Biodiversity Impact Story"
        ],
        "social": [
            "People First: Our Social Impact Journey",
            "Building Community: Our Social Responsibility Story",
            "Human Capital: Investing in Our Greatest Asset"
        ],
        "governance": [
            "Governance Excellence: Our ESG Leadership Approach",
            "Responsible Leadership: Our Governance Framework",
            "Transparency in Action: Our Governance Structure"
        ]
    }
    
    # Audience-specific modifiers
    audience_modifiers = {
        "executives": "Strategic Overview",
        "investors": "Value Creation Assessment",
        "employees": "Our Collective Impact",
        "regulators": "Compliance & Performance",
        "customers": "Our Commitment to You",
        "general-public": "Making a Difference"
    }
    
    # Use category templates, or default if category not found
    if category in title_templates:
        title = random.choice(title_templates[category])
    else:
        title = random.choice([
            "Sustainability in Action: Our ESG Journey",
            "Building a Sustainable Future: Our Progress",
            "Sustainability Milestones: Our Path Forward"
        ])
    
    # Add audience modifier if applicable
    if audience in audience_modifiers and random.random() > 0.5:
        title = f"{title}: {audience_modifiers[audience]}"
    
    return title

def generate_story_tags(category: str, audience: str) -> List[str]:
    """Generate tags for a story based on category and audience"""
    tags = [category]
    
    # Add audience tag
    if audience != 'all':
        tags.append(audience)
    
    # Add related tags based on category
    category_tags = {
        "emissions": ["climate", "carbon", "energy"],
        "water": ["conservation", "water-risk", "resources"],
        "waste": ["circular", "recycling", "materials"],
        "biodiversity": ["nature", "conservation", "habitat"],
        "social": ["diversity", "community", "equity"],
        "governance": ["ethics", "transparency", "leadership"]
    }
    
    # Add 1-2 related tags from the category
    if category in category_tags:
        related_tags = random.sample(category_tags[category], min(2, len(category_tags[category])))
        tags.extend(related_tags)
    
    # Add a general sustainability tag
    general_tags = ["sustainability", "ESG", "impact", "strategy", "performance"]
    tags.append(random.choice(general_tags))
    
    return tags

def get_story_metrics(category: str) -> List[Dict[str, Any]]:
    """Generate example metrics for a story based on category"""
    metrics = []
    
    if category == 'emissions':
        metrics = [
            {"name": "Scope 1 Emissions", "value": random.randint(1000, 5000), "unit": "tCO2e", "change": random.uniform(-15, -2)},
            {"name": "Scope 2 Emissions", "value": random.randint(2000, 8000), "unit": "tCO2e", "change": random.uniform(-12, -1)},
            {"name": "Renewable Energy", "value": random.randint(20, 80), "unit": "%", "change": random.uniform(5, 15)}
        ]
    elif category == 'water':
        metrics = [
            {"name": "Water Withdrawal", "value": round(random.uniform(500, 2000), 1), "unit": "ML", "change": random.uniform(-10, -1)},
            {"name": "Water Recycled", "value": random.randint(15, 50), "unit": "%", "change": random.uniform(2, 8)},
            {"name": "Water Intensity", "value": round(random.uniform(0.5, 5), 2), "unit": "m³/unit", "change": random.uniform(-12, -3)}
        ]
    elif category == 'waste':
        metrics = [
            {"name": "Waste Generated", "value": random.randint(500, 3000), "unit": "tonnes", "change": random.uniform(-12, -3)},
            {"name": "Recycling Rate", "value": random.randint(30, 75), "unit": "%", "change": random.uniform(3, 12)},
            {"name": "Landfill Diversion", "value": random.randint(50, 90), "unit": "%", "change": random.uniform(4, 10)}
        ]
    elif category == 'biodiversity':
        metrics = [
            {"name": "Land Restored", "value": random.randint(5, 100), "unit": "hectares", "change": random.uniform(10, 30)},
            {"name": "Species Protected", "value": random.randint(3, 25), "unit": "count", "change": random.uniform(1, 5)},
            {"name": "Natural Capital Value", "value": random.randint(1, 10), "unit": "$ million", "change": random.uniform(3, 15)}
        ]
    elif category == 'social':
        metrics = [
            {"name": "Gender Diversity", "value": random.randint(35, 50), "unit": "% women", "change": random.uniform(2, 8)},
            {"name": "Community Investment", "value": round(random.uniform(0.2, 5), 1), "unit": "$ million", "change": random.uniform(5, 20)},
            {"name": "Employee Satisfaction", "value": random.randint(70, 95), "unit": "%", "change": random.uniform(1, 5)}
        ]
    elif category == 'governance':
        metrics = [
            {"name": "Board Diversity", "value": random.randint(30, 50), "unit": "%", "change": random.uniform(5, 15)},
            {"name": "ESG Training", "value": random.randint(80, 98), "unit": "% completed", "change": random.uniform(2, 10)},
            {"name": "Supplier Code Compliance", "value": random.randint(85, 99), "unit": "%", "change": random.uniform(1, 8)}
        ]
    else:
        # Default metrics for any other category
        metrics = [
            {"name": "Sustainability Score", "value": random.randint(70, 95), "unit": "/100", "change": random.uniform(3, 10)},
            {"name": "ESG Rating", "value": random.choice(["A", "AA", "AAA"]), "unit": "", "change": 1},
            {"name": "Sustainability ROI", "value": random.randint(10, 25), "unit": "%", "change": random.uniform(1, 8)}
        ]
    
    return metrics

def generate_chart_data(category: str, period: str = 'quarterly', chart_type: str = 'line') -> Dict[str, Any]:
    """
    Generate chart data for storytelling visualizations
    
    Args:
        category: Category of data (emissions, water, social, etc.)
        period: Time period (quarterly, annual, monthly)
        chart_type: Type of chart (line, bar, pie, etc.)
        
    Returns:
        Chart data configuration
    """
    # Set up time periods based on specified period
    if period == 'quarterly':
        labels = ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024']
    elif period == 'annual':
        labels = ['2020', '2021', '2022', '2023', '2024']
    elif period == 'monthly':
        # Get last 6 months
        today = datetime.now()
        labels = []
        for i in range(5, -1, -1):
            month = today.month - i
            year = today.year
            if month <= 0:
                month += 12
                year -= 1
            month_name = datetime(year, month, 1).strftime('%b %Y')
            labels.append(month_name)
    else:
        labels = ['Period 1', 'Period 2', 'Period 3', 'Period 4']
    
    # Generate chart data based on category and chart type
    if chart_type == 'line':
        # Generate line chart data
        if category == 'emissions':
            return {
                'type': 'line',
                'data': {
                    'labels': labels,
                    'datasets': [
                        {
                            'label': 'Scope 1 Emissions (tCO2e)',
                            'data': generate_trend_data(5000, 4000, len(labels), trend='decreasing'),
                            'borderColor': 'rgb(255, 99, 132)',
                            'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                            'tension': 0.1
                        },
                        {
                            'label': 'Scope 2 Emissions (tCO2e)',
                            'data': generate_trend_data(8000, 6000, len(labels), trend='decreasing'),
                            'borderColor': 'rgb(54, 162, 235)',
                            'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                            'tension': 0.1
                        }
                    ]
                }
            }
        elif category == 'water':
            return {
                'type': 'line',
                'data': {
                    'labels': labels,
                    'datasets': [
                        {
                            'label': 'Water Withdrawal (ML)',
                            'data': generate_trend_data(2000, 1800, len(labels), trend='decreasing'),
                            'borderColor': 'rgb(54, 162, 235)',
                            'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                            'tension': 0.1
                        },
                        {
                            'label': 'Water Recycled (%)',
                            'data': generate_trend_data(20, 40, len(labels), trend='increasing'),
                            'borderColor': 'rgb(75, 192, 192)',
                            'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                            'tension': 0.1
                        }
                    ]
                }
            }
        else:
            # Default chart
            return {
                'type': 'line',
                'data': {
                    'labels': labels,
                    'datasets': [
                        {
                            'label': 'Sustainability Metric',
                            'data': generate_trend_data(50, 80, len(labels), trend='increasing'),
                            'borderColor': 'rgb(75, 192, 192)',
                            'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                            'tension': 0.1
                        }
                    ]
                }
            }
    elif chart_type == 'bar':
        # Generate bar chart data
        if category == 'waste':
            return {
                'type': 'bar',
                'data': {
                    'labels': labels,
                    'datasets': [
                        {
                            'label': 'Waste Generated (tonnes)',
                            'data': generate_trend_data(3000, 2400, len(labels), trend='decreasing'),
                            'backgroundColor': 'rgba(255, 99, 132, 0.5)'
                        },
                        {
                            'label': 'Recycled (%)',
                            'data': generate_trend_data(40, 70, len(labels), trend='increasing'),
                            'backgroundColor': 'rgba(75, 192, 192, 0.5)'
                        }
                    ]
                }
            }
        elif category == 'social':
            return {
                'type': 'bar',
                'data': {
                    'labels': ['Board', 'Senior Management', 'Middle Management', 'Staff'],
                    'datasets': [
                        {
                            'label': 'Gender Diversity (% Women)',
                            'data': [35, 38, 45, 48],
                            'backgroundColor': 'rgba(153, 102, 255, 0.5)'
                        },
                        {
                            'label': 'Target',
                            'data': [50, 50, 50, 50],
                            'type': 'line',
                            'borderColor': 'rgb(255, 99, 132)',
                            'borderWidth': 2,
                            'fill': False
                        }
                    ]
                }
            }
        else:
            # Default bar chart
            return {
                'type': 'bar',
                'data': {
                    'labels': labels,
                    'datasets': [
                        {
                            'label': 'Sustainability Metric',
                            'data': generate_trend_data(30, 80, len(labels), trend='increasing'),
                            'backgroundColor': [
                                'rgba(255, 99, 132, 0.5)',
                                'rgba(54, 162, 235, 0.5)',
                                'rgba(255, 206, 86, 0.5)',
                                'rgba(75, 192, 192, 0.5)',
                                'rgba(153, 102, 255, 0.5)'
                            ]
                        }
                    ]
                }
            }
    elif chart_type == 'pie':
        # Generate pie chart data
        if category == 'emissions':
            return {
                'type': 'pie',
                'data': {
                    'labels': ['Scope 1', 'Scope 2', 'Scope 3'],
                    'datasets': [
                        {
                            'data': [15, 25, 60],
                            'backgroundColor': [
                                'rgba(255, 99, 132, 0.5)',
                                'rgba(54, 162, 235, 0.5)',
                                'rgba(255, 206, 86, 0.5)'
                            ]
                        }
                    ]
                }
            }
        elif category == 'governance':
            return {
                'type': 'pie',
                'data': {
                    'labels': ['Environmental', 'Social', 'Governance', 'Economic'],
                    'datasets': [
                        {
                            'data': [30, 25, 20, 25],
                            'backgroundColor': [
                                'rgba(75, 192, 192, 0.5)',
                                'rgba(153, 102, 255, 0.5)',
                                'rgba(255, 159, 64, 0.5)',
                                'rgba(201, 203, 207, 0.5)'
                            ]
                        }
                    ]
                }
            }
        else:
            # Default pie chart
            return {
                'type': 'pie',
                'data': {
                    'labels': ['Category 1', 'Category 2', 'Category 3', 'Category 4'],
                    'datasets': [
                        {
                            'data': [25, 30, 15, 30],
                            'backgroundColor': [
                                'rgba(255, 99, 132, 0.5)',
                                'rgba(54, 162, 235, 0.5)',
                                'rgba(255, 206, 86, 0.5)',
                                'rgba(75, 192, 192, 0.5)'
                            ]
                        }
                    ]
                }
            }
    else:
        # Default radar chart for unknown chart types
        return {
            'type': 'radar',
            'data': {
                'labels': ['Environmental', 'Social', 'Governance', 'Economic', 'Innovation'],
                'datasets': [
                    {
                        'label': 'Current Performance',
                        'data': [65, 75, 70, 80, 60],
                        'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                        'borderColor': 'rgb(54, 162, 235)',
                        'pointBackgroundColor': 'rgb(54, 162, 235)'
                    },
                    {
                        'label': 'Target',
                        'data': [90, 85, 80, 88, 82],
                        'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                        'borderColor': 'rgb(255, 99, 132)',
                        'pointBackgroundColor': 'rgb(255, 99, 132)'
                    }
                ]
            }
        }

def register_routes(app):
    """
    Register storytelling routes with Flask app (called from direct_app.py)
    
    Args:
        app: Flask application instance
    """
    # Check if we're in direct mode by looking for specific attribute
    if hasattr(app, 'direct_mode') and app.direct_mode:
        # Import the stories blueprint from routes module and register it
        try:
            from frontend.routes.stories import register_blueprint
            register_blueprint(app)
            logger.info("Storytelling routes registered via blueprint (direct mode)")
        except ImportError as e:
            logger.error(f"Could not register storytelling routes: {str(e)}")
    else:
        logger.info("Storytelling routes NOT registered - use blueprint registration instead")

def generate_trend_data(start: float, end: float, points: int, trend: str = 'increasing') -> List[float]:
    """
    Generate trend data for charts with random variations
    
    Args:
        start: Starting value
        end: Ending value
        points: Number of data points
        trend: Direction of trend ('increasing', 'decreasing', 'stable')
        
    Returns:
        List of data points
    """
    if points <= 1:
        return [start]
    
    # Calculate step size
    step = (end - start) / (points - 1)
    
    # Generate base trend
    data = []
    for i in range(points):
        base_value = start + step * i
        
        # Add random variation (±10%)
        variation = base_value * random.uniform(-0.1, 0.1)
        value = base_value + variation
        
        # Ensure value remains positive
        value = max(0, value)
        
        # Round to appropriate precision
        if value >= 100:
            value = round(value)
        else:
            value = round(value, 1)
        
        data.append(value)
    
    # Ensure the last value is close to the end value (±5%)
    if len(data) > 0 and data[-1] != end:
        data[-1] = end * random.uniform(0.95, 1.05)
        data[-1] = round(data[-1]) if data[-1] >= 100 else round(data[-1], 1)
    
    return data