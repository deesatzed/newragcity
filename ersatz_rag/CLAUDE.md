# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

ERSATZ_RAG is a multi-system repository containing:
- **Regulus**: Corporate policy & compliance chatbot with admin dashboard
- **Cognitron**: Medical-grade personal knowledge assistant with confidence calibration

The project integrates **3 novel approaches** for advanced RAG:
- **PageIndex**: Reasoning-based document structure extraction using LLM intelligence
- **LEANN**: Efficient vector search with selective recomputation and metadata filtering
- **deepConf**: Multi-factor confidence scoring and early stopping in LLM responses

**Integration Status**: ✅ All 3 approaches fully integrated and production-ready (Level 3/3)

## Development Commands

### Python Environment Setup
```bash
# Use Python 3.13 from conda environment for all Python operations
export PYTHON_PATH="/opt/homebrew/anaconda3/envs/py13/bin/python"
```

### Regulus Backend (FastAPI)
```bash
cd regulus/backend

# Install dependencies using uv with Python 3.13
uv sync --python $PYTHON_PATH

# Run all tests (real integration tests, no mocks)
$PYTHON_PATH -m pytest tests/ -v

# Run specific test file
$PYTHON_PATH -m pytest tests/test_upload.py -v

# Test 3-approach integration demo
$PYTHON_PATH complete_demo.py

# Test approach integration module
$PYTHON_PATH app/three_approach_integration.py

# Start development server
$PYTHON_PATH -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run linting
$PYTHON_PATH -m ruff check .

# Run type checking (if configured)
$PYTHON_PATH -m mypy app/
```

### Regulus Admin Frontend (Next.js)
```bash
cd regulus/admin_frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run linting
npm run lint

# Run type checking
npm run typecheck
```

### Cognitron System
```bash
cd cognitron

# Install Cognitron package
$PYTHON_PATH -m pip install -e .

# Run core integration tests
$PYTHON_PATH test_cognitron_integration.py

# Run end-to-end tests
$PYTHON_PATH test_end_to_end.py

# Run all tests
$PYTHON_PATH scripts/test_all.py

# Run specific test suites
$PYTHON_PATH test_cognitron_core.py
$PYTHON_PATH test_temporal_intelligence.py
```

### Global Integration Tests
```bash
cd tests

# Run comprehensive test suite
$PYTHON_PATH -m pytest test_comprehensive_suite.py -v

# Run integration tests
$PYTHON_PATH -m pytest test_integration.py -v

# Run performance/load tests
$PYTHON_PATH -m pytest test_performance_load.py -v
```

### Docker Compose (Full Stack)
```bash
cd regulus

# Start all services (backend, frontend, PostgreSQL, Redis)
docker-compose up

# Build and start with rebuild
docker-compose up --build

# View logs for specific service
docker-compose logs backend
docker-compose logs frontend

# Execute commands in running containers
docker-compose exec backend python -m pytest
docker-compose exec backend python complete_demo.py

# Stop all services
docker-compose down

# Stop and remove volumes (clean reset)
docker-compose down -v
```

## Architecture & Key Components

### Regulus System Architecture
- **Backend** (`regulus/backend/app/`):
  - `main.py`: FastAPI endpoints for upload, query, and configuration
  - `indexing.py`: Document processing and LEANN indexing service
  - `models.py`: SQLAlchemy database models for documents and audit trails
  - `memory.py`: Confidence-gated case memory system
  - `llm.py`: LLM integration with OpenAI/OpenRouter support
  - `agent.py`: Compliance agent orchestration
  - `three_approach_integration.py`: Core ThreeApproachRAG class integrating all approaches

- **Admin Frontend** (`regulus/admin_frontend/`):
  - Next.js 14 with App Router
  - TypeScript + Tailwind CSS
  - Components in `src/components/`
  - API routes in `src/app/api/`

- **Infrastructure**:
  - PostgreSQL: Document storage, metadata, audit trails
  - Redis + arq: Background job processing for document indexing
  - LEANN HNSW backend: Vector search index storage

