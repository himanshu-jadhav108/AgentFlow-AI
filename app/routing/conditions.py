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

    In Phase 4, we direct the flow to the 'generate' node to compile the answer.

    Args:
        state: Current AgentState.

    Returns:
        str: Name of the target node.
    """
    logger.info("Routing edge after retrieve. Directing to 'generate' node.")
    return "generate"


def route_after_verify(state: AgentState) -> str:
    """Evaluates state after verification.

    Branches back to 'generate' if verification failed and the retry limit
    has not been exceeded. Otherwise, terminates by routing to 'end'.

    Args:
        state: Current AgentState.

    Returns:
        str: Name of the next node ('generate' or 'end').
    """
    verification_status = state.get("verification_status", "unverified")
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 3)

    logger.info(
        f"Routing edge after verify. Status: '{verification_status}' | "
        f"Retry Count: {retry_count}/{max_retries}"
    )

    if verification_status == "verified":
        return "end"
    elif verification_status == "hallucinated":
        if retry_count < max_retries:
            logger.info("Factual verification failed. Retrying answer generation.")
            return "generate"
        else:
            logger.warning("Factual verification failed and max retries reached. Routing to end.")
            return "end"
    else:
        logger.warning(f"Unknown verification status '{verification_status}'. Routing to end.")
        return "end"
