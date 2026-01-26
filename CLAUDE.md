# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ MANDATORY PRE-TASK CHECKLIST (newragcity Anti-Drift System)

**BEFORE starting ANY task, you MUST complete this checklist**:

- [ ] **Read MISSION_CRITICAL.md** (`/Volumes/WS4TB/newragcity/UltraRAG-main/MISSION_CRITICAL.md`)
- [ ] **Verify task is about unified newragcity system** (NOT individual components like DKR alone, Ersatz alone, or RoT alone)
- [ ] **Confirm approach aligns with docker-compose.yml architecture** (10 services working TOGETHER)
- [ ] **If benchmarking**: Planning to test END-TO-END system (NOT isolated component evaluators)
- [ ] **If implementing**: Planning to integrate ALL components (NOT working on one subsystem in isolation)

### Checklist Failure Mode

**If ANY checkbox fails**:
1. STOP immediately
2. Read MISSION_CRITICAL.md in full
3. Ask user for clarification: "I want to confirm - are you asking me to work on [X]? Based on MISSION_CRITICAL.md, I understand newragcity as a unified system where DKR + Ersatz + RoT + UltraRAG work together. Should I approach this as [unified approach] or did you mean something else?"
4. Do NOT proceed until user confirms approach

### Quick Drift Check

**Are you about to**:
- ❌ Create dkr_evaluator.py, ersatz_evaluator.py, or other component-specific evaluators?
- ❌ Benchmark DKR, Ersatz, or RoT individually?
- ❌ Test components in isolation instead of through docker-compose?
- ❌ Propose "Let's validate each component before integration"?

**If YES to any** → DRIFT DETECTED → Read MISSION_CRITICAL.md immediately

### Correct Patterns

**User says**: "Run the benchmarks"
→ **You think**: "Test the complete newragcity system end-to-end via docker-compose"
→ **NOT**: "Implement evaluators for each component"

**User says**: "Test the system"
→ **You think**: "Start docker-compose up and run queries through unified API"
→ **NOT**: "Test DKR, then Ersatz, then RoT separately"

### Why This Checklist Exists

This repository has experienced **5 catastrophic drifts** where the unified system concept was lost. The checklist ensures we remember:

**newragcity = DKR + Ersatz + RoT + UltraRAG (TOGETHER as ONE system)**

**NOT**: DKR (alone), Ersatz (alone), RoT (alone)

For complete drift history and recovery procedures, see MISSION_CRITICAL.md.

---

## Repository Overview

**UltraRAG** is a lightweight RAG development framework based on the Model Context Protocol (MCP) architecture. It standardizes core RAG components (Retriever, Generation, etc.) as independent MCP Servers combined with powerful workflow orchestration through YAML configuration.

**Key Features**:
- Low-code orchestration of complex RAG workflows via YAML (loops, branches, sequences)
- Modular MCP server architecture for extreme reusability
- Built-in unified evaluation and benchmark comparison
- Visual RAG IDE (UltraRAG UI) with Pipeline Builder and bidirectional canvas/code sync
- One-click conversion from pipeline logic to interactive web UI

**Version**: v3.0 (January 2026)
**Python Requirements**: >=3.11, <3.13

## Installation and Setup

### Install Dependencies

**Using uv (recommended)**:
```bash
# Core dependencies only (for UI and basic functions)
uv sync

# Full installation (retrieval, generation, corpus, evaluation)
uv sync --all-extras

# Module-specific installation
uv sync --extra retriever
uv sync --extra generation
uv sync --extra evaluation
uv sync --extra corpus
```

**Using pip into existing environment**:
```bash
# Core dependencies
uv pip install -e .

# Full installation
uv pip install -e ".[all]"

# Module-specific
uv pip install -e ".[retriever]"
```

### Activate Virtual Environment

```bash
# Windows CMD
.venv\Scripts\activate.bat

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

### Verify Installation

```bash
ultrarag run examples/sayhello.yaml
# Expected output: "Hello, UltraRAG v3!"
```

## Core Commands

### Running Pipelines

```bash
# Run a pipeline from YAML configuration
ultrarag run <pipeline_yaml_file>

# Example: Basic hello world
ultrarag run examples/sayhello.yaml

