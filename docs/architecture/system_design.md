# System Architecture Design

AgentFlow AI implements a decoupled Clean Architecture structure:
- **Core Node Logic**: Individual state nodes under `app/nodes/`.
- **API endpoints**: REST controllers under `app/api/`.
- **Hybrid Verification**: Layered rules and semantic validation under `app/verification/`.
- **Observability**: Metrics and timers under `monitoring/`.
- **Caching**: Thread-safe in-memory caching under `cache/`.
