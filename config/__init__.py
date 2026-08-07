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
    ENABLE_RULE_VERIFICATION,
    ENABLE_SEMANTIC_VERIFICATION,
    RULE_VALIDATION_ENABLED,
    SEMANTIC_VALIDATION_ENABLED,
    MIN_CONFIDENCE,
    MAX_RETRIES,
)

__all__ = [
    "settings",
    "ENV",
    "PORT",
    "MODEL_NAME",
    "EMBEDDING_MODEL",
    "VECTOR_DB_PATH",
    "LOG_LEVEL",
    "ENABLE_RULE_VERIFICATION",
    "ENABLE_SEMANTIC_VERIFICATION",
    "RULE_VALIDATION_ENABLED",
    "SEMANTIC_VALIDATION_ENABLED",
    "MIN_CONFIDENCE",
    "MAX_RETRIES",
]
