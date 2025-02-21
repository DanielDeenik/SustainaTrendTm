import logging
import sys
from typing import Any, Dict, Optional
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }

        # Add request_id if available
        request_id = getattr(record, "request_id", None)
        if request_id:
            log_obj["request_id"] = request_id

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # Add extra data if available
        extra_data = getattr(record, "extra_data", None)
        if extra_data:
            log_obj.update(extra_data)

        return json.dumps(log_obj)

def setup_logger(name: str = __name__, log_level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with JSON formatting
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Create console handler with JSON formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    # Remove existing handlers to prevent duplicate logs
    logger.handlers = []
    logger.addHandler(handler)

    return logger

# Create the logger instance
logger = setup_logger("sustainability_platform")

# Add custom LogRecord attributes
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance with the specified name
    """
    return logging.getLogger(name if name else "sustainability_platform")