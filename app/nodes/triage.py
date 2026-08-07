"""Triage node implementation for initial query classification."""

from app.state.agent_state import AgentState
from core.logger import logger


def triage_node(state: AgentState) -> dict:
    """Intelligent triage node. Classifies the query using rule-based constraints.

    Provides paths for clarification, out-of-scope queries, sensitive escalations,
    and valid answerable documentation searches.

    Args:
        state: Current AgentState.

    Returns:
        dict: State updates containing classification and triage metadata.
    """
    logger.info("--- ENTERING NODE: TRIAGE ---")
    question = state.get("question", "").strip()

    # Default fallback
    classification = "answerable"
    reason = "Valid support query matching system domain."
    priority = 1

    # Token/word check
    words = [w for w in question.split() if w]

    # 1. Clarification rules: empty, extremely short, or missing context
    if not question:
        classification = "clarification"
        reason = "Empty search query provided."
    elif len(words) < 3:
        classification = "clarification"
        reason = "Question is too short to establish context (less than 3 words)."

    # 2. Sensitive Escalation rules: security risks, legal threats, credit card leaks
    else:
        sensitive_keywords = [
            "hack",
            "exploit",
            "leak",
            "legal",
            "court",
            "credit card",
            "compromised",
            "security breach",
            "billing fraud",
            "payment failed",
        ]
        for kw in sensitive_keywords:
            if kw in question.lower():
                classification = "escalate"
                reason = f"Security or transaction keyword detected: '{kw}'."
                priority = 5  # Highest priority escalation
                break

        # 3. Out of Scope rules: off-topic general questions
        if classification == "answerable":
            off_topic_keywords = [
                "weather",
                "recipe",
                "pizza",
                "cook",
                "movie",
                "song",
                "joke",
                "game",
                "sports",
                "music",
            ]
            for kw in off_topic_keywords:
                if kw in question.lower():
                    classification = "out_of_scope"
                    reason = f"General query classified as off-topic: '{kw}'."
                    break

    logger.info(f"Triage classification results: '{classification}' | Reason: {reason}")

    # Copy and update metadata dictionary
    meta = state.get("metadata", {}).copy() if state.get("metadata") else {}
    meta.update({
        "triage_reason": reason,
        "priority": priority,
    })

    return {
        "classification": classification,
        "metadata": meta,
        "execution_log": [f"Triage node: Classified query as '{classification}'. Reason: {reason}"],
    }
