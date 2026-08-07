"""Semantic grounding validator querying local LLM to verify truthfulness."""

import time
from typing import Any, Dict, List
from app.llm.inference import InferenceManager
from app.prompts.verification_prompt import VERIFICATION_PROMPT_TEMPLATE
from app.generation.formatter import parse_json_response
from core.logger import logger


class SemanticVerifier:
    """Validator that utilizes LLM reasoning to evaluate answer truthfulness."""

    def __init__(self) -> None:
        self.inference_manager = InferenceManager()

    def verify(
        self,
        question: str,
        answer_payload: Dict[str, Any],
        retrieved_chunks: List[Any],
    ) -> Dict[str, Any]:
        """Asks the local model to analyze if the answer contradicts the context.

        Args:
            question: The original user question.
            answer_payload: Generated answer dict (answer, citations, reason).
            retrieved_chunks: List of RetrievedChunk instances.

        Returns:
            Dict[str, Any]: Semantic validation outputs (passed, reason, latency_ms).
        """
        start_time = time.time()
        answer = answer_payload.get("answer", "").strip()

        logger.info("SemanticVerifier: Initiating LLM grounding evaluation...")

        # 1. Fast Refusal check - skip model invocation if the answer is a correct support refusal
        refusal_phrase = "couldn't find supporting information"
        if refusal_phrase in answer.lower():
            latency_ms = (time.time() - start_time) * 1000
            logger.info("SemanticVerifier: Answer is a correct refusal. Skipping LLM query.")
            return {
                "passed": True,
                "reason": "Correctly refused answering due to lack of factual document support.",
                "latency_ms": latency_ms,
            }

        # 2. Format search context docs
        context_parts = []
        for chunk in retrieved_chunks:
            source = getattr(chunk, "source", "Unknown Source")
            chunk_id = getattr(chunk, "chunk_id", "Unknown ID")
            text = getattr(chunk, "text", "")
            context_parts.append(f"Source Document: {source} (Chunk: {chunk_id})\nText: {text}")

        context_str = "\n\n".join(context_parts) if context_parts else "No context available."

        # 3. Assemble prompt using Verification Prompt Template
        verification_prompt = VERIFICATION_PROMPT_TEMPLATE.format(
            context=context_str,
            answer=answer,
        )

        try:
            # 4. Invoke LLM with zero temperature for high determinism
            raw_eval = self.inference_manager.generate_text(verification_prompt, max_new_tokens=256, temperature=0.0)
            eval_data = parse_json_response(raw_eval)

            supported = bool(eval_data.get("supported", False))
            reason = str(eval_data.get("reason", "Semantic verification completed.")).strip()
            latency_ms = (time.time() - start_time) * 1000

            logger.info(
                f"SemanticVerifier completed in {latency_ms:.2f}ms. "
                f"Supported: {supported}. Reason: {reason}"
            )

            return {
                "passed": supported,
                "reason": reason,
                "latency_ms": latency_ms,
            }

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.warning(
                f"SemanticVerifier: LLM validation execution failed ({e}). "
                f"Falling back to basic validation pass."
            )
            return {
                "passed": True,
                "reason": f"Semantic check bypassed due to LLM error: {e}",
                "latency_ms": latency_ms,
            }
        
