"""Central Component Registry for dependency injection and plugin management."""

from typing import Any, Callable, Dict
from core.logger import logger


class ComponentRegistry:
    """Manages component lazy-loading, singleton lifespans, and replacements."""

    def __init__(self) -> None:
        """Initializes containers for instances and factory creators."""
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._instances: Dict[str, Any] = {}

    def register(
        self, key: str, factory: Callable[[], Any], singleton: bool = True
    ) -> None:
        """Registers a factory for a given component key.

        Args:
            key: Component identifier.
            factory: Callable building the component.
            singleton: Cache instance for future lookups.
        """
        self._factories[key] = factory
        if key in self._instances:
            del self._instances[key]

    def get(self, key: str) -> Any:
        """Retrieves or creates a component instance.

        Args:
            key: Component identifier.

        Returns:
            Any: Component instance.
        """
        if key in self._instances:
            return self._instances[key]

        if key not in self._factories:
            self._initialize_default(key)

        if key not in self._factories:
            raise KeyError(f"Registry: Component '{key}' is not registered.")

        instance = self._factories[key]()
        self._instances[key] = instance
        return instance

    def replace(self, key: str, instance: Any) -> None:
        """Overrides a component instance (e.g. for testing mocks).

        Args:
            key: Component identifier.
            instance: Direct object replacement.
        """
        self._instances[key] = instance
        logger.info(f"Registry: Overrode component '{key}' with direct instance.")

    def _initialize_default(self, key: str) -> None:
        """Lazy-loads default implementations from plugins."""
        logger.info(f"Registry: Lazy loading default implementation for '{key}'...")
        if key == "llm":
            from app.llm.LocalHFLLM import LocalHFLLM

            self.register("llm", lambda: LocalHFLLM())
        elif key == "retriever":
            from app.retrievers.FAISSRetriever import FAISSRetriever

            self.register("retriever", lambda: FAISSRetriever())
        elif key == "verifier":
            from app.verifiers.HybridVerifier import HybridVerifier

            self.register("verifier", lambda: HybridVerifier())
        elif key == "embeddings":
            from app.embeddings.SentenceTransformerEmbedding import (
                SentenceTransformerEmbedding,
            )

            self.register("embeddings", lambda: SentenceTransformerEmbedding())
        elif key == "vectorstore":
            from app.vectorstores.FAISSVectorStore import FAISSVectorStore

            self.register("vectorstore", lambda: FAISSVectorStore())

    # Typed getter aliases for clean dependency injection calls
    def get_retriever(self) -> Any:
        """Helper getter for retrievers."""
        return self.get("retriever")

    def get_llm(self) -> Any:
        """Helper getter for LLM instances."""
        return self.get("llm")

    def get_verifier(self) -> Any:
        """Helper getter for verifiers."""
        return self.get("verifier")

    def get_embeddings(self) -> Any:
        """Helper getter for embeddings models."""
        return self.get("embeddings")

    def get_vectorstore(self) -> Any:
        """Helper getter for vector databases stores."""
        return self.get("vectorstore")


# Global dependency container
dependency_container = ComponentRegistry()
