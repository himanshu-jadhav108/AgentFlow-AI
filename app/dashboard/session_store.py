"""Thread-safe in-memory session storage for developer debug history."""

from collections import OrderedDict
from threading import Lock
from typing import Any, Dict, List, Optional
from config.settings import settings
from core.logger import logger


class SessionStore:
    """Stores query executions diagnostics in a sliding-window memory cache."""

    def __init__(self, limit: int = None) -> None:
        """Initializes thread locks and sliding history limits."""
        self._limit = limit or settings.MAX_DEBUG_HISTORY
        self._history: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._lock = Lock()

    def store_session(self, request_id: str, session_data: Dict[str, Any]) -> None:
        """Saves session diagnostics details, evicting oldest if limit exceeded.

        Args:
            request_id: Core request UUID identifier.
            session_data: Full diagnostics metrics collection.
        """
        with self._lock:
            # If request already exists, update and move to end
            if request_id in self._history:
                self._history.pop(request_id)

            self._history[request_id] = session_data

            # Evict oldest entry if history is full
            if len(self._history) > self._limit:
                oldest_key, _ = self._history.popitem(last=False)
                logger.info(f"SessionStore: Evicted oldest debug session: '{oldest_key}'")

            logger.info(f"SessionStore: Cached debug session for '{request_id}' (Total size: {len(self._history)})")

    def get_session(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves diagnostics for a specific request ID.

        Args:
            request_id: Core request UUID identifier.

        Returns:
            Optional[Dict[str, Any]]: Diagnostics details, or None.
        """
        with self._lock:
            return self._history.get(request_id)

    def get_history_summaries(self) -> List[Dict[str, Any]]:
        """Compiles light summaries list for all cached queries.

        Returns:
            List[Dict[str, Any]]: Summarized request logs.
        """
        with self._lock:
            summaries = []
            for req_id, data in self._history.items():
                summaries.append(
                    {
                        "request_id": req_id,
                        "timestamp": data.get("timestamp", ""),
                        "question": data.get("question", ""),
                        "classification": data.get("classification", ""),
                        "confidence": data.get("confidence", 0.0),
                        "latency_ms": data.get("latency_ms", 0.0),
                    }
                )
            return list(reversed(summaries))

    def clear(self) -> None:
        """Clears all session diagnostics logs."""
        with self._lock:
            self._history.clear()
            logger.info("SessionStore: Purged all stored debug sessions.")


# Global diagnostics session storage
debug_session_store = SessionStore()
