"""FastAPI server for the React agent."""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from langgraph.server import add_routes
from shared.logging import setup_logging, get_logger
from shared.settings import ReactAgentSettings

from .graph import build_graph


settings = ReactAgentSettings()

# Set environment variables from settings so LangChain can find them
if settings.openai_api_key:
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key
if settings.anthropic_api_key:
    os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key
if settings.langchain_api_key:
    os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    setup_logging(settings.log_level)
    logger.info("Starting React Agent server", port=settings.react_agent_port)
    yield
    logger.info("Shutting down React Agent server")


app = FastAPI(
    title="React Agent",
    description="ReAct pattern agent implementation using LangGraph",
    version="0.1.0",
    lifespan=lifespan,
)

graph = build_graph()
add_routes(app, graph, path="/")


@app.get("/healthz")
async def health() -> dict[str, bool]:
    """Health check endpoint."""
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "react_agent.server:app",
        host=settings.react_agent_host,
        port=settings.react_agent_port,
        reload=True,
    )
