# API Execution & Verification Guide

This guide details how to query, verify, and understand each endpoint exposed by the AgentFlow AI service.

---

## 1. Core Support Query (`POST /ask`)

- **How it works**:
  Triages the question, searches the FAISS index database for matching passages, compiles context prompts, triggers the HuggingFace LLM local execution, runs the hybrid verifiers, and resolves self-correction loops.
  
- **cURL Command**:
  ```bash
  curl -X POST "http://127.0.0.1:8000/ask" \
       -H "Content-Type: application/json" \
       -d '{"question": "How do I reset my password?"}'
  ```

- **Python Execution**:
  ```python
  import requests

  url = "http://127.0.0.1:8000/ask"
  payload = {"question": "How do I reset my password?"}
  response = requests.post(url, json=payload).json()
  print("Answer:", response["answer"])
  print("Confidence:", response["confidence"])
  ```

- **Output Fields**:
  - `answer`: Grounded response.
  - `confidence`: Grounding weight score.
  - `sources`: Reference filenames list.
  - `explainability`: Diagnostic timeline (returned when `DEBUG_MODE=True`).
  - `execution_trace`: Internal node transitions list (returned when `DEBUG_MODE=True`).

---

## 2. Explainable Diagnostics (`POST /explain`)

- **How it works**:
  Runs the support RAG pipeline and returns the final answer alongside the full diagnostic explainability report.

- **cURL Command**:
  ```bash
  curl -X POST "http://127.0.0.1:8000/explain" \
       -H "Content-Type: application/json" \
       -d '{"question": "What API access limits are enforced?"}'
  ```

---

## 3. Rebuild Database Index (`POST /index`)

- **How it works**:
  Triggers a full rebuild of the FAISS vector database by reading, preprocessing, chunking, and indexing raw markdown and case files. Purges memory caches.

- **cURL Command**:
  ```bash
  curl -X POST "http://127.0.0.1:8000/index"
  ```

---

## 4. Semantic Search (`POST /search`)

- **How it works**:
  Queries the vector store index directly (bypassing LangGraph and LLM answer generation) and returns raw scored text segments.

- **cURL Command**:
  ```bash
  curl -X POST "http://127.0.0.1:8000/search" \
       -H "Content-Type: application/json" \
       -d '{"query": "admin credentials", "top_k": 3, "min_similarity": 0.3}'
  ```

---

## 5. System Status Health (`GET /system/status`)

- **How it works**:
  Exposes CPU/Memory footprints, CUDA status, loaded model singletons, FAISS database metadata hashes, and total document counts.

- **cURL Command**:
  ```bash
  curl -X GET "http://127.0.0.1:8000/system/status"
  ```

---

## 6. Developer Debug endpoints (`GET /debug/*`)

These endpoints assist in tracing state machines and latencies:
- **`GET /debug/history`**: Returns summaries of recent queries.
- **`GET /debug/session/{request_id}`**: Retrieves Mermaid path charts and ASCII event flowcharts.
- **`GET /debug/metrics`**: Displays aggregated timing metrics.
- **`DELETE /debug/history`**: Clears session store logs.

**Example querying a debug session**:
```bash
curl -X GET "http://127.0.0.1:8000/debug/session/req-171828"
```
