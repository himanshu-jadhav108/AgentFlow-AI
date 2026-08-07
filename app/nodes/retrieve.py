"""Retrieve node implementation integrating Phase 2 document search."""

from app.retrieval.retriever import SemanticRetriever
from app.state.agent_state import AgentState
from core.logger import logger


def retrieve_node(state: AgentState) -> dict:
    """Retrieval node that queries the local FAISS database for matching context.

    Saves search results, source file lists, and calculates confidence scores.

    Args:
        state: Current AgentState.

    Returns:
        dict: State updates containing retrieved chunks, sources, and similarity confidence.
    """
    import time
    from app.core.registry import dependency_container
    from app.core.trace import record_node_trace

    start_time = time.time()
    logger.info("--- ENTERING NODE: RETRIEVE ---")
    question = state.get("question", "")

    # Retrieve components via Dependency Injection registry
    retriever = dependency_container.get_retriever()

    # Search (defaults to k=4)
    try:
        results = retriever.retrieve(query=question, top_k=4, min_similarity=0.0)
    except Exception as e:
        logger.error(f"Error querying retriever from graph node: {e}")
        results = []

    # Compile unique source document paths
    sources = sorted(list(set(chunk.source for chunk in results)))

    # Compute confidence: use the similarity score of the top ranked chunk, fallback to 0.0
    confidence = results[0].score if results else 0.0

    logger.info(
        f"Retrieve node completed. Found {len(results)} matching chunks. Top confidence: {confidence:.4f}"
    )

    updates = {
        "selected_chunks": results,
        "sources": sources,
        "confidence": confidence,
        "execution_log": [
            f"Retrieve node: Searched database. Found {len(results)} chunks. "
            f"Top match confidence: {confidence:.4f}"
        ],
    }

    record_node_trace(
        state=state,
        node_name="retrieve",
        start_time=start_time,
        input_summary=f"Query: {question}",
        output_summary=f"Found: {len(results)} chunks | Top confidence: {confidence:.4f}",
        decision="generate",
    )
    updates["execution_trace"] = state["execution_trace"]
    return updates
