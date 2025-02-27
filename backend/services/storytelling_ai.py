"""
AI-Powered Sustainability Storytelling Service
Uses LangChain and OpenAI to generate strategic narratives for sustainability
that align with McKinsey frameworks and provide investment and monetization pathways.
"""
import os
import json
import logging
from datetime import datetime
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import LangChain components, but provide fallbacks if not available
try:
    from langchain.chat_models import ChatOpenAI
    from langchain.chains import RetrievalQA
    LANGCHAIN_AVAILABLE = True
except ImportError:
    logger.warning("LangChain not available. Using mock storytelling.")
    LANGCHAIN_AVAILABLE = False

def generate_sustainability_story(company_name, industry):
    """
    Generate an AI-powered sustainability transformation story

    Args:
        company_name (str): Name of the company
        industry (str): Industry the company operates in

    Returns:
        dict: Structured sustainability story with strategy, monetization model,
              investment pathway, and actionable recommendations
    """
    logger.info(f"Generating sustainability story for {company_name} in {industry} industry")

    # Check if OpenAI API key is available
    openai_api_key = os.getenv('OPENAI_API_KEY')

    if openai_api_key and LANGCHAIN_AVAILABLE:
        try:
            # Use LangChain and OpenAI to generate the story
            prompt = f"""
            Create an **AI-powered sustainability transformation story** for {company_name} in the {industry} industry.

            ## Chain of Thought Analysis

            1. **Industry Analysis**: Analyze the {industry} industry's key sustainability challenges, opportunities, and emerging regulations.
            2. **Competitor Benchmarking**: Identify how leading companies in {industry} are differentiating through sustainability initiatives.
            3. **Materiality Assessment**: Determine which sustainability issues are most material to {company_name}'s financial performance.
            4. **Value Chain Mapping**: Analyze where in {company_name}'s value chain sustainability initiatives would create the most impact.
            5. **Financial Impact Projection**: Predict how sustainability initiatives would affect revenue growth, cost reduction, risk mitigation, and brand value.

            ## Strategic Frameworks

            📌 **Strategic Storytelling Using Advanced McKinsey Frameworks**  
            - **Horizon Model**: Short-term (compliance), medium-term (efficiency), and long-term (transformation) sustainability roadmap  
            - **7-S Framework**: Align strategy, structure, systems, shared values, skills, style, and staff around sustainability
            - **Business Flywheel**: Create a self-reinforcing sustainability business model similar to Amazon, Netflix, or LinkedIn  
            - **Three Horizons of Growth**: Balance managing existing businesses, nurturing emerging businesses, and creating viable options
            - **CSRD Compliance**: Map sustainability impact to EU Corporate Sustainability Reporting Directive metrics
            - **Competitor SWOT Analysis**: Identify sustainability-related strengths, weaknesses, opportunities, and threats vs. competitors

            🎯 **Key Insights & Monetization Strategy**  
            - What sustainability initiatives {company_name} should prioritize for maximum business impact?  
            - How can they **monetize sustainability data and initiatives**?  
            - What investment pathways (venture capital, grants, debt, green bonds) should they pursue?
            - How can {company_name} use sustainability as a competitive advantage in {industry}?
            - What sustainability-linked performance metrics should executives be measured on?

            Format the response as a JSON object with these keys:
            {{
              "Company": "{company_name}",
              "Industry": "{industry}",
              "Industry_Context": "Analysis of {industry} sustainability trends and competitive landscape",
              "Sustainability_Strategy": "Comprehensive strategy with short, medium, and long-term horizons",
              "Competitor_Benchmarking": "How {company_name} compares to industry leaders on key sustainability metrics",
              "Monetization_Model": "Business model for generating revenue from sustainability initiatives",
              "Investment_Pathway": "Financial strategy for funding sustainability transformation",
              "Actionable_Recommendations": ["Specific action 1", "Specific action 2", "Specific action 3"],
              "Performance_Metrics": ["Metric 1", "Metric 2", "Metric 3"],
              "Estimated_Financial_Impact": {{"Revenue_Growth": "+X%", "Cost_Reduction": "-Y%", "Risk_Mitigation": "Z description"}}
            }}
            """

            llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.4)
            response = RetrievalQA.from_chain_type(llm, chain_type="stuff").run(prompt)

            # Try to parse the response as JSON
            try:
                if isinstance(response, str):
                    return json.loads(response)
                return response
            except json.JSONDecodeError:
                logger.warning("Failed to parse AI response as JSON, returning raw response")
                return {
                    "Company": company_name,
                    "Industry": industry,
                    "Sustainability_Strategy": response,
                    "Monetization_Model": "Could not generate",
                    "Investment_Pathway": "Could not generate",
                    "Actionable_Recommendations": ["Please try again with more specific information"]
                }

        except Exception as e:
            logger.error(f"Error using LangChain/OpenAI for storytelling: {str(e)}")
            return generate_mock_sustainability_story(company_name, industry)
    else:
        logger.warning("OpenAI API key not available or LangChain not installed. Using mock storytelling.")
        return generate_mock_sustainability_story(company_name, industry)

