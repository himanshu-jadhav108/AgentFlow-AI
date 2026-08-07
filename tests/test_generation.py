"""Unit and integration tests for LLM loading, generation, and verification loops."""

from typing import Any, Dict, List
import pytest
from app.generation.answer_generator import AnswerGenerator
from app.generation.formatter import parse_json_response
from app.llm.inference import InferenceManager
from app.llm.model_loader import ModelLoader
from app.prompts.generation_prompt import GENERATION_PROMPT_TEMPLATE
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.verification.confidence import calculate_confidence
from app.verification.verifier import verify_answer
from app.state.agent_state import AgentState
from app.graph.builder import build_graph


def test_model_loader_singleton() -> None:
    """Verify that ModelLoader behaves as a singleton and loads once."""
    loader1 = ModelLoader()
    loader2 = ModelLoader()
    assert loader1 is loader2

    model1 = loader1.load_model()
    model2 = loader2.load_model()
    assert model1 is model2
    assert loader1.device == "cpu"  # Mocked to CPU in conftest.py


def test_json_formatter() -> None:
    """Test extracting JSON from raw text containing Markdown formats or extra content."""
    raw_markdown = "Here is the result:\n```json\n{\"answer\": \"Hello\", \"citations\": [\"faq.md\"]}\n```"
    parsed = parse_json_response(raw_markdown)
    assert parsed["answer"] == "Hello"
    assert parsed["citations"] == ["faq.md"]

    raw_raw = "{\"answer\": \"Hi\", \"citations\": [\"data.md\"]}"
    parsed_raw = parse_json_response(raw_raw)
    assert parsed_raw["answer"] == "Hi"

    with pytest.raises(ValueError):
        parse_json_response("This is not JSON at all.")


def test_confidence_scoring() -> None:
    """Test deterministic confidence score calculations."""
    class MockChunk:
        def __init__(self, source: str, score: float):
            self.source = source
            self.score = score
            self.confidence_score = score

    retrieved = [MockChunk("faq.md", 0.90), MockChunk("guide.md", 0.80)]

    # 1. Verified and fully aligned citations:
    # Retrieval Sim = 0.85 (0.425 weight)
    # Agreement = 1.0 (0.3 weight)
    # Verification = 1.0 (0.2 weight)
    # Expected confidence = 0.925
    # Note: calculate_confidence now uses default weights: 0.4, 0.3, 0.2, 0.1
    # 0.4 * 0.85 + 0.3 * 1.0 + 0.2 * 1.0 + 0.1 * 1.0 = 0.34 + 0.3 + 0.2 + 0.1 = 0.94
    conf = calculate_confidence(retrieved, ["faq.md", "guide.md"], True, True, "Here is the answer.")
    assert abs(conf - 0.94) < 0.001

    # 2. Refusal message confidence
    # Expected confidence = (0.85 * 0.4) + (0.3 * 1.0) + (0.2 * 1.0) + (0.1 * 1.0) = 0.94
    refusal_conf = calculate_confidence(
        retrieved, [], True, True, "I couldn't find supporting information."
    )
    assert abs(refusal_conf - 0.94) < 0.001

    # 3. Unverified response citation mismatch
    # Expected confidence = (0.85 * 0.4) + (0.3 * 0.0) + (0.2 * 0.5) + (0.1 * 1.0) = 0.34 + 0.0 + 0.10 + 0.10 = 0.54
    bad_conf = calculate_confidence(retrieved, ["faq.md", "bad.md"], True, False, "Ungrounded answer.")
    assert abs(bad_conf - 0.54) < 0.001


def test_verifier_grounding() -> None:
    """Test answer verification rules."""
    class MockChunk:
        def __init__(self, source: str):
            self.source = source
            self.chunk_id = "c1"
            self.text = "Mock context text."

    chunks = [MockChunk("faq.md")]

    # A. Passes citation check and verified via mock LLM
    res = verify_answer({"answer": "How do I reset my password?", "citations": ["faq.md"]}, chunks)
    assert res["supported"] is True

    # B. Fails on citations mismatch (cited source not retrieved)
    res_bad = verify_answer({"answer": "Some text", "citations": ["missing.md"]}, chunks)
    assert res_bad["supported"] is False
    assert "not retrieved" in res_bad["reason"].lower()

    # C. Refusal auto-passes
    res_refuse = verify_answer({"answer": "I couldn't find supporting information.", "citations": []}, chunks)
    assert res_refuse["supported"] is True


@pytest.mark.asyncio
async def test_retry_loop_hallucination() -> None:
    """Verify that the LangGraph workflow triggers a retry loop when verification flags a hallucination."""
    graph = build_graph()
    
    # We query using a keyword designed to return supported: false in our mock tokenizer (see conftest.py)
    # "hallucinated answer" in prompt -> supported: false
    initial_state: AgentState = {
        "question": "generate hallucinated answer password reset",
        "conversation_history": [],
        "retrieved_documents": [],
        "selected_chunks": [],
        "answer": None,
        "confidence": 0.0,
        "sources": [],
        "requires_human": False,
        "retry_count": 0,
        "max_retries": 2, # Force exit fail-safe fast
        "verification_status": "unverified",
        "metadata": {},
        "execution_log": [],
        "timestamps": {},
    }

    final_state = await graph.ainvoke(initial_state)

    # Check that retry mechanism successfully executed:
    # 1. Verification status is marked verified at the end because of fail-safe trigger
    # 2. Retry count is equal to max_retries (2)
    # 3. Answer is updated to the clean fail-safe refusal string
    assert final_state["retry_count"] >= 2
    assert "could not verify the answer" in final_state["answer"].lower()
    
    # Assert nodes are registered in log
    logs = final_state["execution_log"]
    assert any("generate" in log.lower() for log in logs)
    assert any("verify" in log.lower() for log in logs)


def test_api_ask_endpoint(client) -> None:
    """Integration test for POST /ask endpoint."""
    # Ensure FAISS index seeded
    client.post("/index")

    # A. Valid answerable question
    payload = {"question": "How do I reset my password?"}
    response = client.post("/ask", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["classification"] == "answerable"
    assert "password" in data["answer"].lower()
    assert data["confidence"] > 0.0
    assert "faq.md" in data["sources"]
    assert data["requires_human"] is False

    # B. Off-topic query refusal
    refusal_payload = {"question": "Can you give me a pepperoni pizza recipe?"}
    refusal_res = client.post("/ask", json=refusal_payload)
    assert refusal_res.status_code == 200
    
    refusal_data = refusal_res.json()
    assert refusal_data["classification"] == "out_of_scope"
    assert "out of scope" in refusal_data["answer"].lower()
    assert refusal_data["requires_human"] is False
