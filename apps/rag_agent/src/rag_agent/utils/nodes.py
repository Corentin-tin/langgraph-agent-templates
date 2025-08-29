"""Node implementations for the RAG agent graphs."""

from typing import Dict, Any

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model

from shared.logging import get_logger
from .state import AgentState, ResearcherState, IndexState
from .tools import (
    load_embeddings,
    load_vector_store,
    load_sample_documents,
    split_documents,
    retrieve_documents,
    format_docs_xml,
)
from .prompts import (
    QUERY_ANALYSIS_PROMPT,
    RESEARCH_PLANNER_PROMPT,
    RESPONSE_GENERATOR_PROMPT,
    RESEARCHER_QUERY_PROMPT,
)

logger = get_logger(__name__)


def load_chat_model_from_env(model: str = "anthropic/claude-3-5-sonnet-20240620"):
    """Load chat model from environment configuration."""
    provider, model_name = model.split("/", maxsplit=1)
    return init_chat_model(model_name, model_provider=provider)


# Index Graph Nodes


async def index_docs(state: IndexState) -> Dict[str, Any]:
    """Index documents into the vector store."""
    logger.info("Starting document indexing")

    try:
        # Load documents if not provided
        if not state.documents:
            documents = await load_sample_documents()
        else:
            documents = state.documents

        if not documents:
            logger.warning("No documents to index")
            return {"indexed_count": 0, "errors": ["No documents found"]}

        # Split documents into chunks
        chunks = split_documents(documents)

        # Load embeddings and vector store
        embeddings = load_embeddings()
        vector_store = load_vector_store("faiss", embeddings)  # Default to FAISS for simplicity

        # Add documents to vector store
        await vector_store.aadd_documents(chunks)

        logger.info("Document indexing completed", count=len(chunks))
        return {"indexed_count": len(chunks)}

    except Exception as e:
        error_msg = f"Indexing failed: {str(e)}"
        logger.error("Document indexing failed", error=str(e))
        return {"errors": [error_msg]}


# Retrieval Graph Nodes


async def query_analysis(state: AgentState) -> Dict[str, Any]:
    """Analyze the user query and determine routing."""
    logger.info("Analyzing query for routing")

    if not state.messages:
        return {"query_analysis": "general"}

    last_message = state.messages[-1]
    if not isinstance(last_message, HumanMessage):
        return {"query_analysis": "general"}

    question = last_message.content

    try:
        model = load_chat_model_from_env()
        prompt = ChatPromptTemplate.from_template(QUERY_ANALYSIS_PROMPT)
        parser = JsonOutputParser()
        chain = prompt | model | parser

        result = await chain.ainvoke({"question": question})

        datasource = result.get("datasource", "general")
        logger.info("Query analysis completed", datasource=datasource)

        return {"query_analysis": datasource}

    except Exception as e:
        logger.error("Query analysis failed", error=str(e))
        return {"query_analysis": "general"}


async def research_planner(state: AgentState) -> Dict[str, Any]:
    """Create a research plan for complex queries."""
    logger.info("Creating research plan")

    if not state.messages:
        return {"research_plan": "No query provided", "steps": []}

    last_message = state.messages[-1]
    question = last_message.content if isinstance(last_message, HumanMessage) else ""

    try:
        model = load_chat_model_from_env()
        prompt = ChatPromptTemplate.from_template(RESEARCH_PLANNER_PROMPT)
        chain = prompt | model

        result = await chain.ainvoke({"question": question})
        plan = result.content

        # Extract steps from the plan (simplified)
        steps = [
            step.strip() for step in plan.split("\n") if step.strip() and not step.startswith("#")
        ][:4]

        logger.info("Research plan created", steps_count=len(steps))

        return {"research_plan": plan, "steps": steps}

    except Exception as e:
        logger.error("Research planning failed", error=str(e))
        return {"research_plan": f"Planning failed: {str(e)}", "steps": []}


async def retrieve_docs(state: AgentState) -> Dict[str, Any]:
    """Retrieve documents from the vector store."""
    logger.info("Retrieving documents")

    if not state.messages:
        return {"documents": []}

    last_message = state.messages[-1]
    query = last_message.content if isinstance(last_message, HumanMessage) else ""

    try:
        # Load vector store
        embeddings = load_embeddings()
        vector_store = load_vector_store("faiss", embeddings)

        # Retrieve documents
        docs = await retrieve_documents(vector_store, query, k=10)

        logger.info("Documents retrieved", count=len(docs))
        return {"documents": docs}

    except Exception as e:
        logger.error("Document retrieval failed", error=str(e))
        return {"documents": []}


async def generate_response(state: AgentState) -> Dict[str, Any]:
    """Generate response based on retrieved documents."""
    logger.info("Generating response")

    if not state.messages:
        return {"messages": [AIMessage(content="No query provided.")]}

    last_message = state.messages[-1]
    question = last_message.content if isinstance(last_message, HumanMessage) else ""

    # Format documents as context
    context = format_docs_xml(state.documents)

    try:
        model = load_chat_model_from_env()
        prompt = ChatPromptTemplate.from_template(RESPONSE_GENERATOR_PROMPT)
        chain = prompt | model

        result = await chain.ainvoke({"question": question, "context": context})

        response = AIMessage(content=result.content)
        logger.info("Response generated")

        return {"messages": [response], "answer": result.content}

    except Exception as e:
        error_msg = f"Response generation failed: {str(e)}"
        logger.error("Response generation failed", error=str(e))
        return {"messages": [AIMessage(content=error_msg)]}


# Researcher Subgraph Nodes


async def generate_queries(state: ResearcherState) -> Dict[str, Any]:
    """Generate search queries for research."""
    logger.info("Generating research queries")

    if not state.research_question:
        return {"queries": []}

    try:
        model = load_chat_model_from_env()
        prompt = ChatPromptTemplate.from_template(RESEARCHER_QUERY_PROMPT)
        chain = prompt | model

        result = await chain.ainvoke({"question": state.research_question})

        # Extract queries from result (simplified)
        queries = [
            q.strip()
            for q in result.content.split("\n")
            if q.strip() and q.strip().startswith(("1.", "2.", "3.", "-", "*"))
        ]

        # Clean up queries
        queries = [
            q.split(".", 1)[-1].strip() if q[0].isdigit() else q.lstrip("-* ").strip()
            for q in queries
        ]
        queries = [q for q in queries if len(q) > 10][:3]  # Keep top 3 meaningful queries

        logger.info("Research queries generated", count=len(queries))
        return {"queries": queries}

    except Exception as e:
        logger.error("Query generation failed", error=str(e))
        return {"queries": []}


async def research_step(state: ResearcherState) -> Dict[str, Any]:
    """Execute research for generated queries."""
    logger.info("Executing research step")

    if not state.queries:
        return {"documents": []}

    try:
        # Load vector store
        embeddings = load_embeddings()
        vector_store = load_vector_store("faiss", embeddings)

        all_docs = []
        for query in state.queries:
            docs = await retrieve_documents(vector_store, query, k=5)
            all_docs.extend(docs)

        logger.info("Research step completed", docs_count=len(all_docs))
        return {"documents": all_docs}

    except Exception as e:
        logger.error("Research step failed", error=str(e))
        return {"documents": []}
