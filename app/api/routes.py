"""REST API endpoints defining route handlers for AgentFlow AI."""

import os
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from app.api.dependencies import get_agent_graph, get_cache_manager, get_retriever
from app.api.validators import RequestValidator
from app.schemas.answer import AskRequest, AskResponse
import time
from app.schemas.retrieval import SearchRequest, SearchResponse, IndexResponse, GraphRunRequest, GraphRunResponse
from app.services.indexing_service import IndexingService
from cache.cache_manager import CacheManager
from config.settings import settings
from core.logger import logger
from models.responses import HealthResponse, VersionResponse
from monitoring.metrics import metrics

router = APIRouter()


@router.get("/", include_in_schema=False)
async def root_redirect() -> RedirectResponse:
    """Redirects client requests to interactive API Swagger docs."""
    return RedirectResponse(url="/docs")


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Check System Health",
    description="Returns application health status, target run environment, and loaded settings configuration.",
)
async def health_check() -> HealthResponse:
    logger.debug("Health endpoint queried.")
    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
    )


@router.get(
    "/version",
    response_model=VersionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Application Version",
    description="Returns core application code version and running API specifications.",
)
async def get_version() -> VersionResponse:
    return VersionResponse(
        version="0.1.0",
        app_name=settings.APP_NAME,
        api_version="v1",
        description="Local Customer Support Agent powered by LangGraph, FastAPI, and FAISS",
    )


@router.post(
    "/index",
    response_model=IndexResponse,
    status_code=status.HTTP_200_OK,
    summary="Rebuild Vector Index",
    description="Triggers search database regeneration by parsing raw markdown documents from disk.",
)
async def rebuild_index(
    cache_manager: CacheManager = Depends(get_cache_manager),
) -> IndexResponse:
    logger.info("API command received: Rebuild database index.")
    try:
        service = IndexingService()
        response = service.build_index()

        if response.status == "error":
            raise HTTPException(status_code=500, detail=response.message)

        # Clear query caches as context facts have changed
        cache_manager.clear()
        return response

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception(f"Index rebuild failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to build vector index: {e}")


@router.post(
    "/search",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search Document Index",
    description="Queries local vector database, returning scored semantic document chunks.",
)
async def search_index(
    request: SearchRequest,
    retriever=Depends(get_retriever),
) -> SearchResponse:
    logger.info(f"API search received: Query: '{request.query}'")

    # Sanitize input query
    sanitized_query = RequestValidator.validate_question(request.query)

    start_time = time.time()
    try:
        results = retriever.retrieve(
            query=sanitized_query,
            top_k=request.top_k,
            min_similarity=request.min_similarity,
        )

        latency_ms = (time.time() - start_time) * 1000
        return SearchResponse(
            query=sanitized_query,
            results=results,
            latency_ms=latency_ms,
        )
    except Exception as e:
        logger.exception(f"Semantic search execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database search execution failure: {e}")


