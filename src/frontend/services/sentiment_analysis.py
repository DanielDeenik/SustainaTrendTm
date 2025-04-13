"""
BERT-Based Sentiment Analysis Module for Sustainability Intelligence Platform

This module provides advanced NLP capabilities for sentiment analysis of
sustainability-related content using BERT models from Hugging Face.

Key features:
1. Real-time sentiment scoring of sustainability content
2. Topic-specific sentiment analysis (climate, social, governance)
3. Trend analysis of sentiment over time
4. Social listening for sustainability topics
"""
import os
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import random
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load transformers conditionally to allow fallback to mock mode
try:
    from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
    TRANSFORMERS_AVAILABLE = True
    logger.info("Transformers library loaded successfully for BERT sentiment analysis")
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers library not available. Using mock sentiment analysis.")

# Global sentiment analysis pipeline (lazy-loaded)
_sentiment_pipeline = None

def get_sentiment_pipeline():
    """
    Get or initialize the sentiment analysis pipeline.
    
    Returns:
        A sentiment analysis pipeline or None if not available
    """
    global _sentiment_pipeline
    
    if not TRANSFORMERS_AVAILABLE:
        logger.warning("Cannot create sentiment pipeline - transformers not available")
        return None
    
    if _sentiment_pipeline is None:
        try:
            logger.info("Initializing sentiment analysis pipeline")
            # Use a smaller, faster model for sentiment analysis
            # Options: distilbert-base-uncased-finetuned-sst-2-english (faster),
            #          cardiffnlp/twitter-roberta-base-sentiment (social media focused)
            model_name = "distilbert-base-uncased-finetuned-sst-2-english"
            _sentiment_pipeline = pipeline("sentiment-analysis", model=model_name)
            logger.info(f"Sentiment analysis pipeline initialized with model: {model_name}")
        except Exception as e:
            logger.error(f"Error initializing sentiment pipeline: {str(e)}")
            return None
    
    return _sentiment_pipeline

