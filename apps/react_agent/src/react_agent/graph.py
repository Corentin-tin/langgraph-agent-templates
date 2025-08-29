"""Core graph definition for the React agent."""

from typing import Any

from langgraph.graph import StateGraph

from shared.logging import get_logger
from .state import InputState, State
from .utils.state import Context
from .utils.nodes import call_model, route_model_output, tools_node

logger = get_logger(__name__)


def build_graph() -> Any:
    """Build and return the ReAct agent graph."""
    logger.info("Building ReAct agent graph")

    # Create the graph with proper state and context schemas
    builder = StateGraph(State, input_schema=InputState, context_schema=Context)

    # Add nodes
    builder.add_node("call_model", call_model)
    builder.add_node("tools", tools_node)

    # Set entry point
    builder.set_entry_point("call_model")

    # Add conditional edge from model to either tools or end
    builder.add_conditional_edges("call_model", route_model_output)

    # Add edge from tools back to model for the ReAct loop
    builder.add_edge("tools", "call_model")

    # Compile the graph
    graph = builder.compile()

    logger.info("ReAct agent graph built successfully")
    return graph
