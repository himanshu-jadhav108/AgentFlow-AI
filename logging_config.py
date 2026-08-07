"""Logging configuration for Rich console and file logging."""

import logging
import sys
from rich.logging import RichHandler
from config.settings import settings


def setup_rich_logging() -> None:
    """Configures standard logging using Rich console log handler and rotating file logger."""
    log_level = settings.LOG_LEVEL.upper()

    # Define message formats
    file_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Keep root at debug, handlers will restrict

    # Remove any existing handlers
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    # 1. Rich Console Handler
    console_handler = RichHandler(
        level=log_level,
        rich_tracebacks=True,
        markup=True,
        show_path=False,
    )
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger.addHandler(console_handler)

    # 2. File Handler
    import os
    os.makedirs("logs", exist_ok=True)
    file_handler = logging.FileHandler("logs/agentflow.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(file_format))
    root_logger.addHandler(file_handler)

    # Silence noise from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("huggingface_hub").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    logging.info("Rich and File logging initialized successfully.")
