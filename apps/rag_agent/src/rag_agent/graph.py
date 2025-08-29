"""Graph definitions for the RAG agent."""

from typing import Literal

from langgraph.graph import StateGraph, START, END

from shared.logging import get_logger
from .utils.state import AgentState, ResearcherState, IndexState
from .utils.nodes import (
    # Index graph nodes
    index_docs,
    # Main graph nodes
    query_analysis,
    research_planner,
    retrieve_docs,
    generate_response,
    # Researcher subgraph nodes
    generate_queries,
    research_step,
)

logger = get_logger(__name__)


def route_query(
    state: AgentState,
) -> Literal["research_planner", "retrieve_docs", "generate_response"]:
    """Route based on query analysis."""
    analysis = state.query_analysis or "general"

    logger.info("Routing query", analysis=analysis)

    if analysis == "langchain":
        return "retrieve_docs"
    elif analysis == "more-info":
        return "research_planner"
    else:
        return "generate_response"


def build_indexer_graph():
    """Build the document indexing graph."""
    logger.info("Building indexer graph")

    builder = StateGraph(IndexState)

    # Add nodes
    builder.add_node("index_docs", index_docs)

    # Add edges
    builder.add_edge(START, "index_docs")
    builder.add_edge("index_docs", END)

    graph = builder.compile()
    logger.info("Indexer graph built successfully")

    return graph


def build_researcher_graph():
    """Build the researcher subgraph."""
    logger.info("Building researcher subgraph")

    builder = StateGraph(ResearcherState)

    # Add nodes
    builder.add_node("generate_queries", generate_queries)
    builder.add_node("research_step", research_step)

    # Add edges
    builder.add_edge(START, "generate_queries")
    builder.add_edge("generate_queries", "research_step")
    builder.add_edge("research_step", END)

    graph = builder.compile()
    logger.info("Researcher subgraph built successfully")

    return graph


def build_retrieval_graph():
    """Build the main retrieval and response graph."""
    logger.info("Building retrieval graph")

    builder = StateGraph(AgentState)

    # Add nodes
    builder.add_node("query_analysis", query_analysis)
    builder.add_node("research_planner", research_planner)
    builder.add_node("retrieve_docs", retrieve_docs)
    builder.add_node("generate_response", generate_response)

    # Add edges
    builder.add_edge(START, "query_analysis")

    # Conditional routing based on query analysis
    builder.add_conditional_edges(
        "query_analysis",
        route_query,
        {
            "research_planner": "research_planner",
            "retrieve_docs": "retrieve_docs",
            "generate_response": "generate_response",
        },
    )

    # Research planning flow
    builder.add_edge("research_planner", "retrieve_docs")

    # All paths lead to response generation
    builder.add_edge("retrieve_docs", "generate_response")
    builder.add_edge("generate_response", END)

    graph = builder.compile()
    logger.info("Retrieval graph built successfully")

    return graph


# Create graph instances
indexer_graph = build_indexer_graph()
retrieval_graph = build_retrieval_graph()
researcher_graph = build_researcher_graph()
