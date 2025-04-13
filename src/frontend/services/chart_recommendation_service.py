"""
Chart Recommendation Service for SustainaTrend™

This service provides intelligent chart selection based on:
1. Data characteristics (time series, categorical, etc.)
2. Target audience (Board, Sustainability Team, Investors)
3. Narrative focus (Performance, Risk, Compliance)
4. Best practices in data visualization
"""

import logging
import json
from typing import Dict, List, Any, Tuple, Optional

# Setup logging
logger = logging.getLogger(__name__)

# Chart type constants
LINE_CHART = "line"
BAR_CHART = "bar"
AREA_CHART = "area"
STACKED_BAR = "stacked_bar"
PIE_CHART = "pie"
RADAR_CHART = "radar"
HEATMAP = "heatmap"
SCATTER_PLOT = "scatter"
SANKEY = "sankey"
GAUGE = "gauge"
FUNNEL = "funnel"
WATERFALL = "waterfall"

class ChartRecommender:
    """Intelligent chart recommendation system"""
    
    def __init__(self):
        """Initialize the chart recommender"""
        logger.info("Initializing Chart Recommender")
        
        # Define audience preferences
        self.audience_preferences = {
            "board": {
                "preferred": [GAUGE, PIE_CHART, WATERFALL],
                "avoid": [SCATTER_PLOT, HEATMAP, SANKEY],
                "max_data_points": 7,  # Board members prefer simpler visuals
                "description": "Board members prefer high-level visuals showing status and progress"
            },
            "sustainability_team": {
                "preferred": [LINE_CHART, AREA_CHART, HEATMAP, SCATTER_PLOT],
                "avoid": [],
                "max_data_points": 15,  # Sustainability teams can handle more detail
                "description": "Sustainability teams need detailed visuals that show patterns and causality"
            },
            "investors": {
                "preferred": [LINE_CHART, BAR_CHART, WATERFALL],
                "avoid": [RADAR_CHART, HEATMAP, FUNNEL],
                "max_data_points": 10,  # Investors prefer clear comparison visuals
                "description": "Investors need visuals that clearly show performance and comparison to benchmarks"
            }
        }
        
        # Define focus preferences
        self.focus_preferences = {
            "performance_analysis": {
                "preferred": [LINE_CHART, BAR_CHART, GAUGE],
                "description": "Performance analysis focuses on trends, comparisons, and status"
            },
            "risk_assessment": {
                "preferred": [HEATMAP, RADAR_CHART, GAUGE],
                "description": "Risk assessment visualizes threats, vulnerabilities, and impact levels"
            },
            "csrd_esg_compliance": {
                "preferred": [STACKED_BAR, SANKEY, WATERFALL],
                "description": "CSRD/ESG compliance shows regulatory status, gaps, and coverage"
            }
        }
        
        # Define data type compatibility
        self.data_compatibility = {
            "time_series": {
                "compatible": [LINE_CHART, AREA_CHART, BAR_CHART],
                "optimal": LINE_CHART,
                "description": "Time series data shows change over time periods"
            },
            "categorical": {
                "compatible": [BAR_CHART, PIE_CHART, STACKED_BAR],
                "optimal": BAR_CHART,
                "description": "Categorical data compares different categories or groups"
            },
            "part_to_whole": {
                "compatible": [PIE_CHART, STACKED_BAR, WATERFALL],
                "optimal": PIE_CHART,
                "description": "Part-to-whole shows how components contribute to a total"
            },
            "correlation": {
                "compatible": [SCATTER_PLOT, HEATMAP],
                "optimal": SCATTER_PLOT,
                "description": "Correlation data shows relationships between variables"
            },
            "distribution": {
                "compatible": [HEATMAP, BAR_CHART],
                "optimal": BAR_CHART,
                "description": "Distribution data shows how values are spread"
            }
        }
    
    def recommend_chart(
        self,
        metric: str,
        data: List[Dict[str, Any]],
        audience: str = "board",
        narrative_focus: str = "performance_analysis",
        chart_type: str = "auto"
    ) -> Dict[str, Any]:
        """
        Recommends the best chart type based on data, audience, and narrative focus
        
        Args:
            metric: The metric being visualized
            data: The dataset to visualize
            audience: Target audience (board, sustainability_team, investors)
            narrative_focus: Focus of the narrative
            chart_type: Specific chart type to use, or "auto" for AI recommendation
            
        Returns:
            Dictionary with chart recommendation and explanation
        """
        logger.info(f"Recommending chart for metric: {metric}, audience: {audience}")
        
        # If chart type is specified, use it
        if chart_type != "auto":
            return self._create_chart_recommendation(
                chart_type=chart_type,
                metric=metric,
                data=data,
                audience=audience,
                narrative_focus=narrative_focus,
                explanation=f"Using manually specified chart type: {chart_type}"
            )
        
        # Determine data characteristics
        data_type, data_properties = self._analyze_data(data)
        
        # Normalize inputs
        audience = audience.lower()
        narrative_focus = narrative_focus.lower().replace(" ", "_")
        
        # Handle unknown audience or focus
        if audience not in self.audience_preferences:
            audience = "board"  # Default to board
        
        if narrative_focus not in self.focus_preferences:
            narrative_focus = "performance_analysis"  # Default to performance
        
        # Score each chart type
        chart_scores = self._score_chart_types(
            data_type=data_type,
            data_properties=data_properties,
            audience=audience,
            narrative_focus=narrative_focus
        )
        
        # Get top recommendation
        top_chart = max(chart_scores.items(), key=lambda x: x[1]["score"])
        chart_type = top_chart[0]
        explanation = top_chart[1]["reason"]
        
        return self._create_chart_recommendation(
            chart_type=chart_type,
            metric=metric,
            data=data,
            audience=audience,
            narrative_focus=narrative_focus,
            explanation=explanation
        )
    
    def _analyze_data(self, data: List[Dict[str, Any]]) -> Tuple[str, Dict[str, Any]]:
        """
        Analyzes the dataset to determine its type and properties
        
        Args:
            data: The dataset to analyze
            
        Returns:
            Tuple of (data_type, data_properties)
        """
        # Default values
        data_type = "time_series"  # Default assumption
        data_properties = {
            "data_points": len(data),
            "has_time_dimension": False,
            "has_categories": False,
            "unique_categories": 0,
            "has_negative_values": False,
            "distribution_type": "normal"  # Default assumption
        }
        
        # Skip analysis for empty data
        if not data:
            return data_type, data_properties
        
        # Check for time dimension (date or time field)
        time_fields = ["date", "time", "timestamp", "year", "month", "day", "period"]
        for item in data:
            for key in item.keys():
                if any(time_field in key.lower() for time_field in time_fields):
                    data_properties["has_time_dimension"] = True
                    break
        
        # Check for categories
        category_fields = ["category", "type", "group", "name", "label"]
        categories = set()
        for item in data:
            for key in item.keys():
                if any(cat_field in key.lower() for cat_field in category_fields):
                    categories.add(str(item[key]))
                    data_properties["has_categories"] = True
        
        data_properties["unique_categories"] = len(categories)
        
        # Check for negative values
        for item in data:
            for key, value in item.items():
                if isinstance(value, (int, float)) and value < 0:
                    data_properties["has_negative_values"] = True
                    break
        
        # Determine data type based on properties
        if data_properties["has_time_dimension"]:
            data_type = "time_series"
        elif data_properties["has_categories"] and data_properties["unique_categories"] <= 5:
            data_type = "part_to_whole"
        elif data_properties["has_categories"]:
            data_type = "categorical"
        else:
            # Default to correlation if we can't determine
            data_type = "correlation"
        
        return data_type, data_properties
    
    def _score_chart_types(
        self,
        data_type: str,
        data_properties: Dict[str, Any],
        audience: str,
        narrative_focus: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Scores each chart type based on compatibility with data, audience, and focus
        
        Args:
            data_type: Type of data (time_series, categorical, etc.)
            data_properties: Properties of the data
            audience: Target audience
            narrative_focus: Focus of the narrative
            
        Returns:
            Dictionary of chart types with scores and reasons
        """
        scores = {}
        
        # Start with all chart types
        chart_types = [
            LINE_CHART, BAR_CHART, AREA_CHART, STACKED_BAR, PIE_CHART,
            RADAR_CHART, HEATMAP, SCATTER_PLOT, SANKEY, GAUGE, FUNNEL, WATERFALL
        ]
        
        for chart_type in chart_types:
            # Initialize score
            scores[chart_type] = {
                "score": 0,
                "reason": ""
            }
            
            # Data compatibility (most important)
            data_score = 0
            if data_type in self.data_compatibility:
                if chart_type in self.data_compatibility[data_type]["compatible"]:
                    data_score = 5
                if chart_type == self.data_compatibility[data_type]["optimal"]:
                    data_score = 10
            
            # Audience preference
            audience_score = 0
            if audience in self.audience_preferences:
                if chart_type in self.audience_preferences[audience]["preferred"]:
                    audience_score = 5
                if chart_type in self.audience_preferences[audience]["avoid"]:
                    audience_score = -5
            
            # Focus preference
            focus_score = 0
            if narrative_focus in self.focus_preferences:
                if chart_type in self.focus_preferences[narrative_focus]["preferred"]:
                    focus_score = 3
            
            # Special rules
            special_score = 0
            
            # Too many data points for pie chart
            if chart_type == PIE_CHART and data_properties["data_points"] > 7:
                special_score = -5
                
            # Negative values for pie chart
            if chart_type == PIE_CHART and data_properties["has_negative_values"]:
                special_score = -10
                
            # Too many categories for radar chart
            if chart_type == RADAR_CHART and data_properties["unique_categories"] > 10:
                special_score = -5
            
            # Calculate total score
            total_score = data_score + audience_score + focus_score + special_score
            scores[chart_type]["score"] = total_score
            
            # Generate reasoning
            reason_parts = []
            
            if data_score > 0:
                if chart_type == self.data_compatibility[data_type]["optimal"]:
                    reason_parts.append(f"Optimal for {data_type} data")
                else:
                    reason_parts.append(f"Compatible with {data_type} data")
            
            if audience_score > 0:
                reason_parts.append(f"Preferred by {audience} audience")
            elif audience_score < 0:
                reason_parts.append(f"Not ideal for {audience} audience")
            
            if focus_score > 0:
                reason_parts.append(f"Supports {narrative_focus.replace('_', ' ')} focus")
            
            if special_score < 0:
                if chart_type == PIE_CHART and data_properties["data_points"] > 7:
                    reason_parts.append("Too many data points for pie chart")
                if chart_type == PIE_CHART and data_properties["has_negative_values"]:
                    reason_parts.append("Negative values not suitable for pie chart")
                if chart_type == RADAR_CHART and data_properties["unique_categories"] > 10:
                    reason_parts.append("Too many categories for radar chart")
            
            scores[chart_type]["reason"] = ". ".join(reason_parts)
        
        return scores
    
    def _create_chart_recommendation(
        self,
        chart_type: str,
        metric: str,
        data: List[Dict[str, Any]],
        audience: str,
        narrative_focus: str,
        explanation: str
    ) -> Dict[str, Any]:
        """
        Creates a chart recommendation object
        
        Args:
            chart_type: Recommended chart type
            metric: The metric being visualized
            data: The dataset to visualize
            audience: Target audience
            narrative_focus: Focus of the narrative
            explanation: Explanation for the recommendation
            
        Returns:
            Chart recommendation object
        """
        # Create sample configuration for the chart
        sample_config = self._create_sample_config(chart_type, metric, data)
        
        return {
            "chart_type": chart_type,
            "explanation": explanation,
            "audience_notes": self.audience_preferences.get(audience, {}).get("description", ""),
            "focus_notes": self.focus_preferences.get(narrative_focus, {}).get("description", ""),
            "sample_config": sample_config,
            "data_truncated": len(data) > self.audience_preferences.get(audience, {}).get("max_data_points", 10)
        }
    
    def _create_sample_config(
        self,
        chart_type: str,
        metric: str,
        data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Creates a sample configuration for the recommended chart
        
        Args:
            chart_type: Chart type
            metric: The metric being visualized
            data: The dataset to visualize
            
        Returns:
            Sample chart configuration
        """
        config = {
            "type": chart_type,
            "title": f"{metric} Analysis",
            "data": data[:10],  # Limit to 10 data points for API response
            "options": {}
        }
        
        # Add chart-specific options
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
        elif chart_type == AREA_CHART:
            config["options"] = {
                "xAxis": {"type": "category"},
                "yAxis": {"type": "value"},
                "series": [{"type": "line", "areaStyle": {}}]
            }
        elif chart_type == RADAR_CHART:
            config["options"] = {
                "radar": {
                    "indicator": []
                },
                "series": [{"type": "radar"}]
            }
        elif chart_type == HEATMAP:
            config["options"] = {
                "visualMap": {
                    "min": 0,
                    "max": 10,
                    "calculable": True
                },
                "series": [{"type": "heatmap"}]
            }
        elif chart_type == GAUGE:
            config["options"] = {
                "series": [{
                    "type": "gauge",
                    "startAngle": 180,
                    "endAngle": 0,
                    "min": 0,
                    "max": 100
                }]
            }
        
        return config

# Singleton instance
_chart_recommender = None

def get_chart_recommender() -> ChartRecommender:
    """
    Get or create a ChartRecommender instance
    
    Returns:
        ChartRecommender instance
    """
    global _chart_recommender
    if _chart_recommender is None:
        _chart_recommender = ChartRecommender()
    
    return _chart_recommender

def recommend_chart_for_data(
    metric: str,
    data: List[Dict[str, Any]],
    audience: str = "board",
    narrative_focus: str = "performance_analysis",
    chart_type: str = "auto"
) -> Dict[str, Any]:
    """
    Recommends the best chart type for the given data
    
    Args:
        metric: The metric being visualized
        data: The dataset to visualize
        audience: Target audience (board, sustainability_team, investors)
        narrative_focus: Focus of the narrative (performance_analysis, risk_assessment, csrd_esg_compliance)
        chart_type: Specific chart type or "auto" for AI recommendation
        
    Returns:
        Chart recommendation
    """
    recommender = get_chart_recommender()
    return recommender.recommend_chart(
        metric=metric,
        data=data,
        audience=audience,
        narrative_focus=narrative_focus,
        chart_type=chart_type
    )

def get_chart_options() -> Dict[str, List[str]]:
    """
    Get available chart options for UI selection
    
    Returns:
        Dictionary with chart options by category
    """
    return {
        "time_based": [LINE_CHART, AREA_CHART, BAR_CHART],
        "comparative": [BAR_CHART, STACKED_BAR, RADAR_CHART],
        "proportional": [PIE_CHART, WATERFALL, FUNNEL],
        "relational": [SCATTER_PLOT, HEATMAP, SANKEY],
        "status": [GAUGE]
    }

def get_chart_type_info(chart_type: str) -> Dict[str, str]:
    """
    Get information about a specific chart type
    
    Args:
        chart_type: Chart type
        
    Returns:
        Dictionary with chart information
    """
    chart_info = {
        LINE_CHART: {
            "name": "Line Chart",
            "description": "Shows trends over time or continuous data",
            "best_for": "Time series data, trends, continuous data"
        },
        BAR_CHART: {
            "name": "Bar Chart",
            "description": "Compares values across categories",
            "best_for": "Categorical comparisons, ranking data"
        },
        AREA_CHART: {
            "name": "Area Chart",
            "description": "Shows volume over time with filled areas",
            "best_for": "Cumulative values, part-to-whole relationships over time"
        },
        STACKED_BAR: {
            "name": "Stacked Bar Chart",
            "description": "Shows components of a total across categories",
            "best_for": "Composition analysis across categories"
        },
        PIE_CHART: {
            "name": "Pie Chart",
            "description": "Shows composition or proportions of a whole",
            "best_for": "Proportion analysis with few categories (≤7)"
        },
        RADAR_CHART: {
            "name": "Radar Chart",
            "description": "Shows multiple variables in a radial layout",
            "best_for": "Multi-dimensional performance analysis"
        },
        HEATMAP: {
            "name": "Heatmap",
            "description": "Shows intensity with color variations",
            "best_for": "Distribution patterns, correlations between variables"
        },
        SCATTER_PLOT: {
            "name": "Scatter Plot",
            "description": "Shows relationship between variables",
            "best_for": "Correlation analysis, distribution patterns"
        },
        SANKEY: {
            "name": "Sankey Diagram",
            "description": "Shows flow between nodes with proportional bands",
            "best_for": "Resource flow, process visualization"
        },
        GAUGE: {
            "name": "Gauge Chart",
            "description": "Shows progress toward a goal with a needle indicator",
            "best_for": "Progress visualization, performance against targets"
        },
        FUNNEL: {
            "name": "Funnel Chart",
            "description": "Shows stages in a process with decreasing values",
            "best_for": "Process conversion visualization"
        },
        WATERFALL: {
            "name": "Waterfall Chart",
            "description": "Shows how an initial value is affected by sequential changes",
            "best_for": "Cumulative effect analysis, financial statements"
        }
    }
    
    return chart_info.get(chart_type, {
        "name": chart_type.capitalize(),
        "description": "Custom chart type",
        "best_for": "Specific visualization needs"
    })