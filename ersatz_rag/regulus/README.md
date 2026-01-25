# Regulus: Corporate Policy & Compliance Bot

Regulus is an intelligent, web-based chatbot that serves as the definitive source of truth for all company policies, providing instant, traceable answers with 100% auditability.

This project is production-ready and integrates three novel AI approaches:
1.  **PageIndex**: For reasoning-based document structure extraction.
2.  **LEANN**: For efficient, high-performance vector search using IBM Granite embeddings.
3.  **deepConf**: For multi-factor confidence scoring and gating.

## How to Test

Testing can be performed by running the standalone demo script, which showcases the complete "Broad-then-Deep" retrieval pipeline.

### 1. Prerequisites

- Python 3.10+
- An API key for an LLM provider. The application will automatically look for one of the following environment variables:
  - `PAGEINDEX_API_KEY`
  - `OPENAI_API_KEY`
  - `OPENROUTER_API_KEY`

Export the key in your terminal:

```bash
export OPENROUTER_API_KEY="your-api-key-here"
```

### 2. Setup

First, set up a virtual environment and install the required dependencies from the `backend` directory.

```bash
# Navigate to the backend directory
cd regulus/backend

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Indexing Script (if needed)

The demo script relies on a pre-built index. If the index does not exist at `/tmp/final_granite_ai_policy`, you will need to run the indexing script first. 

*(Note: A dedicated indexing script was not found, but the logic exists within `three_approach_integration.py`. A separate script should be created for this purpose if the index needs to be rebuilt).* 

### 4. Run the Complete Demo

Execute the `complete_demo.py` script from the `regulus/backend` directory to see the full system in action.

```bash
# From the regulus/backend directory
python3 complete_demo.py
```

The script will:
- Initialize the 3-approach RAG system.
- Verify that the pre-built index exists.
- Run a series of test queries against the index.
- Display the "Broad-then-Deep" retrieval results, including a multi-factor `deepConf` confidence breakdown for each result.
- Show the final status of the system and any high-confidence cases learned during the session.
