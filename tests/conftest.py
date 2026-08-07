"""Pytest configuration and fixtures.

Automatically mocks local HuggingFace LLM loaders to run tests without downloading weights.
"""

import os
from typing import Any
from unittest.mock import MagicMock

import pytest
import torch
from fastapi.testclient import TestClient

# Override config environment variables for testing
os.environ["APP_ENV"] = "testing"
os.environ["LOG_LEVEL"] = "DEBUG"
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["LLM_MODEL_NAME"] = "test-model"

from app.llm.model_loader import ModelLoader
from app.llm.tokenizer import TokenizerLoader
# Import settings and app after setting overrides
from config.settings import settings
from main import app


class MockModel:
    """Mock model that returns dummy token tensors on generate."""

    def generate(self, *args, **kwargs) -> Any:
        return torch.tensor([[1, 2, 3, 4]])


class MockTokenizer:
    """Mock tokenizer returning token tensors and custom strings based on prompt text."""

    def __init__(self) -> None:
        self.pad_token = "[PAD]"
        self.eos_token = "[EOS]"
        self.pad_token_id = 0
        self.eos_token_id = 1
        self.last_prompt = ""

    def __call__(self, text: str, *args, **kwargs) -> Any:
        self.last_prompt = text
        inputs = MagicMock()
        inputs.input_ids = torch.tensor([[1, 2]])
        # Mock dictionary access for **inputs unpack
        inputs.keys.return_value = ["input_ids"]
        inputs.__getitem__.return_value = torch.tensor([[1, 2]])
        inputs.to.return_value = inputs
        return inputs

    def decode(self, tokens: Any, *args, **kwargs) -> str:
        prompt = getattr(self, "last_prompt", "")
        # Return custom JSON structures depending on the prompt instructions
        if (
            "VERIFICATION_PROMPT_TEMPLATE" in prompt
            or "Verify" in prompt
            or "Factual Context Chunks" in prompt
        ):
            # Check if answer contains a hallucination for retry tests
            if "hallucinated answer" in prompt.lower():
                return '{"supported": false, "reason": "Contains hallucinated facts."}'
            return '{"supported": true, "reason": "Proposed answer matches context."}'
        elif "pepperoni pizza" in prompt or "recipe" in prompt:
            return (
                '{"answer": "I couldn\'t find supporting information.", "citations": [], '
                '"reason": "Off-topic query refusal."}'
            )
        elif "reset my password" in prompt or "password" in prompt:
            if "hallucinated" in prompt.lower():
                return (
                    '{"answer": "This is a hallucinated answer about password reset.", '
                    '"citations": ["faq.md"], "reason": "Direct lookup match."}'
                )
            return (
                '{"answer": "How do I reset my password? Go to settings -> Account -> Reset password.", '
                '"citations": ["faq.md"], "reason": "Direct lookup match."}'
            )
        else:
            return '{"answer": "Mocked LLM answer.", "citations": ["faq.md"], "reason": "Standard mock response."}'


@pytest.fixture(autouse=True, scope="session")
def mock_llm_loaders() -> None:
    """Monkeypatch LLM loaders session-wide to return mock instances."""

    # Define patch overrides
    def mock_load_model(self) -> Any:
        if self._model is None:
            self._model = MockModel()
            self._device = "cpu"
        return self._model

    def mock_load_tokenizer(self) -> Any:
        self._tokenizer = MockTokenizer()
        return self._tokenizer

    # Apply patches directly to loader classes
    ModelLoader.load_model = mock_load_model
    TokenizerLoader.load_tokenizer = mock_load_tokenizer


@pytest.fixture(scope="session")
def test_settings() -> Any:
    """Fixture to access configuration settings."""
    return settings


@pytest.fixture(scope="session")
def client() -> Any:
    """Fixture for FastAPI TestClient."""
    with TestClient(app) as c:
        yield c
