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
    assert data["llm_provider"] == "ollama"
    assert data["llm_model_name"] == "test-model"
    assert "embedding_model" in data
