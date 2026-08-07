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
    logger.info("--- ENTERING NODE: START ---")
    now_str = datetime.datetime.now().isoformat()

    return {
        "execution_log": ["Initialized state in START node."],
        "timestamps": {"start_time": now_str},
        "retry_count": 0,
        "max_retries": 3,
        "requires_human": False,
        "confidence": 0.0,
        "verification_status": "unverified",
    }
