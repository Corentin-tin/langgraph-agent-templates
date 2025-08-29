"""Shared settings configuration using Pydantic."""

from pydantic_settings import BaseSettings
from typing import Literal


class BaseAppSettings(BaseSettings):
    """Base settings for all applications."""

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    environment: Literal["development", "staging", "production"] = "development"

    # LLM Configuration
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    # LangSmith Configuration (optional)
    langchain_tracing_v2: bool = False
    langchain_api_key: str | None = None
    langchain_project: str = "langgraph-agents"

    class Config:
        env_file = ".env"
        extra = "ignore"


class ReactAgentSettings(BaseAppSettings):
    """Settings specific to the React agent."""

    react_agent_host: str = "0.0.0.0"
    react_agent_port: int = 2024


class RagAgentSettings(BaseAppSettings):
    """Settings specific to the RAG agent."""

    rag_agent_host: str = "0.0.0.0"
    rag_agent_port: int = 2025

    # Vector store configuration
    qdrant_url: str | None = None
    qdrant_api_key: str | None = None
