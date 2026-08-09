"""Main entry point for the FastAPI application of AgentFlow AI."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api.exception_handlers import register_exception_handlers
from app.api.middleware import (RateLimitingMiddleware, RequestIDMiddleware,
                                SecurityHeadersMiddleware,
                                TimingLoggingMiddleware)
from app.api.routes import router as api_router
from app.graph.builder import build_graph
from app.graph.visualization import generate_graph_visualizations
from config.settings import settings
from core.logger import logger, setup_logging

# 1. Initialize log configuration
setup_logging()

# 2. Pre-compile orchestration graph
agent_graph = build_graph()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager that handles startup hooks."""
    logger.info("Initializing AgentFlow AI Production API Service...")
    logger.info(
        f"Configuration: APP_NAME='{settings.APP_NAME}', ENV='{settings.APP_ENV}'"
    )
    logger.info(
        f"In-Memory Cache status: {settings.ENABLE_CACHE} (TTL: {settings.CACHE_TTL_SECONDS}s)"
    )
    logger.info(
        f"Rate Limiter status: Limit {settings.RATE_LIMIT_REQUESTS} reqs / {settings.RATE_LIMIT_WINDOW_SECONDS}s"
    )

    # Generate graph visualizations on server startup
    logger.info("Generating state visualizations (Mermaid, ASCII, PNG)...")
    generate_graph_visualizations(agent_graph)

    # Automatic startup validation: check model caches and FAISS databases
    from app.services.index_manager import IndexManager
    from app.services.model_manager import ModelManager

    logger.info("Automatic Startup: Syncing local model caches...")
    ModelManager.download_model()

    logger.info("Automatic Startup: Pre-loading LLM weights into RAM...")
    from app.llm.model_loader import ModelLoader
    from app.llm.tokenizer import TokenizerLoader
    ModelLoader().load_model()
    TokenizerLoader().load_tokenizer()

    logger.info("Automatic Startup: Verifying local FAISS index status...")
    IndexManager.ensure_index_ready()

    yield
    logger.info("Shutting down AgentFlow AI API Service...")


# 3. Instantiate FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise-grade local customer support AI agent service with hybrid verification & caching.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 4. Register Standard Middlewares (Execution order is bottom-to-top)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(TimingLoggingMiddleware)
app.add_middleware(RateLimitingMiddleware)
app.add_middleware(RequestIDMiddleware)

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Gzip Compression Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 5. Register Exception Handlers
register_exception_handlers(app)

# 6. Include API Routers
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn

    logger.info(f"Running web server on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.APP_ENV == "development",
    )
