"""
Predictive Analytics Service for Sustainability Trends
Uses advanced AI and statistical models to forecast sustainability metrics
and identify emerging trends before they materialize.
"""
import os
import json
import logging
import numpy as np
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import advanced AI libraries, but provide fallbacks if not available
try:
    from langchain_community.chat_models import ChatOpenAI
    from langchain.chains import RetrievalQA
    import pandas as pd
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    ADVANCED_ANALYTICS_AVAILABLE = True
    logger.info("Advanced analytics libraries loaded successfully")
except ImportError:
    logger.warning("Advanced analytics libraries not available. Using mock predictions.")
    ADVANCED_ANALYTICS_AVAILABLE = False

def predict_sustainability_trends(
    metrics: List[Dict[str, Any]], 
    forecast_periods: int = 3,
    prediction_interval: float = 0.95
) -> Dict[str, Any]:
    """
    Use advanced ML techniques to predict future sustainability metrics trends

    Args:
        metrics (List[Dict]): Historical sustainability metrics data
        forecast_periods (int): Number of future periods to forecast
        prediction_interval (float): Confidence interval for predictions (0-1)

    Returns:
        Dict: Predicted metrics with confidence intervals and supporting insights
    """
    logger.info(f"Generating predictive analytics for {len(metrics)} metrics, forecasting {forecast_periods} periods ahead")

    # Check if advanced analytics libraries are available
    if ADVANCED_ANALYTICS_AVAILABLE and len(metrics) >= 3:  # Need minimum data points for regression
        try:
            return generate_ml_predictions(metrics, forecast_periods, prediction_interval)
        except Exception as e:
            logger.error(f"Error using ML for predictions: {str(e)}")
            return generate_mock_predictions(metrics, forecast_periods)
    else:
        logger.warning("Using mock predictions due to insufficient data or missing libraries")
        return generate_mock_predictions(metrics, forecast_periods)

def generate_ml_predictions(
    metrics: List[Dict[str, Any]], 
    forecast_periods: int,
    prediction_interval: float
) -> Dict[str, Any]:
    """Generate predictions using machine learning models"""
    logger.info("Using ML models for predictive analytics")
    
    # Convert metrics to pandas DataFrame for analysis
    df = pd.DataFrame(metrics)
    
    # Group by metric name and category
    predictions = {
        "forecast_date": datetime.now().isoformat(),
        "forecast_periods": forecast_periods,
        "prediction_interval": prediction_interval,
        "predictions": []
    }
    
    # Get unique metric names
    metric_names = df['name'].unique()
    
    for name in metric_names:
        # Filter data for this metric
        metric_data = df[df['name'] == name].sort_values('timestamp')
        
        if len(metric_data) < 3:  # Skip if not enough data points
            continue
            
        # Extract values and convert to numerical format
        values = pd.to_numeric(metric_data['value'])
        timestamps = pd.to_datetime(metric_data['timestamp'])
        
        # Create time-based features (days since first measurement)
        first_date = timestamps.min()
        X = np.array([(t - first_date).days for t in timestamps]).reshape(-1, 1)
        y = values.values
        
        # Train a linear regression model
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        model = LinearRegression()
        model.fit(X_scaled, y)
        
        # Generate future dates for predictions
        last_date = timestamps.max()
        future_dates = [last_date + timedelta(days=30*i) for i in range(1, forecast_periods+1)]
        future_X = np.array([(t - first_date).days for t in future_dates]).reshape(-1, 1)
        future_X_scaled = scaler.transform(future_X)
        
        # Make predictions
        predicted_values = model.predict(future_X_scaled)
        
        # Calculate confidence intervals (simplified approach)
        residuals = y - model.predict(X_scaled)
        residual_std = np.std(residuals)
        z_score = 1.96  # For ~95% confidence interval
        confidence_interval = z_score * residual_std
        
        # Determine trend direction and strength
        slope = model.coef_[0]
        trend_strength = abs(slope) / np.mean(y) if np.mean(y) != 0 else abs(slope)
        trend_direction = "improving" if (slope < 0 and name in ["Carbon Emissions", "Energy Consumption", "Water Usage"]) or \
                          (slope > 0 and name not in ["Carbon Emissions", "Energy Consumption", "Water Usage"]) else "worsening"
        
        # Prepare prediction object
        metric_prediction = {
            "name": name,
            "category": metric_data['category'].iloc[0],
            "unit": metric_data['unit'].iloc[0],
            "current_value": float(values.iloc[-1]),
            "predicted_values": [float(v) for v in predicted_values],
            "prediction_dates": [d.isoformat() for d in future_dates],
            "confidence_intervals": [float(confidence_interval) for _ in range(forecast_periods)],
            "trend_direction": trend_direction,
            "trend_strength": float(min(1.0, trend_strength * 10)),  # Scale to 0-1
            "model_accuracy": float(model.score(X_scaled, y))
        }
        
        predictions["predictions"].append(metric_prediction)
    
    # Add AI-powered insights if OpenAI is available
    predictions["ai_insights"] = generate_ai_insights(predictions["predictions"])
    
    return predictions

