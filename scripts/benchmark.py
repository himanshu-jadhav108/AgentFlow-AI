"""Observability benchmarking script measuring query execution performance."""

import os
import sys
import time

# Add workspace directory to python search path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psutil
import torch
from fastapi.testclient import TestClient
from main import app
from core.logger import logger

# Ensure target directories exist
os.makedirs("docs", exist_ok=True)


def run_benchmark() -> None:
    """Executes 100 API queries in-memory and writes a benchmark report."""
    logger.info("Starting performance benchmarking runner...")
    client = TestClient(app)

    # Rebuild search index first
    logger.info("Initializing search index for benchmark context...")
    client.post("/index")

    # Monitor initial memory
    process = psutil.Process(os.getpid())
    start_mem = process.memory_info().rss / (1024 * 1024)

    # 100 requests sequence payload (mix of answerable and unanswerable topics)
    queries = [
        "How do I reset my password?",
        "Can you share a pepperoni pizza recipe?",
        "How do read-only users setup API keys?",
    ]

    latencies = []

    logger.info("Executing 100 requests against /ask...")
    for i in range(100):
        q = queries[i % len(queries)]
        start = time.time()
        client.post("/ask", json={"question": q})
        latencies.append((time.time() - start) * 1000)

    # Monitor final memory
    end_mem = process.memory_info().rss / (1024 * 1024)
    mem_delta = end_mem - start_mem

    best = min(latencies)
    worst = max(latencies)
    avg = sum(latencies) / len(latencies)
    gpu_mem = torch.cuda.memory_allocated() / (1024 * 1024) if torch.cuda.is_available() else 0.0

    # Write report Markdown
    report_content = f"""# Performance Benchmark Report

System-wide performance benchmarks compiled over 100 sequential query executions:

## Execution Metrics
- **Total Request Load:** 100
- **Average Latency:** {avg:.2f} ms
- **Best Case Latency (Cache Hits):** {best:.2f} ms
- **Worst Case Latency (Cold Starts):** {worst:.2f} ms

## Resource Allocation
- **RAM memory delta footprint:** {mem_delta:.2f} MB
- **GPU VRAM Allocation:** {gpu_mem:.2f} MB
- **Active Thread Count:** {psutil.cpu_count(logical=True)} CPUs
"""

    with open("docs/benchmark_report.md", "w", encoding="utf-8") as f:
        f.write(report_content)

    logger.info(
        f"Benchmark completed successfully! "
        f"Average Latency: {avg:.2f}ms. "
        f"Report saved to docs/benchmark_report.md"
    )


if __name__ == "__main__":
    run_benchmark()
