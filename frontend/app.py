from flask import Flask, render_template
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from flask_caching import Cache
import pandas as pd
import redis
import os
import logging
import plotly.express as px
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)

# Setup Redis Cache
cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    'CACHE_DEFAULT_TIMEOUT': 300
})

# Initialize Dash with Bootstrap
dash_app = dash.Dash(
    __name__,
    server=app,
    routes_pathname_prefix='/dashboard/',
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

# Generate mock AI trend data
def get_ai_trends():
    dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
    return pd.DataFrame({
        'date': dates,
        'sustainability_score': [75, 82, 78, 85, 89, 91, 88, 92, 95, 93],
        'efficiency_score': [65, 70, 75, 72, 78, 82, 85, 83, 88, 90],
        'innovation_score': [80, 83, 85, 88, 87, 91, 93, 94, 92, 95]
    })

# Dashboard layout
dash_app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("AI-Powered Sustainability Analytics", className="text-center mb-4"), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='trends-chart',
                figure=px.line(
                    get_ai_trends(),
                    x='date',
                    y=['sustainability_score', 'efficiency_score', 'innovation_score'],
                    title='AI Trend Analysis'
                )
            )
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Key Metrics"),
                dbc.CardBody([
                    html.H4("Current Sustainability Score", className="card-title"),
                    html.H2("93", className="text-success"),
                    html.P("Trending upward by 5% this week", className="card-text")
                ])
            ], className="mb-4")
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Efficiency Metrics"),
                dbc.CardBody([
                    html.H4("Resource Efficiency", className="card-title"),
                    html.H2("90", className="text-primary"),
                    html.P("Improved by 8% from last month", className="card-text")
                ])
            ], className="mb-4")
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Innovation Index"),
                dbc.CardBody([
                    html.H4("AI Innovation Score", className="card-title"),
                    html.H2("95", className="text-info"),
                    html.P("Leading in sector by 15%", className="card-text")
                ])
            ], className="mb-4")
        ], width=4),
    ]),
    dcc.Interval(
        id='interval-component',
        interval=30000,
        n_intervals=0
    )
], fluid=True)

@app.route('/')
def home():
    """Render the home page"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)