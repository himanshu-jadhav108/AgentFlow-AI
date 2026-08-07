"""Hybrid verification manager orchestrating rules and semantic validators."""

import time
from typing import Any, Dict, List

from app.verification.rule_verifier import RuleVerifier
from app.verification.semantic_verifier import SemanticVerifier
from config.settings import settings
from core.logger import logger


class HybridVerifier:
    """Orchestrator managing sequence control flows over all verifier modules."""

    def __init__(self) -> None:
        self.rule_verifier = RuleVerifier()
        self.semantic_verifier = SemanticVerifier()

    def verify(
        self,
        question: str,
        answer_payload: Dict[str, Any],
        retrieved_chunks: List[Any],
        retry_count: int,
    ) -> Dict[str, Any]:
        """Runs rule checks followed by semantic checks based on configuration toggles.

        Supports early exit if rule validation fails.

        Args:
            question: Original query message.
            answer_payload: Generated answer dict.
            retrieved_chunks: List of RetrievedChunk instances.
            retry_count: Current retry count.

        Returns:
            Dict[str, Any]: Consolidated verification results.
        """
        start_time = time.time()

        # Load config toggles supporting both naming variants
        rule_enabled = (
            settings.ENABLE_RULE_VERIFICATION and settings.RULE_VALIDATION_ENABLED
        )
        semantic_enabled = (
            settings.ENABLE_SEMANTIC_VERIFICATION
            and settings.SEMANTIC_VALIDATION_ENABLED
        )

        logger.info(
            f"HybridVerifier: Starting. Config rules-enabled={rule_enabled}, "
            f"semantic-enabled={semantic_enabled}"
        )

        failures = []
        rule_passed = True
        semantic_passed = True

        # 1. Run Rule Verification
        if rule_enabled:
            rule_res = self.rule_verifier.verify(
                answer_payload=answer_payload,
                retrieved_chunks=retrieved_chunks,
                retry_count=retry_count,
            )
            rule_passed = rule_res.get("passed", False)

            if not rule_passed:
                failures.extend(rule_res.get("errors", ["Rule verification failed."]))
                latency_ms = (time.time() - start_time) * 1000
                reason_str = " | ".join(failures)

                logger.warning(
                    f"HybridVerifier: Rule checks failed. Triggering early exit. "
                    f"Latency: {latency_ms:.2f}ms. Reasons: {reason_str}"
                )

                return {
                    "passed": False,
                    "reason": reason_str,
                    "rule_passed": False,
                    "semantic_passed": None,
                    "latency_ms": latency_ms,
                }

        # 2. Run Semantic Grounding Verification (only if rule check succeeded)
        if semantic_enabled:
            semantic_res = self.semantic_verifier.verify(
                question=question,
                answer_payload=answer_payload,
                retrieved_chunks=retrieved_chunks,
            )
            semantic_passed = semantic_res.get("passed", False)

            if not semantic_passed:
                failures.append(
                    semantic_res.get("reason", "Semantic verification failed.")
                )

        passed = rule_passed and semantic_passed
        latency_ms = (time.time() - start_time) * 1000

        reason_str = (
            " | ".join(failures)
            if failures
            else "Grounding verification passed successfully."
        )

        logger.info(
            f"HybridVerifier: Execution finished in {latency_ms:.2f}ms. Passed: {passed}. "
            f"Diagnostic comments: '{reason_str}'"
        )

        return {
            "passed": passed,
            "reason": reason_str,
            "rule_passed": rule_passed,
            "semantic_passed": semantic_passed,
            "latency_ms": latency_ms,
        }
