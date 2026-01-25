# Universal Knowledge Pack (UKP) - Future Features Roadmap

**Status**: Captured from `domain_agnostic_knowledge_pack.md` after Phase 2 completion  
**Date**: 2025-10-13  
**Current System**: Multi-domain capable, agent-based, production-ready

---

## ✅ Already Implemented (Phase 2 Complete)

| Feature | UKP Concept | Current Implementation | Status |
|---------|-------------|----------------------|--------|
| **Lossless citations** | Span hashes + offsets | Section IDs + stable identifiers | ✅ Done |
| **Vector-free retrieval** | Deterministic filtering | TF-IDF + metadata + disambiguation | ✅ Done |
| **Modular orchestration** | MCP roles | TOC/Loader/Answer agents | ✅ Done |
| **Token-aware** | Budget enforcement | LoaderAgent with 4000 token budget | ✅ Done |
| **Auditable** | Provenance | Plain JSON, stable citations | ✅ Done |
| **Domain adapters** | Pluggable converters | Healthcare + Generic adapters | ✅ Done |
| **Policy enforcement** | RBAC + sensitivity | PolicyEnforcer (PHI/PII/residency) | ✅ Done |

---

## 🔮 Future Features (Post-MVP)

### Phase 3: Enhanced Citations & Integrity

#### 1. Content Hashing (`content_sha256`, `span_sha256`)
**UKP Reference**: Lines 27, 37-38, 106-107

**Value**: Cryptographic proof of citation integrity

**Implementation**:
```python
# Add to section schema
{
  "section_id": "ch04_se2",
  "content_sha256": "a3f5...",  # Hash of full section
  "span_sha256": "b7c2...",     # Hash of cited excerpt
  "byte_offset": [1024, 2048]   # Exact span location
}
```

**Benefits**:
- Byte-for-byte verification of citations
- Detect if source content changed
- Immutable audit trail

**Effort**: Medium (2-3 days)

---

#### 2. Lossless Proof Protocol (LPP)
**UKP Reference**: Lines 104-108

**Value**: Verifiable provenance bundles

**Implementation**:
```json
{
  "query": "What is the treatment for DKA?",
  "answer": "...",
  "citations": [
    {
      "section_id": "ch04_se2",
      "path": "/sections/4/text",
      "start": 1024,
      "end": 2048,
      "content_sha256": "a3f5...",
      "verified": true
    }
  ],
  "provenance": {
    "timestamp": "2025-10-13T07:30:00Z",
    "model": "gpt-4",
    "tokens_used": 1250,
    "deterministic_score": 0.85,
    "semantic_score": 0.82
  }
}
```

**Benefits**:
- One-click replay of queries
- Audit compliance
- Citation verification

**Effort**: Medium (3-4 days)

---

### Phase 4: Advanced Retrieval

#### 3. Declarative Retrieval Plan (DRP)
**UKP Reference**: Lines 51-72

**Value**: Structured query planning for complex tasks

**Implementation**:
```json
{
  "plan_id": "query_123",
  "goals": ["answer question", "justify with citations"],
  "filters": [
    {"field": "tags", "op": "contains", "value": "diabetes"},
    {"field": "date", "op": ">=", "value": "2024-01-01"}
  ],
  "ops": [
    {"op": "LOAD", "paths": ["file_a.json#/sec/2"]},
    {"op": "REDUCE", "strategy": "dedupe+salience"},
    {"op": "SYNTHESIZE"},
    {"op": "VERIFY", "mode": "cite-by-hash"}
  ],
  "budgets": {"max_tokens_ctx": 4000, "max_paths": 10}
}
```

**Benefits**:
- Multi-step reasoning
- Complex queries (compare, compute, timeline)
- Explicit query plans (debuggable)

**Effort**: High (1-2 weeks)

---

#### 4. Multi-Pass Retrieval (Wide → Narrow → Final)
**UKP Reference**: Lines 100-102

**Value**: Better recall for complex queries

