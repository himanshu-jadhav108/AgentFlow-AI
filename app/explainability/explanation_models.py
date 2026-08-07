"""Pydantic schemas and models for the Explainability Engine."""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class ExplainabilityReport(BaseModel):
    """Overall diagnostic report explaining the RAG pipeline execution."""

    request_id: str = Field(..., description="The unique correlation ID.")
    question: str = Field(..., description="The original customer query question.")
    classification: str = Field(..., description="The triage classification category.")
    retrieval_summary: str = Field(..., description="Textual summary of FAISS retrieve lookups.")
    source_summary: str = Field(..., description="Summary details analyzing unique references.")
    verification_summary: str = Field(..., description="Factual grounding verification report.")
    confidence_breakdown: Dict[str, float] = Field(..., description="Weighted confidence values.")
    execution_summary: str = Field(..., description="Summary sentence mapping path and outcome.")
    graph_path: List[str] = Field(..., description="Visited LangGraph nodes sequence.")
    timeline: List[Dict[str, Any]] = Field(..., description="Timestamps sequence mapping.")
    warnings: List[str] = Field(..., description="Diagnostic warning alerts (e.g. low scores).")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary run details.")
