"""Configuration management for AgentFlow AI using Pydantic Settings.

Provides loaded, validated environment variables with type safety.
"""

from typing import Any, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General Settings
    APP_NAME: str = Field(
        default="AgentFlow AI Support Agent", description="The name of the application."
    )
    APP_ENV: str = Field(
        default="development",
        description="The run environment (e.g., development, production).",
    )
    HOST: str = Field(
        default="0.0.0.0", description="IP address to bind the API server to."
    )
    PORT: int = Field(default=8000, description="Port to bind the API server to.")
    LOG_LEVEL: str = Field(
        default="INFO", description="Log level for application logging."
    )

    # Model Settings
    LLM_PROVIDER: Literal["ollama", "huggingface", "llama-cpp"] = Field(
        default="ollama",
        description="The local LLM provider to use.",
    )
    LLM_MODEL_NAME: str = Field(
        default="phi3",
        description="Model identifier/name to use with the selected provider.",
    )
    LLM_API_URL: str = Field(
        default="http://localhost:11434",
        description="URL for API-based local LLM providers (like Ollama).",
    )

    # Embedding Settings
    EMBEDDING_MODEL_NAME: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Name of the sentence-transformers model to download and run locally.",
    )

    # Storage Paths
    VECTOR_DB_PATH: str = Field(
        default="data/vectorstore",
        description="Path to save/load FAISS vector indexes.",
    )
    DOCUMENTS_DIR: str = Field(
        default="data/documents",
        description="Directory containing source text documents to index.",
    )

    # Hybrid Verification Options
    ENABLE_RULE_VERIFICATION: bool = Field(
        default=True, description="Enable rule-based deterministic validation checks."
    )
    ENABLE_SEMANTIC_VERIFICATION: bool = Field(
        default=True, description="Enable LLM semantic validation check."
    )
    RULE_VALIDATION_ENABLED: bool = Field(
        default=True, description="Alias toggle for rule validation checks."
    )
    SEMANTIC_VALIDATION_ENABLED: bool = Field(
        default=True, description="Alias toggle for semantic validation checks."
    )
    MIN_CONFIDENCE: float = Field(
        default=0.5,
        description="Minimum confidence threshold required to pass validation.",
    )
    MAX_RETRIES: int = Field(
        default=3,
        description="Maximum execution retries allowed for verification loop.",
    )

    # Caching Options
    ENABLE_CACHE: bool = Field(
        default=True, description="Enable in-memory query answer caching."
    )
    CACHE_TTL_SECONDS: int = Field(
        default=300, description="Time-to-Live in seconds for cached queries."
    )

    # Rate Limiting & Security Options
    RATE_LIMIT_REQUESTS: int = Field(
        default=100, description="Max requests permitted in the sliding window."
    )
    RATE_LIMIT_WINDOW_SECONDS: int = Field(
        default=60, description="Sliding window duration in seconds."
    )
    MAX_PAYLOAD_SIZE_BYTES: int = Field(
        default=1024 * 1024, description="Maximum payload size in bytes (default 1MB)."
    )

    def __init__(self, **values: Any) -> None:
        import importlib
        import os

        env = values.get("APP_ENV", os.getenv("APP_ENV", "development")).lower()
        overrides = {}
        try:
            profile_module = importlib.import_module(f"config.{env}")
            overrides = getattr(profile_module, "OVERRIDES", {})
        except Exception:
            pass
        merged = {**overrides, **values}
        super().__init__(**merged)


# Instantiate settings for global project import
settings = Settings()
