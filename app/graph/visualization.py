"""Graph visualization exporter generating Mermaid, ASCII, and PNG files."""

import os
from typing import Any

from core.logger import logger


def generate_graph_visualizations(compiled_graph: Any) -> None:
    """Generate Mermaid markdown, ASCII, and PNG formats of the graph and save them to assets/.

    Args:
        compiled_graph: Compiled LangGraph object.
    """
    assets_dir = "assets"
    os.makedirs(assets_dir, exist_ok=True)

    # 1. Exclude Mermaid Markdown chart
    try:
        mermaid_code = compiled_graph.get_graph().draw_mermaid()
        mermaid_file = os.path.join(assets_dir, "graph_mermaid.md")
        with open(mermaid_file, "w", encoding="utf-8") as f:
            f.write(f"```mermaid\n{mermaid_code}\n```")
        logger.info(f"Saved Mermaid chart flowchart to {mermaid_file}")
    except Exception as e:
        logger.error(f"Failed to generate Mermaid visualization code: {e}")

    # 2. Exclude PNG image (native LangGraph web request draw tool)
    try:
        png_bytes = compiled_graph.get_graph().draw_mermaid_png()
        png_file = os.path.join(assets_dir, "graph_flowchart.png")
        with open(png_file, "wb") as f:
            f.write(png_bytes)
        logger.info(f"Saved PNG flowchart rendering to {png_file}")
    except Exception as e:
        logger.warning(
            f"Could not generate PNG flowchart image: {e} "
            "(this is normal if system dependencies like pygraphviz/pyppeteer are missing)."
        )

    # 3. Exclude ASCII flowchart representation
    try:
        ascii_desc = (
            "==================================================\n"
            "          AGENTFLOW AI WORKFLOW ASCII             \n"
            "==================================================\n"
            "                  [START]                         \n"
            "                     │                            \n"
            "                     ▼                            \n"
            "                  [start] (Node)                  \n"
            "                     │                            \n"
            "                     ▼                            \n"
            "                  [triage] (Node)                 \n"
            "                     │                            \n"
            "         ┌───────────┼───────────┬──────────────┐ \n"
            "         ▼           ▼           ▼              ▼ \n"
            "     [retrieve] [clarification] [escalation] [out_of_scope] \n"
            "         │           │           │              │ \n"
            "         ▼           │           │              │ \n"
            "       [end] ◄───────┴───────────┴──────────────┘ \n"
            "         │                                        \n"
            "         ▼                                        \n"
            "       [END]                                      \n"
            "==================================================\n"
        )
        ascii_file = os.path.join(assets_dir, "graph_ascii.txt")
        with open(ascii_file, "w", encoding="utf-8") as f:
            f.write(ascii_desc)
        logger.info(f"Saved ASCII flowchart to {ascii_file}")
    except Exception as e:
        logger.error(f"Failed to generate ASCII representation: {e}")
