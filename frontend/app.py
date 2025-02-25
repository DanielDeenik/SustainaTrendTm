from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_socketio import SocketIO
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime
import os
import logging
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask
server = Flask(__name__)

# Initialize Dash
app = Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    url_base_pathname='/'
)

# Redis Cache Configuration
cache = Cache(server, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    'CACHE_DEFAULT_TIMEOUT': 300
})

# Database configuration
server.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(server)

# Initialize SocketIO
socketio = SocketIO(server, async_mode='eventlet', message_queue=os.getenv('REDIS_URL'))

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

# Navigation bar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Dashboard", href="/")),
        dbc.NavItem(dbc.NavLink("AI Insights", href="/ai-insights")),
        dbc.NavItem(dbc.NavLink("Analytics", href="/analytics")),
    ],
    brand="Sustainability Intelligence Platform",
    brand_href="/",
    color="primary",
    dark=True,
    className="mb-4"
)

# Dash Layout
app.layout = html.Div([
    navbar,
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Sustainability Metrics Dashboard", className="text-center mb-4"), width=12)
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='metrics-chart'),
                dcc.Interval(id='interval-component', interval=30000)
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(id='metrics-cards', className="mt-4")
            ], width=12)
        ])
    ], fluid=True)
])

@server.route('/api/metrics')
@cache.cached(timeout=30)
def get_metrics():
    try:
        metrics = Metric.query.order_by(Metric.timestamp.desc()).all()
        return jsonify([metric.to_dict() for metric in metrics])
    except Exception as e:
        logger.error(f"Error fetching metrics: {str(e)}")
        return jsonify({'error': 'Failed to fetch metrics'}), 500

@server.route('/health')
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

# Dash Callbacks
@app.callback(
    Output('metrics-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_metrics_chart(_):
    try:
        metrics = Metric.query.order_by(Metric.timestamp.desc()).all()
        df = pd.DataFrame([metric.to_dict() for metric in metrics])

        if df.empty:
            return {}

        fig = px.line(
            df,
            x='timestamp',
            y='value',
            color='category',
            title='Sustainability Metrics Over Time'
        )

        fig.update_layout(
            template='plotly_dark',
            xaxis_title='Time',
            yaxis_title='Value',
            hovermode='x unified',
            legend_title='Category',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )

        return fig
    except Exception as e:
        logger.error(f"Error updating metrics chart: {str(e)}")
        return {}

@app.callback(
    Output('metrics-cards', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_metrics_cards(_):
    try:
        metrics = Metric.query.order_by(Metric.timestamp.desc()).all()
        cards = []
        for metric in metrics:
            card = dbc.Card([
                dbc.CardHeader(metric.name),
                dbc.CardBody([
                    html.H4(f"{metric.value} {metric.unit}", className="card-title"),
                    html.P(f"Category: {metric.category}", className="card-text"),
                    html.P(f"Last updated: {metric.timestamp.strftime('%Y-%m-%d %H:%M:%S')}", 
                          className="card-text text-muted")
                ])
            ], className="mb-3")
            cards.append(card)
        return cards
    except Exception as e:
        logger.error(f"Error updating metrics cards: {str(e)}")
        return []

if __name__ == '__main__':
    with server.app_context():
        db.create_all()
    socketio.run(server, host='0.0.0.0', port=5000, debug=True)