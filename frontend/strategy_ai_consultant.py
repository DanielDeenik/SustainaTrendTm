"""
Strategy AI Consultant Module for SustainaTrend™

This module provides AI-powered strategy generation and consulting services
for sustainability strategy development and implementation.
"""

import json
import logging
import random
from typing import Dict, Any, List, Optional
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

# Flag to indicate if the consultant is available
STRATEGY_AI_CONSULTANT_AVAILABLE = True

def analyze_trend(trend_name: str, industry: str = None, with_stepps: bool = True) -> Dict[str, Any]:
    """
    Analyze a sustainability trend for a specific industry
    
    Args:
        trend_name: Name of the trend to analyze
        industry: Industry context for the analysis (optional)
        with_stepps: Whether to include STEPPS framework analysis
        
    Returns:
        Dictionary with trend analysis and strategic recommendations
    """
    # Log the analysis request
    logger.info(f"Analyzing trend '{trend_name}' for industry '{industry or 'general'}'")
    
    # Create mock trend data for analysis
    trend_data = {
        "name": trend_name,
        "category": _determine_trend_category(trend_name),
        "trend_direction": "improving",
        "virality_score": 75,
        "keywords": trend_name.lower().split()
    }
    
    # Import here to avoid circular imports
    from trend_virality_benchmarking import analyze_trend_with_stepps
    
    # Get STEPPS analysis if requested
    stepps_analysis = analyze_trend_with_stepps(trend_data) if with_stepps else {}
    
    # Generate industry-specific insights
    industry_insights = _generate_industry_insights(trend_name, industry)
    
    # Format the complete analysis
    analysis = {
        "trend_name": trend_name,
        "industry_context": industry or "general",
        "summary": f"Analysis of '{trend_name}' sustainability trend in the {industry or 'general'} industry context",
        "strategic_recommendations": _generate_strategic_recommendations(trend_name, industry),
        "industry_insights": industry_insights,
        "implementation_timeframe": _estimate_implementation_timeframe(trend_data),
        "stepps_analysis": stepps_analysis if with_stepps else {}
    }
    
    return analysis

def _determine_trend_category(trend_name: str) -> str:
    """Determine the most likely category for a trend based on its name"""
    trend_lower = trend_name.lower()
    
    if any(term in trend_lower for term in ["carbon", "emission", "climate", "energy", "renewable"]):
        return "Climate Action"
    elif any(term in trend_lower for term in ["circular", "waste", "recycl", "reuse"]):
        return "Circular Economy"
    elif any(term in trend_lower for term in ["water", "biodiversity", "forest", "conservation"]):
        return "Natural Resources"
    elif any(term in trend_lower for term in ["social", "diversity", "inclusion", "equity", "community"]):
        return "Social Impact"
    elif any(term in trend_lower for term in ["governance", "reporting", "disclosure", "compliance"]):
        return "ESG Governance"
    elif any(term in trend_lower for term in ["supply", "chain", "procurement", "sourcing"]):
        return "Supply Chain"
    else:
        return "Emerging Trends"

def _generate_strategic_recommendations(trend_name: str, industry: str = None) -> List[str]:
    """Generate strategic recommendations based on trend and industry"""
    recommendations = [
        f"Conduct a comprehensive assessment of how {trend_name} impacts your operations",
        f"Develop a stakeholder engagement strategy specifically addressing {trend_name}",
        f"Implement pilot projects to test innovative approaches to {trend_name}"
    ]
    
    if industry:
        industry_lower = industry.lower()
        if "tech" in industry_lower or "technology" in industry_lower:
            recommendations.append(f"Explore digital solutions to measure and manage {trend_name} impacts")
        elif "manufacturing" in industry_lower:
            recommendations.append(f"Evaluate production processes for {trend_name} optimization opportunities")
        elif "finance" in industry_lower:
            recommendations.append(f"Develop financial products aligned with {trend_name} principles")
    
    return recommendations

def _generate_industry_insights(trend_name: str, industry: str = None) -> str:
    """Generate industry-specific insights for a trend"""
    if not industry:
        return f"This trend affects multiple industries and presents cross-sector collaboration opportunities."
    
    industry_lower = industry.lower()
    if "tech" in industry_lower or "technology" in industry_lower:
        return f"In the technology sector, {trend_name} is driving innovation in digital solutions and creating new market opportunities."
    elif "manufacturing" in industry_lower:
        return f"Manufacturing companies implementing {trend_name} strategies are seeing efficiency gains and cost reductions."
    elif "finance" in industry_lower:
        return f"Financial institutions are incorporating {trend_name} into risk assessment and investment decision frameworks."
    elif "retail" in industry_lower:
        return f"Retailers embracing {trend_name} are strengthening brand loyalty and capturing eco-conscious market segments."
    elif "energy" in industry_lower:
        return f"Energy companies are using {trend_name} to navigate the transition to a low-carbon future."
    else:
        return f"Companies in the {industry} sector can gain competitive advantage by strategically addressing {trend_name}."