# Example: Standard RAG deployment
ultrarag run examples/rag_deploy.yaml

# Example: Loop-based iterative RAG
ultrarag run examples/rag_loop.yaml

# Example: Branch-based conditional RAG
ultrarag run examples/rag_branch.yaml

# Example: Evaluation on TREC benchmark
ultrarag run examples/eval_trec.yaml
```

### Starting UltraRAG UI

```bash
# Launch UI in chat mode (default)
ultrarag ui

# Launch UI in admin mode (for pipeline development)
ultrarag ui --admin

# Custom host/port
ultrarag ui --host 0.0.0.0 --port 8080
```

Access the UI at `http://localhost:5050` (or custom port).

### Working with MCP Servers

Each server in `servers/` is an independent MCP server with:
- `src/<server_name>.py`: Tool implementations
- `parameter.yaml`: Default configuration

**Available Servers**:
- `retriever`: Vector/BM25 search, indexing (FAISS, Milvus backends)
- `generation`: LLM generation (vLLM, OpenAI, HuggingFace backends)
- `prompt`: Prompt templates and formatting
- `evaluation`: Metrics calculation (ROUGE, NDCG, MAP, etc.)
- `corpus`: Document processing and chunking
- `reranker`: Re-ranking retrieved passages
- `benchmark`: Dataset loading and formatting
- `custom`: Custom logic (output extraction, passage merging)
- `router`: Decision routing for conditional branches
- `sayhello`: Example/demo server

## Architecture

### MCP Server Structure

Each server follows this pattern:

```
servers/<server_name>/
├── src/
│   └── <server_name>.py    # Tools implementation
└── parameter.yaml           # Configuration defaults
```

**Server Implementation** (`src/<server_name>.py`):
```python
from ultrarag import UltraRAG_MCP_Server

mcp = UltraRAG_MCP_Server(
    name="server_name",
    instructions="Server description"
)

@mcp.tool()
async def tool_name(param1: str, param2: int) -> str:
    """Tool description."""
    # Tool logic
    return result
```

### Pipeline YAML Structure

Pipelines orchestrate server tools via YAML:

```yaml
# Define which servers to load
servers:
  retriever: servers/retriever
  generation: servers/generation
  prompt: servers/prompt

# Define execution pipeline
pipeline:
  # Simple tool call
  - retriever.retriever_init

  # Tool with parameters
  - retriever.retriever_search:
      input:
        query_list: questions
      output:
        ret_psg: passages

  # Loop structure
  - loop:
      times: 3
      steps:
        - prompt.gen_subq
        - generation.generate

  # Branch structure
  - branch:
      router:
        - router.check_condition
      branches:
        path_a:
          - prompt.format_a
        path_b:
          - prompt.format_b
```

### Client Architecture

The `ultrarag` CLI (`src/ultrarag/client.py`) acts as the MCP Client:
1. Loads YAML configuration
2. Starts all defined MCP servers
3. Connects via `fastmcp.Client`
4. Executes pipeline steps sequentially/conditionally
5. Manages shared state across tool calls

### UltraRAG UI Architecture

**Backend** (`ui/backend/`):
- `app.py`: Flask application with REST endpoints
- `pipeline_manager.py`: Pipeline execution, state management, canvas builder

**Frontend** (`ui/frontend/`):
- Pre-built static files (HTML/CSS/JS)
- Canvas-based visual pipeline editor
- Real-time bidirectional sync with YAML code

**Modes**:
- **Chat Mode**: Interactive Q&A with deployed pipelines
- **Admin Mode**: Pipeline development, testing, knowledge base management

## Configuration Management

### Server Configuration (`servers/*/parameter.yaml`)

Each server has default parameters that can be overridden in pipeline YAML or via environment variables.

**Example: Retriever Configuration**
```yaml
# servers/retriever/parameter.yaml
model_name_or_path: openbmb/MiniCPM-Embedding-Light
corpus_path: data/corpus_example.jsonl
embedding_path: embedding/embedding.npy

backend: sentence_transformers
# Options: infinity, sentence_transformers, openai, bm25

index_backend: faiss
# Options: faiss, milvus

batch_size: 16
top_k: 5
```

