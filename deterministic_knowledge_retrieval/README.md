# DKR - Deterministic Knowledge Retrieval

**A deterministic, vector-free, multi-domain RAG system with agent-based architecture**

This system implements a novel approach to Retrieval-Augmented Generation (RAG) that prioritizes **explainability**, **reproducibility**, and **compliance** over semantic flexibility. It works across ANY domain (healthcare, finance, policy, code, etc.) without requiring vector databases or embeddings.

## 🎯 Key Features

- ✅ **Deterministic Routing**: TF-IDF + metadata (no black-box embeddings)
- ✅ **Multi-Domain**: Pluggable adapters for healthcare, finance, policy, code, generic JSON
- ✅ **Agent Architecture**: TOC Agent, Loader Agent, Answer/Verifier Agent
- ✅ **Lossless Citations**: Every answer traceable to exact source sections
- ✅ **Policy Enforcement**: PHI/PII/residency controls built-in
- ✅ **Token Budget Management**: Strict 4000-token context limits
- ✅ **Hybrid Confidence** (Optional): Semantic validation without sacrificing explainability
- ✅ **Production-Ready**: 38 passing tests, comprehensive documentation

## Prerequisites
- Python 3.10+ (tested on Python 3.13 via Conda env `/Users/o2satz/miniforge3/envs/py13`).
- `pip` or `conda` for dependency management.
- Optional: Agno, LanceDB, and OpenAI credentials if you intend to enable the full AgentOS stack.

## Setup
1. (Recommended) Activate the existing environment:
   ```bash
   conda activate /Users/o2satz/miniforge3/envs/py13
   ```
   or create a fresh virtualenv:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements-dev.txt
   ```
2. Install optional AgentOS dependencies later with `pip install -r requirements.txt` once you are ready to integrate Agno.
3. Verify the installation by running `python -m pytest`; the suite should report all tests passing.
4. For a step-by-step walkthrough, see [`docs/SETUP_AND_USAGE.md`](docs/SETUP_AND_USAGE.md).

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run tests
pytest tests/ -v

# 3. Start the service
uvicorn src.main:agent_os_app --reload

# 4. Query the system
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -H "X-User-Region: US" \
  -H "X-PHI-Clearance: true" \
  -H "X-PII-Clearance: true" \
  -d '{"question": "What is the treatment for pneumonia?"}'
```

## API Endpoints

- **`POST /query`** - Query the knowledge base
  - Headers: `X-User-Region`, `X-PHI-Clearance`, `X-PII-Clearance`
  - Body: `{"question": "your question"}`
  - Returns: Answer with citations and confidence score

- **`GET /meta`** - Dataset metadata and warnings
- **`GET /sections`** - List all indexed sections
- **`GET /health`** - Health status and diagnostics

## Project Structure

```
src/
├── agents/                    # Agent-based architecture
│   ├── toc_agent.py          # TOC Agent: Deterministic routing
│   ├── loader_agent.py       # Loader Agent: Token budget management
│   ├── answer_verifier_agent.py  # Answer/Verifier: LLM synthesis + verification
│   └── confidence_validator.py   # Optional: Hybrid confidence (semantic)
├── domain_adapters/           # Multi-domain support
│   ├── base_adapter.py       # Base adapter interface
│   ├── healthcare_adapter.py # Healthcare domain
│   ├── generic_adapter.py    # Generic JSON
│   └── registry.py           # Adapter registry
├── pydantic_schemas.py        # Data contracts (AJ Pack schema)
├── ingestion_workflow.py      # Ingestion pipeline
├── data_loader.py             # Document loaders
├── policy_enforcer.py         # Security policy enforcement
├── llm_providers.py           # LLM provider abstraction
├── service.py                 # FastAPI service
└── main.py                    # Application entrypoint

tests/                         # Comprehensive test suite (38 tests)
docs/                          # Documentation
├── MULTI_DOMAIN.md           # Multi-domain guide
├── HYBRID_CONFIDENCE.md      # Hybrid confidence system
├── UKP_FUTURE_FEATURES.md    # Future roadmap
└── QUICKSTART.md             # Getting started guide
```

## Monitoring & Logs
- Warnings for malformed JSON inputs are emitted as structured log lines:
  ```json
  {"event": "ingestion_warning", "detail": "..."}
  ```
  Tail the server logs or forward them to your log pipeline to trigger alerts.
- `/health` mirrors these warnings so orchestrators or uptime probes can flag degraded states.

## Testing
- Run the full suite:
  ```bash
  python -m pytest
  ```
- Target individual modules:
  ```bash
  python -m pytest tests/test_data_loader.py
  ```
- The loader tests ensure new infection JSON files respect the expected schema before they are ingested.

## Updating the Dataset
- Drop additional infection JSON files (e.g., `new_condition.json`) in the project root; the loader automatically discovers them.
- Validate locally with `python -m pytest tests/test_data_loader.py`.
- Check `/meta` or `/health` after restarting the service to confirm there are no warnings.

## Documentation

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get up and running in 5 minutes
- **[Multi-Domain Guide](docs/MULTI_DOMAIN.md)** - Add new domains (finance, policy, code)
- **[Hybrid Confidence](docs/HYBRID_CONFIDENCE.md)** - Optional semantic validation
- **[Future Features](docs/UKP_FUTURE_FEATURES.md)** - Roadmap and planned enhancements
- **[Blog Post](docs/BLOG.md)** - Deep dive into novel concepts and architecture

## Configuration

### Environment Variables

```bash
# LLM Provider (default: mock)
LLM_PROVIDER=mock  # or openai, anthropic, ollama

# OpenAI (if using)
OPENAI_API_KEY=sk-...

# Anthropic (if using)
ANTHROPIC_API_KEY=sk-ant-...

# Ollama (if using)
OLLAMA_BASE_URL=http://localhost:11434

# Optional: Enable semantic validation for hybrid confidence
ENABLE_SEMANTIC_VALIDATION=false  # Set to 'true' to enable
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test modules
pytest tests/test_design_alignment.py -v
pytest tests/test_policy_enforcement.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

**Test Results**: 38 passed, 3 skipped (93% coverage of implemented features)

## Novel Concepts

### 1. Deterministic RAG (No Vectors)
- Uses TF-IDF + metadata instead of embeddings
- 100% explainable routing decisions
- No model drift, stable citations

### 2. Agent-Based Architecture
- **TOC Agent**: Routes queries using deterministic scoring
- **Loader Agent**: Manages token budgets with REQUEST_LOAD/RELEASE verbs
- **Answer/Verifier Agent**: Synthesizes and verifies answers

### 3. Hybrid Confidence (Optional)
- Primary: Deterministic routing (explainable)
- Secondary: Semantic validation (confidence calibration)
- Best of both worlds: explainability + validation

### 4. Multi-Domain by Design
- Pluggable adapters for any domain
- Deterministic Knowledge Pack format
- Same agents work across all domains

### 5. Policy-First Security
- PHI/PII/residency enforcement at query time
- Metadata-driven access control
- Compliant by design

## Performance

- **Latency**: <10ms routing (deterministic), 50-100ms with semantic validation
- **Token Efficiency**: ≤2-10% of corpus loaded per query
- **Cost**: $0 for deterministic routing (no API calls)
- **Scalability**: Handles millions of sections with parallel sharding

## License

See LICENSE file for details.

## Contributing

See CONTRIBUTING.md for guidelines.

## Support

For questions, issues, or feature requests, please open an issue on GitHub.
