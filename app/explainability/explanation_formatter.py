"""Formatter translating raw explainability reports into formatted string blocks."""

from app.explainability.explanation_models import ExplainabilityReport


def format_report_to_text(report: ExplainabilityReport) -> str:
    """Formats an ExplainabilityReport into a structured text document.

    Args:
        report: Compiles report.

    Returns:
        str: Multi-line description text block.
    """
    lines = [
        f"=== Explainability Diagnostic Report - {report.request_id} ===",
        f"Question: {report.question}",
        f"Pipeline Decision: {report.classification}",
        "",
        "--- Retrieval ---",
        report.retrieval_summary,
        "",
        "--- Citations & References ---",
        report.source_summary,
        "",
        "--- Factual Verification ---",
        report.verification_summary,
        "",
        "--- Confidence Factors Breakdown ---",
    ]

    for key, val in report.confidence_breakdown.items():
        name = key.replace("_", " ").title()
        lines.append(f" - {name}: {val:.4f}")

    lines.extend(
        [
            "",
            "--- Node Sequence Trace ---",
            " -> ".join(report.graph_path),
            "",
            "--- Warnings ---",
        ]
    )

    if report.warnings:
        for warn in report.warnings:
            lines.append(f" [WARNING] {warn}")
    else:
        lines.append(" None detected.")

    return "\n".join(lines)