### Cognitron System Architecture
- **Core Components** (`cognitron/cognitron/`):
  - `agent.py`: CognitronAgent main orchestration
  - `llm.py`: MedicalGradeLLM with confidence tracking via logprobs
  - `memory.py`: CaseMemory SQLite-based learning system
  - `indexing.py`: Multi-domain content indexing service
  - `topics.py`: AI-powered knowledge organization

- **Confidence System**:
  - Medical-grade thresholds: Critical (>95%), High (>85%), Medium (>70%)
  - Multi-factor scoring: semantic, authority, relevance, structure, model
  - Confidence-gated responses and storage

### 3 Novel Approaches Integration Details

**1. PageIndex - Document Intelligence**
- Location: `regulus/backend/app/indexing.py` (page_index_main function)
- Generates hierarchical tree structure from PDFs
- Creates reasoning confidence scores for each node
- Fallback to simple chunking when API unavailable
- API keys: PAGEINDEX_API_KEY, OPENAI_API_KEY, or OPENROUTER_API_KEY

**2. LEANN - Vector Search Engine**
- IBM Granite embeddings: `ibm-granite/granite-embedding-english-r2`
- Backend: HNSW with selective recomputation
- Metadata filters: effective_date, is_archived, version, source_type
- Semantic scores: 800+ range for high-quality matches
- Index management in `regulus/backend/app/indexing.py`

**3. deepConf - Confidence Scoring**
- 5-factor analysis in `calculate_composite_confidence()`
- Threshold gating (default 0.80) for response quality
- Case memory integration for pattern learning
- Early stopping based on confidence levels

**Complete Integration**: `ThreeApproachRAG` class orchestrates all approaches

## Environment Configuration

### Required Environment Variables
```bash
# LLM APIs (at least one required)
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-or-v1-...

# PageIndex (uses above keys or dedicated)
PAGEINDEX_API_KEY=...

# Database (Regulus)
DATABASE_URL=postgresql://user:pass@localhost/regulus
POSTGRES_USER=regulus_user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=regulus

# Redis (for background jobs)
REDIS_URL=redis://localhost:6379

# Cognitron Paths
COGNITRON_INDEX_PATH=~/.cognitron/index
COGNITRON_MEMORY_PATH=~/.cognitron/memory.db
```

## Testing Philosophy

- **No mocks/simulation**: All tests use real integrations
- **Golden dataset**: 50 policy questions with >90% accuracy target
- **Performance targets**:
  - Query p95 latency <10s
  - Semantic scores >800 for relevant matches
  - Confidence calibration accuracy >90%

## Query Processing Workflow

1. **Broad Search Phase**:
   - LEANN vector search with IBM Granite embeddings
   - Metadata filtering (dates, versions, archived status)
   - Top-k retrieval (typically k=10)

2. **Deep Analysis Phase**:
   - Multi-factor deepConf scoring on retrieved chunks
   - Confidence components: semantic, authority, relevance, structure, model
   - Composite confidence calculation with weighting

3. **Response Generation**:
   - Confidence gating (threshold filtering)
   - High-confidence case memory storage
   - Complete citations with node_ids and page ranges
   - Audit trail logging with approach status

## Document Processing Pipeline

1. Upload endpoint receives PDF/documents
2. Arq worker processes document asynchronously
3. PageIndex generates tree structure (with fallback)
4. Tree nodes converted to chunks with metadata
5. LEANN indexing with Granite embeddings
6. Metadata association (version, effective_date, source)
7. Index optimization and persistence

## Specialized Agents

When working on specific subsystems, use specialized agents from `.claude/agents/`:

- **leann-indexing-specialist**: LEANN configuration, metadata filtering
- **pageindex-reasoning-engineer**: PDF processing, tree generation
- **deepconf-confidence-architect**: Confidence scoring, early stopping
- **compliance-audit-guardian**: Audit trails, policy versioning
- **admin-dashboard-architect**: Frontend components, upload flows
- **integration-test-orchestrator**: Golden datasets, end-to-end tests

## Performance Optimization Points

- LEANN index pre-computation for common queries
- Case memory caching for repeated high-confidence patterns
- Confidence early-stopping to reduce LLM token usage
- Metadata filtering before semantic search for efficiency
- Batch processing for document uploads