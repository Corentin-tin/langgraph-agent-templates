"""State and context definitions for the React agent."""

import os
from dataclasses import dataclass, field, fields
from typing import Annotated

from shared.logging import get_logger

logger = get_logger(__name__)


@dataclass(kw_only=True)
class Context:
    """The context configuration for the React agent."""

    system_prompt: str = field(
        default="You are a helpful AI assistant.\n\nSystem time: {system_time}",
        metadata={
            "description": "The system prompt to use for the agent's interactions. "
            "This prompt sets the context and behavior for the agent."
        },
    )

    model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="openai/gpt-4o",
        metadata={
            "description": "The name of the language model to use for the agent's main interactions. "
            "Should be in the form: provider/model-name."
        },
    )

    max_search_results: int = field(
        default=10,
        metadata={
            "description": "The maximum number of search results to return for each search query."
        },
    )

    max_iterations: int = field(
        default=10,
        metadata={"description": "Maximum number of reasoning iterations before stopping."},
    )

    def __post_init__(self) -> None:
        """Fetch env vars for attributes that were not passed as args."""
        for f in fields(self):
            if not f.init:
                continue

            if getattr(self, f.name) == f.default:
                env_value = os.environ.get(f.name.upper(), f.default)
                setattr(self, f.name, env_value)
                logger.debug("Loaded config from environment", field=f.name, value=env_value)
