"""Unit tests validating the Explainability Engine."""

from app.explainability.confidence_breakdown import calculate_confidence_breakdown
from app.explainability.explanation_builder import ExplanationBuilder
from app.explainability.explanation_formatter import format_report_to_text
from app.explainability.source_analyzer import analyze_sources
from app.explainability.timeline_builder import build_execution_timeline


def test_confidence_breakdown_math() -> None:
    """Verifies grounding calculation weights logic."""
    res = calculate_confidence_breakdown(
        retrieval_score=0.8,
        source_coverage=0.6,
        verification_passed=True,
        consistency_score=0.9,
    )
    assert "total_confidence" in res
    # 0.8 * 0.4 = 0.32
    # 0.6 * 0.25 = 0.15
    # 1.0 * 0.25 = 0.25
    # 0.9 * 0.1 = 0.09
    # Total = 0.81
    assert abs(res["total_confidence"] - 0.81) < 1e-4
    assert res["verification_contribution"] == 0.25


def test_builder_compiling() -> None:
    """Verifies overall diagnostic builder creates valid report schemas."""
    state = {
        "question": "How do read-only users setup API keys?",
        "classification": "answerable",
        "selected_chunks": [],
        "sources": [],
        "verification_status": "verified",
        "confidence": 0.8,
        "retry_count": 0,
        "execution_trace": {
            "request_id": "test-req",
            "graph_path": ["start", "triage", "retrieve", "end"],
            "nodes": [
                {
                    "node_name": "start",
                    "timestamp": "2026-08-07 10:00:00",
                    "duration_ms": 1.5,
                    "output_summary": "init",
                }
            ],
        },
    }
    report = ExplanationBuilder.build_report(state)
    assert report.request_id == "test-req"
    assert "Factual Grounding Check: PASS" in report.verification_summary

    txt = format_report_to_text(report)
    assert "API keys?" in txt
