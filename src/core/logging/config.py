import structlog
from src.core.config import settings

from src.core.logging.constants import LogRenderer
from src.core.logging.utils import redact_sensitive_data, log_timestamper

LOG_LEVEL = settings.logging.level
LOG_RENDERER = settings.logging.renderer
ENABLE_COLORED_CONSOLE_LOGS = settings.logging.enable_colored_console_logs
ENABLE_RICH_TRACEBACK_FORMATTER = settings.logging.enable_rich_traceback_formatter

if LOG_RENDERER == LogRenderer.JSON:
    renderer = structlog.processors.JSONRenderer()
else:
    renderer = structlog.dev.ConsoleRenderer(
        colors=ENABLE_COLORED_CONSOLE_LOGS,
        exception_formatter=(
            structlog.dev.RichTracebackFormatter()
            if ENABLE_RICH_TRACEBACK_FORMATTER
            else structlog.dev.plain_traceback
        ),
    )


def configure_structlog():

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            log_timestamper,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.ExceptionRenderer(),
            structlog.processors.UnicodeDecoder(),
            redact_sensitive_data,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Standard logging config for uvicorn
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "structlog": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": renderer,
            "foreign_pre_chain": [
                structlog.contextvars.merge_contextvars,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                log_timestamper,
                structlog.processors.StackInfoRenderer(),
                structlog.processors.ExceptionRenderer(),
                structlog.processors.UnicodeDecoder(),
                redact_sensitive_data,
            ],
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "structlog",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL.value,
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["console"],
            "level": LOG_LEVEL.value,
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console"],
            "level": LOG_LEVEL.value,
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["console"],
            "level": LOG_LEVEL.value,
            "propagate": False,
        },
        "fastapi": {
            "handlers": ["console"],
            "level": LOG_LEVEL.value,
            "propagate": False,
        },
    }
}