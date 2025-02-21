import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_db
from backend.middleware.logging import RequestLoggingMiddleware
from backend.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)
from backend.routes import metrics
from backend.utils.logger import logger

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
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Initialize database
try:
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Database initialization failed: {str(e)}")
    raise

# Include routers
app.include_router(metrics.router, prefix="/api")

@app.get("/")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)