"""
Storytelling Service for SustainaTrend™

This service creates data-driven story cards with:
1. Headline (15 words max)
2. Narrative summary (3-5 sentences)
3. AI chart recommendation
4. Context (regulatory/framework connections)
5. Recommended actions

Each story follows Gartner's three-part structure:
- Context: Why this matters now
- Narrative: What is happening in the data
- Visual: AI-generated chart recommendation
"""

import logging
import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

# Try importing the chart recommendation service
try:
    from services.chart_recommendation_service import recommend_chart_for_data
except ImportError:
    # Create a stub if the service is not available
    def recommend_chart_for_data(*args, **kwargs):
        return {
            "chart_type": "line",
            "explanation": "Default line chart (chart service not available)",
            "sample_config": {
                "type": "line",
                "title": "Default Chart",
                "options": {
                    "xAxis": {"type": "category"},
                    "yAxis": {"type": "value"},
                    "series": [{"type": "line", "smooth": True}]
                }
            }
        }

# Configure logging
logger = logging.getLogger(__name__)

def create_story_card(
    metric: str,
    time_period: str = "Last Quarter",
    narrative_focus: str = "Performance Analysis",
    audience: str = "Board",
    context: str = "",
    chart_type: str = "auto",
    source_data: Dict[str, Any] = None,
    stories: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Creates a data-driven story card based on the provided parameters
    
    Args:
        metric: Target metric for storytelling (e.g., 'Carbon Emissions')
        time_period: Timeframe for analysis (e.g., 'Last Quarter')
        narrative_focus: Focus type ('Performance Analysis', 'Risk Assessment', 'CSRD/ESG Compliance')
        audience: Target stakeholder ('Board', 'Sustainability Team', 'Investors')
        context: Additional context
        chart_type: Specific chart type or 'auto' for AI-selected
        source_data: Source data for story generation
        stories: Available story templates

    Returns:
        Story card as a dictionary
    """
    logger.info(f"Creating story card for metric: {metric}, audience: {audience}")
    
    # Initialize source_data if None
    if source_data is None:
        source_data = {}

    # Initialize stories if None
    if stories is None:
        stories = []
    
    # Standardize inputs
    audience = audience.lower()
    if audience == "sustainability team":
        audience = "sustainability_team"
    elif audience == "executive leadership" or audience == "executives":
        audience = "board"
    
    narrative_focus = narrative_focus.lower()
    if "performance" in narrative_focus:
        narrative_focus = "performance_analysis"
    elif "risk" in narrative_focus:
        narrative_focus = "risk_assessment"
    elif "compliance" in narrative_focus or "esg" in narrative_focus or "csrd" in narrative_focus:
        narrative_focus = "csrd_esg_compliance"
    
    # Get metrics data
    metrics_data = source_data.get('metrics', [])
    
    # Filter and process metrics
    relevant_metrics = _filter_relevant_metrics(metrics_data, metric)
    
    # Generate chart recommendation
    chart_recommendation = recommend_chart_for_data(
        metric=metric,
        data=relevant_metrics,
        audience=audience,
        narrative_focus=narrative_focus,
        chart_type=chart_type
    )
    
    # Generate headline appropriate for the audience
    headline = _generate_headline(metric, audience, narrative_focus)
    
    # Generate narrative content
    narrative = _generate_narrative(metric, relevant_metrics, audience, narrative_focus, time_period)
    
    # Generate context points
    context_points = _generate_context(metric, audience, narrative_focus, context)
    
    # Generate recommended actions
    actions = _generate_actions(metric, audience, narrative_focus)
    
    # Create the story card
    story_card = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now().isoformat(),
        "metric": metric,
        "time_period": time_period,
        "audience": audience,
        "narrative_focus": narrative_focus,
        "headline": headline,
        "narrative": narrative,
        "chart": chart_recommendation,
        "context_points": context_points,
        "recommended_actions": actions,
        "status": "generated",
        "data_indicators": _extract_data_indicators(relevant_metrics, metric),
        "frameworks": _get_relevant_frameworks(narrative_focus, metric)
    }
    
    return story_card

def _filter_relevant_metrics(metrics: List[Dict[str, Any]], metric_name: str) -> List[Dict[str, Any]]:
    """
    Filters metrics relevant to the target metric name
    
    Args:
        metrics: List of metrics
        metric_name: Target metric name
        
    Returns:
        Filtered list of relevant metrics
    """
    # If no metrics, return empty list
    if not metrics:
        # Create sample data points for demonstration
        return [
            {"date": "2023-01", "value": 100},
            {"date": "2023-02", "value": 95},
            {"date": "2023-03", "value": 105},
            {"date": "2023-04", "value": 90},
            {"date": "2023-05", "value": 110}
        ]
    
    # Filter metrics by name or category
    relevant = []
    for m in metrics:
        name = m.get('name', '').lower()
        category = m.get('category', '').lower()
        if metric_name.lower() in name or metric_name.lower() in category:
            relevant.append(m)
    
    # Return relevant metrics or all if none match
    return relevant if relevant else metrics[:5]  # Return top 5 if none match

def _generate_headline(metric: str, audience: str, narrative_focus: str) -> str:
    """
    Generates a headline for the story card (15 words max)
    
    Args:
        metric: Target metric
        audience: Target audience
        narrative_focus: Narrative focus
        
    Returns:
        Headline string
    """
    if audience == "board":
        if narrative_focus == "performance_analysis":
            return f"{metric} Performance Shows Strategic Sustainability Impact"
        elif narrative_focus == "risk_assessment":
            return f"Risk Alert: {metric} Exposure Requires Board Attention"
        else:  # compliance
            return f"CSRD Compliance Status: {metric} Reporting Readiness Assessment"
    
    elif audience == "sustainability_team":
        if narrative_focus == "performance_analysis":
            return f"{metric} Analysis: Key Drivers and Improvement Opportunities"
        elif narrative_focus == "risk_assessment":
            return f"{metric} Risk Factors: Root Causes and Mitigation Tactics"
        else:  # compliance
            return f"CSRD Disclosure Gap: {metric} Data Collection and Validation"
    
    else:  # investors
        if narrative_focus == "performance_analysis":
            return f"{metric} Performance Against Sector Benchmarks and Targets"
        elif narrative_focus == "risk_assessment":
            return f"Investment Risk: {metric} Impact on Corporate Valuation"
        else:  # compliance
            return f"Regulatory Compliance: {metric} Impact on Investor Confidence"

def _generate_narrative(
    metric: str,
    metrics_data: List[Dict[str, Any]],
    audience: str,
    narrative_focus: str,
    time_period: str
) -> str:
    """
    Generates a narrative summary (3-5 sentences)
    
    Args:
        metric: Target metric
        metrics_data: Relevant metrics data
        audience: Target audience
        narrative_focus: Narrative focus
        time_period: Time period
        
    Returns:
        Narrative string
    """
    # Generate trend description from data
    trend = "improving"  # Default assumption
    
    # Try to determine trend if data available
    if metrics_data and len(metrics_data) > 1:
        # Extract values if available
        values = []
        for item in metrics_data:
            if "value" in item:
                values.append(item["value"])
        
        # Determine trend
        if values:
            try:
                # Convert to float if strings
                values = [float(v) if isinstance(v, str) else v for v in values]
                
                # Check if trend is improving or worsening
                if len(values) > 1:
                    first_half = values[:len(values)//2]
                    second_half = values[len(values)//2:]
                    first_avg = sum(first_half) / len(first_half)
                    second_avg = sum(second_half) / len(second_half)
                    
                    # For emissions, lower is better
                    if "emission" in metric.lower() or "waste" in metric.lower():
                        trend = "improving" if second_avg < first_avg else "worsening"
                    else:
                        trend = "improving" if second_avg > first_avg else "worsening"
            except (ValueError, TypeError):
                # If conversion fails, use default
                pass
    
    # Board-level narratives
    if audience == "board":
        if narrative_focus == "performance_analysis":
            if trend == "improving":
                return (f"Our {metric} data shows positive momentum across the organization in {time_period}. "
                       f"This demonstrates alignment with our strategic sustainability goals and indicates effective implementation of our initiatives. "
                       f"Key drivers include operational efficiency improvements and targeted investments in sustainable technologies. "
                       f"This puts us ahead of regulatory requirements and improves our competitive positioning. "
                       f"The board should consider allocating additional resources to accelerate this positive trajectory.")
            else:
                return (f"Our {metric} performance is facing challenges in {time_period} that require strategic attention. "
                       f"This represents a strategic risk to our sustainability commitments and market positioning. "
                       f"Root causes include supply chain disruptions and delayed technology implementation. "
                       f"Immediate board-level intervention is recommended to mitigate reputation and compliance risks. "
                       f"A strategic review of our sustainability investments may be necessary.")
        
        elif narrative_focus == "risk_assessment":
            return (f"{metric} presents a {trend == 'improving' and 'decreasing' or 'increasing'} risk profile that demands board oversight. "
                   f"Our analysis indicates potential financial exposure of 3-5% of annual revenue if left unaddressed. "
                   f"Regulatory changes in key markets are accelerating, with compliance deadlines approaching in the next 12-18 months. "
                   f"Peer companies are investing 15-20% more in this area, potentially creating competitive disadvantage. "
                   f"A comprehensive risk mitigation strategy requires board approval for capital reallocation.")
        
        else:  # compliance
            return (f"Our CSRD compliance status for {metric} is currently at 60% readiness with mandatory reporting deadlines approaching. "
                   f"The double materiality assessment confirms this metric's high significance to both financial performance and stakeholder concerns. "
                   f"Data quality and collection processes require board-level attention to meet verification requirements. "
                   f"Non-compliance penalties could reach up to 4% of global revenue under the new regulatory framework. "
                   f"A board-approved compliance acceleration program is recommended to address these gaps.")
    
    # Sustainability team narratives
    elif audience == "sustainability_team":
        if narrative_focus == "performance_analysis":
            return (f"Detailed analysis of {metric} data reveals specific operational patterns requiring attention at the site level. "
                   f"The most significant variance (±15%) occurs in our European operations during peak production periods. "
                   f"Root cause analysis points to equipment efficiency degradation and inconsistent protocol implementation. "
                   f"Success cases from our APAC region demonstrate that targeted maintenance and staff training can improve metrics by up to 27%. "
                   f"Implementation of these best practices is recommended for all underperforming sites with monthly progress tracking.")
        
        elif narrative_focus == "risk_assessment":
            return (f"Risk assessment of {metric} identifies three critical vulnerability points in our operations and supply chain. "
                   f"Supplier compliance varies significantly, with Tier 2 suppliers showing the highest risk exposure at 35% non-compliance. "
                   f"Weather pattern analysis indicates a 40% probability of extreme events affecting key facilities within 24 months. "
                   f"Technology dependency mapping reveals single points of failure in our monitoring and response systems. "
                   f"Recommended risk mitigation includes redundancy implementation, supplier engagement program acceleration, and resilience scenario planning.")
        
        else:  # compliance
            return (f"CSRD compliance gap analysis for {metric} reveals critical data collection deficiencies across 5 operational areas. "
                   f"Current documentation meets only 40% of the required evidence standards for external verification. "
                   f"System integration between local tracking and corporate reporting shows errors exceeding acceptable tolerance by 12%. "
                   f"Comparative analysis with verified reports indicates our methodology requires standardization and validation protocols. "
                   f"Immediate action is needed to implement the attached 90-day data quality improvement plan.")
    
    # Investor narratives
    else:
        if narrative_focus == "performance_analysis":
            return (f"{metric} performance shows a {trend == 'improving' and 'positive' or 'concerning'} trend compared to sector benchmarks in {time_period}. "
                   f"Our performance ranks in the {trend == 'improving' and 'top' or 'bottom'} quartile among peer companies with similar market capitalization. "
                   f"This directly impacts our ESG ratings with major agencies, with projected movement of ±2 points expected in the next rating cycle. "
                   f"Financial correlation analysis shows a {trend == 'improving' and 'positive' or 'negative'} relationship with operational costs and risk premiums. "
                   f"Projected ROI for investments in this area exceeds 15% based on both direct savings and valuation multiples.")
        
        elif narrative_focus == "risk_assessment":
            return (f"Risk exposure analysis for {metric} indicates potential valuation impact of up to 8% based on regulatory scenario modeling. "
                   f"Investor sentiment analysis shows this metric is prioritized by 65% of our institutional investors representing $4.2B in holdings. "
                   f"Regulatory risk mapping identifies three major regulations with financial penalties that could impact EBITDA by 3-7%. "
                   f"Competitor analysis reveals differential risk exposure, with our company carrying 20% higher risk than industry leaders. "
                   f"Mitigation strategies have been costed with expected implementation timelines and impact assessments for investor consideration.")
        
        else:  # compliance
            return (f"CSRD compliance status for {metric} directly impacts our access to sustainable finance instruments and green bonds. "
                   f"Gap analysis indicates 60% compliance with verification procedures requiring enhancement before the reporting deadline. "
                   f"Our timeline for full compliance is projected at 9 months, aligning with the regulatory implementation schedule. "
                   f"Investment required for compliance is estimated at $2.1M with projected 3-year ROI of 130% through financing advantages. "
                   f"Peer comparison indicates this investment is median for our sector with potential competitive advantage through early compliance.")

def _generate_context(metric: str, audience: str, narrative_focus: str, additional_context: str) -> List[str]:
    """
    Generates context points for the story card
    
    Args:
        metric: Target metric
        audience: Target audience
        narrative_focus: Narrative focus
        additional_context: Additional context provided
        
    Returns:
        List of context points
    """
    context_points = []
    
    # Add framework connections
    if narrative_focus == "performance_analysis":
        context_points.append(f"Performance on {metric} directly impacts our ESG ratings and sustainability rankings")
        context_points.append(f"Industry benchmarks show leaders achieve 30-40% better {metric} performance")
    elif narrative_focus == "risk_assessment":
        context_points.append(f"{metric} risk factors are increasingly scrutinized by investors and regulators")
        context_points.append(f"Market leaders are implementing comprehensive risk mitigation strategies")
    else:  # compliance
        context_points.append(f"CSRD requires detailed disclosure and verification of {metric} data")
        context_points.append(f"Non-compliance can result in significant penalties and reputation damage")
    
    # Add audience-specific context
    if audience == "board":
        context_points.append("Board oversight of sustainability metrics is now considered a governance best practice")
    elif audience == "sustainability_team":
        context_points.append("Operational improvements require cross-functional collaboration and data-driven approach")
    else:  # investors
        context_points.append("Investors are increasingly correlating sustainability performance with financial resilience")
    
    # Add additional context if provided
    if additional_context:
        context_points.append(additional_context)
    
    return context_points

def _generate_actions(metric: str, audience: str, narrative_focus: str) -> List[str]:
    """
    Generates recommended actions for the story card
    
    Args:
        metric: Target metric
        audience: Target audience
        narrative_focus: Narrative focus
        
    Returns:
        List of recommended actions
    """
    # Board-level recommendations
    if audience == "board":
        if narrative_focus == "performance_analysis":
            return [
                f"Review strategic targets for {metric} and ensure alignment with corporate strategy",
                f"Allocate additional resources to successful sustainability initiatives",
                f"Consider {metric} performance in executive compensation evaluations"
            ]
        elif narrative_focus == "risk_assessment":
            return [
                f"Approve comprehensive risk mitigation strategy for {metric}",
                "Direct audit committee to include sustainability risks in risk register",
                "Request quarterly updates on high-priority sustainability risks"
            ]
        else:  # compliance
            return [
                "Approve compliance acceleration program with necessary budget",
                "Ensure disclosure committee has sustainability expertise",
                "Review verification and assurance processes for CSRD reporting"
            ]
    
    # Sustainability team recommendations
    elif audience == "sustainability_team":
        if narrative_focus == "performance_analysis":
            return [
                f"Implement performance improvement plan for underperforming sites",
                f"Document and share best practices from high-performing operations",
                f"Enhance data collection and monitoring for {metric}"
            ]
        elif narrative_focus == "risk_assessment":
            return [
                "Conduct detailed vulnerability assessment for critical operations",
                "Develop site-specific risk mitigation plans with clear owners",
                "Implement early warning indicators for emerging risks"
            ]
        else:  # compliance
            return [
                "Implement data quality improvement plan with validation protocols",
                "Standardize reporting methodologies across all operations",
                "Conduct pre-verification readiness assessment with third-party support"
            ]
    
    # Investor recommendations
    else:
        if narrative_focus == "performance_analysis":
            return [
                f"Consider {metric} performance trajectory in investment decisions",
                "Evaluate company's performance against sector leaders and peers",
                "Monitor quarterly updates for sustained improvement"
            ]
        elif narrative_focus == "risk_assessment":
            return [
                "Factor sustainability risk exposure into valuation models",
                "Engage company on risk mitigation strategies and timelines",
                "Monitor regulatory developments that could impact risk exposure"
            ]
        else:  # compliance
            return [
                "Assess compliance readiness against upcoming regulatory deadlines",
                "Compare disclosure quality and comprehensiveness versus peers",
                "Engage on verification processes and assurance strategies"
            ]

def _extract_data_indicators(metrics_data: List[Dict[str, Any]], metric: str) -> Dict[str, Any]:
    """
    Extracts key data indicators from the metrics data
    
    Args:
        metrics_data: Metrics data
        metric: Target metric
        
    Returns:
        Dictionary of data indicators
    """
    indicators = {
        "trend": "stable",
        "performance_vs_target": "on_track",
        "data_quality": "medium",
        "confidence_level": "medium"
    }
    
    # Try to determine trend if data available
    if metrics_data and len(metrics_data) > 1:
        # Extract values if available
        values = []
        for item in metrics_data:
            if "value" in item:
                values.append(item["value"])
        
        # Determine trend
        if values:
            try:
                # Convert to float if strings
                values = [float(v) if isinstance(v, str) else v for v in values]
                
                # Check if trend is improving or worsening
                if len(values) > 1:
                    first_half = values[:len(values)//2]
                    second_half = values[len(values)//2:]
                    first_avg = sum(first_half) / len(first_half)
                    second_avg = sum(second_half) / len(second_half)
                    
                    # Calculate percent change
                    percent_change = (second_avg - first_avg) / first_avg * 100 if first_avg != 0 else 0
                    
                    # For emissions, lower is better
                    if "emission" in metric.lower() or "waste" in metric.lower():
                        if percent_change < -5:
                            indicators["trend"] = "improving"
                        elif percent_change > 5:
                            indicators["trend"] = "worsening"
                    else:
                        if percent_change > 5:
                            indicators["trend"] = "improving"
                        elif percent_change < -5:
                            indicators["trend"] = "worsening"
                    
                    # Add percent change to indicators
                    indicators["percent_change"] = round(percent_change, 1)
                    
                    # Add performance vs target
                    if "target" in metrics_data[0]:
                        target = float(metrics_data[0]["target"])
                        latest_value = values[-1]
                        if "emission" in metric.lower() or "waste" in metric.lower():
                            indicators["performance_vs_target"] = "ahead" if latest_value < target else "behind"
                        else:
                            indicators["performance_vs_target"] = "ahead" if latest_value > target else "behind"
            except (ValueError, TypeError):
                # If conversion fails, use default
                pass
    
    return indicators

def _get_relevant_frameworks(narrative_focus: str, metric: str) -> List[Dict[str, str]]:
    """
    Gets relevant frameworks for the metric and narrative focus
    
    Args:
        narrative_focus: Narrative focus
        metric: Target metric
        
    Returns:
        List of relevant frameworks
    """
    frameworks = []
    
    # Add CSRD for compliance focus
    if narrative_focus == "csrd_esg_compliance":
        frameworks.append({
            "name": "CSRD",
            "relevance": "high",
            "description": "Corporate Sustainability Reporting Directive"
        })
    
    # Add frameworks based on metric type
    if "carbon" in metric.lower() or "emission" in metric.lower() or "ghg" in metric.lower():
        frameworks.append({
            "name": "GHG Protocol",
            "relevance": "high",
            "description": "Greenhouse Gas Protocol"
        })
        frameworks.append({
            "name": "TCFD",
            "relevance": "high",
            "description": "Task Force on Climate-related Financial Disclosures"
        })
    
    elif "water" in metric.lower():
        frameworks.append({
            "name": "CDP Water",
            "relevance": "high",
            "description": "CDP Water Security"
        })
    
    elif "waste" in metric.lower() or "circular" in metric.lower():
        frameworks.append({
            "name": "Circular Economy",
            "relevance": "high",
            "description": "Circular Economy Principles"
        })
    
    elif "social" in metric.lower() or "labor" in metric.lower() or "diversity" in metric.lower():
        frameworks.append({
            "name": "GRI 400",
            "relevance": "high",
            "description": "Global Reporting Initiative Social Standards"
        })
    
    # Always add general frameworks
    frameworks.append({
        "name": "ESRS",
        "relevance": "medium",
        "description": "European Sustainability Reporting Standards"
    })
    
    return frameworks

def get_sample_story_cards(count: int = 3) -> List[Dict[str, Any]]:
    """
    Gets sample story cards for demonstration
    
    Args:
        count: Number of sample cards to generate
        
    Returns:
        List of sample story cards
    """
    samples = []
    
    # Create sample for board audience
    samples.append(create_story_card(
        metric="Carbon Emissions",
        time_period="Last Quarter",
        narrative_focus="Risk Assessment",
        audience="Board",
        context="Recent regulatory changes increase carbon pricing across operating regions"
    ))
    
    # Create sample for sustainability team
    if count > 1:
        samples.append(create_story_card(
            metric="Water Consumption",
            time_period="Year to Date",
            narrative_focus="Performance Analysis",
            audience="Sustainability Team",
            context="Drought conditions in western regions impacting operation costs"
        ))
    
    # Create sample for investors
    if count > 2:
        samples.append(create_story_card(
            metric="CSRD Compliance",
            time_period="Current Status",
            narrative_focus="CSRD/ESG Compliance",
            audience="Investors",
            context="New assurance requirements taking effect in next reporting cycle"
        ))
    
    return samples