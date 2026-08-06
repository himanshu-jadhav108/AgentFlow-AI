# AgentFlow AI: Local Customer Support Agent

AgentFlow AI is an enterprise-grade, production-ready local AI Customer Support Agent built with Python 3.11+, FastAPI, LangGraph, LangChain, FAISS, and local LLMs/embeddings.

The architecture emphasizes separation of concerns, maintainability, type hints, robust testing, and strict local execution (no external API dependencies like OpenAI or Gemini).

---

## Technical Stack
- **Web & API Framework:** FastAPI (with Uvicorn)
- **Workflow & Orchestration:** LangGraph & LangChain
- **Local Embeddings:** Sentence-Transformers (`all-MiniLM-L6-v2`)
- **Local Vector Database:** FAISS
- **Local LLMs:** Ollama / HuggingFace Pipelines (Phi-3, TinyLlama)
- **Validation & Settings:** Pydantic & Pydantic Settings
- **Testing:** Pytest & HTTPX
- **Logging:** Loguru

---

## Project Structure
```
agentflow_ai/
│
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration management with Pydantic Settings
│
├── core/
│   ├── __init__.py
│   └── logger.py            # Unified logging using loguru (integrates uvicorn & fastapi)
│
├── docs/
│   └── phase_01.md          # Educational phase documentation (Phase 1)
│
├── tests/
│   ├── conftest.py          # Test configuration & fixtures
│   └── test_config.py       # Configuration and API endpoint tests
│
├── .env.example             # Template for configuration
├── .env                     # Local settings (derived from .env.example)
├── main.py                  # API service entrypoint
├── requirements.txt         # Project dependencies
└── README.md                # Project README
```

---

## Phase 1 Setup & Verification

### 1. Environment Setup
We recommend setting up a virtual environment (using `venv` or `conda`):

```bash
# Using standard venv
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Verify Configuration
Copy `.env.example` to `.env` (already done by setup) and modify configuration as needed.

### 3. Run Verification Tests
Use pytest to run the configuration and health endpoint tests:

```bash
pytest
```

### 4. Start FastAPI Server
Start the local server for development:

```bash
python main.py
```
And access the health check at `http://127.0.0.1:8000/health`.
