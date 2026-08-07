"""Pydantic schemas for API responses and error messages."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Schema representing the application health status."""

    status: str = Field(..., description="Application health status (e.g. 'healthy').")
    app_name: str = Field(..., description="The name of the application.")
    environment: str = Field(..., description="The running environment mode.")


class VersionResponse(BaseModel):
    """Schema representing application and API version metadata."""

    version: str = Field(..., description="The semantic version of the application.")
    app_name: str = Field(..., description="The name of the application.")
    api_version: str = Field(..., description="Supported API route version.")
    description: str = Field(..., description="Brief description of the service.")


class ErrorResponse(BaseModel):
    """Standardized schema for API error responses."""

    detail: str = Field(..., description="Human-readable error details.")
    status_code: int = Field(..., description="HTTP status code corresponding to the error.")
    error_code: Optional[str] = Field(default=None, description="Optional internal error classification code.")
    meta: Optional[Dict[str, Any]] = Field(default=None, description="Additional context or validation details.")
