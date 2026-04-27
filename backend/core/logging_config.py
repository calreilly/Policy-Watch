import logging
import logging.config
from pythonjsonlogger import jsonlogger
from datetime import datetime

LOG_FORMAT = "%(timestamp)s %(level)s %(name)s %(message)s"

def setup_logging():
    """Configure JSON structured logging with rotating file handlers."""
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": jsonlogger.JsonFormatter,
                "format": LOG_FORMAT
            },
            "standard": {
                "format": "% (asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "json",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "json",
                "filename": "logs/app.log",
                "maxBytes": 10_485_760,
                "backupCount": 5
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "json",
                "filename": "logs/error.log",
                "maxBytes": 10_485_760,
                "backupCount": 5
            }
        },
        "loggers": {
            "": {
                "handlers": ["console", "file", "error_file"],
                "level": "DEBUG",
                "propagate": True
            },
            "backend.services": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False
            }
        }
    }
    logging.config.dictConfig(logging_config)
    logger = logging.getLogger(__name__)
    logger.info("Logging initialized", extra={"timestamp": datetime.utcnow().isoformat()})
    return logger
