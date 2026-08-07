# Execution Tracing

AgentFlow AI tracks timing, decisions, and summaries for every single LangGraph node step.

---

## State Diagram Flow

Every node appends details using `record_node_trace`:

```
START ──► Triage ──► Retrieve ──► Generate ──► Verify ──► END
  │         │          │            │          │         │
  ▼         ▼          ▼            ▼          ▼         ▼
[Trace]  [Trace]    [Trace]      [Trace]    [Trace]   [Trace]
```

---

## Fields Tracked
The trace object stored inside `AgentState` contains:
- `request_id`: Core correlation ID.
- `question`: User query string.
- `graph_path`: Sequence of visited nodes.
- `retriever_time_ms`: Cumulative time spent in similarity searches.
- `generation_time_ms`: Cumulative time spent in inference generations.
- `verification_time_ms`: Cumulative time spent in rule & semantic checking.
- `retry_count`: Verification failures count.
- `total_execution_time_ms`: Total latency in milliseconds.
- `nodes`: List of step dictionaries.
