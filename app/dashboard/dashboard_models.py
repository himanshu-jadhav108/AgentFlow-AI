"""Pydantic schemas and models for the Developer Debug Dashboard."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DebugSessionReport(BaseModel):
    """Deep diagnostics report describing a single RAG execution step."""

    request_id: str = Field(..., description="Unique correlation ID.")
    timestamp: str = Field(..., description="Date and time of execution.")
    question: str = Field(..., description="User query question.")
    classification: str = Field(..., description="Triage classification.")
    final_response: Dict[str, Any] = Field(..., description="Final returned answer package.")
    execution_trace: Dict[str, Any] = Field(..., description="Raw execution trace details.")
    explainability_report: Dict[str, Any] = Field(..., description="Explainability report details.")
    performance_metrics: Dict[str, Any] = Field(..., description="Timing breakdown percentages.")
    warnings: List[str] = Field(..., description="System warnings collected.")