**Implementation**:
```python
# Pass 1: Wide net (low threshold)
candidates = toc_agent.route_query(query, threshold=0.3)  # Get 20 candidates

# Pass 2: Narrow (re-rank with more context)
top_candidates = rerank(candidates, query, top_k=5)

# Pass 3: Final (load only best)
final_sections = loader_agent.load(top_candidates[:2])
```

**Benefits**:
- Better coverage for ambiguous queries
- Reduced false negatives
- Still deterministic (just more passes)

**Effort**: Medium (3-5 days)

---

### Phase 5: Declarative Computations

#### 5. Models Layer (`models.jsonl`)
**UKP Reference**: Lines 30, 66

**Value**: Enable calculations without code

**Implementation**:
```json
// models.jsonl
{"id": "yoy_growth", "formula": "(q2-q1)/q1", "inputs": ["q1", "q2"]}
{"id": "avg_price", "formula": "sum(prices)/count(prices)", "inputs": ["prices[]"]}

// In DRP:
{"op": "COMPUTE", "model_id": "yoy_growth", "inputs": {"q1": 100, "q2": 120}}
// Result: 0.20 (20% growth)
```

**Benefits**:
- Financial analysis (growth, ratios)
- Scientific calculations
- No custom code per query

**Effort**: High (1-2 weeks)

---

### Phase 6: Relations & Graph

#### 6. Relations Layer (`relations.jsonl`)
**UKP Reference**: Line 29

**Value**: Cross-references between sections

**Implementation**:
```json
// relations.jsonl
{"from": "ch04_se2", "to": "ch05_se1", "type": "references", "label": "See also"}
{"from": "ch04_se2", "to": "table_01", "type": "contains", "label": "Data"}
{"from": "ch04_se2", "to": "fig_03", "type": "illustrates", "label": "Figure"}
```

**Benefits**:
- "See also" recommendations
- Table/figure linking
- Document graph traversal

**Effort**: Medium (4-5 days)

---

### Phase 7: Advanced Kits

#### 7. Compare Kit
**UKP Reference**: Lines 189-196

**Value**: Schema-agnostic diff/contrast

**Use Cases**:
- Compare treatment protocols across guidelines
- Diff policy versions
- Contrast financial quarters

**Effort**: Medium (3-4 days)

---

#### 8. Timeline Kit
**UKP Reference**: Lines 189-196

**Value**: Time-ordered narratives

**Use Cases**:
- Patient timeline (EMR)
- Policy evolution
- Financial history

**Effort**: Medium (3-4 days)

---

#### 9. Table Kit
**UKP Reference**: Lines 189-196

**Value**: Normalize/union disparate tables

**Use Cases**:
- Merge pricing tables
- Combine lab results
- Financial statement consolidation

**Effort**: High (1 week)

---

### Phase 8: Performance & Scale

#### 10. Delta Loading
**UKP Reference**: Line 102

**Value**: Never reload same span twice

**Implementation**:
```python
class LoaderAgent:
    def __init__(self):
        self.loaded_hashes = set()  # Track loaded content
    
    def request_load(self, section):
        content_hash = sha256(section['text'])
        if content_hash in self.loaded_hashes:
            return False, "Already loaded (delta skip)"
        self.loaded_hashes.add(content_hash)
        # ... load section
```

**Benefits**:
- Reduced token usage
- Faster multi-turn conversations
- Lower costs

**Effort**: Low (1-2 days)

---

#### 11. Parallel Sharding
**UKP Reference**: Lines 78, 161

**Value**: Speed up retrieval with parallel workers

**Implementation**:
```python
# Split candidates across workers
shards = shard_candidates(candidates, num_workers=4)

# Process in parallel
results = await asyncio.gather(*[
    worker.process(shard) for shard in shards
])

# Merge results
final = merge_and_rank(results)
```

**Benefits**:
- 2-4x speedup for large knowledge bases
- Better P95 latency
- Scales to millions of sections

**Effort**: High (1-2 weeks)

---

### Phase 9: Observability

