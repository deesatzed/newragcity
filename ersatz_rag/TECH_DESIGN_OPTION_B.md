# Regulus Hybrid Retrieval Design (Option B)

Decisions (confirmed)
- Dense model: bge-large-en-v1.5 (sentence-transformers)
- Lexical engine: OpenSearch (BM25), single-node for development
- Fusion: Reciprocal Rank Fusion (RRF) over BM25 and dense candidates
- Rerank: Cross-encoder (e.g., ms-marco-MiniLM-L-6-v2) over fused top K
- Diversification: MMR to reduce near-duplicate evidence
- Abstention: Allowed when evidence is weak or inconsistent

Objectives
- High recall/precision on policy/legal corpora with sub-second latency.
- Full provenance: doc_id, source_file, section anchors, offsets.
- No mocks; every answer must be grounded in real indexed content.

## Architecture

- Source of truth: Postgres `doc_registry`
  - Columns: doc_id (UUID PK), source_file, sha256, mime, version, tags, ingest_ts, page_count.
- Dense index: Qdrant collection `regulus_docs`
  - Vector: 1024-d (bge-large-en-v1.5)
  - HNSW: M=32, ef_construction=256; query ef_search=64..200 (tunable)
  - Payload: { doc_id, chunk_id, title, source_file, section_path, page, char_start, char_end, ts }
- Lexical index: OpenSearch index `regulus_docs`
  - Mapping: title(text), body(text), section_path(keyword), doc_id(keyword), chunk_id(keyword), tags(keyword), date(date)
  - Analyzer: standard + English stemmer; optional 3–5 n-grams for phrase boost

## Ingestion Pipeline (real only)

1) Chunking: 2-paragraph chunks, 20–30% overlap; preserve section/page anchors
2) Deduplication: SHA256 or MinHash on normalized text
3) Embeddings: bge-large-en-v1.5 (batched) → Qdrant upsert with payload
4) Lexical: Index chunk body + metadata in OpenSearch
5) Audit: Log (doc_id, chunk_count, qdrant_upserts, os_docs_written) and expose counters via /metrics

## Query Pipeline (no placeholders)

1) Normalize query; apply synonyms later if approved
2) Candidate generation
   - BM25 (OpenSearch): topK_lex = 100
   - Dense (Qdrant): topK_vec = 100
3) Fusion
   - RRF on ranks; tie-break by source diversity
4) Rerank and diversification
   - Cross-encoder rerank top 50 (ms-marco-MiniLM-L-6-v2)
   - MMR with λ≈0.3; final top 10
5) Evidence packaging
   - Merge adjacent chunks; include page ranges and char offsets
   - Return doc_id, title, source_file, snippet, anchors

## SLO Guardrails (initial)
- Retrieval latency: p95 ≤ 600 ms (BM25 + dense + CE rerank top 50) on target hardware
- Indexing throughput: ≥ 20 chunks/sec CPU (batched); measured end-to-end
- Accuracy targets on internal QA set: +10–20% nDCG@10 vs baseline; track MRR@10, Recall@50
- Stability: zero fabricated answers; citations must map to actual content on disk

## Observability & Audit
- Real /metrics: requests, p95, error counts for ingestion and query
- Structured logs: doc_id, candidate counts, fused ranks, rerank scores (redact PII)
- Deterministic seeds for rerank tie-breaks (repeatable)

## Acceptance (pre-commit checklist)
- Real: Verify doc_id exists in Qdrant and OpenSearch after ingestion
- User value: `/query` returns true snippets and source paths from user-ingested PDFs
- Dynamic: Change in corpus changes results (remove/add) – demonstrate
- Real user test: Script with curl commands and expected structural outputs (citations + snippet present)

## Phasing
- PR-0: Compose OpenSearch; design docs; health verification
- PR-1: Ingestion to Qdrant + OpenSearch (no mocks), audit logs, metrics
- PR-2: Hybrid retrieval in Regulus backend with RRF + CE rerank + MMR
- PR-3: Thalamus to use hybrid gateway; return richer citations
- PR-4: Confidence fusion & calibration plan; abstention gating
