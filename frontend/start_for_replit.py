"""
Start script for Replit environment to ensure proper binding 
for the Sustainability Intelligence Platform.

This script ensures the Flask application correctly binds to the 
host and port expected by Replit's proxying system.
"""

import os
import sys
import logging
import socket
import time
from app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/replit_startup.log")
    ]
)

logger = logging.getLogger("replit_startup")

def is_port_in_use(port):
    """Check if port is in use to avoid binding conflicts"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('0.0.0.0', port)) == 0

def kill_process_on_port(port):
    """Attempt to kill any process currently using the port"""
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        logger.info(f"Killing process {proc.pid} ({proc.name()}) using port {port}")
                        proc.kill()
                        time.sleep(0.5)  # Give it time to die
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except ImportError:
        # If psutil isn't available, try using lsof and kill
        try:
            import subprocess
            result = subprocess.run(['lsof', '-i', f':{port}'], stdout=subprocess.PIPE)
            if result.stdout:
                lines = result.stdout.decode('utf-8').strip().split('\n')
                if len(lines) > 1:  # Header + at least one process
                    pid = lines[1].split()[1]
                    logger.info(f"Killing process {pid} using port {port}")
                    subprocess.run(['kill', '-9', pid])
                    time.sleep(0.5)  # Give it time to die
                    return True
        except (subprocess.SubprocessError, IndexError, FileNotFoundError):
            pass
    return False

def main():
    """Main entry point function optimized for Replit"""
    # Create log directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    logger.info("Starting SustainaTrend Intelligence Platform for Replit")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Python version: {sys.version}")
    
    # Set Replit-specific environment variables 
    # to ensure proper connectivity
    os.environ['REPLIT_ENVIRONMENT'] = 'true'
    
    # For Replit, we need to ensure we're binding to the correct port
    # Replit expects us to use port 3000, 5000, 8080, or env PORT variable
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'  # Always bind to all interfaces in Replit
    os.environ['HOST'] = host
    os.environ['PORT'] = str(port)
    
    # Check if the port is already in use and try to free it
    if is_port_in_use(port):
        logger.warning(f"Port {port} is already in use. Attempting to free it...")
        if kill_process_on_port(port):
            logger.info(f"Successfully freed port {port}")
        else:
            logger.warning(f"Could not free port {port}. Continuing anyway...")
            # Try to choose a different port if available
            for alt_port in [3000, 8080]:
                if alt_port != port and not is_port_in_use(alt_port):
                    logger.info(f"Using alternative port {alt_port}")
                    port = alt_port
                    os.environ['PORT'] = str(port)
                    break
    
    logger.info(f"Replit config: Setting up server at {host}:{port}")
    
    # Add key environment variables if missing
    if 'FLASK_ENV' not in os.environ:
        os.environ['FLASK_ENV'] = 'development'
    
    # Force debug mode for better visibility in development
    os.environ['DEBUG'] = 'true'
    
    # Set environment variables for Flask app
    os.environ['SERVER_THREADS'] = '4'  # Increase server threads for better performance
    
    # Create Flask application with Replit-specific config
    app = create_app()
    
    # For compatibility with Replit's proxy
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )
    logger.info("Added ProxyFix middleware for Replit compatibility")
    
    # Use the configured host and port
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    # Log the registered routes and server configuration
    logger.info(f"Registered routes: {len(list(app.url_map.iter_rules()))}")
    
    # List the first 10 routes for debugging
    route_list = list(app.url_map.iter_rules())
    for i, rule in enumerate(route_list[:10]):
        logger.info(f"Route {i+1}: {rule.endpoint} - {rule}")
    
    logger.info(f"Starting Flask server on {host}:{port} with debug={debug}")
    
    # Add a simple logging route for diagnostics
    @app.route('/debug/status')
    def debug_status():
        """Simple status endpoint for debugging Replit proxy issues"""
        return {
            'status': 'ok',
            'environment': 'replit',
            'port': port,
            'host': host,
            'timestamp': time.time(),
            'routes': len(list(app.url_map.iter_rules()))
        }
    
    # Run the application with the specified host and port
    # This will make the app accessible to Replit's proxying system
    app.run(host=host, port=port, debug=debug, threaded=True)

if __name__ == '__main__':
    main()