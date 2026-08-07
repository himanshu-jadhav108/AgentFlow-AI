"""VERIFY node evaluating answer correctness and computing confidence."""

from app.state.agent_state import AgentState
from app.verification.verifier import verify_answer
from app.verification.confidence import calculate_confidence
from app.verification.retry import get_retry_feedback
from core.logger import logger


def verify_node(state: AgentState) -> dict:
    """Verifies that the generated answer matches factual document chunks.

    Applies the weighted confidence score formula and increments retry counts.

    Args:
        state: Current AgentState.

    Returns:
        dict: State updates containing verification status, retry count, and confidence.
    """
    logger.info("--- ENTERING NODE: VERIFY ---")

    question = state.get("question", "")
    answer = state.get("answer", "")
    sources = state.get("sources", [])
    selected_chunks = state.get("selected_chunks", [])
    retry_count = state.get("retry_count", 0)

    # Compile dataset for validator
    answer_payload = {
        "answer": answer,
        "citations": sources,
    }

    # Execute dual-layer verification check
    verif_data = verify_answer(answer_payload, selected_chunks)
    supported = verif_data.get("supported", False)
    reason = verif_data.get("reason", "Verification complete.")

    meta = state.get("metadata", {}).copy() if state.get("metadata") else {}
    meta["verification_reason"] = reason

    if supported:
        verification_status = "verified"
        log_msg = f"Verify node: Answer verified successfully. Reason: {reason}"
    else:
        verification_status = "hallucinated"
        retry_count += 1

        # Formulate self-correction feedback for the next model iteration
        feedback = get_retry_feedback(question, answer, reason)
        meta["retry_feedback"] = feedback
        log_msg = f"Verify node: Verification failed (Cycle #{retry_count}). Reason: {reason}"

    # Compute deterministic confidence score
    confidence = calculate_confidence(
        retrieved_chunks=selected_chunks,
        citations=sources,
        is_verified=supported,
        answer=answer,
    )

    # Check for fail-safe trigger (stop retrying and output a clean refusal)
    max_retries = state.get("max_retries", 3)
    if not supported and retry_count >= max_retries:
        logger.error(f"Verify node: Maximum retry limit ({max_retries}) reached. Activating fail-safe.")
        log_msg += " | Max retries reached. Triggering fail-safe."
        # Update answer to the fail-safe refusal string
        answer = "I could not verify the answer using available documentation."
        # Update verification status to verified to exit the loop
        verification_status = "verified"

    return {
        "answer": answer,
        "verification_status": verification_status,
        "retry_count": retry_count,
        "confidence": confidence,
        "metadata": meta,
        "execution_log": [log_msg],
    }
