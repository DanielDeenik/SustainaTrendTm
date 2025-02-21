import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List
import uvicorn
import logging
import sys
from models import SustainabilityMetrics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sustainability Intelligence API")

# Configure CORS with more specific settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for development
sustainability_data: List[SustainabilityMetrics] = []

@app.get("/")
async def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to Sustainability Intelligence API"}

@app.get("/api/sustainability/{company_id}")
async def get_sustainability_metrics(company_id: str):
    logger.info(f"Fetching metrics for company_id: {company_id}")
    metrics = [m for m in sustainability_data if m.company_id == company_id]
    if not metrics:
        logger.warning(f"No metrics found for company_id: {company_id}")
        raise HTTPException(status_code=404, detail="Metrics not found")
    return metrics

@app.post("/api/sustainability")
async def create_sustainability_metrics(metrics: SustainabilityMetrics):
    logger.info("Creating new sustainability metrics")
    try:
        metrics.id = str(uuid.uuid4())
        metrics.last_updated = datetime.utcnow()
        sustainability_data.append(metrics)
        logger.info(f"Successfully created metrics with id: {metrics.id}")
        return metrics
    except Exception as e:
        logger.error(f"Error creating metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/sustainability/{metrics_id}")
async def update_sustainability_metrics(metrics_id: uuid.UUID, updated_metrics: SustainabilityMetrics):
    for i, metrics in enumerate(sustainability_data):
        if metrics.id == metrics_id:
            updated_metrics.id = metrics_id
            updated_metrics.last_updated = datetime.utcnow()
            sustainability_data[i] = updated_metrics
            return updated_metrics
    raise HTTPException(status_code=404, detail="Metrics not found")

if __name__ == "__main__":
    try:
        logger.info("Starting FastAPI server...")
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        sys.exit(1)