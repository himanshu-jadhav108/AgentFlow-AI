"""Out of scope node implementation for off-topic queries."""

from app.state.agent_state import AgentState
from core.logger import logger


def out_of_scope_node(state: AgentState) -> dict:
    """Out-of-scope node. Handles queries categorized as off-topic or out-of-bounds.

    Args:
        state: Current AgentState.

    Returns:
        dict: State updates containing the out-of-scope answer.
    """
    logger.info("--- ENTERING NODE: OUT OF SCOPE ---")

    reason = state.get("metadata", {}).get("triage_reason", "Off-topic query.")
    out_of_scope_msg = (
        "I'm sorry, but this question is out of scope for our customer support database. "
        "Please ask questions related to roles, passwords, API credentials, or platforms."
    )

    logger.info(f"Query out of scope. Reason: {reason}")

    return {
        "answer": out_of_scope_msg,
        "confidence": 0.0,
        "execution_log": [
            f"Out-of-Scope node: Off-topic query handled. Reason: {reason}"
        ],
    }
