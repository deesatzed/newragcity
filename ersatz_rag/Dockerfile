# Ersatz (LEANN + PageIndex + deepConf) Orchestration Service Dockerfile
# Part of newragcity unified RAG system
# Uses Regulus backend as the three-approach integration layer

FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    postgresql-client \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Set up PATH for uv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/root/.local/bin:/root/.cargo/bin:$VIRTUAL_ENV/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy the regulus backend code (contains ThreeApproachRAG integration)
COPY regulus/backend /app

# Copy wait-for-postgres script
RUN chmod +x ./wait-for-postgres.sh 2>/dev/null || true

# Create virtual environment and install dependencies
RUN uv venv --python /usr/local/bin/python3.13 $VIRTUAL_ENV
RUN . $VIRTUAL_ENV/bin/activate && uv pip install -e .

# Create data directories
RUN mkdir -p /data/indexes /data/memory

# Expose port for Ersatz service
EXPOSE 8020

# Environment variables (can be overridden by docker-compose)
ENV PYTHONUNBUFFERED=1
ENV INDEX_PATH=/data/indexes/cognitron_index
ENV MEMORY_PATH=/data/memory.db
ENV LOG_LEVEL=info
ENV ERSATZ_PORT=8020

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8020/health || exit 1

# Run the Ersatz orchestration service
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8020"]
