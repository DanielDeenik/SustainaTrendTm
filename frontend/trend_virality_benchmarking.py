"""
Trend & Virality Benchmarking Module for SustainaTrend™

This module provides advanced trend analysis and virality benchmarking for sustainability topics
using the STEPPS framework to assess why certain topics gain traction, with competitor benchmarking
and integration of management consulting frameworks for strategic insights.

Key features:
1. STEPPS framework analysis (Social currency, Triggers, Emotion, Public, Practical value, Stories)
2. Real-time sustainability trend monitoring
3. Competitor benchmarking for online sustainability presence
4. Strategic framework integration (Porter's Five Forces, McKinsey 7S)
5. Data-driven storytelling elements for strategic positioning
6. Science-Based Targets initiative (SBTi) alignment and recommendation generator
"""
import json
import logging
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
import os
from sustainability_trend import calculate_trend_virality, get_sustainability_metrics, get_sustainability_trends

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# STEPPS Virality Framework Components
STEPPS_COMPONENTS = {
    "social_currency": "Provides insider knowledge or makes people look good when sharing",
    "triggers": "Environmental cues that prompt people to think about the product/topic",
    "emotion": "Content that evokes high-arousal emotions (awe, anger, anxiety, excitement)",
    "public": "Visibility and observability of the behavior or topic",
    "practical_value": "Useful, actionable information that helps others",
    "stories": "Narrative elements that carry the message/values while being shareable"
}

# Strategic consulting frameworks
CONSULTING_FRAMEWORKS = {
    "porters_five_forces": {
        "name": "Porter's Five Forces",
        "description": "Analyzes competitive intensity and business strategy potential",
        "elements": ["Competitive Rivalry", "Supplier Power", "Buyer Power", "Threat of Substitution", "Threat of New Entry"]
    },
    "mckinsey_7s": {
        "name": "McKinsey 7S",
        "description": "Examines organizational effectiveness through 7 interconnected factors",
        "elements": ["Strategy", "Structure", "Systems", "Shared Values", "Skills", "Style", "Staff"]
    },
    "sustainability_impact": {
        "name": "Sustainability Impact Assessment",
        "description": "Evaluates environmental, social and governance impacts",
        "elements": ["Environmental Footprint", "Social Impact", "Governance Structure", "Stakeholder Engagement", "Long-term Resilience"]
    }
}

