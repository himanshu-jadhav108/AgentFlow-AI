"""Unit tests validating the Debug Session Dashboard."""

from app.dashboard.graph_renderer import render_graph_mermaid
from app.dashboard.session_store import SessionStore
from app.dashboard.timeline_renderer import render_timeline_ascii


def test_session_store_eviction() -> None:
    """Verifies that the session store evicts oldest requests when limit is exceeded."""
    store = SessionStore(limit=2)
    store.store_session("req-1", {"question": "q1"})
    store.store_session("req-2", {"question": "q2"})
    store.store_session("req-3", {"question": "q3"})

    # req-1 should have been evicted
    assert store.get_session("req-1") is None
    assert store.get_session("req-2") is not None
    assert store.get_session("req-3") is not None

    store.clear()
    assert len(store.get_history_summaries()) == 0


def test_renderers_output() -> None:
    """Verifies diagram and ASCII timeline output generation."""
    mermaid = render_graph_mermaid(["start", "triage", "end"])
    assert "start --> triage" in mermaid

    ascii_flow = render_timeline_ascii(
        [{"event": "Request Received", "duration_ms": 1.2, "timestamp": "2026"}]
    )
    assert "Request Received" in ascii_flow
