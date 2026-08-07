# Phase 5: Production API, Observability, Caching & Performance

This document covers the details of Phase 5, where we converted the AgentFlow AI Support Agent into a highly optimized, observable, production-grade enterprise backend service.

---

## 1. Goal
The primary objective of Phase 5 is to transition our AI orchestration agent into an enterprise-class FastAPI service. We focus on enhancing robustness, speed, security, and traceability without changing the underlying LangGraph logic.

---

## 2. REST API Design
Our production backend implements a clean, restful interface with request/response model safety:
- `GET /`: Redirects to interactive OpenAPI docs.
- `GET /health`: Basic health checks and environment attributes.
- `GET /version`: Current API details.
- `POST /index`: Rebuilds the FAISS database index.
- `POST /search`: Queries vector database passages.
- `POST /ask`: Triggers the self-correcting RAG workflow.
- `POST /graph/run`: Backward-compatible graph trace endpoint.
- `GET /metrics`: Observability statistics.
- `GET /graph`: Workflow flowchart details.

---

## 3. FastAPI Best Practices
- **Dependency Injection**: Dependencies (retrievers, graph singletons, cache manager instances) are lazily loaded.
- **Pydantic Validation**: All endpoints use typed Pydantic request and response models.
- **Lifespan Context Hooks**: Startup and shutdown lifecycle events compile graph structures and output visualization diagrams.

---

## 4. Middleware
We register ASGI and custom `BaseHTTPMiddleware` classes:
- `RequestIDMiddleware`: Generates and links an `X-Request-ID` correlation header to all requests.
- `RateLimitingMiddleware`: Uses sliding windows to enforce rate limits (default 100 requests/minute per IP).
- `SecurityHeadersMiddleware`: Injects HSTS, Content-Security-Policy, X-Frame-Options.
- `TimingLoggingMiddleware`: Calculates execution time and blocks payloads exceeding `1MB`.

---

## 5. Validation
We sanitize search strings in [app/api/validators.py](file:///D:/Projects/AgentFlow%20AI/app/api/validators.py):
- Enforces character lengths (3 to 1000).
- Blocks path traversal strings (e.g. `../`, `/etc/passwd`).
- Sanitizes script tags and raw HTML strings.

---

## 6. Error Handling
Global handlers inside [app/api/exception_handlers.py](file:///D:/Projects/AgentFlow%20AI/app/api/exception_handlers.py) catch exceptions and format them into standard JSON structures, preventing stack trace exposure:
```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Validation failed: field 'question' cannot be empty",
        "details": {}
    }
}
```

---

## 7. Metrics
Our observability engine tracks system performance stats:
- **Request Counts**: Total, Success, and Failure counts.
- **Average Speeds**: Response time, retriever search time, generation time, and verification time.
- **Retry Statistics**: Total times verification loops were triggered.

---

## 8. Logging
We write structured Method, Path, Latency, and Request ID logs to the console using Loguru. Log messages do not record sensitive query content.

---

## 9. Caching
Our local caching system contains two parts:
1. **MemoryCache**: Thread-safe key-value cache with Time-to-Live (TTL) automatic expirations.
2. **CacheManager**: Coordinates answer lookups, returning cached RAG results in sub-milliseconds.

---

## 10. Async Programming
Every API handler is declared `async def`, enabling FastAPI to utilize asynchronous loop concurrency. Heavy file index building runs in non-blocking executor threads.

---

## 11. Benchmarking
Our script runs 100 sequential queries to calculate worst-case, best-case, and average response times.

---

## 12. Folder Changes
```
app/
├── api/
│   ├── routes.py             # Route handlers definitions
│   ├── dependencies.py       # Reusable FastAPI dependencies
│   ├── middleware.py         # Timing, rate-limiter, security headers
│   ├── exception_handlers.py # Global JSON error formats
│   └── validators.py         # Request sanitizations
│
├── monitoring/
│   ├── metrics.py            # Latency recorders and stats trackers
│   └── timing.py             # Timing block context manager
│
└── cache/
    ├── memory_cache.py       # Thread-safe TTL cache
    └── cache_manager.py      # Caching manager singleton
```

---

## 13. Every File Explained
- **`app/api/routes.py`**: Hosts HTTP endpoints and runs validators.
- **`app/api/middleware.py`**: Intercepts requests, attaches correlation IDs, and validates size limits.
- **`app/api/validators.py`**: Scans inputs for security violations.
- **`cache/memory_cache.py`**: Stores key-value items with expirations.
- **`monitoring/metrics.py`**: Computes moving latency averages.

---

## 14. Sequence Diagrams
```
[Client]                [Middleware]               [Routes]             [Cache]
   │                         │                        │                    │
   │─── POST /ask ──────────►│                        │                    │
   │                         │─── Validate limit ────►│                    │
   │                         │                        │─── Get cache ─────►│
   │                         │                        │◄── [Hit] ──────────│
   │◄── 200 OK (Cache Hit) ──│◄───────────────────────│                    │
```

---

## 15. API Flow
```
[Client Request] ──► CORS/Security Headers ──► Rate Limiter ──► Payload Size Limit ──► Cache Check
                                                                                            │
   ┌────────────────────────────────◄── Cache Hit ──────────────────────────────────────────┘
   │
   ▼
[Graph execution (retrieve -> generate -> verify)] ──► Update Cache ──► Expose Response
```

---

## 16. Interview Questions
1. **Q**: Why are correlation IDs useful in microservice architectures?
   - **A**: They link multiple requests across disparate API logs, letting developers trace issues end-to-end.
2. **Q**: What are the disadvantages of BaseHTTPMiddleware in FastAPI?
   - **A**: It can block ASGI stream flows. For custom header manipulation, pure ASGI middleware is sometimes preferred.

---

## 17. Homework
- **Exercise**: Implement cache eviction policies like Least Recently Used (LRU) in `MemoryCache`.
- **Exercise**: Integrate timing metrics into Prometheus using Prometheus Python Client.

---

## 18. Quiz
1. Which middleware checks maximum request body sizes?
   - [ ] CORS Middleware
   - [x] TimingLoggingMiddleware
   - [ ] RateLimitingMiddleware
2. Where are query caches cleared?
   - [ ] GET /metrics
   - [x] POST /index
   - [ ] GET /graph

---

## 19. Common Mistakes
- **VRAM leakage**: Loading multiple model instances on API calls. Always use singletons.

---

## 20. Debugging
- **Rate limiting triggers on test runs**: Ensure `APP_ENV=testing` is set to bypass standard rate limiting.

---

## 21. Performance Tips
- Configure Gzip compression thresholds to prevent CPU cycles overhead on small payloads.

---

## 22. Production Considerations
- Enable HTTPS (SSL) on reverse proxies (e.g. Nginx).
- Enforce strict API keys header authorizations.

---

## 23. Best Practices
- Never return internal traceback details to clients.
- Log latency timings for database search steps.

---

## 24. Summary
In Phase 5, we added structured error handling, token caches, request limits, rate-limiters, timing blocks, and benchmark reports.

---

## 25. Preview of Phase 6
In Phase 6, we will package the application using multi-stage Docker containers and run end-to-end staging validations.
