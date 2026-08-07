# AgentFlow AI: Local Customer Support Agent

AgentFlow AI is a local AI Customer Support Agent built using Python 3.11+, FastAPI, LangGraph, LangChain, FAISS, and local embedding/LLM systems.

The system features a Clean Architecture, dynamic environment configuration profiles, automatic startup cache synchronization, timing metrics, and is fully containerized.

---

## Quick Start (Python Installation)

To set up, validate system resources, download models, build index files, and run all tests in one command:

```bash
# 1. Create a virtual environment inheriting system packages (recommended for pre-compiled PyTorch/FAISS)
python -m venv --system-site-packages .venv
.venv\Scripts\activate

# 2. Run the automated setup script
python scripts/setup.py
```

---

## Docker Installation

To build images, mount cache volumes (so weights are never downloaded twice), and deploy the API:

```bash
docker compose up --build
```
This mounts:
- `huggingface_cache` to persist LLM weights.
- `vector_data` to persist FAISS index files.

---

## Project Structure
```
agentflow_ai/
│
├── app/                     # Core application logic
│   ├── api/                 # REST endpoints and middlewares
│   │   ├── routes.py
│   │   ├── middleware.py
│   │   └── exception_handlers.py
│   │
│   ├── services/            # Managers and services
│   │   ├── model_manager.py # Checks and pre-downloads weights
│   │   └── index_manager.py # Checks and auto-rebuilds FAISS indexes
│   │
│   ├── nodes/               # Single-responsibility graph nodes
│   ├── graph/               # LangGraph builder and visualizations
│   ├── verification/        # Decoupled verification engine
│   └── schemas/             # Pydantic validation schemas
│
├── config/                  # Dynamic environment configurations
│   ├── development.py       # Developer overrides
│   ├── production.py        # Production overrides
│   ├── testing.py           # Testing overrides
│   └── settings.py          # Unified profile loader
│
├── scripts/                 # CLI tools
│   ├── setup.py             # Installs dependencies and runs checks
│   ├── rebuild_index.py     # Triggers vector index regeneration
│   ├── download_models.py   # Pre-downloads model weights
│   └── clean_cache.py       # Clears in-memory caching layers
│
├── examples/                # API Request/Response schema examples
│   ├── sample_requests.json
│   └── sample_responses.json
│
├── docs/                    # Architectural and deployment guides
│   ├── architecture/
│   ├── development/
│   └── deployment/
│   └── phase_06.md
```

---

## Automatic Startup Validation
On booting the FastAPI application:
1. **Model Cache check**: The server verifies if model weights are present. If missing, it downloads them from Hugging Face hub.
2. **FAISS index check**: The server scans for database files and hashes all knowledge base files. If files are missing or modified, it rebuilds the index automatically.
3. **Graph boot**: Compiles the graph and starts the API server.

---

## Configuration Profiles
Manage profile configurations by setting `APP_ENV` environment variable:
- `development`: Verbose logging and short cache durations.
- `production`: Custom payload bounds and longer cache TTLs.
- `testing`: Disables cache to allow clean test executions.

### Verifier options inside `.env`:
```env
# Target profile (development / production / testing)
APP_ENV=development

# Enable/disable verifier layers
ENABLE_RULE_VERIFICATION=true
ENABLE_SEMANTIC_VERIFICATION=true

# Cache configurations
ENABLE_CACHE=true
CACHE_TTL_SECONDS=300
```

---

## Diagnostics Status Endpoint (`GET /system/status`)
Provides deep system health diagnostics:
```json
{
  "python_version": "3.11.4 (main, Jun 5 2023, 11:31:11)",
  "cuda_available": false,
  "gpu_details": "N/A",
  "model_name": "Qwen/Qwen2.5-0.5B-Instruct",
  "model_loaded": true,
  "vector_index_path": "data/vectorstore",
  "vector_index_exists": true,
  "vector_index_metadata": {
    "knowledge_hash": "d41d8cd98f00b204e9800998ecf8427e",
    "indexing_time_s": 0.84,
    "documents_processed": 5,
    "chunks_created": 25
  },
  "knowledge_base_document_count": 5,
  "embedding_model_name": "sentence-transformers/all-MiniLM-L6-v2",
  "memory_rss_mb": 248.12,
  "system_ready": true
}
```

---

## Verification & Testing
Run pytest to verify all 35 tests covering units, integrations, and load performance limits:

```bash
python -m pytest
```
