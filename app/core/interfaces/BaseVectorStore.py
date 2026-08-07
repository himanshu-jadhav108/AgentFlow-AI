"""Abstract Base Class defining the Vector Store contract."""

from abc import ABC, abstractmethod
from typing import Any, List


class BaseVectorStore(ABC):
    """Interface for local vector database indices."""

    @abstractmethod
    def add_documents(self, documents: List[Any]) -> None:
        """Adds text documents/chunks into the active index.

        Args:
            documents: List of text chunk structures.
        """
        pass

    @abstractmethod
    def similarity_search_with_score(
        self, query: str, k: int
    ) -> List[Any]:
        """Performs nearest-neighbor similarity search.

        Args:
            query: Query search string.
            k: Top-k matches count.

        Returns:
            List[Any]: Scored retrieval objects.
        """
        pass

    @abstractmethod
    def save(self, path: str) -> None:
        """Persists FAISS files locally.

        Args:
            path: Directory location.
        """
        pass

    @abstractmethod
    def load(self, path: str) -> None:
        """Loads database files into memory.

        Args:
            path: Target directory path.
        """
        pass
