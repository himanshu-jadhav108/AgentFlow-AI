"""Cache manager to orchestrate API data caching based on config options."""

from typing import Any, Dict, Optional

from cache.memory_cache import MemoryCache
from config.settings import settings
from core.logger import logger


class CacheManager:
    """Singleton cache coordinator that enforces configuration-level toggles."""

    _instance: Optional["CacheManager"] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "CacheManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_manager()
        return cls._instance

    def _init_manager(self) -> None:
        self._answer_cache = MemoryCache()

    def get_answer(self, question: str) -> Optional[Dict[str, Any]]:
        """Retrieves cached response dict for a given query if caching is active.

        Args:
            question: Cleaned query text.

        Returns:
            Optional[Dict[str, Any]]: Decoded payload from cache, or None.
        """
        if not settings.ENABLE_CACHE:
            return None

        # Clean/normalize key
        key = f"q:{question.strip().lower()}"
        cached = self._answer_cache.get(key)
        if cached:
            logger.info(f"Cache hit: Found resolved answer for '{question}'")
            return cached
        return None

    def set_answer(self, question: str, response_payload: Dict[str, Any]) -> None:
        """Stores a resolved answer payload in the cache.

        Args:
            question: Cleaned query text.
            response_payload: Dictionary payload to cache.
        """
        if not settings.ENABLE_CACHE:
            return

        key = f"q:{question.strip().lower()}"
        ttl = settings.CACHE_TTL_SECONDS
        self._answer_cache.set(key, response_payload, ttl)

    def clear(self) -> None:
        """Clears all caches and statistics."""
        self._answer_cache.clear()

    @property
    def stats(self) -> Dict[str, Any]:
        """Gives summary statistics across all caches.

        Returns:
            Dict[str, Any]: Consolidated cache hit/miss status.
        """
        return {
            "enabled": settings.ENABLE_CACHE,
            "answer_cache": self._answer_cache.stats,
        }