**Example: Generation Configuration**
```yaml
# servers/generation/parameter.yaml
backend: vllm
# Options: vllm, openai, hf

backend_configs:
  vllm:
    model_name_or_path: openbmb/MiniCPM4-8B
    gpu_ids: "2,3"
    gpu_memory_utilization: 0.9
  openai:
    model_name: gpt-4
    base_url: https://api.openai.com/v1
    api_key: ${OPENAI_API_KEY}

sampling_params:
  temperature: 0.7
  top_p: 0.8
  max_tokens: 2048
```

### Environment Variables

Create `.env` file in project root (based on `.env.dev`):

```bash
# LLM APIs
LLM_API_KEY=           # For generation server
OPENAI_API_KEY=        # OpenAI models
ZHIPUAI_API_KEY=       # ZhipuAI models

# Search APIs
TAVILY_API_KEY=        # Tavily web search
EXA_API_KEY=           # Exa web search

# Retriever APIs
RETRIEVER_API_KEY=     # External retriever service
```

## Development Workflow

### Creating a New MCP Server

1. **Create server directory**:
   ```bash
   mkdir -p servers/myserver/src
   ```

2. **Implement server** (`servers/myserver/src/myserver.py`):
   ```python
   from ultrarag import UltraRAG_MCP_Server

   mcp = UltraRAG_MCP_Server(
       name="myserver",
       instructions="What this server does"
   )

   @mcp.tool()
   async def my_tool(input_text: str) -> str:
       """Tool description for LLM."""
       # Implementation
       return f"Processed: {input_text}"
   ```

3. **Create configuration** (`servers/myserver/parameter.yaml`):
   ```yaml
   default_param: value
   another_param: 42
   ```

4. **Use in pipeline**:
   ```yaml
   servers:
     myserver: servers/myserver

   pipeline:
     - myserver.my_tool:
         input:
           input_text: "Hello"
   ```

### Testing Pipelines

**Create test YAML**:
```yaml
servers:
  myserver: servers/myserver

pipeline:
  - myserver.my_tool:
      input:
        input_text: "test input"
```

**Run test**:
```bash
ultrarag run test_pipeline.yaml
```

### Debugging

**Enable verbose logging**:
```python
# In server code
from ultrarag.mcp_logging import get_logger

logger = get_logger(__name__)
logger.info("Debug information")
logger.error("Error details")
```

**Check tool registration**:
```bash
# Tools are listed when client connects to servers
ultrarag run <pipeline> --log-level DEBUG
```

## Advanced Features

### Control Flow Structures

**Loops**:
```yaml
- loop:
    times: 5  # Number of iterations
    steps:
      - prompt.generate_question
      - generation.generate
      - custom.process_output
```

**Conditional Branches**:
```yaml
- branch:
    router:  # Router determines which branch to take
      - router.check_condition
    branches:
      continue:  # Branch name
        - prompt.expand_query
        - retriever.search
      stop:  # Alternative branch
        - custom.finalize
```

### State Management

Pipeline maintains shared state across tools:

```yaml
- retriever.search:
    output:
      ret_psg: passages  # Store result in 'passages' variable

- prompt.format:
    input:
      context: passages  # Use 'passages' from previous step
    output:
      formatted: prompt_text

- generation.generate:
    input:
      prompt: prompt_text  # Chain through multiple steps
```

### Data Integration

**Load corpus**:
```yaml
- corpus.build_text_corpus:
    input:
      corpus_dir: data/documents/
      output_path: data/corpus.jsonl
```

**Index corpus**:
```yaml
- retriever.retriever_init  # Initialize with corpus_path from parameter.yaml
```

**Custom data formats**:
- JSONL: `{"id": "doc1", "title": "...", "contents": "..."}`
- Supports chunking, metadata, multimodal content

## Evaluation and Benchmarking

### Built-in Benchmarks

UltraRAG includes standard RAG benchmarks:
- TREC datasets
- MS MARCO
- Natural Questions
- HotpotQA

**Run evaluation**:
```yaml
servers:
  benchmark: servers/benchmark
  evaluation: servers/evaluation

pipeline:
  - benchmark.get_data:  # Load benchmark dataset
      input:
        dataset_name: "nq"

  # ... your RAG pipeline ...

  - evaluation.evaluate:  # Calculate metrics
      input:
        predictions: generated_answers
        references: gold_answers
```

