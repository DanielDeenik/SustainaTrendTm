import logging
import sys
from typing import Any, Dict
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
        
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id
            
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
            
        if hasattr(record, 'extra_data'):
            log_obj.update(record.extra_data)
            
        return json.dumps(log_obj)

def setup_logger(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create console handler with JSON formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    
    # Remove existing handlers to prevent duplicate logs
    logger.handlers = []
    logger.addHandler(handler)
    
    return logger

logger = setup_logger("sustainability_platform")
