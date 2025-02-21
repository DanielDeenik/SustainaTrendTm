import os
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import sys
from typing import List, Optional
from sqlalchemy.orm import Session
from pydantic import ValidationError

from models import MetricModel, MetricCreate, Metric
from database import get_db, init_db
from middleware.logging import RequestLoggingMiddleware
from middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)
from utils.logger import logger

# Initialize FastAPI app
app = FastAPI(
    title="Sustainability Intelligence API",
    description="API for sustainability metrics and reporting",
    version="1.0.0"
)

# Add middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://0.0.0.0:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Initialize database tables
try:
    init_db()
    logger.info("Database tables initialized successfully")
except Exception as e:
    logger.error(
        "Failed to initialize database",
        extra={"error": str(e)},
        exc_info=True
    )
    raise

@app.get("/")
async def read_root(request: Request):
    logger.info(
        "Health check request",
        extra={
            "extra_data": {
                "request_id": request.state.request_id
            }
        }
    )
    return {
        "message": "Welcome to Sustainability Intelligence API",
        "status": "healthy",
        "request_id": request.state.request_id,
        "version": "1.0.0"
    }

@app.get("/api/metrics", response_model=List[Metric])
async def get_metrics(
    request: Request,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        logger.info(
            "Fetching metrics",
            extra={
                "extra_data": {
                    "request_id": request.state.request_id,
                    "category": category
                }
            }
        )

        query = db.query(MetricModel)
        if category:
            if category not in {'emissions', 'water', 'energy', 'waste', 'social', 'governance'}:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid category: {category}"
                )
            query = query.filter(MetricModel.category == category)

        metrics = query.order_by(MetricModel.timestamp.desc()).all()

        logger.info(
            "Metrics fetched successfully",
            extra={
                "extra_data": {
                    "request_id": request.state.request_id,
                    "count": len(metrics)
                }
            }
        )
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error fetching metrics",
            extra={
                "extra_data": {
                    "request_id": request.state.request_id,
                    "error": str(e)
                }
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching metrics"
        )

@app.post("/api/metrics", response_model=Metric)
async def create_metric(
    request: Request,
    metric: MetricCreate,
    db: Session = Depends(get_db)
):
    try:
        logger.info(
            "Creating new metric",
            extra={
                "extra_data": {
                    "request_id": request.state.request_id,
                    "metric_data": metric.dict(exclude_unset=True)
                }
            }
        )

        db_metric = MetricModel(**metric.dict())
        db.add(db_metric)
        db.commit()
        db.refresh(db_metric)

        logger.info(
            "Metric created successfully",
            extra={
                "extra_data": {
                    "request_id": request.state.request_id,
                    "metric_id": db_metric.id
                }
            }
        )
        return db_metric
    except ValidationError as e:
        # Let the validation_exception_handler handle this
        raise
    except Exception as e:
        logger.error(
            "Error creating metric",
            extra={
                "extra_data": {
                    "request_id": request.state.request_id,
                    "error": str(e)
                }
            },
            exc_info=True
        )
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error while creating metric"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)