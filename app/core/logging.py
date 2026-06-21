import logging
import sys
import json
from datetime import datetime, timezone
from typing import Any, Dict

class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "filename": record.filename,
            "line": record.lineno,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Allow extra fields to be passed dynamically
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
            
        return json.dumps(log_data)

def setup_logging(env: str = "development") -> None:
    root_logger = logging.getLogger()
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    handler = logging.StreamHandler(sys.stdout)
    if env == "production":
        handler.setFormatter(StructuredFormatter())
        root_logger.setLevel(logging.INFO)
    else:
        # Human-readable format for development
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] - %(message)s"
        )
        handler.setFormatter(formatter)
        root_logger.setLevel(logging.DEBUG)
        
    root_logger.addHandler(handler)

logger = logging.getLogger("rag-app")
