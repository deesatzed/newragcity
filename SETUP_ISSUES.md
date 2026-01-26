# Setup Issues and Solutions Log

This document tracks all issues encountered during first-time setup of The Vault codebase, along with their solutions. This log ensures future users can set up the project without encountering the same problems.

## Prerequisites Status

✅ **WORKING**: Python 3.11+ requirement
✅ **WORKING**: uv package manager installation
✅ **WORKING**: Basic dependency installation via `uv sync`

---

## Issue #1: Incorrect Default Paths in Scripts

**Severity**: Medium
**Status**: ✅ FIXED

### Problem
All scripts use incorrect default paths with "TheVault/" prefix:
- `scripts/ingest_bulk.py` defaults to `TheVault/data/input_docs` and `TheVault/data/corpus.jsonl`
- `scripts/generate_eval.py` defaults to `TheVault/data/corpus.jsonl` and `TheVault/data/golden_set.json`
- `run_vault.sh` references `TheVault/pipeline/vault_main.yaml`

The actual directory structure doesn't have a "TheVault/" subdirectory.

### Error Message
```
Input directory not found: TheVault/data/input_docs
```

### Solution
Updated all default paths to remove "TheVault/" prefix:
- `scripts/ingest_bulk.py`: Changed defaults to `data/input_docs` and `data/corpus.jsonl`
- `scripts/generate_eval.py`: Changed defaults to `data/corpus.jsonl` and `data/golden_set.json`
- `run_vault.sh`: Changed to `pipeline/vault_main.yaml`

### Test Command
```bash
uv run python scripts/ingest_bulk.py
```

---

## Issue #2: Missing openai Dependency

**Severity**: High
**Status**: ✅ FIXED

### Problem
The `scripts/generate_eval.py` and `servers/local_llm/src/llm_server.py` import the `openai` package, but it's not listed in `pyproject.toml` dependencies.

### Error Message
```
ModuleNotFoundError: No module named 'openai'
```

### Solution
Added `openai>=1.0.0` to dependencies in `pyproject.toml`:
```toml
dependencies = [
    "ultrarag>=0.3.0",
    "fastmcp>=2.0.0",
    "python-dotenv",
    "rich",
    "typer",
    "pymupdf",
    "tqdm",
    "openai>=1.0.0"
]
```

Then ran:
```bash
uv sync
```

### Test Command
```bash
uv run python -c "from openai import AsyncOpenAI; print('OK')"
```

---

## Issue #3: Scripts Require uv run Prefix

**Severity**: Medium
**Status**: ✅ DOCUMENTED

### Problem
Running Python scripts directly (e.g., `python scripts/ingest_bulk.py`) doesn't use the virtual environment created by `uv sync`, leading to import errors or missing dependencies.

### Error Message
```
Warning: PyMuPDF (fitz) not found. PDF processing will be skipped. Run 'uv sync' to enable.
```

### Solution
Always use `uv run` prefix when running Python scripts or commands:

**Correct:**
```bash
uv run python scripts/ingest_bulk.py
uv run python scripts/generate_eval.py
```

**Incorrect:**
```bash
python scripts/ingest_bulk.py  # Won't use virtual environment
```

Updated `run_vault.sh` to use `uv run` prefix for all ultrarag commands.

---

## Issue #4: No LLM Server Check in generate_eval.py

**Severity**: Medium
**Status**: ✅ FIXED

### Problem
The `scripts/generate_eval.py` script would fail silently when the local LLM server wasn't running, producing empty results without clear error messages.

### Error Message
```
Error generating Q/A: Connection error.
Error generating Q/A: Connection error.
Golden set saved to data/golden_set.json  # Empty file
```

### Solution
Added connection check at script startup to fail fast with helpful error message:

```python
# Test connection to LLM server
try:
    await client.models.list()
except Exception as e:
    print(f"\n❌ Error: Cannot connect to local LLM server at {args.base_url}")
    print(f"   Details: {e}")
    print("\nPlease start a local LLM server first. For example:")
    print("   vllm serve Qwen/Qwen2.5-14B-Instruct --port 8000")
    print("   # OR")
    print("   ollama serve")
    print("   # OR")
    print("   Use LM Studio on http://localhost:8000")
    return
```

### Test Command
```bash
uv run python scripts/generate_eval.py --samples 2
# Should show clear error if LLM not running
```

---

## Issue #5: Missing uv run in run_vault.sh

**Severity**: High
**Status**: ✅ FIXED

### Problem
The `run_vault.sh` script calls `ultrarag` commands directly without `uv run`, causing "command not found" errors.

### Error Message
```
./run_vault.sh: line 11: ultrarag: command not found
```

### Solution
Updated `run_vault.sh` to prefix all ultrarag commands with `uv run`:

```bash
# Before
ultrarag build pipeline/vault_main.yaml
ultrarag run pipeline/vault_main.yaml

# After
uv run ultrarag build pipeline/vault_main.yaml
uv run ultrarag run pipeline/vault_main.yaml
```

---

## Issue #6: ultrarag Commands Don't Exist

**Severity**: CRITICAL ⚠️
**Status**: ⛔ BLOCKING

### Problem
The `ultrarag` package installed from PyPI (version 1.0.0) does not have `build` or `run` commands. It only has a `serve` command for starting a web server with Ollama integration.

### Error Message
```
usage: ultrarag [-h] {serve} ...
ultrarag: error: argument command: invalid choice: 'build' (choose from 'serve')
```

### Available Commands
```bash
$ uv run ultrarag --help
usage: ultrarag [-h] {serve} ...

positional arguments:
  {serve}     Commands
    serve     Start web server
```

