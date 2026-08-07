"""Dashboard service coordinating session stores, diagnostic reports, and clear options."""

import time
from typing import Any, Dict, List, Optional
from app.dashboard.dashboard_formatter import compile_debug_session_report
from app.dashboard.dashboard_models import DebugSessionReport
from app.dashboard.session_store import debug_session_store
from app.explainability.explanation_builder import ExplanationBuilder
from core.logger import logger


class DashboardService:
    """Orchestrator for managing developer debug logs and history exports."""

    @staticmethod
    def capture_run(
        request_id: str,
        question: str,
        classification: str,
        final_state: Dict[str, Any],
        response: Dict[str, Any],
    ) -> None:
        """Assembles and stores a debug trace snapshot after workflow completion.

        Args:
            request_id: Correlation query ID.
            question: Original question.
            classification: Final triage classification.
            final_state: Final mutated state dictionary.
            response: Final returned API JSON dict.
        """
        # Compile explainability report using our ExplainabilityBuilder
        report = ExplanationBuilder.build_report(final_state)

        session_data = {
            "request_id": request_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "question": question,
            "classification": classification,
            "confidence": final_state.get("confidence", 0.0),
            "latency_ms": final_state.get("execution_trace", {}).get(
                "total_execution_time_ms", 0.0
            ),
            "final_response": response,
            "execution_trace": final_state.get("execution_trace", {}),
            "explainability_report": report.model_dump(),
        }

        debug_session_store.store_session(request_id, session_data)

    @staticmethod
    def get_session_report(request_id: str) -> Optional[DebugSessionReport]:
        """Compiles and returns the structured DebugSessionReport for a query.

        Args:
            request_id: Correlation query ID.

        Returns:
            Optional[DebugSessionReport]: Formatted report, or None.
        """
        session = debug_session_store.get_session(request_id)
        if not session:
            return None

        # Build metrics and timelines using dashboard_formatter
        return compile_debug_session_report(session)

    @staticmethod
    def get_history() -> List[Dict[str, Any]]:
        """Returns summaries of recent requests.

        Returns:
            List[Dict[str, Any]]: Summary history list.
        """
        return debug_session_store.get_history_summaries()

    @staticmethod
    def get_aggregated_metrics() -> Dict[str, Any]:
        """Aggregates latency timing metrics from all stored sessions.

        Returns:
            Dict[str, Any]: Consolidated timing statistics.
        """
        summaries = debug_session_store.get_history_summaries()
        total_sessions = len(summaries)

        if total_sessions == 0:
            return {
                "total_queries_captured": 0,
                "average_latency_ms": 0.0,
                "max_latency_ms": 0.0,
                "min_latency_ms": 0.0,
            }

        latencies = [s["latency_ms"] for s in summaries]
        avg_latency = sum(latencies) / total_sessions

        return {
            "total_queries_captured": total_sessions,
            "average_latency_ms": round(avg_latency, 2),
            "max_latency_ms": round(max(latencies), 2),
            "min_latency_ms": round(min(latencies), 2),
        }

    @staticmethod
    def clear_history() -> None:
        """Purges stored history caches."""
        debug_session_store.clear()
