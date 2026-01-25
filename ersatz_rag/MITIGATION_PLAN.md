# Mitigation Plan: Regulus, Thalamus, Cognitron

Decisions (confirmed)
- Dense model: bge-large-en-v1.5
- OpenSearch confirmed for lexical/BM25
- SLO guardrails: initial p95 ≤ 600 ms for retrieval with hybrid + rerank; revisit after measurements
- Abstention allowed when evidence is weak or inconsistent

## Current Caveats (No Mocks)
- Regulus
  - No true hybrid retrieval yet; `/metrics` endpoint is a stub
  - Model/DB defaults may hinder dev speed unless configured
- Thalamus
  - Retrieval previously ranked naive candidates; confidence uncalibrated
- Cognitron / LEANN
  - In-memory only (loss on restart); mem-agent clarify is passthrough (notes are real)

## Phase 1: Hybrid Retrieval & Observability (Real Only)
- Add OpenSearch service (done in compose) and verify health
- Implement ingestion to Qdrant (dense) + OpenSearch (lexical): chunks, dedup, embeddings, payloads
- Expose real `/metrics` for ingestion/query
- Return doc_id/source_file/anchors with every result

## Phase 2: Confidence & Validation
- Build fused confidence using deepConf + retrieval signals (reranker score, evidence count, coverage, entailment)
- Calibrate via Platt/Isotonic on labeled QA set
- Add abstention threshold and minimum evidence requirements

## Phase 3: Query Understanding & Recall
- Add query rewriting (k=3) and HyDE; fuse candidates via RRF; cap rerank set ≤ 100
- Optional PRF; explore SPLADE/docT5query in OpenSearch if beneficial
- Consider multi-hop for complex queries

## Phase 4: Persistence & Resilience
- Make LEANN persistent (Qdrant volumes; service-level upsert)
- Replace Regulus `/metrics` stub with real counters
- Add alerts on error rates and latency SLO breaches

## Acceptance Criteria (4 Gates)
1. Real functionality: Ingestion writes verifiably to Qdrant and OpenSearch
2. User value: `/query` returns true snippets and citations from ingested docs
3. Dynamic: Changing corpus changes results; demonstrate both add/remove cases
4. Real user test: Human runs documented commands and verifies citations/snippets exist in actual files

## Testing Plan
- Integration tests that:
  - Verify `/metrics` increments for ingestion and query
  - Validate citations refer to actual file paths and byte ranges
  - Measure p95 latency and log to artifacts
- Coverage gaps: document and add follow-up tasks until ≥ 100% or waived explicitly

## Security & Compliance
- No fabricated outputs; provenance returned with results
- Redact PII in logs; rotate logs; store audit records for ingestion actions
