"""Timeline renderer converting timelines into structured ASCII lists."""

from typing import Any, Dict, List


def render_timeline_ascii(timeline: List[Dict[str, Any]]) -> str:
    """Renders a text ASCII flow representation of the execution timeline.

    Args:
        timeline: Timeline events list.

    Returns:
        str: ASCII flowchart string.
    """
    lines = ["Timeline Process Flow:", "====================="]
    for i, event in enumerate(timeline):
        lines.append(
            f"[{i + 1}] {event.get('event', 'Step')} "
            f"({event.get('duration_ms', 0.0):.2f}ms) - {event.get('timestamp', '')}"
        )
        lines.append(f"    Summary: {event.get('summary', '')}")
        if i < len(timeline) - 1:
            lines.append("        ↓")
    return "\n".join(lines)
