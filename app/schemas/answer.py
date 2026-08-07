"""Pydantic schemas for the customer support ask query."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """Schema representing a user question query request."""

    question: str = Field(
        ...,
        description="The customer support question or message query.",
        min_length=1,
    )


class AskResponse(BaseModel):
    """Schema representing the verified agent answer response."""

    classification: str = Field(
        ...,
        description="The triage category: 'answerable', 'clarification', 'escalate', or 'out_of_scope'.",
    )
    answer: str = Field(
        ...,
        description="The grounded answer text compiled by the LLM or response templates.",
    )
    confidence: float = Field(
        ...,
        description="The computed confidence score matching the verification and retrieval layers [0.0 - 1.0].",
    )
    sources: List[str] = Field(
        default_factory=list,
        description="The list of source documents cited to formulate the answer.",
    )
    requires_human: bool = Field(
        ...,
        description="Flag indicating if the issue needs escalation to a human representative.",
    )
    reason: str = Field(
        ...,
        description="The decision reasoning description (e.g., 'Supported by documentation').",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional execution context tracking priority, categories, and latency benchmarks.",
    )
    explainability: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Detailed explainability report, exposed only in debug mode.",
    )
    execution_trace: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Detailed execution trace, exposed only in debug mode.",
    )