def analyze_sustainability_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze sentiment of sustainability-related text using BERT.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with sentiment analysis results
    """
    if not text or len(text.strip()) == 0:
        logger.warning("Empty text provided for sentiment analysis")
        return {
            "sentiment": "neutral",
            "score": 0.5,
            "confidence": 0,
            "analysis_type": "none",
            "timestamp": datetime.now().isoformat()
        }
    
    # Get the sentiment pipeline
    sentiment_pipeline = get_sentiment_pipeline()
    
    # If transformers are available and pipeline initialized successfully
    if TRANSFORMERS_AVAILABLE and sentiment_pipeline:
        try:
            # Truncate text if too long (BERT has token limits)
            # Most BERT models have a limit of 512 tokens
            max_length = 512
            truncated_text = text[:1000]  # Rough character estimate
            
            # Run sentiment analysis
            start_time = time.time()
            result = sentiment_pipeline(truncated_text)[0]
            processing_time = time.time() - start_time
            
            # Parse the result
            label = result['label'].lower()
            score = result['score']
            
            # Map to a -1 to 1 scale for consistency
            normalized_score = score
            if label == 'negative':
                normalized_score = 1 - score  # Flip the score for negative sentiment
                sentiment = "negative"
            else:
                sentiment = "positive"
            
            # For DistilBERT model, "NEGATIVE" and "POSITIVE" are the labels
            # Adjust mapping based on your model
            
            logger.info(f"BERT sentiment analysis completed in {processing_time:.2f}s: {sentiment} ({score:.2f})")
            
            return {
                "sentiment": sentiment,
                "score": normalized_score,
                "confidence": score,
                "analysis_type": "bert",
                "processing_time": processing_time,
                "model": sentiment_pipeline.model.config.name_or_path,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in BERT sentiment analysis: {str(e)}")
            # Fall back to mock analysis on error
    
    # Mock sentiment analysis when transformers not available
    logger.info("Using mock sentiment analysis")
    return generate_mock_sentiment_analysis(text)

def generate_mock_sentiment_analysis(text: str) -> Dict[str, Any]:
    """
    Generate mock sentiment analysis results for demonstration.
    
    Args:
        text: Text to analyze
        
    Returns:
        Mock sentiment analysis results
    """
    # Simple keyword-based mock sentiment
    text_lower = text.lower()
    
    # Sustainability sentiment keywords
    positive_keywords = [
        "sustainable", "renewable", "green", "clean", "efficient", 
        "progress", "improvement", "innovation", "solution", "positive",
        "carbon neutral", "net zero", "renewable", "recycled", "conservation",
        "ethical", "responsible", "benefit", "success", "achieve"
    ]
    
    negative_keywords = [
        "unsustainable", "polluting", "emissions", "waste", "harmful", 
        "risk", "problem", "challenge", "failure", "negative",
        "carbon intensive", "deforestation", "pollution", "violation", "unethical",
        "controversy", "penalty", "fine", "lawsuit", "damage"
    ]
    
    # Count keyword occurrences
    positive_count = sum(text_lower.count(keyword) for keyword in positive_keywords)
    negative_count = sum(text_lower.count(keyword) for keyword in negative_keywords)
    
    # Calculate sentiment score (-1 to 1)
    total = positive_count + negative_count
    if total == 0:
        sentiment_score = 0
        sentiment = "neutral"
        confidence = 0.5
    else:
        sentiment_score = (positive_count - negative_count) / total
        confidence = min(0.9, 0.5 + abs(sentiment_score) * 0.4)  # Scale confidence based on score strength
        
        if sentiment_score > 0.1:
            sentiment = "positive"
        elif sentiment_score < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
            confidence = 0.6  # Lower confidence for neutral predictions
    
    # Normalize sentiment score to 0-1 range for mock results
    normalized_score = (sentiment_score + 1) / 2
    
    return {
        "sentiment": sentiment,
        "score": normalized_score,
        "confidence": confidence,
        "analysis_type": "mock",
        "positive_terms": positive_count,
        "negative_terms": negative_count,
        "timestamp": datetime.now().isoformat()
    }

def analyze_topic_sentiment(text: str, topic: str) -> Dict[str, Any]:
    """
    Analyze sentiment specifically for a sustainability topic.
    
    Args:
        text: Text to analyze
        topic: Sustainability topic to focus on (e.g., "climate", "social", "governance")
        
    Returns:
        Topic-specific sentiment analysis
    """
    # First, extract topic-relevant text segments
    topic_keywords = get_topic_keywords(topic)
    
    # Extract sentences containing topic keywords
    topic_segments = extract_topic_segments(text, topic_keywords)
    
    if not topic_segments:
        return {
            "topic": topic,
            "sentiment": "neutral",
            "score": 0.5,
            "confidence": 0,
            "relevant_text": "",
            "topic_mentioned": False
        }
    
    # Analyze the topic segments
    joined_segments = " ".join(topic_segments)
    sentiment_result = analyze_sustainability_sentiment(joined_segments)
    
    # Add topic-specific information
    sentiment_result["topic"] = topic
    sentiment_result["relevant_text"] = joined_segments[:200] + "..." if len(joined_segments) > 200 else joined_segments
    sentiment_result["topic_mentioned"] = True
    sentiment_result["segment_count"] = len(topic_segments)
    
    return sentiment_result

def extract_topic_segments(text: str, keywords: List[str], context_words: int = 20) -> List[str]:
    """
    Extract text segments related to specific topic keywords.
    
    Args:
        text: Full text to analyze
        keywords: List of topic keywords to search for
        context_words: Number of words before and after the keyword to include
        
    Returns:
        List of text segments containing topic keywords with context
    """
    segments = []
    words = text.split()
    
    for i, word in enumerate(words):
        if any(keyword.lower() in word.lower() for keyword in keywords):
            # Get context around the keyword
            start = max(0, i - context_words)
            end = min(len(words), i + context_words + 1)
            segment = " ".join(words[start:end])
            segments.append(segment)
    
    return segments

def get_topic_keywords(topic: str) -> List[str]:
    """
    Get keywords related to a sustainability topic.
    
    Args:
        topic: Sustainability topic
        
    Returns:
        List of related keywords
    """
    # Map topics to related keywords
    topic_keywords = {
        "climate": [
            "climate", "carbon", "emission", "greenhouse", "temperature", "global warming",
            "renewable", "fossil fuel", "CO2", "methane", "climate change", "paris agreement"
        ],
        "social": [
            "social", "employee", "diversity", "inclusion", "community", "human rights",
            "labor", "safety", "health", "wellbeing", "gender", "equality", "discrimination"
        ],
        "governance": [
            "governance", "board", "compliance", "ethics", "transparency", "accountability",
            "corruption", "policy", "risk management", "executive", "compensation", "voting"
        ],
        "water": [
            "water", "consumption", "efficiency", "scarcity", "conservation", "quality",
            "wastewater", "discharge", "treatment", "freshwater", "watershed"
        ],
        "waste": [
            "waste", "recycling", "circular", "landfill", "disposal", "recovery",
            "reuse", "reduce", "compost", "hazardous", "plastic"
        ],
        "biodiversity": [
            "biodiversity", "ecosystem", "species", "habitat", "conservation", "deforestation",
            "wildlife", "nature", "preservation", "land use", "restoration"
        ]
    }
    
    # Default to climate if topic not found
    return topic_keywords.get(topic.lower(), topic_keywords["climate"])

def batch_analyze_sentiment(texts: List[str]) -> List[Dict[str, Any]]:
    """
    Analyze sentiment for multiple texts in batch.
    
    Args:
        texts: List of texts to analyze
        
    Returns:
        List of sentiment analysis results
    """
    results = []
    
    for text in texts:
        result = analyze_sustainability_sentiment(text)
        results.append(result)
    
    return results

def analyze_sentiment_trends(texts: List[str], dates: List[str]) -> Dict[str, Any]:
    """
    Analyze sentiment trends over time from a series of texts.
    
    Args:
        texts: List of texts to analyze
        dates: List of dates corresponding to each text (ISO format)
        
    Returns:
        Sentiment trend analysis
    """
    if len(texts) != len(dates):
        logger.error(f"Number of texts ({len(texts)}) doesn't match number of dates ({len(dates)})")
        return {
            "error": "Mismatched number of texts and dates",
            "trend": "unknown",
            "data": []
        }
    
    # Analyze sentiment for each text
    results = []
    for i, (text, date) in enumerate(zip(texts, dates)):
        sentiment = analyze_sustainability_sentiment(text)
        results.append({
            "date": date,
            "sentiment": sentiment["sentiment"],
            "score": sentiment["score"],
            "confidence": sentiment.get("confidence", 0.5),
            "text_index": i
        })
    
    # Sort by date
    results.sort(key=lambda x: x["date"])
    
    # Calculate trend
    if len(results) > 1:
        scores = [r["score"] for r in results]
        first_half = scores[:len(scores)//2]
        second_half = scores[len(scores)//2:]
        
        first_half_avg = sum(first_half) / len(first_half) if first_half else 0.5
        second_half_avg = sum(second_half) / len(second_half) if second_half else 0.5
        
        change = second_half_avg - first_half_avg
        
        if change > 0.1:
            trend = "improving"
        elif change < -0.1:
            trend = "worsening"
        else:
            trend = "stable"
    else:
        trend = "insufficient data"
    
    return {
        "trend": trend,
        "data_points": len(results),
        "average_score": sum(r["score"] for r in results) / len(results) if results else 0.5,
        "trend_change": change if len(results) > 1 else 0,
        "data": results
    }

@lru_cache(maxsize=10)
def get_mock_social_media_data(topic: str = "sustainability", count: int = 50) -> List[Dict[str, Any]]:
    """
    Generate mock social media data for demonstration.
    
    Args:
        topic: Topic to generate data for
        count: Number of data points to generate
        
    Returns:
        List of mock social media posts
    """
    # Keywords for different topics
    topic_keywords = {
        "sustainability": [
            "sustainability", "sustainable", "green", "eco-friendly", "climate action",
            "net zero", "carbon neutral", "renewable energy", "ESG", "circular economy"
        ],
        "climate": [
            "climate change", "global warming", "carbon emissions", "greenhouse gases",
            "renewable", "clean energy", "climate crisis", "fossil fuels", "paris agreement"
        ],
        "social": [
            "social impact", "diversity", "inclusion", "workplace safety", "community",
            "human rights", "fair wages", "gender equality", "social responsibility"
        ],
        "governance": [
            "corporate governance", "transparency", "accountability", "board diversity",
            "compliance", "ethical", "responsible", "stakeholder", "reporting"
        ]
    }
    
    # Sources for mock data
    sources = ["Twitter", "LinkedIn", "Reddit", "News Article", "Corporate Blog", "NGO Report"]
    
    # Get keywords for the selected topic, default to sustainability
    keywords = topic_keywords.get(topic.lower(), topic_keywords["sustainability"])
    
    # Generate mock data
    results = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    for i in range(count):
        # Generate a random date within the range
        days_back = random.randint(0, 90)
        post_date = end_date - timedelta(days=days_back)
        
        # Generate topic-specific content
        keyword = random.choice(keywords)
        
        # Vary sentiment distribution based on topic
        if topic.lower() == "climate":
            sentiment_weights = [0.4, 0.3, 0.3]  # negative, neutral, positive
        elif topic.lower() == "social":
            sentiment_weights = [0.2, 0.3, 0.5]  # negative, neutral, positive
        elif topic.lower() == "governance":
            sentiment_weights = [0.3, 0.4, 0.3]  # negative, neutral, positive
        else:
            sentiment_weights = [0.3, 0.3, 0.4]  # negative, neutral, positive
        
        sentiment_type = random.choices(["negative", "neutral", "positive"], weights=sentiment_weights)[0]
        
        # Generate content based on sentiment
        if sentiment_type == "positive":
            prefix = random.choice([
                "Excited about ", "Great progress on ", "Impressive ", "Celebrating ", 
                "Proud of our ", "Breakthrough in ", "Success story: "
            ])
            content = f"{prefix}{keyword} efforts showing real impact. #Sustainability"
            score = random.uniform(0.7, 0.95)
        elif sentiment_type == "negative":
            prefix = random.choice([
                "Concerned about ", "Disappointing ", "Falling behind on ", "Problems with ",
                "Challenges in ", "Failing ", "Lack of progress in "
            ])
            content = f"{prefix}{keyword} initiatives. We need to do better. #Sustainability"
            score = random.uniform(0.05, 0.3)
        else:
            prefix = random.choice([
                "Analyzing ", "Reviewing ", "Considering ", "Looking at ", 
                "Examining ", "Evaluating ", "New report on "
            ])
            content = f"{prefix}{keyword} performance and initiatives. #Sustainability"
            score = random.uniform(0.4, 0.6)
        
        # Generate engagement metrics
        engagement = {
            "likes": random.randint(5, 1000),
            "shares": random.randint(0, 200),
            "comments": random.randint(0, 50),
            "reach": random.randint(500, 10000)
        }
        
        # Add to results
        results.append({
            "source": random.choice(sources),
            "date": post_date.isoformat(),
            "content": content,
            "topic": topic,
            "keyword": keyword,
            "sentiment": sentiment_type,
            "score": score,
            "engagement": engagement,
            "author_type": random.choice(["individual", "organization", "media", "influencer", "expert"])
        })
    
    # Sort by date
    results.sort(key=lambda x: x["date"], reverse=True)
    
    return results

def analyze_social_sentiment(topic: str = "sustainability", timeframe: str = "90d") -> Dict[str, Any]:
    """
    Analyze sentiment across social media for a sustainability topic.
    
    Args:
        topic: Sustainability topic to analyze
        timeframe: Time period to analyze (30d, 90d, 1y)
        
    Returns:
        Social sentiment analysis results
    """
    # In a real implementation, this would fetch data from social media APIs
    # For now, generate mock data
    
    # Number of data points based on timeframe
    if timeframe == "30d":
        count = 30
    elif timeframe == "1y":
        count = 100
    else:  # 90d default
        count = 50
    
    # Get mock social media data
    social_data = get_mock_social_media_data(topic, count)
    
    # Calculate overall sentiment stats
    sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
    scores = []
    engagement_by_sentiment = {"positive": 0, "neutral": 0, "negative": 0}
    sources = {}
    
    for post in social_data:
        sentiment_counts[post["sentiment"]] += 1
        scores.append(post["score"])
        
        # Sum engagement metrics by sentiment
        engagement = post["engagement"]["likes"] + post["engagement"]["shares"] * 3  # Weigh shares more heavily
        engagement_by_sentiment[post["sentiment"]] += engagement
        
        # Count by source
        source = post["source"]
        if source not in sources:
            sources[source] = {"count": 0, "sentiment_sum": 0}
        sources[source]["count"] += 1
        sources[source]["sentiment_sum"] += post["score"]
    
    # Calculate average sentiment by source
    for source in sources:
        sources[source]["average_sentiment"] = sources[source]["sentiment_sum"] / sources[source]["count"]
    
    # Calculate overall average
    average_score = sum(scores) / len(scores) if scores else 0.5
    
    # Determine overall sentiment and trend
    if average_score > 0.6:
        overall_sentiment = "positive"
    elif average_score < 0.4:
        overall_sentiment = "negative"
    else:
        overall_sentiment = "neutral"
    
    # Calculate weekly averages for trend
    weekly_averages = calculate_weekly_sentiment_averages(social_data)
    
    # Determine trend based on weekly averages
    trend = determine_sentiment_trend(weekly_averages)
    
    return {
        "topic": topic,
        "timeframe": timeframe,
        "overall_sentiment": overall_sentiment,
        "average_score": average_score,
        "sentiment_distribution": sentiment_counts,
        "engagement_by_sentiment": engagement_by_sentiment,
        "sources": sources,
        "trend": trend,
        "weekly_averages": weekly_averages,
        "sample_posts": social_data[:5],  # Include a few sample posts
        "total_posts_analyzed": len(social_data)
    }

def calculate_weekly_sentiment_averages(social_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Calculate weekly sentiment averages from social media data.
    
    Args:
        social_data: List of social media posts with sentiment scores
        
    Returns:
        List of weekly sentiment averages
    """
    # Group posts by week
    weeks = {}
    
    for post in social_data:
        date = datetime.fromisoformat(post["date"].split("T")[0])
        week_start = (date - timedelta(days=date.weekday())).strftime("%Y-%m-%d")
        
        if week_start not in weeks:
            weeks[week_start] = {"sum": 0, "count": 0}
        
        weeks[week_start]["sum"] += post["score"]
        weeks[week_start]["count"] += 1
    
    # Calculate averages
    weekly_averages = []
    for week_start, data in weeks.items():
        weekly_averages.append({
            "week": week_start,
            "average_score": data["sum"] / data["count"],
            "post_count": data["count"]
        })
    
    # Sort by week
    weekly_averages.sort(key=lambda x: x["week"])
    
    return weekly_averages

