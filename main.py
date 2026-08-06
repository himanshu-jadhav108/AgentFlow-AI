"""Main entry point for the FastAPI application of AgentFlow AI."""

from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi import FastAPI
from config.settings import settings
from core.logger import setup_logging, logger

# Initialize unified loguru logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle hooks for the FastAPI application."""
    logger.info("Starting up AgentFlow AI API Service...")
    logger.info(f"Configuration: ENV={settings.APP_ENV}, PORT={settings.PORT}")
    logger.info(f"Local AI Config: LLM={settings.LLM_PROVIDER}:{settings.LLM_MODEL_NAME}")
    logger.info(f"Vector Database Path: {settings.VECTOR_DB_PATH}")
    yield
    logger.info("Shutting down AgentFlow AI API Service...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise-grade local customer support AI agent using FastAPI and LangGraph",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Check system health status and configuration details."""
    logger.debug("Health check endpoint queried")
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model_name": settings.LLM_MODEL_NAME,
        "embedding_model": settings.EMBEDDING_MODEL_NAME,
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Running web server on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.APP_ENV == "development",
    )
