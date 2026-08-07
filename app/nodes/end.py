"""END node implementation for final wrap up operations."""

import datetime

from app.state.agent_state import AgentState
from core.logger import logger


def end_node(state: AgentState) -> dict:
    """Sentinel END node. Calculates execution latencies and logs final stats.

    Args:
        state: Current AgentState.

    Returns:
        dict: State updates detailing latency and final trace log.
    """
    import time
    from app.core.trace import record_node_trace

    node_start_time = time.time()
    logger.info("--- ENTERING NODE: END ---")
    now_str = datetime.datetime.now().isoformat()

    # Calculate latency if start_time exists
    latency_ms = 0.0
    start_time_str = state.get("timestamps", {}).get("start_time")
    if start_time_str:
        try:
            start_datetime = datetime.datetime.fromisoformat(start_time_str)
            end_datetime = datetime.datetime.fromisoformat(now_str)
            latency_ms = (end_datetime - start_datetime).total_seconds() * 1000
        except Exception as e:
            logger.error(f"Error calculating total graph latency: {e}")

    logger.info(f"Graph execution completed in {latency_ms:.2f}ms. State finalized.")

    # Update total execution time in trace
    trace = state.get("execution_trace")
    if trace:
        trace["total_execution_time_ms"] = round(latency_ms, 2)
        trace["final_decision"] = state.get("classification", "unknown")

    # Copy and update timestamps
    timestamps = state.get("timestamps", {}).copy()
    timestamps.update(
        {
            "end_time": now_str,
            "latency_ms": str(latency_ms),
        }
    )

    updates = {
        "timestamps": timestamps,
        "execution_log": [f"Finalized state in END node. Uptime: {latency_ms:.2f}ms."],
    }

    record_node_trace(
        state=state,
        node_name="end",
        start_time=node_start_time,
        input_summary=f"Final classification: {state.get('classification', 'unknown')}",
        output_summary=f"Finalized workflow. Latency: {latency_ms:.2f}ms",
        decision="none",
    )
    updates["execution_trace"] = state["execution_trace"]
    return updates
