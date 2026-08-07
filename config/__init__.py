"""Configuration package initializer.

Re-exports core Settings and mapped configuration variables.
"""

from config.config import (EMBEDDING_MODEL, ENABLE_RULE_VERIFICATION,
                           ENABLE_SEMANTIC_VERIFICATION, ENV, LOG_LEVEL,
                           MAX_RETRIES, MIN_CONFIDENCE, MODEL_NAME, PORT,
                           RULE_VALIDATION_ENABLED,
                           SEMANTIC_VALIDATION_ENABLED, VECTOR_DB_PATH)
from config.settings import settings

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
