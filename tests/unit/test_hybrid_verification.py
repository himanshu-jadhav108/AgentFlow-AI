"""Unit tests verifying the Hybrid Verification Pipeline and Confidence Engine."""

import pytest

from app.verification.confidence import calculate_confidence
from app.verification.hybrid_verifier import HybridVerifier
from app.verification.rule_verifier import RuleVerifier
from app.verification.semantic_verifier import SemanticVerifier
from config.settings import settings


class MockChunk:
    """Mock document chunk representation for test scenarios."""

    def __init__(self, source: str, score: float = 0.85):
        self.source = source
        self.chunk_id = "c1"
        self.text = "Mock support info details."
        self.score = score
        self.confidence_score = score


def test_rule_verifier_valid_payload() -> None:
    """Verify RuleVerifier passes standard correct outputs."""
    verifier = RuleVerifier()
    payload = {
        "answer": "Read-only users cannot create API keys.",
        "citations": ["faq.md"],
        "reason": "Direct lookup match.",
    }
    chunks = [MockChunk("faq.md")]

    res = verifier.verify(payload, chunks, retry_count=0)
    assert res["passed"] is True
    assert len(res["errors"]) == 0


def test_rule_verifier_malformed_schema() -> None:
    """Verify RuleVerifier fails when schema fields are missing or null."""
    verifier = RuleVerifier()

    # Missing field
    res = verifier.verify({"answer": "test"}, [], 0)
    assert res["passed"] is False
    assert any("missing" in err.lower() for err in res["errors"])

    # Null field
    res_null = verifier.verify(
        {"answer": "test", "citations": None, "reason": "test"}, [], 0
    )
    assert res_null["passed"] is False
    assert any("null" in err.lower() for err in res_null["errors"])


def test_rule_verifier_citation_containment() -> None:
    """Verify RuleVerifier ensures cited documents belong to retrieved chunks."""
    verifier = RuleVerifier()
    payload = {
        "answer": "Test answer",
        "citations": ["unretrieved.md"],
        "reason": "Direct match.",
    }
    chunks = [MockChunk("faq.md")]

    res = verifier.verify(payload, chunks, retry_count=0)
    assert res["passed"] is False
    assert any("not retrieved" in err.lower() for err in res["errors"])


def test_rule_verifier_duplicate_citations() -> None:
    """Verify RuleVerifier removes duplicate citations in-place."""
    verifier = RuleVerifier()
    payload = {
        "answer": "Test answer",
        "citations": ["faq.md", "faq.md", "guide.md", "guide.md"],
        "reason": "Direct match.",
    }
    chunks = [MockChunk("faq.md"), MockChunk("guide.md")]

    res = verifier.verify(payload, chunks, retry_count=0)
    assert res["passed"] is True
    # Duplicate entries must be stripped in-place
    assert payload["citations"] == ["faq.md", "guide.md"]


@pytest.mark.asyncio
async def test_semantic_verifier_grounding() -> None:
    """Verify SemanticVerifier executes model prompts to detect support alignment."""
    verifier = SemanticVerifier()
    chunks = [MockChunk("faq.md")]

    # A. Valid answer (mocked to True in conftest.py)
    payload = {
        "answer": "How do I reset my password?",
        "citations": ["faq.md"],
        "reason": "Lookup.",
    }
    res = verifier.verify("How do I reset my password?", payload, chunks)
    assert res["passed"] is True

    # B. Hallucinated answer (mocked to False in conftest.py)
    payload_bad = {
        "answer": "hallucinated answer text",
        "citations": ["faq.md"],
        "reason": "Lookup.",
    }
    res_bad = verifier.verify("Some question?", payload_bad, chunks)
    assert res_bad["passed"] is False


def test_hybrid_verifier_orchestration() -> None:
    """Verify HybridVerifier orchestrates and permits early exits."""
    verifier = HybridVerifier()
    chunks = [MockChunk("faq.md")]

    # 1. Rules fail -> Early Exit (semantic check skipped)
    payload_bad_rules = {
        "answer": "",  # Empty answer fails rule validation
        "citations": ["faq.md"],
        "reason": "Lookup",
    }
    res = verifier.verify("Question?", payload_bad_rules, chunks, retry_count=0)
    assert res["passed"] is False
    assert res["rule_passed"] is False
    assert res["semantic_passed"] is None  # Skipped!

    # 2. Both pass
    payload_good = {
        "answer": "How do I reset my password?",
        "citations": ["faq.md"],
        "reason": "Lookup",
    }
    res_good = verifier.verify("Question?", payload_good, chunks, retry_count=0)
    assert res_good["passed"] is True
    assert res_good["rule_passed"] is True
    assert res_good["semantic_passed"] is True


def test_confidence_engine_weighted_formula() -> None:
    """Verify redesigned weighted confidence engine computations."""
    chunks = [MockChunk("faq.md", 0.90)]

    # Retrieval Sim = 0.90 (0.4 weight = 0.36)
    # Semantic Pass = 1.0 (0.3 weight = 0.30)
    # Source Coverage = 1.0 (0.2 weight = 0.20)
    # Rule Pass = 1.0 (0.1 weight = 0.10)
    # Expected confidence = 0.36 + 0.30 + 0.20 + 0.10 = 0.96
    conf = calculate_confidence(
        retrieved_chunks=chunks,
        citations=["faq.md"],
        rule_passed=True,
        semantic_passed=True,
        answer="Grounded answer.",
    )
    assert abs(conf - 0.96) < 0.001

    # Fails semantic checks
    # Expected confidence = 0.36 + 0.00 + 0.20 + 0.10 = 0.66
    conf_bad = calculate_confidence(
        retrieved_chunks=chunks,
        citations=["faq.md"],
        rule_passed=True,
        semantic_passed=False,
        answer="Grounded answer.",
    )
    assert abs(conf_bad - 0.66) < 0.001
