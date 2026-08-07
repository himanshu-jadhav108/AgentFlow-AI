"""Source reference analyzer for knowledge base retrieval checks."""

from typing import Any, Dict, List


def analyze_sources(chunks: List[Any], citations: List[str]) -> Dict[str, Any]:
    """Calculates coverage, diversity, duplicate references, and scores.

    Args:
        chunks: List of RetrievedChunk objects.
        citations: List of source file citations.

    Returns:
        Dict[str, Any]: Source metrics report.
    """
    total_chunks = len(chunks)
    unique_sources = list(set(chunk.source for chunk in chunks if hasattr(chunk, "source")))
    unique_citations = list(set(citations))

    scores = [chunk.score for chunk in chunks if hasattr(chunk, "score")]
    avg_similarity = sum(scores) / len(scores) if scores else 0.0

    diversity = len(unique_sources)
    coverage = len(unique_citations) / diversity if diversity > 0 else 0.0

    # Compile descriptive text summary
    summary_msg = (
        f"Retrieved {total_chunks} relevant document chunks from {diversity} unique source files. "
        f"Citations map to {len(unique_citations)} unique files. "
        f"Average similarity score is {avg_similarity:.4f}."
    )

    return {
        "summary": summary_msg,
        "total_retrieved_chunks": total_chunks,
        "unique_sources_count": diversity,
        "unique_citations_count": len(unique_citations),
        "average_similarity": round(avg_similarity, 4),
        "source_coverage_ratio": round(coverage, 4),
    }
