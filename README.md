# AgentFlow AI: Local Customer Support Agent

AgentFlow AI is a local AI Customer Support Agent built using Python 3.11+, FastAPI, LangGraph, LangChain, FAISS, and local embedding/LLM systems.

The system features a Clean Architecture separating concerns, is fully type-safe, and runs completely locally (requiring zero external API calls to OpenAI, Gemini, or other cloud endpoints).

---

## Technical Stack
- **Web & API Framework:** FastAPI (with Uvicorn)
- **Workflow & Orchestration:** LangGraph & LangChain
- **Local Embeddings:** Sentence-Transformers (`all-MiniLM-L6-v2`)
- **Local Vector Database:** FAISS
- **Local LLMs:** Ollama / HuggingFace Pipelines (Phi-3, TinyLlama)
- **Validation & Settings:** Pydantic & Pydantic Settings
- **Testing:** Pytest & HTTPX
- **Logging:** Loguru & Rich

---

## Project Structure
```
agentflow_ai/
│
├── app/                     # Core application logic
│   ├── graph/               # LangGraph builder and visualizations
│   │   ├── builder.py
│   │   └── visualization.py
│   │
│   ├── state/               # Workflow state schemas
│   │   └── agent_state.py
│   │
│   ├── nodes/               # Single-responsibility nodes
│   │   ├── start.py
│   │   ├── triage.py
│   │   ├── retrieve.py
│   │   ├── clarification.py
│   │   ├── escalation.py
│   │   ├── out_of_scope.py
│   │   └── end.py
│   │
│   ├── routing/             # Conditional branching functions
│   │   └── conditions.py
│   │
│   ├── loaders/             # Markdown and JSON case loaders
│   ├── preprocessing/       # Document cleaner and chunker
│   ├── embeddings/          # Lazy-loaded embedding model singleton
│   ├── vectorstore/         # FAISS vector store manager
│   ├── retrieval/           # Search retrievers and scoring ranker
│   └── schemas/             # Pydantic schemas for data and APIs
│
├── config/
│   └── settings.py          # Configuration management with Pydantic Settings
│
├── core/
│   ├── exceptions.py        # Custom exceptions and global handlers
│   └── logger.py            # Unified logging using loguru (forwarded to Rich)
│
├── data/                    # App data directory (Git ignored)
│   ├── documents/           # Source knowledge base & cases
│   └── vectorstore/         # Local FAISS binary index files
│
├── docs/
│   ├── phase_01.md          # Educational phase documentation (Phase 1)
│   ├── phase_02.md          # Retrieval pipeline documentation (Phase 2)
│   └── phase_03.md          # LangGraph orchestration documentation (Phase 3)
│
├── tests/
│   ├── conftest.py          # Test configuration & fixtures
│   ├── test_config.py       # Configuration and API endpoint tests
│   ├── test_retrieval.py    # Retrieval pipeline unit & integration tests
│   └── test_graph.py        # LangGraph agent integration tests
│
├── assets/                  # Exported visualization graphics
│   ├── graph_mermaid.md     # Flowchart code
│   ├── graph_ascii.txt      # Text visualization diagram
│   └── graph_flowchart.png  # Rendered image file
│
├── .env.example             # Template for configuration
├── .env                     # Local settings (derived from .env.example)
├── main.py                  # API service entrypoint
├── requirements.txt         # Project dependencies
└── README.md                # Project README
```

---

## Agent Orchestration Workflow (LangGraph)

AgentFlow AI uses LangGraph to orchestrate state transitions. A visual diagram of the execution flow is shown below:

```mermaid
graph TD;
    __start__([START]) --> start;
    start --> triage;
    triage -.-> |clarification| clarification;
    triage -.-> |escalate| escalation;
    triage -.-> |out_of_scope| out_of_scope;
    triage -.-> |answerable| retrieve;
    clarification --> end;
    escalation --> end;
    out_of_scope --> end;
    retrieve -.-> end;
    end --> __end__([END]);
```

