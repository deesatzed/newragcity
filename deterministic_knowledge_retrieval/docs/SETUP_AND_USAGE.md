# Setup & Usage Guide

This guide walks through configuring the Doc-MCP Skeleton on a new machine, verifying that ingestion succeeds, and operating the fallback FastAPI service.

## 1. Environment Preparation
1. **Clone or sync** the repository onto your workstation.
2. **Choose a Python runtime**:
   - Recommended: activate the shared Conda environment  
     `conda activate /Users/o2satz/miniforge3/envs/py13`
   - Alternative: create a project-local virtualenv  
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     pip install -r requirements-dev.txt
     ```
3. **Optional AgentOS stack**: defer installing Agno/LanceDB/OpenAI dependencies until you are ready to replace the fallback API (`pip install -r requirements.txt`).

## 2. First-Time Verification
1. Run the automated tests to confirm the loader and service behave as expected:
   ```bash
   python -m pytest
   ```
   All suites should pass; failures typically indicate malformed JSON inputs or missing dependencies.
2. Inspect the dataset summary by importing the ingestion workflow:
   ```bash
   python - <<'PY'
   from src.ingestion_workflow import run_ingestion_with_metadata
   pack, warnings = run_ingestion_with_metadata("bootstrap")
   print("Dataset:", pack.manifest.dataset_id, pack.manifest.version)
   print("Sections:", sum(len(file.content) for file in pack.content))
   print("Warnings:", warnings)
   PY
   ```

## 3. Running the Service
1. Launch the server:
   ```bash
   uvicorn src.main:agent_os_app --reload
   ```
   - If Agno dependencies are absent, the fallback FastAPI app starts automatically.
   - Logs will include JSON-formatted ingestion warnings (one per skipped file).
2. Exercise the API:
   ```bash
   curl http://localhost:8000/meta         # dataset metadata + warnings
   curl http://localhost:8000/sections     # section catalogue
   curl -X POST http://localhost:8000/query \
        -H "Content-Type: application/json" \
        -d '{"question": "Initial therapy for neutropenic fever?"}'
   ```
3. Monitor health:
   ```bash
   curl http://localhost:8000/health
   ```
   The response reports `status: "ok"` unless ingestion warnings are present (`"degraded"`).

## 4. Managing Infection JSON Data
1. Place new infection JSON files (matching the existing schema) in the repository root.
2. Validate them before committing:
   ```bash
   python -m pytest tests/test_data_loader.py
   ```
3. Restart the service and confirm `/meta` and `/health` show no warnings.

## 5. Upgrading Toward Production
- **AgentOS Integration**: install Agno + LanceDB, set `OPENAI_API_KEY`, and verify the AgentOS branch of `src/main.py` runs without falling back.
- **Containerization**: port the design-time `Dockerfile`/`nanobot.yaml` into this codebase and run the nanobot lifecycle (`nanobot build/run/stop`).
- **Monitoring Hooks**: forward the JSON warning logs and poll `/health` from your orchestrator to catch ingestion regressions automatically.
- **Security & Secrets**: inject credentials via environment variables or secrets managers; never commit sensitive files.

Refer to `STATUS.md` for the latest build snapshot, mock components, and outstanding roadmap items.
