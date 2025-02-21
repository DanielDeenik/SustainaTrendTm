from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from typing import Union, Dict, Any
from backend.utils.logger import logger

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with proper error formatting"""
    error_detail = {
        "status_code": exc.status_code,
        "detail": str(exc.detail),
        "type": "http_error",
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

async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle validation errors with detailed feedback"""
    error_detail = {
        "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "detail": "Validation error",
        "type": "validation_error",
        "errors": [{"field": ".".join(map(str, e["loc"])), "message": e["msg"]} for e in exc.errors()],
        "request_id": getattr(request.state, "request_id", None)
    }

    logger.error(
        "Validation error",
        extra={
            "extra_data": error_detail
        }
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_detail
    )

async def not_found_exception_handler(request: Request) -> JSONResponse:
    """Handle 404 Not Found errors with a user-friendly message"""
    error_detail = {
        "status_code": status.HTTP_404_NOT_FOUND,
        "detail": "The requested resource could not be found",
        "type": "not_found",
        "path": request.url.path,
        "request_id": getattr(request.state, "request_id", None)
    }

    logger.warning(
        f"Resource not found: {request.url.path}",
        extra={
            "extra_data": error_detail
        }
    )

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=error_detail
    )

async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle any unhandled exceptions with a safe error response"""
    error_detail = {
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "detail": "An unexpected error occurred",
        "type": "server_error",
        "request_id": getattr(request.state, "request_id", None)
    }

    logger.error(
        "Unhandled exception",
        extra={
            "extra_data": {
                **error_detail,
                "error_type": exc.__class__.__name__,
                "error_message": str(exc)
            }
        },
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_detail
    )