from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uuid
from utils.logger import logger

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Add request_id to request state
        request.state.request_id = request_id
        
        # Log request details
        logger.info(
            "Incoming request",
            extra={
                "extra_data": {
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "client_host": request.client.host if request.client else None,
                }
            }
        )
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response details
            logger.info(
                "Request completed",
                extra={
                    "extra_data": {
                        "request_id": request_id,
                        "status_code": response.status_code,
                        "process_time_ms": round(process_time * 1000, 2)
                    }
                }
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            return response
            
        except Exception as e:
            logger.error(
                "Request failed",
                extra={
                    "extra_data": {
                        "request_id": request_id,
                        "error": str(e)
                    }
                },
                exc_info=True
            )
            raise
