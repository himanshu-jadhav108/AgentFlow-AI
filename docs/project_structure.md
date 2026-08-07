# Project Structure Index

This document maps every directory and file in the AgentFlow AI repository, detailing its purpose, responsibilities, and dependency relationships.

---

## Folder Tree

```
D:\Projects\AgentFlow AI\
│
├── config/                  # Configuration Profile Management
│   ├── settings.py          # Unified profile loader
│   ├── development.py       # Development profile overrides
│   ├── production.py        # Production profile overrides
│   └── testing.py           # Testing profile overrides
│
├── app/                     # Core Application Source
│   ├── api/                 # API Layer
│   │   ├── routes.py        # FastAPI endpoint router mappings
│   │   ├── middleware.py    # Request limits, size boundaries, and correlation IDs
│   │   └── exception_handlers.py # Custom error-to-JSON handlers
│   │
│   ├── core/                # System Abstractions
│   │   ├── interfaces/      # Contract APIs (BaseRetriever, BaseLLM, etc.)
│   │   ├── registry.py      # DI Container and lazy-loader Component Registry
│   │   └── trace.py         # Step recorders mapping node transitions
│   │
│   ├── retrievers/          # FAISSRetriever plugin wrapper
│   ├── llm/                 # LocalHFLLM plugin wrapper
│   ├── verifiers/           # HybridVerifier plugin wrapper
│   ├── embeddings/          # SentenceTransformerEmbedding plugin wrapper
│   ├── vectorstores/        # FAISSVectorStore plugin wrapper
│   │
│   ├── state/               # LangGraph state TypedDict declarations
│   ├── graph/               # Graph workflows compilers
│   ├── retrieval/           # Text extraction, chunk loading, and indexing
│   ├── generation/          # Prompt templates formatting and model execution
│   ├── verification/        # Grounding fact checkers and confidence rules
│   ├── explainability/      # Diagnostic timeline events and warning logs
│   └── dashboard/           # Debug session store history and endpoints
│
├── scripts/                 # CLI tools
│   ├── setup.py             # Setup environment checks and test execution
│   ├── rebuild_index.py     # Rebuild FAISS index binaries
│   ├── download_models.py   # Download transformer model weights
│   └── clean_cache.py       # Purge cache systems
│
├── tests/                   # Pytest automation suite
│   ├── unit/                # Unit test scripts
│   ├── integration/         # LangGraph workflow tests
│   └── performance/         # Caching and rate-limits tests
│
└── docs/                    # Documentation guides
```

---

## File Responsibilities

### Configuration (`config/`)
- `settings.py`: Initializes `Settings` inheriting from `pydantic-settings`. Dynamically merges profile-specific override variables based on `APP_ENV`.
- `development.py`: Enables high verbosity logging, caching, and sets shorter TTL benchmarks.
- `production.py`: Disables debug modes/dashboards and restricts payload sizes to 512KB.
- `testing.py`: Disables caching to verify facts assertions cleanly.

### API (`app/api/`)
- `routes.py`: Registers routes like `/ask`, `/explain`, `/system/status`, and `/debug/*`.
- `middleware.py`: Handles security constraints (payload limits) and tracks latency execution timings.
- `exception_handlers.py`: Catch-all handlers returning structured error packages.

### Core Interface Plugins (`app/core/`)
- `interfaces/`: Sets contracts forcing plugins to implement methods like `retrieve()`, `generate()`, and `verify()`.
- `registry.py`: Acts as the central registry, resolving dependencies lazily. Supports mock override replacements via `dependency_container.replace()`.
- `trace.py`: Populates `execution_trace` in `AgentState` recording step latencies.

### RAG Nodes (`app/nodes/`)
- `start.py`, `triage.py`, `retrieve.py`, `generate.py`, `verify.py`, `end.py`: Small single-responsibility functions acting as LangGraph node processors.
