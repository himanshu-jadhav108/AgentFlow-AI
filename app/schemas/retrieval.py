"""Pydantic schemas for the retrieval and indexing endpoints."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Schema for a similarity search query request."""

    query: str = Field(
        ...,
        description="The user's query or support question to search for.",
        min_length=1,
    )
    top_k: Optional[int] = Field(
        default=None,
        description="Maximum number of relevant chunks to retrieve. Overrides config default.",
        ge=1,
    )
    min_similarity: Optional[float] = Field(
        default=None,
        description="Minimum similarity score threshold. Overrides config default.",
        ge=0.0,
        le=1.0,
    )


class RetrievedChunk(BaseModel):
    """Schema representing a single retrieved document chunk."""

    chunk_id: str = Field(..., description="Unique identifier for the chunk.")
    document_id: str = Field(..., description="Unique identifier of the parent document.")
    source: str = Field(..., description="Source path or name of the parent document.")
    text: str = Field(..., description="Text content of the chunk.")
    score: float = Field(..., description="Raw similarity score from vector store (e.g. FAISS L2/Cosine).")
    confidence_score: float = Field(..., description="Normalized confidence score [0, 1].")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata from the original document or chunking process.",
    )


class SearchResponse(BaseModel):
    """Schema for the search query response."""

    query: str = Field(..., description="The original search query.")
    results: List[RetrievedChunk] = Field(
        default_factory=list,
        description="List of retrieved chunks sorted by confidence.",
    )
    latency_ms: float = Field(..., description="Time taken to perform the search in milliseconds.")


class IndexResponse(BaseModel):
    """Schema for the index rebuild response."""

    status: str = Field(..., description="Status of the index rebuild (e.g., 'success').")
    documents_processed: int = Field(..., description="Number of source documents loaded and cleaned.")
    chunks_created: int = Field(..., description="Number of vector chunks generated and indexed.")
    message: str = Field(..., description="Informative status message.")


class GraphRunRequest(BaseModel):
    """Schema representing a request to execute the support agent workflow."""

    question: str = Field(
        ...,
        description="The support question or query text to submit to the agent.",
        min_length=1,
    )


class GraphRunResponse(BaseModel):
    """Schema representing the completed agent execution trace and final state snapshot."""

    question: str = Field(..., description="The original support query question.")
    classification: str = Field(..., description="The final classification category determined by the agent triage.")
    node_path: List[str] = Field(..., description="The ordered sequence of graph nodes executed in this run.")
    final_state: Dict[str, Any] = Field(..., description="Full state snapshot at the conclusion of the execution path.")

