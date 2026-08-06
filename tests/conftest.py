"""Pytest configuration and fixtures."""

import os
import pytest
from fastapi.testclient import TestClient

# Override config environment variables for testing
os.environ["APP_ENV"] = "testing"
os.environ["LOG_LEVEL"] = "DEBUG"
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["LLM_MODEL_NAME"] = "test-model"

# Import settings and app after setting overrides
from config.settings import settings
from main import app


@pytest.fixture(scope="session")
def test_settings():
    """Fixture to access configuration settings."""
    return settings


@pytest.fixture(scope="session")
def client():
    """Fixture for FastAPI TestClient."""
    with TestClient(app) as c:
        yield c
