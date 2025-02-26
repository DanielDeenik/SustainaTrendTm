# Gunicorn configuration for Sustainability Dashboard
import multiprocessing

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
errorlog = "logs/error.log"
accesslog = "logs/access.log"
loglevel = "info"

# Process naming
proc_name = "sustainability_dashboard"

# Server hooks
def on_starting(server):
    """
    Log when the server starts.
    """
    server.log.info("Starting Sustainability Dashboard")

def on_exit(server):
    """
    Log when the server exits.
    """
    server.log.info("Shutting down Sustainability Dashboard")

# Preload app to speed up worker spawning
preload_app = True
