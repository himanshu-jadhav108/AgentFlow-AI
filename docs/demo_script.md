# Demo Script: 10-Minute AgentFlow AI Walkthrough

This demo script guides you through demonstrating the core capabilities of AgentFlow AI.

---

## 1. Introduction (1 Minute)
- **Objective**: Explain the purpose of AgentFlow AI.
- **Action**: Outline the system's goals: local execution, Clean Architecture, hybrid verification, and explainability.

## 2. Architecture & Folder Tour (2 Minutes)
- **Objective**: Walk through the code structure.
- **Action**: Point out the primary modules:
  - `config/`: Dynamic configuration profiles overrides.
  - `app/core/`: Interfaces, registries, and trace helpers.
  - `app/explainability/`: Timelines, warning logs, and pipeline breakdowns.
  - `app/dashboard/`: Debug session store history and endpoints.
  - `scripts/`: System setup, index rebuilds, and weight downloads.

## 3. Setup & Startup Sequence (1 Minute)
- **Objective**: Show how the system starts up.
- **Action**: Explain the startup validations:
  - Runs `python scripts/setup.py` to check system requirements and run tests.
  - Highlights the automatic model download and FAISS index check.

## 4. Swagger UI & Endpoints (2 Minutes)
- **Objective**: Demonstrate API routes.
- **Action**: Open a browser and navigate to `http://localhost:8000/docs`:
  - Show `/system/status` health metrics.
  - Submits a query to `/ask` to show the answer, sources, and metadata.

## 5. Verification & Self-Correction (2 Minutes)
- **Objective**: Demonstrate the retry loop.
- **Action**: Show how a failed grounding verification routes execution back to the generator, updating the state's `retry_count` and appending system revision feedback to the prompt.

## 6. Explainability & Dashboard (1.5 Minutes)
- **Objective**: Explain why an answer was generated.
- **Action**: Submit a query to `/explain` (or `/ask` with `DEBUG_MODE=True`):
  - View the returned pipeline timeline, confidence breakdown, and source coverage ratios.
  - Query `/debug/history` and `/debug/metrics` to show the developer dashboard statistics.

## 7. Conclusion (0.5 Minutes)
- **Objective**: Wrap up.
- **Action**: Summarize: the agent runs entirely on local resources, enforces factual correctness through hybrid verification, and provides full execution transparency.
