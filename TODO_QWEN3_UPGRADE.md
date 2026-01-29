# TODO: Upgrade to Qwen3-Embedding-0.6B

**Priority**: High (after quick validation completes)
**Effort**: Medium (2-4 hours)
**Impact**: +10-15% performance improvement expected

---

## Current Situation

**Using**: BAAI/bge-base-en-v1.5 (109M params, 768 dims)
- **Why**: Compatibility, stability, works out-of-the-box
- **Status**: ✅ Running successfully in quick validation benchmark
- **Performance**: Expected 0.45-0.65 nDCG@10 (competitive)

**Desired**: Qwen/Qwen3-Embedding-0.6B (600M params, higher dims)
- **Why**: Newer, potentially better performance, 5× larger than BGE
- **Status**: ❌ Blocked by transformers version incompatibility
- **Blocker**: Requires `transformers>=4.50.0` (bleeding edge)

---

## Why Qwen3 Failed

### Error 1: Model Type Not Recognized
```
Error: The checkpoint you are trying to load has model type `qwen3`
but Transformers does not recognize this architecture.
```

**Root Cause**:
- Qwen3 architecture is too new for current transformers version
- Current environment likely has transformers 4.35-4.45
- Qwen3 requires transformers>=4.50.0 (not yet stable)

### Attempted Model IDs
1. ❌ `Qwen/Qwen3-Embedding-0.6B` - Correct ID, but architecture not supported
2. ❌ `Alibaba-NLP/Qwen3-Embedding-0.6B` - Invalid namespace

---

## Upgrade Plan

### Phase 1: Environment Preparation (30 min)

**Create isolated test environment**:
```bash
# Create new conda environment
conda create -n qwen3_test python=3.11 -y
conda activate qwen3_test

# Install bleeding-edge transformers
pip install transformers>=4.50.0 --upgrade

# Install other dependencies
pip install sentence-transformers torch numpy scipy
```

**Test Qwen3 loading**:
```python
from sentence_transformers import SentenceTransformer

# Test if Qwen3 loads
model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B", trust_remote_code=True)
print(f"Model loaded: {model}")
print(f"Embedding dim: {model.get_sentence_embedding_dimension()}")

# Test embedding generation
embeddings = model.encode(["test query"])
print(f"Embedding shape: {embeddings.shape}")
```

**Expected Output**:
```
Model loaded: SentenceTransformer(...)
Embedding dim: 1024 (or similar)
Embedding shape: (1, 1024)
```

### Phase 2: Dependency Audit (30 min)

**Check for breaking changes**:
```bash
# List current transformers version
pip show transformers

# Check what else depends on transformers
pip show -f transformers | grep Requires

# Test critical imports
python -c "from app.three_approach_integration import ThreeApproachRAG"
```

**Potential conflicts**:
- `leann` library may have transformers version constraints
- `sentence_transformers` compatibility with transformers>=4.50.0
- Other UltraRAG components using transformers

**Mitigation**:
- Document all version requirements in `requirements_qwen3.txt`
- Create separate Docker image with Qwen3 dependencies
- Test each component individually before full integration

### Phase 3: Integration Testing (1-2 hours)

**Update configuration files**:
```bash
# Update all embedding model references
.env: EMBEDDING_MODEL=Qwen/Qwen3-Embedding-0.6B
docker-compose.yml: EMBEDDING_MODEL=Qwen/Qwen3-Embedding-0.6B
servers/retriever/parameter.yaml: model_name_or_path=Qwen/Qwen3-Embedding-0.6B
beir_unified_benchmark.py: embedding_model="Qwen/Qwen3-Embedding-0.6B"
beir_all_datasets.py: embedding_model="Qwen/Qwen3-Embedding-0.6B"
```

**Run validation tests**:
```bash
# Test ThreeApproachRAG initialization
python -c "
from app.three_approach_integration import ThreeApproachRAG
rag = ThreeApproachRAG(
    embedding_model='Qwen/Qwen3-Embedding-0.6B',
    confidence_threshold=0.80
)
print('✅ ThreeApproachRAG initialized successfully')
"

# Test small-scale benchmark (50 queries)
cd ersatz_rag/regulus/backend/benchmarks
python beir_unified_benchmark.py --max-queries 50
```