#### 12. Glass Box Telemetry
**UKP Reference**: Lines 158-162

**Value**: Full visibility into retrieval decisions

**Implementation**:
```json
{
  "query_id": "q_123",
  "stages": [
    {
      "stage": "routing",
      "candidates": 50,
      "time_ms": 12,
      "top_scores": [85, 72, 68]
    },
    {
      "stage": "loading",
      "sections_loaded": 2,
      "tokens_used": 1200,
      "time_ms": 45
    },
    {
      "stage": "synthesis",
      "tokens_generated": 250,
      "time_ms": 1800,
      "model": "gpt-4"
    }
  ],
  "total_cost": "$0.0042",
  "total_time_ms": 1857
}
```

**Benefits**:
- Debug slow queries
- Optimize costs
- Monitor quality

**Effort**: Medium (3-4 days)

---

### Phase 10: Additional Domains

#### 13. Finance Adapter
**Value**: Financial documents, reports, statements

**Sources**:
- SEC filings (10-K, 10-Q)
- Earnings reports
- Financial statements

**Effort**: Medium (3-5 days)

---

#### 14. Policy Adapter
**Value**: Legal/policy documents

**Sources**:
- Regulations
- Compliance documents
- Legal contracts

**Effort**: Medium (3-5 days)

---

#### 15. Code Adapter
**Value**: Source code as knowledge

**Sources**:
- AST parsing
- Function/class extraction
- Docstring indexing

**Effort**: High (1 week)

---

## 📊 Priority Matrix

| Feature | Value | Effort | Priority | Phase |
|---------|-------|--------|----------|-------|
| Content hashing | High | Medium | 🔥 High | 3 |
| Lossless Proof Protocol | High | Medium | 🔥 High | 3 |
| Delta loading | Medium | Low | 🔥 High | 3 |
| Multi-pass retrieval | Medium | Medium | ⚠️ Medium | 4 |
| Relations layer | Medium | Medium | ⚠️ Medium | 4 |
| Declarative Retrieval Plan | High | High | ⚠️ Medium | 4 |
| Declarative computations | High | High | ⚠️ Medium | 5 |
| Compare Kit | Medium | Medium | ⚠️ Medium | 7 |
| Timeline Kit | Medium | Medium | ⚠️ Medium | 7 |
| Table Kit | High | High | ⚠️ Medium | 7 |
| Glass Box Telemetry | High | Medium | ⚠️ Medium | 9 |
| Parallel sharding | Medium | High | 🔵 Low | 8 |
| Finance adapter | Medium | Medium | 🔵 Low | 10 |
| Policy adapter | Medium | Medium | 🔵 Low | 10 |
| Code adapter | Medium | High | 🔵 Low | 10 |

---

## 🎯 Recommended Sequence

### **Phase 3: Enhanced Integrity** (1-2 weeks)
1. Content hashing
2. Lossless Proof Protocol
3. Delta loading

### **Phase 4: Advanced Retrieval** (2-3 weeks)
4. Multi-pass retrieval
5. Relations layer
6. Declarative Retrieval Plan

### **Phase 5: Computations** (1-2 weeks)
7. Declarative computations (`models.jsonl`)

### **Phase 7: Kits** (2-3 weeks)
8. Compare Kit
9. Timeline Kit
10. Table Kit

### **Phase 8: Performance** (2-3 weeks)
11. Parallel sharding
12. Caching optimizations

### **Phase 9: Observability** (1 week)
13. Glass Box Telemetry
14. Cost tracking

### **Phase 10: Domain Expansion** (ongoing)
15. Finance adapter
16. Policy adapter
17. Code adapter

---

## 📝 Notes

- **All features maintain**: Deterministic routing, vector-free retrieval, lossless citations
- **Backward compatible**: Existing AJ Packs continue to work
- **Incremental**: Each phase adds value without breaking previous work
- **Tested**: Each feature requires comprehensive test coverage

---

**Document maintained by**: Cascade AI  
**Last updated**: 2025-10-13  
**Status**: Living document - update as features are implemented
