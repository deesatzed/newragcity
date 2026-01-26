# UltraRAG Context for Gemini

## Project Overview

**UltraRAG** is a lightweight, modular RAG (Retrieval-Augmented Generation) development framework based on the **Model Context Protocol (MCP)**. It decouples RAG components (Retriever, Generator, etc.) into independent MCP Servers, allowing for flexible orchestration via a YAML-based pipeline configuration.

The framework is designed for both research exploration and industrial prototyping, supporting complex control structures like conditional branches and loops within the RAG pipeline.

## Key Technologies

*   **Language:** Python (>= 3.11, < 3.13)
*   **Core Framework:** `fastmcp`, `mcp`
*   **Package Management:** `uv`
*   **Configuration:** YAML, `.env`
*   **Vector Search:** `faiss`, `milvus` (via `pymilvus`)
*   **LLM Integration:** `openai`, `vllm`, `transformers`

## Architecture

UltraRAG follows a Client-Server architecture:

1.  **MCP Client (`src/ultrarag/client.py`):**
    *   Reads the **Pipeline Configuration** (YAML).
    *   Manages the execution flow (sequential, loops, branches).
    *   Handles data passing (`UltraData`) and memory management between steps.
    *   Communicates with MCP Servers to execute tools.

2.  **MCP Servers (`servers/`):**
    *   Independent modules providing specific capabilities.
    *   Examples: `retriever`, `generation`, `evaluation`, `sayhello`.
    *   Each server has its own `src/` directory and `parameter.yaml` configuration.
    *   Implemented using `UltraRAG_MCP_Server` (wrapper around `FastMCP`).

3.  **Pipeline:**
    *   Defined in a YAML file (e.g., `examples/sayhello.yaml`).
    *   Lists a sequence of steps, where each step calls a tool exposed by a server (e.g., `sayhello.greet`).

## Directory Structure

*   `src/ultrarag/`: Core framework code (Client, CLI, Utilities).
*   `servers/`: Collection of built-in MCP servers.
    *   `servers/<name>/src/`: Server implementation code.
    *   `servers/<name>/parameter.yaml`: Default configuration for the server.
*   `examples/`: Sample pipeline configurations and tutorials.
*   `data/`: Sample data for testing.
*   `ui/`: Web UI implementation.

## Usage Guide

### 1. Installation

The project uses `uv` for dependency management.

```bash
# Install core dependencies
uv sync

# Install all extras (retriever, generation, etc.)
uv sync --all-extras
```

### 2. Running a Pipeline

Use the `ultrarag` CLI to run a pipeline defined in a YAML file.

```bash
# Run the 'sayhello' example
ultrarag run examples/sayhello.yaml

# Run with custom parameters
ultrarag run examples/rag.yaml --param examples/parameter/rag_parameter.yaml
```

### 3. Building Configuration

To generate or update the server configuration files based on a pipeline:

```bash
ultrarag build examples/sayhello.yaml
```

### 4. Running the UI

Launch the Web UI for interactive usage:

```bash
# Basic chat mode
ultrarag show ui

# Admin mode (with pipeline builder)
ultrarag show ui --admin
```

## Development & Extension

### Creating a New Server

1.  Create a directory in `servers/`.
2.  Add a `parameter.yaml` for configuration.
3.  Create a `src` directory and a Python file (e.g., `myserver.py`).
4.  Inherit from `UltraRAG_MCP_Server` and define tools.

**Example (`servers/sayhello/src/sayhello.py`):**

```python
from typing import Dict
from ultrarag.server import UltraRAG_MCP_Server

app = UltraRAG_MCP_Server("sayhello")

@app.tool(output="name->msg")
def greet(name: str) -> Dict[str, str]:
    """Greet a person."""
    ret = f"Hello, {name}!"
    return {"msg": ret}

if __name__ == "__main__":
    app.run(transport="stdio")
```

### Defining a Pipeline

Create a YAML file in `examples/` or your project root.

```yaml
servers:
  myserver: servers/myserver  # Path to your server directory

pipeline:
  - myserver.greet  # Call the tool
```

### Pipeline Control Flow

*   **Loop:**
    ```yaml
    - loop:
        times: 3
        steps:
          - myserver.some_tool
    ```
*   **Branch (Router):**
    ```yaml
    - branch:
        router:
          - myserver.router_tool
        branches:
          case_a:
            - myserver.tool_a
          case_b:
            - myserver.tool_b
    ```

## Key Files

*   `src/ultrarag/client.py`: The heart of the pipeline execution engine.
*   `src/ultrarag/server.py`: Base class for MCP servers.
*   `pyproject.toml`: Dependency definitions.
*   `README.md`: Main documentation.
