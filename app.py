from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Database configuration using environment variables
required_vars = ['DATABASE_URL', 'PGDATABASE', 'PGUSER', 'PGPASSWORD', 'PGHOST', 'PGPORT']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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
def dashboard():
    try:
        metrics = Metric.query.order_by(Metric.timestamp.desc()).all()
        # Group metrics by category
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
def get_metrics():
    try:
        metrics = Metric.query.order_by(Metric.timestamp.desc()).all()
        return jsonify([metric.to_dict() for metric in metrics])
    except Exception as e:
        logger.error(f"Error fetching metrics: {str(e)}")
        return jsonify({'error': 'Failed to fetch metrics'}), 500

@app.before_first_request
def create_tables():
    try:
        logger.info("Creating database tables if they don't exist...")
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        raise

if __name__ == '__main__':
    # Ensure the app runs on port 5000 and is accessible from outside
    app.run(host='0.0.0.0', port=5000, debug=True)