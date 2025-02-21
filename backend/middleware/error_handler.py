from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from utils.logger import logger
from typing import Union, Dict, Any

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    error_detail = {
        "status_code": exc.status_code,
        "message": str(exc.detail),
        "request_id": getattr(request.state, "request_id", None)
    }
    
    logger.error(
        f"HTTP Exception: {exc.status_code}",
        extra={
            "extra_data": error_detail
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_detail
    )

async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    error_detail = {
        "status_code": 500,
        "message": "Internal server error",
        "request_id": getattr(request.state, "request_id", None)
    }
    
    logger.error(
        "Unhandled exception",
        extra={
            "extra_data": error_detail
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content=error_detail
    )
