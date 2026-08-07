"""Metrics formatter calculating latency distribution percentages."""

from typing import Any, Dict


def calculate_performance_metrics(trace: Dict[str, Any]) -> Dict[str, Any]:
    """Computes timings and percentages contribution of each RAG step.

    Args:
        trace: Raw execution trace dictionary.

    Returns:
        Dict[str, Any]: Formatted performance breakdown.
    """
    total = trace.get("total_execution_time_ms", 0.0)
    retriever_ms = trace.get("retriever_time_ms", 0.0)
    generation_ms = trace.get("generation_time_ms", 0.0)
    verification_ms = trace.get("verification_time_ms", 0.0)

    # Fallback to sum of steps if total trace is 0
    if total <= 0.0:
        total = retriever_ms + generation_ms + verification_ms

    if total > 0.0:
        retriever_pct = (retriever_ms / total) * 100
        generation_pct = (generation_ms / total) * 100
        verification_pct = (verification_ms / total) * 100
    else:
        retriever_pct = generation_pct = verification_pct = 0.0

    other_ms = max(0.0, total - (retriever_ms + generation_ms + verification_ms))
    other_pct = (other_ms / total) * 100 if total > 0.0 else 0.0

    return {
        "total_latency_ms": round(total, 2),
        "retriever_latency": {
            "duration_ms": round(retriever_ms, 2),
            "percentage": round(retriever_pct, 2),
        },
        "generation_latency": {
            "duration_ms": round(generation_ms, 2),
            "percentage": round(generation_pct, 2),
        },
        "verification_latency": {
            "duration_ms": round(verification_ms, 2),
            "percentage": round(verification_pct, 2),
        },
        "system_overhead": {
            "duration_ms": round(other_ms, 2),
            "percentage": round(other_pct, 2),
        },
    }
