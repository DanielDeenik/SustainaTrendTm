import multiprocessing

# Worker Settings
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "eventlet"
threads = 4

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

# Server Settings
bind = "0.0.0.0:5000"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

# Worker Tuning
worker_connections = 1000

# WebSocket Configuration
websocket_ping_interval = 25
websocket_ping_timeout = 120

# Process Naming
proc_name = "sustainability_dashboard"

# Server Mechanics
graceful_timeout = 120
