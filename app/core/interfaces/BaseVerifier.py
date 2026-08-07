"""Abstract Base Class defining the Verifier contract."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseVerifier(ABC):
    """Interface for answer grounding validation pipelines."""

    @abstractmethod
    def verify(
        self, question: str, answer: str, contexts: List[str]
    ) -> Dict[str, Any]:
        """Validates formatting and fact grounding correctness.

        Args:
            question: Original question context.
            answer: Generated support answer.
            contexts: Selected retrieval source strings.

        Returns:
            Dict[str, Any]: Grounding checks statistics and outcome status.
        """
        pass