### Execution Flow Details:
1. **START**: Sets initial state defaults and stamps the start execution time.
2. **TRIAGE**: Inspects the question using rule-based constraints (LLM in future). Decides if it requires details (Clarification), security/billing support (Escalate), is off-topic (Out of Scope), or is ready for search (Answerable).
3. **RETRIEVE**: Invokes the `SemanticRetriever` to pull context from FAISS and calculates similarity confidence scores.
4. **CLARIFICATION / ESCALATION / OUT OF SCOPE**: Handle respective states, returning tailored messages and setting priority flags.
5. **END**: Records the total run time latency and shuts down the trace loop.

---

## Setup & Verification

### 1. Installation
We recommend setting up a virtual environment (using `venv` or `conda`):

```bash
# Set up venv with system libraries (recommended for pre-compiled PyTorch/FAISS on bleeding-edge Python versions)
python -m venv --system-site-packages .venv
.venv\Scripts\activate

# Install/verify dependencies
pip install -r requirements.txt
```

### 2. Seeding Sample Documents
Verify that you have mock documentation files placed under:
- Markdown files: `data/documents/knowledge_base/`
- JSON case history file: `data/documents/resolved_cases.json`

Run `/index` to build the vector store:
```bash
curl -X POST http://127.0.0.1:8000/index
```

### 3. Run Pytest Suite
Run the test suite verifying all 18 tests across config, retrieval, and graph pipelines:

```bash
python -m pytest
```

---

## API Examples

### 1. Run Agent Graph (`POST /graph/run`)
Submits a query to the LangGraph agent orchestrator.
- **Request**: `POST /graph/run`
- **Body**:
```json
{
  "question": "How do I reset my password?"
}
```
- **Response (Answerable Path)**:
```json
{
  "question": "How do I reset my password?",
  "classification": "answerable",
  "node_path": [
    "start",
    "triage",
    "retrieve",
    "end"
  ],
  "final_state": {
    "question": "How do I reset my password?",
    "classification": "answerable",
    "conversation_history": [],
    "retrieved_documents": [],
    "selected_chunks": [
      {
        "chunk_id": "9a1d_c0",
        "document_id": "9a1d",
        "source": "data/documents/knowledge_base/faq.md",
        "text": "How do I reset my password? Go to settings -> Account -> Reset password...",
        "score": 0.892,
        "confidence_score": 0.892,
        "metadata": {}
      }
    ],
    "answer": null,
    "confidence": 0.892,
    "sources": [
      "data/documents/knowledge_base/faq.md"
    ],
    "requires_human": false,
    "retry_count": 0,
    "max_retries": 3,
    "verification_status": "unverified",
    "metadata": {
      "triage_reason": "Valid support query matching system domain.",
      "priority": 1
    },
    "execution_log": [
      "Initialized state in START node.",
      "Triage node: Classified query as 'answerable'. Reason: Valid support query matching system domain.",
      "Retrieve node: Searched database. Found 1 chunks. Top match confidence: 0.8920",
      "Finalized state in END node. Uptime: 24.12ms."
    ],
    "timestamps": {
      "start_time": "2026-08-07T11:34:02.124563",
      "end_time": "2026-08-07T11:34:02.148687",
      "latency_ms": "24.12"
    }
  }
}
```

### 2. Request Clarification (`POST /graph/run`)
- **Request Body**: `{"question": "Reset"}` (Too short/ambiguous)
- **Response**:
```json
{
  "question": "Reset",
  "classification": "clarification",
  "node_path": [
    "start",
    "triage",
    "clarification",
    "end"
  ],
  "final_state": {
    "question": "Reset",
    "classification": "clarification",
    "answer": "I need more information before I can answer. Could you please clarify your request by specifying which product, role, or feature you are referring to?",
    ...
  }
}
```
