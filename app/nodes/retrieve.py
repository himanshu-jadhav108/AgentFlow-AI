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
    logger.info("--- ENTERING NODE: RETRIEVE ---")
    question = state.get("question", "")

    # Instantiate Phase 2 Retriever
    retriever = SemanticRetriever()

    # Search (defaults to k=4)
    try:
        results = retriever.retrieve(query=question)
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

    return {
        "selected_chunks": results,
        "sources": sources,
        "confidence": confidence,
        "execution_log": [
            f"Retrieve node: Searched database. Found {len(results)} chunks. "
            f"Top match confidence: {confidence:.4f}"
        ],
    }
