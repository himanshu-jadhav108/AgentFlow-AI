"""AgentState schema definition for LangGraph orchestration."""

from typing import Annotated, Any, Dict, List, Optional

from typing_extensions import TypedDict


def append_log(left: List[str], right: List[str]) -> List[str]:
    """Reducer function that appends log entries.

    This ensures that each node's logged execution steps are accumulated
    rather than overwritten.
    """
    return left + right


class AgentState(TypedDict):
    """Strongly typed state dict representing the workflow state of the Support Agent."""

    question: str
    """The initial or clarified input question from the customer."""

    classification: str
    """The triage category: 'answerable', 'clarification', 'escalate', or 'out_of_scope'."""

    conversation_history: List[Dict[str, str]]
    """The dialogue history, typically containing list of {'role': '...', 'content': '...'} dicts."""

    retrieved_documents: List[Any]
    """The raw documents loaded from files before cleaning and chunking."""

    selected_chunks: List[Any]
    """Retrieved and ranked matching chunks from the FAISS database (RetrievedChunk schemas)."""

    answer: Optional[str]
    """The generated answer text, clarification request, or out-of-scope messaging."""

    confidence: float
    """Similarity or confidence score estimate, normalized between [0.0 - 1.0]."""

    sources: List[str]
    """File names or paths from which the retrieved chunks originated."""

    requires_human: bool
    """Boolean flag indicating that the query needs to be escalated to a human support agent."""

    retry_count: int
    """Number of retry attempts executed during verification or error cycles."""

    max_retries: int
    """Maximum allowable retry cycles before automatic escalation."""

    verification_status: str
    """Result of truthfulness or correctness checks: 'verified', 'hallucinated', or 'unverified'."""

    metadata: Dict[str, Any]
    """Arbitrary metadata dictionary tracking triage reason, priority, or categories."""

    execution_log: Annotated[List[str], append_log]
    """Cumulative trace logging every node transition and execution milestone."""

    timestamps: Dict[str, str]
    """Timestamp records tracking initialization, node transitions, and total execution latencies."""

    execution_trace: Dict[str, Any]
    """The diagnostic trace capturing node paths, timing, and pipeline metrics."""
