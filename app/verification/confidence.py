"""Confidence score calculator using weighted, configurable grounding metrics."""

from typing import Any, List

from core.logger import logger


def calculate_confidence(
    retrieved_chunks: List[Any],
    citations: List[str],
    rule_passed: bool,
    semantic_passed: bool,
    answer: str,
    retrieval_weight: float = 0.4,
    semantic_weight: float = 0.3,
    coverage_weight: float = 0.2,
    rule_weight: float = 0.1,
) -> float:
    """Calculates grounded confidence using weighted, configurable factors.

    Formula:
      Confidence = (W_ret * Retrieval Similarity) +
                   (W_sem * Semantic Pass) +
                   (W_cov * Source Coverage) +
                   (W_rule * Rule Pass)

    1. Retrieval Similarity (W_ret weight):
       Average similarity score of top matching FAISS chunks.
    2. Semantic Verification (W_sem weight):
       1.0 if semantic check passed (or is disabled), 0.0 if failed.
    3. Source Coverage (W_cov weight):
       Fraction of cited source names matching retrieved document sources.
       If answer is refusal ("I couldn't find supporting information."), score is 1.0.
    4. Rule Validation (W_rule weight):
       1.0 if deterministic rule checks passed, 0.0 if failed.

    Args:
        retrieved_chunks: List of RetrievedChunk instances.
        citations: List of source names cited in the answer.
        rule_passed: Rule verifier passed status.
        semantic_passed: Semantic verifier passed status.
        answer: Generated answer text string.
        retrieval_weight: Weight for similarity score [default 0.4].
        semantic_weight: Weight for semantic correctness [default 0.3].
        coverage_weight: Weight for citation match agreements [default 0.2].
        rule_weight: Weight for deterministic validation checks [default 0.1].

    Returns:
        float: Weighted confidence score clamped in [0.0 - 1.0].
    """
    logger.info("ConfidenceEngine: Redesigning weighted confidence calculations...")

    # Normalize weights to ensure they sum to 1.0
    total_w = retrieval_weight + semantic_weight + coverage_weight + rule_weight
    if total_w != 1.0 and total_w > 0.0:
        retrieval_weight /= total_w
        semantic_weight /= total_w
        coverage_weight /= total_w
        rule_weight /= total_w

    # 1. Retrieval Similarity (W_ret)
    retrieval_similarity = 0.0
    if retrieved_chunks:
        scores = [
            getattr(c, "confidence_score", getattr(c, "score", 0.0))
            for c in retrieved_chunks
        ]
        retrieval_similarity = sum(scores) / len(scores)

    # 2. Semantic Verification (W_sem)
    semantic_score = 1.0 if semantic_passed else 0.0

    # 3. Source Coverage (W_cov)
    coverage_score = 0.0
    retrieved_sources = set(
        getattr(c, "source", "") for c in retrieved_chunks if getattr(c, "source", "")
    )

    refusal_phrase = "couldn't find supporting information"
    is_refusal = refusal_phrase in answer.lower()

    if is_refusal:
        coverage_score = 1.0
    elif not citations:
        coverage_score = 0.0
    else:
        matching = sum(
            1
            for cite in citations
            if any(cite.lower() in src.lower() for src in retrieved_sources)
        )
        coverage_score = matching / len(citations)

    # 4. Rule Validation (W_rule)
    rule_score = 1.0 if rule_passed else 0.0

    # Calculate final confidence
    raw_confidence = (
        (retrieval_weight * retrieval_similarity)
        + (semantic_weight * semantic_score)
        + (coverage_weight * coverage_score)
        + (rule_weight * rule_score)
    )

    confidence = max(0.0, min(1.0, raw_confidence))

    logger.info(
        f"Confidence Weights - Ret: {retrieval_weight} ({retrieval_similarity:.4f}), "
        f"Sem: {semantic_weight} ({semantic_score:.1f}), "
        f"Cov: {coverage_weight} ({coverage_score:.1f}), "
        f"Rule: {rule_weight} ({rule_score:.1f}) | "
        f"Grounded Confidence: {confidence:.4f}"
    )

    return confidence
