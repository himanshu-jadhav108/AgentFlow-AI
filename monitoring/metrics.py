"""System metrics manager for capturing production observability data."""

from threading import Lock
from typing import Any, Dict, List, Optional


class SystemMetrics:
    """Thread-safe statistics collector capturing system latency and load counts."""

    _instance: Optional["SystemMetrics"] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "SystemMetrics":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_metrics()
        return cls._instance

    def _init_metrics(self) -> None:
        self._lock = Lock()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_retries = 0

        # Latency lists for running averages (capped at 1000 items to limit memory footprint)
        self.response_times: List[float] = []
        self.retriever_times: List[float] = []
        self.generation_times: List[float] = []
        self.verification_times: List[float] = []
        self.model_load_time_ms = 0.0

    def record_request(self, success: bool, duration_ms: float) -> None:
        """Records API call result and execution latency."""
        with self._lock:
            self.total_requests += 1
            if success:
                self.successful_requests += 1
            else:
                self.failed_requests += 1
            self.response_times.append(duration_ms)
            if len(self.response_times) > 1000:
                self.response_times.pop(0)

    def record_retriever(self, duration_ms: float) -> None:
        """Records FAISS vector search execution duration."""
        with self._lock:
            self.retriever_times.append(duration_ms)
            if len(self.retriever_times) > 1000:
                self.retriever_times.pop(0)

    def record_generation(self, duration_ms: float) -> None:
        """Records LLM token generation inference duration."""
        with self._lock:
            self.generation_times.append(duration_ms)
            if len(self.generation_times) > 1000:
                self.generation_times.pop(0)

    def record_verification(self, duration_ms: float) -> None:
        """Records grounding rules and semantic validation duration."""
        with self._lock:
            self.verification_times.append(duration_ms)
            if len(self.verification_times) > 1000:
                self.verification_times.pop(0)

    def record_retries(self, count: int) -> None:
        """Accumulates retry loop execution counts."""
        with self._lock:
            self.total_retries += count

    def record_model_load(self, duration_ms: float) -> None:
        """Saves initial model loading and initialization latency."""
        with self._lock:
            self.model_load_time_ms = duration_ms

    def get_summary(self) -> Dict[str, Any]:
        """Calculates averages and returns metrics summary.

        Returns:
            Dict[str, Any]: JSON-serializable observability dictionary.
        """
        with self._lock:
            avg_resp = sum(self.response_times) / len(self.response_times) if self.response_times else 0.0
            avg_ret = sum(self.retriever_times) / len(self.retriever_times) if self.retriever_times else 0.0
            avg_gen = sum(self.generation_times) / len(self.generation_times) if self.generation_times else 0.0
            avg_ver = sum(self.verification_times) / len(self.verification_times) if self.verification_times else 0.0

            return {
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "total_retries": self.total_retries,
                "avg_response_time_ms": round(avg_resp, 2),
                "avg_retriever_time_ms": round(avg_ret, 2),
                "avg_generation_time_ms": round(avg_gen, 2),
                "avg_verification_time_ms": round(avg_ver, 2),
                "model_load_time_ms": round(self.model_load_time_ms, 2),
            }


# Expose system metrics instance globally
metrics = SystemMetrics()
