import logging
import sys
from logging.config import dictConfig


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "trace_id": {
            "()": "app.core.trace.TraceIdFilter",
        },
    },
    "formatters": {
        "default": {
            "format": (
                "[%(asctime)s] "
                "[trace_id=%(trace_id)s] "
                "[%(levelname)s] "
                "%(name)s: "
                "%(message)s"
            )
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "filters": ["trace_id"],
            "formatter": "default",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
    "loggers": {
        "uvicorn": {"level": "INFO"},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"level": "INFO"},
    },
}


def setup_logging():
    dictConfig(LOGGING_CONFIG)
