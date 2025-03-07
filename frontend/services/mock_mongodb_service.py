"""
Mock MongoDB Service Layer for SustainaTrend™

This module provides a mock service layer for MongoDB operations,
allowing the application to function without an actual MongoDB connection.
"""

import logging
from typing import List, Dict, Any, Optional, Sequence
from datetime import datetime, timedelta
import random
import json

# Configure logging
logger = logging.getLogger(__name__)

class MockMongoDBService:
    """Mock service class for MongoDB operations"""
    
    @staticmethod
    def check_connection() -> bool:
        """
        Check if mock MongoDB connection is available
        
        Returns:
            bool: Always returns True
        """
        logger.info("Mock MongoDB connection check requested")
        return True
            
    @classmethod
    def get_metrics(
        cls,
        category: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get mock sustainability metrics with optional filtering
        
        Args:
            category: Filter by category (optional)
            start_date: Filter by minimum date (optional)
            end_date: Filter by maximum date (optional)
            limit: Maximum number of metrics to return
            
        Returns:
            List of mock metrics as dictionaries
        """
        logger.info(f"Mock metrics requested (category={category}, limit={limit})")
        
        # Create mock metrics data
        metrics_categories = ["environmental", "social", "governance", "economic", "climate"]
        metrics_names = {
            "environmental": ["Carbon Emissions", "Water Usage", "Waste Generation", "Renewable Energy", "Environmental Compliance"],
            "social": ["Employee Diversity", "Pay Equity", "Community Investment", "Worker Safety", "Human Rights"],
            "governance": ["Board Diversity", "Executive Compensation", "Ethics Violations", "Transparency Score", "Risk Management"],
            "economic": ["Sustainable Revenue", "Green Innovation", "Resource Efficiency", "Supply Chain Sustainability", "Circular Economy"],
            "climate": ["Scope 1 Emissions", "Scope 2 Emissions", "Scope 3 Emissions", "Climate Risk Score", "Carbon Offsets"]
        }
        metrics_units = {
            "Carbon Emissions": "tons",
            "Water Usage": "m³",
            "Waste Generation": "tons",
            "Renewable Energy": "%",
            "Environmental Compliance": "incidents",
            "Employee Diversity": "%",
            "Pay Equity": "ratio",
            "Community Investment": "USD",
            "Worker Safety": "incidents",
            "Human Rights": "violations",
            "Board Diversity": "%",
            "Executive Compensation": "ratio",
            "Ethics Violations": "count",
            "Transparency Score": "score",
            "Risk Management": "score",
            "Sustainable Revenue": "%",
            "Green Innovation": "count",
            "Resource Efficiency": "score",
            "Supply Chain Sustainability": "score",
            "Circular Economy": "%",
            "Scope 1 Emissions": "tons",
            "Scope 2 Emissions": "tons",
            "Scope 3 Emissions": "tons",
            "Climate Risk Score": "score",
            "Carbon Offsets": "tons"
        }
        
        # Generate mock metrics
        result = []
        
        # Filter categories if specified
        if category:
            categories_to_use = [category] if category in metrics_categories else metrics_categories
        else:
            categories_to_use = metrics_categories
            
        # Create a realistic time distribution (newer data more common)
        now = datetime.now()
        timeframes = [
            (now - timedelta(days=1), now, 0.4),                      # Last day (40%)
            (now - timedelta(days=7), now - timedelta(days=1), 0.3),  # Last week (30%)
            (now - timedelta(days=30), now - timedelta(days=7), 0.2), # Last month (20%)
            (now - timedelta(days=90), now - timedelta(days=30), 0.1) # Last quarter (10%)
        ]
        
        # Generate mock data
        total_metrics = 0
        for cat in categories_to_use:
            # Determine how many metrics to generate for this category
            metrics_per_category = min(limit // len(categories_to_use), len(metrics_names[cat]))
            
            for i in range(metrics_per_category):
                # Select metric name
                metric_name = metrics_names[cat][i % len(metrics_names[cat])]
                
                # Decide timeframe according to distribution
                timeframe_idx = random.choices(
                    range(len(timeframes)), 
                    weights=[tf[2] for tf in timeframes],
                    k=1
                )[0]
                
                start, end, _ = timeframes[timeframe_idx]
                timestamp = start + timedelta(
                    seconds=random.randint(0, int((end - start).total_seconds()))
                )
                
                # Skip if outside requested date range
                if start_date and timestamp < start_date:
                    continue
                if end_date and timestamp > end_date:
                    continue
                
                # Generate value based on metric type
                if "%" in metrics_units.get(metric_name, ""):
                    value = round(random.uniform(0, 100), 1)
                elif "ratio" in metrics_units.get(metric_name, ""):
                    value = round(random.uniform(0.5, 2.0), 2)
                elif "score" in metrics_units.get(metric_name, ""):
                    value = round(random.uniform(1, 10), 1)
                elif "count" in metrics_units.get(metric_name, "") or "incidents" in metrics_units.get(metric_name, "") or "violations" in metrics_units.get(metric_name, ""):
                    value = random.randint(0, 10)
                elif "USD" in metrics_units.get(metric_name, ""):
                    value = random.randint(10000, 1000000)
                else:
                    value = round(random.uniform(10, 1000), 1)
                
                # Create metric
                metric = {
                    "id": f"metric_{total_metrics + 1}",
                    "name": metric_name,
                    "category": cat,
                    "value": value,
                    "unit": metrics_units.get(metric_name, "units"),
                    "timestamp": timestamp.isoformat(),
                    "source": random.choice(["Internal Reporting", "Third-Party Audit", "Regulatory Filing", "Sustainability Report"]),
                    "trend": random.choice(["increasing", "decreasing", "stable"])
                }
                
                result.append(metric)
                total_metrics += 1
                
                # Stop if we've reached the limit
                if total_metrics >= limit:
                    break
            
            # Stop if we've reached the limit
            if total_metrics >= limit:
                break
        
        logger.info(f"Returning {len(result)} mock metrics")
        return result
    
    @classmethod
    def get_trends(
        cls,
        category: Optional[str] = None,
        min_virality: Optional[float] = None,
        timeframe: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get mock sustainability trends with optional filtering
        
        Args:
            category: Filter by category (optional)
            min_virality: Minimum virality score (optional)
            timeframe: Timeframe filter (optional)
            limit: Maximum number of trends to return
            
        Returns:
            List of mock trends as dictionaries
        """
        logger.info(f"Mock trends requested (category={category}, min_virality={min_virality}, limit={limit})")
        
        # Create mock trends data
        trend_categories = ["environmental", "social", "governance", "economic", "climate"]
        trend_names = {
            "environmental": [
                "Circular Economy", "Plastic-Free Packaging", "Zero Waste Movement", 
                "Biodiversity Initiatives", "Carbon Neutrality", "Ocean Plastic Cleanup",
                "Sustainable Agriculture", "Eco-Friendly Materials", "Reforestation Programs"
            ],
            "social": [
                "Social Impact Investing", "Diversity in Leadership", "Equal Pay Initiatives", 
                "Ethical Supply Chains", "Community Engagement", "Employee Wellbeing",
                "Human Rights Policies", "Local Sourcing", "Accessibility Standards"
            ],
            "governance": [
                "ESG Reporting Standards", "Corporate Transparency", "Stakeholder Capitalism", 
                "Responsible Leadership", "Ethics Committees", "Regulatory Compliance",
                "Anti-Corruption Measures", "Board Diversity", "Shareholder Activism"
            ],
            "economic": [
                "Green Bonds", "Sustainable Finance", "Impact Investing", 
                "Conscious Consumerism", "Sustainable Business Models", "Resource Efficiency",
                "Longevity Economics", "Green Procurement", "Sustainability ROI"
            ],
            "climate": [
                "Climate Resilience", "Science-Based Targets", "Net-Zero Commitments", 
                "Carbon Disclosure", "Climate Risk Assessment", "Renewable Energy Transition",
                "Low-Carbon Solutions", "Climate Justice", "Carbon Markets"
            ]
        }
        
        # Generate mock trends
        result = []
        
        # Filter categories if specified
        if category:
            categories_to_use = [category] if category in trend_categories else trend_categories
        else:
            categories_to_use = trend_categories
        
        # Calculate date threshold based on timeframe
        now = datetime.now()
        date_threshold = None
        
        if timeframe:
            if timeframe == 'week':
                date_threshold = now - timedelta(days=7)
            elif timeframe == 'month':
                date_threshold = now - timedelta(days=30)
            elif timeframe == 'quarter':
                date_threshold = now - timedelta(days=90)
            elif timeframe == 'year':
                date_threshold = now - timedelta(days=365)
        
        # Use weighted distribution for virality scores
        # Most trends have medium virality, fewer have very high or low
        virality_ranges = [
            (0.9, 1.0, 0.1),   # Very high (10%)
            (0.7, 0.9, 0.25),  # High (25%)
            (0.5, 0.7, 0.4),   # Medium (40%)
            (0.3, 0.5, 0.15),  # Low (15%)
            (0.1, 0.3, 0.1)    # Very low (10%)
        ]
        
        # Generate mock data
        total_trends = 0
        for cat in categories_to_use:
            for name in trend_names[cat]:
                # Decide virality range according to distribution
                range_idx = random.choices(
                    range(len(virality_ranges)), 
                    weights=[vr[2] for vr in virality_ranges],
                    k=1
                )[0]
                
                min_val, max_val, _ = virality_ranges[range_idx]
                virality_score = round(random.uniform(min_val, max_val), 2)
                
                # Skip if below minimum virality
                if min_virality is not None and virality_score < min_virality:
                    continue
                
                # Determine timestamp (weighted toward more recent)
                days_ago = int(random.triangular(1, 120, 14))  # Weighted toward recent (mode = 14)
                timestamp = now - timedelta(days=days_ago)
                
                # Skip if outside timeframe
                if date_threshold and timestamp < date_threshold:
                    continue
                
                # Create trend
                trend = {
                    "id": f"trend_{total_trends + 1}",
                    "name": name,
                    "category": cat,
                    "virality_score": virality_score,
                    "timestamp": timestamp.isoformat(),
                    "sources": random.sample([
                        "Twitter", "LinkedIn", "News Articles", "Industry Reports", 
                        "Research Papers", "Conferences", "Corporate Announcements"
                    ], random.randint(1, 3)),
                    "momentum": random.choice(["rising", "steady", "falling"]),
                    "relevance_score": round(random.uniform(0.5, 1.0), 2)
                }
                
                result.append(trend)
                total_trends += 1
                
                # Stop if we've reached the limit
                if total_trends >= limit:
                    break
            
            # Stop if we've reached the limit
            if total_trends >= limit:
                break
        
        # Sort by virality score (descending)
        result.sort(key=lambda x: x["virality_score"], reverse=True)
        
        logger.info(f"Returning {len(result)} mock trends")
        return result[:limit]
    
    @classmethod
    def get_stories(
        cls,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get mock sustainability stories with optional filtering
        
        Args:
            category: Filter by category (optional)
            tags: Filter by tags (optional)
            start_date: Filter by minimum date (optional)
            end_date: Filter by maximum date (optional)
            limit: Maximum number of stories to return
            skip: Number of stories to skip (for pagination)
            
        Returns:
            List of mock stories as dictionaries
        """
        logger.info(f"Mock stories requested (category={category}, limit={limit}, skip={skip})")
        
        # Create mock stories data
        story_categories = ["environmental", "social", "governance", "economic", "climate"]
        
        story_templates = {
            "environmental": [
                {
                    "title_template": "{company}'s Journey to Zero Waste: Eliminating {waste_type} from Operations",
                    "content_template": "In a bold move towards sustainability, {company} has successfully eliminated {waste_type} from its operations. Through innovative redesign and process optimization, the company has achieved a {percent}% reduction in waste sent to landfill compared to its {year} baseline. Key initiatives included {initiative1} and {initiative2}, which not only reduced environmental impact but also resulted in annual savings of {amount} USD.",
                    "variables": {
                        "company": ["Eco Innovations", "GreenTech Solutions", "Sustainable Corp", "EcoSphere Industries", "NatureTrust"],
                        "waste_type": ["Single-Use Plastics", "Packaging Waste", "Food Waste", "Electronic Waste", "Chemical Waste"],
                        "percent": lambda: random.randint(50, 95),
                        "year": lambda: random.randint(2015, 2022),
                        "initiative1": ["employee engagement programs", "supplier partnerships", "circular design principles", "material substitution", "process reengineering"],
                        "initiative2": ["waste stream analysis", "composting facilities", "reusable packaging systems", "take-back programs", "digital transformation"],
                        "amount": lambda: f"{random.randint(100, 999):,}"
                    }
                },
                {
                    "title_template": "Breakthrough in {resource} Conservation: {company}'s Innovative Approach",
                    "content_template": "{company} has demonstrated remarkable success in {resource} conservation through its innovative {technology} technology. The {location}-based initiative has reduced {resource} consumption by {percent}% across {scope} operations. The approach combines {method1} with {method2}, creating a scalable solution for the {industry} industry. Environmental experts from {organization} have validated the results, highlighting the potential for industry-wide application.",
                    "variables": {
                        "company": ["BlueDropTech", "ResourceWise", "EcoEfficiency Inc", "ConservePro", "GreenCircle"],
                        "resource": ["Water", "Energy", "Forest", "Soil", "Mineral"],
                        "technology": ["AI-powered", "Biomimetic", "Closed-loop", "Precision", "Smart-grid"],
                        "location": ["European", "North American", "Global", "Urban", "Rural"],
                        "percent": lambda: random.randint(30, 75),
                        "scope": ["manufacturing", "supply chain", "retail", "distribution", "corporate"],
                        "method1": ["real-time monitoring", "predictive analytics", "material science advances", "stakeholder collaboration", "lifecycle assessment"],
                        "method2": ["efficiency benchmarking", "regenerative design", "behavioral science", "policy integration", "technological innovation"],
                        "industry": ["manufacturing", "consumer goods", "agriculture", "construction", "transportation"],
                        "organization": ["Environmental Protection Agency", "World Resources Institute", "Green Business Alliance", "Sustainable Industry Forum", "EcoCertification Board"]
                    }
                }
            ],
            "social": [
                {
                    "title_template": "{company} Transforms Community Engagement Through {program_name} Initiative",
                    "content_template": "The {program_name} initiative by {company} has revolutionized corporate community engagement in {location}. Launched in {year}, the program has benefited over {beneficiaries} people through its focus on {focus_area}. The company invested {amount} USD and {volunteer_hours} employee volunteer hours, creating measurable improvements in {outcome1} and {outcome2}. {stakeholder}, {title} at {organization}, commented: '{quote}'",
                    "variables": {
                        "company": ["CommunityCorp", "SocialImpact Inc", "PeoplePlus", "HumanityFirst", "BetterSociety Group"],
                        "program_name": ["EmpowerTogether", "CommunityRise", "FutureBuilders", "LocalStrength", "UnityWorks"],
                        "location": ["urban communities", "underserved regions", "developing markets", "local neighborhoods", "global operations"],
                        "year": lambda: random.randint(2018, 2024),
                        "beneficiaries": lambda: f"{random.randint(1, 50):,}000",
                        "focus_area": ["education access", "healthcare equity", "digital inclusion", "skills development", "economic empowerment"],
                        "amount": lambda: f"{random.randint(500, 5000):,}000",
                        "volunteer_hours": lambda: f"{random.randint(5, 50):,}000",
                        "outcome1": ["community resilience", "youth employment", "gender equality", "financial inclusion", "social mobility"],
                        "outcome2": ["public health indicators", "educational outcomes", "local economic growth", "social cohesion", "quality of life measures"],
                        "stakeholder": ["Dr. Sarah Johnson", "Michael Rodriguez", "Emma Chen", "Dr. Robert Williams", "Fatima Al-Hassan"],
                        "title": ["Director", "Community Leader", "Program Evaluator", "Chief Impact Officer", "Executive Director"],
                        "organization": ["Community Foundation", "Social Progress Institute", "Impact Measurement Alliance", "Regional Development Authority", "United Communities Network"],
                        "quote": ["This program demonstrates how corporate investment can create genuine social value when designed with community needs at its center.", "The data shows clear improvement across key social indicators, setting a new standard for corporate community engagement.", "We've seen unprecedented levels of collaboration between business and community stakeholders through this initiative."]
                    }
                },
                {
                    "title_template": "Breaking Barriers: {company}'s Groundbreaking {diversity_type} Initiative Shows Promising Results",
                    "content_template": "{company} has released the first-year results of its {program_name} initiative, showing significant progress in {diversity_type}. The company has increased representation of {group} by {percent}% across {level} positions. Key elements of the program include {element1}, {element2}, and {element3}. The initiative has also contributed to a {business_outcome}% improvement in {business_metric}, supporting the business case for diversity and inclusion. {executive}, {title} at {company}, stated: '{quote}'",
                    "variables": {
                        "company": ["DiversityWorks", "InclusionTech", "EquityNow", "FairFuture Inc", "UnityForward"],
                        "program_name": ["AllVoices", "Inclusive Growth", "Diversity Accelerator", "Equal Opportunity Initiative", "Representation Matters"],
                        "diversity_type": ["Gender Diversity", "Racial Equity", "Disability Inclusion", "Age Diversity", "Socioeconomic Inclusion"],
                        "group": ["women", "underrepresented minorities", "people with disabilities", "first-generation professionals", "LGBTQ+ individuals"],
                        "percent": lambda: random.randint(20, 60),
                        "level": ["leadership", "technical", "professional", "entry-level", "board-level"],
                        "element1": ["targeted recruitment strategies", "mentorship programs", "inclusive policy development", "bias training", "community partnerships"],
                        "element2": ["transparent pay practices", "flexible working arrangements", "career development pathways", "sponsorship programs", "accessibility improvements"],
                        "element3": ["accountability metrics", "cultural competence building", "employee resource groups", "inclusive leadership training", "supplier diversity"],
                        "business_outcome": lambda: random.randint(10, 40),
                        "business_metric": ["employee engagement", "innovation outputs", "talent retention", "customer satisfaction", "market expansion"],
                        "executive": ["Maria Rodriguez", "Dr. James Chen", "Aisha Johnson", "Thomas Williams", "Sarah Patel"],
                        "title": ["Chief Diversity Officer", "VP of People", "Head of Inclusion", "CEO", "Director of Equity Programs"],
                        "quote": ["The data clearly shows that our focus on inclusion isn't just the right thing to do—it's also driving stronger business results.", "We're seeing how diverse perspectives lead to better decision-making and more innovative solutions to complex challenges.", "This is just the beginning of our journey to create a truly inclusive organization that reflects the diversity of the communities we serve."]
                    }
                }
            ],
            "governance": [
                {
                    "title_template": "{company} Sets New Standard for {governance_area} with Industry-Leading Framework",
                    "content_template": "{company} has introduced a comprehensive framework for {governance_area}, setting a new benchmark in the {industry} sector. The approach incorporates {element1}, {element2}, and {element3}, addressing key stakeholder concerns about {concern}. Independent verification by {organization} confirmed that the framework exceeds regulatory requirements by implementing {percent}% more rigorous standards than mandated. {executive}, {title} at {company}, explained: '{quote}' The company has committed to {commitment} by {year}.",
                    "variables": {
                        "company": ["Governance Solutions", "IntegrityFirst", "Compliance Innovations", "TrustGuard Inc", "TransparencyTech"],
                        "governance_area": ["Board Oversight", "Executive Accountability", "Risk Management", "Corporate Transparency", "Stakeholder Engagement"],
                        "industry": ["financial services", "healthcare", "technology", "manufacturing", "energy"],
                        "element1": ["independent verification mechanisms", "stakeholder advisory panels", "real-time compliance monitoring", "ethical decision frameworks", "transparent reporting structures"],
                        "element2": ["comprehensive code of conduct", "advanced data governance", "robust grievance mechanisms", "conflict of interest policies", "executive compensation alignment"],
                        "element3": ["third-party due diligence", "scenario-based risk testing", "ethical leadership development", "whistleblower protections", "policy effectiveness reviews"],
                        "concern": ["systemic risk", "conflicts of interest", "regulatory compliance", "ethical decision-making", "accountability gaps"],
                        "organization": ["Governance Standards Institute", "Corporate Ethics Review Board", "Regulatory Excellence Commission", "International Transparency Council", "Compliance Certification Authority"],
                        "percent": lambda: random.randint(30, 75),
                        "executive": ["Richard Thompson", "Dr. Lisa Chen", "Michael Adebayo", "Jennifer Williams", "Robert Gupta"],
                        "title": ["Chief Governance Officer", "Head of Corporate Affairs", "Lead Independent Director", "Ethics Committee Chair", "General Counsel"],
                        "quote": ["We recognize that robust governance is foundational to sustainable business success and stakeholder trust.", "Our approach moves beyond compliance to create genuine accountability and transparency throughout the organization.", "This framework enables us to anticipate and address emerging governance challenges in an increasingly complex business environment."],
                        "commitment": ["annual independent governance reviews", "expanded stakeholder reporting", "governance performance-linked compensation", "board diversity targets", "enhanced risk disclosure"],
                        "year": lambda: random.randint(2025, 2030)
                    }
                },
                {
                    "title_template": "Breakthrough in {reporting_type}: {company}'s New Approach to Transparency",
                    "content_template": "{company} has launched an innovative approach to {reporting_type}, addressing long-standing challenges in corporate disclosure. The {technology}-enabled system provides {frequency} visibility into {data_area}, allowing stakeholders to {stakeholder_action}. The initiative was developed in partnership with {partner} and incorporates feedback from {stakeholder_group}. Early results show {percent}% improvement in {metric}, with {organization} recognizing the company as a {recognition}. {executive}, {company}'s {title}, noted: '{quote}'",
                    "variables": {
                        "company": ["DataTrust", "TransparenTech", "Disclosure Dynamics", "Clarity Systems", "ReportingRevolution"],
                        "reporting_type": ["ESG Disclosure", "Financial Transparency", "Impact Reporting", "Risk Disclosure", "Performance Transparency"],
                        "technology": ["blockchain", "AI-powered", "real-time", "integrated", "multi-stakeholder"],
                        "frequency": ["real-time", "dynamic", "quarterly", "continuous", "interactive"],
                        "data_area": ["sustainability performance", "governance practices", "supply chain compliance", "climate risk exposure", "stakeholder engagement"],
                        "stakeholder_action": ["track progress against commitments", "compare performance across peers", "verify reported information", "understand complex data relationships", "engage directly with management"],
                        "partner": ["Transparency International", "Accounting Standards Board", "Sustainability Consortium", "Digital Ethics Institute", "Global Reporting Initiative"],
                        "stakeholder_group": ["investors", "regulators", "customers", "civil society organizations", "industry peers"],
                        "percent": lambda: random.randint(40, 85),
                        "metric": ["data accuracy", "reporting timeliness", "stakeholder trust", "information accessibility", "disclosure completeness"],
                        "organization": ["World Economic Forum", "International Standards Organization", "Corporate Reporting Dialogue", "Transparency Awards", "ESG Reporting Council"],
                        "recognition": ["transparency leader", "disclosure innovator", "reporting excellence award winner", "accountability champion", "governance pacesetter"],
                        "executive": ["Dr. Katherine Johnson", "Samuel Chen", "Elizabeth Rodriguez", "Marcus Thompson", "Priya Patel"],
                        "title": ["Chief Transparency Officer", "Head of Stakeholder Relations", "Director of Corporate Affairs", "Senior VP of Governance", "Reporting Innovation Lead"],
                        "quote": ["This approach fundamentally reimagines corporate disclosure for the digital age, moving beyond static reports to dynamic, verifiable information.", "We're setting a new standard that makes complex corporate information more accessible, comparable, and actionable for all stakeholders.", "Transparency isn't just about sharing more data—it's about providing meaningful, verified information that builds trust and enables better decision-making."]
                    }
                }
            ],
            "economic": [
                {
                    "title_template": "{company} Demonstrates {percent}% ROI from {sustainability_area} Investments",
                    "content_template": "A rigorous financial analysis of {company}'s investments in {sustainability_area} has demonstrated a {percent}% return on investment over {timeframe} years. The company allocated {amount} USD to initiatives including {initiative1} and {initiative2}, generating both direct financial returns and {benefit_type} benefits. Key value drivers included {driver1}, {driver2}, and {driver3}. {expert}, {title} at {organization}, noted: '{quote}' The company plans to scale this approach across {scale_area} operations by {year}.",
                    "variables": {
                        "company": ["EcoValue", "SustainROI", "GreenProfit", "EcoFinance", "ResourceReturns"],
                        "percent": lambda: random.randint(15, 45),
                        "sustainability_area": ["Energy Efficiency", "Circular Economy", "Sustainable Sourcing", "Clean Technology", "Water Stewardship"],
                        "timeframe": lambda: random.randint(3, 7),
                        "amount": lambda: f"{random.randint(5, 50):,} million",
                        "initiative1": ["facility retrofits", "process optimization", "supplier development programs", "product redesign", "efficiency technologies"],
                        "initiative2": ["renewable energy installations", "waste reduction systems", "supply chain digitization", "material innovation", "closed-loop manufacturing"],
                        "benefit_type": ["operational", "reputational", "risk mitigation", "market differentiation", "regulatory compliance"],
                        "driver1": ["reduced operational costs", "increased resource productivity", "enhanced customer loyalty", "preemptive regulatory compliance", "improved access to capital"],
                        "driver2": ["waste valorization", "extended product lifecycles", "reduced commodity price exposure", "talent attraction and retention", "supply chain resilience"],
                        "driver3": ["new market opportunities", "reduced insurance premiums", "increased stakeholder trust", "enhanced innovation capabilities", "brand value enhancement"],
                        "expert": ["Dr. Jonathan Miller", "Prof. Sophia Chen", "Alejandro Rodriguez", "Dr. Katherine Williams", "Mohammed Al-Faisal"],
                        "title": ["Sustainable Finance Director", "Chief Economist", "Investment Analyst", "Sustainability ROI Expert", "Capital Markets Strategist"],
                        "organization": ["Sustainable Investment Institute", "Economic Analysis Group", "Corporate Value Research", "Environment-Financial Integration Council", "Business Sustainability Forum"],
                        "quote": ["This analysis demonstrates conclusively that well-designed sustainability initiatives can deliver superior financial returns while creating environmental and social value.", "The comprehensive methodology applied here sets a new standard for measuring the true return on sustainability investments.", "These results challenge the persistent myth that sustainability requires financial trade-offs—when executed strategically, it clearly enhances enterprise value."],
                        "scale_area": ["global", "regional", "manufacturing", "recently acquired", "downstream"],
                        "year": lambda: random.randint(2025, 2028)
                    }
                },
                {
                    "title_template": "Pioneering {business_model}: {company}'s Transition to {economic_approach}",
                    "content_template": "{company} has successfully transitioned to a {business_model} model, demonstrating the viability of {economic_approach} in the {industry} sector. The {timeframe}-year transformation involved {element1}, {element2}, and collaboration with {partners}. Financial results include {financial_result1} and {financial_result2}, while creating {impact} positive impact. {executive}, {company}'s {title}, explained: '{quote1}' Industry analysts have noted that this approach could {industry_impact}, with {analyst}, {analyst_title} at {firm}, commenting: '{quote2}'",
                    "variables": {
                        "company": ["CircularSolutions", "RegenerativeEnterprises", "ValueLoopCorp", "SustainableVentures", "EcoSystemsInc"],
                        "business_model": ["Product-as-a-Service", "Circular Economy", "Regenerative Business", "Shared Value", "Stakeholder Capitalism"],
                        "economic_approach": ["life-cycle value creation", "regenerative economics", "closed-loop systems", "service-based revenue", "embedded sustainability"],
                        "industry": ["manufacturing", "consumer goods", "technology", "industrial", "retail"],
                        "timeframe": lambda: random.randint(2, 5),
                        "element1": ["business model redesign", "stakeholder co-creation processes", "value chain transformation", "digital enablement", "lifecycle management systems"],
                        "element2": ["performance metrics realignment", "customer relationship evolution", "financing structure innovation", "talent capability building", "governance adaptation"],
                        "partners": ["industry consortia", "academic institutions", "technology providers", "policy stakeholders", "community organizations"],
                        "financial_result1": ["20% revenue growth from sustainable offerings", "35% improvement in customer retention", "40% reduction in resource input costs", "15% price premium in target segments", "25% decrease in capital intensity"],
                        "financial_result2": ["increased resilience to supply disruptions", "enhanced access to sustainability-linked financing", "reduced regulatory compliance costs", "improved asset utilization rates", "new revenue streams from previously discarded materials"],
                        "impact": ["environmental", "social", "community", "ecosystem", "market"],
                        "executive": ["Alexandra Chen", "Dr. Michael Rodriguez", "Sarah Thompson", "Raj Patel", "Dr. Emma Williams"],
                        "title": ["Chief Sustainability Officer", "Business Transformation Lead", "CEO", "Head of Circular Economy", "VP of Sustainable Business"],
                        "quote1": ["This transformation required rethinking our entire approach to value creation, moving beyond incremental efficiency to fundamental business model innovation.", "We've demonstrated that economic success and positive impact aren't trade-offs but mutually reinforcing when designed thoughtfully from the ground up.", "This wasn't just about doing less harm—it was about reimagining our business to be regenerative by design, creating value for all stakeholders."],
                        "industry_impact": ["redefine competition in the sector", "accelerate similar transitions across the industry", "establish new best practices for sustainable business", "drive broader economic system change", "create pressure for policy evolution"],
                        "analyst": ["James Wilson", "Dr. Maria Garcia", "Thomas Zhang", "Dr. Olivia Johnson", "Ahmed Al-Farsi"],
                        "analyst_title": ["Senior Industry Analyst", "Sustainability Economics Researcher", "Market Transformation Expert", "Director of Future Business Models", "Chief Analyst"],
                        "firm": ["Future Markets Institute", "Industry Transformation Group", "Sustainable Business Research", "NextEconomy Partners", "Market Evolution Advisors"],
                        "quote2": ["This case demonstrates that business model innovation is the next frontier of competitive advantage in a resource-constrained, stakeholder-driven market.", "The financial results challenge conventional wisdom about the economics of sustainability and signal a fundamental shift in how value creation is understood.", "Early movers in this transformation stand to capture disproportionate market share and influence industry standards for years to come."]
                    }
                }
            ],
            "climate": [
                {
                    "title_template": "{company} Achieves {percent}% Emissions Reduction Through {strategy} Strategy",
                    "content_template": "{company} has announced a {percent}% reduction in {scope} emissions, {timeframe} ahead of its science-based targets. The achievement comes through implementation of a comprehensive {strategy} strategy across {operations} operations. Key initiatives included {initiative1}, {initiative2}, and {initiative3}, resulting in both emissions reductions and {financial_impact}. {executive}, {company}'s {title}, stated: '{quote}' The company plans to reach {future_goal} by {year}, aligning with {standard}.",
                    "variables": {
                        "company": ["ClimateSolutions", "CarbonTransition", "NetZeroCorp", "ClimateLeaders", "EmissionsTech"],
                        "percent": lambda: random.randint(25, 65),
                        "scope": ["Scope 1 and 2", "value chain", "product lifecycle", "operational", "absolute"],
                        "timeframe": ["two years", "18 months", "one year", "three years", "six months"],
                        "strategy": ["Deep Decarbonization", "Carbon-Smart", "Climate Positive", "Zero Carbon", "Climate Resilience"],
                        "operations": ["global", "manufacturing", "supply chain", "product", "enterprise-wide"],
                        "initiative1": ["renewable energy transition", "electrification of operations", "process efficiency improvements", "materials innovation", "low-carbon logistics"],
                        "initiative2": ["digital twin optimization", "supplier engagement programs", "circular material flows", "energy storage deployment", "heat recovery systems"],
                        "initiative3": ["carbon insetting projects", "clean energy investment", "refrigerant management", "alternative feedstocks", "building retrofits"],
                        "financial_impact": ["$15 million in annual energy savings", "20% reduction in operating costs", "enhanced access to green financing", "5% improvement in margins", "$25 million in avoided carbon costs"],
                        "executive": ["Dr. Rebecca Thompson", "Michael Chen", "Sarah Rodriguez", "James Wilson", "Fatima Al-Harbi"],
                        "title": ["Chief Climate Officer", "VP of Sustainability", "Head of Climate Strategy", "CEO", "Director of Decarbonization"],
                        "quote": ["This milestone demonstrates that ambitious climate action can drive business value when fully integrated into corporate strategy.", "We've proven that decarbonization at scale is not only possible but economically advantageous when approached systematically.", "This achievement reflects our understanding that climate leadership is essential for long-term competitiveness and stakeholder trust."],
                        "future_goal": ["net-zero emissions", "carbon negative operations", "climate positive value chain", "absolute zero emissions", "1.5°C-aligned operations"],
                        "year": lambda: random.randint(2030, 2040),
                        "standard": ["the Paris Agreement", "Science Based Targets initiative", "Race to Zero criteria", "Climate Neutral standards", "Net Zero Initiative framework"]
                    }
                },
                {
                    "title_template": "Groundbreaking Climate Resilience: {company}'s Innovative Approach to {risk_area}",
                    "content_template": "{company} has implemented an innovative approach to managing {risk_area} climate risks across its {operations} operations. The {timeframe}-year program combines {element1}, {element2}, and {element3}, reducing vulnerability by {percent}%. The company invested {amount} in this initiative, which has already prevented approximately {prevented_impact} in potential climate-related disruptions. The approach was developed in collaboration with {partner} and has been recognized by {organization} as {recognition}. {executive}, {company}'s {title}, explained: '{quote}'",
                    "variables": {
                        "company": ["ResilienceTech", "ClimateAdapt", "RiskReady", "ClimateSecure", "AdaptiveEnterprises"],
                        "risk_area": ["physical", "transition", "water-related", "supply chain", "infrastructure"],
                        "operations": ["global", "critical", "high-risk", "customer-facing", "production"],
                        "timeframe": lambda: random.randint(2, 5),
                        "element1": ["scenario-based risk modeling", "climate-adaptive design", "early warning systems", "natural infrastructure solutions", "decentralized energy systems"],
                        "element2": ["supplier resilience programs", "climate stress testing", "redundancy planning", "natural hazard management", "flexible production capabilities"],
                        "element3": ["community resilience partnerships", "climate risk disclosure", "cross-industry collaboration", "nature-based solutions", "dynamic resource allocation"],
                        "percent": lambda: random.randint(40, 85),
                        "amount": lambda: f"{random.randint(10, 100):,} million",
                        "prevented_impact": lambda: f"{random.randint(30, 200):,} million in damages",
                        "partner": ["Climate Resilience Institute", "Engineering Research Consortium", "Regional Adaptation Network", "Risk Management Authority", "Sustainable Infrastructure Alliance"],
                        "organization": ["World Economic Forum", "United Nations Office for Disaster Risk Reduction", "Global Adaptation Commission", "Insurance Industry Climate Initiative", "Climate Risk Standards Board"],
                        "recognition": ["leading practice", "innovation in resilience", "climate-ready business model", "resilience excellence", "adaptive management benchmark"],
                        "executive": ["Dr. Jason Chen", "Maria Rodriguez", "Robert Williams", "Dr. Aisha Johnson", "Thomas Kumar"],
                        "title": ["Chief Resilience Officer", "Head of Climate Risk", "VP of Business Continuity", "Director of Climate Strategy", "Adaptation Program Lead"],
                        "quote": ["Climate resilience is no longer optional—it's a core business imperative that protects value and enables long-term success in a changing world.", "This approach moves beyond risk management to strategic opportunity, positioning us to thrive in conditions where others may struggle.", "We've developed a methodology that quantifies climate resilience in financial terms, allowing us to make investment decisions that optimize both protection and growth."]
                    }
                }
            ]
        }
        
        # Generate mock data
        result = []
        
        # Filter categories if specified
        if category:
            categories_to_use = [category] if category in story_categories else story_categories
        else:
            categories_to_use = story_categories
        
        # Calculate date range
        now = datetime.now()
        if not start_date:
            start_date = now - timedelta(days=365)  # Default to last year
        if not end_date:
            end_date = now
            
        # Create a realistic distribution of dates
        date_weights = {
            7: 0.3,    # Last week (30%)
            30: 0.25,  # Last month (25%)
            90: 0.2,   # Last quarter (20%)
            180: 0.15, # Last 6 months (15%)
            365: 0.1   # Last year (10%)
        }
        
        # Generate stories for each category
        total_stories = skip  # Start counter at skip value
        all_stories = []
        
        for cat in categories_to_use:
            # Get templates for this category
            templates = story_templates.get(cat, [])
            if not templates:
                continue
                
            # Generate multiple stories per template
            stories_per_template = max(20 // len(templates), 1)  # Distribute evenly
            
            for template in templates:
                for _ in range(stories_per_template):
                    # Determine publication date
                    days_ago_bracket = random.choices(
                        list(date_weights.keys()),
                        weights=list(date_weights.values()),
                        k=1
                    )[0]
                    
                    days_ago = random.randint(1, days_ago_bracket)
                    publication_date = now - timedelta(days=days_ago)
                    
                    # Skip if outside requested date range
                    if publication_date < start_date or publication_date > end_date:
                        continue
                    
                    # Generate story variables
                    variables = {}
                    for var_name, var_values in template["variables"].items():
                        if callable(var_values):
                            variables[var_name] = var_values()
                        else:
                            variables[var_name] = random.choice(var_values)
                    
                    # Generate title and content
                    title = template["title_template"].format(**variables)
                    content = template["content_template"].format(**variables)
                    
                    # Generate tags
                    possible_tags = [
                        "innovation", "best practice", "case study", "leadership",
                        "technology", "collaboration", "science-based", "measurable impact",
                        "long-term value", "stakeholder engagement", cat
                    ]
                    story_tags = random.sample(possible_tags, random.randint(3, 5))
                    
                    # Skip if tags filter is applied and doesn't match
                    if tags and not any(tag in tags for tag in story_tags):
                        continue
                    
                    # Create story
                    story = {
                        "id": f"story_{total_stories + 1}",
                        "title": title,
                        "content": content,
                        "category": cat,
                        "tags": story_tags,
                        "publication_date": publication_date.isoformat(),
                        "author": "SustainaTrend Editorial Team",
                        "reading_time": random.randint(3, 10),
                        "image_url": f"/static/images/story_{random.randint(1, 10)}.jpg"
                    }
                    
                    all_stories.append(story)
                    total_stories += 1
        
        # Sort by publication date (most recent first)
        all_stories.sort(key=lambda x: x["publication_date"], reverse=True)
        
        # Apply skip and limit
        result = all_stories[skip:skip+limit]
        
        logger.info(f"Returning {len(result)} mock stories")
        return result
    
    @classmethod
    def get_categories(cls) -> List[str]:
        """
        Get all unique categories from the metrics collection
        
        Returns:
            List of unique category names
        """
        logger.info("Mock categories requested")
        return ["environmental", "social", "governance", "economic", "climate"]
    
    @classmethod
    def insert_metric(cls, metric_data: Dict[str, Any]) -> Optional[str]:
        """
        Insert a new sustainability metric (mock)
        
        Args:
            metric_data: Metric data to insert
            
        Returns:
            Mock ID of inserted document
        """
        logger.info(f"Mock metric insertion: {metric_data.get('name', 'Unknown')}")
        return f"mock_metric_{random.randint(1000, 9999)}"
    
    @classmethod
    def insert_trend(cls, trend_data: Dict[str, Any]) -> Optional[str]:
        """
        Insert a new sustainability trend (mock)
        
        Args:
            trend_data: Trend data to insert
            
        Returns:
            Mock ID of inserted document
        """
        logger.info(f"Mock trend insertion: {trend_data.get('name', 'Unknown')}")
        return f"mock_trend_{random.randint(1000, 9999)}"
    
    @classmethod
    def insert_story(cls, story_data: Dict[str, Any]) -> Optional[str]:
        """
        Insert a new sustainability story (mock)
        
        Args:
            story_data: Story data to insert
            
        Returns:
            Mock ID of inserted document
        """
        logger.info(f"Mock story insertion: {story_data.get('title', 'Unknown')}")
        return f"mock_story_{random.randint(1000, 9999)}"