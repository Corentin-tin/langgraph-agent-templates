"""FastAPI server for the RAG agent."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from langgraph.server import add_routes
from shared.logging import setup_logging, get_logger
from shared.settings import RagAgentSettings

from .graph import indexer_graph, retrieval_graph


settings = RagAgentSettings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    setup_logging(settings.log_level)
    logger.info("Starting RAG Agent server", port=settings.rag_agent_port)
    yield
    logger.info("Shutting down RAG Agent server")


app = FastAPI(
    title="RAG Agent",
    description="Retrieval-Augmented Generation agent using LangGraph",
    version="0.1.0",
    lifespan=lifespan,
)

# Add routes for both graphs
add_routes(app, indexer_graph, path="/indexer")
add_routes(app, retrieval_graph, path="/")


@app.get("/healthz")
async def health() -> dict[str, bool]:
    """Health check endpoint."""
    return {"ok": True}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with API information."""
    return {
        "message": "RAG Agent API",
        "endpoints": {
            "indexer": "/indexer - Document indexing graph",
            "retrieval": "/ - Main retrieval and response graph",
            "health": "/healthz - Health check",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "rag_agent.server:app",
        host=settings.rag_agent_host,
        port=settings.rag_agent_port,
        reload=True,
    )
