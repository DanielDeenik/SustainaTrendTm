"""
SustainaTrend Intelligence Platform - Minimal Version

This is a simplified version of the Flask application that should run with minimal dependencies.
"""
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
logger = logging.getLogger(__name__)

try:
    from flask import Flask, render_template, redirect, jsonify, g, request
    logger.info("Flask imported successfully")
except ImportError:
    logger.error("Could not import Flask. Make sure it's installed.")
    raise

def get_api_status():
    """Get API connection status for various services"""
    # Check for OpenAI API key
    openai_connected = bool(os.environ.get('OPENAI_API_KEY'))
    
    # Check for PostgreSQL connection
    postgres_connected = bool(os.environ.get('DATABASE_URL'))
    
    return {
        "overall": "online" if postgres_connected else "partial",
        "last_check": datetime.now().isoformat(),
        "services": {
            "openai": {
                "status": "online" if openai_connected else "offline",
                "model": "gpt-4" if openai_connected else None
            }
        },
        "infrastructure": {
            "postgres": {
                "status": "online" if postgres_connected else "offline",
                "version": "14.5" if postgres_connected else None
            }
        },
        "system": {
            "cpu_usage": "N/A",
            "memory_usage": "N/A",
            "uptime": "N/A"
        }
    }

def get_sustainability_metrics():
    """Get sample sustainability metrics"""
    return {
        "emissions": {
            "value": 78.5,
            "unit": "tonnes CO2e",
            "change": -12.3,
            "target": 50
        },
        "energy": {
            "value": 342,
            "unit": "MWh",
            "change": -8.7,
            "target": 300
        },
        "water": {
            "value": 1.28,
            "unit": "million L",
            "change": -4.2,
            "target": 1.0
        },
        "waste": {
            "value": 56.3,
            "unit": "tonnes",
            "change": -15.8,
            "target": 40
        },
        "renewable": {
            "value": 42,
            "unit": "%",
            "change": 5.3,
            "target": 100
        }
    }

def create_app():
    """Create and configure the Flask application"""
    # Create Flask application
    app = Flask(__name__, 
              template_folder='templates',
              static_folder='static')
    
    # Configure the application
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'sustainatrend-dev-key-2025'),
        DEBUG=True
    )
    
    # Theme preference handling
    @app.before_request
    def before_request():
        """Execute before each request to set theme preference"""
        g.theme = request.cookies.get('theme', 'dark')
    
    # Register template context processors
    @app.context_processor
    def inject_theme_preference():
        """Inject theme preference into all templates"""
        return {"theme": g.get('theme', 'dark')}
    
    # Home route redirects to dashboard
    @app.route('/')
    def home():
        """Redirect to dashboard as the primary landing page"""
        return redirect('/dashboard/')
    
    # Dashboard route
    @app.route('/dashboard/')
    def dashboard():
        """Main dashboard with sustainability metrics"""
        metrics = get_sustainability_metrics()
        status = get_api_status()
        return render_template(
            'clean/dashboard.html',
            active_nav='dashboard',
            metrics=metrics,
            status=status,
            page_title="Sustainability Dashboard"
        )
    
    # Toggle theme
    @app.route('/toggle-theme/', methods=['POST'])
    def toggle_theme():
        """Toggle between light and dark theme"""
        # Get current theme from cookie or default to dark
        current_theme = request.cookies.get('theme', 'dark')
        # Toggle theme
        new_theme = 'light' if current_theme == 'dark' else 'dark'
        
        # Create response with redirect to previous page
        response = redirect(request.referrer or '/')
        
        # Set cookie with new theme
        response.set_cookie('theme', new_theme, max_age=31536000)  # 1 year
        
        return response
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)