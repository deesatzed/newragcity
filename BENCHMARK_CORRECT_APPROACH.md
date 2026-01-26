# Benchmarking newragcity: The CORRECT Unified Approach

**Date**: January 25, 2026
**Anti-Drift System**: MISSION_CRITICAL.md enforced
**Status**: ✅ No Drift Detected

---

## ✅ CORRECT APPROACH: Unified System Benchmarking

### What to Run

**Command**:
```bash
bash test_unified_system.sh
```

**Or with Docker**:
```bash
# Start complete system (10 services)
docker-compose up -d

# Wait for initialization
sleep 120

# Run benchmark tests
bash test_unified_system.sh
```

---

## What This Tests (Unified System)

### 1. Complete System Integration
- **All 10 services working together**:
  - ultrarag (orchestration)
  - dkr-server (deterministic retrieval)
  - ersatz-server (semantic search orchestrator)
  - leann-service (vector search)
  - deepconf-service (confidence scoring)
  - pageindex-service (document intelligence)
  - rot-server (visual reasoning)
  - postgres (database)
  - redis (caching)
  - ollama (local LLM)

### 2. End-to-End Query Workflow
```
User Query
    ↓
POST http://localhost:8000/query
    ↓
UltraRAG Orchestrator
    ↓
DKR + Ersatz + RoT (in parallel or sequential)
    ↓
Results Aggregation + Confidence Scoring
    ↓
Unified Response
```

### 3. Metrics Measured
- ✅ **Query Latency**: End-to-end time from query to response (target <10s p95)
- ✅ **Confidence Accuracy**: Calibration of confidence scores (target >90%)
- ✅ **Multi-Approach Routing**: Which approaches participated (audit trail)
- ✅ **Citation Quality**: Completeness and accuracy of source references
- ✅ **Response Quality**: Correctness of answers with all approaches integrated

### 4. Test Scenarios
1. **Document Upload**: Tests complete ingestion pipeline
   - PageIndex generates hierarchical structure
   - LEANN indexes with IBM Granite embeddings
   - DKR builds exact matching index
   - All working together

2. **Exact Lookup Query**: Tests DKR prioritization
   - Query: "Error code E-4217"
   - DKR should handle exact matches
   - Ersatz provides semantic context
   - Response includes both

3. **Conceptual Query**: Tests Ersatz semantic search
   - Query: "What are best practices for..."
   - Ersatz (LEANN + PageIndex + deepConf) leads
   - DKR provides exact references if available
   - RoT adds reasoning if complex

4. **Complex Multi-Step**: Tests RoT visual compression
   - Query: "Analyze this contract for compliance issues across 5 departments"
   - RoT assesses complexity (high)
   - Generates compressed visual reasoning
   - Ersatz provides source context
   - DKR provides exact policy references

---

## ❌ WRONG APPROACH: Component Isolation (Drift #5 Pattern)

### What NOT to Do

**DO NOT create**:
```python
# servers/rot_reasoning/benchmarks/dkr_evaluator.py   ❌ WRONG
# servers/rot_reasoning/benchmarks/ersatz_evaluator.py ❌ WRONG

# These test components in isolation, not the unified system!
```

**DO NOT run**:
```bash
# Test DKR alone                    ❌ WRONG
python deterministic_knowledge_retrieval/tests/test_toc_agent.py

# Test Ersatz alone                 ❌ WRONG
python ersatz_rag/tests/test_cognitron_integration.py

# Test RoT alone                     ❌ WRONG
python servers/rot_reasoning/benchmarks/run_benchmarks.py --quick-test
```

### Why This is Wrong

**User perspective**:
- Users run ONE app: `docker-compose up -d`
- Users query ONE endpoint: `http://localhost:8000/query`
- Users receive ONE response from ALL approaches integrated

**Testing components individually**:
- ❌ Tests subsystems that users never interact with directly
- ❌ Doesn't validate integration (the actual value proposition)
- ❌ Misses routing logic (when to use which approach)
- ❌ Doesn't measure end-to-end performance
- ❌ Treats newragcity as 4 separate apps instead of ONE unified system

---

## Benchmark Comparison

### Before (Drift #5 - WRONG)

**Proposed approach** (January 25, 2026 morning):
```python
# Implement isolated evaluators
- dkr_evaluator.py: Test DKR alone on BEIR
  - Metrics: Exact match rate, precision, recall

- ersatz_evaluator.py: Test Ersatz alone on BEIR
  - Metrics: nDCG@10, semantic similarity

- rot_evaluator.py: Test RoT alone on compression
  - Metrics: Compression ratio, speedup

# Result: Three separate benchmarks for three separate apps
```

**Problems**:
1. Doesn't test the actual product users interact with
2. Misses integration value (multi-approach routing)
3. Can't measure end-to-end confidence calibration
4. Ignores UltraRAG orchestration layer

### After (Anti-Drift System - CORRECT)

