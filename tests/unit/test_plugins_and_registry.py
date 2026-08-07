"""Unit tests validating interfaces contracts and registries."""

from typing import List
import pytest
from app.core.interfaces.BaseRetriever import BaseRetriever
from app.core.registry import ComponentRegistry
from app.schemas.retrieval import RetrievedChunk


class MockRetriever(BaseRetriever):
    """Faux retriever for tests."""

    def retrieve(
        self, query: str, top_k: int, min_similarity: float
    ) -> List[RetrievedChunk]:
        """Simple mock return."""
        return []


def test_registry_lazy_loading() -> None:
    """Verifies registry falls back to standard lazy load factories."""
    reg = ComponentRegistry()
    # Retriever
    ret = reg.get_retriever()
    assert ret is not None

    # Embeddings
    embed = reg.get_embeddings()
    assert embed is not None


def test_registry_overrides() -> None:
    """Verifies registry supports replacing instances (DI mock checks)."""
    reg = ComponentRegistry()
    mock = MockRetriever()
    reg.replace("retriever", mock)

    assert reg.get_retriever() is mock
