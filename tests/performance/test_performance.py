"""Performance and security middleware tests."""

import time

from fastapi import status

from cache.cache_manager import CacheManager
from config.settings import settings


def test_cache_hit_miss_flow() -> None:
    """Verify in-memory query cache managers."""
    original_cache = settings.ENABLE_CACHE
    settings.ENABLE_CACHE = True

    try:
        cache = CacheManager()
        cache.clear()

        # Initial query is a cache miss
        val1 = cache.get_answer("How do I reset my password?")
        assert val1 is None

        # Save to cache
        payload = {"answer": "Use settings.", "confidence": 0.9, "sources": []}
        cache.set_answer("How do I reset my password?", payload)

        # Secondary query is a cache hit
        val2 = cache.get_answer("How do I reset my password?")
        assert val2 is not None
        assert val2["answer"] == "Use settings."

        # Stats verify hit
        stats = cache.stats
        assert stats["answer_cache"]["hits"] == 1
        assert stats["answer_cache"]["misses"] == 1

        # Clear cache resets stats
        cache.clear()
        assert cache.stats["answer_cache"]["size"] == 0
    finally:
        settings.ENABLE_CACHE = original_cache


def test_rate_limiting_middleware(client) -> None:
    """Verify rate limiter blocks IPs exceeding max configured bounds."""
    # Temporarily set limit low for quick test validation
    original_limit = settings.RATE_LIMIT_REQUESTS
    settings.RATE_LIMIT_REQUESTS = 3

    try:
        # First 3 queries pass
        for _ in range(3):
            res = client.get("/health")
            assert res.status_code == status.HTTP_200_OK

        # 4th query is rate-limited
        res_limit = client.get("/health")
        assert res_limit.status_code == status.HTTP_429_TOO_MANY_REQUESTS

        data = res_limit.json()
        assert data["success"] is False
        assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"

    finally:
        # Restore rate-limit settings
        settings.RATE_LIMIT_REQUESTS = original_limit


def test_oversized_payload_rejection(client) -> None:
    """Verify timing middleware blocks payloads larger than MAX_PAYLOAD_SIZE_BYTES."""
    # Temporarily set max size low
    original_max = settings.MAX_PAYLOAD_SIZE_BYTES
    settings.MAX_PAYLOAD_SIZE_BYTES = 50  # 50 bytes

    try:
        # Submit payload larger than 50 bytes
        huge_question = "x" * 200
        res = client.post("/ask", json={"question": huge_question})
        assert res.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE

        data = res.json()
        assert data["success"] is False
        assert data["error"]["code"] == "PAYLOAD_TOO_LARGE"

    finally:
        settings.MAX_PAYLOAD_SIZE_BYTES = original_max


def test_path_traversal_query_rejection(client) -> None:
    """Verify request validation filters out traversal attacks."""
    payload = {"question": "Read file ../../../etc/passwd"}
    res = client.post("/ask", json=payload)
    assert res.status_code == status.HTTP_400_BAD_REQUEST

    data = res.json()
    assert "traversal" in data["error"]["message"].lower()
