from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uuid
from backend.utils.logger import logger
from typing import Optional, Callable
from starlette.types import ASGIApp

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable):
        request_id = str(uuid.uuid4())
        start_time = time.time()

        # Add request_id to request state
        request.state.request_id = request_id

        # Extract useful request information
        request_info = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client_host": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "referer": request.headers.get("referer"),
        }

        # Log request details
        logger.info(
            "Incoming request",
            extra={
                "extra_data": request_info
            }
        )

        try:
            # Process the request
            response = await call_next(request)
            process_time = time.time() - start_time

            # Log response details
            response_info = {
                **request_info,
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 2)
            }

            log_level = "error" if response.status_code >= 500 else "warning" if response.status_code >= 400 else "info"
            getattr(logger, log_level)(
                "Request completed",
                extra={
                    "extra_data": response_info
                }
            )

            # Add request ID and timing headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            return response

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                "Request failed",
                extra={
                    "extra_data": {
                        **request_info,
                        "error": str(e),
                        "process_time_ms": round(process_time * 1000, 2)
                    }
                },
                exc_info=True
            )
            raise