"""Unit and integration tests for the LangGraph agent orchestration."""

import pytest
from fastapi import status

from app.graph.builder import build_graph
from app.state.agent_state import AgentState


def test_graph_compilation() -> None:
    """Verify that the LangGraph StateGraph builds and compiles without errors."""
    graph = build_graph()
    assert graph is not None
    # Verify that nodes are registered in the graph structure
    node_names = [node for node in graph.get_graph().nodes.keys()]
    assert "start" in node_names
    assert "triage" in node_names
    assert "retrieve" in node_names
    assert "clarification" in node_names
    assert "escalation" in node_names
    assert "out_of_scope" in node_names
    assert "end" in node_names


@pytest.mark.asyncio
async def test_triage_answerable_path() -> None:
    """Test triage classification and routing for a standard document query."""
    graph = build_graph()
    initial_state: AgentState = {
        "question": "How do I generate an API key?",
        "conversation_history": [],
        "retrieved_documents": [],
        "selected_chunks": [],
        "answer": None,
        "confidence": 0.0,
        "sources": [],
        "requires_human": False,
        "retry_count": 0,
        "max_retries": 3,
        "verification_status": "unverified",
        "metadata": {},
        "execution_log": [],
        "timestamps": {},
    }

    final_state = await graph.ainvoke(initial_state)

    # Asserts
    assert final_state["classification"] == "answerable"
    assert len(final_state["selected_chunks"]) > 0  # Should retrieve mock docs
    assert final_state["confidence"] > 0.0
    assert (
        "faq.md" in final_state["sources"][0]
        or "resolved_cases.json" in final_state["sources"][0]
    )
    assert final_state["requires_human"] is False

    # Check execution trace logs
    logs = final_state["execution_log"]
    assert any("triage" in log.lower() for log in logs)
    assert any("retrieve" in log.lower() for log in logs)
    assert any("end" in log.lower() for log in logs)


@pytest.mark.asyncio
async def test_triage_clarification_path() -> None:
    """Test triage classification and routing for vague questions."""
    graph = build_graph()
    initial_state: AgentState = {
        "question": "Reset",  # Too short
        "conversation_history": [],
        "retrieved_documents": [],
        "selected_chunks": [],
        "answer": None,
        "confidence": 0.0,
        "sources": [],
        "requires_human": False,
        "retry_count": 0,
        "max_retries": 3,
        "verification_status": "unverified",
        "metadata": {},
        "execution_log": [],
        "timestamps": {},
    }

    final_state = await graph.ainvoke(initial_state)

    # Asserts
    assert final_state["classification"] == "clarification"
    assert "clarify" in final_state["answer"].lower()
    assert final_state["requires_human"] is False
    assert len(final_state["selected_chunks"]) == 0

    logs = final_state["execution_log"]
    assert any("clarification" in log.lower() for log in logs)


@pytest.mark.asyncio
async def test_triage_escalation_path() -> None:
    """Test triage classification and routing for sensitive/billing issues."""
    graph = build_graph()
    initial_state: AgentState = {
        "question": "My account was compromised and my credit card leaked",
        "conversation_history": [],
        "retrieved_documents": [],
        "selected_chunks": [],
        "answer": None,
        "confidence": 0.0,
        "sources": [],
        "requires_human": False,
        "retry_count": 0,
        "max_retries": 3,
        "verification_status": "unverified",
        "metadata": {},
        "execution_log": [],
        "timestamps": {},
    }

    final_state = await graph.ainvoke(initial_state)

    # Asserts
    assert final_state["classification"] == "escalate"
    assert final_state["requires_human"] is True
    assert "escalate" in final_state["answer"].lower()
    assert final_state["metadata"]["escalation_priority"] == 5

    logs = final_state["execution_log"]
    assert any("escalation" in log.lower() for log in logs)


@pytest.mark.asyncio
async def test_triage_out_of_scope_path() -> None:
    """Test triage classification and routing for off-topic query."""
    graph = build_graph()
    initial_state: AgentState = {
        "question": "Can you give me a recipe for pepperoni pizza?",
        "conversation_history": [],
        "retrieved_documents": [],
        "selected_chunks": [],
        "answer": None,
        "confidence": 0.0,
        "sources": [],
        "requires_human": False,
        "retry_count": 0,
        "max_retries": 3,
        "verification_status": "unverified",
        "metadata": {},
        "execution_log": [],
        "timestamps": {},
    }

    final_state = await graph.ainvoke(initial_state)

    # Asserts
    assert final_state["classification"] == "out_of_scope"
    assert "out of scope" in final_state["answer"].lower()
    assert final_state["requires_human"] is False

    logs = final_state["execution_log"]
    assert any("out-of-scope" in log.lower() for log in logs)


def test_api_graph_run(client) -> None:
    """Integration test for POST /graph/run endpoint."""
    # Ensure vector store index is created first
    client.post("/index")

    payload = {"question": "How do I reset my password?"}
    response = client.post("/graph/run", json=payload)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["question"] == "How do I reset my password?"
    assert data["classification"] == "answerable"
    assert "start" in data["node_path"]
    assert "triage" in data["node_path"]
    assert "retrieve" in data["node_path"]
    assert "end" in data["node_path"]

    final_state = data["final_state"]
    assert final_state["confidence"] > 0.0
    assert len(final_state["selected_chunks"]) > 0
    assert (
        "faq.md" in final_state["sources"][0]
        or "resolved_cases.json" in final_state["sources"][0]
    )
