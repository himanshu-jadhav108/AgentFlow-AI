"""Abstract Base Class defining the Embedding Model contract."""

from abc import ABC, abstractmethod
from typing import List


class BaseEmbeddingModel(ABC):
    """Interface for text embedding pipelines."""

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Calculates embedding vector for a single query string.

        Args:
            text: Query search text.

        Returns:
            List[float]: Core vector float list.
        """
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Calculates embedding vectors for a list of document strings.

        Args:
            texts: List of document text strings.

        Returns:
            List[List[float]]: List of vector float lists.
        """
        pass
