"""VERIFY node evaluating answer correctness using a hybrid pipeline."""

import time

from app.state.agent_state import AgentState
from app.verification.confidence import calculate_confidence
from app.verification.hybrid_verifier import HybridVerifier
from app.verification.retry import get_retry_feedback
from core.logger import logger


def verify_node(state: AgentState) -> dict:
    """Verifies that the generated answer matches factual document chunks.

    Applies deterministic rule validation followed by semantic model verification.
    Computes a weighted grounding confidence score and handles loops.

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
        "reason": state.get("metadata", {}).get(
            "triage_reason", "Processed successfully."
        ),
    }

    # Execute Hybrid Verification Pipeline
    verifier = HybridVerifier()
    res = verifier.verify(
        question=question,
        answer_payload=answer_payload,
        retrieved_chunks=selected_chunks,
        retry_count=retry_count,
    )

    passed = res.get("passed", False)
    reason = res.get("reason", "Verification complete.")
    rule_passed = res.get("rule_passed", False)
    semantic_passed = res.get("semantic_passed", False)
    latency_ms = res.get("latency_ms", 0.0)

    meta = state.get("metadata", {}).copy() if state.get("metadata") else {}
    meta["verification_reason"] = reason
    meta["verification_latency_ms"] = latency_ms

    if passed:
        verification_status = "verified"
        log_msg = f"Verify node: Answer verified successfully. Reason: {reason}"
    else:
        verification_status = "hallucinated"
        retry_count += 1

        # Formulate self-correction feedback for the next model iteration
        feedback = get_retry_feedback(question, answer, reason)
        meta["retry_feedback"] = feedback
        log_msg = (
            f"Verify node: Verification failed (Cycle #{retry_count}). Reason: {reason}"
        )

    # Compute deterministic weighted confidence score
    confidence = calculate_confidence(
        retrieved_chunks=selected_chunks,
        citations=sources,
        rule_passed=rule_passed,
        semantic_passed=bool(semantic_passed),
        answer=answer,
    )

    # Check for fail-safe trigger (stop retrying and output a clean refusal)
    max_retries = state.get("max_retries", 3)
    if not passed and retry_count >= max_retries:
        logger.error(
            f"Verify node: Maximum retry limit ({max_retries}) reached. Activating fail-safe."
        )
        log_msg += " | Max retries reached. Triggering fail-safe."
        answer = "I could not verify the answer using available documentation."
        verification_status = "verified"

    # Record metrics
    from monitoring.metrics import metrics

    metrics.record_verification(latency_ms)
    metrics.record_retries(1 if not passed else 0)

    return {
        "answer": answer,
        "verification_status": verification_status,
        "retry_count": retry_count,
        "confidence": confidence,
        "metadata": meta,
        "execution_log": [log_msg],
    }
