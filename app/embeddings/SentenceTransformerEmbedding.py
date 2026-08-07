"""Concrete Embedding wrapper utilizing SentenceTransformers."""

from typing import List
from app.core.interfaces.BaseEmbeddingModel import BaseEmbeddingModel
from app.embeddings.embedding_model import LocalEmbeddingManager


class SentenceTransformerEmbedding(BaseEmbeddingModel):
    """Embedding implementation wrapping HuggingFace/SentenceTransformers."""

    def __init__(self, concrete_embeddings=None) -> None:
        """Initializes using core embedding model runner.

        Args:
            concrete_embeddings: Core embedding model instance.
        """
        self._embeddings = (
            concrete_embeddings or LocalEmbeddingManager().get_embeddings()
        )

    def embed_query(self, text: str) -> List[float]:
        """Calculates query vector."""
        return self._embeddings.embed_query(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Calculates document vectors list."""
        return self._embeddings.embed_documents(texts)
