"""Dashboard formatter coordinating traces, reports, and timeline renderers."""

from typing import Any, Dict
from app.dashboard.dashboard_models import DebugSessionReport
from app.dashboard.graph_renderer import render_graph_mermaid
from app.dashboard.metrics_formatter import calculate_performance_metrics
from app.dashboard.timeline_renderer import render_timeline_ascii


def compile_debug_session_report(session: Dict[str, Any]) -> DebugSessionReport:
    """Formats raw session dictionary into a typed DebugSessionReport schema.

    Args:
        session: Stored raw session data.

    Returns:
        DebugSessionReport: Fully compiled debug session report.
    """
    trace = session.get("execution_trace", {})
    explainability = session.get("explainability_report", {})

    # Calculate metrics
    perf = calculate_performance_metrics(trace)

    # Render ASCII timeline
    timeline_events = explainability.get("timeline", [])
    ascii_timeline = render_timeline_ascii(timeline_events)

    # Render Mermaid graph
    graph_path = trace.get("graph_path", [])
    mermaid_graph = render_graph_mermaid(graph_path)

    # Copy explainability report dictionary and inject visualizations
    explainability_extended = dict(explainability)
    explainability_extended.update(
        {
            "ascii_timeline": ascii_timeline,
            "mermaid_graph": mermaid_graph,
        }
    )

    return DebugSessionReport(
        request_id=session.get("request_id", ""),
        timestamp=session.get("timestamp", ""),
        question=session.get("question", ""),
        classification=session.get("classification", ""),
        final_response=session.get("final_response", {}),
        execution_trace=trace,
        explainability_report=explainability_extended,
        performance_metrics=perf,
        warnings=explainability.get("warnings", []),
    )
