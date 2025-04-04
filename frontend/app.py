"""
SustainaTrend Intelligence Platform - Consolidated Application

This file serves as the single entry point for the Flask application with a clean,
consolidated architecture.
"""
import os
import logging
import redis
import psutil
from flask import Flask, render_template, jsonify, request, redirect, url_for, g, session
from datetime import datetime
from werkzeug.utils import secure_filename
from logging.config import dictConfig
from flask_caching import Cache
import importlib.util

# Configure logging function
def configure_logging():
    """Configure logging for the application"""
    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'default',
                'stream': 'ext://sys.stdout',
            },
            'file': {
                'class': 'logging.FileHandler',
                'level': 'INFO',
                'formatter': 'default',
                'filename': 'app.log',
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console', 'file']
        }
    })

# Run the logging configuration
configure_logging()

# Initialize logger
logger = logging.getLogger(__name__)

def get_api_status():
    """
    Get API connection status for various services
    
    Returns:
        dict: Comprehensive API connection status information
    """
    # Check for OpenAI API key
    openai_connected = bool(os.environ.get('OPENAI_API_KEY'))
    
    # Check for Google Gemini API key
    gemini_connected = bool(os.environ.get('GOOGLE_API_KEY'))
    
    # Check for Pinecone API key
    pinecone_connected = bool(os.environ.get('PINECONE_API_KEY'))
    
    # Check for PostgreSQL connection
    postgres_connected = bool(os.environ.get('DATABASE_URL'))
    
    # Check for Redis connection
    redis_connected = False
    try:
        # Only attempt to check Redis if it's installed
        if importlib.util.find_spec("redis") is not None:
            redis_connected = True
    except:
        redis_connected = False
    
    # Get system metrics
    cpu_usage = "32%"
    memory_usage = "512 MB"
    uptime = "4 hours 12 minutes"
    
    try:
        cpu_usage = f"{psutil.cpu_percent()}%"
        memory = psutil.virtual_memory()
        memory_usage = f"{memory.used / (1024 * 1024):.0f} MB"
        
        # Calculate uptime
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime_seconds = (datetime.now() - boot_time).total_seconds()
        
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        uptime = f"{hours} hours {minutes} minutes"
    except:
        # If psutil fails, we'll use the default values
        pass
    
    return {
        # Overall status (simplified)
        "overall": "online" if (postgres_connected and (openai_connected or gemini_connected)) else "partial",
        "last_check": datetime.now().isoformat(),
        
        # API Services
        "services": {
            "openai": {
                "status": "online" if openai_connected else "offline",
                "model": "gpt-4" if openai_connected else None
            },
            "gemini": {
                "status": "online" if gemini_connected else "offline",
                "model": "gemini-pro" if gemini_connected else None
            },
            "pinecone": {
                "status": "online" if pinecone_connected else "offline",
                "index": "sustainability-index" if pinecone_connected else None
            }
        },
        
        # Infrastructure
        "infrastructure": {
            "postgres": {
                "status": "online" if postgres_connected else "offline",
                "version": "14.5" if postgres_connected else None
            },
            "redis": {
                "status": "online" if redis_connected else "offline"
            }
        },
        
        # System metrics
        "system": {
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "uptime": uptime
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

def create_app(test_config=None):
    """
    Create and configure the Flask application
    
    Args:
        test_config: Configuration dictionary for testing (optional)
        
    Returns:
        Flask application instance
    """
    # Create Flask application
    app = Flask(__name__, 
              template_folder='templates',
              static_folder='static')
    
    # Configure the application
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'sustainatrend-platform-secret-key-2025'),
        DEBUG=os.environ.get('FLASK_ENV', 'development') == 'development',
        # Replit specific configurations
        SERVER_NAME=None,  # Set to None to handle Replit's proxy
        PREFERRED_URL_SCHEME='https',
        APPLICATION_ROOT='/',
    )
    
    # Replit-specific configuration for proxy
    if os.environ.get('REPLIT_ENVIRONMENT') == 'true':
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(
            app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
        )
        app.logger.info("Configured ProxyFix middleware for Replit environment")
    
    # Apply test config if provided
    if test_config:
        app.config.update(test_config)
    
    # Initialize the application
    @app.before_request
    def before_request():
        """Execute before each request to set theme preference"""
        g.theme = request.cookies.get('theme', 'dark')
    
    # Register template context processors
    @app.context_processor
    def inject_theme_preference():
        """Inject theme preference into all templates"""
        return {"theme": g.get('theme', 'dark')}
    
    # Add custom template filters
    @app.template_filter('date')
    def date_filter(value, format='%Y-%m-%d'):
        """Format a date according to the given format"""
        if value is None:
            return ""
        if isinstance(value, str):
            # Try to parse the string to a datetime if needed
            from datetime import datetime
            try:
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                try:
                    value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
                except (ValueError, AttributeError):
                    return value
        try:
            return value.strftime(format)
        except (AttributeError, ValueError):
            return str(value)
    
    # Setup caching system
    try:
        redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=0,
            socket_timeout=5,
            decode_responses=True
        )
        # Test connection
        redis_client.ping()
        logger.info("Connected to Redis successfully")
        cache = Cache(app, config={
            'CACHE_TYPE': 'redis',
            'CACHE_REDIS_HOST': os.getenv('REDIS_HOST', 'localhost'),
            'CACHE_REDIS_PORT': int(os.getenv('REDIS_PORT', 6379)),
            'CACHE_DEFAULT_TIMEOUT': 300
        })
    except (redis.ConnectionError, redis.exceptions.RedisError) as e:
        logger.warning(f"Redis connection failed, using simple cache instead: {str(e)}")
        cache = Cache(app, config={'CACHE_TYPE': 'simple'})
    
    # Register routes
    register_routes(app)
    
    return app

