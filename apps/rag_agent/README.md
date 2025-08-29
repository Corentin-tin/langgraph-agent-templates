# RAG Agent

A Retrieval-Augmented Generation (RAG) research agent implementation using LangGraph. This agent can index documents, analyze queries, retrieve relevant information, and generate contextual responses.

## Features

- **Multi-Graph Architecture**: Separate graphs for indexing and retrieval operations
- **Smart Query Routing**: Classifies queries and routes to appropriate handlers
- **Research Planning**: Breaks down complex queries into research steps
- **Multiple Vector Store Support**: Elasticsearch, Pinecone, MongoDB Atlas, FAISS
- **Multiple LLM Providers**: OpenAI, Anthropic, Fireworks, Cohere
- **LangGraph Studio Compatible**: Designed for development and debugging in LangGraph Studio

## Quick Start

### Local Development

1. **Install dependencies:**
```bash
cd apps/rag_agent
uv sync
```

2. **Set up environment:**
```bash
cp .env.example .env
# Edit .env with your API keys and vector store configuration
```

3. **Run the server:**
```bash
uvicorn rag_agent.server:app --reload --port 2025
```

### LangGraph Studio

1. Open LangGraph Studio
2. Connect to `http://localhost:2025` for the main retrieval graph
3. Connect to `http://localhost:2025/indexer` for document indexing
4. Start indexing documents and asking questions

## Configuration

Configure the agent through environment variables:

```bash
# LLM Configuration
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
FIREWORKS_API_KEY=your-fireworks-api-key
COHERE_API_KEY=your-cohere-api-key

# Vector Store Selection
VECTOR_STORE=elasticsearch  # elasticsearch, pinecone, mongodb, faiss

# Elasticsearch Configuration
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_CLOUD_ID=your-elastic-cloud-id
ELASTICSEARCH_API_KEY=your-elastic-api-key

# Pinecone Configuration  
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX=your-index-name

# MongoDB Configuration
MONGODB_ATLAS_URI=your-mongodb-atlas-uri
MONGODB_DATABASE=rag_database
MONGODB_COLLECTION=documents

# Embedding Configuration
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_PROVIDER=openai
```

## Architecture

The RAG agent consists of three main graphs:

### 1. Indexer Graph (`/indexer`)
- Loads and processes documents
- Splits documents into chunks
- Stores embeddings in vector database

### 2. Retrieval Graph (`/`)
- Analyzes user queries
- Routes to appropriate handlers
- Retrieves relevant documents
- Generates contextual responses

### 3. Researcher Subgraph
- Generates research queries
- Executes parallel document retrieval
- Manages research context

```
src/rag_agent/
├── graph.py              # Graph definitions
├── server.py             # FastAPI server
├── sample_docs.json      # Sample documents for indexing
└── utils/
    ├── nodes.py           # Node implementations
    ├── tools.py           # Vector store & document tools
    ├── state.py           # State definitions
    └── prompts.py         # System prompts from official template
```

## Usage Workflow

### 1. Index Documents
First, index your documents using the indexer graph:

```python
# Using LangGraph Studio or API
POST /indexer/invoke
{
  "input": {
    "documents": []  # Will load sample docs if empty
  }
}
```

### 2. Query the RAG System
Ask questions using the main retrieval graph:

```python
# Using LangGraph Studio or API  
POST /invoke
{
  "input": {
    "messages": [
      {"role": "human", "content": "What is LangGraph?"}
    ]
  }
}
```

## Vector Store Setup

### Elasticsearch
```bash
# Local Elasticsearch
docker run -p 9200:9200 -e "discovery.type=single-node" elasticsearch:8.11.0

# Or use Elasticsearch Cloud
ELASTICSEARCH_CLOUD_ID=your-cloud-id
ELASTICSEARCH_API_KEY=your-api-key
```

### Pinecone
```bash
PINECONE_API_KEY=your-api-key
PINECONE_INDEX=your-index-name
```

### MongoDB Atlas
```bash
MONGODB_ATLAS_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=rag_database
MONGODB_COLLECTION=documents
```

### FAISS (Default/Local)
No additional setup required - uses local FAISS index.

## Extending the Agent

### Adding Custom Documents
Replace or extend `sample_docs.json` with your own documents:

```json
[
  {
    "content": "Your document content here...",
    "metadata": {
      "source": "Your Source",
      "title": "Document Title",
      "url": "https://example.com"
    }
  }
]
```

### Customizing Query Routing
Modify the query analysis in `utils/prompts.py`:

```python
QUERY_ANALYSIS_PROMPT = """Your custom routing logic here..."""
```

### Adding New Vector Stores
Extend `utils/tools.py` with additional vector store implementations.

## Testing

Run the test suite:
```bash
pytest tests/
```

## Docker

Build and run with Docker:
```bash
docker build -t rag-agent .
docker run -p 2025:2025 --env-file .env rag-agent
```

## API Endpoints

- `GET /` - API information
- `POST /invoke` - Main retrieval graph
- `POST /indexer/invoke` - Document indexing
- `GET /healthz` - Health check