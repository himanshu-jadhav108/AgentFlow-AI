"""Abstract Base Class defining the Retriever contract."""

from abc import ABC, abstractmethod
from typing import List
from app.schemas.retrieval import RetrievedChunk


class BaseRetriever(ABC):
    """Interface for document similarity retrieve pipelines."""

    @abstractmethod
    def retrieve(
        self, query: str, top_k: int, min_similarity: float
    ) -> List[RetrievedChunk]:
        """Queries database passages and returns scored document chunks.

        Args:
            query: Sanitized question.
            top_k: Number of chunks to select.
            min_similarity: Score boundary limit.

        Returns:
            List[RetrievedChunk]: Matched passage list.
        """
        pass
