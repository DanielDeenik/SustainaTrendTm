# SustainaTrend™ Intelligence Platform

![SustainaTrend Logo](generated-icon.png)

## Overview

SustainaTrend™ is a cutting-edge sustainability intelligence platform that leverages advanced AI technologies to transform complex environmental data into engaging, actionable insights. The platform combines real-time data analysis, predictive analytics, and AI-powered search capabilities to provide comprehensive sustainability intelligence for businesses and organizations.

## Key Features

### 1. Advanced AI Search Engine
- **Hybrid Search Technology**: Combines Google Gemini AI with Google Search API and internal data sources
- **Multiple Search Modes**: Choose between AI-powered, keyword-based, or hybrid search approaches
- **Intelligent Query Enhancement**: Automatically augments queries with sustainability context
- **Comprehensive Result Filtering**: Filter by category, source, relevance score, and date
- **Automated Result Summarization**: AI-generated summaries of search results

### 2. Sustainability Analytics
- **Trend Analysis**: Identify emerging sustainability trends with virality scoring
- **Predictive Analytics**: Forecast future sustainability metrics and performance indicators
- **Competitive Benchmarking**: Compare sustainability performance against industry peers
- **Materiality Assessment**: AI-powered assessment of material sustainability issues

### 3. Sustainability Storytelling
- **AI-Generated Narratives**: Create compelling sustainability stories automatically
- **Strategic Frameworks**: Aligned with leading management consulting methodologies
- **Investment Pathways**: Identify sustainable investment opportunities
- **Monetization Models**: Develop business models around sustainability initiatives

### 4. Robust Error Handling & API Management
- **Comprehensive API Status Reporting**: Real-time monitoring of all API services
- **Multi-Layer Fallback System**: Graceful degradation with detailed status reporting
- **Enhanced Credential Validation**: Extensive API key validation and formatting checks
- **Transparent Service Status**: Visual indicators for service availability and detailed error feedback

## Technology Stack

### Frontend
- **Flask**: Powerful Python web framework for building the frontend application
- **Bootstrap**: Responsive CSS framework for modern UI design
- **Plotly**: Interactive data visualization library for analytics dashboards
- **jQuery**: JavaScript library for enhanced user interactions

### Backend
- **FastAPI**: High-performance Python API framework
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) system
- **PostgreSQL**: Advanced open-source database for data persistence
- **Redis**: In-memory data structure store for caching (optional)

### AI & Machine Learning
- **Google Gemini API**: Advanced language model for AI-powered analytics and search
- **Google Custom Search API**: Web search capabilities for comprehensive results
- **Custom NLP Models**: Specialized models for sustainability context understanding
- **Vector Search**: Semantic similarity search for concept-based matching

## Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL (optional)
- Redis (optional)
- Google Gemini API key
- Google Custom Search API key with CSE ID

### Environment Setup
1. Clone the repository
2. Create a `.env` file in the `frontend` directory with the following variables:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   GOOGLE_API_KEY=your_google_api_key
   GOOGLE_CSE_ID=your_google_cse_id
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application
```bash
# Start the dashboard
./start.sh
```

The application will be available at http://localhost:5000 by default.

## Architecture

The SustainaTrend™ platform follows a modular architecture:

- **Frontend Layer**: Flask web application serving the user interface
- **Search Engine**: Hybrid search system combining multiple data sources
- **API Integration Layer**: Connections to external AI and search services
- **Analytics Engine**: Processing and analysis of sustainability metrics
- **Data Layer**: Storage and retrieval of application data

See the [ARCHITECTURE.md](ARCHITECTURE.md) file for detailed architectural information.

## Error Handling & Fallback System

SustainaTrend™ implements a sophisticated error handling and fallback system:

1. **API Status Monitoring**: Continuous monitoring of all external API services
2. **Graceful Degradation**: Automatic fallback to alternative services when primary services fail
3. **Transparent Reporting**: Clear communication of service status and fallback modes
4. **Mock Data System**: Generation of realistic mock data when real data is unavailable

## License

Copyright © 2025 SustainaTrend™. All rights reserved.

## Contact

For questions or support, please contact support@sustainatrend.com