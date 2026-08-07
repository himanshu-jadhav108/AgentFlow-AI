"""START node implementation for graph initialization."""

import datetime

from app.state.agent_state import AgentState
from core.logger import logger


def start_node(state: AgentState) -> dict:
    """Sentinel START node. Sets up initial timestamps and default state keys.

    Args:
        state: Current AgentState.

    Returns:
        dict: State updates containing initialization values.
    """
    import time
    from app.core.trace import init_execution_trace, record_node_trace

    start_time = time.time()
    logger.info("--- ENTERING NODE: START ---")
    now_str = datetime.datetime.now().isoformat()

    metadata = state.get("metadata") or {}
    request_id = metadata.get("request_id", f"req-{int(start_time)}")
    trace = init_execution_trace(request_id, state.get("question", ""))

    updates = {
        "execution_log": ["Initialized state in START node."],
        "timestamps": {"start_time": now_str},
        "retry_count": 0,
        "max_retries": 3,
        "requires_human": False,
        "confidence": 0.0,
        "verification_status": "unverified",
        "execution_trace": trace,
    }

    record_node_trace(
        state=updates,
        node_name="start",
        start_time=start_time,
        input_summary=f"Question: {state.get('question')}",
        output_summary="Initialized state trace.",
        decision="triage",
    )
    return updates