def determine_sentiment_trend(weekly_averages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Determine the sentiment trend from weekly averages.
    
    Args:
        weekly_averages: List of weekly sentiment averages
        
    Returns:
        Trend analysis
    """
    if not weekly_averages or len(weekly_averages) < 2:
        return {
            "direction": "insufficient data",
            "strength": 0,
            "description": "Insufficient data to determine trend"
        }
    
    # Get first and last week averages
    first_week = weekly_averages[0]["average_score"]
    last_week = weekly_averages[-1]["average_score"]
    
    # Calculate change
    absolute_change = last_week - first_week
    percent_change = (absolute_change / first_week) * 100 if first_week != 0 else 0
    
    # Determine trend direction and strength
    if absolute_change > 0.05:
        direction = "improving"
        strength = min(1.0, absolute_change * 5)  # Scale to 0-1
    elif absolute_change < -0.05:
        direction = "worsening"
        strength = min(1.0, abs(absolute_change) * 5)  # Scale to 0-1
    else:
        direction = "stable"
        strength = 0.1  # Minimal strength for stable trends
    
    # Generate description
    if direction == "improving":
        if strength > 0.7:
            description = "Strong positive trend in sentiment"
        else:
            description = "Slight improvement in sentiment"
    elif direction == "worsening":
        if strength > 0.7:
            description = "Strong negative trend in sentiment"
        else:
            description = "Slight decline in sentiment"
    else:
        description = "Sentiment has remained relatively stable"
    
    return {
        "direction": direction,
        "strength": strength,
        "absolute_change": absolute_change,
        "percent_change": percent_change,
        "description": description
    }

def configure_routes(app):
    """
    Configure Flask routes for sentiment analysis
    
    Args:
        app: Flask application
    """
    from flask import request, jsonify, render_template
    
    @app.route('/sentiment-analysis')
    def sentiment_analysis_dashboard():
        """Sentiment Analysis Dashboard"""
        try:
            logger.info("Sentiment analysis dashboard requested")
            return render_template("sentiment_analysis.html")
        except Exception as e:
            logger.error(f"Error loading sentiment analysis dashboard: {str(e)}")
            return f"Error loading sentiment analysis dashboard: {str(e)}", 500
    
    @app.route('/api/sentiment-analysis', methods=['POST'])
    def api_sentiment_analysis():
        """API endpoint for sentiment analysis"""
        try:
            data = request.get_json()
            
            if not data or 'text' not in data:
                return jsonify({"error": "No text provided"}), 400
            
            text = data.get('text')
            
            # Get optional topic
            topic = data.get('topic')
            
            if topic:
                result = analyze_topic_sentiment(text, topic)
            else:
                result = analyze_sustainability_sentiment(text)
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error in sentiment analysis endpoint: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/social-sentiment', methods=['GET'])
    def api_social_sentiment():
        """API endpoint for social media sentiment analysis"""
        try:
            topic = request.args.get('topic', 'sustainability')
            timeframe = request.args.get('timeframe', '90d')
            
            result = analyze_social_sentiment(topic, timeframe)
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error in social sentiment endpoint: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/batch-sentiment', methods=['POST'])
    def api_batch_sentiment():
        """API endpoint for batch sentiment analysis"""
        try:
            data = request.get_json()
            
            if not data or 'texts' not in data:
                return jsonify({"error": "No texts provided"}), 400
            
            texts = data.get('texts')
            
            results = batch_analyze_sentiment(texts)
            
            return jsonify({"results": results})
        except Exception as e:
            logger.error(f"Error in batch sentiment analysis endpoint: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    logger.info("Sentiment analysis routes configured")

def register_routes(app):
    """
    Register sentiment analysis routes with Flask app
    
    Args:
        app: Flask application
    """
    configure_routes(app)
    logger.info("Sentiment analysis routes registered")