**Success Criteria**:
- ✅ No import errors
- ✅ Model loads without errors
- ✅ Embeddings generated successfully
- ✅ No MPS out-of-memory errors (600M should fit in 48GB)
- ✅ nDCG@10 scores > BGE baseline

### Phase 4: Production Deployment (30 min)

**If all tests pass**:
```bash
# Update production requirements
pip freeze > requirements_qwen3.txt

# Commit changes
git add -A
git commit -m "feat: Upgrade to Qwen3-Embedding-0.6B for improved performance

- Upgraded transformers to >=4.50.0
- Updated all embedding model references to Qwen/Qwen3-Embedding-0.6B
- Validated compatibility with ThreeApproachRAG system
- Expected performance improvement: +10-15% nDCG@10

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to GitHub
git push origin main
```

**Re-run quick validation**:
```bash
cd ersatz_rag/regulus/backend/benchmarks
./run_automated_sota.sh quick
```

**Compare results**:
- BGE baseline: 0.45-0.65 nDCG@10 (current)
- Qwen3 target: 0.55-0.75 nDCG@10 (expected +10-15%)

---

## Rollback Plan

**If Qwen3 upgrade fails**:

1. **Revert changes**:
   ```bash
   git revert HEAD
   git push origin main
   ```

2. **Restore BGE configuration**:
   - All config files automatically restored to BGE via git revert

3. **Document failure**:
   - Log specific error messages
   - Identify blocking dependencies
   - Create GitHub issue for future resolution

4. **Alternative**: Stay with BGE for now
   - BGE is proven, stable, and competitive
   - Acceptable for validation and initial benchmarking
   - Revisit Qwen3 after transformers>=4.50.0 becomes stable

---

## Expected Performance Gains

### Model Comparison

| Model | Params | Dims | MTEB Rank | Expected nDCG@10 | Memory |
|-------|---------|------|-----------|------------------|--------|
| BGE-base | 109M | 768 | #1 in class | 0.45-0.65 | 1-2 GB |
| Qwen3-0.6B | 600M | 1024+ | Top 3 overall | 0.55-0.75 | 5-8 GB |

### BEIR Benchmark Projections

**With BGE (current)**:
- nfcorpus: 0.45-0.55 (vs SOTA 0.3381) = +33-63%
- scifact: 0.55-0.65 (vs SOTA 0.6885) = -5% to +9%
- arguana: 0.45-0.55 (vs SOTA 0.6375) = -29% to -14%

**With Qwen3 (expected)**:
- nfcorpus: 0.55-0.65 (vs SOTA 0.3381) = +63-92%
- scifact: 0.65-0.75 (vs SOTA 0.6885) = +9% to +18%
- arguana: 0.55-0.65 (vs SOTA 0.6375) = -14% to +2%

**Aggregate improvement**: +10-15% across all datasets

---

## Timeline

**Trigger**: After quick validation benchmark completes successfully with BGE

**Total Time**: 2-4 hours

| Phase | Duration | Dependencies |
|-------|----------|-------------|
| Environment Setup | 30 min | conda, pip |
| Dependency Audit | 30 min | Current system stable |
| Integration Testing | 1-2 hours | Small-scale benchmark data |
| Production Deployment | 30 min | All tests pass |

**Start After**: BGE quick validation results reviewed and validated

---

## Success Metrics

**Upgrade is successful if**:
1. ✅ Qwen3 model loads without errors
2. ✅ No breaking changes to other components
3. ✅ nDCG@10 scores improve by ≥5% over BGE
4. ✅ No MPS out-of-memory errors
5. ✅ Query latency remains acceptable (<10s p95)

**Upgrade is deferred if**:
1. ❌ transformers>=4.50.0 breaks critical dependencies
2. ❌ Qwen3 causes MPS memory issues (unlikely with 600M)
3. ❌ Performance does not improve over BGE
4. ❌ Integration testing reveals compatibility issues

---

## Current Status

- **BGE Benchmark**: ✅ Running (process 8089)
- **Qwen3 Upgrade**: 🕐 Pending (after BGE validation completes)
- **Priority**: High (next task after current benchmark)
- **Owner**: To be assigned after quick validation review

---

**Created**: 2026-01-29
**Last Updated**: 2026-01-29
**Status**: Pending - Waiting for BGE quick validation results
