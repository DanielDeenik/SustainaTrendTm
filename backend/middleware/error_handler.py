from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from ..utils.logger import logger
from typing import Union, Dict, Any
from pydantic import ValidationError

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    error_detail = {
        "status_code": exc.status_code,
        "message": str(exc.detail),
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
    error_detail = {
        "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "message": "Validation error",
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

async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    error_detail = {
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "message": "Internal server error",
        "type": "server_error",
        "request_id": getattr(request.state, "request_id", None)
    }

    logger.error(
        "Unhandled exception",
        extra={
            "extra_data": error_detail,
            "error_type": exc.__class__.__name__,
            "error_message": str(exc)
        },
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_detail
    )