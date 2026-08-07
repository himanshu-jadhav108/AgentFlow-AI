"""LangGraph workflow builder for local support agent orchestration."""

from typing import Any
from langgraph.graph import END, START, StateGraph
from app.state.agent_state import AgentState
from app.nodes.start import start_node
from app.nodes.triage import triage_node
from app.nodes.retrieve import retrieve_node
from app.nodes.generate import generate_node
from app.nodes.verify import verify_node
from app.nodes.clarification import clarification_node
from app.nodes.escalation import escalation_node
from app.nodes.out_of_scope import out_of_scope_node
from app.nodes.end import end_node
from app.routing.conditions import route_after_triage, route_after_retrieve, route_after_verify
from core.logger import logger


def build_graph() -> Any:
    """Configures nodes, transitions, and conditional routing edges, compiling the graph.

    Returns:
        CompiledGraph: The compiled executable LangGraph instance.
    """
    logger.info("Initializing StateGraph configuration...")

    # 1. Instantiate the stateful graph builder
    workflow = StateGraph(AgentState)

    # 2. Add node functions to the graph
    workflow.add_node("start", start_node)
    workflow.add_node("triage", triage_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("generate", generate_node)
    workflow.add_node("verify", verify_node)
    workflow.add_node("clarification", clarification_node)
    workflow.add_node("escalation", escalation_node)
    workflow.add_node("out_of_scope", out_of_scope_node)
    workflow.add_node("end", end_node)

    # 3. Define control flow edges
    workflow.add_edge(START, "start")
    workflow.add_edge("start", "triage")

    # Conditional edge routing after Triage Node
    workflow.add_conditional_edges(
        "triage",
        route_after_triage,
        {
            "retrieve": "retrieve",
            "clarification": "clarification",
            "escalation": "escalation",
            "out_of_scope": "out_of_scope",
        },
    )

    # Conditional edge routing after Retrieve Node pointing to generate node
    workflow.add_conditional_edges(
        "retrieve",
        route_after_retrieve,
        {
            "generate": "generate",
        },
    )

    # Linear transition from Generate to Verify
    workflow.add_edge("generate", "verify")

    # Conditional edge routing after Verify Node (loops back or terminates)
    workflow.add_conditional_edges(
        "verify",
        route_after_verify,
        {
            "generate": "generate",
            "end": "end",
        },
    )

    # Terminal routes pointing to final End Node
    workflow.add_edge("clarification", "end")
    workflow.add_edge("escalation", "end")
    workflow.add_edge("out_of_scope", "end")
    workflow.add_edge("end", END)

    logger.info("Compiling the LangGraph workflow...")
    compiled_graph = workflow.compile()
    logger.info("LangGraph workflow compiled successfully.")
    return compiled_graph