def _estimate_implementation_timeframe(trend_data: Dict[str, Any]) -> str:
    """Estimate implementation timeframe based on trend complexity"""
    category = trend_data.get("category", "")
    
    if category in ["Climate Action", "Circular Economy"]:
        return "Long-term (2-5 years)"
    elif category in ["Supply Chain", "Natural Resources"]:
        return "Medium-term (1-2 years)"
    else:
        return "Short-term (6-12 months)"

class StrategyAIConsultant:
    """
    AI-powered strategy consultant for sustainability strategy development
    """
    
    def __init__(self):
        """Initialize the Strategy AI Consultant"""
        self.strategies_cache = {}
        logger.info("Strategy AI Consultant initialized")
        
    def generate_strategy(self, 
                         company_name: str, 
                         industry: str, 
                         focus_areas: Optional[str] = None,
                         trends: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive sustainability strategy
        
        Args:
            company_name: Name of the company
            industry: Industry of the company
            focus_areas: Comma-separated focus areas (optional)
            trends: Specific trends to analyze (optional)
            
        Returns:
            Dictionary with generated strategy and recommendations
        """
        # Log request for debugging
        logger.info(f"Generating strategy for {company_name} in {industry} industry")
        logger.info(f"Focus areas: {focus_areas}")
        logger.info(f"Trends to analyze: {trends}")

        # Process focus areas
        focus_area_list = []
        if focus_areas:
            focus_area_list = [area.strip() for area in focus_areas.split(',') if area.strip()]
        
        # Generate the main strategy components
        strategy_components = self._generate_strategy_components(company_name, industry, focus_area_list)
        
        # Process trends if provided
        if trends:
            extracted_trends = self._extract_trends(trends, industry)
            # Format the trends for display
            trend_analysis = self._format_trends_for_display(extracted_trends)
        else:
            # Generate default trend analysis
            trend_analysis = "No specific trends were requested for analysis."
        
        # Create the strategy result
        strategy_result = {
            "status": "success",
            "message": "Strategy generated successfully",
            "company": company_name,
            "industry": industry,
            "result": strategy_components,
            "trend_analysis": trend_analysis
        }
        
        return strategy_result
        
    def generate_legacy_strategy(self, 
                         company_name: str, 
                         industry: str, 
                         focus_areas: Optional[str] = None,
                         trends: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive sustainability strategy (legacy method)
        
        Args:
            company_name: Name of the company
            industry: Industry of the company
            focus_areas: Comma-separated focus areas (optional)
            trends: Specific trends to analyze (optional)
            
        Returns:
            Dictionary with generated strategy and recommendations
        """
        # Log request for debugging
        logger.info(f"Generating legacy strategy for {company_name} in {industry} industry")
        logger.info(f"Focus areas: {focus_areas}")
        logger.info(f"Trends to analyze: {trends}")
        
        # Simply call the new method
        return self.generate_strategy(company_name, industry, focus_areas, trends)
        
    def generate_ai_strategy(self, 
                           company_name: str, 
                           industry: str, 
                           focus_areas: Optional[List[str]] = None,
                           trend_analysis: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate an AI-powered sustainability strategy with enhanced formatting and structure
        
        Args:
            company_name: Name of the company
            industry: Industry of the company
            focus_areas: List of focus areas (optional)
            trend_analysis: Trend analysis information (optional)
            
        Returns:
            Dictionary with generated strategy and recommendations in structured format
        """
        # Log request for debugging
        logger.info(f"Generating AI strategy for {company_name} in {industry} industry")
        logger.info(f"Focus areas: {focus_areas}")
        logger.info(f"Trend analysis: {trend_analysis}")
        
        # Convert focus_areas to list if provided as string
        if focus_areas is None:
            focus_areas = []
        
        # Default focus areas if none provided
        if not focus_areas:
            if "tech" in industry.lower() or "technology" in industry.lower():
                focus_areas = ["Energy Efficiency", "Supply Chain Sustainability", "Carbon Footprint Reduction"]
            elif "manufacturing" in industry.lower():
                focus_areas = ["Circular Economy", "Renewable Energy", "Sustainable Materials"]
            elif "finance" in industry.lower() or "bank" in industry.lower():
                focus_areas = ["ESG Investing", "Climate Risk Management", "Sustainable Finance Products"]
            elif "retail" in industry.lower():
                focus_areas = ["Sustainable Packaging", "Ethical Sourcing", "Carbon Footprint Reduction"]
            elif "energy" in industry.lower() or "oil" in industry.lower() or "gas" in industry.lower():
                focus_areas = ["Renewable Energy Transition", "Emissions Reduction", "Environmental Impact"]
            elif "real estate" in industry.lower() or "property" in industry.lower():
                focus_areas = ["Green Building", "Energy Efficiency", "Community Impact"]
            else:
                focus_areas = ["Carbon Footprint Reduction", "Circular Economy", "Stakeholder Engagement"]
        
        # Generate industry-specific intro based on industry
        if "tech" in industry.lower() or "technology" in industry.lower():
            intro = f"As a technology company, {company_name} has unique opportunities to lead in sustainability through digitalization, energy-efficient innovations, and responsible supply chain management."
        elif "manufacturing" in industry.lower():
            intro = f"In the manufacturing sector, {company_name} can drive sustainability through material innovation, energy-efficient production processes, and circular economy principles."
        elif "finance" in industry.lower() or "bank" in industry.lower():
            intro = f"As a financial institution, {company_name} can catalyze sustainability through ESG-aligned investments, climate risk management, and sustainable finance products."
        elif "retail" in industry.lower():
            intro = f"{company_name}, operating in the retail sector, can pioneer sustainability through transparent supply chains, sustainable packaging, and consumer education."
        elif "energy" in industry.lower() or "oil" in industry.lower() or "gas" in industry.lower():
            intro = f"In the energy sector, {company_name} faces the critical challenge of balancing energy transition with operational stability while driving decarbonization efforts."
        elif "real estate" in industry.lower() or "property" in industry.lower():
            intro = f"As a real estate company, {company_name} can lead sustainability through green building practices, energy efficiency upgrades, and community-centered development."
        else:
            intro = f"{company_name} has the opportunity to pioneer sustainability in the {industry} industry through strategic initiatives aligned with global sustainability frameworks and stakeholder expectations."
        
        # Generate strategy objectives based on focus areas
        objectives = []
        for area in focus_areas:
            if "carbon" in area.lower() or "emission" in area.lower():
                objectives.append({
                    "title": "Carbon Footprint Reduction",
                    "description": f"Implement a comprehensive carbon management program to measure, reduce, and offset {company_name}'s greenhouse gas emissions across all operations.",
                    "kpis": ["30% reduction in Scope 1 & 2 emissions by 2030", "Carbon-neutral operations by 2040", "100% renewable energy by 2035"]
                })
            elif "energy" in area.lower():
                objectives.append({
                    "title": "Energy Efficiency Transformation",
                    "description": f"Transform {company_name}'s energy consumption through efficiency measures, renewable energy integration, and smart energy management systems.",
                    "kpis": ["40% improvement in energy efficiency by 2030", "75% renewable energy sourcing by 2030", "Zero coal in energy mix by 2028"]
                })
            elif "circular" in area.lower():
                objectives.append({
                    "title": "Circular Economy Integration",
                    "description": f"Redesign {company_name}'s products, services, and operations to eliminate waste and maximize resource efficiency through circular principles.",
                    "kpis": ["80% waste diversion from landfill by 2025", "50% recycled content in products by 2030", "100% recyclable packaging by 2024"]
                })
            elif "supply chain" in area.lower() or "sourcing" in area.lower():
                objectives.append({
                    "title": "Sustainable Supply Chain",
                    "description": f"Transform {company_name}'s supply chain to ensure environmental responsibility, social equity, and economic resilience.",
                    "kpis": ["100% suppliers committed to sustainability code by 2025", "80% reduction in supply chain emissions by 2030", "Zero deforestation in supply chain by 2026"]
                })
            elif "stakeholder" in area.lower() or "community" in area.lower():
                objectives.append({
                    "title": "Stakeholder Engagement & Impact",
                    "description": f"Develop comprehensive programs to engage {company_name}'s stakeholders in sustainability initiatives and create positive social impact.",
                    "kpis": ["Annual sustainability report with stakeholder input", "Community investment of 2% of profits", "Employee sustainability training for 100% of workforce"]
                })
            elif "esg" in area.lower() or "invest" in area.lower() or "financ" in area.lower():
                objectives.append({
                    "title": "ESG Investment Integration",
                    "description": f"Integrate ESG considerations into {company_name}'s investment decisions, financial products, and risk management frameworks.",
                    "kpis": ["100% ESG screening for all investments by 2024", "$500M allocated to sustainable finance initiatives", "Climate risk assessment for all portfolios"]
                })
            elif "build" in area.lower() or "property" in area.lower():
                objectives.append({
                    "title": "Green Building & Infrastructure",
                    "description": f"Develop and retrofit {company_name}'s properties to meet leading green building standards and minimize environmental impact.",
                    "kpis": ["LEED Gold certification for all new buildings", "50% reduction in building energy consumption", "100% smart building technology implementation"]
                })
            else:
                objectives.append({
                    "title": area,
                    "description": f"Implement strategic initiatives to advance {area.lower()} across {company_name}'s operations and value chain.",
                    "kpis": ["Establish baseline metrics by Q2 2025", "Develop comprehensive strategy by Q4 2025", "50% improvement from baseline by 2030"]
                })
                
        # Generate implementation roadmap
        roadmap = [
            {
                "phase": "Phase 1: Foundation Building",
                "timeline": "Q3 2025 - Q1 2026",
                "key_initiatives": [
                    "Conduct comprehensive sustainability assessment across all operations",
                    "Establish baseline metrics for each focus area",
                    "Develop governance structure for sustainability initiatives",
                    "Engage key stakeholders to align on priorities and goals"
                ]
            },
            {
                "phase": "Phase 2: Strategic Implementation",
                "timeline": "Q2 2026 - Q4 2027",
                "key_initiatives": [
                    "Launch pilot programs for each strategic objective",
                    "Implement data collection and reporting systems",
                    "Develop supplier engagement and assessment program",
                    "Begin integration of sustainability metrics into business decisions"
                ]
            },
            {
                "phase": "Phase 3: Scaling & Integration",
                "timeline": "Q1 2028 - Q4 2029",
                "key_initiatives": [
                    "Scale successful pilots across all operations",
                    "Integrate sustainability criteria into all business processes",
                    "Implement advanced technologies for efficiency and monitoring",
                    "Develop innovation partnerships for sustainability solutions"
                ]
            },
            {
                "phase": "Phase 4: Leadership & Transformation",
                "timeline": "2030 and beyond",
                "key_initiatives": [
                    "Achieve industry leadership in key sustainability metrics",
                    "Transform business model to fully integrate sustainability",
                    "Drive industry-wide collaborations and standards",
                    "Expand positive impact beyond direct operations"
                ]
            }
        ]
        
        # Incorporate trend analysis if provided
        trend_insights = []
        if trend_analysis:
            trend_insights = [
                {
                    "trend": "Climate Action Acceleration",
                    "impact": "Increasing regulatory pressures and stakeholder expectations will require more ambitious climate targets and transparent reporting.",
                    "strategic_response": "Implement science-based targets and TCFD-aligned climate risk reporting"
                },
                {
                    "trend": "Circular Economy Transition",
                    "impact": "Growing resource constraints and waste concerns are driving market shifts toward circular business models.",
                    "strategic_response": "Redesign products and processes for circularity and resource efficiency"
                },
                {
                    "trend": "Supply Chain Transparency",
                    "impact": "Customers and regulators increasingly demand full visibility into environmental and social impacts throughout the supply chain.",
                    "strategic_response": "Implement blockchain-based traceability and supplier sustainability scoring"
                }
            ]
            
            # Add custom trend based on provided analysis
            trend_insights.append({
                "trend": "Custom Industry Analysis",
                "impact": f"Based on provided trend analysis: {trend_analysis[:100]}...",
                "strategic_response": f"Develop tailored strategy to address {industry}-specific sustainability challenges and opportunities"
            })
        
        # Format final response
        result = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "company": company_name,
            "industry": industry,
            "strategy": {
                "introduction": intro,
                "focus_areas": focus_areas,
                "strategic_objectives": objectives,
                "implementation_roadmap": roadmap,
                "trend_insights": trend_insights
            }
        }
        
        # Cache the result for future reference
        cache_key = f"{company_name}_{industry}"
        self.strategies_cache[cache_key] = result
        
        return result
    
    def _format_trends_for_display(self, trends: List[Dict[str, Any]]) -> str:
        """
        Format extracted trends for display in the strategy result
        
        Args:
            trends: List of trend dictionaries
            
        Returns:
            Formatted string with trend information
        """
        if not trends:
            return "No specific trends were provided for analysis."
            
        text = "# Trend Analysis\n\n"
        
        for i, trend in enumerate(trends, 1):
            text += f"## Trend {i}: {trend['name']}\n\n"
            text += f"{trend['description']}\n\n"
            text += f"* Category: {trend['category']}\n"
            text += f"* Impact: {trend['impact']}\n"
            text += f"* Relevance Score: {trend['relevance']:.2f}/1.0\n\n"
        
        return text
        
    def _generate_strategy_components(self, 
                                     company_name: str, 
                                     industry: str, 
                                     focus_areas: List[str],
                                     trends_input: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate detailed strategy components
        
        Args:
            company_name: Name of the company
            industry: Industry of the company
            focus_areas: List of focus areas
            trends_input: Specific trends to analyze
            
        Returns:
            Dictionary with detailed strategy components
        """
        # In a production environment, this would call an AI service
        # For demonstration, we'll simulate AI response with structured data
        
        # Default focus areas if none provided
        if not focus_areas:
            if industry.lower() in ['energy', 'oil', 'gas', 'utilities']:
                focus_areas = ['Carbon Reduction', 'Renewable Energy', 'Water Management']
            elif industry.lower() in ['technology', 'software', 'it']:
                focus_areas = ['Energy Efficiency', 'Diversity & Inclusion', 'E-waste']
            elif industry.lower() in ['financial', 'banking', 'insurance']:
                focus_areas = ['ESG Investing', 'Governance', 'Financial Inclusion']
            else:
                focus_areas = ['Carbon Footprint', 'Circular Economy', 'Social Impact']
        
        # Extract trends from input or use defaults based on industry
        trends = self._extract_trends(trends_input, industry)
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(company_name, industry, focus_areas)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(industry, focus_areas, trends)
        
        # Generate implementation roadmap
        implementation_roadmap = self._generate_implementation_roadmap(focus_areas)
        
        # Generate KPIs
        kpis = self._generate_kpis(focus_areas, industry)
        
        # Combine all components into final strategy
        strategy = {
            "company_name": company_name,
            "industry": industry,
            "focus_areas": focus_areas,
            "generated_date": datetime.now().isoformat(),
            "executive_summary": executive_summary,
            "recommendations": recommendations,
            "implementation_roadmap": implementation_roadmap,
            "kpis": kpis,
            "trends_analysis": trends
        }
        
        # Format strategy into text for display
        formatted_result = self._format_strategy_for_display(strategy)
        
        return {
            "status": "success",
            "result": formatted_result,
            "strategy_data": strategy  # Raw data for potential further processing
        }
    
    def _extract_trends(self, trends_input: Optional[str], industry: str) -> List[Dict[str, Any]]:
        """
        Extract trends from input or generate default ones based on industry
        
        Args:
            trends_input: User-provided trends text
            industry: Company industry
            
        Returns:
            List of trend objects with analysis
        """
        trends = []
        
        # If user provided specific trends, parse and analyze them
        if trends_input:
            trend_lines = [t.strip() for t in trends_input.split('\n') if t.strip()]
            for trend in trend_lines:
                trends.append({
                    "name": trend,
                    "relevance": random.uniform(0.65, 0.95),
                    "impact": random.choice(["High", "Medium", "Very High"]),
                    "timeframe": random.choice(["Short-term", "Medium-term", "Long-term"]),
                    "analysis": self._generate_trend_analysis(trend, industry)
                })
        
        # If no trends provided or less than 3 trends, add default ones
        default_trends = {
            "energy": [
                "Renewable Energy Integration",
                "Carbon Capture Technologies",
                "Smart Grid Solutions"
            ],
            "technology": [
                "Green AI and Sustainable Computing",
                "Remote Work Carbon Reduction",
                "E-waste Management Solutions"
            ],
            "financial": [
                "ESG-linked Financial Products",
                "Climate Risk Disclosure",
                "Sustainable Investment Frameworks"
            ],
            "retail": [
                "Sustainable Supply Chain Optimization",
                "Packaging Reduction Initiatives",
                "Circular Economy Business Models"
            ],
            "manufacturing": [
                "Zero-waste Manufacturing",
                "Sustainable Materials Innovation",
                "Energy Efficiency Retrofitting"
            ],
            "healthcare": [
                "Sustainable Healthcare Facilities",
                "Medical Waste Reduction",
                "Telehealth Carbon Footprint Reduction"
            ]
        }
        
        # Map industry to category
        industry_category = "technology"  # default
        for category in default_trends:
            if category in industry.lower():
                industry_category = category
                break
        
        # Add default trends if needed
        while len(trends) < 3:
            default_trend = default_trends[industry_category][len(trends) % len(default_trends[industry_category])]
            # Skip if already added
            if not any(t["name"] == default_trend for t in trends):
                trends.append({
                    "name": default_trend,
                    "relevance": random.uniform(0.70, 0.90),
                    "impact": random.choice(["High", "Medium"]),
                    "timeframe": random.choice(["Short-term", "Medium-term"]),
                    "analysis": self._generate_trend_analysis(default_trend, industry)
                })
        
        return trends
    
    def _generate_trend_analysis(self, trend: str, industry: str) -> str:
        """
        Generate analysis for a specific trend
        
        Args:
            trend: Trend name
            industry: Company industry
            
        Returns:
            Trend analysis text
        """
        analyses = [
            f"This trend represents a significant opportunity for companies in the {industry} sector, particularly those focused on long-term sustainability goals.",
            f"Organizations in {industry} are increasingly adopting this approach to meet stakeholder expectations and regulatory requirements.",
            f"Early adopters of this trend in the {industry} space have seen 15-20% improvements in related sustainability metrics and enhanced brand perception.",
            f"This emerging trend aligns with global sustainability frameworks and offers competitive differentiation in the {industry} marketplace."
        ]
        
        return random.choice(analyses)
    
    def _generate_executive_summary(self, 
                                   company_name: str, 
                                   industry: str, 
                                   focus_areas: List[str]) -> str:
        """
        Generate executive summary for the strategy
        
        Args:
            company_name: Company name
            industry: Company industry
            focus_areas: Focus areas
            
        Returns:
            Executive summary text
        """
        focus_areas_text = ", ".join(focus_areas[:-1]) + " and " + focus_areas[-1] if len(focus_areas) > 1 else focus_areas[0]
        
        summary = f"This sustainability strategy provides a comprehensive framework for {company_name} to enhance its environmental and social impact while driving business value in the {industry} sector. "
        summary += f"Focusing on {focus_areas_text}, this strategy identifies key opportunities, challenges, and actionable recommendations aligned with industry best practices and emerging trends. "
        summary += f"By implementing these recommendations, {company_name} can establish leadership in sustainable business practices, mitigate risks, and capitalize on emerging opportunities in a rapidly evolving sustainability landscape."
        
        return summary
    
    def _generate_recommendations(self, 
                                industry: str, 
                                focus_areas: List[str],
                                trends: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate specific recommendations based on industry and focus areas
        
        Args:
            industry: Company industry
            focus_areas: Focus areas
            trends: Analyzed trends
            
        Returns:
            List of recommendation objects
        """
        recommendations = []
        
        # Map focus areas to recommendation templates
        recommendation_templates = {
            "carbon": [
                {
                    "title": "Science-Based Emissions Reduction Program",
                    "description": "Develop a science-based carbon reduction program aligned with the Paris Agreement's 1.5°C pathway, with clear interim targets for 2025 and 2030.",
                    "implementation_difficulty": "Medium",
                    "impact": "High",
                    "timeframe": "18-24 months"
                },
                {
                    "title": "Carbon Accounting System Enhancement",
                    "description": "Implement an advanced carbon accounting system that tracks Scope 1, 2, and 3 emissions with quarterly reporting and integration with financial systems.",
                    "implementation_difficulty": "Medium",
                    "impact": "Medium",
                    "timeframe": "6-12 months"
                }
            ],
            "energy": [
                {
                    "title": "Renewable Energy Transition",
                    "description": "Transition to 100% renewable energy through a combination of on-site generation, power purchase agreements (PPAs), and renewable energy certificates (RECs).",
                    "implementation_difficulty": "High",
                    "impact": "Very High",
                    "timeframe": "24-36 months"
                },
                {
                    "title": "Energy Efficiency Program",
                    "description": "Implement an energy efficiency program targeting 25% reduction in energy intensity through equipment upgrades, process optimization, and behavior change.",
                    "implementation_difficulty": "Medium",
                    "impact": "High",
                    "timeframe": "12-18 months"
                }
            ],
            "water": [
                {
                    "title": "Water Stewardship Initiative",
                    "description": "Develop a comprehensive water stewardship strategy including water risk assessment, reduction targets, and community-based watershed protection projects.",
                    "implementation_difficulty": "Medium",
                    "impact": "High",
                    "timeframe": "18-24 months"
                }
            ],
            "circular": [
                {
                    "title": "Circular Product Design Framework",
                    "description": "Implement a circular design framework for products and packaging, focusing on durability, repairability, and end-of-life recycling.",
                    "implementation_difficulty": "High",
                    "impact": "High",
                    "timeframe": "18-24 months"
                },
                {
                    "title": "Zero Waste Certification",
                    "description": "Achieve zero waste to landfill certification for all major facilities through comprehensive waste reduction, recycling, and composting programs.",
                    "implementation_difficulty": "Medium",
                    "impact": "Medium",
                    "timeframe": "12-18 months"
                }
            ],
            "diversity": [
                {
                    "title": "Comprehensive DEI Strategy",
                    "description": "Develop a comprehensive diversity, equity, and inclusion strategy with measurable targets for representation, pay equity, and inclusive culture.",
                    "implementation_difficulty": "Medium",
                    "impact": "High",
                    "timeframe": "12-18 months"
                }
            ],
            "governance": [
                {
                    "title": "ESG Governance Structure",
                    "description": "Establish a formal ESG governance structure with board oversight, executive accountability, and cross-functional implementation teams.",
                    "implementation_difficulty": "Low",
                    "impact": "High",
                    "timeframe": "6-12 months"
                },
                {
                    "title": "Sustainability Reporting Framework",
                    "description": "Implement a comprehensive sustainability reporting framework aligned with GRI, SASB, and TCFD standards with third-party assurance.",
                    "implementation_difficulty": "Medium",
                    "impact": "Medium",
                    "timeframe": "12-18 months"
                }
            ]
        }
        
        # Map focus areas to categories
        focus_area_mapping = {
            "carbon": ["carbon", "emissions", "climate", "ghg"],
            "energy": ["energy", "renewable", "efficiency"],
            "water": ["water", "resource"],
            "circular": ["circular", "waste", "recycling", "packaging"],
            "diversity": ["diversity", "dei", "inclusion", "social"],
            "governance": ["governance", "esg", "reporting", "disclosure"]
        }
        
        # Match focus areas to categories and add relevant recommendations
        for focus_area in focus_areas:
            focus_area_lower = focus_area.lower()
            matched_categories = []
            
            # Find matching categories
            for category, keywords in focus_area_mapping.items():
                if any(keyword in focus_area_lower for keyword in keywords):
                    matched_categories.append(category)
            
            # If no match found, add to general category
            if not matched_categories:
                matched_categories = ["governance"]  # Default
            
            # Add recommendations from matched categories
            for category in matched_categories:
                if category in recommendation_templates:
                    for rec in recommendation_templates[category]:
                        # Skip if similar recommendation already added
                        if not any(r["title"] == rec["title"] for r in recommendations):
                            recommendations.append(rec)
        
        # Add trend-based recommendations
        for trend in trends:
            trend_recommendation = {
                "title": f"Strategic Response to {trend['name']}",
                "description": f"Develop a strategic response to the '{trend['name']}' trend, including market opportunity assessment, capability gap analysis, and implementation roadmap.",
                "implementation_difficulty": "Medium",
                "impact": trend["impact"],
                "timeframe": "12-18 months" if trend["timeframe"] == "Short-term" else "18-24 months"
            }
            recommendations.append(trend_recommendation)
        
        # Limit to top 5 recommendations if more exist
        if len(recommendations) > 5:
            recommendations = recommendations[:5]
        
        return recommendations
    
    def _generate_implementation_roadmap(self, focus_areas: List[str]) -> Dict[str, List[str]]:
        """
        Generate implementation roadmap with phased activities
        
        Args:
            focus_areas: Focus areas
            
        Returns:
            Dictionary with phased implementation activities
        """
        # Generate implementation activities based on focus areas
        short_term = [
            "Conduct baseline assessment of current sustainability performance",
            "Establish sustainability governance structure and accountability",
            "Develop detailed implementation plans for priority initiatives"
        ]
        
        medium_term = [
            "Implement data collection and reporting systems for key metrics",
            "Launch pilot programs for high-impact initiatives",
            "Develop stakeholder engagement and communication strategy"
        ]
        
        long_term = [
            "Scale successful pilot programs across the organization",
            "Integrate sustainability criteria into business planning processes",
            "Establish external partnerships to address systemic challenges"
        ]
        
        # Add focus-area specific activities
        focus_area_activities = {
            "carbon": {
                "short": "Conduct detailed carbon footprint assessment across operations",
                "medium": "Implement carbon reduction initiatives in high-impact areas",
                "long": "Achieve carbon neutrality through reduction and offsets"
            },
            "energy": {
                "short": "Conduct energy audit and identify efficiency opportunities",
                "medium": "Implement renewable energy procurement strategy",
                "long": "Achieve targeted renewable energy percentage"
            },
            "water": {
                "short": "Complete water risk assessment for key operations",
                "medium": "Implement water efficiency and recycling projects",
                "long": "Achieve water neutrality in water-stressed regions"
            },
            "circular": {
                "short": "Complete waste audit and identify circular opportunities",
                "medium": "Implement circular design principles in product development",
                "long": "Achieve zero waste to landfill across operations"
            },
            "diversity": {
                "short": "Conduct diversity assessment and gap analysis",
                "medium": "Implement diversity recruitment and development programs",
                "long": "Achieve diversity targets across all organizational levels"
            },
            "governance": {
                "short": "Establish ESG governance structure and policies",
                "medium": "Implement comprehensive ESG reporting framework",
                "long": "Integrate ESG criteria into executive compensation"
            }
        }
        
        # Map focus areas to categories (simplified mapping)
        for focus_area in focus_areas:
            focus_area_lower = focus_area.lower()
            
            for category, activities in focus_area_activities.items():
                if category in focus_area_lower:
                    short_term.append(activities["short"])
                    medium_term.append(activities["medium"])
                    long_term.append(activities["long"])
                    break
        
        # Remove duplicates and limit to reasonable number
        short_term = list(dict.fromkeys(short_term))[:5]
        medium_term = list(dict.fromkeys(medium_term))[:5]
        long_term = list(dict.fromkeys(long_term))[:5]
        
        return {
            "short_term": short_term,
            "medium_term": medium_term,
            "long_term": long_term
        }
    
    def _generate_kpis(self, focus_areas: List[str], industry: str) -> List[Dict[str, Any]]:
        """
        Generate relevant KPIs based on focus areas
        
        Args:
            focus_areas: Focus areas
            industry: Company industry
            
        Returns:
            List of KPI objects
        """
        # Base KPI templates by category
        kpi_templates = {
            "carbon": [
                {"name": "GHG Emissions Reduction", "metric": "% reduction in Scope 1 & 2 emissions", "target": "50% by 2030"},
                {"name": "Carbon Intensity", "metric": "tCO2e per revenue unit", "target": "30% reduction by 2025"}
            ],
            "energy": [
                {"name": "Renewable Energy Use", "metric": "% of total energy from renewables", "target": "100% by 2030"},
                {"name": "Energy Efficiency", "metric": "Energy use per unit of production", "target": "25% improvement by 2025"}
            ],
            "water": [
                {"name": "Water Consumption", "metric": "Total water withdrawal", "target": "30% reduction by 2025"},
                {"name": "Water Recycling Rate", "metric": "% of water recycled/reused", "target": "50% by 2025"}
            ],
            "circular": [
                {"name": "Waste Diversion Rate", "metric": "% of waste diverted from landfill", "target": "95% by 2025"},
                {"name": "Circular Material Use", "metric": "% of recycled/renewable materials", "target": "50% by 2030"}
            ],
            "diversity": [
                {"name": "Workforce Diversity", "metric": "% representation in management", "target": "40% women, 30% underrepresented groups by 2025"},
                {"name": "Pay Equity", "metric": "Pay gap by gender and ethnicity", "target": "0% gap by 2023"}
            ],
            "governance": [
                {"name": "ESG Disclosure Score", "metric": "3rd party ESG rating", "target": "Top quartile by 2024"},
                {"name": "Sustainability Training", "metric": "% of employees completed", "target": "100% annually"}
            ]
        }
        
        # Selected KPIs based on focus areas
        selected_kpis = []
        
        # Add standard KPIs for all
        selected_kpis.append({
            "name": "Sustainability Strategy Implementation",
            "metric": "% of initiatives on track",
            "target": "90% completion rate"
        })
        
        # Add KPIs based on focus areas
        for focus_area in focus_areas:
            focus_area_lower = focus_area.lower()
            
            for category, kpis in kpi_templates.items():
                if category in focus_area_lower:
                    for kpi in kpis:
                        # Only add if not already added
                        if not any(k["name"] == kpi["name"] for k in selected_kpis):
                            selected_kpis.append(kpi)
        
        # Add industry-specific KPIs
        industry_kpis = {
            "technology": {"name": "Product Energy Efficiency", "metric": "Energy use of products", "target": "20% improvement per generation"},
            "financial": {"name": "Sustainable Financing", "metric": "% of portfolio in sustainable investments", "target": "30% by 2025"},
            "energy": {"name": "Low-Carbon Products", "metric": "% revenue from low-carbon products", "target": "50% by 2030"},
            "manufacturing": {"name": "Sustainable Suppliers", "metric": "% of suppliers meeting sustainability criteria", "target": "90% by 2025"},
            "retail": {"name": "Sustainable Products", "metric": "% of products with sustainability certification", "target": "75% by 2025"}
        }
        
        # Add industry-specific KPI if relevant
        for industry_key, kpi in industry_kpis.items():
            if industry_key in industry.lower():
                selected_kpis.append(kpi)
                break
        
        # Limit to reasonable number
        if len(selected_kpis) > 6:
            selected_kpis = selected_kpis[:6]
        
        return selected_kpis
    
    def _format_strategy_for_display(self, strategy: Dict[str, Any]) -> str:
        """
        Format the strategy into readable text format for display
        
        Args:
            strategy: Raw strategy data
            
        Returns:
            Formatted strategy text
        """
        text = f"# Sustainability Strategy for {strategy['company_name']}\n\n"
        
        # Executive Summary
        text += "## Executive Summary\n\n"
        text += f"{strategy['executive_summary']}\n\n"
        
        # Recommendations
        text += "## Strategic Recommendations\n\n"
        for i, rec in enumerate(strategy['recommendations'], 1):
            text += f"### {i}. {rec['title']}\n\n"
            text += f"{rec['description']}\n\n"
            text += f"* Impact: {rec['impact']}\n"
            text += f"* Implementation: {rec['implementation_difficulty']} difficulty, {rec['timeframe']} timeframe\n\n"
        
        # Implementation Roadmap
        text += "## Implementation Roadmap\n\n"
        text += "### Short-term (0-12 months)\n\n"
        for activity in strategy['implementation_roadmap']['short_term']:
            text += f"* {activity}\n"
        text += "\n### Medium-term (1-2 years)\n\n"
        for activity in strategy['implementation_roadmap']['medium_term']:
            text += f"* {activity}\n"
        text += "\n### Long-term (2-5 years)\n\n"
        for activity in strategy['implementation_roadmap']['long_term']:
            text += f"* {activity}\n\n"
        
        # Key Performance Indicators
        text += "## Key Performance Indicators\n\n"
        for kpi in strategy['kpis']:
            text += f"* **{kpi['name']}**: {kpi['metric']} — Target: {kpi['target']}\n"
        text += "\n"
        
        # Trend Analysis
        text += "## Sustainability Trend Analysis\n\n"
        for i, trend in enumerate(strategy['trends_analysis'], 1):
            text += f"### Trend {i}: {trend['name']}\n\n"
            text += f"{trend['analysis']}\n\n"
            text += f"* Impact: {trend['impact']}\n"
            text += f"* Timeframe: {trend['timeframe']}\n"
            text += f"* Relevance Score: {trend['relevance']:.2f}/1.0\n\n"
        
        return text
        
# Old legacy method removed to avoid duplication

# Note: The global strategy_consultant instance is initialized at the end of the file

def generate_ai_strategy(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate an AI-powered sustainability strategy
    
    Args:
        data: Dictionary containing strategy generation parameters
        
    Returns:
        Dictionary with generated strategy
    """
    # Extract parameters
    company_name = data.get('companyName', '')
    industry = data.get('industry', '')
    focus_areas = data.get('focusAreas', '')
    trend_input = data.get('trendInput', '')
    
    # Validate required parameters
    if not company_name or not industry:
        return {
            "status": "error",
            "message": "Company name and industry are required"
        }
    
    # Generate strategy
    try:
        result = strategy_consultant.generate_strategy(
            company_name=company_name,
            industry=industry,
            focus_areas=focus_areas,
            trends=trend_input
        )
        return result
    except Exception as e:
        logger.error(f"Error generating strategy: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to generate strategy: {str(e)}"
        }
        
# Function to register routes with Flask application
def register_routes(app):
    """
    Register Strategy AI Consultant routes with a Flask application
    
    Args:
        app: Flask application
    """
    logger.info("Strategy AI Consultant routes registered")
    
    # No additional routes needed as the main functionality is accessed through the enhanced_strategy.py routes
    # This function exists to maintain consistency with other modules
    pass

# Initialize global strategy consultant instance
strategy_consultant = StrategyAIConsultant()
logger.info("Global Strategy AI Consultant instance created")