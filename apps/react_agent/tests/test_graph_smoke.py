"""Smoke tests for the React agent graph."""

import pytest
from unittest.mock import AsyncMock, patch

from react_agent.graph import build_graph
from react_agent.state import InputState


@pytest.mark.asyncio
async def test_graph_builds():
    """Test that the graph builds without errors."""
    graph = build_graph()
    assert graph is not None


@pytest.mark.asyncio
async def test_graph_basic_invoke():
    """Test basic graph invocation with mocked dependencies."""
    with patch("react_agent.utils.nodes.load_chat_model") as mock_load_model:
        # Mock the chat model
        mock_model = AsyncMock()
        mock_model.bind_tools.return_value = mock_model
        mock_model.ainvoke.return_value = type(
            "AIMessage",
            (),
            {"content": "Hello! How can I help you today?", "tool_calls": [], "id": "test-id"},
        )()
        mock_load_model.return_value = mock_model

        graph = build_graph()

        # Test basic invocation
        input_state = InputState(messages=[{"role": "human", "content": "Hello, who are you?"}])

        result = await graph.ainvoke(input_state)
        assert result is not None
        assert "messages" in result


@pytest.mark.asyncio
async def test_graph_with_context():
    """Test graph invocation with custom context."""
    with patch("react_agent.utils.nodes.load_chat_model") as mock_load_model:
        mock_model = AsyncMock()
        mock_model.bind_tools.return_value = mock_model
        mock_model.ainvoke.return_value = type(
            "AIMessage", (), {"content": "Test response", "tool_calls": [], "id": "test-id"}
        )()
        mock_load_model.return_value = mock_model

        graph = build_graph()

        # Test with custom context
        from react_agent.utils.state import Context

        context = Context(model="anthropic/claude-3-5-sonnet-20240620", max_search_results=5)

        input_state = InputState(messages=[{"role": "human", "content": "Test message"}])

        result = await graph.ainvoke(input_state, context=context)
        assert result is not None
