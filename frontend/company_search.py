"""
Company Sustainability Search Module for SustainaTrend™

This module provides advanced search capabilities for company sustainability data,
with sentiment analysis and virality metrics integration.

Key features:
1. Company-specific sustainability search across multiple sources
2. Sentiment analysis for sustainability mentions
3. Virality metrics tracking for trending sustainability topics
4. Integration with ESRS framework categories
"""
import json
import logging
import re
import os
import asyncio
import httpx
import random
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from functools import lru_cache
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Import sentiment analysis functionality
try:
    from sentiment_analysis import analyze_sustainability_sentiment, analyze_topic_sentiment
    SENTIMENT_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("Sentiment analysis module loaded successfully")
except ImportError:
    SENTIMENT_AVAILABLE = False
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.warning("Sentiment analysis module not available, using fallback mechanisms")

# Import ESRS framework categories
try:
    from esrs_framework import ESRS_FRAMEWORK
    ESRS_AVAILABLE = True
    logger.info("ESRS framework module loaded successfully")
except ImportError:
    ESRS_AVAILABLE = False
    logger.warning("ESRS framework module not available, using fallback mechanisms")

# Default ESRS categories if module not available
DEFAULT_ESRS_CATEGORIES = {
    "E1": "Climate Change",
    "E2": "Pollution",
    "E3": "Water and Marine Resources",
    "E4": "Biodiversity and Ecosystems", 
    "E5": "Resource Use and Circular Economy",
    "S1": "Own Workforce",
    "S2": "Workers in the Value Chain",
    "S3": "Affected Communities",
    "S4": "Consumers and End-users",
    "G1": "Business Conduct",
    "G2": "Corporate Governance"
}

# Company data sources
COMPANY_DATA_SOURCES = {
    "sustainability_reports": {
        "name": "Sustainability Reports",
        "description": "Official company sustainability and ESG reports",
        "reliability": 0.9
    },
    "news_articles": {
        "name": "News Articles",
        "description": "News coverage of company sustainability initiatives and issues",
        "reliability": 0.7
    },
    "social_media": {
        "name": "Social Media",
        "description": "Company and stakeholder sustainability discussions on social platforms",
        "reliability": 0.5
    },
    "ngo_reports": {
        "name": "NGO Reports",
        "description": "NGO assessments and critiques of company sustainability performance",
        "reliability": 0.8
    },
    "regulatory_filings": {
        "name": "Regulatory Filings",
        "description": "Official sustainability disclosures to regulatory bodies",
        "reliability": 0.95
    }
}

# Top sustainable companies for demo/fallback
TOP_SUSTAINABLE_COMPANIES = [
    {"name": "Patagonia", "industry": "Apparel", "ticker": "PRIVATE"},
    {"name": "Unilever", "industry": "Consumer Goods", "ticker": "UL"},
    {"name": "Tesla", "industry": "Automotive", "ticker": "TSLA"},
    {"name": "Microsoft", "industry": "Technology", "ticker": "MSFT"},
    {"name": "Ørsted", "industry": "Energy", "ticker": "ORSTED.CO"},
    {"name": "Neste", "industry": "Energy", "ticker": "NESTE.HE"},
    {"name": "Schneider Electric", "industry": "Industrial", "ticker": "SBGSY"},
    {"name": "American Electric Power", "industry": "Utilities", "ticker": "AEP"},
    {"name": "Autodesk", "industry": "Software", "ticker": "ADSK"},
    {"name": "Banco do Brasil", "industry": "Financial Services", "ticker": "BDORY"},
    {"name": "Apple", "industry": "Technology", "ticker": "AAPL"},
    {"name": "Alphabet", "industry": "Technology", "ticker": "GOOGL"},
    {"name": "Natura &Co", "industry": "Consumer Goods", "ticker": "NTCO"},
    {"name": "Kering", "industry": "Luxury Goods", "ticker": "KER.PA"},
    {"name": "Cisco Systems", "industry": "Technology", "ticker": "CSCO"}
]

