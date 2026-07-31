"""
Logging configuration for the Review Analyzer application.
"""

import logging
import logging.config
from pathlib import Path
from typing import Dict, Any

from app.config.settings import LOG_LEVEL, LOG_FILE

def setup_logging() -> None:
    """
    Configure logging for the application.
    """
    # Create log directory if it doesn't exist
    log_path = Path(LOG_FILE)
    log_path.parent.mkdir(exist_ok=True)
    
    # Configure logging
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
            }
        },
        "handlers": {
            "default": {
                "level": LOG_LEVEL,
                "formatter": "standard",
                "class": "logging.StreamHandler",
            },
            "file": {
                "level": LOG_LEVEL,
                "formatter": "detailed",
                "class": "logging.FileHandler",
                "filename": str(log_path),
                "mode": "a",
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["default", "file"],
                "level": LOG_LEVEL,
                "propagate": False
            }
        }
    }
    
    logging.config.dictConfig(logging_config)