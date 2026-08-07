"""Graph renderer converting graph paths into Mermaid representations."""

from typing import List


def render_graph_mermaid(graph_path: List[str]) -> str:
    """Creates a Mermaid flowchart diagram showing visited nodes.

    Args:
        graph_path: List of visited node names.

    Returns:
        str: Mermaid syntax string.
    """
    if not graph_path:
        return "graph TD;\n    start[START] --> end[END];"

    lines = ["graph LR;"]
    # Node formatting definitions
    for node in set(graph_path):
        lines.append(f'    {node}["{node.capitalize()} Node"];')

    # Connections definitions
    for i in range(len(graph_path) - 1):
        lines.append(f"    {graph_path[i]} --> {graph_path[i + 1]};")

    return "\n".join(lines)
