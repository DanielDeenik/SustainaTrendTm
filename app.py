from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_socketio import SocketIO
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Redis Cache Configuration
cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    'CACHE_DEFAULT_TIMEOUT': 300
})

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize SocketIO
socketio = SocketIO(app, async_mode='eventlet', message_queue=os.getenv('REDIS_URL'))

# Metric model
class Metric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat()
        }

@app.route('/')
@cache.cached(timeout=60)  # Cache the dashboard for 60 seconds
def dashboard():
    try:
        metrics = Metric.query.order_by(Metric.timestamp.desc()).all()
        metrics_by_category = {}
        for metric in metrics:
            if metric.category not in metrics_by_category:
                metrics_by_category[metric.category] = []
            metrics_by_category[metric.category].append(metric)

        return render_template(
            'dashboard.html',
            metrics_by_category=metrics_by_category,
            page_title='Sustainability Dashboard',
            now=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        return render_template('error.html', error="Failed to load dashboard data"), 500

@app.route('/api/metrics')
@cache.cached(timeout=30)  # Cache API responses for 30 seconds
def get_metrics():
    try:
        metrics = Metric.query.order_by(Metric.timestamp.desc()).all()
        return jsonify([metric.to_dict() for metric in metrics])
    except Exception as e:
        logger.error(f"Error fetching metrics: {str(e)}")
        return jsonify({'error': 'Failed to fetch metrics'}), 500

@app.route('/health')
@cache.cached(timeout=10)  # Cache health check for 10 seconds
def health():
    try:
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

def init_db():
    """Initialize database and create sample data"""
    try:
        logger.info("Creating database tables...")
        db.create_all()

        # Add sample data if no metrics exist
        if not Metric.query.first():
            sample_metrics = [
                Metric(name='Carbon Footprint', category='emissions', value=156.7, unit='kg CO2e'),
                Metric(name='Water Usage', category='water', value=2450.5, unit='gallons'),
                Metric(name='Energy Consumption', category='energy', value=4500, unit='kWh')
            ]
            db.session.bulk_save_objects(sample_metrics)
            db.session.commit()
            logger.info("Added sample metrics")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

if __name__ == '__main__':
    try:
        with app.app_context():
            init_db()
        # Use SocketIO instead of app.run for WebSocket support
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise