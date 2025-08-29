"""State definitions for the RAG agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from langchain_core.documents import Document
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from typing_extensions import Annotated


def add_documents(left: List[Document] | None, right: List[Document] | None) -> List[Document]:
    """Add documents with deduplication based on content."""
    if not left:
        left = []
    if not right:
        right = []

    # Use dict to deduplicate by source and content
    seen = {}
    for doc in left + right:
        key = (doc.metadata.get("source", ""), doc.page_content)
        if key not in seen:
            seen[key] = doc

    return list(seen.values())


@dataclass
class InputState:
    """Input state for the RAG agent."""

    messages: Annotated[Sequence[AnyMessage], add_messages] = field(default_factory=list)


@dataclass
class AgentState(InputState):
    """Complete state for the RAG retrieval graph."""

    # Query routing
    query_analysis: str | None = field(default=None)

    # Research planning
    research_plan: str | None = field(default=None)
    steps: List[str] = field(default_factory=list)

    # Documents and retrieval
    documents: Annotated[List[Document], add_documents] = field(default_factory=list)
    retrieved_docs: Annotated[List[Document], add_documents] = field(default_factory=list)

    # Response generation
    answer: str | None = field(default=None)

    # Metadata
    user_id: str | None = field(default=None)
    session_id: str | None = field(default=None)


@dataclass
class ResearcherState:
    """State for the researcher subgraph."""

    # Research queries
    research_question: str = field(default="")
    queries: List[str] = field(default_factory=list)

    # Retrieved documents
    documents: Annotated[List[Document], add_documents] = field(default_factory=list)

    # Metadata
    step_number: int = field(default=0)


@dataclass
class IndexState:
    """State for document indexing."""

    # Documents to index
    documents: List[Document] = field(default_factory=list)

    # Indexing status
    indexed_count: int = field(default=0)
    errors: List[str] = field(default_factory=list)

    # Source tracking
    source_file: str | None = field(default=None)
