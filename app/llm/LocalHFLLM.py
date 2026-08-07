"""Concrete LLM wrapper running local model generation workflows."""

from typing import Any
from app.core.interfaces.BaseLLM import BaseLLM
from app.llm.inference import InferenceManager


class LocalHFLLM(BaseLLM):
    """LLM implementation calling HF generation pipelines."""

    def __init__(self, concrete_inference: InferenceManager = None) -> None:
        """Initializes using injected inference singleton.

        Args:
            concrete_inference: Core inference runner.
        """
        self._inference = concrete_inference or InferenceManager()

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Invokes local pipeline generation."""
        return self._inference.generate_text(prompt=prompt, **kwargs)

    def generate_text(self, prompt: str, **kwargs: Any) -> str:
        """Invokes local pipeline generation (compatibility mapping)."""
        return self._inference.generate_text(prompt=prompt, **kwargs)
