"""Pretty-print execution traces using Rich console formatting."""

from typing import Any, Dict
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class DebugLogger:
    """Formatter to display detailed node-by-node timelines in console."""

    def __init__(self) -> None:
        """Initializes Rich Console instance."""
        self.console = Console()

    def log_trace(self, trace: Dict[str, Any]) -> None:
        """Outputs panel blocks and formatted tables detailing graph iterations.

        Args:
            trace: Dictionary containing execution trace metrics.
        """
        if not trace:
            return

        title = f"[bold green]Execution Trace Report - Request ID: {trace.get('request_id')}[/bold green]"
        info = (
            f"[bold]Question:[/bold] {trace.get('question')}\n"
            f"[bold]Decision:[/bold] {trace.get('final_decision')}\n"
            f"[bold]Confidence:[/bold] {trace.get('confidence', 0.0):.2f}\n"
            f"[bold]Retries:[/bold] {trace.get('retry_count', 0)}\n"
            f"[bold]Total Latency:[/bold] {trace.get('total_execution_time_ms', 0.0):.2f} ms"
        )
        self.console.print(Panel(info, title=title, border_style="cyan"))

        table = Table(
            title="Visited Nodes Timeline",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Node Name", style="cyan")
        table.add_column("Timestamp", style="dim")
        table.add_column("Duration", justify="right", style="green")
        table.add_column("Decision", style="yellow")
        table.add_column("Summary", style="white")

        for node in trace.get("nodes", []):
            table.add_row(
                node.get("node_name", "unknown"),
                node.get("timestamp", "N/A"),
                f"{node.get('duration_ms', 0.0):.2f} ms",
                node.get("decision", "continue"),
                node.get("output_summary", ""),
            )

        self.console.print(table)


# Global logger instance
debug_logger = DebugLogger()
