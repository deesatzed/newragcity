# RoT Reasoning Server - Docker Image
# Base image with CUDA support for GPU acceleration

FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.cache/huggingface \
    TRANSFORMERS_CACHE=/app/.cache/huggingface

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    git \
    curl \
    wget \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.11 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy dependency files first (for layer caching)
COPY requirements.txt .
COPY .python-version .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy source code and configuration
COPY src/ ./src/
COPY parameter.yaml .

# Create checkpoint directories
RUN mkdir -p /app/checkpoints/stage1 /app/checkpoints/stage2

# Create cache directory
RUN mkdir -p /app/.cache/huggingface

# Expose port for MCP server
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import fastmcp; print('healthy')" || exit 1

# Default command: run tests
CMD ["python", "src/rot_reasoning.py", "--test"]

# Alternative commands:
# Start MCP server: docker run rot-reasoning-server python src/rot_reasoning.py --port 8000
# Run tests: docker run rot-reasoning-server python src/rot_reasoning.py --test
# Interactive shell: docker run -it rot-reasoning-server /bin/bash
