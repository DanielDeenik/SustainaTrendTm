# SustainaTrend™ Intelligence Platform

A comprehensive platform for sustainability analytics, insights, and strategy.

## Features

- **Real-time Analytics Dashboard**: Track sustainability metrics and trends
- **Data Visualization**: Interactive charts and graphs
- **Story Generation**: AI-powered sustainability storytelling
- **Monetization Strategies**: Data-driven recommendations
- **Performance Monitoring**: Built-in analytics and optimization
- **Error Tracking**: Comprehensive error handling and logging
- **AI-Powered Analysis**: Integration with OpenAI and other AI services
- **Document Processing**: Advanced document analysis and querying
- **Trend Analysis**: Real-time trend tracking and virality benchmarking
- **Sustainability Reporting**: Automated report generation

## Architecture

The application follows a modular architecture with the following components:

### Core Components

1. **Frontend Layer** (`src/frontend/`)
   - Flask-based web application
   - Template-based rendering
   - Static asset management
   - Route handlers for different features

2. **Service Layer** (`src/frontend/services/`)
   - AI Services (OpenAI, Google AI, etc.)
   - MongoDB Service for data persistence
   - Document Processing Service
   - Enhanced Search Service
   - Sustainability Co-Pilot
   - Strategy AI Consultant

3. **Data Layer** (`src/frontend/data_moat/`)
   - Data providers and connectors
   - Data transformation utilities
   - Caching mechanisms

4. **Utility Layer** (`src/frontend/utils/`)
   - Helper functions
   - Common utilities
   - Data processing tools

### Key Features

1. **AI Integration**
   - OpenAI for natural language processing
   - Google AI for enhanced capabilities
   - Pinecone for vector search
   - BERT for sentiment analysis

2. **Data Management**
   - MongoDB for data storage
   - Caching for performance optimization
   - File upload handling
   - Data validation and sanitization

3. **Security**
   - Environment-based configuration
   - API key management
   - Error handling and logging
   - Rate limiting

## Prerequisites

- Python 3.8+
- MongoDB 4.4+
- Node.js 14+ (for frontend development)
- OpenAI API key
- Google AI API key (optional)
- Pinecone API key (optional)

## Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Configure the `.env` file with your settings
6. Initialize the database: `python src/frontend/scripts/init_db.py`

## Running the Application

### Manual Start

To start the application manually, run:

```bash
python run.py
```

### Windows Shortcuts

The repository includes a batch file for Windows users:

- `start_sustainatrend.bat` - Starts the application using the unified entry point

## Automatic Startup Options

### Option 1: Startup Folder (Simple)

Run `setup_autostart.bat` to create a shortcut in the Windows Startup folder. This will start the application when you log in.

### Option 2: Windows Service (Recommended)

For a more robust solution, install the application as a Windows service:

1. Download and install [NSSM](https://nssm.cc/download)
2. Run `install_service.bat`
3. The service will start automatically when Windows starts

## Accessing the Application

Once running, the application is accessible at:

- http://127.0.0.1:5000 (localhost)
- http://localhost:5000 (localhost alternative)

## Troubleshooting

If you encounter issues:

1. Check the logs in the `logs` directory
2. Ensure MongoDB is running if you're not using mock data
3. Verify your firewall settings allow connections to port 5000
4. Check that all dependencies are installed correctly

## License

Proprietary - All rights reserved

## Support

For support, email support@sustainatrend.com or open an issue in the repository.