### Root Cause
The codebase expects a different version of UltraRAG that supports:
- YAML-based pipeline orchestration
- `ultrarag build` and `ultrarag run` commands
- Pipeline execution with MCP servers

The public PyPI package (v1.0.0) is a basic RAG library without these features.

### Impact
**The main pipeline cannot be executed with the current setup.** The entire orchestration system described in the README doesn't exist in the available package.

### Possible Solutions (Requires Further Investigation)

1. **Check for Private/Unreleased Version**
   - The codebase may require a custom or unreleased version of UltraRAG
   - May need access to a private repository or pre-release version

2. **Alternative Execution Methods**
   - Run MCP servers independently and orchestrate manually
   - Build custom orchestration layer
   - Use MCP inspector/client tools directly

3. **Use Different Package**
   - May need a different package entirely (e.g., custom ultrarag fork)
   - Check if there's a `ultrarag-mcp` or similar variant

### Recommendation
**ACTION NEEDED**: Clarify which version of UltraRAG this codebase requires, or provide installation instructions for the correct version.

---

## Issue #7: Missing ultrarag.server Module

**Severity**: CRITICAL ⚠️
**Status**: ⛔ BLOCKING

### Problem
All MCP servers import `from ultrarag.server import UltraRAG_MCP_Server`, but this module doesn't exist in the installed ultrarag package (v1.0.0).

### Error Message
```
ModuleNotFoundError: No module named 'ultrarag.server'; 'ultrarag' is not a package
```

### What's Actually in ultrarag v1.0.0
```python
['AdaptiveRetriever', 'AnswerValidator', 'AtomicChunker', 'Chunk',
 'OllamaLLM', 'QueryAnalysis', 'QueryProcessor', 'RAG', 'RAGResponse',
 'create_server', 'cli', '__version__']
```

No `server` submodule or `UltraRAG_MCP_Server` class exists.

### Impact
**None of the MCP servers can be initialized or run.** This includes:
- `servers/dkr/src/dkr_server.py`
- `servers/ersatz/src/ersatz_server.py`
- `servers/local_llm/src/llm_server.py`
- `servers/prompt/src/prompt.py`

### Root Cause
Same as Issue #6 - the codebase requires a version of UltraRAG with MCP server support that isn't available in the public package.

### Recommendation
This is a **BLOCKING** issue. The project cannot function without access to the correct version of UltraRAG that includes MCP server support.

---

## Issue #8: External Dependencies Not Documented

**Severity**: High
**Status**: ⚠️ REQUIRES ATTENTION

### Problem
The system requires two external codebases that are not included:

1. **DKR (Deterministic Knowledge Retrieval)**
   - Path in `servers/dkr/parameter.yaml`: `/Volumes/WS4TB/newragcity/UltraRAG-main/deterministic_knowledge_retrieval`
   - Required classes: `TOCAgent`, `DataLoader`
   - Not available in repository

2. **Ersatz/Cognitron**
   - Path in `servers/ersatz/parameter.yaml`: `/Volumes/WS4TB/newragcity/UltraRAG-main/ersatz_rag/cognitron`
   - Required class: `CognitronAgent`
   - Not available in repository

### Impact
Even if Issues #6 and #7 were resolved, the pipeline would fail because these external dependencies don't exist.

### Solution Needed
- Include these codebases in the repository, OR
- Provide instructions for obtaining/installing them, OR
- Create stub implementations for testing, OR
- Document that this is a reference architecture requiring custom implementations

---

## Summary of Current State

### ✅ Working Components
1. ✅ Environment setup with `uv sync`
2. ✅ Document ingestion pipeline (`scripts/ingest_bulk.py`)
3. ✅ Corpus generation from PDFs and text files
4. ✅ Evaluation script structure (needs LLM server to generate data)

### ⛔ Blocking Issues
1. ⛔ **ultrarag package version mismatch** - Public version doesn't support MCP servers or pipeline orchestration
2. ⛔ **Missing ultrarag.server module** - MCP servers cannot be initialized
3. ⛔ **Missing external dependencies** - DKR and Ersatz codebases not available

### ⚠️ Requires LLM Server (When Other Issues Fixed)
- Evaluation dataset generation requires local LLM at `http://localhost:8000/v1`
- Pipeline execution will require local LLM
- Examples: vLLM, Ollama, LM Studio

---

## Next Steps for Making This Runnable

1. **Clarify UltraRAG Version**
   - Document which version of UltraRAG is required
   - Provide installation instructions or repository link
   - OR: Remove dependency and implement alternative orchestration

2. **Provide External Dependencies**
   - Include DKR and Ersatz implementations
   - OR: Provide installation/setup instructions
   - OR: Create mock implementations for testing

3. **Update Documentation**
   - Clearly state all prerequisites including external codebases
   - Update README with actual working commands
   - Document that this may be a reference architecture

4. **Consider Alternative Architecture**
   - If UltraRAG with MCP support isn't available, consider:
     - Using standard MCP protocol with different tooling
     - Implementing custom orchestration
     - Providing standalone server examples

---

## Fixed Issues Summary

The following issues have been resolved and new users should not encounter them:

1. ✅ Incorrect default paths in scripts - Fixed
2. ✅ Missing openai dependency - Added to pyproject.toml
3. ✅ Scripts need uv run prefix - Documented and fixed in run_vault.sh
4. ✅ Silent failures in generate_eval.py - Added connection check with helpful error
5. ✅ Missing uv run in run_vault.sh - Fixed

## Remaining Issues

Two critical blocking issues remain:
- ⛔ UltraRAG package version mismatch (no MCP support)
- ⛔ Missing external DKR and Ersatz dependencies

These require clarification from the original developers or access to additional codebases/packages.
