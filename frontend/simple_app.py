"""
Simple Flask Application for SustainaTrend™ Intelligence Platform

This file provides a minimal implementation to demonstrate the
storytelling API and chart recommendation functionality.
"""

import logging
import os
import sys
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

from flask import Flask, render_template, jsonify, request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)

# Set up template directory
app.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
app.static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# -------------------------------------------------------------------------
# Data services
# -------------------------------------------------------------------------

def get_sustainability_metrics():
    """Get sustainability metrics data"""
    metrics = []
    categories = ["Carbon Emissions", "Water Usage", "Energy Consumption", "Waste Management"]
    
    for i, category in enumerate(categories):
        # Generate time series data
        time_series = []
        base_value = random.uniform(80, 120)
        trend = random.choice(["improving", "stable", "worsening"])
        
        for month in range(12):
            date = (datetime.now() - timedelta(days=30 * (11 - month))).strftime("%Y-%m")
            
            # Adjust value based on trend
            if trend == "improving":
                factor = 0.95 ** month
            elif trend == "worsening":
                factor = 1.05 ** month
            else:
                factor = 1
            
            value = base_value * factor
            
            # Add noise
            noise = random.uniform(-5, 5)
            value = max(0, value + noise)
            
            time_series.append({
                "date": date,
                "value": round(value, 2)
            })
        
        metrics.append({
            "id": f"metric_{i+1}",
            "name": category,
            "category": category.split()[0],
            "description": f"Tracks {category.lower()} across all operations",
            "time_series": time_series,
            "latest_value": time_series[-1]["value"],
            "target": round(base_value * 0.8, 2),
            "status": "active"
        })
    
    return metrics

def get_trends():
    """Get sustainability trends data"""
    trends = []
    categories = ["Climate Transition", "Circular Economy", "Social Impact", "ESG Reporting"]
    titles = [
        "Net Zero Commitments Accelerate",
        "Carbon Pricing Adoption Growth",
        "Plastic Reduction Strategies",
        "Human Rights Due Diligence",
        "CSRD Implementation Timeline"
    ]
    
    for i, title in enumerate(titles):
        category = categories[i % len(categories)]
        
        trends.append({
            "id": f"trend_{i+1}",
            "title": title,
            "category": category,
            "description": f"Analysis of {title.lower()} across the industry",
            "virality_score": round(random.uniform(30, 95), 1),
            "momentum": random.choice(["rising", "stable", "falling"]),
            "impact_level": random.choice(["high", "medium", "low"]),
            "timeframe": random.choice(["short-term", "medium-term", "long-term"]),
            "created_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
        })
    
    return trends

