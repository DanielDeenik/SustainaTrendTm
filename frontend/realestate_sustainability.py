"""
Real Estate Sustainability Intelligence Module for SustainaTrend™

This module provides specialized functionality for analyzing real estate sustainability data,
with a focus on housing corporations, realtors, and property investors.

Key features:
1. Property energy efficiency analysis (EPC labels, BREEAM-NL certifications)
2. Carbon footprint assessment for real estate portfolios
3. Green financing eligibility evaluation
4. Sustainability-driven market trend analysis
5. Housing & mortgage data integration

The module supports RAG-based insights generation for private market data.
"""
import json
import logging
import random
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import jinja2.exceptions
from flask import Flask, render_template, jsonify, request, Blueprint, Response, stream_with_context
from typing import List, Dict, Any, Optional, Union, Tuple

# Custom JSON encoder to handle numpy and pandas types
class NumPyJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, np.integer):
            return int(o)
        elif isinstance(o, np.floating):
            return float(o)
        elif isinstance(o, np.ndarray):
            return o.tolist()
        elif isinstance(o, pd.Timestamp):
            return o.isoformat()
        elif hasattr(o, 'to_dict'):
            return o.to_dict()
        return super(NumPyJSONEncoder, self).default(o)
from flask import jsonify, request, render_template
from typing import List, Dict, Any, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Real estate sustainability categories
REALESTATE_CATEGORIES = {
    "energy_efficiency": "Energy Efficiency",
    "carbon_footprint": "Carbon Footprint",
    "green_financing": "Green Financing",
    "certifications": "Sustainability Certifications",
    "market_trends": "Market Trends"
}

def get_real_estate_metrics() -> List[Dict[str, Any]]:
    """
    Fetch real estate sustainability metrics data.
    
    Returns:
        List of real estate metrics data dictionaries
    """
    # In production, this would fetch actual data from APIs or databases
    # For now, we generate mock data that matches our real estate sustainability categories
    try:
        metrics = generate_mock_realestate_metrics()
        logger.info(f"Generated {len(metrics)} real estate sustainability metrics")
        return metrics
    except Exception as e:
        logger.error(f"Error generating real estate metrics: {str(e)}")
        return []

