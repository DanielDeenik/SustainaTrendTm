from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from typing import Union, Dict, Any
from backend.utils.logger import logger

async def handle_error(request: Request, exc: Exception) -> JSONResponse:
    """
    Unified error handler that provides consistent error responses
    """
    request_id = getattr(request.state, "request_id", None)

    if isinstance(exc, HTTPException):
        status_code = exc.status_code
        detail = exc.detail
    elif isinstance(exc, ValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        detail = exc.errors()
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        detail = "An unexpected error occurred"

    error_response = {
        "status_code": status_code,
        "detail": detail,
        "type": "validation_error" if isinstance(exc, ValidationError) else "server_error",
        "request_id": request_id
    }

    # Log the error with appropriate severity
    if status_code >= 500:
        logger.error(
            f"Server error occurred: {str(exc)}",
            extra={"error_response": error_response},
            exc_info=True
        )
    else:
        logger.warning(
            f"Client error occurred: {str(exc)}",
            extra={"error_response": error_response}
        )

    return JSONResponse(
        status_code=status_code,
        content=error_response
    )