def recommend_chart(metric, data, audience="board", narrative_focus="performance_analysis"):
    """
    Recommend the best chart type based on data characteristics, audience, and narrative focus
    
    Args:
        metric: The metric being visualized
        data: The dataset for visualization
        audience: Target audience (board, sustainability_team, investors)
        narrative_focus: Focus of the narrative
        
    Returns:
        Chart recommendation
    """
    # Chart type constants
    LINE_CHART = "line"
    BAR_CHART = "bar"
    PIE_CHART = "pie"
    GAUGE_CHART = "gauge"
    
    # Audience preferences
    audience_preferences = {
        "board": {
            "preferred": [GAUGE_CHART, PIE_CHART],
            "description": "Board members prefer high-level visuals showing status and progress"
        },
        "sustainability_team": {
            "preferred": [LINE_CHART, BAR_CHART],
            "description": "Sustainability teams need detailed visuals that show patterns and causality"
        },
        "investors": {
            "preferred": [LINE_CHART, BAR_CHART],
            "description": "Investors need visuals that clearly show performance and comparison to benchmarks"
        }
    }
    
    # Focus preferences
    focus_preferences = {
        "performance_analysis": {
            "preferred": [LINE_CHART, BAR_CHART, GAUGE_CHART],
            "description": "Performance analysis focuses on trends, comparisons, and status"
        },
        "risk_assessment": {
            "preferred": [GAUGE_CHART, PIE_CHART],
            "description": "Risk assessment visualizes threats, vulnerabilities, and impact levels"
        },
        "csrd_esg_compliance": {
            "preferred": [BAR_CHART, PIE_CHART],
            "description": "CSRD/ESG compliance shows regulatory status, gaps, and coverage"
        }
    }
    
    # Normalize inputs
    audience = audience.lower()
    if audience == "sustainability team":
        audience = "sustainability_team"
    
    narrative_focus = narrative_focus.lower()
    if "performance" in narrative_focus:
        narrative_focus = "performance_analysis"
    elif "risk" in narrative_focus:
        narrative_focus = "risk_assessment"
    elif "compliance" in narrative_focus or "esg" in narrative_focus:
        narrative_focus = "csrd_esg_compliance"
    
    # Check for time series data
    has_time_dimension = False
    if data and len(data) > 0:
        if "date" in data[0] or "time" in data[0] or "year" in data[0]:
            has_time_dimension = True
    
    # Select chart type
    if has_time_dimension:
        chart_type = LINE_CHART
        reason = "Time series data is best shown with a line chart"
    else:
        # Default to bar chart
        chart_type = BAR_CHART
        reason = "Default chart type for non-time series data"
    
    # Override based on audience preferences
    if audience in audience_preferences:
        preferred = audience_preferences[audience]["preferred"]
        if preferred and preferred[0]:
            if has_time_dimension and LINE_CHART in preferred:
                chart_type = LINE_CHART
                reason = f"Time series data optimized for {audience} audience"
            else:
                chart_type = preferred[0]
                reason = f"Preferred chart type for {audience} audience"
    
    # Create sample config
    config = {
        "type": chart_type,
        "title": f"{metric} Analysis",
        "data": data[:10],  # Limit to 10 data points
        "options": {}
    }
    
    if chart_type == LINE_CHART:
        config["options"] = {
            "xAxis": {"type": "category"},
            "yAxis": {"type": "value"},
            "series": [{"type": "line", "smooth": True}]
        }
    elif chart_type == BAR_CHART:
        config["options"] = {
            "xAxis": {"type": "category"},
            "yAxis": {"type": "value"},
            "series": [{"type": "bar"}]
        }
    elif chart_type == PIE_CHART:
        config["options"] = {
            "series": [{"type": "pie", "radius": "70%"}]
        }
    elif chart_type == GAUGE_CHART:
        config["options"] = {
            "series": [{
                "type": "gauge",
                "startAngle": 180,
                "endAngle": 0,
                "min": 0,
                "max": 100
            }]
        }
    
    return {
        "chart_type": chart_type,
        "explanation": reason,
        "audience_notes": audience_preferences.get(audience, {}).get("description", ""),
        "focus_notes": focus_preferences.get(narrative_focus, {}).get("description", ""),
        "sample_config": config
    }

def create_story_card(metric, audience, narrative_focus, time_period):
    """
    Create a data-driven story card based on the provided parameters
    
    Args:
        metric: Target metric for storytelling
        audience: Target stakeholder
        narrative_focus: Focus type
        time_period: Timeframe for analysis
        
    Returns:
        Story card as a dictionary
    """
    # Get metrics data
    metrics = get_sustainability_metrics()
    
    # Get relevant metrics
    relevant_metrics = []
    for m in metrics:
        if metric.lower() in m.get("name", "").lower():
            relevant_metrics = m.get("time_series", [])
            break
    
    if not relevant_metrics and metrics:
        relevant_metrics = metrics[0].get("time_series", [])
    
    # Get chart recommendation
    chart = recommend_chart(metric, relevant_metrics, audience, narrative_focus)
    
    # Generate headline based on audience and focus
    if audience.lower() == "board":
        if narrative_focus.lower() == "risk assessment":
            headline = f"Risk Alert: {metric} Exposure Requires Board Attention"
        else:
            headline = f"{metric} Performance Shows Strategic Sustainability Impact"
    elif audience.lower() == "sustainability team":
        headline = f"{metric} Analysis: Key Drivers and Improvement Opportunities"
    else:  # investors
        headline = f"{metric} Performance Against Sector Benchmarks and Targets"
    
    # Generate narrative content
    narrative = f"Our {metric} data shows positive momentum across the organization in {time_period}. This demonstrates alignment with our strategic sustainability goals and indicates effective implementation of our initiatives. Key drivers include operational efficiency improvements and targeted investments in sustainable technologies."
    
    # Generate context points
    context_points = [
        f"Performance on {metric} directly impacts our ESG ratings and sustainability rankings",
        "Industry benchmarks show leaders achieve 30-40% better performance",
        "Regulatory requirements are increasing in key markets"
    ]
    
    # Generate recommended actions
    if audience.lower() == "board":
        actions = [
            f"Review strategic targets for {metric} and ensure alignment with corporate strategy",
            f"Allocate additional resources to successful sustainability initiatives",
            f"Consider {metric} performance in executive compensation evaluations"
        ]
    elif audience.lower() == "sustainability team":
        actions = [
            f"Implement performance improvement plan for underperforming sites",
            f"Document and share best practices from high-performing operations",
            f"Enhance data collection and monitoring for {metric}"
        ]
    else:  # investors
        actions = [
            f"Consider {metric} performance trajectory in investment decisions",
            "Evaluate company's performance against sector leaders and peers",
            "Monitor quarterly updates for sustained improvement"
        ]
    
    # Create story card
    story_card = {
        "id": str(random.randint(1000, 9999)),
        "created_at": datetime.now().isoformat(),
        "metric": metric,
        "time_period": time_period,
        "audience": audience,
        "narrative_focus": narrative_focus,
        "headline": headline,
        "narrative": narrative,
        "chart": chart,
        "context_points": context_points,
        "recommended_actions": actions,
        "status": "generated"
    }
    
    return story_card