**Metrics Supported**:
- Retrieval: NDCG, MAP, MRR, Recall@K
- Generation: ROUGE-L, BERTScore, Exact Match
- End-to-end: Answer accuracy, F1 score

### Custom Evaluation

Add custom metrics in `servers/evaluation/src/evaluation.py`:

```python
@mcp.tool()
async def custom_metric(predictions: list, references: list) -> dict:
    """Calculate custom metric."""
    # Implementation
    return {"custom_score": score}
```

## Special Considerations

### Embeddings and Vector Search

**Supported backends**:
- `sentence_transformers`: Local embedding models
- `infinity`: Optimized inference server
- `openai`: OpenAI embedding API
- `bm25`: Sparse retrieval (no embeddings)

**Index backends**:
- `faiss`: Fast CPU/GPU similarity search
- `milvus`: Distributed vector database (supports Milvus Lite for local development)

**GPU Configuration**:
```yaml
# servers/retriever/parameter.yaml
gpu_ids: "0,1"  # Use GPUs 0 and 1
index_backend_configs:
  faiss:
    index_use_gpu: True
```

### LLM Generation

**vLLM backend** (for local models):
```yaml
backend: vllm
backend_configs:
  vllm:
    model_name_or_path: openbmb/MiniCPM4-8B
    gpu_ids: "0,1"
    gpu_memory_utilization: 0.9
    dtype: auto
```

**OpenAI backend** (for API models):
```yaml
backend: openai
backend_configs:
  openai:
    model_name: gpt-4
    base_url: https://api.openai.com/v1
    api_key: ${OPENAI_API_KEY}
```

### Docker Deployment

**Pull pre-built image**:
```bash
docker pull hdxin2002/ultrarag:v0.3.0
```

**Run container**:
```bash
docker run -it --gpus all -p 5050:5050 hdxin2002/ultrarag:v0.3.0
```

**Build from source**:
```bash
docker build -t ultrarag:custom .
docker run -it --gpus all -p 5050:5050 ultrarag:custom
```

UltraRAG UI automatically starts and is accessible at `http://localhost:5050`.

## Project Structure Reference

```
UltraRAG-main/
├── src/ultrarag/          # Core client/server framework
│   ├── client.py          # MCP client and pipeline executor
│   ├── server.py          # UltraRAG_MCP_Server base class
│   ├── api.py             # Python API for direct integration
│   ├── cli.py             # CLI utilities
│   └── utils.py           # Helper functions
├── servers/               # MCP server implementations
│   ├── retriever/        # Vector/BM25 retrieval
│   ├── generation/       # LLM generation
│   ├── prompt/           # Prompt templates
│   ├── evaluation/       # Metrics and benchmarking
│   ├── corpus/           # Document processing
│   ├── reranker/         # Reranking
│   ├── benchmark/        # Dataset loading
│   ├── custom/           # Custom utilities
│   └── router/           # Branch routing logic
├── ui/                   # UltraRAG UI
│   ├── backend/          # Flask server
│   └── frontend/         # Static web assets
├── examples/             # Example pipeline configurations
├── data/                 # Corpus and datasets
├── docs/                 # Documentation
├── ersatz_rag/           # Separate ERSATZ_RAG project (has own CLAUDE.md)
├── deterministic_knowledge_retrieval/  # DKR research code
├── TheVault/             # Additional server implementations
├── pyproject.toml        # Python dependencies
└── .env.dev              # Environment variable template
```

## Related Projects

This repository contains multiple sub-projects:

**ersatz_rag/**: A separate multi-system RAG project with Regulus (corporate chatbot) and Cognitron (medical assistant). See `ersatz_rag/CLAUDE.md` for specific guidance.

**deterministic_knowledge_retrieval/**: Research implementation of deterministic retrieval methods.

**TheVault/**: Additional experimental MCP servers and tools.

## Resources

- **Documentation**: https://ultrarag.openbmb.cn/
- **GitHub Issues**: https://github.com/OpenBMB/UltraRAG/issues
- **Discord**: https://discord.gg/yRFFjjJnnS
- **Model Context Protocol**: https://modelcontextprotocol.io/
