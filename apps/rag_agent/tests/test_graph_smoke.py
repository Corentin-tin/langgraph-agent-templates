"""Smoke tests for the RAG agent graphs."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from rag_agent.graph import build_indexer_graph, build_retrieval_graph, build_researcher_graph
from rag_agent.utils.state import AgentState, IndexState, ResearcherState


@pytest.mark.asyncio
async def test_indexer_graph_builds():
    """Test that the indexer graph builds without errors."""
    graph = build_indexer_graph()
    assert graph is not None


@pytest.mark.asyncio
async def test_retrieval_graph_builds():
    """Test that the retrieval graph builds without errors."""
    graph = build_retrieval_graph()
    assert graph is not None


@pytest.mark.asyncio
async def test_researcher_graph_builds():
    """Test that the researcher graph builds without errors."""
    graph = build_researcher_graph()
    assert graph is not None


@pytest.mark.asyncio
async def test_indexer_graph_basic_invoke():
    """Test basic indexer graph invocation with mocked dependencies."""
    with (
        patch("rag_agent.utils.nodes.load_sample_documents") as mock_load_docs,
        patch("rag_agent.utils.nodes.load_embeddings") as mock_embeddings,
        patch("rag_agent.utils.nodes.load_vector_store") as mock_vector_store,
    ):

        # Mock sample documents
        mock_load_docs.return_value = [
            MagicMock(page_content="Test content", metadata={"source": "test"})
        ]

        # Mock embeddings and vector store
        mock_embeddings.return_value = MagicMock()
        mock_store = AsyncMock()
        mock_store.aadd_documents = AsyncMock()
        mock_vector_store.return_value = mock_store

        graph = build_indexer_graph()

        input_state = IndexState(documents=[])
        result = await graph.ainvoke(input_state)

        assert result is not None
        assert "indexed_count" in result


@pytest.mark.asyncio
async def test_retrieval_graph_basic_invoke():
    """Test basic retrieval graph invocation with mocked dependencies."""
    with (
        patch("rag_agent.utils.nodes.load_chat_model_from_env") as mock_load_model,
        patch("rag_agent.utils.nodes.load_embeddings") as mock_embeddings,
        patch("rag_agent.utils.nodes.load_vector_store") as mock_vector_store,
    ):

        # Mock chat model
        mock_model = AsyncMock()
        mock_model.ainvoke.return_value = MagicMock(content='{"datasource": "general"}')
        mock_load_model.return_value = mock_model

        # Mock embeddings and vector store
        mock_embeddings.return_value = MagicMock()
        mock_store = AsyncMock()
        mock_store.asimilarity_search = AsyncMock(return_value=[])
        mock_vector_store.return_value = mock_store

        graph = build_retrieval_graph()

        input_state = AgentState(messages=[{"role": "human", "content": "What is LangGraph?"}])

        result = await graph.ainvoke(input_state)

        assert result is not None
        assert "messages" in result


@pytest.mark.asyncio
async def test_researcher_graph_basic_invoke():
    """Test basic researcher graph invocation with mocked dependencies."""
    with (
        patch("rag_agent.utils.nodes.load_chat_model_from_env") as mock_load_model,
        patch("rag_agent.utils.nodes.load_embeddings") as mock_embeddings,
        patch("rag_agent.utils.nodes.load_vector_store") as mock_vector_store,
    ):

        # Mock chat model
        mock_model = AsyncMock()
        mock_model.ainvoke.return_value = MagicMock(
            content="1. Query about topic\n2. Another query"
        )
        mock_load_model.return_value = mock_model

        # Mock embeddings and vector store
        mock_embeddings.return_value = MagicMock()
        mock_store = AsyncMock()
        mock_store.asimilarity_search = AsyncMock(return_value=[])
        mock_vector_store.return_value = mock_store

        graph = build_researcher_graph()

        input_state = ResearcherState(research_question="What is the latest in AI research?")

        result = await graph.ainvoke(input_state)

        assert result is not None
        assert "documents" in result
