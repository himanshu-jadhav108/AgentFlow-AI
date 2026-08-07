"""Execution tracing helpers to monitor LangGraph nodes execution."""

import time
from typing import Any, Dict


def init_execution_trace(request_id: str, question: str) -> Dict[str, Any]:
    """Pre-populates an empty execution trace dictionary.

    Args:
        request_id: Correlation query ID.
        question: User query question.

    Returns:
        Dict[str, Any]: Pre-populated trace payload.
    """
    return {
        "request_id": request_id,
        "question": question,
        "graph_path": [],
        "visited_nodes": [],
        "retriever_time_ms": 0.0,
        "generation_time_ms": 0.0,
        "verification_time_ms": 0.0,
        "retry_count": 0,
        "confidence": 0.0,
        "final_decision": "unknown",
        "total_execution_time_ms": 0.0,
        "nodes": [],
    }


def record_node_trace(
    state: Dict[str, Any],
    node_name: str,
    start_time: float,
    input_summary: str,
    output_summary: str,
    decision: str = "continue",
) -> Dict[str, Any]:
    """Appends timing, summaries, and decisions for a single node step.

    Args:
        state: State dictionary to modify.
        node_name: Current node identifier.
        start_time: Epoch timestamp when node execution initiated.
        input_summary: Input summary description.
        output_summary: Output summary description.
        decision: Node conditional decision route name.

    Returns:
        Dict[str, Any]: Mutated state.
    """
    duration_ms = (time.time() - start_time) * 1000

    trace = state.get("execution_trace")
    if not trace:
        trace = init_execution_trace("manual", state.get("question", ""))

    trace["visited_nodes"].append(node_name)
    trace["graph_path"].append(node_name)

    node_info = {
        "node_name": node_name,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_ms": round(duration_ms, 2),
        "input_summary": input_summary,
        "output_summary": output_summary,
        "decision": decision,
    }
    trace["nodes"].append(node_info)

    # Accumulate component speeds
    if node_name == "retrieve":
        trace["retriever_time_ms"] = round(
            trace.get("retriever_time_ms", 0.0) + duration_ms, 2
        )
    elif node_name == "generate":
        trace["generation_time_ms"] = round(
            trace.get("generation_time_ms", 0.0) + duration_ms, 2
        )
    elif node_name == "verify":
        trace["verification_time_ms"] = round(
            trace.get("verification_time_ms", 0.0) + duration_ms, 2
        )
        trace["retry_count"] = state.get("retry_count", 0)
        trace["confidence"] = state.get("confidence", 0.0)

    state["execution_trace"] = trace
    return state
