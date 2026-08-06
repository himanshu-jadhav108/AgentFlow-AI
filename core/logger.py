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
    """Configure Loguru to log to stdout and file, intercepting standard library logs."""
    # Remove default loguru handler
    logger.remove()

    # Define color-coded format for terminal
    terminal_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # Standard format for text file logs (no color tags)
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} - "
        "{message}"
    )

    # Add console logging
    logger.add(
        sys.stdout,
        format=terminal_format,
        level=settings.LOG_LEVEL.upper(),
        colorize=True,
    )

    # Add file logging
    logger.add(
        "logs/agentflow.log",
        format=file_format,
        level="DEBUG",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
    )

    # Intercept standard library logging configuration
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Re-route uvicorn loggers to use our InterceptHandler
    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"):
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False
