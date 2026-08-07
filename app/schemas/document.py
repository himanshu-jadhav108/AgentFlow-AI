"""Domain model representing a structured document in the system."""

from typing import Any, Dict
from pydantic import BaseModel, Field


class Document(BaseModel):
    """Unified Document domain model used throughout the retrieval pipeline."""

    id: str = Field(..., description="Unique identifier for the document.")
    content: str = Field(..., description="The raw or cleaned text content.")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Associated metadata (e.g. source path, author, priority, title).",
    )
