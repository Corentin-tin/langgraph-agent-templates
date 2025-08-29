# React Agent

A ReAct (Reasoning and Acting) pattern agent implementation using LangGraph. This agent can reason about problems, use tools, and iteratively work towards solutions.

## Features

- **ReAct Pattern**: Implements Reasoning → Acting → Observing in a continuous loop
- **Tool Integration**: Built-in web search with Tavily, extensible for custom tools
- **Multiple LLM Support**: Works with Anthropic Claude, OpenAI, and Fireworks models
- **LangGraph Studio Compatible**: Designed for development and debugging in LangGraph Studio
- **Configurable**: Runtime configuration through environment variables and context

## Quick Start

### Local Development

1. **Install dependencies:**
```bash
cd apps/react_agent
uv sync
```

2. **Set up environment:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Run the server:**
```bash
uvicorn react_agent.server:app --reload --port 2024
```

### LangGraph Studio

1. Open LangGraph Studio
2. Connect to `http://localhost:2024`
3. Start chatting with the agent

## Configuration

The agent can be configured through environment variables:

```bash
# LLM Configuration
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Tool Configuration
TAVILY_API_KEY=your-tavily-api-key

# Agent Settings
MODEL=anthropic/claude-3-5-sonnet-20240620
MAX_SEARCH_RESULTS=10
MAX_ITERATIONS=10
```

## Architecture

```
src/react_agent/
├── graph.py              # Core graph definition
├── server.py             # FastAPI server
├── state.py              # State definitions
└── utils/
    ├── nodes.py           # Node implementations (Think/Act)
    ├── tools.py           # Available tools
    ├── state.py           # Context configuration
    └── prompts.py         # System prompts
```

## Extending the Agent

### Adding New Tools

1. Add your tool function to `utils/tools.py`:
```python
async def my_custom_tool(input: str) -> str:
    \"\"\"Your custom tool implementation.\"\"\"
    # Implementation here
    return result

# Add to TOOLS list
TOOLS.append(my_custom_tool)
```

2. The tool will automatically be available to the agent.

### Customizing Prompts

Edit the system prompt in `utils/state.py`:
```python
@dataclass(kw_only=True)
class Context:
    system_prompt: str = field(
        default="Your custom system prompt here...",
        # ...
    )
```

### Changing Models

Set the `MODEL` environment variable or modify the default in `Context`:
```bash
MODEL=openai/gpt-4o
# or
MODEL=fireworks/accounts/fireworks/models/llama-v3p1-405b-instruct
```

## Testing

Run the test suite:
```bash
pytest tests/
```

## Docker

Build and run with Docker:
```bash
docker build -t react-agent .
docker run -p 2024:2024 --env-file .env react-agent
```