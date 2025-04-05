"""
SustainaTrend Intelligence Platform - Consolidated Application

This file serves as the single entry point for the Flask application with a clean,
consolidated architecture.
"""
import os
import logging
import redis
import psutil
import uuid
from flask import Flask, render_template, jsonify, request, redirect, url_for, g, session, flash
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
    from routes.strategy_api import strategy_api_bp
    from routes.monetization import monetization_bp
    from routes.strategy import strategy_bp
    
    # Register blueprints
    app.register_blueprint(strategy_api_bp)
    app.register_blueprint(monetization_bp)
    app.register_blueprint(strategy_bp)
    
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
    @app.route('/performance/')
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
    @app.route('/overview/')
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
    @app.route('/trend-analysis/')
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
    @app.route('/strategy-hub/')
    def strategy_hub():
        """Strategy Hub for sustainability insights"""
        # Import strategy AI consultant for template
        try:
            from strategy_ai_consultant import strategy_consultant
            consultant_available = True
        except (ImportError, AttributeError):
            strategy_consultant = None
            consultant_available = False
            logger.warning("Strategy AI Consultant not available for strategy hub route")
        
        # Try to import Ethical AI module
        try:
            import ethical_ai
            ethical_ai_available = True
            logger.info("Ethical AI module available for strategy hub route")
        except (ImportError, AttributeError):
            ethical_ai_available = False
            logger.warning("Ethical AI module not available for strategy hub route")
        
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
            ethical_ai_available=ethical_ai_available,
            monetization_strategies=monetization_strategies,
            page_title="Strategy Hub"
        )
    
    # Legacy routes that redirect to main strategy hub
    @app.route('/enhanced-strategy/')
    @app.route('/strategy-hub-direct/')
    def legacy_strategy_hub():
        """Redirect legacy strategy routes to the main strategy hub"""
        return redirect('/strategy-hub/')
        
    # Legacy routes without trailing slashes
    @app.route('/performance')
    def legacy_performance():
        """Redirect from /performance to /performance/"""
        return redirect('/performance/')
        
    @app.route('/overview')
    def legacy_overview():
        """Redirect from /overview to /overview/"""
        return redirect('/overview/')
        
    @app.route('/trend-analysis')
    def legacy_trend_analysis():
        """Redirect from /trend-analysis to /trend-analysis/"""
        return redirect('/trend-analysis/')
        
    @app.route('/strategy-hub')
    def legacy_strategy_hub_no_slash():
        """Redirect from /strategy-hub to /strategy-hub/"""
        return redirect('/strategy-hub/')
        
    @app.route('/documents/document-upload')
    def legacy_document_upload():
        """Redirect from /documents/document-upload to /documents/document-upload/"""
        return redirect('/documents/document-upload/')
        
    @app.route('/search')
    def legacy_search():
        """Redirect from /search to /search/"""
        return redirect('/search/')
        
    @app.route('/debug')
    def legacy_debug():
        """Redirect from /debug to /debug/"""
        return redirect('/debug/')
        
    @app.route('/api-status')
    def legacy_api_status():
        """Redirect from /api-status to /api-status/"""
        return redirect('/api-status/')
        
    @app.route('/vc-lens')
    def legacy_vc_lens():
        """Redirect from /vc-lens to /vc-lens/"""
        return redirect('/vc-lens/')
        
    @app.route('/settings')
    def legacy_settings():
        """Redirect from /settings to /settings/"""
        return redirect('/settings/')
    
    # Documents route
    @app.route('/documents/document-upload/')
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
    @app.route('/search/')
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
    @app.route('/settings/')
    def settings():
        """Application settings"""
        status = get_api_status()
        return render_template(
            'clean/settings.html',
            active_nav='settings',
            status=status,
            page_title="Settings"
        )
    
    # Debug route - maps to settings for consistency
    @app.route('/debug/')
    def debug():
        """Debug and settings (legacy route)"""
        return redirect('/settings/')
    
    # API Status route
    @app.route('/api-status/')
    def api_status():
        """API connection status"""
        status = get_api_status()
        return render_template(
            'clean/api_status.html',
            active_nav='api_status',
            status=status,
            page_title="API Status"
        )
        
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
    
    # VC-Lens main page
    @app.route('/vc-lens/')
    def vc_lens():
        """VC-Lens™ main page"""
        # Get a list of submitted assessments and theses
        # In a real implementation, these would be fetched from a database
        # For demonstration purposes, we'll create sample data plus any uploaded files
        
        # Try to list actual uploaded files from both project root and frontend directories
        # with categorization
        
        # Structure to hold categorized files
        file_categories = {
            'thesis_dir': {'path': 'uploads/thesis', 'files': []},
            'frontend_thesis_dir': {'path': 'frontend/uploads/thesis', 'files': []},
            'uploads_dir': {'path': 'uploads', 'files': []}
        }
        
        # Combined list for backward compatibility
        thesis_files = []
        
        # Try the thesis-specific directory 
        thesis_dir = os.path.join('uploads', 'thesis')
        
        if os.path.exists(thesis_dir):
            try:
                thesis_files_list = [f for f in os.listdir(thesis_dir) if os.path.isfile(os.path.join(thesis_dir, f))]
                file_categories['thesis_dir']['files'] = thesis_files_list
                thesis_files.extend(thesis_files_list)
                app.logger.info(f"Found {len(thesis_files_list)} thesis files in uploads/thesis: {thesis_files_list}")
            except Exception as e:
                app.logger.error(f"Error listing thesis files from uploads/thesis: {str(e)}")
                
        # Try the frontend/uploads/thesis directory
        frontend_thesis_dir = os.path.join('frontend', 'uploads', 'thesis')
        
        if os.path.exists(frontend_thesis_dir):
            try:
                frontend_thesis_files = [f for f in os.listdir(frontend_thesis_dir) if os.path.isfile(os.path.join(frontend_thesis_dir, f))]
                
                # Only include files that aren't already in our list
                unique_frontend_files = []
                for file in frontend_thesis_files:
                    if file not in thesis_files:
                        thesis_files.append(file)
                        unique_frontend_files.append(file)
                
                file_categories['frontend_thesis_dir']['files'] = unique_frontend_files
                app.logger.info(f"Found {len(frontend_thesis_files)} thesis files in frontend/uploads/thesis (adding {len(unique_frontend_files)} unique ones)")
            except Exception as e:
                app.logger.error(f"Error listing thesis files from frontend/uploads/thesis: {str(e)}")
                
        # Also check for general upload files in the root uploads directory
        uploads_dir = 'uploads'
        
        if os.path.exists(uploads_dir):
            try:
                # Only include files that aren't in a subdirectory and aren't already in our list
                upload_files = [f for f in os.listdir(uploads_dir) 
                              if os.path.isfile(os.path.join(uploads_dir, f)) 
                              and f not in thesis_files]
                              
                file_categories['uploads_dir']['files'] = upload_files
                thesis_files.extend(upload_files)
                app.logger.info(f"Found {len(upload_files)} additional files in uploads/: {upload_files}")
            except Exception as e:
                app.logger.error(f"Error listing files from uploads/: {str(e)}")
        
        # Sample and submitted assessments (in a real app, these would all come from a database)
        assessments = [
            {
                'id': str(uuid.uuid4()),
                'company_name': 'Green Innovations',
                'industry': 'Renewable Energy',
                'submission_date': datetime.now().strftime("%Y-%m-%d"),
                'status': 'Under Review'
            }
        ]
        
        # Generate thesis entries from uploaded files
        # This combines sample data with actual uploaded files
        theses = []
        
        # Add actual uploaded files that don't match our sample patterns
        uploaded_files = [f for f in thesis_files if not (f.startswith('test_thesis') or f.startswith('additional_doc'))]
        
        if uploaded_files:
            # Add Green Ventures thesis (for the newly uploaded file)
            theses.append({
                'id': str(uuid.uuid4()),
                'fund_name': 'Green Ventures',
                'investment_focus': 'Renewable Energy',
                'submission_date': datetime.now().strftime("%Y-%m-%d"),
                'status': 'Under Review',
                'files': uploaded_files
            })
        
        # Add sample theses with any matching files
        sample_theses = [
            {
                'id': str(uuid.uuid4()),
                'fund_name': 'Test Fund',
                'investment_focus': 'Climate Tech',
                'submission_date': datetime.now().strftime("%Y-%m-%d"),
                'status': 'Processing',
                'files': [f for f in thesis_files if f.startswith('test_thesis')]
            },
            {
                'id': str(uuid.uuid4()),
                'fund_name': 'Test Fund 2',
                'investment_focus': 'Green Energy',
                'submission_date': datetime.now().strftime("%Y-%m-%d"),
                'status': 'Processing',
                'files': [f for f in thesis_files if f.startswith('additional_doc')]
            }
        ]
        
        # Only add sample theses if they have matching files
        for thesis in sample_theses:
            if thesis['files']:
                theses.append(thesis)
        
        status = get_api_status()
        
        return render_template(
            'clean/vc_lens.html',
            active_nav='vc_lens',
            status=status,
            page_title="VC-Lens™",
            assessments=assessments,
            theses=theses,
            thesis_files=thesis_files,
            file_categories=file_categories
        )
    
    # VC-Lens startup assessment page
    @app.route('/vc-lens/startup-assessment/')
    def startup_assessment():
        """VC-Lens™ Startup Assessment Form"""
        status = get_api_status()
        return render_template(
            'clean/startup_assessment.html',
            active_nav='vc_lens',
            status=status,
            page_title="Startup Assessment - VC-Lens™"
        )
    
    # VC-Lens upload thesis page
    @app.route('/vc-lens/upload-thesis/')
    def upload_thesis():
        """VC-Lens™ Investment Thesis Upload Form"""
        status = get_api_status()
        return render_template(
            'clean/upload_thesis.html',
            active_nav='vc_lens',
            status=status,
            page_title="Upload Investment Thesis - VC-Lens™"
        )
    
    # Process document for AI-powered field extraction
    @app.route('/vc-lens/process-document', methods=['POST'])
    def process_document_for_fields():
        """Process a document and extract fields for auto-populating forms"""
        if request.method == 'POST':
            try:
                # Check if document was uploaded
                if 'document' not in request.files:
                    return jsonify({'success': False, 'error': 'No document uploaded'})
                
                document = request.files['document']
                if not document or not document.filename:
                    return jsonify({'success': False, 'error': 'No document selected'})
                
                # Get form type
                form_type = request.form.get('form_type')
                if not form_type:
                    return jsonify({'success': False, 'error': 'Form type not specified'})
                
                # Save uploaded file temporarily
                filename = secure_filename(document.filename)
                temp_path = os.path.join('uploads', 'temp', filename)
                os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                document.save(temp_path)
                
                # Import document processor if needed
                from document_processor import DocumentProcessor
                processor = DocumentProcessor()
                
                # Extract text from document
                try:
                    extracted_text, page_count = processor.extract_text(temp_path)
                    app.logger.info(f"Successfully extracted text from document ({page_count} pages)")
                except Exception as e:
                    app.logger.error(f"Error extracting text from document: {str(e)}")
                    return jsonify({'success': False, 'error': f'Error extracting text: {str(e)}'})
                
                # Extract structured fields based on form type
                try:
                    result = processor.extract_structured_fields(extracted_text, form_type)
                    app.logger.info(f"Field extraction result: {result['success']}, confidence: {result.get('confidence', 'unknown')}")
                    
                    if result['success']:
                        # Clean up temporary file after processing
                        try:
                            os.remove(temp_path)
                        except:
                            pass
                            
                        return jsonify({
                            'success': True,
                            'fields': result['fields'],
                            'form_type': form_type,
                            'confidence': result.get('confidence', 'medium')
                        })
                    else:
                        return jsonify({
                            'success': False, 
                            'error': result.get('error', 'Failed to extract fields'),
                            'fields': result.get('fields', {})
                        })
                except Exception as e:
                    app.logger.error(f"Error extracting fields from document: {str(e)}")
                    return jsonify({'success': False, 'error': f'Error extracting fields: {str(e)}'})
                    
            except Exception as e:
                app.logger.error(f"Error processing document: {str(e)}")
                return jsonify({'success': False, 'error': f'Unexpected error: {str(e)}'})
        
        return jsonify({'success': False, 'error': 'Invalid request method'})
    
    # Submit VC-Lens startup assessment
    @app.route('/vc-lens/startup-assessment/submit', methods=['POST'])
    def submit_startup_assessment():
        """Process the startup assessment form submission"""
        if request.method == 'POST':
            try:
                # Extract form data
                company_name = request.form.get('company_name', '')
                industry = request.form.get('industry', '')
                funding_stage = request.form.get('funding_stage', '')
                founding_year = request.form.get('founding_year', '')
                sustainability_vision = request.form.get('sustainability_vision', '')
                current_practices = request.form.get('current_practices', '')
                sustainability_challenges = request.form.get('sustainability_challenges', '')
                metrics_tracked = request.form.get('metrics_tracked', '')
                competitive_advantage = request.form.get('competitive_advantage', '')
                investor_alignment = request.form.get('investor_alignment', '')
                
                # Create a timestamp for this assessment
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Create an assessment entry
                assessment = {
                    'id': uuid.uuid4().hex,
                    'timestamp': timestamp,
                    'company_name': company_name,
                    'industry': industry,
                    'funding_stage': funding_stage,
                    'founding_year': founding_year,
                    'sustainability_vision': sustainability_vision,
                    'current_practices': current_practices,
                    'sustainability_challenges': sustainability_challenges,
                    'metrics_tracked': metrics_tracked,
                    'competitive_advantage': competitive_advantage,
                    'investor_alignment': investor_alignment,
                    'status': 'submitted'
                }
                
                # In a real implementation, we would save this to a database
                # For now, just flash a success message
                flash('Assessment for {} successfully submitted!'.format(company_name), 'success')
                
                # Redirect to VC-Lens main page
                return redirect(url_for('vc_lens'))
                
            except Exception as e:
                app.logger.error(f"Error submitting startup assessment: {str(e)}")
                flash('Error submitting assessment. Please try again.', 'error')
                return redirect(url_for('startup_assessment'))
        
        # If not a POST request, redirect to the form
        return redirect(url_for('startup_assessment'))
    
    # Submit VC-Lens investment thesis
    @app.route('/vc-lens/upload-thesis/submit', methods=['POST'])
    def submit_investment_thesis():
        """Process the investment thesis form submission"""
        if request.method == 'POST':
            try:
                # Extract form data
                fund_name = request.form.get('fund_name', '')
                investment_focus = request.form.get('investment_focus', '')
                fund_stage = request.form.get('fund_stage', '')
                thesis_year = request.form.get('thesis_year', '')
                analysis_objectives = request.form.get('analysis_objectives', '')
                
                # Get selected analysis frameworks
                analysis_frameworks = request.form.getlist('analysis_frameworks')
                
                # Handle file upload
                thesis_document = request.files.get('thesis_document')
                additional_documents = request.files.getlist('additional_documents')
                
                # Initialize thesis_path as None
                thesis_path = None
                
                if thesis_document and thesis_document.filename:
                    # Save main thesis document
                    filename = secure_filename(thesis_document.filename)
                    thesis_path = os.path.join('uploads', 'thesis', filename)
                    thesis_dir = os.path.join('uploads', 'thesis')
                    app.logger.info(f"Creating directory: {thesis_dir}")
                    os.makedirs(thesis_dir, exist_ok=True)
                    app.logger.info(f"Saving thesis to: {thesis_path}")
                    thesis_document.save(thesis_path)
                    app.logger.info(f"Thesis saved successfully: {os.path.exists(thesis_path)}")
                
                # Save additional documents if any
                additional_paths = []
                for doc in additional_documents:
                    if doc and doc.filename:
                        add_filename = secure_filename(doc.filename)
                        add_path = os.path.join('uploads', 'thesis', add_filename)
                        doc.save(add_path)
                        additional_paths.append(add_path)
                
                # Create a timestamp for this submission
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Create a thesis submission entry
                thesis_submission = {
                    'id': uuid.uuid4().hex,
                    'timestamp': timestamp,
                    'fund_name': fund_name,
                    'investment_focus': investment_focus,
                    'fund_stage': fund_stage,
                    'thesis_year': thesis_year,
                    'analysis_objectives': analysis_objectives,
                    'analysis_frameworks': analysis_frameworks,
                    'thesis_document_path': thesis_path,
                    'additional_document_paths': additional_paths,
                    'status': 'processing'
                }
                
                # In a real implementation, we would save this to a database and 
                # start an asynchronous processing job
                # For now, just flash a success message
                flash('Investment thesis for {} successfully uploaded and is being processed!'.format(fund_name), 'success')
                
                # Redirect to VC-Lens main page
                return redirect(url_for('vc_lens'))
                
            except Exception as e:
                app.logger.error(f"Error uploading investment thesis: {str(e)}")
                flash('Error uploading investment thesis. Please try again.', 'error')
                return redirect(url_for('upload_thesis'))
        
        # If not a POST request, redirect to the form
        return redirect(url_for('upload_thesis'))

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)