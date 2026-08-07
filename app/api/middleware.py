"""API Middlewares for timing, correlation IDs, rate-limiting, and security."""

import time
import uuid
from collections import defaultdict
from threading import Lock
from typing import Callable, Dict, List

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config.settings import settings
from core.logger import logger
from monitoring.metrics import metrics


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware attaching a unique Request ID to all requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check if incoming request already contains ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Sliding-window in-memory IP rate limiter."""

    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)
        self._requests: Dict[str, List[float]] = defaultdict(list)
        self._lock = Lock()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = settings.RATE_LIMIT_WINDOW_SECONDS
        limit = settings.RATE_LIMIT_REQUESTS

        # Bypass standard testing requests to prevent rate limit contamination
        if settings.APP_ENV == "testing" and limit >= 10:
            return await call_next(request)

        with self._lock:
            # Filter out expired request timestamps
            self._requests[client_ip] = [
                t for t in self._requests[client_ip] if now - t < window
            ]

            if len(self._requests[client_ip]) >= limit:
                logger.warning(
                    f"Rate Limiter: Blocked IP '{client_ip}' (exceeded limit of {limit}/{window}s)"
                )
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "success": False,
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": f"Too many requests. Limit is {limit} per {window} seconds.",
                            "details": {},
                        },
                    },
                )

            # Record current timestamp
            self._requests[client_ip].append(now)

        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware injecting enterprise security headers."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response: Response = await call_next(request)
        # Apply standard hardening headers
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        return response


class TimingLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware capturing request logging, latency timings, and size verification."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        method = request.method
        path = request.url.path
        request_id = getattr(request.state, "request_id", "unknown")

        # Payload size validation
        content_length = request.headers.get("content-length")
        max_size = settings.MAX_PAYLOAD_SIZE_BYTES
        if content_length and int(content_length) > max_size:
            logger.warning(
                f"Middleware: Blocked oversized payload ({content_length} bytes) on {path}"
            )
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={
                    "success": False,
                    "error": {
                        "code": "PAYLOAD_TOO_LARGE",
                        "message": f"Payload exceeds maximum allowed size of {max_size / (1024*1024):.1f}MB.",
                        "details": {},
                    },
                },
            )

        logger.info(f"API Request [{request_id}]: {method} {path} initiated.")

        success = True
        try:
            response: Response = await call_next(request)
            return response
        except Exception as e:
            success = False
            raise e
        finally:
            latency_ms = (time.time() - start_time) * 1000
            status_code = response.status_code if "response" in locals() else 500

            # Record to system metrics (exclude metrics endpoint itself to prevent skewing averages)
            if "/metrics" not in path:
                metrics.record_request(
                    success=success and status_code < 400, duration_ms=latency_ms
                )

            logger.info(
                f"API Response [{request_id}]: {method} {path} finished with "
                f"status {status_code} in {latency_ms:.2f}ms."
            )