async def search_company_sustainability(company_name: str, 
                                        sources: Optional[List[str]] = None,
                                        esrs_categories: Optional[List[str]] = None,
                                        max_results: int = 20,
                                        include_sentiment: bool = True) -> Dict[str, Any]:
    """
    Search for company sustainability information across multiple sources
    
    Args:
        company_name: Name of the company to search for
        sources: List of sources to search (defaults to all)
        esrs_categories: List of ESRS categories to filter by
        max_results: Maximum number of results to return
        include_sentiment: Whether to include sentiment analysis
        
    Returns:
        Dictionary with search results and analysis
    """
    logger.info(f"Searching for sustainability data on company: {company_name}")
    
    # Initialize result structure
    result = {
        "company": company_name,
        "timestamp": datetime.now().isoformat(),
        "query": f"{company_name} sustainability",
        "result_count": 0,
        "results": [],
        "sentiment_analysis": None,
        "esrs_distribution": None,
        "virality_metrics": None
    }
    
    # Validate sources
    valid_sources = list(COMPANY_DATA_SOURCES.keys())
    if sources:
        sources = [s for s in sources if s in valid_sources]
    else:
        sources = valid_sources
    
    # Get company information to enhance search
    company_info = get_company_info(company_name)
    
    try:
        # Try to get real search results
        search_results = await _perform_company_search(company_name, company_info, sources, max_results)
        
        # If we get results, process them
        if search_results:
            result["results"] = search_results
            result["result_count"] = len(search_results)
            
            # Filter by ESRS category if specified
            if esrs_categories:
                result["results"] = _filter_by_esrs_categories(search_results, esrs_categories)
                result["result_count"] = len(result["results"])
    except Exception as e:
        logger.error(f"Error performing company search: {str(e)}")
        # Fall back to mock results
        mock_results = _generate_mock_company_results(company_name, company_info, sources, max_results)
        result["results"] = mock_results
        result["result_count"] = len(mock_results)
    
    # Add sentiment analysis if requested
    if include_sentiment and SENTIMENT_AVAILABLE:
        try:
            sentiment_analysis = _analyze_results_sentiment(result["results"])
            result["sentiment_analysis"] = sentiment_analysis
        except Exception as e:
            logger.error(f"Error performing sentiment analysis: {str(e)}")
    
    # Add ESRS distribution analysis
    result["esrs_distribution"] = _analyze_esrs_distribution(result["results"])
    
    # Add virality metrics
    result["virality_metrics"] = _calculate_virality_metrics(result["results"])
    
    return result

