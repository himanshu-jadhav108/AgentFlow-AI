"""Escalation node implementation for human support routing."""

from app.state.agent_state import AgentState
from core.logger import logger


def escalation_node(state: AgentState) -> dict:
    """Escalation node. Routes complex, sensitive, or high-risk cases to human agents.

    Sets requires_human flag and stores escalation details in the metadata.

    Args:
        state: Current AgentState.

    Returns:
        dict: State updates routing the case to a human.
    """
    import time
    from app.core.trace import record_node_trace

    start_time = time.time()
    logger.info("--- ENTERING NODE: ESCALATION ---")

    # Retrieve priority from metadata (defaulting to 3 if not present)
    meta = state.get("metadata", {}).copy() if state.get("metadata") else {}
    priority = meta.get("priority", 3)
    reason = meta.get("triage_reason", "Escalated by workflow rule.")

    escalation_msg = (
        f"This request has been escalated to a human support representative (Priority {priority}). "
        f"Reason: {reason}"
    )

    logger.warning(f"Case escalated. Priority: {priority} | Reason: {reason}")

    # Update metadata to track escalation state
    meta.update(
        {
            "escalation_priority": priority,
            "escalation_reason": reason,
            "escalated": True,
        }
    )

    updates = {
        "requires_human": True,
        "answer": escalation_msg,
        "metadata": meta,
        "execution_log": [f"Escalation node: Escalated to human. Reason: {reason}"],
    }

    record_node_trace(
        state=state,
        node_name="escalation",
        start_time=start_time,
        input_summary=f"Escalation reason: {reason}",
        output_summary=f"Escalated (Priority {priority}).",
        decision="end",
    )
    updates["execution_trace"] = state["execution_trace"]
    return updates
