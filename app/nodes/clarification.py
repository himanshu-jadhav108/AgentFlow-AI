"""Clarification node implementation for handling ambiguous queries."""

from app.state.agent_state import AgentState
from core.logger import logger


def clarification_node(state: AgentState) -> dict:
    """Clarification node. Formulates a response asking the user to clarify their question.

    Args:
        state: Current AgentState.

    Returns:
        dict: State updates containing the clarification answer.
    """
    import time
    from app.core.trace import record_node_trace

    start_time = time.time()
    logger.info("--- ENTERING NODE: CLARIFICATION ---")

    clarification_msg = (
        "I need more information before I can answer. "
        "Could you please clarify your request by specifying which product, role, or feature you are referring to?"
    )

    logger.info("Generated clarification message.")

    updates = {
        "answer": clarification_msg,
        "confidence": 0.0,
        "execution_log": ["Clarification node: Requested query details from user."],
    }

    record_node_trace(
        state=state,
        node_name="clarification",
        start_time=start_time,
        input_summary=f"Question: {state.get('question')}",
        output_summary="Clarification request generated.",
        decision="end",
    )
    updates["execution_trace"] = state["execution_trace"]
    return updates
