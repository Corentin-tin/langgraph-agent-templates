"""Node implementations for the React agent graph."""

from datetime import UTC, datetime
from typing import Any, Dict, List, Literal, cast

from langchain_core.messages import AIMessage
from langgraph.prebuilt import ToolNode

from shared.logging import get_logger
from ..state import State
from .state import Context
from .tools import TOOLS

# System prompt is defined in the Context class


logger = get_logger(__name__)


def load_chat_model(fully_specified_name: str) -> Any:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.
    """
    from langchain.chat_models import init_chat_model

    provider, model = fully_specified_name.split("/", maxsplit=1)
    return init_chat_model(model, model_provider=provider)


async def call_model(state: State, context: Context | None = None) -> Dict[str, List[AIMessage]]:
    """Call the language model with the current state.

    This node represents the "Think" step in the ReAct pattern.
    """
    if context is None:
        context = Context()

    model = load_chat_model(context.model).bind_tools(TOOLS)

    system_message = context.system_prompt.format(system_time=datetime.now(tz=UTC).isoformat())

    messages = [{"role": "system", "content": system_message}] + list(state.messages)

    logger.info("Calling model", model=context.model, message_count=len(messages))

    response = cast(
        AIMessage,
        await model.ainvoke(messages),
    )

    # If we're at max iterations and model still wants to use tools, stop
    if state.is_last_step and response.tool_calls:
        logger.warning("Reached max iterations with pending tool calls")
        return {
            "messages": [
                AIMessage(
                    id=response.id,
                    content="Sorry, I could not find an answer to your question in the specified number of steps.",
                )
            ]
        }

    return {"messages": [response]}


def route_model_output(state: State) -> Literal["__end__", "tools"]:
    """Route the model output to either tools or end.

    This represents the decision point in the ReAct pattern.
    """
    last_message = state.messages[-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError(
            f"Expected AIMessage in output edges, but got {type(last_message).__name__}"
        )

    if not last_message.tool_calls:
        logger.info("Model completed without tool calls - ending")
        return "__end__"

    logger.info("Model requested tool calls", tool_count=len(last_message.tool_calls))
    return "tools"


# Create the tool node for the "Act" step in ReAct
tools_node = ToolNode(TOOLS)
