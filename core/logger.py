"""Logging configuration for AgentFlow AI.

Integrates loguru with standard Python logging to capture all application,
server, and library logs in a single unified format.
"""

import logging
import sys
from loguru import logger
from config.settings import settings


class InterceptHandler(logging.Handler):
    """Logs from standard logging to loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        # Find caller from where originated the logged message
        frame = logging.currentframe()
        depth = 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging() -> None:
    """Configure Loguru to redirect to standard logging, letting Rich handle the output."""
    # Remove default loguru handler
    logger.remove()

    # Call the Rich logging configuration setup
    from logging_config import setup_rich_logging
    setup_rich_logging()

    # Route Loguru records to the standard library root logger
    class PropagateHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            try:
                level = logging.getLevelName(record.levelname)
            except Exception:
                level = record.levelno
            logging.getLogger(record.name).log(level, record.getMessage())

    # Add PropagateHandler to loguru
    logger.add(PropagateHandler(), level="DEBUG")

    # Re-route standard loggers (like uvicorn and fastapi) to propagate up to root
    # so they print through RichHandler and write to the log file.
    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"):
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = []
        logging_logger.propagate = True
