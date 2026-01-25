# Cognitron: Personal Knowledge Assistant - Build Checklist (Option 1: Full-Featured)

## Phase 1: Foundation & Environment Setup
- [ ] Init Git repo and set up uv with pyproject.toml.
- [ ] Add dependencies: leann-core, leann-backend-hnsw (from PyPI), pageindex (local module with OpenAI API), typer, rich, scikit-learn, sqlite.
- [ ] Configure ruff and pytest. Implement a basic CI pipeline on GitHub Actions to run linters and initial tests.
- [ ] Define project structure: cognitron/ (for core logic), cli.py, tests/.
- [ ] Set environment variables: CHATGPT_API_KEY for PageIndex, OpenAI API for deepConf LLM calls.
- [ ] Install vLLM and apply deepConf patch to vllm/v1/engine/logprobs.py and output_processor.py.

## Phase 2: Core Technology Integration & Indexing
- [ ] Data Models: In cognitron/models.py, define Pydantic or dataclass models for Chunk, DocumentMetadata, and Topic.
- [ ] IndexingService: In cognitron/indexing.py, create class IndexingService. Import from leann.api import LeannBuilder, LeannSearcher; from pageindex.page_index import page_index_main.
  - Implement async def run_indexing(self, paths: List[Path]): Iterate through paths. For each file, determine strategy using a _get_strategy(file_path) helper.
  - Smart Chunking Logic: If strategy is pageindex, call page_index_main(pdf_path), iterate through tree nodes (node_id, title, summary, start_index, end_index), create Chunk objects.
  - AST Chunking Logic: If strategy is ast, read file and use astchunk to generate chunks.
  - Add all generated chunks to a LeannBuilder instance and call LeannBuilder.build_index().
- [ ] TopicService: In cognitron/topics.py, create class TopicService. Implement async def generate_topics(self, index_path: str): Load embeddings from LEANN index, run HDBSCAN, generate labels with LLM, save to topics.json.

## Phase 3: Agentic Layer & Confidence Memory
- [ ] Agent & LLM Backend: In cognitron/agent.py, create class CognitronAgent. In cognitron/llm.py, create a wrapper around openai.AsyncOpenAI that modifies chat.completions.create to always include logprobs=True and top_logprobs=5. It should parse and return both the message and the logprobs object.
- [ ] Confidence Calculation: In cognitron/confidence.py, implement calculate_confidence_profile(trace: List[LLMCall]) -> ConfidenceProfile. Define the ConfidenceProfile data schema: { "planner_confidence": float, "steps": [ { "step_confidence": float, "tool_confidence": float } ] }. Use the "Lowest Group Confidence" metric.
- [ ] deepConf Integration: Apply patch to vllm/v1/engine/logprobs.py: Extend LogprobsProcessor with conf fields (conf_grouped, conf_list, etc.), add check_conf_stop() method. Update _update_sample_logprobs() to track confidence in sliding window. In output_processor.py, insert early-stop check before RequestOutput construction. Enable via SamplingParams.extra_args: {"enable_conf": true, "window_size": 2048, "threshold": 17}.
- [ ] ConfidenceGatedCaseMemory: In cognitron/memory.py, create class CaseMemory using SQLite. DB Schema: cases (id, timestamp, query, outcome, confidence_profile_json). Implement async def add_case(...) and async def retrieve_cases(query: str, min_confidence: float). Retrieval uses a simple embedding similarity search on the query column.

## Phase 4: CLI Application
- [ ] In cli.py, set up Typer application.
- [ ] cognitron index: Takes a list of paths, runs IndexingService, then TopicService.
- [ ] cognitron ask: Instantiates CognitronAgent, runs the query, and uses rich to print the final answer and any intermediate thoughts.
- [ ] cognitron topics: Loads topics.json and displays it in a formatted table.

## Phase 5: Testing, Benchmarking, and Hardening
- [ ] Create a tests/fixtures directory with sample code and documents.
- [ ] Write unit tests for confidence calculation and indexing strategies.
- [ ] Write an end-to-end integration test for the ask command that mocks LLM calls but uses a real index.
- [ ] Benchmark index command performance on a 1000-file repository using LEANN's selective recomputation for storage efficiency.
- [ ] Validate that no network traffic occurs during local operations (except for intended LLM calls).