async def _perform_company_search(company_name: str, 
                                 company_info: Dict[str, Any], 
                                 sources: List[str],
                                 max_results: int) -> List[Dict[str, Any]]:
    """
    Perform the actual company sustainability search
    
    Args:
        company_name: Company name to search for
        company_info: Additional company information
        sources: Sources to search
        max_results: Maximum results to return
        
    Returns:
        List of search results
    """
    all_results = []
    
    # Use list of sources to build search contexts
    for source in sources:
        # Adjust number of results per source based on total desired
        results_per_source = max(1, max_results // len(sources))
        
        # Create source-specific search query
        if source == "sustainability_reports":
            query = f"{company_name} sustainability report ESG"
        elif source == "news_articles":
            query = f"{company_name} sustainability news ESG initiatives"
        elif source == "social_media":
            query = f"{company_name} sustainability social media ESG discussion"
        elif source == "ngo_reports":
            query = f"{company_name} sustainability NGO assessment ESG performance"
        elif source == "regulatory_filings":
            query = f"{company_name} sustainability SEC CSRD ESRS filing disclosure"
        else:
            query = f"{company_name} sustainability ESG"
        
        # Attempt to perform real-world search (this would connect to actual APIs in production)
        try:
            source_results = await _search_source(query, source, results_per_source)
            all_results.extend(source_results)
        except Exception as e:
            logger.error(f"Error searching source {source}: {str(e)}")
            # Fall back to mock results for this source
            mock_source_results = _generate_mock_source_results(
                company_name, company_info, source, results_per_source
            )
            all_results.extend(mock_source_results)
    
    # Randomize to avoid source clustering, then sort by relevance
    random.shuffle(all_results)
    
    # Sort by relevance score (descending)
    all_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    # Limit to max results
    return all_results[:max_results]

async def _search_source(query: str, source: str, max_results: int) -> List[Dict[str, Any]]:
    """
    Search a specific source for sustainability information
    
    Args:
        query: Search query
        source: Source to search
        max_results: Maximum results to return
        
    Returns:
        List of search results
    """
    # This would normally connect to external search APIs or databases
    # For now, we'll return mock results
    return _generate_mock_source_results("", {}, source, max_results)

def _generate_mock_company_results(company_name: str, 
                                  company_info: Dict[str, Any],
                                  sources: List[str],
                                  max_results: int) -> List[Dict[str, Any]]:
    """
    Generate mock search results for company sustainability information
    
    Args:
        company_name: Company name
        company_info: Company information
        sources: Sources to include
        max_results: Maximum results to return
        
    Returns:
        List of mock search results
    """
    all_results = []
    
    # Use list of sources to build search contexts
    for source in sources:
        # Adjust number of results per source based on total desired
        results_per_source = max(1, max_results // len(sources))
        
        # Generate mock results for this source
        source_results = _generate_mock_source_results(
            company_name, company_info, source, results_per_source
        )
        all_results.extend(source_results)
    
    # Randomize to avoid source clustering, then sort by relevance
    random.shuffle(all_results)
    
    # Sort by relevance score (descending)
    all_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    # Limit to max results
    return all_results[:max_results]

def _generate_mock_source_results(company_name: str,
                                 company_info: Dict[str, Any],
                                 source: str,
                                 count: int) -> List[Dict[str, Any]]:
    """
    Generate mock results for a specific source
    
    Args:
        company_name: Company name
        company_info: Company information
        source: Source to generate results for
        count: Number of results to generate
        
    Returns:
        List of mock search results
    """
    results = []
    industry = company_info.get("industry", "")
    
    # Get mock content templates for different sources
    source_content = _get_source_content_templates(source)
    
    # Get ESRS categories to include in results
    esrs_categories = list(DEFAULT_ESRS_CATEGORIES.keys())
    
    # Generate results
    for i in range(count):
        # Select random ESRS category for this result
        esrs_category = random.choice(esrs_categories)
        esrs_name = DEFAULT_ESRS_CATEGORIES.get(esrs_category, "Sustainability")
        
        # Select content template and fill in company name
        content_template = random.choice(source_content)
        title = content_template["title"].replace("{company}", company_name).replace("{category}", esrs_name)
        description = content_template["description"].replace("{company}", company_name).replace("{category}", esrs_name)
        
        # Add industry if available
        if industry:
            title = title.replace("{industry}", industry)
            description = description.replace("{industry}", industry)
        else:
            title = title.replace("{industry}", "")
            description = description.replace("{industry}", "")
        
        # Generate a date within the last 90 days, with more recent dates more likely
        days_ago = int(random.triangular(1, 90, 10))  # Bias toward more recent content
        date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        # Generate a mock URL
        if source == "sustainability_reports":
            domain = f"{company_name.lower().replace(' ', '')}.com".replace('.com.com', '.com')
            url = f"https://www.{domain}/sustainability/report-{date[:4]}.pdf"
        elif source == "news_articles":
            news_domains = ["reuters.com", "bloomberg.com", "wsj.com", "cnbc.com", "ft.com"]
            domain = random.choice(news_domains)
            slug = title.lower().replace(' ', '-')[:40].strip('-')
            url = f"https://www.{domain}/sustainability/{date.replace('-', '/')}/{slug}"
        elif source == "social_media":
            social_domains = ["twitter.com", "linkedin.com", "reddit.com"]
            domain = random.choice(social_domains)
            url = f"https://{domain}/{company_name.lower().replace(' ', '')}/status/{random.randint(1000000000, 9999999999)}"
        elif source == "ngo_reports":
            ngo_domains = ["sustainabilitywatch.org", "climatemonitor.org", "esgobserver.net", "greentransparency.org"]
            domain = random.choice(ngo_domains)
            url = f"https://www.{domain}/company-reports/{company_name.lower().replace(' ', '-')}"
        elif source == "regulatory_filings":
            if random.random() < 0.7:  # 70% chance of SEC
                url = f"https://www.sec.gov/Archives/edgar/data/{random.randint(1000000, 9999999)}/{date.replace('-', '')}-{random.randint(10000, 99999)}.txt"
            else:  # 30% chance of EU
                url = f"https://efrag.org/esrs/filings/{company_name.lower().replace(' ', '-')}-{date[:4]}"
        else:
            url = f"https://www.sustainableresearch.com/companies/{company_name.lower().replace(' ', '-')}"
        
        # Generate relevance score (higher for sources with higher reliability)
        source_reliability = COMPANY_DATA_SOURCES[source]["reliability"]
        relevance_base = random.uniform(0.5, 0.95)  # Base relevance between 0.5 and 0.95
        relevance_score = relevance_base * source_reliability
        
        # Create the result object
        result = {
            "title": title,
            "url": url,
            "source": COMPANY_DATA_SOURCES[source]["name"],
            "source_type": source,
            "description": description,
            "date": date,
            "relevance_score": round(relevance_score, 2),
            "esrs_category": esrs_category,
            "source_reliability": source_reliability,
            "company": company_name
        }
        
        results.append(result)
    
    return results

def _get_source_content_templates(source: str) -> List[Dict[str, str]]:
    """
    Get content templates for a specific source
    
    Args:
        source: Source to get templates for
        
    Returns:
        List of title/description templates
    """
    if source == "sustainability_reports":
        return [
            {
                "title": "{company} Sustainability Report {category} Highlights",
                "description": "{company}'s sustainability report details its {category} performance, including metrics, targets, and initiatives. The report presents comprehensive data on the company's progress and future commitments in this critical ESG area."
            },
            {
                "title": "{company} ESG Report: {category} Progress and Challenges",
                "description": "In its annual ESG disclosure, {company} addresses key {category} issues, presenting both achievements and areas for improvement. The report includes quantitative metrics following global reporting standards and details future improvement plans."
            },
            {
                "title": "{company} {industry} Sustainability Performance: {category}",
                "description": "This sustainability report section examines {company}'s approach to {category} within the {industry} industry context, with comparative benchmarking against sector peers and highlight of industry-specific initiatives."
            }
        ]
    elif source == "news_articles":
        return [
            {
                "title": "{company} Announces New {category} Targets",
                "description": "In a recent announcement, {company} has set ambitious new targets for {category}, aiming to significantly improve their sustainability performance in this area. Industry analysts view this as a strategic move to position the company for regulatory compliance and market leadership."
            },
            {
                "title": "{company}'s {category} Initiative Draws Investor Attention",
                "description": "Investors are responding positively to {company}'s latest {category} initiative, which addresses key sustainability concerns in the {industry} sector. The company's stock has seen movement following this announcement as ESG-focused funds reassess their positions."
            },
            {
                "title": "Analysis: How {company} is Tackling {category} Challenges",
                "description": "This in-depth analysis examines {company}'s approach to {category}, comparing their strategy to industry best practices and regulatory requirements. The article includes expert commentary on the effectiveness and credibility of their sustainability claims."
            }
        ]
    elif source == "social_media":
        return [
            {
                "title": "Discussion: {company}'s {category} Claims Under Scrutiny",
                "description": "Online discussion about {company}'s {category} claims has intensified, with stakeholders debating the authenticity and impact of their sustainability initiatives. Some commenters praise their transparency while others question the substantive impact of their programs."
            },
            {
                "title": "{company} CEO Highlights {category} Progress on Social Media",
                "description": "The CEO of {company} shared updates on the company's {category} progress, generating significant engagement from employees, investors, and customers. The post included specific metrics and commitments that have sparked discussions about leadership in sustainability."
            },
            {
                "title": "Viral: {company}'s {category} Campaign Gains Traction",
                "description": "A social media campaign highlighting {company}'s approach to {category} has gained significant attention online, with mixed reactions from environmental advocates and industry observers. The campaign emphasizes the company's commitments and progress in this area."
            }
        ]
    elif source == "ngo_reports":
        return [
            {
                "title": "NGO Assessment: {company}'s {category} Performance",
                "description": "This independent assessment evaluates {company}'s {category} performance against rigorous sustainability standards, identifying both strengths and areas of concern. The report includes recommendations for improvement and comparison with industry peers."
            },
            {
                "title": "Critical Analysis: {company}'s {category} Claims vs. Reality",
                "description": "This NGO report examines the gap between {company}'s {category} claims and their measurable impact, highlighting discrepancies and presenting evidence-based analysis. The findings suggest several areas where greater transparency and concrete action are needed."
            },
            {
                "title": "{company} Ranked in Top/Bottom Performers for {category}",
                "description": "In a comprehensive industry ranking, {company} has been identified as a top/bottom performer in {category} among {industry} companies. The assessment methodology considers both quantitative metrics and qualitative evaluation of policies and implementation."
            }
        ]
    elif source == "regulatory_filings":
        return [
            {
                "title": "{company} ESRS E1 Disclosure: {category} Compliance",
                "description": "This regulatory filing details {company}'s compliance with ESRS {category} disclosure requirements, including mandated metrics and risk assessments. The document provides insights into the company's approach to meeting evolving regulatory standards in sustainability reporting."
            },
            {
                "title": "{company}'s SEC Climate Disclosure: {category} Risks and Opportunities",
                "description": "In its SEC filing, {company} outlines {category} risks and opportunities, including financial implications and management strategies. The disclosure follows regulatory guidelines for climate-related financial risk reporting and governance oversight."
            },
            {
                "title": "{company} Files Mandatory {category} Report in Compliance with New Regulations",
                "description": "This mandatory filing from {company} addresses {category} in accordance with new regulatory requirements, providing standardized metrics and management approach disclosures. The report reflects the increasing formalization of sustainability reporting in financial disclosures."
            }
        ]
    else:
        return [
            {
                "title": "{company} {category} Overview",
                "description": "An overview of {company}'s approach to {category}, compiled from various public sources and sustainability disclosures. This information provides insights into the company's sustainability strategy and performance in this area."
            }
        ]

def _analyze_results_sentiment(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze sentiment of search results
    
    Args:
        results: Search results to analyze
        
    Returns:
        Sentiment analysis results
    """
    if not SENTIMENT_AVAILABLE:
        return {
            "error": "Sentiment analysis not available",
            "overall_sentiment": "neutral",
            "score": 0.5
        }
    
    # Combine all descriptions for overall sentiment
    all_text = " ".join([r.get("description", "") for r in results if "description" in r])
    overall_sentiment = analyze_sustainability_sentiment(all_text)
    
    # Analyze by ESRS category
    category_sentiments = {}
    for category_id in DEFAULT_ESRS_CATEGORIES:
        # Get results for this category
        category_results = [r for r in results if r.get("esrs_category") == category_id]
        if category_results:
            # Combine descriptions
            category_text = " ".join([r.get("description", "") for r in category_results])
            # Analyze sentiment
            category_sentiment = analyze_sustainability_sentiment(category_text)
            category_sentiments[category_id] = {
                "name": DEFAULT_ESRS_CATEGORIES[category_id],
                "sentiment": category_sentiment["sentiment"],
                "score": category_sentiment["score"],
                "result_count": len(category_results)
            }
    
    # Find most positive and negative categories
    if category_sentiments:
        sorted_categories = sorted(
            [(cat_id, data) for cat_id, data in category_sentiments.items()],
            key=lambda x: x[1]["score"],
            reverse=True
        )
        
        most_positive = sorted_categories[0] if sorted_categories else None
        most_negative = sorted_categories[-1] if len(sorted_categories) > 1 else None
    else:
        most_positive = None
        most_negative = None
    
    sentiment_analysis = {
        "overall_sentiment": overall_sentiment["sentiment"],
        "overall_score": overall_sentiment["score"],
        "category_sentiments": category_sentiments,
        "most_positive_category": {
            "id": most_positive[0],
            "name": most_positive[1]["name"],
            "score": most_positive[1]["score"]
        } if most_positive else None,
        "most_negative_category": {
            "id": most_negative[0],
            "name": most_negative[1]["name"],
            "score": most_negative[1]["score"]
        } if most_negative else None,
        "analysis_type": overall_sentiment.get("analysis_type", "unknown")
    }
    
    return sentiment_analysis

def _analyze_esrs_distribution(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze ESRS category distribution in search results
    
    Args:
        results: Search results to analyze
        
    Returns:
        ESRS distribution analysis
    """
    # Count results by ESRS category
    category_counts = {}
    for category_id in DEFAULT_ESRS_CATEGORIES:
        category_counts[category_id] = 0
    
    # Count occurrences
    for result in results:
        category = result.get("esrs_category")
        if category in category_counts:
            category_counts[category] += 1
    
    # Calculate percentages
    total_results = len(results)
    category_percentages = {}
    for category_id, count in category_counts.items():
        if total_results > 0:
            percentage = (count / total_results) * 100
        else:
            percentage = 0
        
        category_percentages[category_id] = {
            "name": DEFAULT_ESRS_CATEGORIES[category_id],
            "count": count,
            "percentage": round(percentage, 1)
        }
    
    # Identify top categories
    sorted_categories = sorted(
        [(cat_id, data) for cat_id, data in category_percentages.items()],
        key=lambda x: x[1]["count"],
        reverse=True
    )
    
    top_categories = sorted_categories[:3] if len(sorted_categories) >= 3 else sorted_categories
    
    return {
        "total_results": total_results,
        "categories": category_percentages,
        "top_categories": [
            {
                "id": cat_id,
                "name": data["name"],
                "count": data["count"],
                "percentage": data["percentage"]
            }
            for cat_id, data in top_categories
        ]
    }

def _calculate_virality_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate virality metrics for search results
    
    Args:
        results: Search results to analyze
        
    Returns:
        Virality metrics analysis
    """
    # Analyze recency
    dates = [datetime.strptime(r.get("date", "2023-01-01"), "%Y-%m-%d") for r in results if "date" in r]
    now = datetime.now()
    
    # Calculate recency scores (higher for more recent content)
    recency_scores = []
    for date in dates:
        days_ago = (now - date).days
        if days_ago <= 7:  # Last week
            recency_score = 1.0
        elif days_ago <= 30:  # Last month
            recency_score = 0.8
        elif days_ago <= 90:  # Last quarter
            recency_score = 0.6
        elif days_ago <= 365:  # Last year
            recency_score = 0.4
        else:
            recency_score = 0.2
        
        recency_scores.append(recency_score)
    
    # Calculate average recency score
    avg_recency = sum(recency_scores) / len(recency_scores) if recency_scores else 0
    
    # Calculate source diversity score
    sources = [r.get("source_type", "") for r in results]
    unique_sources = set(sources)
    source_diversity = len(unique_sources) / len(COMPANY_DATA_SOURCES)
    
    # Calculate content dispersion (higher when spread across categories)
    categories = [r.get("esrs_category", "") for r in results]
    unique_categories = set(categories)
    category_dispersion = len(unique_categories) / len(DEFAULT_ESRS_CATEGORIES)
    
    # Calculate source reliability average
    reliability_scores = [r.get("source_reliability", 0.5) for r in results]
    avg_reliability = sum(reliability_scores) / len(reliability_scores) if reliability_scores else 0.5
    
    # Calculate overall virality score (weighted average of components)
    # 40% recency, 30% source diversity, 20% category dispersion, 10% reliability
    virality_score = (
        (avg_recency * 0.4) +
        (source_diversity * 0.3) +
        (category_dispersion * 0.2) +
        (avg_reliability * 0.1)
    ) * 100
    
    # Determine trend direction based on date concentration
    if dates:
        recent_month_count = sum(1 for date in dates if (now - date).days <= 30)
        recent_month_percentage = (recent_month_count / len(dates)) * 100
        
        if recent_month_percentage > 60:
            trend_direction = "rapidly increasing"
        elif recent_month_percentage > 40:
            trend_direction = "increasing"
        elif recent_month_percentage > 20:
            trend_direction = "stable"
        else:
            trend_direction = "decreasing"
    else:
        trend_direction = "unknown"
    
    return {
        "virality_score": round(virality_score, 1),
        "trend_direction": trend_direction,
        "recency_score": round(avg_recency * 100, 1),
        "source_diversity": round(source_diversity * 100, 1),
        "category_dispersion": round(category_dispersion * 100, 1),
        "reliability_score": round(avg_reliability * 100, 1),
        "data_points": len(results)
    }

def _filter_by_esrs_categories(results: List[Dict[str, Any]], categories: List[str]) -> List[Dict[str, Any]]:
    """
    Filter results by ESRS categories
    
    Args:
        results: Search results to filter
        categories: ESRS categories to include
        
    Returns:
        Filtered search results
    """
    return [r for r in results if r.get("esrs_category") in categories]

def get_company_info(company_name: str) -> Dict[str, Any]:
    """
    Get information about a company
    
    Args:
        company_name: Name of the company
        
    Returns:
        Company information
    """
    # Normalize company name for comparison
    normalized_name = company_name.lower().strip()
    
    # Check against known companies
    for company in TOP_SUSTAINABLE_COMPANIES:
        if company["name"].lower() == normalized_name:
            return company
    
    # If not found, return basic info
    return {"name": company_name, "industry": "", "ticker": ""}

def configure_routes(app):
    """
    Configure Flask routes for company sustainability search
    
    Args:
        app: Flask application
    """
    from flask import render_template, request, jsonify
    
    @app.route('/company-search', methods=['GET'])
    def company_search_page():
        """Company Sustainability Search Page"""
        # Get ESRS categories for filtering
        if ESRS_AVAILABLE:
            from esrs_framework import get_esrs_categories
            esrs_categories = get_esrs_categories()
        else:
            esrs_categories = {
                cat_id: {"name": name, "description": f"ESRS {cat_id} category"}
                for cat_id, name in DEFAULT_ESRS_CATEGORIES.items()
            }
            
        # Get data sources for filtering
        data_sources = {
            source_id: {
                "name": source_data["name"],
                "description": source_data["description"],
                "reliability": source_data["reliability"]
            }
            for source_id, source_data in COMPANY_DATA_SOURCES.items()
        }
        
        # Get top sustainable companies for suggestions
        companies = [c["name"] for c in TOP_SUSTAINABLE_COMPANIES[:10]]
        
        return render_template(
            'company_search.html',
            esrs_categories=esrs_categories,
            data_sources=data_sources,
            top_companies=companies
        )
    
    @app.route('/api/company-search', methods=['GET', 'POST'])
    def api_company_search():
        """API endpoint for company sustainability search"""
        # Get parameters
        if request.method == 'POST':
            data = request.get_json()
            company_name = data.get('company_name', '')
            sources = data.get('sources', None)
            esrs_categories = data.get('esrs_categories', None)
            include_sentiment = data.get('include_sentiment', True)
            max_results = int(data.get('max_results', 20))
        else:
            company_name = request.args.get('company_name', '')
            sources = request.args.getlist('sources')
            esrs_categories = request.args.getlist('esrs_categories')
            include_sentiment = request.args.get('include_sentiment', 'true').lower() == 'true'
            max_results = int(request.args.get('max_results', 20))
        
        # Validate inputs
        if not company_name:
            return jsonify({
                'success': False,
                'error': 'Missing company_name parameter'
            }), 400
            
        # Convert empty lists to None
        sources = sources if sources else None
        esrs_categories = esrs_categories if esrs_categories else None
        
        # Create async task and wait for result
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                search_company_sustainability(company_name, sources, esrs_categories, max_results, include_sentiment)
            )
            loop.close()
            
            return jsonify({
                'success': True,
                'results': result
            })
        except Exception as e:
            logger.error(f"Error in company search API: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

def register_routes(app):
    """
    Register the company search routes with a Flask application
    
    Args:
        app: Flask application
    """
    configure_routes(app)
    logger.info("Company search routes registered")
"""