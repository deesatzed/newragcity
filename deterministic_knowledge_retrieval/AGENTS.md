# Repository Guidelines

## Project Structure & Module Organization
- Treat `AJrag.txt` as the systems blueprint and `agnoMCPnanobot.txt` as the canonical implementation spec; mirror any substantive code change back into these documents.
- Place runtime code under `src/` (modules such as `pydantic_schemas.py`, `data_loader.py`, `ingestion_workflow.py`, `doc_mcp_team.py`, `main.py`) and keep package setup via `src/__init__.py`.
- Keep fixtures in `tests/` (sample AJ Packs, TOC stubs) and avoid committing large binaries; use `tests/fixtures/` only when persistence is unavoidable. Any new infection JSON should mirror the schema exercised in `tests/test_data_loader.py` so validation passes.

## Build, Test, and Development Commands
- Bootstrap a dev environment with `python -m venv .venv && source .venv/bin/activate` followed by `pip install -r requirements.txt`.
- Run the service locally via `uvicorn src.main:agent_os_app --reload`; if Agno is missing the JSON-only fallback spins up without needing `OPENAI_API_KEY`.
- The ingestion workflow automatically sweeps the repository root for infection JSON files (e.g., `pneumonia.json`) and adds them to the AJ Pack—keep new sources consistent with that schema so loader validation passes.
- Monitor `/meta`, `/health`, and the JSON-formatted service logs for loader warnings whenever new files are added; ingestion skips malformed JSON rather than failing hard.
- Use the nanobot lifecycle for container workflows: `nanobot build`, `nanobot run`, `nanobot stop`; these wrap the `Dockerfile`/`nanobot.yaml`.

## Coding Style & Naming Conventions
- Follow Python 3.10+ / PEP 8 conventions with 4-space indents, type hints, and docstrings that explain agent responsibilities.
- Keep modules snake_case, classes PascalCase, env vars SHOUT_CASE, and AJ identifiers stable (e.g., `ch04_se2`); breaking IDs severs citations.
- Data contracts live in `pydantic_schemas.py`; extend them with explicit `Field` metadata and validation instead of ad-hoc dicts. Maintain JSON-first semantics—avoid introducing vector indices unless the system design changes.

## Testing Guidelines
- Use `pytest` (add to `requirements-dev.txt` if needed) and mirror the module tree (`tests/test_ingestion_workflow.py`, etc.).
- Maintain schema tests that round-trip AJ Packs, TOC routing simulations, and loader budget checks described in `AJrag.txt §8`.
- Gate merges on `pytest --maxfail=1 --disable-warnings -q`; keep golden fixtures minimal but representative.

## Commit & Pull Request Guidelines
- Adopt Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`) and reference design sections (e.g., “docs: sync AJ Pack schema with AJrag §2.2”).
- PRs must summarize behavior changes, note new configuration, include test evidence, and call out any schema or identifier migrations.
- Update both design documents when behavior, workflows, or interfaces drift; reviewers should block merges if specs and code are out of sync.

## Security & Configuration Tips
- Never commit secrets; load `OPENAI_API_KEY` and similar credentials via `.env` (listed in `.gitignore`) or environment injection.
- Align deployments with metadata flags (`phi`, `residency`) in AJ Packs and ensure the nanobot run command passes only approved environment variables.
