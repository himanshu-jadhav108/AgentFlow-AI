"""Unit tests to verify configuration and API health endpoint."""

from fastapi import status


def test_settings_override(test_settings) -> None:
    """Verify that settings are correctly loaded and environment overrides work."""
    assert test_settings.APP_ENV == "testing"
    assert test_settings.LOG_LEVEL == "DEBUG"
    assert test_settings.LLM_PROVIDER == "ollama"
    assert test_settings.LLM_MODEL_NAME == "test-model"


def test_health_endpoint(client) -> None:
    """Verify that the FastAPI health endpoint returns 200 and matches config."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["status"] == "healthy"
    assert "app_name" in data
    assert data["environment"] == "testing"


def test_version_endpoint(client) -> None:
    """Verify that the FastAPI version endpoint returns 200 and version details."""
    response = client.get("/version")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "version" in data
    assert "app_name" in data
    assert data["api_version"] == "v1"
    assert "description" in data


def test_validation_error(client) -> None:
    """Verify that the global validation error handler formats Pydantic errors into ErrorResponse."""
    response = client.post("/search", json={})  # Empty JSON violates query requirement
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    data = response.json()
    assert "Validation failed" in data["detail"]
    assert data["status_code"] == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert data["error_code"] == "VALIDATION_ERROR"
    assert "errors" in data["meta"]