@router.post(
    "/ask",
    response_model=AskResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask Support Agent",
    description="Submits question to the self-correcting RAG workflow. Employs caching and verification.",
)
async def ask_agent(
    request: AskRequest,
    agent_graph=Depends(get_agent_graph),
    cache_manager: CacheManager = Depends(get_cache_manager),
) -> AskResponse:
    logger.info(f"API ask request received: Question: '{request.question}'")

    # 1. Sanitize and validate input
    sanitized_question = RequestValidator.validate_question(request.question)

    # 2. Cache Lookup
    cached_response = cache_manager.get_answer(sanitized_question)
    if cached_response:
        return AskResponse(**cached_response)

    try:
        # 3. Initialize Graph State
        initial_state = {
            "question": sanitized_question,
            "classification": "clarification",
            "conversation_history": [],
            "retrieved_documents": [],
            "selected_chunks": [],
            "answer": None,
            "confidence": 0.0,
            "sources": [],
            "requires_human": False,
            "retry_count": 0,
            "max_retries": settings.MAX_RETRIES,
            "verification_status": "unverified",
            "metadata": {},
            "execution_log": [],
            "timestamps": {},
        }

        # 4. Invoke LangGraph workflow asynchronously
        final_state = await agent_graph.ainvoke(initial_state)

        # 5. Extract state results
        classification = final_state.get("classification", "unknown")
        answer = final_state.get("answer", "")
        confidence = final_state.get("confidence", 0.0)
        sources = final_state.get("sources", [])
        requires_human = final_state.get("requires_human", False)

        meta = final_state.get("metadata", {})
        reason = meta.get("verification_reason", meta.get("triage_reason", "Processed successfully."))

        if not answer:
            answer = "I could not find supporting information."

        response_payload = {
            "classification": classification,
            "answer": answer,
            "confidence": confidence,
            "sources": sources,
            "requires_human": requires_human,
            "reason": reason,
            "metadata": {
                "generation_latency_ms": meta.get("generation_latency_ms", 0.0),
                "verification_latency_ms": meta.get("verification_latency_ms", 0.0),
            },
        }

        # 6. Save successful responses in query cache
        if not requires_human and classification in ["answerable", "out_of_scope"]:
            cache_manager.set_answer(sanitized_question, response_payload)

        return AskResponse(**response_payload)

    except Exception as e:
        logger.exception(f"RAG workflow execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Graph workflow execution failed: {e}")


@router.post(
    "/graph/run",
    response_model=GraphRunResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute Graph Workflow",
    description="Invokes the full LangGraph state machine sequentially and returns the final state snapshot and execution path.",
)
async def run_graph(
    request: GraphRunRequest,
    agent_graph=Depends(get_agent_graph),
) -> GraphRunResponse:
    logger.info(f"API graph run received: Question '{request.question}'")
    sanitized_question = RequestValidator.validate_question(request.question)
    try:
        initial_state = {
            "question": sanitized_question,
            "classification": "clarification",
            "conversation_history": [],
            "retrieved_documents": [],
            "selected_chunks": [],
            "answer": None,
            "confidence": 0.0,
            "sources": [],
            "requires_human": False,
            "retry_count": 0,
            "max_retries": settings.MAX_RETRIES,
            "verification_status": "unverified",
            "metadata": {},
            "execution_log": [],
            "timestamps": {},
        }
        final_state = await agent_graph.ainvoke(initial_state)

        # Determine execution path for backward-compatibility checks
        classification = final_state.get("classification", "unknown")
        node_path = ["start", "triage"]
        if classification == "answerable":
            node_path.extend(["retrieve", "generate", "verify", "end"])
        elif classification == "out_of_scope":
            node_path.extend(["out_of_scope", "end"])
        elif classification == "escalation":
            node_path.extend(["escalation", "end"])
        else:
            node_path.extend(["clarification", "end"])

        return GraphRunResponse(
            question=sanitized_question,
            classification=classification,
            node_path=node_path,
            final_state=final_state,
        )
    except Exception as e:
        logger.exception(f"Graph execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/metrics",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get System Metrics",
    description="Exposes system latency timing metrics and cache hit statistics.",
)
async def get_metrics() -> Dict[str, Any]:
    """Returns timing averages, total loads, and cache hits data."""
    cache_manager = get_cache_manager()
    return {
        "system_metrics": metrics.get_summary(),
        "cache_statistics": cache_manager.stats,
    }


@router.get(
    "/graph",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get Workflow Graph",
    description="Returns the current LangGraph structural workflow drawing formats.",
)
async def get_graph() -> Dict[str, Any]:
    """Returns ASCII drawings and Mermaid formatting blocks representing agent workflow paths."""
    mermaid_path = "assets/graph_mermaid.md"
    ascii_path = "assets/graph_ascii.txt"

    mermaid_content = "Graph definition not found."
    ascii_content = "Graph definition not found."

    if os.path.exists(mermaid_path):
        with open(mermaid_path, "r", encoding="utf-8") as f:
            mermaid_content = f.read()

    if os.path.exists(ascii_path):
        with open(ascii_path, "r", encoding="utf-8") as f:
            ascii_content = f.read()

    return {
        "mermaid": mermaid_content,
        "ascii": ascii_content,
    }
