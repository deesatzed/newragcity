# Thalamus: Clinical & Research Co-Pilot - Build Checklist (Option 1: Full-Featured)

## Phase 1: Foundation & Environment Setup
- [ ] Init Git monorepo with backend/ and frontend/ directories.
- [ ] Backend: FastAPI project with uv. Dependencies: fastapi, uvicorn, leann-core, leann-backend-hnsw (from PyPI), pageindex (local module), psycopg2-binary (for PostgreSQL), arq.
- [ ] Frontend: Next.js project with TypeScript, Tailwind CSS, and react-query for data fetching.
- [ ] Set up docker-compose.yml with services for the backend, frontend, PostgreSQL, and Redis (for the task queue).
- [ ] Set environment variables: CHATGPT_API_KEY for PageIndex, OpenAI API for deepConf LLM calls.
- [ ] Install vLLM and apply deepConf patch to vllm/v1/engine/logprobs.py and output_processor.py.

## Phase 2: Core Technology Integration & Indexing
- [ ] Database Schema: Use an ORM (e.g., SQLAlchemy) to define tables for Documents (with metadata like publication_date, document_type), Cases, and background IndexingJobs.
- [ ] IndexingService: In backend/services/indexing.py, create an arq worker function process_and_index_document(ctx, doc_id: int). Import from leann.api import LeannBuilder, LeannSearcher; from pageindex.page_index import page_index_main.
  - Logic: Fetch doc from DB -> call page_index_main(pdf_path), iterate tree nodes (node_id, title, summary, start_index, end_index), extract text chunks, add to LeannBuilder with metadata (publication_date, document_type), call LeannBuilder.build_index().
- [ ] API Endpoint /upload: Create a secure endpoint that accepts a PDF file, saves it to storage (e.g., S3), creates a Documents record in the DB, and enqueues an arq job to index it.
- [ ] RetrievalService: In backend/services/retrieval.py, implement async def broad_then_deep_query(...). Define the API contract for the /query endpoint. Request: { "query": str }. Response: { "answer": str, "evidence": List[EvidenceSnippet] }. Logic: Implement the two-stage retrieval using LeannSearcher for broad search, then PageIndex reasoning for deep analysis. The response must be validated to ensure all evidence snippets are populated correctly.

## Phase 3: Agentic Layer & Confidence Memory
- [ ] ResearchAgent: The main broad_then_deep_query function will be orchestrated by this agent.
- [ ] LLM Backend: Create an LLM service that requests and parses logprobs for all calls.
- [ ] deepConf Integration: Apply patch to vllm/v1/engine/logprobs.py: Extend LogprobsProcessor with conf fields (conf_grouped, conf_list, etc.), add check_conf_stop() method, update _update_sample_logprobs() to track confidence in sliding window, enable via SamplingParams.extra_args {"enable_conf": true, "window_size": 2048, "threshold": 17}.
- [ ] ConfidenceGatedCaseMemory: Implement CaseMemory service with methods to write cases to the PostgreSQL DB and retrieve them. Schema for ConfidenceProfile must include scores for each stage of the "Broad-then-Deep" process: triage_leann_confidence, deepdive_pageindex_confidence, synthesis_confidence.
- [ ] Confidence-Based Source Boosting: Add a document_type field to the Documents table. When the ResearchAgent starts a query, it retrieves past high-confidence cases. It performs a simple analysis: "For queries like this, which document_types appeared most often in successful, high-confidence results?" It then passes a boost parameter to the LeannSearcher to up-rank results from those document types.

## Phase 4: Web Application
- [ ] Backend API: Build out the full FastAPI application with endpoints for query, document management, and user feedback.
- [ ] Frontend UI: Design a search interface and a results view. The results view must render the synthesized answer and the interactive "Evidence" cards. Clicking an evidence card should highlight the text and provide a link to the source PDF. Implement the thumbs up/down feedback buttons and connect them to a /feedback API endpoint.

## Phase 5: Testing & Validation
- [ ] Write unit tests for all services and API endpoints.
- [ ] Create a "golden dataset" of 20 medical PDFs and 50 questions with known answers and source locations.
- [ ] Write an end-to-end test that runs through the golden dataset and asserts that accuracy is >90% and all citations are correct.
- [ ] Load test the /query endpoint to ensure p95 latency is under 15 seconds using LEANN's efficient search.
- [ ] Set up a staging environment and conduct a beta test with at least 5 medical professionals.
