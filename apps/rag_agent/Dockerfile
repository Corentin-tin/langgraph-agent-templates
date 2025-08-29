# RAG Agent Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml /app/
COPY uv.lock* /app/

# Install dependencies
RUN uv pip install --system -r pyproject.toml

# Copy source code
COPY src/ /app/src/
COPY langgraph.json /app/langgraph.json
COPY .env.example /app/.env.example

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PORT=2025
ENV HOST=0.0.0.0

# Expose port
EXPOSE 2025

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:2025/healthz || exit 1

# Run the application
CMD ["uvicorn", "rag_agent.server:app", "--host", "0.0.0.0", "--port", "2025"]