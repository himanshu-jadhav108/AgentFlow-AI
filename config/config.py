"""Configuration mapping variables from settings."""

from config.settings import settings

# Map settings to exact requested Phase 1 configuration keys
ENV = settings.APP_ENV
PORT = settings.PORT
MODEL_NAME = settings.LLM_MODEL_NAME
EMBEDDING_MODEL = settings.EMBEDDING_MODEL_NAME
VECTOR_DB_PATH = settings.VECTOR_DB_PATH
LOG_LEVEL = settings.LOG_LEVEL
