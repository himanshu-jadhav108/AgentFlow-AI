"""Concrete Verifier wrapper executing hybrid checks, conforming to BaseVerifier."""

from typing import Any, Dict, List
from app.core.interfaces.BaseVerifier import BaseVerifier
from app.verification.hybrid_verifier import HybridVerifier as ConcreteHybridVerifier


class HybridVerifier(BaseVerifier):
    """Verifier implementation performing dual fact validations."""

    def __init__(self, concrete_verifier: ConcreteHybridVerifier = None) -> None:
        """Initializes using core hybrid verifier object.

        Args:
            concrete_verifier: Concrete verifier runner.
        """
        self._verifier = concrete_verifier or ConcreteHybridVerifier()

    def verify(
        self,
        question: str,
        answer: str = "",
        contexts: List[str] = None,
        answer_payload: Dict[str, Any] = None,
        retrieved_chunks: List[Any] = None,
        retry_count: int = 0,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Runs validation sequence and returns results statistics.

        Supports both standard interface contracts and node parameters.
        """
        # If payload and chunks are supplied, delegate directly
        if answer_payload is not None:
            return self._verifier.verify(
                question=question,
                answer_payload=answer_payload,
                retrieved_chunks=retrieved_chunks or [],
                retry_count=retry_count,
            )

        # Fallback mapping to interface structure
        payload = {
            "answer": answer,
            "citations": [],
            "reason": "Direct interface verification",
        }
        # Build mock chunks from contexts
        from app.schemas.retrieval import RetrievedChunk

        mock_chunks = []
        for i, text in enumerate(contexts or []):
            mock_chunks.append(
                RetrievedChunk(
                    chunk_id=f"verify_mock_{i}",
                    document_id=f"verify_doc_{i}",
                    source=f"doc_{i}.md",
                    text=text,
                    score=1.0,
                    confidence_score=1.0,
                    metadata={},
                )
            )

        return self._verifier.verify(
            question=question,
            answer_payload=payload,
            retrieved_chunks=mock_chunks,
            retry_count=retry_count,
        )
