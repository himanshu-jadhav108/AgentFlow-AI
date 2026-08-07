"""Ranking logic for sorting and scoring retrieved document chunks."""

from typing import Any, List, Tuple
from langchain_core.documents import Document as LCDocument
from app.schemas.retrieval import RetrievedChunk
from core.logger import logger


class SearchResultRanker:
    """Ranker to process search candidates, calculate confidence scores, and sort them hierarchically."""

    def rank_results(
        self,
        query: str,
        candidates: List[Tuple[LCDocument, float]],
        min_similarity: float = 0.0,
    ) -> List[RetrievedChunk]:
        """Convert raw candidates into RetrievedChunks, calculate scores, filter, and sort.

        Sorting order:
          1. Confidence score (descending)
          2. Document priority (descending, higher numbers represent higher priority)
          3. Chunk position/index (ascending)

        Args:
            query: The search query string.
            candidates: List of (LCDocument, score) from FAISS.
            min_similarity: Minimum similarity score to include in final output.

        Returns:
            List[RetrievedChunk]: Ranked and filtered chunks.
        """
        ranked_list: List[RetrievedChunk] = []

        for lc_doc, raw_score in candidates:
            # LangChain FAISS with COSINE distance returns Cosine Distance (1 - CosineSimilarity)
            # Normalize to Cosine Similarity = 1.0 - Cosine Distance
            similarity = 1.0 - raw_score
            similarity = max(0.0, min(1.0, similarity))  # Clamp to [0, 1] range

            # Filter by minimum similarity threshold
            if similarity < min_similarity:
                logger.debug(
                    f"Filtering chunk {lc_doc.metadata.get('chunk_id')} "
                    f"with similarity {similarity:.4f} below threshold {min_similarity:.4f}"
                )
                continue

            chunk_id = lc_doc.metadata.get("chunk_id", "unknown")
            doc_id = lc_doc.metadata.get("document_id", "unknown")
            source = lc_doc.metadata.get("source", "unknown")

            # Extract priority (default to 1 if not present)
            priority = int(lc_doc.metadata.get("priority", 1))

            chunk = RetrievedChunk(
                chunk_id=chunk_id,
                document_id=doc_id,
                source=source,
                text=lc_doc.page_content,
                score=similarity,  # Store cosine similarity as the score
                confidence_score=similarity,  # Map similarity directly to confidence
                metadata={
                    **lc_doc.metadata,
                    "priority": priority,
                },
            )
            ranked_list.append(chunk)

        # Hierarchical sorting:
        # 1. Similarity score (descending) -> -x.score
        # 2. Priority (descending, higher priority first) -> -x.metadata["priority"]
        # 3. Chunk index (ascending, earlier index first) -> x.metadata.get("chunk_index", 0)
        ranked_list.sort(
            key=lambda x: (
                -x.score,
                -x.metadata.get("priority", 1),
                x.metadata.get("chunk_index", 0),
            )
        )

        logger.debug(f"Ranked {len(ranked_list)} search results.")
        return ranked_list
