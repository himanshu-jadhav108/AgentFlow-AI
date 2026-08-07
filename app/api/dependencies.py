"""API dependency injection resources."""

from typing import Any
from app.graph.builder import build_graph
from app.retrieval.retriever import SemanticRetriever
from cache.cache_manager import CacheManager

# Pre-compiled singletons to avoid rebuilds across request boundaries
_compiled_graph = build_graph()
_retriever_instance = SemanticRetriever()
_cache_instance = CacheManager()


def get_agent_graph() -> Any:
    """Returns the compiled LangGraph workflow instance."""
    return _compiled_graph


def get_retriever() -> SemanticRetriever:
    """Returns the SemanticRetriever database query resource."""
    return _retriever_instance


def get_cache_manager() -> CacheManager:
    """Returns the global query cache manager instance."""
    return _cache_instance
