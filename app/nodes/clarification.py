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
    logger.info("--- ENTERING NODE: CLARIFICATION ---")

    clarification_msg = (
        "I need more information before I can answer. "
        "Could you please clarify your request by specifying which product, role, or feature you are referring to?"
    )

    logger.info("Generated clarification message.")

    return {
        "answer": clarification_msg,
        "confidence": 0.0,
        "execution_log": ["Clarification node: Requested query details from user."],
    }
