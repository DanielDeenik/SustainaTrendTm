"""
Sustainability Trend Analysis Module

This module provides functionality for analyzing sustainability metrics trends,
calculating virality scores, and identifying key trending topics in sustainability data.
"""
import json
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from flask import jsonify
from typing import List, Dict, Any, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_sustainability_metrics() -> List[Dict[str, Any]]:
    """
    Fetch sustainability metrics data from the backend API or cache.
    This function will be used to get the raw metrics data for trend analysis.
    
    Returns:
        List of metrics data dictionaries
    """
    # This is a placeholder that will be connected to the actual data source
    # In the real implementation, this would fetch data from the backend API
    from simple_app import get_sustainability_metrics as get_metrics
    
    try:
        metrics = get_metrics()
        logger.info(f"Retrieved {len(metrics)} metrics for trend analysis")
        return metrics
    except Exception as e:
        logger.error(f"Error retrieving metrics for trend analysis: {str(e)}")
        return []

def calculate_trend_virality(metrics: List[Dict[str, Any]], category: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Calculate virality scores for sustainability trends based on metrics data.
    
    Args:
        metrics: List of metrics data dictionaries
        category: Optional category to filter metrics by
        
    Returns:
        List of trend data dictionaries with virality scores
    """
    if not metrics:
        logger.warning("No metrics data available for trend analysis")
        return []
    
    try:
        # Convert metrics to DataFrame for easier analysis
        df = pd.DataFrame(metrics)
        
        # Filter by category if specified
        if category:
            df = df[df["category"] == category]
            
        # Group metrics by name and calculate trend statistics
        trend_data = []
        
        for name, group in df.groupby("name"):
            # Sort by timestamp to analyze trends over time
            group = group.sort_values("timestamp")
            
            if len(group) < 2:
                logger.debug(f"Insufficient data points for {name} to calculate trend")
                continue
                
            # Calculate rate of change and momentum
            group["value"] = pd.to_numeric(group["value"])
            
            # Calculate simple rate of change
            latest_value = group["value"].iloc[-1]
            earliest_value = group["value"].iloc[0]
            percent_change = ((latest_value - earliest_value) / earliest_value) * 100 if earliest_value != 0 else 0
            
            # Determine trend direction
            if name in ["Carbon Emissions", "Energy Consumption", "Water Usage"]:
                # For these metrics, decreasing is good
                trend_direction = "improving" if percent_change < 0 else "worsening"
                # Invert percent change for virality calculation
                percent_change = -percent_change
            else:
                # For metrics like ESG Score and Waste Recycled, increasing is good
                trend_direction = "improving" if percent_change > 0 else "worsening"
            
            # Calculate a virality score (0-100)
            # Base on absolute change magnitude, with diminishing returns for extreme values
            change_magnitude = min(abs(percent_change) * 2, 100)
            change_factor = 0.7  # Weight for the magnitude of change
            
            # Momentum factor - how consistent is the trend
            values = group["value"].tolist()
            consecutive_changes = sum(1 for i in range(1, len(values)) if 
                                    (values[i] > values[i-1] and percent_change > 0) or
                                    (values[i] < values[i-1] and percent_change < 0))
            momentum_score = (consecutive_changes / (len(values) - 1)) * 100 if len(values) > 1 else 0
            momentum_factor = 0.3  # Weight for momentum
            
            # Calculate final virality score
            virality_score = (change_magnitude * change_factor) + (momentum_score * momentum_factor)
            
            # Get the category and unit from the first item in the group
            category = group["category"].iloc[0]
            unit = group["unit"].iloc[0]
            
            # Identify trending keywords based on the category and trend direction
            keywords = get_trending_keywords(name, category, trend_direction)
            
            # Determine trend duration based on data points and consistency
            trend_duration = get_trend_duration(group)
            
            # Create trend data entry
            trend_data.append({
                "trend_id": len(trend_data) + 1,
                "name": name,
                "category": category,
                "current_value": latest_value,
                "unit": unit,
                "trend_direction": trend_direction,
                "percent_change": round(percent_change, 2),
                "virality_score": round(virality_score, 2),
                "keywords": keywords,
                "trend_duration": trend_duration,
                "timestamp": group["timestamp"].iloc[-1]
            })
            
        logger.info(f"Calculated trend data for {len(trend_data)} metrics")
        return trend_data
        
    except Exception as e:
        logger.error(f"Error calculating trend virality: {str(e)}")
        return []

def get_trending_keywords(name: str, category: str, trend_direction: str) -> List[str]:
    """
    Identify trending keywords associated with a sustainability metric.
    
    Args:
        name: Name of the sustainability metric
        category: Category of the metric
        trend_direction: Direction of the trend (improving/worsening)
        
    Returns:
        List of trending keywords
    """
    # Predefined keywords based on metric category and trend direction
    keywords_map = {
        "emissions": {
            "improving": ["carbon neutral", "emissions reduction", "climate action"],
            "worsening": ["carbon footprint", "climate impact", "emission compliance"]
        },
        "energy": {
            "improving": ["renewable energy", "energy efficiency", "clean power"],
            "worsening": ["energy consumption", "power usage", "energy costs"]
        },
        "water": {
            "improving": ["water conservation", "water efficiency", "water management"],
            "worsening": ["water usage", "water scarcity", "water risk"]
        },
        "waste": {
            "improving": ["waste reduction", "recycling", "circular economy"],
            "worsening": ["waste management", "landfill", "waste streams"]
        },
        "social": {
            "improving": ["ESG leadership", "sustainability reporting", "corporate responsibility"],
            "worsening": ["ESG risk", "sustainability compliance", "reporting standards"]
        }
    }
    
    # Get keywords for this category and trend direction
    category_keywords = keywords_map.get(category, {})
    direction_keywords = category_keywords.get(trend_direction, [])
    
    # Add metric-specific keywords
    metric_keywords = []
    if "carbon" in name.lower():
        metric_keywords = ["carbon management", "emissions tracking"]
    elif "energy" in name.lower():
        metric_keywords = ["energy analytics", "power monitoring"]
    elif "water" in name.lower():
        metric_keywords = ["water footprint", "water sustainability"]
    elif "waste" in name.lower():
        metric_keywords = ["zero waste", "waste analytics"]
    elif "esg" in name.lower():
        metric_keywords = ["ESG scoring", "sustainability metrics"]
        
    # Combine and return unique keywords
    all_keywords = list(set(direction_keywords + metric_keywords))
    return all_keywords[:5]  # Return up to 5 keywords

def get_trend_duration(group: pd.DataFrame) -> str:
    """
    Determine the duration of a trend based on data consistency.
    
    Args:
        group: DataFrame group for a metric
        
    Returns:
        Trend duration classification (short/medium/long-term)
    """
    # If we have data for more than 5 months and trend is consistent, it's long-term
    if len(group) >= 5:
        return "long-term"
    # If we have data for 3-4 months, it's medium-term
    elif len(group) >= 3:
        return "medium-term"
    # Otherwise it's short-term
    else:
        return "short-term"

def get_sustainability_trends(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Main function to get sustainability trend analysis.
    
    Args:
        category: Optional category to filter trends by
        
    Returns:
        List of trend data dictionaries with virality scores and analysis
    """
    # Get metrics data
    metrics = get_sustainability_metrics()
    
    # Calculate trend virality and analysis
    trends = calculate_trend_virality(metrics, category)
    
    # Sort trends by virality score (descending)
    trends = sorted(trends, key=lambda x: x.get("virality_score", 0), reverse=True)
    
    return trends

# API endpoint function to be registered with Flask app
def api_sustainability_trends(category: Optional[str] = None):
    """
    API endpoint to get sustainability trend analysis.
    
    Args:
        category: Optional category to filter trends by
        
    Returns:
        JSON response with trend data
    """
    trends = get_sustainability_trends(category)
    return jsonify(trends)
