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
    logger.info("--- ENTERING NODE: END ---")
    now_str = datetime.datetime.now().isoformat()

    # Calculate latency if start_time exists
    latency_ms = 0.0
    start_time_str = state.get("timestamps", {}).get("start_time")
    if start_time_str:
        try:
            start_time = datetime.datetime.fromisoformat(start_time_str)
            end_time = datetime.datetime.fromisoformat(now_str)
            latency_ms = (end_time - start_time).total_seconds() * 1000
        except Exception as e:
            logger.error(f"Error calculating total graph latency: {e}")

    logger.info(f"Graph execution completed in {latency_ms:.2f}ms. State finalized.")

    # Copy and update timestamps
    timestamps = state.get("timestamps", {}).copy()
    timestamps.update(
        {
            "end_time": now_str,
            "latency_ms": str(latency_ms),
        }
    )

    return {
        "timestamps": timestamps,
        "execution_log": [f"Finalized state in END node. Uptime: {latency_ms:.2f}ms."],
    }
