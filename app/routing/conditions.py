"""Conditional routing rules for LangGraph transitions."""

from app.state.agent_state import AgentState
from core.logger import logger


def route_after_triage(state: AgentState) -> str:
    """Evaluates the classification of the triage node and determines the next node.

    Args:
        state: Current AgentState.

    Returns:
        str: Name of the target node to transition to.
    """
    classification = state.get("classification", "clarification")
    logger.info(f"Routing edge after triage. Classification: '{classification}'")

    if classification == "clarification":
        return "clarification"
    elif classification == "escalate":
        return "escalation"
    elif classification == "out_of_scope":
        return "out_of_scope"
    elif classification == "answerable":
        return "retrieve"
    else:
        logger.warning(f"Unknown classification '{classification}'. Routing to clarification.")
        return "clarification"


def route_after_retrieve(state: AgentState) -> str:
    """Evaluates state after chunk retrieval and determines next steps.

    Currently redirects directly to 'end' as Generation and Verification nodes
    will be integrated in Phase 4.

    Args:
        state: Current AgentState.

    Returns:
        str: Name of the target node.
    """
    logger.info("Routing edge after retrieve. Directing to 'end' node (Generation deferred to Phase 4).")
    return "end"
