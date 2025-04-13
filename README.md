# SustainaTrend™ Intelligence Platform

A comprehensive platform for tracking, analyzing, and monetizing sustainability trends across industries.

## Features

- **Real-time Analytics Dashboard**: Track sustainability metrics and trends
- **Data Visualization**: Interactive charts and graphs
- **Story Generation**: AI-powered sustainability storytelling
- **Monetization Strategies**: Data-driven recommendations
- **Performance Monitoring**: Built-in analytics and optimization
- **Error Tracking**: Comprehensive error handling and logging

## Prerequisites

- Python 3.8+
- MongoDB 4.4+
- Node.js 14+ (for frontend development)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/sustainatrend.git
   cd sustainatrend
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate   # Windows
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Initialize the database:
   ```
   python scripts/init_db.py
   ```

## Running the Application

### Development Mode

```
python run.py
```

This will start the application in development mode with debugging enabled.

### Production Mode

```
set DEBUG=False
python run.py
```

This will start the application in production mode using the Waitress server.

## Accessing the Application

Once the application is running, you can access it at:

- Main Dashboard: http://127.0.0.1:5000/
- Analytics Dashboard: http://127.0.0.1:5000/analytics
- API Documentation: http://127.0.0.1:5000/api/docs
- Health Check: http://127.0.0.1:5000/health

## Project Structure

```
sustainatrend/
├── src/
│   ├── frontend/
│   │   ├── static/
│   │   ├── templates/
│   │   └── routes/
│   ├── data_providers/
│   └── utils/
├── scripts/
├── tests/
├── docs/
├── .env
├── requirements.txt
└── run.py
```

## API Documentation

API documentation is available at `/api/docs` when running the application.

## Testing

Run tests with:
```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@sustainatrend.com or open an issue in the repository.