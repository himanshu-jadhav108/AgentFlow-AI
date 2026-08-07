"""Configuration package initializer.

Re-exports core Settings and mapped configuration variables.
"""

from config.settings import settings
from config.config import (
    ENV,
    PORT,
    MODEL_NAME,
    EMBEDDING_MODEL,
    VECTOR_DB_PATH,
    LOG_LEVEL,
)

__all__ = [
    "settings",
    "ENV",
    "PORT",
    "MODEL_NAME",
    "EMBEDDING_MODEL",
    "VECTOR_DB_PATH",
    "LOG_LEVEL",
]
