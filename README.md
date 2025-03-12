# SustainaTrend™ Intelligence Platform

A cutting-edge AI-driven platform that transforms complex sustainability data into clear visual stories and actionable intelligence for real estate and organizations.

![SustainaTrend](generated-icon.png)

## Overview

SustainaTrend™ follows a visual-first, AI-driven architecture that prioritizes storytelling over traditional dashboards. Our core design principle: "Only the minimum required actionable data, visualized clearly, AI-generated stories, and no clutter. AI is always ready to explain."

## Key Features

- **Home AI Trends Feed**: Real-time sustainability trends from social media and CSRD PDFs, presented as visual story cards.
- **Company & Sector Risk Tracker**: AI-analyzed risks and opportunities with auto-generated KPIs and narratives.
- **PDF & Report Analyzer**: Upload CSRD/ESG reports for AI-powered extraction and comparison against market trends.
- **AI Sustainability Story Cards**: Generate narrative + chart + recommendation for any metric or trend.
- **Sustainability Co-Pilot**: Contextual AI assistant for insights, questions, and dynamic story creation.
- **Minimal API & Data Terminal**: Programmatic access to sustainability trends data with minimal UI exposure.

## Technology Stack

### Frontend
- **React/SvelteKit**: For highly responsive, component-based UI
- **D3.js/Recharts**: For customizable, AI-driven visualizations
- **TailwindCSS**: For clean, consistent styling
- **Web Components**: For encapsulated, reusable story cards

### Backend
- **FastAPI**: High-performance API framework
- **LangChain/LlamaIndex**: For RAG and AI orchestration
- **PostgreSQL**: For structured data storage
- **Vector Database**: For semantic search capabilities
- **Redis**: For caching and real-time features

### AI & ML
- **Google Gemini API**: Core LLM for text generation and reasoning
- **OpenAI API (Optional)**: For specialized tasks
- **Hugging Face Models**: For specialized NLP tasks
- **Custom ML Pipeline**: For trend analysis and anomaly detection
- **Autonomous Agents**: For continuous data monitoring and story generation

## Architecture

The platform follows a visual-first, AI-driven architecture focused on storytelling:

1. **Data Collection Layer**: Web scrapers, PDF processors, and API connectors for sustainability data ingestion
2. **AI Processing Layer**: LLM processing, insight generation, and story creation
3. **Presentation Layer**: Minimal UI with story cards and contextual controls
4. **Interaction Layer**: Co-Pilot AI for conversational exploration of sustainability data

## Core Modules

- **Home AI Trends Feed**: Real-time sustainability trends presented as visual story cards
- **Company & Sector Risk Tracker**: AI-analyzed sustainability risks and opportunities
- **PDF & Report Analyzer**: AI-powered document analysis with framework mapping
- **AI Story Cards Generator**: Narrative + visualization + recommendation creation
- **Sustainability Co-Pilot**: Contextual AI assistant for insights and exploration
- **Minimal API + Data Terminal**: Programmatic access with minimal UI exposure

## Getting Started

### Prerequisites

- Node.js 20+ and npm/pnpm
- Python 3.11+
- PostgreSQL database
- Redis for caching and real-time features
- Google Gemini API key for AI functionality

### Installation

1. Clone the repository
2. Install frontend dependencies: `cd frontend && npm install`
3. Install backend dependencies: `cd backend && pip install -r requirements.txt`
4. Set up environment variables in `.env` file:
   ```
   # Database connection
   DATABASE_URL=postgresql://user:password@localhost:5432/sustainatrend
   
   # AI APIs
   GEMINI_API_KEY=your_gemini_api_key
   
   # Optional services
   REDIS_URL=redis://localhost:6379
   ```
5. Initialize the database: `npm run db:push`
6. Start the application: `npm run dev`

### Development Mode

The platform can be started in different configurations:

- **Complete Platform**: `npm run dev`
- **Frontend Only**: `npm run dev:frontend`
- **Backend Only**: `npm run dev:backend`
- **Story Generator Service**: `npm run dev:storytelling`

## Development

### Project Structure

```
├── frontend/                    # React/SvelteKit web application
│   ├── components/              # Reusable UI components
│   │   ├── atoms/               # Basic UI elements
│   │   ├── molecules/           # Compound components
│   │   ├── organisms/           # Complex component assemblies
│   │   └── story-cards/         # AI-generated story card templates
│   ├── pages/                   # Application pages/routes
│   ├── services/                # Frontend service modules
│   └── ai-copilot/              # Co-Pilot integration
├── backend/                     # FastAPI services
│   ├── ai/                      # AI processing modules
│   │   ├── storytelling/        # Story generation
│   │   ├── document-analysis/   # PDF/document processing
│   │   ├── trend-detection/     # Trend analysis
│   │   └── agents/              # Autonomous agents
│   ├── data-collectors/         # Data ingestion services
│   ├── api/                     # API endpoints
│   └── models/                  # Data models
└── shared/                      # Shared utilities
```

### Key Interfaces

- **Home Feed**: `http://localhost:5000/`
- **Company Risk Tracker**: `http://localhost:5000/risk-tracker`
- **PDF Analyzer**: `http://localhost:5000/document-analysis`
- **Story Generator**: `http://localhost:5000/story-generator`
- **Co-Pilot API**: `http://localhost:8080/api/copilot`
- **Data Terminal**: `http://localhost:8080/api/terminal`

## License

Copyright © 2025 SustainaTrend. All rights reserved.