def generate_mock_realestate_metrics() -> List[Dict[str, Any]]:
    """
    Generate mock real estate sustainability metrics for development.
    
    Returns:
        List of mock real estate sustainability metrics
    """
    # Current timestamp
    now = datetime.now()
    
    # Generate data for the last 12 months
    metrics = []
    
    # Property energy efficiency metrics
    metrics.extend([
        {
            "id": 1,
            "name": "Average EPC Rating",
            "category": "energy_efficiency",
            "value": get_random_trend_value(2.1, 0.2, 12, improvement=True),  # Lower is better (A=1, G=7)
            "unit": "rating",
            "timestamp": (now - timedelta(days=30*i)).isoformat()
        } for i in range(12)
    ])
    
    metrics.extend([
        {
            "id": 2, 
            "name": "BREEAM-NL Certified Properties",
            "category": "certifications",
            "value": get_random_trend_value(28, 2, 12, improvement=True),
            "unit": "percent",
            "timestamp": (now - timedelta(days=30*i)).isoformat()
        } for i in range(12)
    ])
    
    metrics.extend([
        {
            "id": 3,
            "name": "Portfolio Carbon Intensity",
            "category": "carbon_footprint",
            "value": get_random_trend_value(32, 3, 12, improvement=False),  # Lower is better
            "unit": "kgCO2/m²",
            "timestamp": (now - timedelta(days=30*i)).isoformat()
        } for i in range(12)
    ])
    
    metrics.extend([
        {
            "id": 4,
            "name": "Green Mortgage Share",
            "category": "green_financing",
            "value": get_random_trend_value(18, 2.5, 12, improvement=True),
            "unit": "percent",
            "timestamp": (now - timedelta(days=30*i)).isoformat()
        } for i in range(12)
    ])
    
    metrics.extend([
        {
            "id": 5,
            "name": "Sustainability Premium",
            "category": "market_trends",
            "value": get_random_trend_value(4.2, 0.3, 12, improvement=True),
            "unit": "percent",
            "timestamp": (now - timedelta(days=30*i)).isoformat()
        } for i in range(12)
    ])
    
    metrics.extend([
        {
            "id": 6,
            "name": "Water Efficiency Score",
            "category": "energy_efficiency",
            "value": get_random_trend_value(67, 2, 12, improvement=True),
            "unit": "score",
            "timestamp": (now - timedelta(days=30*i)).isoformat()
        } for i in range(12)
    ])
    
    metrics.extend([
        {
            "id": 7,
            "name": "Circular Materials Usage",
            "category": "carbon_footprint",
            "value": get_random_trend_value(23, 2, 12, improvement=True),
            "unit": "percent",
            "timestamp": (now - timedelta(days=30*i)).isoformat()
        } for i in range(12)
    ])
    
    metrics.extend([
        {
            "id": 8,
            "name": "Green Retrofit ROI",
            "category": "green_financing",
            "value": get_random_trend_value(7.2, 0.4, 12, improvement=True),
            "unit": "percent",
            "timestamp": (now - timedelta(days=30*i)).isoformat()
        } for i in range(12)
    ])
    
    metrics.extend([
        {
            "id": 9,
            "name": "WELL Certified Properties",
            "category": "certifications",
            "value": get_random_trend_value(12, 1.5, 12, improvement=True),
            "unit": "percent",
            "timestamp": (now - timedelta(days=30*i)).isoformat()
        } for i in range(12)
    ])
    
    metrics.extend([
        {
            "id": 10,
            "name": "Green Building Rental Premium",
            "category": "market_trends",
            "value": get_random_trend_value(5.8, 0.2, 12, improvement=True),
            "unit": "percent",
            "timestamp": (now - timedelta(days=30*i)).isoformat()
        } for i in range(12)
    ])
    
    # Additional metrics based on client requirements
    
    # Building insulation metrics
    metrics.extend([
        {
            "id": 11,
            "name": "Average Insulation R-Value",
            "category": "energy_efficiency",
            "value": get_random_trend_value(3.8, 0.2, 12, improvement=True), 
            "unit": "m²·K/W",
            "timestamp": (now - timedelta(days=30*i)).isoformat()
        } for i in range(12)
    ])
    
    # Solar potential metrics
    metrics.extend([
        {
            "id": 12,
            "name": "Solar Adoption Rate",
            "category": "energy_efficiency",
            "value": get_random_trend_value(22.5, 1.8, 12, improvement=True),
            "unit": "percent",
            "timestamp": (now - timedelta(days=30*i)).isoformat()
        } for i in range(12)
    ])
    
    # Embodied carbon in construction
    metrics.extend([
        {
            "id": 13,
            "name": "Embodied Carbon",
            "category": "carbon_footprint",
            "value": get_random_trend_value(350, 15, 12, improvement=False),  # Lower is better
            "unit": "kgCO2e/m²",
            "timestamp": (now - timedelta(days=30*i)).isoformat()
        } for i in range(12)
    ])
    
    # Lifecycle sustainability score
    metrics.extend([
        {
            "id": 14,
            "name": "Lifecycle Sustainability Score",
            "category": "carbon_footprint",
            "value": get_random_trend_value(64, 2.5, 12, improvement=True),
            "unit": "score",
            "timestamp": (now - timedelta(days=30*i)).isoformat()
        } for i in range(12)
    ])
    
    # Green mortgage interest rate discount
    metrics.extend([
        {
            "id": 15,
            "name": "Green Mortgage Rate Discount",
            "category": "green_financing",
            "value": get_random_trend_value(0.38, 0.05, 12, improvement=True),
            "unit": "percent",
            "timestamp": (now - timedelta(days=30*i)).isoformat()
        } for i in range(12)
    ])
    
    # Sustainability tax benefits
    metrics.extend([
        {
            "id": 16,
            "name": "Sustainability Tax Benefits",
            "category": "green_financing",
            "value": get_random_trend_value(1250, 125, 12, improvement=True),
            "unit": "EUR",
            "timestamp": (now - timedelta(days=30*i)).isoformat()
        } for i in range(12)
    ])
    
    # GRESB score
    metrics.extend([
        {
            "id": 17,
            "name": "GRESB Rating",
            "category": "certifications",
            "value": get_random_trend_value(75, 3, 12, improvement=True),
            "unit": "score",
            "timestamp": (now - timedelta(days=30*i)).isoformat()
        } for i in range(12)
    ])
    
    # Neighborhood sustainability benchmarking
    metrics.extend([
        {
            "id": 18,
            "name": "Neighborhood Sustainability Score",
            "category": "market_trends",
            "value": get_random_trend_value(68, 2.2, 12, improvement=True),
            "unit": "score",
            "timestamp": (now - timedelta(days=30*i)).isoformat()
        } for i in range(12)
    ])
    
    # Renovation potential score
    metrics.extend([
        {
            "id": 19,
            "name": "Green Upgrade Potential",
            "category": "market_trends",
            "value": get_random_trend_value(56, 3, 12, improvement=True),
            "unit": "score",
            "timestamp": (now - timedelta(days=30*i)).isoformat()
        } for i in range(12)
    ])
    
    # Regulatory risk exposure
    metrics.extend([
        {
            "id": 20,
            "name": "Regulatory Risk Exposure",
            "category": "market_trends",
            "value": get_random_trend_value(28, 4, 12, improvement=False),  # Lower is better
            "unit": "score",
            "timestamp": (now - timedelta(days=30*i)).isoformat()
        } for i in range(12)
    ])
    
    return metrics