**Actual approach** (January 25, 2026 evening):
```bash
# Test unified system
bash test_unified_system.sh

# Measures:
1. End-to-end query latency (complete system)
2. Multi-approach routing effectiveness
3. Confidence calibration across all approaches
4. Citation quality from integrated sources
5. Response quality with DKR + Ersatz + RoT working together

# Result: One unified benchmark for one unified system
```

**Benefits**:
1. ✅ Tests what users actually experience
2. ✅ Validates integration (the core value proposition)
3. ✅ Measures complete system performance
4. ✅ Verifies all approaches work together correctly
5. ✅ Aligns with docker-compose.yml architecture

---

## Deployment Options for Benchmarking

### Option 1: Docker Compose (Full System)
```bash
# Prerequisites
docker --version  # Ensure Docker installed
docker-compose --version

# Start system
cp .env.example .env
docker-compose up -d

# Wait for initialization
sleep 120

# Run benchmarks
bash test_unified_system.sh

# View results
docker-compose logs -f ultrarag
```

### Option 2: The Vault Pipeline (Direct Orchestration)
```bash
# Prerequisites
uv sync  # Install dependencies

# Run integrated pipeline
bash TheVault/run_vault.sh

# This runs vault_main.yaml which orchestrates:
# - DKR initialization
# - Ersatz initialization
# - Query processing through both approaches
# - Result synthesis
```

### Option 3: Manual API Testing
```bash
# Start system (either method above)

# Upload test document
curl -X POST http://localhost:8000/upload \
  -F "file=@test_document.pdf"

# Run query (tests ALL approaches)
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the incident response procedure?",
    "confidence_threshold": 0.85,
    "show_audit_trail": true
  }'

# Examine response:
# - answer: Generated response
# - confidence: Calibrated score
# - sources: Citations from DKR, Ersatz, RoT
# - audit_trail: Which approaches participated
```

---

## Success Criteria

### ✅ System is Working Correctly When:

1. **All services start successfully**
   ```bash
   docker-compose ps
   # Should show 10 services running
   ```

2. **End-to-end queries work**
   ```bash
   curl http://localhost:8000/query
   # Returns response with all approaches integrated
   ```

3. **Audit trail shows multi-approach integration**
   ```json
   {
     "audit_trail": {
       "dkr_used": true,
       "ersatz_used": true,
       "rot_used": false  // or true for complex queries
     }
   }
   ```

4. **Performance meets targets**
   - Query latency <10s (p95)
   - Confidence calibration >90% accuracy
   - Citations complete and accurate

---

## Anti-Drift Verification

### Before Starting Benchmarks, Ask:

1. **Am I testing the unified system?** (YES required)
   - ✅ YES: docker-compose up, query unified endpoint
   - ❌ NO: Testing DKR/Ersatz/RoT separately

2. **Am I treating components as separate apps?** (NO required)
   - ✅ NO: Components are subsystems of ONE app
   - ❌ YES: Creating dkr_evaluator.py, etc.

3. **Would this make sense to end users?** (YES required)
   - ✅ YES: Testing the product they interact with
   - ❌ NO: Testing internal subsystems

4. **Am I following docker-compose.yml?** (YES required)
   - ✅ YES: All 10 services working together
   - ❌ NO: Running individual Python scripts

**If ANY answer is wrong** → Read MISSION_CRITICAL.md → Course correct

---

## Files for Unified Benchmarking

**Created**:
- ✅ `test_unified_system.sh` - Unified benchmark test script
- ✅ `BENCHMARK_CORRECT_APPROACH.md` - This document

**Reference**:
- ✅ `MISSION_CRITICAL.md` - Anti-drift guardrails
- ✅ `docker-compose.yml` - Complete system definition
- ✅ `QUICK_START.md` - User deployment guide
- ✅ `TheVault/run_vault.sh` - Alternative execution method
- ✅ `TheVault/pipeline/vault_main.yaml` - Integration pipeline

**Do NOT use** (drift patterns):
- ❌ `servers/rot_reasoning/benchmarks/run_benchmarks.py` (isolated RoT)
- ❌ `servers/rot_reasoning/benchmarks/dkr_evaluator.py` (would be drift)
- ❌ `servers/rot_reasoning/benchmarks/ersatz_evaluator.py` (would be drift)

---

## Summary

**CORRECT unified approach**:
```
User says: "Run the benchmarks"
→ Start docker-compose up -d (complete system)
→ Run test_unified_system.sh (end-to-end tests)
→ Measure: DKR + Ersatz + RoT working TOGETHER
→ ✅ SUCCESS: Tested the actual product
```

**WRONG drift pattern (Drift #5)**:
```
User says: "Run the benchmarks"
→ Analyze servers/rot_reasoning/benchmarks/
→ Propose dkr_evaluator.py, ersatz_evaluator.py
→ Test components individually
→ ❌ DRIFT: Forgot this is ONE unified system
```

**Remember**: newragcity = DKR + Ersatz + RoT + UltraRAG (TOGETHER)

---

**Document Status**: ✅ Active Benchmark Guide
**Enforces**: MISSION_CRITICAL.md principles
**Last Updated**: January 25, 2026
