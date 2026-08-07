"""Explainability builder assembling overall diagnostic reports."""

from typing import Any, Dict
from app.explainability.confidence_breakdown import calculate_confidence_breakdown
from app.explainability.explanation_models import ExplainabilityReport
from app.explainability.source_analyzer import analyze_sources
from app.explainability.timeline_builder import build_execution_timeline
from core.logger import logger


class ExplanationBuilder:
    """Assembles all database matches, citations, and verifications into a report."""

    @staticmethod
    def build_report(state: Dict[str, Any]) -> ExplainabilityReport:
        """Assembles state details and returns a populated report model.

        Args:
            state: Graph state dictionary.

        Returns:
            ExplainabilityReport: The explainability report.
        """
        logger.info("Explainability: Building diagnostic pipeline report...")

        # 1. Retrieve metadata from trace
        trace = state.get("execution_trace") or {}
        req_id = trace.get("request_id", "unknown")
        question = state.get("question", "")
        classification = state.get("classification", "unknown")

        # 2. Analyze sources
        selected_chunks = state.get("selected_chunks") or []
        citations = state.get("sources") or []
        sources_metrics = analyze_sources(selected_chunks, citations)

        # 3. Analyze verification
        verify_status = state.get("verification_status", "unverified")
        passed = verify_status == "verified"
        retry_count = state.get("retry_count", 0)
        verify_summary = (
            f"Factual Grounding Check: {'PASS' if passed else 'FAIL'}.\n"
            f"Verification Status: '{verify_status}'.\n"
            f"Self-Correction Retry Count: {retry_count} iterations."
        )

        # 4. Confidence breakdown
        similarity_score = state.get("confidence", 0.0)
        # Ratio of cited files to retrieved files (capped at 1.0)
        retrieved_sources_count = sources_metrics["unique_sources_count"]
        coverage_ratio = (
            len(set(citations)) / retrieved_sources_count
            if retrieved_sources_count > 0
            else 0.0
        )
        breakdown = calculate_confidence_breakdown(
            retrieval_score=similarity_score,
            source_coverage=min(coverage_ratio, 1.0),
            verification_passed=passed,
            consistency_score=0.9 if passed else 0.2,
        )

        # 5. Timeline & Graph paths
        nodes = trace.get("nodes") or []
        timeline = build_execution_timeline(nodes)
        graph_path = trace.get("graph_path") or []

        # 6. Warnings detector
        warnings = []
        if similarity_score < 0.5:
            warnings.append(
                f"Low query retrieval similarity score ({similarity_score:.4f})."
            )
        if len(citations) == 0 and classification == "answerable":
            warnings.append("No source files cited in response.")
        if retry_count > 1:
            warnings.append(
                f"Multiple self-correction retry cycles executed ({retry_count})."
            )

        execution_summary = (
            f"Query was triaged as '{classification}' and processed through "
            f"nodes: {' -> '.join(graph_path)} in {trace.get('total_execution_time_ms', 0.0):.2f}ms."
        )

        return ExplainabilityReport(
            request_id=req_id,
            question=question,
            classification=classification,
            retrieval_summary=sources_metrics["summary"],
            source_summary=f"Citations: {citations}. Coverage: {coverage_ratio:.2f}",
            verification_summary=verify_summary,
            confidence_breakdown=breakdown,
            execution_summary=execution_summary,
            graph_path=graph_path,
            timeline=timeline,
            warnings=warnings,
            metadata={
                "total_execution_time_ms": trace.get("total_execution_time_ms", 0.0)
            },
        )