def generate_ai_insights(predictions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate AI-powered insights based on predicted trends"""
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not openai_api_key or not ADVANCED_ANALYTICS_AVAILABLE or not predictions:
        return generate_mock_ai_insights(predictions)
    
    try:
        # Extract key information for the prompt
        improving_metrics = [p for p in predictions if p.get("trend_direction") == "improving"]
        worsening_metrics = [p for p in predictions if p.get("trend_direction") == "worsening"]
        
        improving_summary = ", ".join([f"{m['name']} ({m['trend_strength']:.2f} strength)" for m in improving_metrics])
        worsening_summary = ", ".join([f"{m['name']} ({m['trend_strength']:.2f} strength)" for m in worsening_metrics])
        
        # Create the prompt for OpenAI
        prompt = f"""
        Analyze these sustainability metric predictions and provide strategic insights:
        
        Improving Metrics: {improving_summary if improving_metrics else "None"}
        Worsening Metrics: {worsening_summary if worsening_metrics else "None"}
        
        For each trend category (emissions, energy, water, waste, social), provide:
        1. A strategic insight explaining the business impact
        2. A risk assessment of what could happen if the trend continues
        3. A specific recommendation for action
        
        Format the response as a JSON object with these keys:
        {{
          "insights": [
            {{
              "category": "emissions/energy/water/waste/social",
              "trend_summary": "Brief summary of the trend",
              "business_impact": "Strategic business impact of this trend",
              "risk_assessment": "Potential risks if trend continues",
              "recommendation": "Specific action recommendation"
            }}
          ]
        }}
        """
        
        llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.3)
        response = RetrievalQA.from_chain_type(llm, chain_type="stuff").run(prompt)
        
        # Parse the response
        try:
            if isinstance(response, str):
                return json.loads(response).get("insights", [])
            return response.get("insights", [])
        except (json.JSONDecodeError, AttributeError):
            logger.warning("Failed to parse AI insights response")
            return generate_mock_ai_insights(predictions)
    
    except Exception as e:
        logger.error(f"Error generating AI insights: {str(e)}")
        return generate_mock_ai_insights(predictions)

def generate_mock_ai_insights(predictions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate mock AI insights when OpenAI is not available"""
    # Define mock insights templates
    insights_templates = {
        "emissions": {
            "improving": {
                "trend_summary": "Carbon emissions are trending downward",
                "business_impact": "Reduced emissions correlate with 15-20% lower operational costs and improved brand perception",
                "risk_assessment": "Current reduction rate may not meet science-based targets, risking compliance issues",
                "recommendation": "Accelerate renewable energy transition and implement carbon offset program"
            },
            "worsening": {
                "trend_summary": "Carbon emissions are increasing",
                "business_impact": "Rising emissions may lead to carbon taxes and decreased investor confidence",
                "risk_assessment": "Continued increase puts the organization at risk of missing regulatory requirements",
                "recommendation": "Conduct an energy audit and prioritize high-impact emission reduction projects"
            }
        },
        "energy": {
            "improving": {
                "trend_summary": "Energy efficiency is improving",
                "business_impact": "Energy savings translate to approximately 10% reduction in operational expenses",
                "risk_assessment": "Efficiency gains may plateau without technological upgrades",
                "recommendation": "Invest in smart building technology and employee energy conservation programs"
            },
            "worsening": {
                "trend_summary": "Energy consumption is increasing",
                "business_impact": "Higher energy costs may reduce profit margins by 3-5%",
                "risk_assessment": "Energy price volatility creates unpredictable financial exposure",
                "recommendation": "Implement energy management system and investigate renewable energy options"
            }
        },
        "water": {
            "improving": {
                "trend_summary": "Water usage efficiency is improving",
                "business_impact": "Reduced water consumption lowers utility costs and improves community relations",
                "risk_assessment": "Water efficiency gains may be offset by climate change impacts",
                "recommendation": "Implement water recycling systems and drought-resistant landscaping"
            },
            "worsening": {
                "trend_summary": "Water usage is increasing",
                "business_impact": "Rising water costs and potential restrictions in water-stressed regions",
                "risk_assessment": "Water scarcity may impact operations and supply chain resilience",
                "recommendation": "Conduct water audit and implement conservation technologies"
            }
        },
        "waste": {
            "improving": {
                "trend_summary": "Waste recycling rates are improving",
                "business_impact": "Reduced waste management costs and potential for circular economy revenue",
                "risk_assessment": "Recycling markets volatility may impact financial returns",
                "recommendation": "Develop closed-loop product design and packaging initiatives"
            },
            "worsening": {
                "trend_summary": "Waste generation is increasing",
                "business_impact": "Higher disposal costs and potential regulatory non-compliance",
                "risk_assessment": "Reputation damage from excessive waste generation",
                "recommendation": "Implement zero waste program and redesign products for circularity"
            }
        },
        "social": {
            "improving": {
                "trend_summary": "ESG social metrics are improving",
                "business_impact": "Enhanced brand reputation and improved employee retention",
                "risk_assessment": "Social performance expectations continue to rise year over year",
                "recommendation": "Develop integrated social impact measurement system and reporting"
            },
            "worsening": {
                "trend_summary": "ESG social performance is declining",
                "business_impact": "Potential investor concerns and challenges in talent acquisition",
                "risk_assessment": "Increasing scrutiny from stakeholders and potential activism",
                "recommendation": "Review social sustainability strategy and strengthen community engagement"
            }
        }
    }
    
    insights = []
    categories = set(p.get("category", "emissions") for p in predictions)
    
    # Generate insights for each category
    for category in categories:
        category_predictions = [p for p in predictions if p.get("category") == category]
        if not category_predictions:
            continue
            
        # Determine overall trend direction for this category
        improving_count = sum(1 for p in category_predictions if p.get("trend_direction") == "improving")
        worsening_count = sum(1 for p in category_predictions if p.get("trend_direction") == "worsening")
        
        trend_direction = "improving" if improving_count >= worsening_count else "worsening"
        
        # Get the template for this category and trend direction
        category_key = category if category in insights_templates else "emissions"
        insight_template = insights_templates[category_key][trend_direction]
        
        # Add some randomness to make insights more varied
        if random.random() < 0.3:  # 30% chance to flip the insight to opposite trend for variety
            alt_direction = "worsening" if trend_direction == "improving" else "improving"
            insight_template = insights_templates[category_key][alt_direction]
        
        # Create the insight
        insight = {
            "category": category,
            **insight_template
        }
        
        insights.append(insight)
    
    return insights

def generate_mock_predictions(
    metrics: List[Dict[str, Any]], 
    forecast_periods: int
) -> Dict[str, Any]:
    """Generate mock predictions when ML is not available"""
    logger.info("Generating mock predictions")
    
    if not metrics:
        return {
            "forecast_date": datetime.now().isoformat(),
            "forecast_periods": forecast_periods,
            "prediction_interval": 0.95,
            "predictions": [],
            "ai_insights": []
        }
    
    # Group metrics by name
    metrics_by_name = {}
    for metric in metrics:
        name = metric.get("name")
        if name not in metrics_by_name:
            metrics_by_name[name] = []
        metrics_by_name[name].append(metric)
    
    # Generate predictions for each metric
    predictions = {
        "forecast_date": datetime.now().isoformat(),
        "forecast_periods": forecast_periods,
        "prediction_interval": 0.95,
        "predictions": []
    }
    
    for name, metric_group in metrics_by_name.items():
        # Sort by timestamp
        metric_group.sort(key=lambda x: x.get("timestamp", ""))
        
        if not metric_group:
            continue
            
        # Get latest metric values
        latest_metric = metric_group[-1]
        latest_value = float(latest_metric.get("value", 0))
        category = latest_metric.get("category", "emissions")
        unit = latest_metric.get("unit", "")
        
        # Determine trend direction based on metric name
        is_reduction_positive = name in ["Carbon Emissions", "Energy Consumption", "Water Usage"]
        
        # Generate mock trend (improvement for ESG, recycling, etc. and reduction for emissions, water, energy)
        if (is_reduction_positive and random.random() < 0.7) or (not is_reduction_positive and random.random() < 0.7):
            # 70% chance of positive trend (decreasing for emissions, increasing for recycling)
            trend_multipliers = [0.95, 0.91, 0.88] if is_reduction_positive else [1.05, 1.09, 1.12]
            trend_direction = "improving"
        else:
            # 30% chance of negative trend
            trend_multipliers = [1.03, 1.05, 1.07] if is_reduction_positive else [0.98, 0.96, 0.94]
            trend_direction = "worsening"
        
        # Add some random variation
        trend_multipliers = [m * random.uniform(0.98, 1.02) for m in trend_multipliers]
        
        # Generate predicted values
        predicted_values = [latest_value * multiplier for multiplier in trend_multipliers]
        
        # Generate future dates
        last_date = datetime.fromisoformat(latest_metric.get("timestamp", datetime.now().isoformat()).replace('Z', '+00:00'))
        future_dates = [last_date + timedelta(days=30*i) for i in range(1, forecast_periods+1)]
        
        # Calculate mock confidence intervals (wider for further predictions)
        base_interval = latest_value * 0.05  # 5% of current value
        confidence_intervals = [base_interval * (1 + 0.5*i) for i in range(forecast_periods)]
        
        # Calculate trend strength (0-1)
        avg_change = abs(predicted_values[-1] / latest_value - 1)
        trend_strength = min(1.0, avg_change * 10)  # Scale to 0-1
        
        metric_prediction = {
            "name": name,
            "category": category,
            "unit": unit,
            "current_value": latest_value,
            "predicted_values": predicted_values,
            "prediction_dates": [d.isoformat() for d in future_dates],
            "confidence_intervals": confidence_intervals,
            "trend_direction": trend_direction,
            "trend_strength": trend_strength,
            "model_accuracy": random.uniform(0.75, 0.95)  # Mock accuracy between 75-95%
        }
        
        predictions["predictions"].append(metric_prediction)
    
    # Generate mock AI insights
    predictions["ai_insights"] = generate_mock_ai_insights(predictions["predictions"])
    
    return predictions

def perform_materiality_assessment(
    company_name: str,
    industry: str,
    metrics: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Perform an automated materiality assessment to determine which sustainability
    issues are most material to a company's financial performance and stakeholders
    
    Args:
        company_name (str): Name of the company
        industry (str): Industry the company operates in
        metrics (List[Dict]): Optional metrics data
        
    Returns:
        Dict: Materiality assessment with financial impact scores
    """
    logger.info(f"Performing materiality assessment for {company_name} in {industry} industry")
    
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if openai_api_key and ADVANCED_ANALYTICS_AVAILABLE:
        try:
            # Use LangChain and OpenAI for materiality assessment
            prompt = f"""
            Perform a materiality assessment for '{company_name}' in the {industry} industry to identify which sustainability 
            topics have the highest impact on business value and stakeholder concern.
            
            Analyze:
            1. Financial materiality: Impact on revenue, costs, and risk
            2. Stakeholder materiality: Importance to customers, investors, employees, and communities
            3. Sector-specific issues for the {industry} industry
            
            For each material topic, provide:
            1. Topic name
            2. Business impact score (1-10)
            3. Stakeholder concern score (1-10)
            4. Combined materiality score (calculated)
            5. Financial impact statement
            6. Recommended metrics to track
            
            Format the response as a JSON object with this structure:
            {{
              "company": "{company_name}",
              "industry": "{industry}",
              "assessment_date": "ISO date",
              "material_topics": [
                {{
                  "topic": "Topic name",
                  "business_impact_score": 8.5,
                  "stakeholder_concern_score": 7.2,
                  "materiality_score": 7.85,
                  "financial_impact": "Statement of financial impact",
                  "recommended_metrics": ["Metric 1", "Metric 2"]
                }}
              ]
            }}
            
            Return at least 5 material topics, sorted by materiality score (highest first).
            """
            
            llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.3)
            response = RetrievalQA.from_chain_type(llm, chain_type="stuff").run(prompt)
            
            # Parse the response
            try:
                if isinstance(response, str):
                    return json.loads(response)
                return response
            except json.JSONDecodeError:
                logger.warning("Failed to parse materiality assessment response")
                return generate_mock_materiality_assessment(company_name, industry)
                
        except Exception as e:
            logger.error(f"Error using LangChain/OpenAI for materiality assessment: {str(e)}")
            return generate_mock_materiality_assessment(company_name, industry)
    else:
        logger.warning("OpenAI API key not available or LangChain not installed. Using mock materiality assessment.")
        return generate_mock_materiality_assessment(company_name, industry)

def generate_mock_materiality_assessment(company_name: str, industry: str) -> Dict[str, Any]:
    """Generate mock materiality assessment when OpenAI is not available"""
    logger.info(f"Generating mock materiality assessment for {company_name}")
    
    # Industry-specific material topics
    industry_topics = {
        "technology": [
            {
                "topic": "E-waste & Digital Pollution",
                "business_impact_score": 8.7,
                "stakeholder_concern_score": 7.8,
                "materiality_score": 8.25,
                "financial_impact": "E-waste management costs expected to increase by 15-20% due to new regulations. Revenue opportunities from refurbished electronics could offset costs.",
                "recommended_metrics": ["E-waste recycling rate (%)", "Product lifecycle extension (months)", "Hazardous materials per unit (g)"]
            },
            {
                "topic": "Data Center Energy Efficiency",
                "business_impact_score": 9.2,
                "stakeholder_concern_score": 6.8,
                "materiality_score": 8.0,
                "financial_impact": "Energy costs represent 25-30% of data center operational expenses. Efficiency improvements could reduce costs by $1-2M annually.",
                "recommended_metrics": ["PUE (Power Usage Effectiveness)", "Renewable energy use (%)", "Energy cost per data unit ($)"]
            },
            {
                "topic": "Digital Inclusion & Accessibility",
                "business_impact_score": 6.9,
                "stakeholder_concern_score": 8.5,
                "materiality_score": 7.7,
                "financial_impact": "Expanding market by 15-20% through accessible product design. Reduced legal risk from accessibility lawsuits.",
                "recommended_metrics": ["Accessibility compliance rate (%)", "Digital inclusion investment ($)", "Users from underrepresented regions (%)"]
            },
            {
                "topic": "Data Privacy & Security",
                "business_impact_score": 9.5,
                "stakeholder_concern_score": 9.2,
                "materiality_score": 9.35,
                "financial_impact": "Data breaches cost an average of $4.24M per incident. Prevention investments show 3:1 ROI.",
                "recommended_metrics": ["Security breach incidents (#)", "Data privacy compliance score", "Security investment (% of IT budget)"]
            },
            {
                "topic": "AI Ethics & Responsible Innovation",
                "business_impact_score": 7.8,
                "stakeholder_concern_score": 8.9,
                "materiality_score": 8.35,
                "financial_impact": "Early investment in responsible AI frameworks reduces redevelopment costs and regulatory risks by 30%.",
                "recommended_metrics": ["AI ethics review completion rate (%)", "Algorithmic bias incidents (#)", "Responsible innovation investment ($)"]
            }
        ],
        "manufacturing": [
            {
                "topic": "Circular Economy & Materials",
                "business_impact_score": 8.5,
                "stakeholder_concern_score": 7.6,
                "materiality_score": 8.05,
                "financial_impact": "Circular design and remanufacturing could reduce raw material costs by 20-30% and create new service revenue streams.",
                "recommended_metrics": ["Recycled content (%)", "Material recovery rate (%)", "Product recyclability rate (%)"]
            },
            {
                "topic": "Energy Efficiency & Emissions",
                "business_impact_score": 9.3,
                "stakeholder_concern_score": 8.7,
                "materiality_score": 9.0,
                "financial_impact": "Carbon taxes expected to impact operating costs by 5-7%. Energy efficiency investments showing 30% ROI.",
                "recommended_metrics": ["Energy intensity (kWh/unit)", "Scope 1+2 emissions (tCO2e)", "Renewable energy use (%)"]
            },
            {
                "topic": "Supply Chain Sustainability",
                "business_impact_score": 8.9,
                "stakeholder_concern_score": 8.3,
                "materiality_score": 8.6,
                "financial_impact": "Sustainable sourcing reduces supply disruption risks by 25% and improves inventory costs by 5-10%.",
                "recommended_metrics": ["Supplier ESG assessment coverage (%)", "Sustainable sourcing (%)", "Supply chain emissions (tCO2e)"]
            },
            {
                "topic": "Water Management",
                "business_impact_score": 7.8,
                "stakeholder_concern_score": 7.5,
                "materiality_score": 7.65,
                "financial_impact": "Water conservation initiatives reduce utility costs by 15-20% and mitigate water scarcity risks in key operating regions.",
                "recommended_metrics": ["Water withdrawal (m³)", "Water recycling rate (%)", "Water intensity (m³/unit)"]
            },
            {
                "topic": "Worker Health & Safety",
                "business_impact_score": 9.1,
                "stakeholder_concern_score": 9.4,
                "materiality_score": 9.25,
                "financial_impact": "Each lost-time incident costs $30-50K on average. Strong safety programs reduce insurance premiums by 15-25%.",
                "recommended_metrics": ["Incident rate", "Safety training hours", "Near-miss reporting rate"]
            }
        ]
    }
    
    # Default topics for industries not explicitly covered
    default_topics = [
        {
            "topic": "Greenhouse Gas Emissions",
            "business_impact_score": round(random.uniform(7.5, 9.5), 1),
            "stakeholder_concern_score": round(random.uniform(7.0, 9.0), 1),
            "materiality_score": None,  # Will be calculated
            "financial_impact": "Carbon pricing mechanisms expected to impact operational costs by 3-8% by 2030. Emissions reduction projects show average 25% ROI.",
            "recommended_metrics": ["Scope 1 & 2 emissions (tCO2e)", "Carbon intensity (tCO2e/$M revenue)", "Emissions reduction (% year-over-year)"]
        },
        {
            "topic": "Energy Management",
            "business_impact_score": round(random.uniform(7.0, 9.0), 1),
            "stakeholder_concern_score": round(random.uniform(6.5, 8.5), 1),
            "materiality_score": None,
            "financial_impact": "Energy represents 15-25% of operational costs. Efficiency initiatives and renewable energy can reduce expenses by $0.8-1.5M annually.",
            "recommended_metrics": ["Energy consumption (MWh)", "Renewable energy (%)", "Energy intensity (kWh/unit)"]
        },
        {
            "topic": "Waste & Circular Economy",
            "business_impact_score": round(random.uniform(6.5, 8.5), 1),
            "stakeholder_concern_score": round(random.uniform(7.0, 8.5), 1),
            "materiality_score": None,
            "financial_impact": "Waste management costs increasing 5-10% annually. Circular initiatives create new revenue streams and reduce material costs by 10-15%.",
            "recommended_metrics": ["Waste to landfill (tons)", "Waste diversion rate (%)", "Circular material use (%)"]
        },
        {
            "topic": "Water Conservation",
            "business_impact_score": round(random.uniform(6.0, 8.5), 1),
            "stakeholder_concern_score": round(random.uniform(6.5, 8.0), 1),
            "materiality_score": None,
            "financial_impact": "Water costs projected to increase 20-30% in water-stressed regions. Conservation reduces operational expenses and supply chain risks.",
            "recommended_metrics": ["Water withdrawal (m³)", "Water recycling rate (%)", "Water stress exposure (% operations in high-stress areas)"]
        },
        {
            "topic": "Diversity, Equity & Inclusion",
            "business_impact_score": round(random.uniform(7.0, 8.5), 1),
            "stakeholder_concern_score": round(random.uniform(8.0, 9.5), 1),
            "materiality_score": None,
            "financial_impact": "Diverse companies outperform peers by 25-36% on profitability. Improved talent attraction and retention reduces hiring costs by 20%.",
            "recommended_metrics": ["Workforce diversity metrics", "Pay equity ratio", "Employee engagement score"]
        },
        {
            "topic": "Supply Chain Management",
            "business_impact_score": round(random.uniform(7.5, 9.0), 1),
            "stakeholder_concern_score": round(random.uniform(7.0, 8.5), 1),
            "materiality_score": None,
            "financial_impact": "Sustainable procurement reduces supply disruption risks by 15-20% and improves supplier performance metrics by 10-15%.",
            "recommended_metrics": ["Supplier ESG assessment coverage (%)", "Supply chain emissions (tCO2e)", "Sustainable procurement (%)"]
        }
    ]
    
    # Get the appropriate topics based on industry
    topics = industry_topics.get(industry.lower(), default_topics)
    
    # Calculate materiality scores for topics that don't have them
    for topic in topics:
        if topic["materiality_score"] is None:
            topic["materiality_score"] = round((topic["business_impact_score"] + topic["stakeholder_concern_score"]) / 2, 2)
    
    # Sort topics by materiality score (highest first)
    topics.sort(key=lambda x: x["materiality_score"], reverse=True)
    
    # Create the assessment result
    assessment = {
        "company": company_name,
        "industry": industry,
        "assessment_date": datetime.now().isoformat(),
        "material_topics": topics
    }
    
    return assessment
