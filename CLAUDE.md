# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Install workspace dependencies
uv sync

# Set up environment
cp .env.example .env
# Edit .env with your API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, TAVILY_API_KEY, etc.)
```

### Development Servers
```bash
# React Agent (ReAct pattern with web search)
cd apps/react_agent
uvicorn react_agent.server:app --reload --port 2024

# RAG Agent (Retrieval-Augmented Generation)
cd apps/rag_agent
uvicorn rag_agent.server:app --reload --port 2025
```

### Testing
```bash
# Test all apps from workspace root
uv run pytest

# Test specific app
cd apps/react_agent  # or apps/rag_agent
uv run pytest tests/

# Run single test
uv run pytest tests/test_graph_smoke.py::test_graph_builds -v

# Test with coverage
uv run pytest --cov=src tests/
```

### Code Quality
```bash
# From any app directory (apps/react_agent or apps/rag_agent)
uv run ruff check src/ tests/        # Linting
uv run ruff format src/ tests/       # Formatting with ruff
uv run black src/ tests/             # Formatting with black
uv run mypy src/                     # Type checking
```

### Docker Development
```bash
# Run both agents with dependencies
docker-compose up --build

# With Elasticsearch for RAG agent
docker-compose --profile elasticsearch up --build

# Individual agent
cd apps/react_agent  # or apps/rag_agent
docker build -t react-agent .
docker run -p 2024:2024 --env-file .env react-agent
```

### LangGraph Studio Integration
```bash
# After starting development servers, connect LangGraph Studio to:
# React Agent: http://localhost:2024
# RAG Agent: http://localhost:2025 (main retrieval graph)
# RAG Agent Indexer: http://localhost:2025/indexer (document indexing)
```

## Architecture Overview

### Workspace Structure
This is a uv workspace with three main packages:
- `packages/shared/` - Common utilities (logging, settings, types)
- `apps/react_agent/` - ReAct pattern agent implementation
- `apps/rag_agent/` - RAG pattern agent with multi-graph architecture

### React Agent Architecture
**Pattern**: ReAct (Reasoning and Acting) - Think → Act → Observe loop
**Core Flow**: `call_model` → `route_model_output` → `tools` → `call_model` (repeat until done)
**Key Files**:
- `graph.py`: StateGraph with Context schema, implements the ReAct loop
- `utils/nodes.py`: `call_model`, `route_model_output`, `tools_node`
- `utils/tools.py`: Tavily search tool, extensible TOOLS list
- `utils/state.py`: Context dataclass for runtime configuration
- `state.py`: InputState and State with is_last_step management

### RAG Agent Architecture
**Pattern**: Multi-graph RAG with intelligent routing
**Three Graphs**:
1. **Indexer Graph** (`indexer_graph`): Document processing and vector storage
2. **Retrieval Graph** (`retrieval_graph`): Main conversational flow with query routing
3. **Researcher Graph** (`researcher_graph`): Parallel research query execution

**Core Flow**: `query_analysis` → conditional routing → `retrieve_docs`/`research_planner` → `generate_response`
**Key Files**:
- `graph.py`: Three graph builders, `route_query` logic
- `utils/nodes.py`: All node implementations for each graph
- `utils/tools.py`: Vector store abstractions (Elasticsearch, Pinecone, MongoDB, FAISS)
- `utils/state.py`: AgentState, ResearcherState, IndexState with document deduplication
- `sample_docs.json`: Default knowledge base content

### Shared Architecture
**Settings**: Pydantic BaseSettings with environment variable loading
**Logging**: Structured logging with structlog, configurable levels
**State Management**: LangGraph StateGraph with proper type annotations
**LLM Integration**: `init_chat_model` with provider/model pattern (e.g., "anthropic/claude-3-5-sonnet-20240620")

### Configuration Patterns
Both agents use a Context-based configuration system:
- Environment variable loading in dataclass `__post_init__`
- LLM models specified as "provider/model-name" strings
- Settings classes inherit from shared BaseAppSettings
- Each agent has dedicated settings class (ReactAgentSettings, RagAgentSettings)

### Vector Store Integration (RAG Agent)
The RAG agent supports multiple vector stores through `load_vector_store()`:
- `elasticsearch`: Local or Elastic Cloud with API key auth
- `pinecone`: Requires PINECONE_INDEX environment variable
- `mongodb`: MongoDB Atlas with connection string
- `faiss`: Local FAISS index (default for development)

Vector store selection via `VECTOR_STORE` environment variable.

### Graph Composition Patterns
**React Agent**: Simple loop with conditional edges
**RAG Agent**: Complex routing with three separate graphs, shared state
**State Reducers**: Use `add_messages` and custom `add_documents` for deduplication
**Context Schemas**: Both agents use context schemas for runtime configuration

## Key Integration Points

### Adding Tools to React Agent
Add functions to `apps/react_agent/src/react_agent/utils/tools.py` TOOLS list. Functions are automatically bound to LLM via `bind_tools()`.

### Extending RAG Agent Vector Stores
Add new cases to `load_vector_store()` in `apps/rag_agent/src/rag_agent/utils/tools.py`.

### Modifying Agent Prompts
Prompts are sourced from official templates in `utils/prompts.py` files. The RAG agent uses specific prompts for query analysis, research planning, and response generation.

### LangGraph Studio Compatibility
Both agents expose `langgraph.json` configuration files and FastAPI servers with `add_routes()` for Studio integration. The RAG agent exposes multiple graphs on different paths.

### State Schema Evolution
State modifications require updating the respective state.py files. The RAG agent uses document deduplication via custom reducers.