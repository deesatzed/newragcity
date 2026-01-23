# The Vault: SOTA Proprietary Retrieval System

**The Vault** is a secure, local-first retrieval-augmented generation (RAG) system designed for high-precision enterprise use cases. It fuses three specialized technologies into a single pipeline to ensure 100% citation accuracy, strict role-based access control (RBAC), and "medical-grade" confidence gating.

## 🏗 System Architecture

The Vault employs a "Tri-Core" architecture orchestrated by the Model Context Protocol (MCP):

1.  **The Auditor (DKR Core):**
    *   **Role:** Deterministic retrieval for exact matches (Error codes, specific policy numbers).
    *   **Tech:** TF-IDF, Metadata filtering, Agentic lookup.
    *   **Source:** Manuals, Proprietary Codebase.

2.  **The Scholar (Ersatz Core):**
    *   **Role:** Semantic search for conceptual understanding and guidelines.
    *   **Tech:** Vector Search (Leann), Deep Document Understanding (PageIndex).
    *   **Source:** Guidelines, PDFs, Memos.

3.  **The Generator (Local LLM):**
    *   **Role:** Answer synthesis and citation formatting.
    *   **Tech:** OpenAI-compatible Local Server (vLLM/Llama.cpp).
    *   **Model:** Qwen-2.5-14B-Instruct (Recommended).

## 📂 Directory Structure

```
TheVault/
├── servers/              # MCP Servers (The Engines)
├── pipeline/             # YAML Pipeline Configurations
├── scripts/              # Unified Ingestion & Eval scripts
├── data/                 # Local corpora and databases
│   ├── input_docs/       # DROP YOUR PDFS HERE
│   ├── corpus.jsonl      # Processed corpus
│   └── golden_set.json   # Synthetic Eval Data
└── src/                  # Shared utilities
```

## 🛠 Setup & Usage

### 1. Prerequisites
*   Python 3.11+
*   `uv` (Universal Python Package Manager)
*   A local LLM server running on `http://localhost:8000/v1` (vLLM, Ollama, LM Studio).

### 2. Initialization
```bash
cd TheVault
uv sync
```

### 3. Start Local Model
Ensure your local model server is running. Example with vLLM:
```bash
vllm serve Qwen/Qwen2.5-14B-Instruct --port 8000
```

### 4. 📄 Ingest Your Real Documents
1.  Place your PDF/TXT files into `TheVault/data/input_docs/`.
2.  Run the bulk ingestion script:
    ```bash
    python scripts/ingest_bulk.py
    ```
    *This extracts text using PyMuPDF and builds the DKR corpus.*

### 5. 📊 Generate "Real Metrics" (Golden Set)
Create a ground-truth exam based on **your** documents:
```bash
python scripts/generate_eval.py --samples 50
```
*This uses your local LLM to read your docs and write 50 Q/A pairs to `data/golden_set.json`.*

### 6. 🚀 Run The Vault
Execute the pipeline:
```bash
./run_vault.sh
```

### 7. Evaluate Performance
(Coming Soon: Full pipeline integration for automated scoring)
```bash
python scripts/run_eval.py
```

## 🧪 Testing
We include a "Golden Set" validator to ensure SOTA performance.
