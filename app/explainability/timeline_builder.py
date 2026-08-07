"""Timeline builder compiling timestamps and durations from nodes traces."""

from typing import Any, Dict, List


def build_execution_timeline(nodes_trace: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Converts raw node logs into sequential event records.

    Args:
        nodes_trace: List of node step dictionaries from the execution trace.

    Returns:
        List[Dict[str, Any]]: Sequential event timeline.
    """
    timeline = []
    for node in nodes_trace:
        node_name = node.get("node_name", "unknown").lower()
        event_name = node.get("node_name", "unknown").capitalize()

        # Map to descriptive titles
        if node_name == "start":
            event_name = "Request Received"
        elif node_name == "triage":
            event_name = "Triage Classification"
        elif node_name == "retrieve":
            event_name = "FAISS Retrieval Search"
        elif node_name == "generate":
            event_name = "Prompt Generation"
        elif node_name == "verify":
            event_name = "Hybrid Grounding Verification"
        elif node_name == "end":
            event_name = "Response Returned"

        timeline.append(
            {
                "event": event_name,
                "timestamp": node.get("timestamp", ""),
                "duration_ms": node.get("duration_ms", 0.0),
                "summary": node.get("output_summary", ""),
            }
        )

    return timeline
