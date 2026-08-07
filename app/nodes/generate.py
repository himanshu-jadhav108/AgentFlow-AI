"""GENERATE node executing prompt compiles and LLM text generation."""

import time
from app.state.agent_state import AgentState
from app.generation.answer_generator import AnswerGenerator
from core.logger import logger


def generate_node(state: AgentState) -> dict:
    """Invokes prompt formatting and local LLM execution.

    Appends previous retry comments to the prompt if verification failed.

    Args:
        state: Current AgentState.

    Returns:
        dict: State updates containing generated text, citations, and metadata.
    """
    logger.info("--- ENTERING NODE: GENERATE ---")
    question = state.get("question", "")
    selected_chunks = state.get("selected_chunks", [])
    conversation_history = state.get("conversation_history", [])

    meta = state.get("metadata", {}).copy() if state.get("metadata") else {}
    retry_feedback = meta.get("retry_feedback", "")

    # Inject self-correction details if this execution is a retry cycle
    query_to_submit = question
    if retry_feedback:
        logger.info("Generate node: Injecting self-correction feedback into prompt context.")
        query_to_submit = f"{question}\n\n[SYSTEM REVISION]:\n{retry_feedback}"

    start_time = time.time()
    generator = AnswerGenerator()

    try:
        response_data = generator.generate(
            question=query_to_submit,
            retrieved_chunks=selected_chunks,
            conversation_history=conversation_history,
        )

        latency_ms = (time.time() - start_time) * 1000
        from monitoring.metrics import metrics
        metrics.record_generation(latency_ms)
        meta["generation_latency_ms"] = latency_ms

        # Remove the feedback block once consumed
        meta.pop("retry_feedback", None)

        answer = response_data.get("answer", "")
        citations = response_data.get("citations", [])
        reason = response_data.get("reason", "Success")

        logger.info(f"Generate node: Generated response in {latency_ms:.2f}ms.")

        return {
            "answer": answer,
            "sources": citations if citations else state.get("sources", []),
            "metadata": meta,
            "execution_log": [
                f"Generate node: Generated text in {latency_ms:.2f}ms. "
                f"Model Cited: {citations}. Reasoning: {reason}"
            ],
        }

    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        meta["generation_latency_ms"] = latency_ms
        logger.error(f"Generate node: Inference failed: {e}")

        # Return empty fields to allow the verifier node to catch the error
        return {
            "answer": "",
            "sources": [],
            "metadata": meta,
            "execution_log": [f"Generate node: Inference failed after {latency_ms:.2f}ms. Error: {e}"],
        }