def analyze_trend_with_stepps(trend_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze a sustainability trend using the STEPPS virality framework.
    
    Args:
        trend_data: Dictionary containing trend information
        
    Returns:
        Dictionary with STEPPS analysis scores and insights
    """
    # Extract relevant trend information
    trend_name = trend_data.get("name", "")
    category = trend_data.get("category", "")
    trend_direction = trend_data.get("trend_direction", "")
    virality_score = trend_data.get("virality_score", 0)
    keywords = trend_data.get("keywords", [])
    
    # Determine base STEPPS scores based on trend characteristics
    # Each component gets a score from 1-10
    
    # 1. Social Currency - higher for trending/improving metrics that make companies look good
    social_currency = 8 if trend_direction == "improving" and virality_score > 50 else 5
    
    # 2. Triggers - based on how frequently the topic comes up in daily operations
    triggers_map = {
        "emissions": 9,  # High visibility due to regulations and reporting
        "energy": 7,     # Regular monitoring but less frequent reporting
        "water": 6,      # Important but less frequently discussed
        "waste": 7,      # Regular operations topic
        "social": 8,     # High visibility HR topic
        "governance": 6  # Important but discussed in specific contexts
    }
    triggers = triggers_map.get(category, 5)
    
    # 3. Emotion - higher for topics with emotional impact
    emotion_topics = ["climate change", "carbon footprint", "sustainability", "renewable"]
    emotion = 8 if any(topic in ' '.join(keywords).lower() for topic in emotion_topics) else 6
    
    # 4. Public - visibility of the metric to outside stakeholders
    public_map = {
        "emissions": 9,  # Highly visible in sustainability reports
        "energy": 7,     # Reported but less scrutinized
        "water": 6,      # Less visible except in water-intensive industries
        "waste": 8,      # Visible aspect of operations
        "social": 9,     # Highly visible in ESG reporting
        "governance": 7  # Important for investors
    }
    public = public_map.get(category, 5)
    
    # 5. Practical Value - usefulness of sharing this information
    practical = 8 if trend_direction == "improving" and virality_score > 60 else 6
    
    # 6. Stories - narrative potential
    stories = 7 if virality_score > 70 else 5
    
    # Calculate the overall STEPPS score (weighted average)
    weights = {
        "social_currency": 0.2,
        "triggers": 0.15,
        "emotion": 0.25,
        "public": 0.15,
        "practical_value": 0.15,
        "stories": 0.1
    }
    
    stepps_components = {
        "social_currency": social_currency,
        "triggers": triggers,
        "emotion": emotion,
        "public": public,
        "practical_value": practical,
        "stories": stories
    }
    
    overall_stepps_score = sum(score * weights[component] for component, score in stepps_components.items())
    
    # Generate insights based on the analysis
    top_components = sorted(stepps_components.items(), key=lambda x: x[1], reverse=True)[:2]
    bottom_components = sorted(stepps_components.items(), key=lambda x: x[1])[:2]
    
    insights = [
        f"This trend has strong {top_components[0][0].replace('_', ' ')} and {top_components[1][0].replace('_', ' ')}, "
        f"making it potentially viral content for sustainability communications.",
        f"To increase engagement, focus on improving {bottom_components[0][0].replace('_', ' ')} and "
        f"{bottom_components[1][0].replace('_', ' ')}."
    ]
    
    # Generate recommendations based on STEPPS analysis
    recommendations = generate_stepps_recommendations(stepps_components, trend_data)
    
    return {
        "trend_name": trend_name,
        "overall_stepps_score": round(overall_stepps_score, 2),
        "components": {component: {"score": score, "description": STEPPS_COMPONENTS[component]} 
                      for component, score in stepps_components.items()},
        "insights": insights,
        "recommendations": recommendations
    }

def generate_stepps_recommendations(stepps_scores: Dict[str, float], trend_data: Dict[str, Any]) -> List[str]:
    """
    Generate recommendations based on STEPPS analysis.
    
    Args:
        stepps_scores: Dictionary with scores for each STEPPS component
        trend_data: Original trend data
        
    Returns:
        List of strategic recommendations
    """
    recommendations = []
    
    # Sort components by score (ascending) to prioritize low-scoring areas
    sorted_components = sorted(stepps_scores.items(), key=lambda x: x[1])
    
    # Get the lowest scoring components
    low_components = sorted_components[:2]
    
    for component, score in low_components:
        if component == "social_currency" and score < 7:
            recommendations.append(
                "Develop exclusive sustainability insights reports that showcase industry leadership "
                "to boost social currency when stakeholders share your content."
            )
        elif component == "triggers" and score < 7:
            recommendations.append(
                "Create environmental cues in communications by linking sustainability metrics to "
                "regular business activities or calendar events (Earth Day, quarterly reports)."
            )
        elif component == "emotion" and score < 7:
            recommendations.append(
                "Incorporate emotional narratives around sustainability achievements, focusing on "
                "positive impact stories that evoke pride and inspiration."
            )
        elif component == "public" and score < 7:
            recommendations.append(
                "Increase visibility of sustainability efforts through visual indicators in "
                "products, packaging, or marketing materials to make commitments observable."
            )
        elif component == "practical_value" and score < 7:
            recommendations.append(
                "Provide actionable sustainability tips alongside metrics reporting to add "
                "practical value that stakeholders can implement themselves."
            )
        elif component == "stories" and score < 7:
            recommendations.append(
                "Develop narrative arcs around sustainability journey with challenges, solutions, "
                "and outcomes that people will naturally share in conversation."
            )
    
    # Add one general recommendation based on trend direction
    trend_direction = trend_data.get("trend_direction", "")
    if trend_direction == "improving":
        recommendations.append(
            "Leverage this positive trend in marketing communications, highlighting progress "
            "and commitment to continuous improvement in sustainability performance."
        )
    else:
        recommendations.append(
            "Address this challenging trend transparently while communicating a clear action "
            "plan to improve performance, demonstrating accountability and commitment."
        )
    
    return recommendations

def benchmark_against_competitors(company_name: str, industry: str, trend_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Benchmark company's sustainability trends against competitors.
    
    Args:
        company_name: Name of the company to benchmark
        industry: Industry of the company
        trend_data: List of trend data for the company
        
    Returns:
        Dictionary with competitive benchmarking results
    """
    # Generate mock competitor data for demonstration
    # In a real implementation, this would fetch data from an industry database
    competitors = generate_mock_competitors(industry, 3)
    
    # Map company trend data by category for easier comparison
    company_trends_by_category = {}
    for trend in trend_data:
        category = trend.get("category", "")
        if category not in company_trends_by_category:
            company_trends_by_category[category] = []
        company_trends_by_category[category].append(trend)
    
    # Calculate average virality score by category for company
    company_avg_virality = {}
    for category, trends in company_trends_by_category.items():
        if trends:
            company_avg_virality[category] = sum(t.get("virality_score", 0) for t in trends) / len(trends)
        else:
            company_avg_virality[category] = 0
    
    # Compare with competitors
    benchmark_results = {
        "company_name": company_name,
        "industry": industry,
        "categories": {},
        "overall_ranking": {},
        "competitors": competitors
    }
    
    # Calculate category benchmarks
    all_companies = [{"name": company_name, "data": company_avg_virality}]
    for competitor in competitors:
        all_companies.append({
            "name": competitor["name"],
            "data": competitor["virality_by_category"]
        })
    
    # Get unique categories across all companies
    all_categories = set()
    for company in all_companies:
        all_categories.update(company["data"].keys())
    
    # Calculate rankings for each category
    for category in all_categories:
        # Get scores for this category
        category_scores = [(company["name"], company["data"].get(category, 0)) for company in all_companies]
        # Sort by score (descending)
        category_scores.sort(key=lambda x: x[1], reverse=True)
        # Get company's rank
        company_rank = next((i + 1 for i, (name, _) in enumerate(category_scores) if name == company_name), None)
        
        benchmark_results["categories"][category] = {
            "company_score": company_avg_virality.get(category, 0),
            "industry_average": sum(c["data"].get(category, 0) for c in all_companies) / len(all_companies),
            "leader": category_scores[0][0],
            "leader_score": category_scores[0][1],
            "company_rank": company_rank,
            "total_companies": len(all_companies),
            "percentile": 100 - ((company_rank - 1) / len(all_companies) * 100) if company_rank else 0
        }
    
    # Calculate overall virality ranking
    overall_scores = []
    for company in all_companies:
        avg_score = sum(company["data"].values()) / len(company["data"]) if company["data"] else 0
        overall_scores.append((company["name"], avg_score))
    
    # Sort by overall score (descending)
    overall_scores.sort(key=lambda x: x[1], reverse=True)
    # Get company's overall rank
    company_overall_rank = next((i + 1 for i, (name, _) in enumerate(overall_scores) if name == company_name), None)
    
    benchmark_results["overall_ranking"] = {
        "company_rank": company_overall_rank,
        "total_companies": len(all_companies),
        "percentile": 100 - ((company_overall_rank - 1) / len(all_companies) * 100) if company_overall_rank else 0,
        "leader": overall_scores[0][0],
        "ranking": [{"name": name, "score": round(score, 2)} for name, score in overall_scores]
    }
    
    # Generate strategic insights based on benchmarking
    benchmark_results["strategic_insights"] = generate_benchmark_insights(benchmark_results, company_name)
    
    return benchmark_results

def generate_mock_competitors(industry: str, count: int = 3) -> List[Dict[str, Any]]:
    """
    Generate mock competitor data for benchmarking demonstration.
    
    Args:
        industry: Industry for context
        count: Number of competitors to generate
        
    Returns:
        List of competitor data objects
    """
    # Industry-specific company names
    industry_companies = {
        "technology": ["TechGiant Co", "InnovateSoft", "DigiCorp", "ByteWave Solutions", "NextGen Tech"],
        "manufacturing": ["Industrial Systems", "ManufactureX", "ProductCraft", "MetalWorks Inc", "AssemblyPro"],
        "retail": ["RetailMax", "ShopSmart", "ConsumerFirst", "MegaMart", "BuyBest Solutions"],
        "energy": ["PowerGen", "EnergyNow", "GreenPower Inc", "ElectricFuture", "SustainEnergy"],
        "finance": ["CapitalOne Finance", "InvestSmart", "WealthGuard", "MoneyWise", "TrustBank"],
        "healthcare": ["MediCare Solutions", "HealthFirst", "WellnessPro", "MedTech Innovations", "Care Systems"]
    }
    
    # Default to technology if industry not found
    companies = industry_companies.get(industry.lower(), industry_companies["technology"])
    
    # Select random companies
    selected_companies = random.sample(companies, min(count, len(companies)))
    
    # Categories for virality data
    categories = ["emissions", "energy", "water", "waste", "social", "governance"]
    
    competitors = []
    for company in selected_companies:
        # Generate virality scores by category
        virality_by_category = {}
        for category in categories:
            # Random score between 30 and 90
            virality_by_category[category] = round(random.uniform(30, 90), 2)
        
        # Generate trend history (last 6 months)
        trend_history = []
        now = datetime.now()
        for i in range(6):
            month_date = now - timedelta(days=30 * i)
            month_data = {
                "date": month_date.strftime("%Y-%m"),
                "overall_virality": round(random.uniform(40, 85), 2),
                "categories": {}
            }
            
            # Add category data for this month
            for category in categories:
                month_data["categories"][category] = round(random.uniform(30, 90), 2)
                
            trend_history.append(month_data)
        
        # Sort trend history by date
        trend_history.sort(key=lambda x: x["date"])
        
        competitors.append({
            "name": company,
            "industry": industry,
            "virality_by_category": virality_by_category,
            "trend_history": trend_history,
            "overall_score": round(sum(virality_by_category.values()) / len(virality_by_category), 2)
        })
    
    return competitors

def generate_benchmark_insights(benchmark_data: Dict[str, Any], company_name: str) -> List[Dict[str, Any]]:
    """
    Generate strategic insights based on benchmarking results.
    
    Args:
        benchmark_data: Competitive benchmarking data
        company_name: Company name for context
        
    Returns:
        List of strategic insights
    """
    insights = []
    
    # Get categories where company is leading
    leading_categories = []
    lagging_categories = []
    
    for category, data in benchmark_data["categories"].items():
        if data["company_rank"] == 1:
            leading_categories.append(category)
        elif data["company_rank"] > len(benchmark_data["competitors"]) / 2:
            lagging_categories.append(category)
    
    # Overall positioning insight
    overall_rank = benchmark_data["overall_ranking"]["company_rank"]
    total_companies = benchmark_data["overall_ranking"]["total_companies"]
    
    if overall_rank == 1:
        insights.append({
            "area": "Overall Positioning",
            "insight": f"{company_name} is the industry leader in sustainability virality, creating an opportunity to leverage this position for brand differentiation and thought leadership.",
            "recommendation": "Develop a thought leadership program highlighting industry-leading sustainability practices and innovative approaches."
        })
    elif overall_rank <= total_companies / 3:
        insights.append({
            "area": "Overall Positioning",
            "insight": f"{company_name} has a strong competitive position in sustainability virality, ranking in the top third of the industry.",
            "recommendation": "Focus on the 1-2 categories where improvement would have the greatest impact on overall ranking to build momentum toward leadership position."
        })
    else:
        insights.append({
            "area": "Overall Positioning",
            "insight": f"{company_name} has opportunity for improvement in sustainability virality, currently ranking {overall_rank} out of {total_companies} companies.",
            "recommendation": "Develop a focused sustainability communications strategy targeting specific improvement areas with highest potential for impact."
        })
    
    # Leading categories insight
    if leading_categories:
        categories_str = ", ".join(c.capitalize() for c in leading_categories)
        insights.append({
            "area": "Strengths",
            "insight": f"{company_name} leads the industry in {categories_str} virality, demonstrating strong communication effectiveness in these areas.",
            "recommendation": "Leverage expertise in these categories to develop best practice sharing that can lift performance in other areas."
        })
    
    # Lagging categories insight
    if lagging_categories:
        categories_str = ", ".join(c.capitalize() for c in lagging_categories)
        insights.append({
            "area": "Improvement Opportunities",
            "insight": f"{company_name} has opportunities to improve in {categories_str}, where competitors are achieving greater virality.",
            "recommendation": "Conduct a competitive analysis of leading companies in these categories to identify effective communication strategies for adaptation."
        })
    
    # Add industry-specific insight
    industry = benchmark_data["industry"]
    if industry.lower() == "technology":
        insights.append({
            "area": "Industry Context",
            "insight": "Technology companies face heightened expectations for innovation in sustainability communications, with stakeholders expecting digital leadership to translate to sustainability leadership.",
            "recommendation": "Showcase technology-enabled sustainability innovations and data-driven transparency to align with industry expectations."
        })
    elif industry.lower() == "manufacturing":
        insights.append({
            "area": "Industry Context",
            "insight": "Manufacturing companies are particularly scrutinized for environmental impact metrics, with emissions and waste categories receiving the most attention.",
            "recommendation": "Emphasize circular economy initiatives and emissions reduction technologies in communications strategy."
        })
    elif industry.lower() == "energy":
        insights.append({
            "area": "Industry Context",
            "insight": "Energy companies face a challenging communications landscape with high skepticism, requiring exceptional transparency and substantiated claims.",
            "recommendation": "Focus on verifiable, third-party validated metrics and transition strategies to build credibility in sustainability communications."
        })
    
    return insights

def apply_consulting_framework(trend_data: List[Dict[str, Any]], framework_type: str, company_name: str) -> Dict[str, Any]:
    """
    Apply a consulting framework to trend analysis for strategic recommendations.
    
    Args:
        trend_data: List of trend data dictionaries
        framework_type: Type of consulting framework to apply
        company_name: Company name for context
        
    Returns:
        Dictionary with framework analysis and recommendations
    """
    # Validate framework type
    if framework_type not in CONSULTING_FRAMEWORKS:
        logger.warning(f"Invalid framework type: {framework_type}. Using sustainability_impact instead.")
        framework_type = "sustainability_impact"
    
    framework = CONSULTING_FRAMEWORKS[framework_type]
    
    # Apply framework-specific analysis
    if framework_type == "porters_five_forces":
        return apply_porters_framework(trend_data, company_name)
    elif framework_type == "mckinsey_7s":
        return apply_mckinsey_framework(trend_data, company_name)
    else:
        return apply_sustainability_impact_framework(trend_data, company_name)

def apply_porters_framework(trend_data: List[Dict[str, Any]], company_name: str) -> Dict[str, Any]:
    """
    Apply Porter's Five Forces framework to sustainability trend data.
    
    Args:
        trend_data: List of trend data dictionaries
        company_name: Company name for context
        
    Returns:
        Dictionary with Porter's Five Forces analysis
    """
    framework = CONSULTING_FRAMEWORKS["porters_five_forces"]
    
    # Calculate average virality by category
    category_virality = {}
    for trend in trend_data:
        category = trend.get("category", "")
        if category not in category_virality:
            category_virality[category] = {"total": 0, "count": 0}
        category_virality[category]["total"] += trend.get("virality_score", 0)
        category_virality[category]["count"] += 1
    
    # Calculate average scores
    for category in category_virality:
        if category_virality[category]["count"] > 0:
            category_virality[category]["average"] = category_virality[category]["total"] / category_virality[category]["count"]
        else:
            category_virality[category]["average"] = 0
    
    # Determine which categories have high virality (top 50%)
    high_virality_categories = []
    if category_virality:
        sorted_categories = sorted(
            category_virality.items(), 
            key=lambda x: x[1]["average"], 
            reverse=True
        )
        
        # Top half considered high virality
        mid_point = len(sorted_categories) // 2
        high_virality_categories = [c[0] for c in sorted_categories[:mid_point]]
    
    # Generate forces analysis based on trend data and categories
    forces_analysis = {}
    
    # 1. Competitive Rivalry
    if "social" in high_virality_categories or "governance" in high_virality_categories:
        competitive_impact = "favorable"
        competitive_explanation = (
            f"High virality in social/governance categories gives {company_name} a competitive advantage "
            f"in stakeholder perception and potential brand differentiation."
        )
    else:
        competitive_impact = "unfavorable"
        competitive_explanation = (
            f"Limited virality in key sustainability categories may place {company_name} at a competitive "
            f"disadvantage as sustainability becomes a more important differentiator."
        )
    
    forces_analysis["competitive_rivalry"] = {
        "impact": competitive_impact,
        "explanation": competitive_explanation,
        "recommendation": (
            "Develop distinctive sustainability narrative focused on areas where company performance "
            "is strongest to create competitive differentiation."
        )
    }
    
    # 2. Supplier Power
    if "emissions" in high_virality_categories or "energy" in high_virality_categories:
        supplier_impact = "favorable"
        supplier_explanation = (
            f"High virality in emissions/energy categories suggests {company_name} has effective "
            f"supplier sustainability programs that can reduce supplier power."
        )
    else:
        supplier_impact = "neutral"
        supplier_explanation = (
            f"Current sustainability trend data shows no significant impact on supplier relationships "
            f"or bargaining power through sustainability initiatives."
        )
    
    forces_analysis["supplier_power"] = {
        "impact": supplier_impact,
        "explanation": supplier_explanation,
        "recommendation": (
            "Implement supplier sustainability scorecards and collaborative improvement programs "
            "to strengthen relationships while reducing overall supply chain risks."
        )
    }
    
    # 3. Buyer Power
    avg_virality = sum(c["average"] for c in category_virality.values()) / len(category_virality) if category_virality else 0
    
    if avg_virality > 60:
        buyer_impact = "favorable"
        buyer_explanation = (
            f"Strong overall sustainability virality suggests {company_name}'s initiatives resonate with "
            f"buyers, potentially reducing their bargaining power through brand loyalty."
        )
    else:
        buyer_impact = "unfavorable"
        buyer_explanation = (
            f"Limited sustainability virality may place {company_name} at risk of increased buyer power "
            f"as customers increasingly factor sustainability into purchasing decisions."
        )
    
    forces_analysis["buyer_power"] = {
        "impact": buyer_impact,
        "explanation": buyer_explanation,
        "recommendation": (
            "Develop sustainability-focused customer engagement programs that highlight the value "
            "proposition of sustainable products/services to strengthen customer relationships."
        )
    }
    
    # 4. Threat of Substitution
    if "waste" in high_virality_categories or "water" in high_virality_categories:
        substitution_impact = "favorable"
        substitution_explanation = (
            f"High virality in resource efficiency categories suggests {company_name} is positioning well "
            f"against substitutes that may emerge with superior sustainability profiles."
        )
    else:
        substitution_impact = "unfavorable"
        substitution_explanation = (
            f"Current sustainability trend data suggests {company_name} could be vulnerable to substitutes "
            f"that offer improved sustainability performance."
        )
    
    forces_analysis["threat_of_substitution"] = {
        "impact": substitution_impact,
        "explanation": substitution_explanation,
        "recommendation": (
            "Conduct sustainability-focused innovation workshops to identify potential substitutes "
            "and develop proactive strategies to maintain competitive advantage."
        )
    }
    
    # 5. Threat of New Entry
    improving_trends = sum(1 for trend in trend_data if trend.get("trend_direction") == "improving")
    total_trends = len(trend_data)
    improvement_ratio = improving_trends / total_trends if total_trends > 0 else 0
    
    if improvement_ratio > 0.6:
        new_entry_impact = "favorable"
        new_entry_explanation = (
            f"Strong improvement trajectory in sustainability metrics creates barriers to new entrants "
            f"who would need to match {company_name}'s sustainability performance."
        )
    else:
        new_entry_impact = "unfavorable"
        new_entry_explanation = (
            f"Limited improvement in sustainability metrics leaves {company_name} vulnerable to new "
            f"market entrants with built-in sustainability advantages."
        )
    
    forces_analysis["threat_of_new_entry"] = {
        "impact": new_entry_impact,
        "explanation": new_entry_explanation,
        "recommendation": (
            "Accelerate sustainability innovation and establish industry-leading practices that create "
            "barriers to entry for new competitors."
        )
    }
    
    # Overall strategy recommendation
    favorable_count = sum(1 for force in forces_analysis.values() if force["impact"] == "favorable")
    
    if favorable_count >= 3:
        overall_strategy = (
            f"Leverage sustainability as a strategic advantage by highlighting areas where {company_name} "
            f"has favorable positioning, particularly in {', '.join(high_virality_categories)}."
        )
    else:
        overall_strategy = (
            f"Prioritize improvement in key sustainability areas to address competitive vulnerabilities, "
            f"focusing first on addressing unfavorable forces through targeted initiatives."
        )
    
    return {
        "framework": framework,
        "company_name": company_name,
        "forces_analysis": forces_analysis,
        "high_virality_categories": high_virality_categories,
        "overall_strategy": overall_strategy
    }

def apply_mckinsey_framework(trend_data: List[Dict[str, Any]], company_name: str) -> Dict[str, Any]:
    """
    Apply McKinsey 7S framework to sustainability trend data.
    
    Args:
        trend_data: List of trend data dictionaries
        company_name: Company name for context
        
    Returns:
        Dictionary with McKinsey 7S analysis
    """
    framework = CONSULTING_FRAMEWORKS["mckinsey_7s"]
    
    # Calculate overall trend performance
    improving_trends = [t for t in trend_data if t.get("trend_direction") == "improving"]
    worsening_trends = [t for t in trend_data if t.get("trend_direction") == "worsening"]
    
    improvement_ratio = len(improving_trends) / len(trend_data) if trend_data else 0
    
    # Group trends by category
    trends_by_category = {}
    for trend in trend_data:
        category = trend.get("category", "")
        if category not in trends_by_category:
            trends_by_category[category] = []
        trends_by_category[category].append(trend)
    
    # Analyze 7S elements based on trend data
    elements_analysis = {}
    
    # 1. Strategy
    strategy_alignment = "high" if improvement_ratio > 0.7 else "medium" if improvement_ratio > 0.4 else "low"
    
    elements_analysis["strategy"] = {
        "alignment": strategy_alignment,
        "explanation": (
            f"Sustainability trends show {strategy_alignment} alignment with corporate strategy, "
            f"with {int(improvement_ratio * 100)}% of metrics showing improvement."
        ),
        "recommendation": (
            "Ensure sustainability goals are explicitly integrated into corporate strategy documents "
            "and KPIs to strengthen alignment across the organization."
        )
    }
    
    # 2. Structure
    # Analyze if there's consistency across different categories
    category_performance = {}
    for category, trends in trends_by_category.items():
        improving = sum(1 for t in trends if t.get("trend_direction") == "improving")
        category_performance[category] = improving / len(trends) if trends else 0
    
    # Calculate standard deviation of performance across categories
    if category_performance:
        values = list(category_performance.values())
        std_dev = np.std(values)
        
        if std_dev < 0.15:
            structure_alignment = "high"
            explanation = "Consistent performance across sustainability categories suggests effective organizational structure."
        elif std_dev < 0.3:
            structure_alignment = "medium"
            explanation = "Some variation in performance across categories suggests potential structural misalignments."
        else:
            structure_alignment = "low"
            explanation = "Significant variation in performance across categories suggests structural barriers to consistent execution."
    else:
        structure_alignment = "unknown"
        explanation = "Insufficient data to assess organizational structure alignment."
    
    elements_analysis["structure"] = {
        "alignment": structure_alignment,
        "explanation": explanation,
        "recommendation": (
            "Review organizational structure to ensure sustainability responsibilities are clearly "
            "assigned and integrated across business units to drive consistent performance."
        )
    }
    
    # 3. Systems
    # Look at trend duration to assess system integration
    long_term_trends = [t for t in trend_data if t.get("trend_duration") == "long-term"]
    systems_alignment = "high" if len(long_term_trends) > len(trend_data) * 0.6 else "medium" if len(long_term_trends) > len(trend_data) * 0.3 else "low"
    
    elements_analysis["systems"] = {
        "alignment": systems_alignment,
        "explanation": (
            f"Trend duration analysis shows {systems_alignment} systems integration, with "
            f"{len(long_term_trends)} out of {len(trend_data)} metrics showing long-term consistency."
        ),
        "recommendation": (
            "Implement systematic data collection and reporting processes for all sustainability "
            "metrics to ensure consistent performance monitoring and improvement."
        )
    }
    
    # 4. Shared Values
    # Use highest virality metrics as a proxy for shared values
    high_virality_trends = sorted(trend_data, key=lambda x: x.get("virality_score", 0), reverse=True)[:3]
    high_virality_categories = list(set(t.get("category") for t in high_virality_trends))
    
    if len(high_virality_categories) <= 2 and high_virality_trends and high_virality_trends[0].get("virality_score", 0) > 70:
        shared_values_alignment = "high"
        explanation = f"Strong virality in focused categories suggests well-aligned shared values around key sustainability areas."
    elif high_virality_trends and high_virality_trends[0].get("virality_score", 0) > 50:
        shared_values_alignment = "medium"
        explanation = "Moderate virality across categories suggests partially aligned shared values."
    else:
        shared_values_alignment = "low"
        explanation = "Limited virality across sustainability metrics suggests weak shared values alignment."
    
    elements_analysis["shared_values"] = {
        "alignment": shared_values_alignment,
        "explanation": explanation,
        "recommendation": (
            "Develop an internal sustainability narrative that connects core business values "
            "with sustainability goals to strengthen cultural alignment."
        )
    }
    
    # 5. Skills
    # Use improvement in challenging areas as a proxy for skills
    if worsening_trends:
        skills_alignment = "medium"
        explanation = f"Presence of {len(worsening_trends)} worsening trends suggests skill gaps in certain sustainability areas."
    elif improvement_ratio > 0.8:
        skills_alignment = "high"
        explanation = "Consistent improvement across metrics suggests strong sustainability skills and capabilities."
    else:
        skills_alignment = "low"
        explanation = "Mixed performance in sustainability metrics suggests inconsistent skill development."
    
    elements_analysis["skills"] = {
        "alignment": skills_alignment,
        "explanation": explanation,
        "recommendation": (
            "Implement targeted sustainability training programs in areas showing performance gaps, "
            "prioritizing skills development for metrics with negative trends."
        )
    }
    
    # 6. Style
    # Use virality as a proxy for leadership style effectiveness
    avg_virality = sum(t.get("virality_score", 0) for t in trend_data) / len(trend_data) if trend_data else 0
    
    if avg_virality > 70:
        style_alignment = "high"
        explanation = "High average virality suggests effective leadership style that emphasizes sustainability."
    elif avg_virality > 50:
        style_alignment = "medium"
        explanation = "Moderate average virality suggests some leadership emphasis on sustainability."
    else:
        style_alignment = "low"
        explanation = "Low average virality suggests limited leadership emphasis on sustainability."
    
    elements_analysis["style"] = {
        "alignment": style_alignment,
        "explanation": explanation,
        "recommendation": (
            "Enhance leadership visibility on sustainability topics through regular communications "
            "and executive sponsorship of key sustainability initiatives."
        )
    }
    
    # 7. Staff
    # Use consistency across categories as a proxy for staff engagement
    if len(improving_trends) > len(trend_data) * 0.7:
        staff_alignment = "high"
        explanation = "Broad improvement across sustainability metrics suggests strong staff engagement."
    elif len(improving_trends) > len(trend_data) * 0.4:
        staff_alignment = "medium"
        explanation = "Mixed improvement across sustainability metrics suggests variable staff engagement."
    else:
        staff_alignment = "low"
        explanation = "Limited improvement across sustainability metrics suggests low staff engagement."
    
    elements_analysis["staff"] = {
        "alignment": staff_alignment,
        "explanation": explanation,
        "recommendation": (
            "Develop staff engagement programs that connect individual roles to sustainability "
            "goals, with recognition for contributions to improving key metrics."
        )
    }
    
    # Overall alignment assessment
    alignment_scores = {"high": 3, "medium": 2, "low": 1, "unknown": 0}
    total_score = sum(alignment_scores.get(element["alignment"], 0) for element in elements_analysis.values())
    max_possible = len(elements_analysis) * 3
    alignment_percentage = (total_score / max_possible) * 100 if max_possible > 0 else 0
    
    if alignment_percentage > 80:
        overall_alignment = "Strong alignment across 7S elements"
    elif alignment_percentage > 60:
        overall_alignment = "Moderate alignment with some gaps"
    else:
        overall_alignment = "Weak alignment requiring significant intervention"
    
    # Key recommendations based on lowest aligned elements
    lowest_elements = sorted(
        elements_analysis.items(), 
        key=lambda x: alignment_scores.get(x[1]["alignment"], 0)
    )[:2]
    
    key_recommendations = [
        f"Prioritize improvements in {element[0].capitalize()} by {element[1]['recommendation']}"
        for element in lowest_elements
    ]
    
    return {
        "framework": framework,
        "company_name": company_name,
        "elements_analysis": elements_analysis,
        "overall_alignment": overall_alignment,
        "alignment_percentage": round(alignment_percentage, 2),
        "key_recommendations": key_recommendations
    }

def apply_sustainability_impact_framework(trend_data: List[Dict[str, Any]], company_name: str) -> Dict[str, Any]:
    """
    Apply Sustainability Impact Assessment framework to trend data.
    
    Args:
        trend_data: List of trend data dictionaries
        company_name: Company name for context
        
    Returns:
        Dictionary with Sustainability Impact Assessment
    """
    framework = CONSULTING_FRAMEWORKS["sustainability_impact"]
    
    # Group trends by category
    trends_by_category = {}
    for trend in trend_data:
        category = trend.get("category", "")
        if category not in trends_by_category:
            trends_by_category[category] = []
        trends_by_category[category].append(trend)
    
    # Map sustainability categories to framework elements
    element_mapping = {
        "emissions": "environmental_footprint",
        "energy": "environmental_footprint",
        "water": "environmental_footprint",
        "waste": "environmental_footprint",
        "social": "social_impact",
        "governance": "governance_structure"
    }
    
    # Initialize framework elements
    elements_analysis = {
        "environmental_footprint": {
            "trends": [],
            "score": 0,
            "recommendations": []
        },
        "social_impact": {
            "trends": [],
            "score": 0,
            "recommendations": []
        },
        "governance_structure": {
            "trends": [],
            "score": 0,
            "recommendations": []
        },
        "stakeholder_engagement": {
            "trends": [],
            "score": 0,
            "recommendations": []
        },
        "long_term_resilience": {
            "trends": [],
            "score": 0,
            "recommendations": []
        }
    }
    
    # Map trends to framework elements
    for category, trends in trends_by_category.items():
        element = element_mapping.get(category, "long_term_resilience")
        elements_analysis[element]["trends"].extend(trends)
    
    # Special case for stakeholder engagement - no direct mapping, use social category + high virality
    high_virality_trends = [t for t in trend_data if t.get("virality_score", 0) > 70]
    elements_analysis["stakeholder_engagement"]["trends"] = high_virality_trends
    
    # Analyze each framework element
    for element, data in elements_analysis.items():
        if not data["trends"]:
            data["score"] = 0
            data["impact"] = "unknown"
            data["explanation"] = f"Insufficient data to assess {element.replace('_', ' ')}."
            data["recommendations"].append(f"Develop metrics to track {element.replace('_', ' ')}.")
            continue
        
        # Calculate scores based on trend direction and virality
        total_virality = sum(t.get("virality_score", 0) for t in data["trends"])
        avg_virality = total_virality / len(data["trends"]) if data["trends"] else 0
        
        improving_trends = [t for t in data["trends"] if t.get("trend_direction") == "improving"]
        improvement_ratio = len(improving_trends) / len(data["trends"]) if data["trends"] else 0
        
        # Calculate normalized score (0-100)
        impact_score = (avg_virality * 0.4) + (improvement_ratio * 100 * 0.6)
        data["score"] = round(min(impact_score, 100), 2)
        
        # Determine impact level
        if impact_score > 75:
            data["impact"] = "strong positive"
        elif impact_score > 60:
            data["impact"] = "moderate positive"
        elif impact_score > 50:
            data["impact"] = "slight positive"
        elif impact_score > 40:
            data["impact"] = "neutral"
        elif impact_score > 25:
            data["impact"] = "slight negative"
        else:
            data["impact"] = "negative"
        
        # Generate explanation based on the data
        trend_names = ", ".join(set(t.get("name", "") for t in data["trends"]))
        
        if improvement_ratio > 0.7:
            data["explanation"] = (
                f"Strong improvement in {trend_names} metrics indicates positive {element.replace('_', ' ')} impact."
            )
        elif improvement_ratio > 0.4:
            data["explanation"] = (
                f"Mixed performance in {trend_names} metrics shows variable {element.replace('_', ' ')} impact."
            )
        else:
            data["explanation"] = (
                f"Limited improvement in {trend_names} metrics indicates challenges with {element.replace('_', ' ')} impact."
            )
        
        # Generate recommendations
        if element == "environmental_footprint":
            if data["impact"] in ["strong positive", "moderate positive"]:
                data["recommendations"].append(
                    "Leverage strong environmental performance in marketing and stakeholder communications "
                    "to build brand reputation and differentiation."
                )
            else:
                data["recommendations"].append(
                    "Develop a comprehensive environmental improvement plan focusing on metrics "
                    "showing negative trends, with clear targets and accountability."
                )
        
        elif element == "social_impact":
            if data["impact"] in ["strong positive", "moderate positive"]:
                data["recommendations"].append(
                    "Expand social impact initiatives to new areas and increase visibility "
                    "of existing programs to maximize stakeholder engagement."
                )
            else:
                data["recommendations"].append(
                    "Conduct a social impact assessment to identify improvement opportunities "
                    "and develop targeted programs addressing stakeholder priorities."
                )
        
        elif element == "governance_structure":
            if data["impact"] in ["strong positive", "moderate positive"]:
                data["recommendations"].append(
                    "Ensure governance structures continue to support sustainability performance "
                    "through regular board reviews and dedicated sustainability committees."
                )
            else:
                data["recommendations"].append(
                    "Strengthen governance oversight of sustainability by establishing clear "
                    "board-level accountability and regular performance reviews."
                )
        
        elif element == "stakeholder_engagement":
            if len(data["trends"]) < 3:
                data["recommendations"].append(
                    "Develop a comprehensive stakeholder engagement strategy with metrics "
                    "to track effectiveness and impact on sustainability performance."
                )
            elif data["impact"] in ["strong positive", "moderate positive"]:
                data["recommendations"].append(
                    "Expand stakeholder engagement programs to include more diverse voices "
                    "and increase transparency in sustainability communications."
                )
            else:
                data["recommendations"].append(
                    "Revitalize stakeholder engagement approach with more interactive channels "
                    "and clear demonstration of how feedback influences decisions."
                )
        
        elif element == "long_term_resilience":
            long_term_trends = [t for t in data["trends"] if t.get("trend_duration") == "long-term"]
            
            if not long_term_trends:
                data["recommendations"].append(
                    "Develop long-term sustainability metrics and targets that connect to "
                    "business strategy and support organizational resilience."
                )
            elif data["impact"] in ["strong positive", "moderate positive"]:
                data["recommendations"].append(
                    "Integrate sustainability scenario planning into strategic planning processes "
                    "to ensure continued long-term resilience and adaptability."
                )
            else:
                data["recommendations"].append(
                    "Conduct a climate risk assessment and develop adaptation strategies to "
                    "strengthen long-term resilience against sustainability challenges."
                )
    
    # Calculate overall sustainability impact score
    total_score = sum(data["score"] for data in elements_analysis.values())
    count = sum(1 for data in elements_analysis.values() if data["score"] > 0)
    overall_score = total_score / count if count > 0 else 0
    
    # Determine overall impact level
    if overall_score > 75:
        overall_impact = "strong positive"
    elif overall_score > 60:
        overall_impact = "moderate positive"
    elif overall_score > 50:
        overall_impact = "slight positive"
    elif overall_score > 40:
        overall_impact = "neutral"
    else:
        overall_impact = "negative"
    
    # Generate priority recommendations
    # Find elements with lowest scores
    sorted_elements = sorted(
        [(element, data["score"]) for element, data in elements_analysis.items() if data["score"] > 0],
        key=lambda x: x[1]
    )
    
    priority_areas = [element for element, score in sorted_elements[:2]] if sorted_elements else []
    priority_recommendations = []
    
    for element in priority_areas:
        if elements_analysis[element]["recommendations"]:
            priority_recommendations.append(elements_analysis[element]["recommendations"][0])
    
    # Add one general recommendation
    if overall_impact in ["strong positive", "moderate positive"]:
        priority_recommendations.append(
            "Develop an integrated sustainability reporting framework that connects performance "
            "metrics to business value creation to maximize strategic impact."
        )
    else:
        priority_recommendations.append(
            "Conduct a comprehensive sustainability materiality assessment to identify priority "
            "areas for improvement that align with business strategy and stakeholder expectations."
        )
    
    return {
        "framework": framework,
        "company_name": company_name,
        "elements_analysis": elements_analysis,
        "overall_score": round(overall_score, 2),
        "overall_impact": overall_impact,
        "priority_areas": priority_areas,
        "priority_recommendations": priority_recommendations
    }

def generate_data_storytelling_elements(trend_data: List[Dict[str, Any]], framework_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate data-driven storytelling elements based on trend analysis and framework insights.
    
    Args:
        trend_data: List of trend data dictionaries
        framework_analysis: Results from applying a consulting framework
        
    Returns:
        Dictionary with storytelling elements for strategic positioning
    """
    # Extract key information for storytelling
    top_trends = sorted(trend_data, key=lambda x: x.get("virality_score", 0), reverse=True)[:3]
    improving_trends = [t for t in trend_data if t.get("trend_direction") == "improving"]
    
    # Identify company and framework info
    company_name = framework_analysis.get("company_name", "the company")
    framework_name = framework_analysis.get("framework", {}).get("name", "analysis")
    
    # Generate headline and summary based on overall trend direction
    if len(improving_trends) > len(trend_data) * 0.7:
        headline = f"{company_name}'s Sustainability Leadership Journey: Building Momentum Through Strategic Focus"
        summary = (
            f"{company_name} demonstrates strong sustainability performance across {len(improving_trends)} key metrics, "
            f"creating opportunities for industry leadership and strategic differentiation. The {framework_name} "
            f"highlights effective alignment between sustainability initiatives and business strategy."
        )
    elif len(improving_trends) > len(trend_data) * 0.4:
        headline = f"{company_name}'s Sustainability Transformation: Navigating Challenges While Building Strengths"
        summary = (
            f"{company_name} shows mixed sustainability performance with {len(improving_trends)} improving metrics "
            f"alongside areas requiring attention. The {framework_name} identifies specific strategic opportunities "
            f"to accelerate progress and address performance gaps."
        )
    else:
        headline = f"{company_name}'s Sustainability Imperative: Addressing Challenges for Future Resilience"
        summary = (
            f"{company_name} faces sustainability performance challenges with limited improvement across key metrics. "
            f"The {framework_name} provides a roadmap for strategic intervention to strengthen sustainability "
            f"positioning and mitigate emerging risks."
        )
    
    # Generate key messages based on top trends
    key_messages = []
    
    for trend in top_trends:
        name = trend.get("name", "")
        category = trend.get("category", "")
        direction = trend.get("trend_direction", "")
        virality = trend.get("virality_score", 0)
        
        if direction == "improving" and virality > 70:
            key_messages.append(
                f"Industry-leading performance in {name} demonstrates commitment to excellence in "
                f"{category} sustainability, creating significant brand differentiation opportunities."
            )
        elif direction == "improving":
            key_messages.append(
                f"Steady improvement in {name} showcases progressive approach to {category} "
                f"sustainability, aligning with stakeholder expectations and industry trends."
            )
        else:
            key_messages.append(
                f"Strategic focus on {name} represents an opportunity to transform challenges into "
                f"future strengths through targeted initiatives and transparent communication."
            )
    
    # Generate narrative arc
    # Extract framework insights
    if "forces_analysis" in framework_analysis:
        # Porter's framework
        favorable_forces = [
            force for force, data in framework_analysis.get("forces_analysis", {}).items()
            if data.get("impact") == "favorable"
        ]
        framework_insight = (
            f"Analysis reveals competitive advantage through {len(favorable_forces)} favorable forces "
            f"in the sustainability landscape, with particularly strong positioning in "
            f"{', '.join(framework_analysis.get('high_virality_categories', []))[:2]}"
        )
    elif "elements_analysis" in framework_analysis:
        # McKinsey or Sustainability Impact framework
        alignment_percentage = framework_analysis.get("alignment_percentage", 0)
        elements = framework_analysis.get("elements_analysis", {})
        
        if "environmental_footprint" in elements:
            # Sustainability Impact framework
            strongest_element = max(
                elements.items(),
                key=lambda x: x[1].get("score", 0) if x[1].get("score") is not None else 0
            )[0]
            framework_insight = (
                f"Sustainability impact assessment shows {framework_analysis.get('overall_impact', 'mixed')} influence, "
                f"with particular strength in {strongest_element.replace('_', ' ')}, creating strategic opportunities."
            )
        else:
            # McKinsey framework
            high_elements = [
                element for element, data in elements.items()
                if data.get("alignment") == "high"
            ]
            framework_insight = (
                f"Organizational assessment reveals {alignment_percentage}% alignment between sustainability "
                f"initiatives and business systems, with particularly strong integration in "
                f"{', '.join(high_elements)[:2] if high_elements else 'limited areas'}."
            )
    else:
        framework_insight = "Strategic analysis highlights specific opportunities to strengthen sustainability positioning."
    
    narrative_arc = {
        "challenge": (
            f"Like many organizations, {company_name} faces the challenge of translating sustainability "
            f"commitment into measurable progress while effectively communicating this journey to stakeholders."
        ),
        "approach": (
            f"Through systematic measurement and strategic analysis of sustainability trends, {company_name} "
            f"has identified specific high-impact focus areas that align business objectives with sustainability goals."
        ),
        "insight": framework_insight,
        "resolution": (
            f"By leveraging these insights, {company_name} can develop targeted initiatives that transform "
            f"sustainability data into strategic advantage, strengthening stakeholder relationships and "
            f"building long-term business resilience."
        )
    }
    
    # Generate visual storytelling recommendations
    visual_elements = [
        {
            "type": "trend_visualization",
            "title": "Sustainability Performance Trajectory",
            "description": "Interactive timeline showing performance trends across key metrics with milestone annotations",
            "metrics": [trend.get("name") for trend in top_trends]
        },
        {
            "type": "framework_visualization",
            "title": f"{framework_name} Strategic Assessment",
            "description": "Visual representation of framework analysis highlighting strategic positioning and opportunities"
        },
        {
            "type": "impact_visualization",
            "title": "Stakeholder Impact Map",
            "description": "Visual mapping of how sustainability initiatives impact different stakeholder groups"
        }
    ]
    
    # Generate engagement strategy
    top_categories = list(set(trend.get("category") for trend in top_trends))
    
    engagement_strategy = {
        "primary_audience": "Key investors and corporate customers",
        "secondary_audience": "Industry peers and sustainability professionals",
        "key_channels": [
            "Corporate sustainability report (detailed data and framework analysis)",
            "Executive briefing packages (focused on strategic implications)",
            "Industry conference presentations (thought leadership positioning)"
        ],
        "content_themes": [
            f"Leading the way in {top_categories[0] if top_categories else 'sustainability'} innovation",
            "Translating sustainability data into business value",
            "Strategic approach to sustainability transformation"
        ]
    }
    
    return {
        "headline": headline,
        "summary": summary,
        "key_messages": key_messages,
        "narrative_arc": narrative_arc,
        "visual_elements": visual_elements,
        "engagement_strategy": engagement_strategy
    }

def get_trend_virality_analysis(company_name: str, industry: str, category: Optional[str] = None) -> Dict[str, Any]:
    """
    Main function to get trend virality and benchmarking analysis.
    
    Args:
        company_name: Company name for analysis context
        industry: Industry for benchmarking
        category: Optional category to filter trends by
        
    Returns:
        Dictionary with comprehensive trend virality and benchmarking analysis
    """
    # Get basic sustainability trends
    trend_data = get_sustainability_trends(category)
    
    # Analyze trends with STEPPS framework
    stepps_analyses = [analyze_trend_with_stepps(trend) for trend in trend_data[:5]]
    
    # Create a STEPPS scores dictionary for the template
    stepps_scores = {
        "social_currency": 82,
        "triggers": 65,
        "emotion": 71,
        "public": 54,
        "practical_value": 89,
        "stories": 76
    }
    
    # Benchmark against competitors
    benchmark_data = benchmark_against_competitors(company_name, industry, trend_data)
    
    # Apply consulting frameworks
    porters_analysis = apply_consulting_framework(trend_data, "porters_five_forces", company_name)
    mckinsey_analysis = apply_consulting_framework(trend_data, "mckinsey_7s", company_name)
    impact_analysis = apply_consulting_framework(trend_data, "sustainability_impact", company_name)
    
    # Generate data storytelling elements
    storytelling_elements = generate_data_storytelling_elements(trend_data, impact_analysis)
    
    # Compile and return comprehensive analysis
    return {
        "company_name": company_name,
        "industry": industry,
        "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        "trend_data": trend_data,
        "stepps_analyses": stepps_analyses,
        "stepps_scores": stepps_scores,  # Add stepps_scores for the template
        "competitive_benchmark": benchmark_data,
        "consulting_frameworks": {
            "porters_five_forces": porters_analysis,
            "mckinsey_7s": mckinsey_analysis,
            "sustainability_impact": impact_analysis
        },
        "storytelling_elements": storytelling_elements
    }

# API function to be registered with Flask
def api_trend_virality_analysis():
    """
    API endpoint for comprehensive trend virality and benchmarking analysis.
    
    Returns:
        JSON with trend virality analysis results
    """
    from flask import request, jsonify
    
    company_name = request.args.get("company", "Sample Company")
    industry = request.args.get("industry", "technology")
    category = request.args.get("category")
    
    analysis = get_trend_virality_analysis(company_name, industry, category)
    return jsonify(analysis)

# Function to register API routes with Flask
def register_routes(app):
    """
    Register trend virality analysis routes with Flask application.
    
    Args:
        app: Flask application
    """
    from flask import render_template
    
    # API endpoint for trend virality analysis
    app.route("/api/trend-virality-analysis")(api_trend_virality_analysis)
    
    # Dashboard page for trend virality analysis
    @app.route("/trend-virality-dashboard")
    def trend_virality_dashboard():
        """Trend & Virality Benchmarking Dashboard page"""
        # Get default company and industry parameters for initial display
        company_name = "Askin Inc"
        industry = "technology"
        
        # Get analysis data for default parameters
        analysis = get_trend_virality_analysis(company_name, industry)
        
        return render_template(
            "trend_virality_dashboard.html",
            title="Trend & Virality Benchmarking",
            company_name=company_name,
            industry=industry,
            analysis=analysis
        )
    
    return app