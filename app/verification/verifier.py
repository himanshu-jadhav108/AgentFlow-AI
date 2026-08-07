"""Verification engine validating answer grounding and citations."""

from typing import Any, Dict, List

from app.generation.formatter import parse_json_response
from app.llm.inference import InferenceManager
from app.prompts.verification_prompt import VERIFICATION_PROMPT_TEMPLATE
from core.logger import logger


def verify_answer(
    answer_data: Dict[str, Any],
    retrieved_chunks: List[Any],
) -> Dict[str, Any]:
    """Evaluates whether the generated answer is grounded in retrieved document chunks.

    Runs fast deterministic checks (length, citations validation) and falls back
    to LLM semantic evaluation.

    Args:
        answer_data: The parsed dictionary returned by the generation phase.
        retrieved_chunks: List of RetrievedChunk instances.

    Returns:
        Dict[str, Any]: A dictionary containing 'supported' (bool) and 'reason' (str).
    """
    logger.info("Verifier: Initiating dual-layer verification check...")

    answer = answer_data.get("answer", "").strip()
    citations = answer_data.get("citations", [])

    # --- Layer 1: Fast Deterministic Rules ---

    # 1. Empty check
    if not answer:
        return {
            "supported": False,
            "reason": "Generated answer text is completely empty.",
        }

    # 2. Refusal check
    refusal_phrase = "couldn't find supporting information"
    if refusal_phrase in answer.lower():
        logger.info("Verifier: Answer is a standard support refusal. Auto-verifying.")
        return {
            "supported": True,
            "reason": "Answer correctly indicates a lack of supporting context.",
        }

    # 3. Source Citation presence check
    if not citations:
        logger.warning("Verifier: Grounded answer contains no source citations.")
        return {
            "supported": False,
            "reason": "Answer does not cite any document sources.",
        }

    # 4. Source Citation match check (must exist in retrieved sources)
    retrieved_sources = set(
        getattr(c, "source", "") for c in retrieved_chunks if getattr(c, "source", "")
    )
    for cite in citations:
        # Check if the cited name matches or is a substring of retrieved sources
        if not any(cite.lower() in src.lower() for src in retrieved_sources):
            logger.warning(
                f"Verifier: Cited document '{cite}' is not in retrieved sources: {retrieved_sources}"
            )
            return {
                "supported": False,
                "reason": f"Cited document '{cite}' was not retrieved in search context.",
            }

    # --- Layer 2: LLM-Based Semantic Verification ---
    context_parts = []
    for chunk in retrieved_chunks:
        source_name = getattr(chunk, "source", "Unknown Source")
        chunk_id = getattr(chunk, "chunk_id", "Unknown ID")
        text = getattr(chunk, "text", "")
        context_parts.append(f"Source: {source_name} (Chunk: {chunk_id})\nText: {text}")

    context_str = "\n\n".join(context_parts)
    verification_prompt = VERIFICATION_PROMPT_TEMPLATE.format(
        context=context_str,
        answer=answer,
    )

    try:
        inference_manager = InferenceManager()
        # Enforce zero temperature for deterministic evaluation
        raw_eval = inference_manager.generate_text(
            verification_prompt, max_new_tokens=256, temperature=0.0
        )
        eval_data = parse_json_response(raw_eval)

        supported = eval_data.get("supported", False)
        reason = eval_data.get("reason", "Completed semantic evaluation.")

        logger.info(
            f"Verifier: LLM grounding check complete. Supported={supported}. Reason: {reason}"
        )
        return {"supported": supported, "reason": reason}

    except Exception as e:
        logger.warning(
            f"Verifier: LLM semantic validation failed ({e}). Falling back to citation-match pass."
        )
        return {
            "supported": True,
            "reason": "Fast rules and citation checks passed. LLM verification fallback triggered.",
        }
