"""Thread-safe, TTL-based in-memory cache implementation."""

import time
from threading import Lock
from typing import Any, Dict, Optional, Tuple
from core.logger import logger


class MemoryCache:
    """Lightweight in-memory cache with TTL expiration."""

    def __init__(self) -> None:
        self._cache: Dict[str, Tuple[Any, float]] = {}  # key -> (value, expire_timestamp)
        self._lock = Lock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Retrieves a cached value if it exists and has not expired.

        Args:
            key: Cache key.

        Returns:
            Optional[Any]: The cached value, or None if expired/not found.
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            value, expire_at = self._cache[key]
            if time.time() > expire_at:
                # Cache item expired; remove it
                del self._cache[key]
                self._misses += 1
                logger.debug(f"Cache key '{key}' has expired and was removed.")
                return None

            self._hits += 1
            return value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Stores a value in the cache with a specified TTL.

        Args:
            key: Cache key.
            value: Value to store.
            ttl_seconds: Expiration lifespan in seconds.
        """
        with self._lock:
            expire_at = time.time() + ttl_seconds
            self._cache[key] = (value, expire_at)
            logger.debug(f"Cache set for key '{key}' with TTL {ttl_seconds}s.")

    def clear(self) -> None:
        """Clears all stored cache items and resets statistics."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            logger.info("In-memory cache cleared successfully.")

    def delete(self, key: str) -> bool:
        """Deletes a key from cache. Returns True if existed."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    @property
    def stats(self) -> Dict[str, Any]:
        """Returns cache execution statistics.

        Returns:
            Dict[str, Any]: Cache hit rate, misses, and current size.
        """
        with self._lock:
            total_queries = self._hits + self._misses
            hit_ratio = (self._hits / total_queries) if total_queries > 0 else 0.0
            return {
                "hits": self._hits,
                "misses": self._misses,
                "size": len(self._cache),
                "hit_ratio": round(hit_ratio, 4),
            }
