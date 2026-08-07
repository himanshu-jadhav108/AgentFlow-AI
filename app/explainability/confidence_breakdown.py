"""Confidence breakdown calculator mapping weights for explanations."""

from typing import Dict


def calculate_confidence_breakdown(
    retrieval_score: float,
    source_coverage: float,
    verification_passed: bool,
    consistency_score: float,
) -> Dict[str, float]:
    """Calculates weighted breakdown scores contributing to total confidence.

    Breakdown:
        - Retrieval similarity: 40%
        - Source coverage: 25%
        - Grounding verification: 25%
        - Consistency checks: 10%

    Returns:
        Dict[str, float]: Contributed weights and score factors.
    """
    retrieval_contrib = retrieval_score * 0.40
    coverage_contrib = source_coverage * 0.25
    verify_contrib = (1.0 if verification_passed else 0.0) * 0.25
    consistency_contrib = consistency_score * 0.10

    total = retrieval_contrib + coverage_contrib + verify_contrib + consistency_contrib

    return {
        "retrieval_similarity_contribution": round(retrieval_contrib, 4),
        "source_coverage_contribution": round(coverage_contrib, 4),
        "verification_contribution": round(verify_contrib, 4),
        "consistency_contribution": round(consistency_contrib, 4),
        "total_confidence": round(total, 4),
    }
