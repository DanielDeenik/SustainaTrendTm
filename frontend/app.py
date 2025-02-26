from flask import Flask, render_template
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from flask_caching import Cache
import pandas as pd
import redis
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Starting Sustainability Intelligence Dashboard")

# Initialize Flask
app = Flask(__name__)

# Setup Redis Cache
cache = Cache(app, config={
    'CACHE_TYPE': 'RedisCache', 
    'CACHE_REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0')
})

# Initialize Dash with Bootstrap theme
dash_app = dash.Dash(
    __name__, 
    server=app, 
    routes_pathname_prefix='/dashboard/',
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="Sustainability Intelligence Platform"
)

# Create mock sustainability metrics data
@cache.memoize(timeout=300)
def get_sustainability_metrics():
    """Generate mock sustainability metrics data"""
    # Time periods
    dates = pd.date_range(start='2024-01-01', end='2024-06-30', freq='M')

    # Carbon emissions data (decreasing trend - good)
    emissions_data = pd.DataFrame({
        "date": dates,
        "metric": "Carbon Emissions",
        "value": [45, 42, 38, 35, 32, 30],
        "unit": "tons CO2e",
        "category": "emissions"
    })

    # Energy consumption data (decreasing trend - good)
    energy_data = pd.DataFrame({
        "date": dates,
        "metric": "Energy Consumption",
        "value": [1250, 1200, 1150, 1100, 1075, 1050],
        "unit": "MWh",
        "category": "energy"
    })

    # Water usage data (decreasing trend - good)
    water_data = pd.DataFrame({
        "date": dates,
        "metric": "Water Usage",
        "value": [350, 340, 330, 320, 310, 300],
        "unit": "kiloliters",
        "category": "water"
    })

    # Waste reduction data (increasing trend - good)
    waste_data = pd.DataFrame({
        "date": dates,
        "metric": "Waste Recycled",
        "value": [65, 68, 72, 76, 80, 82],
        "unit": "percent",
        "category": "waste"
    })

    # ESG score data (increasing trend - good)
    esg_data = pd.DataFrame({
        "date": dates,
        "metric": "ESG Score",
        "value": [72, 74, 76, 78, 80, 82],
        "unit": "score",
        "category": "social"
    })

    # Combine all dataframes
    all_data = pd.concat([emissions_data, energy_data, water_data, waste_data, esg_data])

    logger.info(f"Generated sustainability metrics with {len(all_data)} records")
    return all_data

# Dashboard layout with Bootstrap components
dash_app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Sustainability Intelligence Dashboard", className="text-center my-4"),
            html.P("Real-time insights powered by advanced AI analytics", className="text-center mb-5"),
        ], width=12)
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Filter Metrics"),
                dbc.CardBody([
                    html.P("Select Category:"),
                    dcc.Dropdown(
                        id="category-filter",
                        options=[
                            {'label': 'All Categories', 'value': 'all'},
                            {'label': 'Emissions', 'value': 'emissions'},
                            {'label': 'Energy', 'value': 'energy'},
                            {'label': 'Water', 'value': 'water'},
                            {'label': 'Waste', 'value': 'waste'},
                            {'label': 'Social & Governance', 'value': 'social'}
                        ],
                        value='all',
                        clearable=False
                    )
                ])
            ]),
        ], width=12, md=3),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Sustainability Metrics Over Time"),
                dbc.CardBody([
                    dcc.Graph(id="metrics-time-series")
                ])
            ]),
        ], width=12, md=9),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Carbon Emissions"),
                dbc.CardBody([
                    html.H3(id="emissions-value", className="text-center"),
                    html.P("tons CO2e", className="text-center text-muted"),
                    html.P(id="emissions-trend", className="text-center")
                ])
            ]),
        ], width=12, md=4),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Water Usage"),
                dbc.CardBody([
                    html.H3(id="water-value", className="text-center"),
                    html.P("kiloliters", className="text-center text-muted"),
                    html.P(id="water-trend", className="text-center")
                ])
            ]),
        ], width=12, md=4),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Waste Recycled"),
                dbc.CardBody([
                    html.H3(id="waste-value", className="text-center"),
                    html.P("percent", className="text-center text-muted"),
                    html.P(id="waste-trend", className="text-center")
                ])
            ]),
        ], width=12, md=4),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("AI-Powered Sustainability Insights"),
                dbc.CardBody([
                    html.P("Based on the current trends, your organization is showing positive progress in reducing its environmental footprint."),
                    html.P("Key insights:"),
                    html.Ul([
                        html.Li("Carbon emissions have reduced by 33% over the past 6 months"),
                        html.Li("Water consumption is down 14%, ahead of industry average"),
                        html.Li("Waste recycling has improved to 82%, exceeding target goals"),
                        html.Li("Energy efficiency measures have reduced consumption by 16%")
                    ]),
                    html.P("Recommended actions:"),
                    html.Ul([
                        html.Li("Continue investment in renewable energy sources"),
                        html.Li("Implement additional water conservation measures"),
                        html.Li("Expand your circular economy initiatives for further waste reduction")
                    ])
                ])
            ]),
        ], width=12),
    ]),
], fluid=True, className="p-4")

