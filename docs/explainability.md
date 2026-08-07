# AI Explainability Engine

This document details the explainability engine design and implementation.

---

## 1. What is Explainability?
Explainability in AI Support describes explaining the engineering steps (retrieval databases, thresholds, validation rule checks) that produced the answer, rather than trying to explain the deep neural weights of the LLM.

## 2. Engineering Explainability
We focus on **deterministic pipeline diagnostics** (how many chunks match, similarity thresholds, verifier results, timing milestones).

## 3. Why NOT Chain-of-Thought
We never expose or fabricate model Chain-of-Thought (CoT) because:
1. It is non-deterministic and prone to hallucinated explanations.
2. It increases latency and token costs.
3. Exposing raw internal thoughts can leak system prompts and proprietary context.

## 4. Retrieval Summary
We compile chunks processed, total files searched, and top similarity ratings.

## 5. Verification Summary
Shows whether rules validation passed/failed, semantic check results, and loop retry counts.

## 6. Confidence Breakdown
Total confidence is computed using a weighted formula:
- Retrieval similarity: 40%
- Source coverage: 25%
- Grounding verification: 25%
- Output consistency: 10%

## 7. Execution Timeline
Lists steps from Request Received through Triage, Retrieval, Generation, and Verification, including exact timestamps.

## 8. Source Analysis
Analyzes citations count, uniqueness, and diversity across retrieved passages.

## 9. Architecture
```
[AgentState] ──► ExplanationBuilder ──► Source / Timeline Analyzers ──► JSON Report
```

## 10. Interview Questions
- **Q**: What's the main difference between model explainability and system explainability?
  - **A**: Model explainability analyzes weight distributions and neural activations. System explainability details engineering pipeline stages and validations.

## 11. Homework
- **Exercise**: Implement a warnings detector that alerts developers if retrieved chunks originate from deprecated documentation files.

## 12. Quiz
1. Which factor contributes 40% to confidence?
   - [x] Retrieval similarity
   - [ ] Grounding verification
   - [ ] Source coverage

## 13. Best Practices
- Never let the model generate explanations about its own reliability. Use deterministic code statistics.

## 14. Summary
The explainability engine compiles data, timeline events, and confidence factors, exposing them under `/ask` and `POST /explain` when `DEBUG_MODE=True`.