# -------------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------------

@app.route('/')
def home():
    """Home page"""
    return render_template("index.html", title="SustainaTrend™ Intelligence Platform")

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    metrics = get_sustainability_metrics()
    return render_template("dashboard.html", metrics=metrics)

@app.route('/trend-analysis')
def trend_analysis():
    """Trend analysis page"""
    trends = get_trends()
    return render_template("trend_analysis.html", trends=trends)

@app.route('/api/metrics')
def api_metrics():
    """API endpoint for metrics data"""
    metrics = get_sustainability_metrics()
    return jsonify({"metrics": metrics})

@app.route('/api/trends')
def api_trends():
    """API endpoint for trends data"""
    trends = get_trends()
    return jsonify({"trends": trends})

@app.route('/api/storytelling', methods=['POST'])
def api_storytelling():
    """
    API endpoint for AI storytelling generation with Gartner-inspired methodology
    
    Request parameters:
    - metric: Target metric for storytelling (e.g., 'Carbon Emissions')
    - time_period: Timeframe for analysis (e.g., 'Last Quarter')
    - narrative_focus: Focus type ('Performance Analysis', 'Risk Assessment', 'CSRD/ESG Compliance')
    - audience: Target stakeholder ('Board', 'Sustainability Team', 'Investors')
    """
    # Get request data
    data = request.json or {}
    
    # Get parameters for storytelling
    metric = data.get('metric', 'Carbon Emissions')
    time_period = data.get('time_period', 'Last Quarter')
    narrative_focus = data.get('narrative_focus', 'Performance Analysis')
    audience = data.get('audience', 'Board')
    
    # Create story card
    story_card = create_story_card(metric, audience, narrative_focus, time_period)
    
    return jsonify(story_card)

@app.route('/api/chart-recommendation', methods=['POST'])
def api_chart_recommendation():
    """
    API endpoint for AI chart recommendation
    
    Request parameters:
    - metric: Target metric (e.g., 'Carbon Emissions')
    - audience: Target audience ('Board', 'Sustainability Team', 'Investors')
    - narrative_focus: Focus type ('Performance Analysis', 'Risk Assessment', 'CSRD/ESG Compliance')
    """
    # Get request data
    data = request.json or {}
    
    # Get parameters
    metric = data.get('metric', 'Carbon Emissions')
    audience = data.get('audience', 'Board')
    narrative_focus = data.get('narrative_focus', 'Performance Analysis')
    
    # Get metrics data
    metrics = get_sustainability_metrics()
    
    # Get relevant metrics
    relevant_metrics = []
    for m in metrics:
        if metric.lower() in m.get("name", "").lower():
            relevant_metrics = m.get("time_series", [])
            break
    
    if not relevant_metrics and metrics:
        relevant_metrics = metrics[0].get("time_series", [])
    
    # Get chart recommendation
    chart = recommend_chart(metric, relevant_metrics, audience, narrative_focus)
    
    return jsonify(chart)

@app.route('/debug')
def debug_route():
    """Debug route to check registered routes"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            "endpoint": rule.endpoint,
            "methods": [m for m in rule.methods if m not in ["HEAD", "OPTIONS"]],
            "path": str(rule)
        })
    
    system_info = {
        "python_version": sys.version,
        "platform": sys.platform,
        "current_directory": os.getcwd()
    }
    
    debug_data = {
        "routes": routes,
        "system_info": system_info
    }
    
    return jsonify(debug_data)

# -------------------------------------------------------------------------
# Main entry point
# -------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=True)