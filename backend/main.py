import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from typing import Dict, Any
import time

from backend.database import init_db, verify_db_connection
from backend.middleware.logging import RequestLoggingMiddleware
from backend.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
    not_found_exception_handler
)
from backend.routes.metrics import router as metrics_router
from backend.utils.logger import logger
from pydantic import ValidationError

# Initialize FastAPI app
app = FastAPI(
    title="Sustainability Intelligence API",
    description="API for sustainability metrics and reporting",
    version="1.0.0"
)

# Security settings
security = HTTPBearer()
allowed_hosts = os.getenv("ALLOWED_HOSTS", "*").split(",")
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")

# Add middleware in correct order
app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

# Add exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(404, not_found_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Initialize database with retries
MAX_RETRIES = 5
RETRY_DELAY = 2  # seconds

for attempt in range(MAX_RETRIES):
    try:
        init_db()
        logger.info("Database initialized successfully")
        break
    except Exception as e:
        if attempt < MAX_RETRIES - 1:
            logger.warning(f"Database initialization attempt {attempt + 1} failed: {str(e)}")
            time.sleep(RETRY_DELAY)
        else:
            logger.error(f"Database initialization failed after {MAX_RETRIES} attempts: {str(e)}")
            raise

# Include routers with explicit prefix and tags
app.include_router(
    metrics_router,
    prefix="/api",
    tags=["metrics"]
)

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Enhanced health check endpoint for cloud monitoring
    """
    health_status = {
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": time.time(),
    }

    # Check database connectivity
    try:
        db_status = verify_db_connection()
        health_status["database"] = {
            "status": "connected" if db_status else "disconnected",
            "message": "Database connection verified" if db_status else "Database connection failed"
        }
    except Exception as e:
        health_status["database"] = {
            "status": "error",
            "message": str(e)
        }
        health_status["status"] = "degraded"

    return health_status

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    workers = int(os.getenv("WEB_CONCURRENCY", 1))

    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        workers=workers,
        proxy_headers=True,
        forwarded_allow_ips="*",
        log_config="backend/logging.conf"
    )