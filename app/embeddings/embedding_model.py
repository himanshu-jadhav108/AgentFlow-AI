"""Local embedding model manager utilizing Sentence Transformers."""

import threading
import time

from langchain_community.embeddings import HuggingFaceEmbeddings

from config.settings import settings
from core.logger import logger


class LocalEmbeddingManager:
    """Singleton manager for local Hugging Face embedding model, loaded lazily."""

    _instance = None
    _lock = threading.Lock()
    _embeddings = None

    def __new__(cls) -> "LocalEmbeddingManager":
        """Ensures a single instance of LocalEmbeddingManager exists."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(LocalEmbeddingManager, cls).__new__(cls)
        return cls._instance

    def get_embeddings(self) -> HuggingFaceEmbeddings:
        """Lazy load and return the HuggingFaceEmbeddings object.

        Locks execution during first load to prevent double model instantiation in multi-threaded runtimes.

        Returns:
            HuggingFaceEmbeddings: The local embeddings service instance.
        """
        if self._embeddings is None:
            with self._lock:
                if self._embeddings is None:
                    model_name = settings.EMBEDDING_MODEL_NAME
                    logger.info(
                        f"Lazy loading local embedding model: '{model_name}'..."
                    )
                    start_time = time.time()

                    # Load Hugging Face embeddings running locally on CPU
                    self._embeddings = HuggingFaceEmbeddings(
                        model_name=model_name,
                        model_kwargs={"device": "cpu"},
                        encode_kwargs={
                            "normalize_embeddings": True
                        },  # Yields unit vectors for cosine similarity
                    )

                    elapsed = time.time() - start_time
                    logger.info(f"Embedding model loaded in {elapsed:.4f} seconds.")
        return self._embeddings
