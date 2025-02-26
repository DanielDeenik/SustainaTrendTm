# Sustainability Intelligence Platform

A cutting-edge sustainability intelligence platform that transforms complex environmental data into intuitive, actionable insights through advanced AI technologies.

## Architecture

This project uses a three-tier architecture:
1. **PostgreSQL Database** - Stores sustainability metrics and analysis results
2. **FastAPI Backend** - Provides API endpoints for accessing the data
3. **Flask Frontend** - Delivers the dashboard UI and visualizations

## Getting Started

### Prerequisites

- PostgreSQL database (automatically provisioned in Replit)
- Python 3.11+
- Redis (for caching, optional)

### Running the Application

The easiest way to run the application is to use the provided start script:

```bash
./start-all.sh
```

This script will:
1. Ensure the PostgreSQL database is ready
2. Seed the database with sample sustainability metrics data
3. Start the FastAPI backend on port 8000
4. Start the Flask frontend on port 5000

### Accessing the Application

- **Dashboard UI**: http://localhost:5000/dashboard
- **API Endpoints**: 
  - Health Check: http://localhost:8000/health
  - Metrics Data: http://localhost:8000/api/metrics

## Project Structure

```
.
├── backend/                 # FastAPI backend service
│   ├── database.py          # Database connection management
│   ├── main.py              # FastAPI application and routes
│   ├── middleware/          # FastAPI middleware
│   ├── models.py            # Database models
│   ├── routes/              # API route definitions
│   ├── seed_database.py     # Database seeding script
│   ├── start.sh             # Backend startup script
│   └── utils/               # Utility functions
├── frontend/                # Flask frontend service
│   ├── app.py               # Flask application and routes
│   ├── gunicorn.conf.py     # Gunicorn configuration
│   ├── start.sh             # Frontend startup script
│   ├── static/              # Static assets (CSS, JS)
│   └── templates/           # Jinja2 HTML templates
├── logs/                    # Application logs directory
├── README.md                # Project documentation
├── start-all.sh             # Combined startup script
└── test-integration.sh      # Integration test script
```

## API Documentation

### FastAPI Endpoints

- `GET /health` - Health check endpoint
- `GET /api/metrics` - Get all sustainability metrics

### Flask Routes

- `GET /` - Home page
- `GET /dashboard` - Sustainability metrics dashboard
- `GET /api/metrics` - Frontend API proxy to backend metrics
- `GET /debug` - Debug information page

## PostgreSQL Database Schema

The primary database table is `metrics`:

```sql
CREATE TABLE metrics (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('emissions', 'water', 'energy', 'waste', 'social', 'governance')),
    value NUMERIC NOT NULL CHECK (value >= 0),
    unit TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metric_metadata JSONB DEFAULT '{}'::jsonb
)
```

## Testing

Use the test-integration.sh script to verify the entire integration is working:

```bash
./test-integration.sh
```

This performs checks on the database connection, FastAPI backend, and Flask frontend.