def generate_mock_sustainability_story(company_name, industry):
    """
    Generate a mock sustainability story when OpenAI is not available

    Args:
        company_name (str): Name of the company
        industry (str): Industry the company operates in

    Returns:
        dict: Mock sustainability story
    """
    logger.info(f"Generating mock sustainability story for {company_name}")

    # Industry-specific strategy templates
    industry_strategies = {
        "technology": f"{company_name} will focus on reducing e-waste, improving energy efficiency in data centers, and developing sustainable software engineering practices.",
        "manufacturing": f"{company_name} will implement circular economy principles in production, reduce emissions through process optimization, and invest in renewable energy for facilities.",
        "retail": f"{company_name} will create sustainable supply chains, reduce packaging waste, and implement green store designs with energy-efficient operations.",
        "energy": f"{company_name} will accelerate transition to renewable energy sources, implement carbon capture technologies, and optimize grid efficiency.",
        "healthcare": f"{company_name} will reduce medical waste, implement green facility management, and develop sustainable healthcare delivery models.",
        "finance": f"{company_name} will develop ESG investment products, implement sustainable lending practices, and reduce operational carbon footprint.",
        "transportation": f"{company_name} will electrify fleet vehicles, optimize logistics for emissions reduction, and develop sustainable mobility solutions.",
    }

    # Default strategy for industries not in our templates
    default_strategy = f"{company_name} will implement a comprehensive sustainability program focusing on emissions reduction, resource efficiency, and stakeholder engagement."

    # Get the appropriate strategy based on industry
    strategy = industry_strategies.get(industry.lower(), default_strategy)

    # Industry benchmarking insights
    benchmarking_insights = {
        "technology": [
            f"{company_name} is currently behind industry leaders like Microsoft and Google in renewable energy adoption",
            "Software sustainability practices are emerging as a differentiator",
            "Data center energy efficiency is a key competitive metric in the industry"
        ],
        "manufacturing": [
            f"Industry leaders are achieving 30-40% higher resource efficiency than {company_name}",
            "Circular economy models are generating new revenue streams for competitors",
            "Sustainable supply chains are reducing costs by 15-20% for industry leaders"
        ],
        "retail": [
            f"{company_name}'s packaging waste reduction is 25% below the industry average",
            "Leading retailers are achieving price premiums of 20-25% for sustainable products",
            "Sustainable store designs are reducing energy costs by 35% for industry leaders"
        ]
    }

    # Default benchmarking for industries not in our templates
    default_benchmarking = [
        f"{company_name} is in the middle tier of sustainability performers in the {industry} industry",
        "Leading companies are achieving stronger financial returns from sustainability initiatives",
        "Regulatory compliance is the minimum standard, while leaders are going far beyond"
    ]

    # Get the appropriate benchmarking based on industry
    benchmark = benchmarking_insights.get(industry.lower(), default_benchmarking)

    # Generate monetization models
    monetization_models = [
        f"Sustainability Data Analytics Platform: {company_name} can monetize its sustainability data by creating an analytics platform that provides benchmarking, insights, and reporting capabilities for other companies in the {industry} industry.",
        f"Sustainability Consulting Services: {company_name} can leverage its expertise to offer consulting services to other organizations looking to improve their sustainability performance.",
        f"Carbon Offset Marketplace: {company_name} can develop a marketplace connecting carbon offset projects with businesses seeking to achieve carbon neutrality.",
        f"Sustainability-as-a-Service (SaaS): {company_name} can offer subscription-based services for ongoing sustainability management, reporting, and optimization.",
        f"Green Product Certification: {company_name} can develop a certification program for sustainable products in the {industry} sector, generating revenue through certification fees.",
        f"Sustainability-Linked Financing: {company_name} can structure innovative financial products with interest rates tied to achieving sustainability targets."
    ]

    # Generate investment pathways
    investment_pathways = [
        f"Green Bonds: {company_name} should issue green bonds to finance specific climate and environmental projects, accessing the growing sustainable debt market.",
        f"Sustainability-Linked Loans: {company_name} can negotiate loans with interest rates tied to achieving sustainability performance targets.",
        f"Venture Capital for Green Innovation: {company_name} should seek venture capital funding for developing innovative sustainable technologies and solutions.",
        f"Government Grants: {company_name} should pursue government grants and incentives for renewable energy adoption and emissions reduction projects.",
        f"Strategic Partnerships: {company_name} should form strategic partnerships with sustainability-focused investors and organizations for joint ventures.",
        f"Green Investment Fund: {company_name} should establish a dedicated fund for investments in sustainability startups and technologies aligned with its core business."
    ]

    # Generate recommendations
    recommendations = [
        f"Implement science-based targets for emissions reduction aligned with a 1.5°C pathway",
        f"Develop a comprehensive ESG data management system to improve reporting accuracy and efficiency",
        f"Conduct a full supply chain sustainability assessment to identify hotspots and opportunities",
        f"Invest in renewable energy through on-site generation and power purchase agreements",
        f"Train employees on sustainability principles and integrate into performance metrics",
        f"Engage with industry associations to develop sector-specific sustainability standards",
        f"Launch a product innovation initiative focused on circular economy principles",
        f"Implement water conservation technologies across operations",
        f"Develop a sustainability-linked executive compensation program",
        f"Create a sustainability data monetization strategy",
        f"Establish a green finance framework for accessing sustainability-linked capital",
        f"Conduct competitor benchmarking on key sustainability metrics"
    ]

    # Generate performance metrics
    performance_metrics = [
        "Scope 1, 2, and 3 greenhouse gas emissions (tCO2e)",
        "Energy efficiency (kWh per unit of production/revenue)",
        "Water consumption intensity (gallons per unit of production/revenue)",
        "Waste diversion rate (%)",
        "Renewable energy adoption (%)",
        "Sustainability-linked revenue (%)",
        "Employee sustainability engagement score",
        "Supplier sustainability assessment completion rate (%)",
        "ESG rating improvement (year-over-year)",
        "Sustainability R&D investment (% of revenue)"
    ]

    # Generate estimated financial impact
    financial_impact = {
        "Revenue_Growth": f"+{random.randint(5, 15)}%",
        "Cost_Reduction": f"-{random.randint(10, 25)}%",
        "Risk_Mitigation": "Reduced regulatory penalties and improved investor sentiment"
    }

    # Create the mock story
    story = {
        "Company": company_name,
        "Industry": industry,
        "Industry_Context": f"The {industry} industry is facing increasing regulatory pressure, shifting consumer preferences toward sustainable products, and investor scrutiny on ESG performance.",
        "Sustainability_Strategy": strategy,
        "Competitor_Benchmarking": benchmark,
        "Monetization_Model": random.choice(monetization_models),
        "Investment_Pathway": random.choice(investment_pathways),
        "Actionable_Recommendations": random.sample(recommendations, 4),
        "Performance_Metrics": random.sample(performance_metrics, 3),
        "Estimated_Financial_Impact": financial_impact
    }

    return story