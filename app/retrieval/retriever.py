"""Semantic retrieval module for finding relevant document chunks."""

import time
from typing import List, Optional

from app.retrieval.ranking import SearchResultRanker
from app.schemas.retrieval import RetrievedChunk
from app.vectorstore.faiss_store import FAISSStoreManager
from config.settings import settings
from core.logger import logger


class SemanticRetriever:
    """Retriever that searches the local FAISS store and returns ranked results."""

    def __init__(self, store_manager: Optional[FAISSStoreManager] = None) -> None:
        """Initialize the retriever with an optional store manager or create one."""
        self.store_manager = store_manager or FAISSStoreManager()
        self.ranker = SearchResultRanker()

    def _ensure_index_loaded(self) -> bool:
        """Ensures that the FAISS index is loaded in memory."""
        if self.store_manager.db is not None:
            return True

        # Try to load from the configured path
        db_path = settings.VECTOR_DB_PATH
        logger.info(f"Retriever checking local store path: {db_path}")
        return self.store_manager.load_index(db_path)

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_similarity: Optional[float] = None,
    ) -> List[RetrievedChunk]:
        """Retrieves and ranks relevant document chunks matching the query.

        Args:
            query: The user's query question.
            top_k: Max chunks to retrieve. Defaults to 4.
            min_similarity: Minimum confidence threshold [0.0 - 1.0]. Defaults to 0.0.

        Returns:
            List[RetrievedChunk]: Sorted list of retrieved and scored chunks.
        """
        start_time = time.time()

        if not self._ensure_index_loaded():
            logger.error("FAISS index is not initialized. Retrieve aborted.")
            return []

        # Determine limits
        k = top_k or 4
        min_sim = min_similarity if min_similarity is not None else 0.0

        logger.info(
            f"Executing semantic search for query: '{query}' (top_k={k}, min_similarity={min_sim})"
        )

        # Perform FAISS search (returns tuples of (LCDocument, cosine_distance))
        # Since we use distance_strategy="COSINE", the returned score is Cosine Distance (1 - CosineSimilarity)
        try:
            results_with_scores = self.store_manager.db.similarity_search_with_score(
                query, k=k
            )
        except Exception as e:
            logger.error(f"Error executing similarity search: {e}")
            return []

        latency_ms = (time.time() - start_time) * 1000
        from monitoring.metrics import metrics

        metrics.record_retriever(latency_ms)
        logger.info(
            f"FAISS search completed in {latency_ms:.2f}ms. Found {len(results_with_scores)} candidates."
        )

        # Rank results and transform them into RetrievedChunk objects
        ranked_chunks = self.ranker.rank_results(
            query=query,
            candidates=results_with_scores,
            min_similarity=min_sim,
        )

        return ranked_chunks
