# SustainaTrend

A comprehensive sustainability trend analysis and storytelling platform.

## Project Structure

```
SustainaTrend/
├── src/                    # Source code
│   ├── frontend/          # Frontend application code
│   │   ├── static/       # Static assets (CSS, JS, images)
│   │   ├── templates/    # HTML templates
│   │   └── utils/        # Frontend utilities
│   └── backend/          # Backend application code
│       ├── api/          # API endpoints
│       ├── models/       # Data models
│       ├── services/     # Business logic
│       └── utils/        # Backend utilities
├── config/               # Configuration files
├── tests/               # Test files
├── docs/                # Documentation
├── assets/              # Project assets
│   ├── images/         # Image assets
│   └── uploads/        # User uploads
└── scripts/            # Utility scripts
```

## Key Components

### Frontend
- Storytelling interface
- Strategy hub
- Dashboard
- Document upload and processing
- Trend analysis visualization

### Backend
- API endpoints
- Database models
- Search engine integration
- Document processing
- AI-driven analysis

## Setup and Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   npm install
   ```

2. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update configuration values

3. Initialize the database:
   ```bash
   python scripts/initialize_db.py
   ```

4. Run the development server:
   ```bash
   python src/backend/main.py
   ```

## Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Development Guide](docs/DEVELOPMENT.md)

## Testing

Run tests using:
```bash
python -m pytest tests/
```

## License

[License information]