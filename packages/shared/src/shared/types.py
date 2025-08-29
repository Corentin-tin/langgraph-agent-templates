"""Common type definitions for LangGraph agents."""

from typing import TypedDict, List, Dict, Any, Literal
from pydantic import BaseModel


# Message types compatible with LangChain
class BaseMessage(TypedDict):
    """Base message structure compatible with LangChain."""

    type: Literal["human", "ai", "system", "function"]
    content: str


class HumanMessage(TypedDict):
    """Human message."""

    type: Literal["human"]
    content: str


class AIMessage(TypedDict):
    """AI message."""

    type: Literal["ai"]
    content: str


class SystemMessage(TypedDict):
    """System message."""

    type: Literal["system"]
    content: str


class FunctionMessage(TypedDict):
    """Function/tool message."""

    type: Literal["function"]
    content: str
    name: str


# Tool-related types
class ToolCall(BaseModel):
    """Tool call information."""

    id: str
    name: str
    args: Dict[str, Any]


class ToolResult(BaseModel):
    """Tool execution result."""

    tool_call_id: str
    content: str
    is_error: bool = False


# Common state components
class BaseState(TypedDict, total=False):
    """Base state with common fields."""

    messages: List[BaseMessage]
    user_id: str | None
    session_id: str | None
    metadata: Dict[str, Any]