def get_random_trend_value(base: float, volatility: float, months_ago: int, improvement: bool = True) -> float:
    """
    Generate a random trend value with improvement or deterioration over time.
    
    Args:
        base: Base value
        volatility: Volatility factor
        months_ago: How many months ago (higher means further in the past)
        improvement: Whether the metric should improve over time
        
    Returns:
        Generated value
    """
    # Add random noise
    random_factor = np.random.normal(0, volatility)
    
    # Add trend component
    if improvement:
        trend_component = -months_ago * (volatility / 2)  # Negative because older values should be worse
    else:
        trend_component = months_ago * (volatility / 2)  # Positive because older values should be better
    
    return round(base + random_factor + trend_component, 2)

def calculate_realestate_trends(metrics: List[Dict[str, Any]], category: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Calculate trends for real estate sustainability metrics.
    
    Args:
        metrics: List of real estate metrics data
        category: Optional category to filter by
        
    Returns:
        List of trend data with analysis
    """
    if not metrics:
        return []
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(metrics)
    
    # Convert timestamps to datetime objects
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Filter by category if specified
    if category and category != 'all':
        df = df[df['category'] == category]
    
    # Group by name and analyze trends
    results = []
    
    for name, group in df.groupby('name'):
        # Sort by timestamp
        group = group.sort_values('timestamp')
        
        # Get the latest metrics
        latest = group.iloc[-1]
        
        # Get previous metrics
        if len(group) > 1:
            previous = group.iloc[-2]
            
            # Calculate percent change
            if previous['value'] != 0:
                percent_change = ((latest['value'] - previous['value']) / abs(previous['value'])) * 100
            else:
                percent_change = 0
        else:
            percent_change = 0
        
        # Determine if improving or worsening based on the metric
        # For some metrics like carbon intensity, lower is better
        lower_is_better = latest['category'] in ['carbon_footprint'] or 'rating' in latest['unit']
        
        if lower_is_better:
            trend_direction = 'improving' if percent_change < 0 else 'worsening'
            percent_change = abs(percent_change)  # Make positive for display
        else:
            trend_direction = 'improving' if percent_change > 0 else 'worsening'
            percent_change = abs(percent_change)  # Make positive for display
        
        # Calculate trend duration
        trend_duration = get_trend_duration(group)
        
        # Calculate virality score (0-100)
        virality_score = calculate_virality_score(
            abs(percent_change), 
            trend_duration,
            latest['category']
        )
        
        # Generate trending keywords
        keywords = get_trending_keywords(latest['name'], latest['category'], trend_direction)
        
        # Create trend object
        trend = {
            'trend_id': latest['id'],
            'name': latest['name'],
            'category': latest['category'],
            'current_value': latest['value'],
            'unit': latest['unit'],
            'percent_change': round(percent_change, 2),
            'trend_direction': trend_direction,
            'trend_duration': trend_duration,
            'virality_score': round(virality_score, 2),
            'timestamp': latest['timestamp'],
            'keywords': keywords
        }
        
        results.append(trend)
    
    # Sort by virality score
    results.sort(key=lambda x: x['virality_score'], reverse=True)
    
    return results

def get_trend_duration(group: pd.DataFrame) -> str:
    """
    Determine the duration of a trend based on data consistency.
    
    Args:
        group: DataFrame group for a metric
        
    Returns:
        Trend duration classification (short/medium/long-term)
    """
    if len(group) < 3:
        return "short-term"
    
    # Get last three values
    recent_values = group.sort_values('timestamp', ascending=False).iloc[:3]['value'].values
    
    # Check if the trend is consistent
    is_increasing = all(recent_values[i] > recent_values[i+1] for i in range(len(recent_values)-1))
    is_decreasing = all(recent_values[i] < recent_values[i+1] for i in range(len(recent_values)-1))
    
    if is_increasing or is_decreasing:
        if len(group) >= 6:
            # Check if the trend is consistent over a longer period
            longer_values = group.sort_values('timestamp', ascending=False).iloc[:6]['value'].values
            long_increasing = all(longer_values[i] > longer_values[i+1] for i in range(len(longer_values)-1))
            long_decreasing = all(longer_values[i] < longer_values[i+1] for i in range(len(longer_values)-1))
            
            if long_increasing or long_decreasing:
                return "long-term"
            else:
                return "medium-term"
        else:
            return "medium-term"
    else:
        return "short-term"

def calculate_virality_score(percent_change: float, trend_duration: str, category: str) -> float:
    """
    Calculate a virality score for a sustainability trend.
    
    Args:
        percent_change: Percent change in the metric
        trend_duration: Duration of the trend (short/medium/long-term)
        category: Category of the metric
        
    Returns:
        Virality score (0-100)
    """
    # Base score from percent change
    base_score = min(percent_change * 2, 60)  # Cap at 60 points from percent change
    
    # Duration factor
    duration_factors = {
        "short-term": 0.7,
        "medium-term": 1.0,
        "long-term": 1.3
    }
    
    # Category relevance factor
    category_factors = {
        "energy_efficiency": 1.2,
        "carbon_footprint": 1.3,
        "green_financing": 1.0,
        "certifications": 0.9,
        "market_trends": 1.1
    }
    
    # Apply factors
    duration_factor = duration_factors.get(trend_duration, 1.0)
    category_factor = category_factors.get(category, 1.0)
    
    # Calculate final score
    score = base_score * duration_factor * category_factor
    
    # Cap at 100
    return min(score, 100)

def get_trending_keywords(name: str, category: str, trend_direction: str) -> List[str]:
    """
    Generate trending keywords for real estate sustainability metrics.
    
    Args:
        name: Name of the metric
        category: Category of the metric
        trend_direction: Direction of the trend (improving/worsening)
        
    Returns:
        List of trending keywords
    """
    # Base keywords by category
    category_keywords = {
        "energy_efficiency": [
            "energy efficiency", "building performance", "passive design", 
            "insulation", "energy rating"
        ],
        "carbon_footprint": [
            "carbon neutral", "net zero", "embodied carbon", 
            "carbon footprint", "lifecycle assessment"
        ],
        "green_financing": [
            "green mortgage", "sustainable finance", "ESG investing", 
            "climate bonds", "green loans"
        ],
        "certifications": [
            "BREEAM certification", "WELL building", "LEED certification", 
            "EPC label", "green building"
        ],
        "market_trends": [
            "green premium", "sustainability value", "climate resilience", 
            "ESG requirements", "sustainable housing"
        ]
    }
    
    # Get base keywords for this category
    base_keywords = category_keywords.get(category, ["sustainability"])
    
    # Add trend direction and metric-specific keywords
    if trend_direction == "improving":
        direction_keywords = ["improving", "outperforming", "optimizing", "advancing", "leadership"]
    else:
        direction_keywords = ["challenges", "opportunity", "focus area", "attention needed", "priority"]
    
    # Combine and select 5 keywords
    all_keywords = base_keywords + direction_keywords
    
    # Add specific keywords based on the metric name
    name_lower = name.lower()
    if "epc" in name_lower:
        all_keywords.extend(["energy performance certificate", "building standards"])
    elif "carbon" in name_lower:
        all_keywords.extend(["carbon reduction", "emission targets"])
    elif "green" in name_lower and "mortgage" in name_lower:
        all_keywords.extend(["sustainable finance", "green lending"])
    elif "premium" in name_lower:
        all_keywords.extend(["value increase", "market advantage"])
    elif "retrofit" in name_lower:
        all_keywords.extend(["building upgrade", "energy renovation"])
    elif "water" in name_lower:
        all_keywords.extend(["water conservation", "efficient plumbing"])
    elif "breeam" in name_lower or "well" in name_lower:
        all_keywords.extend(["certification standards", "sustainable buildings"])
    
    # Shuffle and select 5 keywords
    np.random.shuffle(all_keywords)
    return all_keywords[:5]

def get_realestate_trend_analysis(category: Optional[str] = None) -> Dict[str, Any]:
    """
    Get comprehensive real estate sustainability trend analysis.
    
    Args:
        category: Optional category to filter by
        
    Returns:
        Dictionary with trend analysis data
    """
    # Get metrics data
    metrics = get_real_estate_metrics()
    
    # Calculate trends
    trends = calculate_realestate_trends(metrics, category)
    
    # Group metrics by timestamp for chart data
    df = pd.DataFrame(metrics)
    
    if not df.empty:
        # Convert timestamps to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Get unique timestamps sorted chronologically
        timestamps = sorted(df['timestamp'].unique())
        
        # Prepare chart data
        chart_data = []
        
        for ts in timestamps:
            # Filter data for this timestamp
            ts_data = df[df['timestamp'] == ts]
            
            # Create data point with aggregated values by category
            data_point = {
                'timestamp': ts.strftime('%Y-%m-%d')
            }
            
            # Add normalized values by category (0-100 scale)
            for category in REALESTATE_CATEGORIES.keys():
                category_data = ts_data[ts_data['category'] == category]
                if not category_data.empty:
                    # Normalize to 0-100 scale (simple average for now)
                    # In a real implementation, this would use more sophisticated aggregation
                    avg_value = category_data['value'].mean()
                    # Simple min-max normalization based on typical ranges
                    # This would be refined based on actual data distributions
                    normalized = avg_value / 100 * 70 + 15  # Scale to range approximately 15-85
                    data_point[category] = round(normalized, 2)
                else:
                    data_point[category] = 0
            
            chart_data.append(data_point)
        
        # Count metrics by category
        category_counts = df['category'].value_counts().to_dict()
    else:
        chart_data = []
        category_counts = {}
    
    # Return comprehensive analysis
    return {
        'success': True,
        'trends': trends,
        'chart_data': chart_data,
        'category_counts': category_counts
    }

def configure_routes(app):
    """
    Configure Flask routes for real estate sustainability intelligence
    
    Args:
        app: Flask application
    """
    @app.route('/realestate-trends')
    def realestate_trend_analysis():
        """Real Estate Sustainability Trend Analysis dashboard with theme support"""
        # Get category filter if provided
        category = request.args.get('category', None)
        
        # Get theme preference (default to dark theme)
        theme = request.args.get('theme', 'dark')
        
        # Get trend data
        trend_data = get_realestate_trend_analysis(category)
        
        # Use the appropriate template based on the theme
        template_name = "realestate_trend_analysis.html"
        if theme == 'dark':
            template_name = "realestate_trend_analysis_dark.html"
            logger.info("Using Finchat dark theme for real estate trend analysis")
        else:
            logger.info("Using light theme for real estate trend analysis")
        
        # Prepare additional metrics for the updated page
        additional_metrics = {
            'energy_efficiency': {
                'avg_value': round(np.mean([m['value'] for m in trend_data['metrics'] if m['category'] == 'energy_efficiency']), 1) if trend_data.get('metrics') else 68.5,
                'change': '+4.2%',
                'trend': 'up',
            },
            'carbon_footprint': {
                'avg_value': round(np.mean([m['value'] for m in trend_data['metrics'] if m['category'] == 'carbon_footprint']), 1) if trend_data.get('metrics') else 32.8,
                'change': '-6.5%',
                'trend': 'down',
            },
            'green_financing': {
                'avg_value': round(np.mean([m['value'] for m in trend_data['metrics'] if m['category'] == 'green_financing']), 1) if trend_data.get('metrics') else 18.7,
                'change': '+12.3%',
                'trend': 'up',
            },
            'market_trends': {
                'avg_value': round(np.mean([m['value'] for m in trend_data['metrics'] if m['category'] == 'market_trends']), 1) if trend_data.get('metrics') else 5.4,
                'change': '+2.1%',
                'trend': 'up',
            },
        }
        
        # Regional performance data
        regions = ['North', 'South', 'East', 'West', 'Central']
        regional_data = {
            'labels': regions,
            'energy_efficiency': [round(np.random.uniform(60, 85), 1) for _ in regions],
            'carbon_footprint': [round(np.random.uniform(25, 45), 1) for _ in regions],
            'green_financing': [round(np.random.uniform(10, 25), 1) for _ in regions]
        }
        
        return render_template(
            template_name,
            trends=trend_data['trends'],
            trend_chart_data=json.dumps(trend_data['chart_data']),
            category=category or 'all',
            categories=REALESTATE_CATEGORIES,
            sort="virality",
            current_theme=theme,
            additional_metrics=additional_metrics,
            regional_data=json.dumps(regional_data, cls=NumPyJSONEncoder)
        )
    
    @app.route('/realestate-unified-dashboard')
    def realestate_unified_dashboard():
        """Unified Real Estate Sustainability Dashboard with BREEAM & Extended Metrics"""
        # Get category filter if provided
        category = request.args.get('category', None)
        
        # Get trend data
        trend_data = get_realestate_trend_analysis(category)
        
        # The theme is now handled by the base template and context processor
        logger.info("Rendering unified real estate dashboard with dynamic theme support")
        
        return render_template(
            "realestate_unified_dashboard.html",
            trends=trend_data['trends'],
            trend_chart_data=json.dumps(trend_data['chart_data'], cls=NumPyJSONEncoder),
            category=category or 'all',
            categories=REALESTATE_CATEGORIES,
            sort="virality"
        )
    
    @app.route('/api-realestate-gemini-search', methods=['GET', 'POST'])
    def api_realestate_gemini_search():
        """API endpoint for Gemini-powered real estate sustainability search"""
        if request.method == 'POST':
            data = request.get_json()
            query = data.get('query', '') if data else ''
        else:
            query = request.args.get('query', '')
        
        try:
            # Import the Gemini search controller
            from gemini_search import GeminiSearchController
            
            # Initialize the Gemini search controller
            gemini_controller = GeminiSearchController()
            
            # Convert the async function to sync using asyncio.run
            import asyncio
            response = asyncio.run(gemini_controller.enhanced_search(
                query=query,
                mode="gemini",
                max_results=5
            ))
            
            # Process the response to extract the most relevant content
            if response and 'results' in response and len(response['results']) > 0:
                first_result = response['results'][0]
                content_html = f"""
                <div class="mb-3">{first_result.get('snippet', '')}</div>
                <div class="st-gemini-source-info">
                    <a href="{first_result.get('url', '#')}" target="_blank" class="st-gemini-source-link">
                        {first_result.get('title', 'Source')} <i class="bi bi-box-arrow-up-right ms-1"></i>
                    </a>
                </div>
                """
                
                # Add more in-depth analysis if available
                if 'analysis' in response:
                    content_html += f"""
                    <div class="alert alert-info mt-3">
                        <i class="bi bi-info-circle"></i> <strong>Insight:</strong> {response['analysis'].get('summary', '')}
                    </div>
                    """
                
                return jsonify({
                    'success': True,
                    'content': content_html,
                    'query': query,
                    'result_count': len(response.get('results', []))
                })
            else:
                # If no results, return a formatted message
                return jsonify({
                    'success': False,
                    'content': """
                    <div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle"></i> No specific information found for this query. 
                        Please try one of the suggested questions or rephrase your query.
                    </div>
                    """,
                    'query': query,
                    'result_count': 0
                })
                
        except Exception as e:
            # Log the error
            app.logger.error(f"Error in Gemini search: {str(e)}")
            
            # Return a formatted error message
            return jsonify({
                'success': False,
                'content': f"""
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle-fill"></i> <strong>Error:</strong> 
                    Unable to process your query at this time. Please try again later.
                </div>
                <div class="small text-muted">Error details: {str(e)}</div>
                """,
                'query': query,
                'error': str(e)
            })
    
    @app.route('/api/realestate-updates')
    def api_realestate_updates():
        """API endpoint for recent updates in real estate sustainability metrics"""
        # This provides a regular JSON API for recent updates
        # Different from the SSE endpoint which provides real-time streaming
        
        return jsonify({
            'updates': [
                {
                    'type': 'breeam',
                    'title': 'BREEAM Rating Updated',
                    'description': 'Marina Heights has achieved "Excellent" BREEAM certification after recent renovations.',
                    'timestamp': datetime.now().isoformat()
                },
                {
                    'type': 'energy',
                    'title': 'Energy Consumption Alert',
                    'description': 'Eastern Complex showing unusual energy consumption patterns in the last 24 hours.',
                    'timestamp': (datetime.now() - timedelta(minutes=15)).isoformat()
                },
                {
                    'type': 'carbon',
                    'title': 'Carbon Reduction Achievement',
                    'description': 'Healthcare Center has achieved carbon neutrality goal for Q1 2025.',
                    'timestamp': (datetime.now() - timedelta(minutes=35)).isoformat()
                }
            ]
        })
            
    @app.route('/api/realestate-trends')
    def api_realestate_trends():
        """API endpoint for real estate sustainability trend data"""
        # Get category filter if provided
        category = request.args.get('category', None)
        
        # Get trend data
        trend_data = get_realestate_trend_analysis(category)
        
        # Use our custom NumPyJSONEncoder to handle numpy data types
        return app.response_class(
            response=json.dumps(trend_data, cls=NumPyJSONEncoder),
            status=200,
            mimetype='application/json'
        )
        
    @app.route('/api/realestate-realtime-updates')
    def realestate_realtime_updates():
        """
        Server-Sent Events endpoint for real-time dashboard updates
        Provides real-time MongoDB data streaming for SimCorp One-inspired UI
        """
        def generate():
            # Initial SSE message to establish connection
            yield "data: {\"event\": \"connected\", \"message\": \"Real-time updates established\"}\n\n"
            
            # In a production environment, this would use a MongoDB change stream
            # For now, we'll simulate real-time updates with periodic data
            count = 0
            try:
                while True:
                    count += 1
                    # Check if client closed connection
                    if request.headers.get('Accept') != 'text/event-stream':
                        break
                        
                    # Generate simulated update data
                    if count % 3 == 0:
                        # BREEAM metrics update
                        update_data = {
                            "event": "breeam_update",
                            "component": "breeam",
                            "data": {
                                "property_id": f"PROP-{random.randint(1000, 9999)}",
                                "score": round(random.uniform(70, 95), 1),
                                "category": random.choice(["management", "health", "energy", "water", "materials"]),
                                "timestamp": datetime.now().isoformat()
                            }
                        }
                    elif count % 3 == 1:
                        # Energy metrics update
                        update_data = {
                            "event": "energy_update",
                            "component": "energy",
                            "data": {
                                "property_id": f"PROP-{random.randint(1000, 9999)}",
                                "consumption": round(random.uniform(80, 150), 1),
                                "unit": "kWh/m²",
                                "trend": random.choice(["decreasing", "stable", "increasing"]),
                                "timestamp": datetime.now().isoformat()
                            }
                        }
                    else:
                        # Carbon metrics update
                        update_data = {
                            "event": "carbon_update",
                            "component": "carbon",
                            "data": {
                                "property_id": f"PROP-{random.randint(1000, 9999)}",
                                "emissions": round(random.uniform(20, 50), 1),
                                "unit": "kgCO₂e/m²",
                                "reduction": round(random.uniform(5, 25), 1),
                                "timestamp": datetime.now().isoformat()
                            }
                        }
                        
                    yield f"data: {json.dumps(update_data)}\n\n"
                    time.sleep(5)  # Send update every 5 seconds
                    
            except GeneratorExit:
                logger.info("Client closed SSE connection")
            except Exception as e:
                logger.error(f"Error in SSE stream: {str(e)}")
                
        return Response(stream_with_context(generate()), 
                      mimetype='text/event-stream',
                      headers={'Cache-Control': 'no-cache', 
                                'Connection': 'keep-alive',
                                'X-Accel-Buffering': 'no'})

def register_routes(app):
    """
    Register real estate sustainability routes with Flask application
    
    Args:
        app: Flask application
    """
    configure_routes(app)
    logger.info("Real Estate Sustainability routes registered")