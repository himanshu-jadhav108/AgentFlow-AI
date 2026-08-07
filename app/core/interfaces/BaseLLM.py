"""Abstract Base Class defining the LLM contract."""

from abc import ABC, abstractmethod
from typing import Any


class BaseLLM(ABC):
    """Interface for LLM text generations."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generates text from prompt inputs.

        Args:
            prompt: Formatted instruction string.
            **kwargs: Extra parameters (temperature, max_tokens, etc.)

        Returns:
            str: Generated text answer.
        """
        pass
