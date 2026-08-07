"""Main entry point for the FastAPI application of AgentFlow AI."""

from contextlib import asynccontextmanager
from typing import Dict, Any, List
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.exceptions import RequestValidationError
from config.settings import settings
from core.logger import setup_logging, logger
from app.schemas.retrieval import SearchRequest, SearchResponse, IndexResponse, GraphRunRequest, GraphRunResponse
from app.services.indexing_service import IndexingService
from app.retrieval.retriever import SemanticRetriever
from models.responses import HealthResponse, VersionResponse, ErrorResponse
from core.exceptions import AppException, app_exception_handler, validation_exception_handler, generic_exception_handler
from app.graph.builder import build_graph
from app.graph.visualization import generate_graph_visualizations

# Initialize unified loguru logging
setup_logging()

# Compile the agent orchestration graph once
agent_graph = build_graph()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle hooks for the FastAPI application."""
    logger.info("Starting up AgentFlow AI API Service...")
    logger.info(f"Configuration: ENV={settings.APP_ENV}, PORT={settings.PORT}")
    logger.info(f"Local AI Config: LLM={settings.LLM_PROVIDER}:{settings.LLM_MODEL_NAME}")
    logger.info(f"Vector Database Path: {settings.VECTOR_DB_PATH}")

    # Generate graph visualizations on startup
    logger.info("Generating agent workflow visualizations (Mermaid, ASCII, PNG)...")
    generate_graph_visualizations(agent_graph)

    yield
    logger.info("Shutting down AgentFlow AI API Service...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise-grade local customer support AI agent using FastAPI and LangGraph",
    version="0.1.0",
    lifespan=lifespan,
)

# Register global exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


@app.get("/", include_in_schema=False)
async def root_redirect():
    """Redirect root path to interactive Swagger API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check system health status and configuration details."""
    logger.debug("Health check endpoint queried")
    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
    )


@app.get("/version", response_model=VersionResponse)
async def get_version() -> VersionResponse:
    """Get the current application version metadata."""
    return VersionResponse(
        version="0.1.0",
        app_name=settings.APP_NAME,
        api_version="v1",
        description="Local Customer Support Agent powered by LangGraph, FastAPI, and FAISS",
    )


@app.post("/index", response_model=IndexResponse)
async def rebuild_index() -> IndexResponse:
    """Trigger a rebuild of the vector database from source markdown files and resolved support cases."""
    logger.info("API request received: Rebuild vector index (/index)")
    try:
        service = IndexingService()
        response = service.build_index()
        if response.status == "error":
            raise HTTPException(status_code=500, detail=response.message)
        return response
    except Exception as e:
        logger.exception(f"Unexpected error rebuilding index: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", response_model=SearchResponse)
async def search_index(request: SearchRequest) -> SearchResponse:
    """Execute a semantic search query against the local FAISS vector store."""
    logger.info(f"API request received: Search query '{request.query}'")
    start_time = time.time()
    try:
        retriever = SemanticRetriever()
        results = retriever.retrieve(
            query=request.query,
            top_k=request.top_k,
            min_similarity=request.min_similarity,
        )
        latency_ms = (time.time() - start_time) * 1000
        logger.info(f"API Search request completed in {latency_ms:.2f}ms. Returned {len(results)} chunks.")
        return SearchResponse(
            query=request.query,
            results=results,
            latency_ms=latency_ms,
        )
    except Exception as e:
        logger.exception(f"Unexpected error executing search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/graph/run", response_model=GraphRunResponse)
async def run_agent_graph(request: GraphRunRequest) -> GraphRunResponse:
    """Execute the support agent LangGraph workflow for the given question."""
    logger.info(f"API request received: Run agent graph for question '{request.question}'")
    try:
        # Initialize default workflow state
        initial_state = {
            "question": request.question,
            "classification": "clarification",
            "conversation_history": [],
            "retrieved_documents": [],
            "selected_chunks": [],
            "answer": None,
            "confidence": 0.0,
            "sources": [],
            "requires_human": False,
            "retry_count": 0,
            "max_retries": 3,
            "verification_status": "unverified",
            "metadata": {},
            "execution_log": [],
            "timestamps": {},
        }

        # Execute compiled graph asynchronously
        final_state = await agent_graph.ainvoke(initial_state)

        # Extract path executed from log trace
        node_path = []
        for log in final_state.get("execution_log", []):
            if "START" in log or "start" in log.lower():
                node_path.append("start")
            elif "triage" in log.lower():
                node_path.append("triage")
            elif "retrieve" in log.lower():
                node_path.append("retrieve")
            elif "clarification" in log.lower():
                node_path.append("clarification")
            elif "escalation" in log.lower() or "escalate" in log.lower():
                node_path.append("escalation")
            elif "out-of-scope" in log.lower() or "out of scope" in log.lower():
                node_path.append("out_of_scope")
            elif "end" in log.lower():
                node_path.append("end")

        # Deduplicate consecutive transitions to keep the path clean
        deduped_path = []
        for node in node_path:
            if not deduped_path or deduped_path[-1] != node:
                deduped_path.append(node)

        return GraphRunResponse(
            question=request.question,
            classification=final_state.get("classification", "unknown"),
            node_path=deduped_path,
            final_state=final_state,
        )
    except Exception as e:
        logger.exception(f"Unexpected error executing graph workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Running web server on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.APP_ENV == "development",
    )
