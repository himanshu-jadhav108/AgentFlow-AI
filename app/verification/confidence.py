"""Confidence score calculator using deterministic grounding factors."""

from typing import Any, List
from core.logger import logger


def calculate_confidence(
    retrieved_chunks: List[Any],
    citations: List[str],
    is_verified: bool,
    answer: str,
) -> float:
    """Calculates a normalized confidence score [0.0 - 1.0].

    Formula:
      Confidence = (0.5 * Retrieval Similarity) + (0.3 * Source Agreement) + (0.2 * Verification Result)

    1. Retrieval Similarity (0.5 weight):
       Average confidence score of the matching retrieved document chunks.
    2. Source Agreement (0.3 weight):
       Fraction of cited source names that exist in the retrieved document set.
       If answer is refusal ("I couldn't find supporting information."), agreement is 1.0.
    3. Verification Result (0.2 weight):
       1.0 if answer passes factual verification, 0.0 if not.

    Args:
        retrieved_chunks: List of RetrievedChunk instances.
        citations: List of source names cited in the answer.
        is_verified: Verification status flag.
        answer: Generated answer text.

    Returns:
        float: Normalized confidence score.
    """
    logger.info("Calculating answer confidence score...")

    # 1. Retrieval Similarity Score (Max 0.5)
    retrieval_similarity = 0.0
    if retrieved_chunks:
        # Sum confidence scores (which are already normalized [0-1])
        scores = [getattr(c, "confidence_score", getattr(c, "score", 0.0)) for c in retrieved_chunks]
        retrieval_similarity = sum(scores) / len(scores)

    # 2. Source Agreement Score (Max 0.3)
    source_agreement = 0.0
    retrieved_sources = set(getattr(c, "source", "") for c in retrieved_chunks if getattr(c, "source", ""))

    refusal_phrase = "couldn't find supporting information"
    is_refusal = refusal_phrase in answer.lower()

    if is_refusal:
        # If it's a refusal, citing no documents is correct agreement
        source_agreement = 1.0
    elif not citations:
        # If it's not a refusal but has no citations, agreement is zero
        source_agreement = 0.0
    else:
        # Check matching sources
        matching_count = sum(1 for cite in citations if any(cite in src for src in retrieved_sources))
        source_agreement = matching_count / len(citations)

    # 3. Verification Score (Max 0.2)
    verification_score = 1.0 if is_verified else 0.0

    # Compile the final weighted score
    raw_confidence = (
        (0.5 * retrieval_similarity) +
        (0.3 * source_agreement) +
        (0.2 * verification_score)
    )

    # Clamp confidence between 0.0 and 1.0
    confidence = max(0.0, min(1.0, raw_confidence))

    logger.info(
        f"Confidence Components - Retrieval: {retrieval_similarity:.4f}, "
        f"Agreement: {source_agreement:.4f}, Verification: {verification_score:.4f} | "
        f"Resulting Confidence: {confidence:.4f}"
    )

    return confidence