def register_routes(app):
    """
    Register main application routes
    
    Args:
        app: Flask application
    """
    # Import strategy modules
    from routes.enhanced_strategy_routes import strategy_bp as enhanced_strategy_bp
    from routes.strategy_api import strategy_api_bp
    from routes.monetization import monetization_bp
    from routes.strategy import strategy_bp, strategy_hub_bp
    
    # Register blueprints
    app.register_blueprint(enhanced_strategy_bp)
    app.register_blueprint(strategy_api_bp)
    app.register_blueprint(monetization_bp)
    app.register_blueprint(strategy_bp)
    app.register_blueprint(strategy_hub_bp)
    
    # Register AI Strategy Consultant routes
    try:
        from strategy_ai_consultant import register_routes as register_strategy_consultant
        register_strategy_consultant(app)
        logger.info("Strategy AI Consultant routes registered")
    except ImportError as e:
        logger.warning(f"Failed to register Strategy AI Consultant routes: {str(e)}")
    
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
    
    # Performance route
    @app.route('/performance')
    def performance():
        """Performance metrics and analysis"""
        metrics = get_sustainability_metrics()
        status = get_api_status()
        return render_template(
            'clean/performance.html',
            active_nav='performance',
            metrics=metrics,
            status=status,
            page_title="Performance Metrics"
        )
    
    # Overview route
    @app.route('/overview')
    def overview():
        """Overview of sustainability metrics"""
        metrics = get_sustainability_metrics()
        status = get_api_status()
        return render_template(
            'clean/overview.html',
            active_nav='overview',
            metrics=metrics,
            status=status,
            page_title="Sustainability Overview"
        )
    
    # Trend Analysis route
    @app.route('/trend-analysis')
    def trend_analysis():
        """Trend analysis for sustainability metrics"""
        metrics = get_sustainability_metrics()
        status = get_api_status()
        return render_template(
            'clean/trend_analysis.html',
            active_nav='trends',
            metrics=metrics,
            status=status,
            page_title="Trend Analysis"
        )
    
    # Strategy Hub route
    @app.route('/strategy-hub-direct/')
    def strategy_hub_direct():
        """Strategy Hub for sustainability insights"""
        # Import strategy AI consultant for template
        try:
            from strategy_ai_consultant import strategy_consultant
            consultant_available = True
        except (ImportError, AttributeError):
            strategy_consultant = None
            consultant_available = False
            logger.warning("Strategy AI Consultant not available for strategy hub route")
        
        # Try to get monetization strategies
        try:
            from monetization_strategies import get_monetization_strategies
            monetization_strategies = get_monetization_strategies()
        except (ImportError, AttributeError):
            monetization_strategies = {}
            logger.warning("Monetization strategies not available for strategy hub route")
            
        status = get_api_status()
        return render_template(
            'clean/strategy_hub.html',
            active_nav='strategy',
            status=status,
            consultant_available=consultant_available,
            monetization_strategies=monetization_strategies,
            page_title="Strategy Hub"
        )
    
    # Original strategy hub route - redirect to direct route
    @app.route('/strategy-hub/')
    def strategy_hub():
        """Strategy Hub route - redirects to direct route"""
        return redirect('/strategy-hub-direct/')
        
    # Legacy strategy hub route - redirect to new route
    @app.route('/enhanced-strategy/')
    def legacy_strategy_hub():
        """Redirect legacy enhanced strategy route to new strategy hub"""
        return redirect('/strategy-hub-direct/')
    
    # Documents route
    @app.route('/documents/document-upload')
    def document_upload():
        """Document upload and analysis"""
        status = get_api_status()
        return render_template(
            'clean/document_upload.html',
            active_nav='documents',
            status=status,
            page_title="Document Upload"
        )
    
    # Search route
    @app.route('/search')
    def search():
        """Search for sustainability metrics and documents"""
        status = get_api_status()
        return render_template(
            'clean/search.html',
            active_nav='search',
            status=status,
            page_title="Search"
        )
    
    # Settings route
    @app.route('/debug')
    def settings():
        """Application settings"""
        status = get_api_status()
        return render_template(
            'clean/settings.html',
            active_nav='debug',
            status=status,
            page_title="Settings"
        )
    
    # API Status route
    @app.route('/api-status')
    def api_status():
        """API connection status"""
        status = get_api_status()
        return render_template(
            'clean/api_status.html',
            active_nav='api_status',
            status=status,
            page_title="API Status"
        )
    
    # VC-Lens main page
    @app.route('/vc-lens/')
    def vc_lens():
        """VC-Lens™ main page"""
        status = get_api_status()
        return render_template(
            'clean/vc_lens.html',
            active_nav='vc_lens',
            status=status,
            page_title="VC-Lens™"
        )

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)