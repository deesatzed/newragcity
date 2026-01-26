# DKR (Deterministic Knowledge Retrieval) Service Dockerfile
# Part of newragcity unified RAG system

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir uvicorn[standard]

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /data

# Expose port for DKR service
EXPOSE 8010

# Environment variables (can be overridden by docker-compose)
ENV PYTHONUNBUFFERED=1
ENV DATA_DIR=/data
ENV LOG_LEVEL=info
ENV DKR_PORT=8010

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8010/health || exit 1

# Run the DKR server
CMD ["python", "-m", "src.agents.run_server"]
