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
├── app/                     # Core application logic
│   ├── loaders/             # Markdown and JSON case loaders
│   ├── preprocessing/       # Document cleaner and chunker
│   ├── embeddings/          # Lazy-loaded embedding model singleton
│   ├── vectorstore/         # FAISS vector store manager
│   ├── retrieval/           # Search retrievers and scoring ranker
│   ├── schemas/             # Pydantic schemas for data and APIs
│   └── services/            # Orchestrated indexing service
│
├── config/
│   └── settings.py          # Configuration management with Pydantic Settings
│
├── core/
│   └── logger.py            # Unified logging using loguru (integrates uvicorn & fastapi)
│
├── data/                    # App data directory (Git ignored)
│   ├── documents/           # Source knowledge base & cases
│   └── vectorstore/         # Local FAISS binary index files
│
├── docs/
│   ├── phase_01.md          # Educational phase documentation (Phase 1)
│   └── phase_02.md          # Retrieval pipeline documentation (Phase 2)
│
├── tests/
│   ├── conftest.py          # Test configuration & fixtures
│   ├── test_config.py       # Configuration and API endpoint tests
│   └── test_retrieval.py    # Retrieval pipeline unit & integration tests
│
├── .env.example             # Template for configuration
├── .env                     # Local settings (derived from .env.example)
├── main.py                  # API service entrypoint
├── requirements.txt         # Project dependencies
└── README.md                # Project README
```

---

## Ingestion & Retrieval Pipeline

In Phase 2, we built the local retrieval infrastructure. It functions as follows:

```
[Markdown Files] & [Support Cases JSON]
             ↓
     [TextCleaner] (Unicode NFKC, Spacing normalization)
             ↓
    [DocumentChunker] (RecursiveCharacterTextSplitter, size=1000, overlap=200)
             ↓
 [LocalEmbeddingManager] (sentence-transformers/all-MiniLM-L6-v2)
             ↓
   [FAISSStoreManager] (Deduplicated updates, saved to data/vectorstore/)
```

When a user query is received:
1. The query is converted into a vector embedding.
2. FAISS performs a similarity search returning nearest neighbor candidate chunks based on **Cosine Similarity**.
3. Candidates are ranked by **Similarity Score**, **Document Priority**, and **Chunk Index**.
4. The ranked results are returned with confidence scores.

---

## Setup & Verification

### 1. Installation
We recommend setting up a virtual environment (using `venv` or `conda`):

```bash
# Set up venv
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Seeding Sample Documents
Verify that you have mock documentation files placed under:
- Markdown files: `data/documents/knowledge_base/`
- JSON case history file: `data/documents/resolved_cases.json`

### 3. Run Pytest Suite
Run the test suite verifying all 10 tests across config and retrieval pipelines:

```bash
python -m pytest
```

### 4. Start the FastAPI API Server
Start the local server for development:

```bash
python main.py
```

---

## API Examples

### 1. Health Status check
- **Request**: `GET /health`
- **Response**:
```json
{
  "status": "healthy",
  "app_name": "AgentFlow AI Support Agent",
  "environment": "development",
  "llm_provider": "ollama",
  "llm_model_name": "phi3",
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
}
```

### 2. Re-Build Vector Index
- **Request**: `POST /index`
- **Response**:
```json
{
  "status": "success",
  "documents_processed": 5,
  "chunks_created": 12,
  "message": "Successfully rebuilt FAISS vector index with 12 chunks in 2.34s."
}
```

### 3. Semantic Search Query
- **Request**: `POST /search`
- **Body**:
```json
{
  "query": "Can read-only users create API keys?",
  "top_k": 3,
  "min_similarity": 0.3
}
```
- **Response**:
```json
{
  "query": "Can read-only users create API keys?",
  "results": [
    {
      "chunk_id": "8b51d0ab91a8_c1",
      "document_id": "8b51d0ab91a8",
      "source": "data\\documents\\knowledge_base\\faq.md",
      "text": "Can Read-Only Users Create API Keys?\nNo, read-only users cannot create API keys. API key creation is restricted to Administrators and Members.",
      "score": 0.9124,
      "confidence_score": 0.9124,
      "metadata": {
        "title": "System Roles and API Access FAQ",
        "priority": 1,
        "type": "knowledge_base"
      }
    }
  ],
  "latency_ms": 14.56
}
```
