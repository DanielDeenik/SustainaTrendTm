import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging
import sys
import json
from typing import List, Optional
from sqlalchemy.orm import Session
from psycopg2.extras import Json

from models import MetricModel, MetricCreate, Metric
from database import get_db, engine, SessionLocal
import models

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sustainability Intelligence API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to Sustainability Intelligence API"}

@app.get("/api/metrics", response_model=List[Metric])
async def get_metrics(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(MetricModel)
        if category:
            query = query.filter(MetricModel.category == category)
        metrics = query.order_by(MetricModel.timestamp.desc()).all()
        return metrics
    except Exception as e:
        logger.error(f"Error fetching metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/metrics", response_model=Metric)
async def create_metric(
    metric: MetricCreate,
    db: Session = Depends(get_db)
):
    try:
        # Convert Pydantic model to dict
        metric_data = metric.dict()

        # Explicitly serialize the metadata to JSON string
        metadata_json = json.dumps(metric_data['metadata'])
        logger.info(f"Serialized metadata: {metadata_json}")

        # Create database model instance with properly adapted JSON
        db_metric = MetricModel(
            name=metric_data['name'],
            category=metric_data['category'],
            value=metric_data['value'],
            unit=metric_data['unit'],
            metadata=Json(json.loads(metadata_json))  # Use psycopg2's Json adapter
        )

        logger.info(f"Created MetricModel instance with metadata type: {type(db_metric.metadata)}")

        db.add(db_metric)
        db.commit()
        db.refresh(db_metric)

        return db_metric
    except Exception as e:
        logger.error(f"Error creating metric: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)