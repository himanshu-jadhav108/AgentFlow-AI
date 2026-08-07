"""Deterministic rule-based validation engine for support agent answers."""

import time
from typing import Any, Dict, List

from core.logger import logger


class RuleVerifier:
    """Validator that performs sub-millisecond, deterministic rule checks."""

    def verify(
        self,
        answer_payload: Dict[str, Any],
        retrieved_chunks: List[Any],
        retry_count: int,
    ) -> Dict[str, Any]:
        """Runs rule checks on the model output without invoking an LLM.

        Args:
            answer_payload: Decoded response dictionary (answer, citations, reason).
            retrieved_chunks: List of RetrievedChunk instances.
            retry_count: The current graph retry execution count.

        Returns:
            Dict[str, Any]: Verification outcome details (passed, errors, latency_ms).
        """
        start_time = time.time()
        errors = []

        logger.info("RuleVerifier: Initiating fast deterministic validations...")

        # 1. Type check
        if not isinstance(answer_payload, dict):
            errors.append("Model output is not structured as a dictionary.")
            latency = (time.time() - start_time) * 1000
            return {"passed": False, "errors": errors, "latency_ms": latency}

        # 2. Schema check: required fields must be present and not null
        required_fields = ["answer", "citations", "reason"]
        for field in required_fields:
            if field not in answer_payload:
                errors.append(f"Required schema field '{field}' is missing.")
            elif answer_payload[field] is None:
                errors.append(f"Required schema field '{field}' is null.")

        if errors:
            latency = (time.time() - start_time) * 1000
            return {"passed": False, "errors": errors, "latency_ms": latency}

        # Extract values
        answer = str(answer_payload["answer"]).strip()
        citations = answer_payload["citations"]
        reason = str(answer_payload["reason"]).strip()

        # 3. Answer exists check
        if not answer:
            errors.append("The generated answer string is empty.")

        # 4. Length limits check
        elif len(answer) > 3000:
            errors.append(
                f"Answer length ({len(answer)} characters) exceeds the 3000 limit."
            )

        # 5. Citations type check
        if not isinstance(citations, list):
            errors.append("Citations field must be a list of strings.")
            citations = []

        # 6. Deduplicate citations list
        deduped = []
        for cite in citations:
            cite_str = str(cite).strip()
            if cite_str and cite_str not in deduped:
                deduped.append(cite_str)

        # Mutate the payload in-place to remove duplicates
        answer_payload["citations"] = deduped
        citations = deduped

        # 7. Grounding/Source citation checks
        refusal_phrase = "couldn't find supporting information"
        is_refusal = refusal_phrase in answer.lower()

        if not is_refusal:
            # Answer is stating facts, so at least one citation must exist
            if not citations:
                errors.append(
                    "Answer contains claims but does not cite any document sources."
                )
            else:
                # Ensure all cited documents belong to retrieved contexts
                retrieved_sources = set(
                    getattr(c, "source", "")
                    for c in retrieved_chunks
                    if getattr(c, "source", "")
                )
                for cite in citations:
                    # Check substring containment case-insensitively
                    if not any(
                        cite.lower() in src.lower() for src in retrieved_sources
                    ):
                        errors.append(
                            f"Cited source document '{cite}' was not retrieved in search context."
                        )

        # 8. Validate retry parameters
        if retry_count < 0:
            errors.append(f"Invalid retry count: {retry_count}")

        passed = len(errors) == 0
        latency_ms = (time.time() - start_time) * 1000

        logger.info(
            f"RuleVerifier completed in {latency_ms:.2f}ms. Passed: {passed}. "
            f"Errors identified: {errors}"
        )

        return {
            "passed": passed,
            "errors": errors,
            "latency_ms": latency_ms,
        }
