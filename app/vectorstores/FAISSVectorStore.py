"""Concrete Vector Store wrapper utilizing FAISS index files."""

from typing import Any, List
from app.core.interfaces.BaseVectorStore import BaseVectorStore
from app.vectorstore.faiss_store import FAISSStoreManager


class FAISSVectorStore(BaseVectorStore):
    """VectorStore implementation wrapping FAISS vector index."""

    def __init__(self, concrete_store: FAISSStoreManager = None) -> None:
        """Initializes using core FAISSStoreManager instance.

        Args:
            concrete_store: Core store database.
        """
        self._store = concrete_store or FAISSStoreManager()

    def add_documents(self, documents: List[Any]) -> None:
        """Adds texts chunks into index."""
        self._store.add_documents(documents)

    def similarity_search_with_score(
        self, query: str, k: int
    ) -> List[Any]:
        """Runs vector space similarity lookups."""
        if self._store.db is None:
            return []
        return self._store.db.similarity_search_with_score(query, k)

    def save(self, path: str) -> None:
        """Saves current index files locally."""
        self._store.save_index(path)

    def load(self, path: str) -> None:
        """Loads index files in memory."""
        self._store.load_index(path)
