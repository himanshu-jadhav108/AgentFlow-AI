"""Concrete Retriever wrapper utilizing FAISS database lookups."""

from typing import List
from app.core.interfaces.BaseRetriever import BaseRetriever
from app.retrieval.retriever import SemanticRetriever
from app.schemas.retrieval import RetrievedChunk


class FAISSRetriever(BaseRetriever):
    """Retriever implementation executing vector search checks."""

    def __init__(self, concrete_retriever: SemanticRetriever = None) -> None:
        """Initializes by injecting concrete retriever.

        Args:
            concrete_retriever: Core retriever instance.
        """
        self._retriever = concrete_retriever or SemanticRetriever()

    def retrieve(
        self, query: str, top_k: int, min_similarity: float
    ) -> List[RetrievedChunk]:
        """Queries local store and returns matched document chunks."""
        return self._retriever.retrieve(
            query=query, top_k=top_k, min_similarity=min_similarity
        )
