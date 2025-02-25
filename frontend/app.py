from flask import Flask, render_template
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from flask_caching import Cache
import pandas as pd
import redis

app = Flask(__name__)

# Setup Redis Cache
cache = Cache(app, config={'CACHE_TYPE': 'RedisCache', 'CACHE_REDIS_URL': 'redis://localhost:6379/0'})

# Initialize Dash
dash_app = dash.Dash(__name__, server=app, routes_pathname_prefix='/dashboard/')

# Mock AI data for trends
def get_ai_trends():
    return pd.DataFrame({
        "Time": ["2024-01", "2024-02", "2024-03"],
        "Trend Score": [75, 85, 90]
    })

dash_app.layout = html.Div(children=[
    html.H1("AI-Powered Analytics Dashboard"),
    dcc.Graph(id="trend-chart",
              figure={
                  "data": [
                      {"x": get_ai_trends()["Time"], "y": get_ai_trends()["Trend Score"], "type": "line", "name": "AI Trend"}
                  ],
                  "layout": {"title": "AI Trends Over Time"}
              })
])

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)