# Callback to update time series chart
@dash_app.callback(
    Output("metrics-time-series", "figure"),
    [Input("category-filter", "value")]
)
def update_time_series(category):
    df = get_sustainability_metrics()

    if category != 'all':
        df = df[df['category'] == category]

    fig = px.line(
        df, 
        x="date", 
        y="value", 
        color="metric",
        title="Sustainability Metrics Over Time",
        labels={"date": "Date", "value": "Value", "metric": "Metric"}
    )

    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=40, b=40)
    )

    return fig

# Callbacks to update metric cards
@dash_app.callback(
    [Output("emissions-value", "children"),
     Output("emissions-trend", "children"),
     Output("emissions-trend", "className")],
    [Input("category-filter", "value")]
)
def update_emissions_card(category):
    df = get_sustainability_metrics()
    emissions_df = df[df['metric'] == "Carbon Emissions"]
    latest_value = emissions_df['value'].iloc[-1]
    previous_value = emissions_df['value'].iloc[-2]
    percent_change = ((latest_value - previous_value) / previous_value) * 100

    trend_text = f"{abs(percent_change):.1f}% {'increase' if percent_change > 0 else 'decrease'} from previous month"
    trend_class = "text-center text-danger" if percent_change > 0 else "text-center text-success"

    return f"{latest_value}", trend_text, trend_class

@dash_app.callback(
    [Output("water-value", "children"),
     Output("water-trend", "children"),
     Output("water-trend", "className")],
    [Input("category-filter", "value")]
)
def update_water_card(category):
    df = get_sustainability_metrics()
    water_df = df[df['metric'] == "Water Usage"]
    latest_value = water_df['value'].iloc[-1]
    previous_value = water_df['value'].iloc[-2]
    percent_change = ((latest_value - previous_value) / previous_value) * 100

    trend_text = f"{abs(percent_change):.1f}% {'increase' if percent_change > 0 else 'decrease'} from previous month"
    trend_class = "text-center text-danger" if percent_change > 0 else "text-center text-success"

    return f"{latest_value}", trend_text, trend_class

@dash_app.callback(
    [Output("waste-value", "children"),
     Output("waste-trend", "children"),
     Output("waste-trend", "className")],
    [Input("category-filter", "value")]
)
def update_waste_card(category):
    df = get_sustainability_metrics()
    waste_df = df[df['metric'] == "Waste Recycled"]
    latest_value = waste_df['value'].iloc[-1]
    previous_value = waste_df['value'].iloc[-2]
    percent_change = ((latest_value - previous_value) / previous_value) * 100

    trend_text = f"{abs(percent_change):.1f}% {'increase' if percent_change > 0 else 'decrease'} from previous month"
    trend_class = "text-center text-success" if percent_change > 0 else "text-center text-danger"

    return f"{latest_value}%", trend_text, trend_class

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)