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
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

def get_mock_stories():
    """Generate mock sustainability stories for development purposes"""
    stories = [
        {
            "id": 1,
            "title": "Carbon Emissions Reduction Success",
            "content": "Our organization achieved a 15% reduction in carbon emissions over the past quarter through energy efficiency initiatives and renewable energy adoption.",
            "category": "emissions",
            "date": "2025-03-01",
            "author": "Sustainability Team",
            "impact": "positive"
        },
        {
            "id": 2,
            "title": "Water Conservation Initiative Results",
            "content": "The water conservation program implemented last year has resulted in a 20% decrease in water usage across all facilities.",
            "category": "water",
            "date": "2025-02-15",
            "author": "Facilities Management",
            "impact": "positive"
        },
        {
            "id": 3,
            "title": "Energy Usage Alert",
            "content": "Energy consumption has increased by 8% in the manufacturing division. Investigation and mitigation measures are being implemented.",
            "category": "energy",
            "date": "2025-03-05",
            "author": "Operations Team",
            "impact": "negative"
        },
        {
            "id": 4,
            "title": "Waste Reduction Program Update",
            "content": "The zero-waste initiative has achieved a 30% reduction in landfill waste through improved recycling and composting programs.",
            "category": "waste",
            "date": "2025-02-28",
            "author": "Waste Management Team",
            "impact": "positive"
        },
        {
            "id": 5,
            "title": "Diversity and Inclusion Metrics",
            "content": "Workforce diversity metrics show a 10% increase in representation across all departments following the implementation of our inclusive hiring practices.",
            "category": "social",
            "date": "2025-03-10",
            "author": "HR Department",
            "impact": "positive"
        }
    ]
    return stories

def get_enhanced_stories(audience='all', category='all'):
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
        
    Returns:
        List of enhanced story dictionaries
    """
    logger.info(f"Generating enhanced stories for audience: {audience}, category: {category}")
    
    # Base stories to enhance
    base_stories = get_mock_stories()
    enhanced_stories = []
    
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
    return enhanced_stories

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
    
    return f"{base_summary}, with {sentiment} trends {trend_text}."