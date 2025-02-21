from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from typing import Union, Dict, Any
from backend.utils.logger import logger

async def error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Unified error handler for all exceptions"""
    if isinstance(exc, HTTPException):
        status_code = exc.status_code
        message = str(exc.detail)
        error_type = "http_error"
        logger_level = logger.error
    elif isinstance(exc, ValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        message = "Validation error"
        error_type = "validation_error"
        errors = exc.errors()
        logger_level = logger.error
        
        error_response = {
            "error": {
                "message": message,
                "status": status_code,
                "errors": errors,
                "request_id": getattr(request.state, "request_id", None)
            }
        }

    elif isinstance(exc, Exception) and status_code == status.HTTP_404_NOT_FOUND:
        status_code = status.HTTP_404_NOT_FOUND
        message = "The requested resource could not be found"
        error_type = "not_found"
        logger_level = logger.warning
        error_response = {
            "error": {
                "message": message,
                "status": status_code,
                "path": request.url.path,
                "request_id": getattr(request.state, "request_id", None)
            }
        }

    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        message = "Internal server error"
        error_type = "server_error"
        logger_level = logger.error
        error_response = {
            "error": {
                "message": message,
                "status": status_code,
                "request_id": getattr(request.state, "request_id", None)
            }
        }

    logger_level(
        f"{error_type.replace('_',' ').title()}: {message}",
        extra={
            "extra_data": {
                **error_response["error"],
                "error_type": exc.__class__.__name__,
                "error_message": str(exc)
            }
        },
        exc_info=isinstance(exc, Exception) and status_code == 500
    )


    return JSONResponse(
        status_code=status_code,
        content=error_response
    )