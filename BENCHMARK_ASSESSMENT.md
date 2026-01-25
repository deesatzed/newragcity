# newragcity Benchmark Assessment: 2026 SOTA Evaluation

**Date**: January 25, 2026
**Source**: Analysis of benchmark_possible.md
**Status**: 7 out of 11 benchmark categories ready or achievable

---

## Executive Summary

newragcity can test **7 out of 11 recommended 2026 SOTA benchmark categories** from benchmark_possible.md. The system has:
- ✅ **4 benchmarks ready to test** (BEIR, CRAG, LongBench, Efficiency)
- ⚠️ **3 benchmarks achievable with additions** (MTEB, Golden Set, RAGBench)
- ❌ **4 benchmarks not applicable or too difficult** (LiveRAG, MedQA, FinanceBench, CodeRAG)

The RoT component has a complete benchmark framework (`run_benchmarks.py`) that needs only dataset downloads and model training to produce SOTA validation results.

---

## Detailed Benchmark Analysis

### ✅ Category 1: READY TO TEST (Framework complete, needs data/models)

#### 1.1 BEIR (Retrieval-Focused) - **HIGH PRIORITY**

**From benchmark_possible.md**:
- **Purpose**: Standard retrieval quality benchmark
- **Datasets**: 18 diverse tasks (nfcorpus, scifact, fiqa, etc.)
- **Metrics**: nDCG@10, Recall@100, MRR
- **2026 SOTA**: ~68-75% nDCG@10 average
- **Why Use**: Tests pure retrieval accuracy across heterogeneous data

**newragcity Status**: ✅ **Framework Complete**
- **Implementation**: `servers/rot_reasoning/benchmarks/run_benchmarks.py`
- **Configured datasets**: nfcorpus, scifact, fiqa
- **Configured metrics**: nDCG@10, recall@100, MRR
- **Infrastructure**: Complete with statistical significance testing (3+ runs, mean ± std)

**What's Needed**:
```bash
# Install dependencies
pip install beir datasets numpy scipy

# Download BEIR datasets
python -c "from beir import util; util.download_and_unzip('nfcorpus', 'datasets/beir')"
python -c "from beir import util; util.download_and_unzip('scifact', 'datasets/beir')"
python -c "from beir import util; util.download_and_unzip('fiqa', 'datasets/beir')"

# Train RoT model (see MODEL_SETUP.md)
```

**Test Command**:
```bash
# Quick test (100 samples, 1 dataset)
python servers/rot_reasoning/benchmarks/run_benchmarks.py --quick-test

# Full evaluation (3 datasets, 3 runs each)
python servers/rot_reasoning/benchmarks/run_benchmarks.py --benchmarks BEIR --runs 3
```

**Expected Results** (after RoT training):
- RoT nDCG@10: 0.40-0.50 (≥90% of vanilla)
- Vanilla nDCG@10: 0.45-0.55 (baseline)
- Compression: 3-4× token reduction
- Speedup: 2-3× inference speed

**SOTA Evaluation**:
- **Tier 1** (Production): ≥90% of baseline accuracy
- **Tier 2** (Competitive): ≥95% of baseline accuracy
- **Tier 3** (SOTA): ≥100% accuracy (equal or better)

---

#### 1.2 CRAG (End-to-End RAG) - **HIGH PRIORITY**

**From benchmark_possible.md**:
- **Purpose**: Challenging multi-hop and unanswerable queries
- **Datasets**: CRAG multi-hop QA
- **Metrics**: Faithfulness (0-1), Answer Relevance, ROUGE/EM
- **2026 SOTA**: 85-95% faithfulness (Agentic RAG variants)
- **Why Use**: Evaluates full RAG pipeline; exposes weaknesses in production

**newragcity Status**: ✅ **Framework Complete**
- **Implementation**: `run_benchmarks.py` CRAG configuration
- **Configured datasets**: crag_multi_hop
- **Configured metrics**: faithfulness, accuracy, f1
- **Evaluation method**: LLM-as-judge for faithfulness scoring

**What's Needed**:
```bash
# Download CRAG from Hugging Face
pip install datasets
python -c "from datasets import load_dataset; load_dataset('crag', cache_dir='datasets/crag')"
```

**Test Command**:
```bash
# Full CRAG evaluation with baselines
python run_benchmarks.py --benchmarks CRAG --baselines vanilla,graph --runs 3
```

**Expected Results**:
- Faithfulness: 0.85-0.92 (target ≥0.90)
- Accuracy: within 5% of vanilla RAG
- Improvement on multi-hop: 10-20% better than vanilla (due to compression efficiency)

**SOTA Claim Criteria**:
- Faithfulness ≥0.90 AND compression ≥3× → **Strong SOTA candidate**
- Faithfulness ≥0.95 → **Clear SOTA** for compressed RAG

---

#### 1.3 LongBench (Long-Context/Complex) - **MEDIUM PRIORITY**

**From benchmark_possible.md**:
- **Purpose**: Handling large docs or multi-step reasoning
- **Datasets**: LongBench RAG tasks
- **Metrics**: Recall@K, End-to-End Accuracy
- **2026 SOTA**: 70-90% on long-context (GraphRAG hybrids lead)
- **Why Use**: Critical for claiming advances over naive RAG

**newragcity Status**: ✅ **Framework Complete**
- **Implementation**: `run_benchmarks.py` LongBench configuration
- **Configured datasets**: longbench_rag
- **Configured metrics**: recall@k, accuracy
- **Relevance**: RoT compression should excel on long documents

**What's Needed**:
```bash
# Download LongBench
pip install datasets
python -c "from datasets import load_dataset; load_dataset('longbench', 'rag', cache_dir='datasets/longbench')"
```

**Test Command**:
```bash
python run_benchmarks.py --benchmarks LongBench --runs 3
```

**Expected Results**:
- Accuracy: 75-85% (competitive with GraphRAG)
- Compression advantage: 3-4× on long contexts
- Potential SOTA: If accuracy ≥85% with compression ≥3×

---

#### 1.4 Efficiency Metrics (RoT-Specific) - **HIGH PRIORITY**

**From benchmark_possible.md**:
- **Not explicitly listed**, but essential for compression techniques

**newragcity Status**: ✅ **Custom Implementation**
- **Implementation**: Built into RoT evaluator
- **Configured metrics**:
  - `compression_ratio`: original_tokens / compressed_tokens (target: ≥3.0×)
  - `speedup`: baseline_latency / rot_latency (target: ≥2.0×)
  - `cost_reduction`: (baseline_cost - rot_cost) / baseline_cost × 100 (target: ≥70%)

**What's Needed**:
- Train RoT model to measure actual metrics (currently placeholder mode)

**Test Command**:
```bash
python run_benchmarks.py --benchmarks Efficiency --runs 3
```

**Expected Results** (based on RoT claims):
- Compression: 3.0-4.0× (≥3.0× target) ✓
- Speedup: 2.0-3.0× (≥2.0× target) ✓
- Cost reduction: 70-75% (≥70% target) ✓
- Accuracy retention: ≥90% (critical for SOTA)

**SOTA Criteria**:
- **Tier 1**: Compression ≥2.0×, Speedup ≥1.5×, Accuracy ≥90%
- **Tier 2**: Compression ≥3.0×, Speedup ≥2.0×, Accuracy ≥95%, Cost ≥70%
- **Tier 3**: Compression ≥3.5×, Speedup ≥2.5×, Accuracy ≥100% (equal/better)

---

### ⚠️ Category 2: CAN TEST WITH ADDITIONS (Needs implementation)

#### 2.1 MTEB Retrieval Subset - **MEDIUM PRIORITY**

**From benchmark_possible.md**:
- **Purpose**: Comprehensive retrieval embedding evaluation
- **Datasets**: ~20 retrieval tasks
- **Metrics**: nDCG@10, Recall@100, MRR (same as BEIR)
- **2026 SOTA**: Top embeddings like Cohere embed-v4, NV-Embed-v2
- **Why Use**: Leaderboard comparison for retrieval quality

**newragcity Status**: ⚠️ **Can Add (4-8 hours)**
- **Not currently configured** in `run_benchmarks.py`
- **Would leverage**: Existing LEANN (Ersatz) vector search
- **Integration point**: `ersatz_rag/leann_service/` with IBM Granite embeddings

**Implementation Plan**:
1. Add MTEB to `BENCHMARKS` dict in `run_benchmarks.py`
2. Create MTEB dataset loader (integrate with LEANN)
3. Test IBM Granite embeddings against MTEB tasks
4. Compare to SOTA (Cohere embed-v4, BGE-large-en-v1.5)

**Expected Results**:
- IBM Granite nDCG@10: ~60-70% (competitive with BGE)
- LEANN + PageIndex boost: +5-10% over vanilla embeddings
- Potential SOTA: If combined approach exceeds 70% avg nDCG@10

**Why Add This**:
- Strong retrieval baseline comparison
- Validates LEANN (Ersatz) vector search quality
- Leaderboard position for retrieval component

---

#### 2.2 Custom Golden Set Evaluation - **HIGH PRIORITY**

**From benchmark_possible.md**:
- **Purpose**: Real-world evaluation with domain data
- **Approach**: Human evaluation or LLM-as-judge
- **Metrics**: Domain-specific accuracy, faithfulness, user satisfaction

**newragcity Status**: ✅ **Partially Implemented**
- **Scripts**: `TheVault/scripts/generate_eval.py`, `run_eval.py`
- **Capability**: Generate synthetic Q/A pairs from uploaded documents
- **Process**:
  1. Upload documents to `TheVault/data/input_docs/`
  2. Generate corpus: `python scripts/ingest_bulk.py`
  3. Create golden set: `python scripts/generate_eval.py --samples 50`
  4. Evaluate: `python scripts/run_eval.py`

**Test Command**:
```bash
# Generate 50 Q/A pairs from your documents
python TheVault/scripts/generate_eval.py --samples 50 --model qwen2.5-14b-instruct

# Run evaluation
python TheVault/scripts/run_eval.py --golden_set TheVault/data/golden_set.json
```

**What's Needed**:
- Upload domain-specific documents (PDFs, TXT, DOCX)
- Configure confidence thresholds (default: 0.80)
- Integrate with multi-approach routing (DKR + Ersatz + RoT)

**Expected Results**:
- Accuracy: 85-95% on domain-specific queries
- Faithfulness: 90-95% (with confidence gating)
- Citation accuracy: 95%+ (DKR exact references)
- Multi-approach advantage: 10-20% improvement over single-method RAG

**Why This Is Critical**:
- Real-world validation (not just academic benchmarks)
- Demonstrates multi-approach routing value
- Production-ready evaluation

---

#### 2.3 RAGBench (Enterprise-Like) - **MEDIUM PRIORITY**

**From benchmark_possible.md**:
- **Purpose**: Enterprise production scenarios
- **Metrics**: Faithfulness, Answer Relevance, ROUGE
- **2026 SOTA**: Similar to CRAG (85-95%)

**newragcity Status**: ⚠️ **Can Add (4-6 hours)**
- **Similar to CRAG** but enterprise-focused
- **Would test**: Multi-approach routing with confidence gating
- **Integration**: Add to `run_benchmarks.py` BENCHMARKS dict

**Implementation Plan**:
1. Download RAGBench dataset
2. Add configuration to `run_benchmarks.py`
3. Implement enterprise-specific metrics (cost, latency, accuracy)

**Why Add This**:
- Enterprise deployment validation
- Cost/latency trade-off analysis
- Complements CRAG with production scenarios

---

### ❌ Category 3: DIFFICULT OR NOT APPLICABLE

#### 3.1 LiveRAG (Real-Time Web) - **NOT SUPPORTED**

**From benchmark_possible.md**:
- **Purpose**: Real-time web retrieval
- **Why Use**: Evaluates RAG with live, dynamic data sources

**newragcity Status**: ❌ **Not Supported**
- **Reason**: Current architecture is deterministic/semantic/compressed retrieval (static)
- **No web search integration** in current design
- **Estimated effort**: 40-80 hours (major feature)

**Why Skip**:
- Not core to newragcity's value proposition (compression, confidence, multi-approach)
- Would require significant architecture changes
- Live web search is orthogonal to static document RAG

---

#### 3.2 MedQA/PubMedQA/BioASQ (Medical Domain) - **PARTIALLY RELEVANT**

**From benchmark_possible.md**:
- **Purpose**: Domain-specific medical benchmarks
- **Metrics**: Domain Accuracy, ROUGE/BLEU
- **2026 SOTA**: 80-90% accuracy (MedBioRAG)

**newragcity Status**: ⚠️ **Partially Relevant**
- **DKR has medical knowledge packs**: ABX, infections, pneumonia, sepsis, etc.
- **Could test** medical benchmarks with existing DKR data
- **Estimated effort**: 8-16 hours

**Why Maybe Add**:
- DKR medical data already exists
- Could demonstrate domain-specific advantage
- Specialized SOTA claim (medical RAG with compression)

**Implementation Plan** (if pursuing):
1. Download MedQA/PubMedQA datasets
2. Integrate with DKR medical knowledge packs
3. Add medical-specific metrics (diagnosis accuracy, guideline adherence)
4. Compare to MedBioRAG SOTA (80-90%)

---

#### 3.3 FinanceBench / CodeRAG - **NOT APPLICABLE**

**From benchmark_possible.md**:
- **Purpose**: Finance or code domain benchmarks
- **2026 SOTA**: Domain-specific (varies)

**newragcity Status**: ❌ **Not Applicable**
- No finance or code-specific features
- Would require domain adaptation
- Not aligned with current use cases

---

#### 3.4 InfiniteBench - **MAY WORK**

**From benchmark_possible.md**:
- **Purpose**: Extremely long contexts (>100k tokens)
- **2026 SOTA**: Varies

**newragcity Status**: ⚠️ **May Work**
- **RoT compression** might handle this exceptionally well
- **LongBench** covers similar ground (less extreme)
- **Estimated effort**: 2-4 hours (download and test)

**Why Consider**:
- Potential differentiation (extreme compression advantage)
- Low effort to try
- Could demonstrate RoT's upper limits

---

## Summary Table

| Benchmark | Category | Ready? | Priority | Effort | SOTA Target | newragcity Advantage |
|-----------|----------|--------|----------|--------|-------------|----------------------|
| **BEIR** | Retrieval | ✅ Yes | HIGH | Download | 68-75% nDCG@10 | Compression + accuracy |
| **CRAG** | End-to-End | ✅ Yes | HIGH | Download | 85-95% faith | Multi-hop + compression |
| **LongBench** | Long-Context | ✅ Yes | MEDIUM | Download | 70-90% acc | Compression on long docs |
| **Efficiency** | RoT-Specific | ✅ Yes | HIGH | Train model | 3×/2×/70% | Core value prop |
| **MTEB** | Retrieval | ⚠️ Add | MEDIUM | 4-8 hrs | Embed SOTA | LEANN + PageIndex |
| **Golden Set** | Real-World | ✅ Partial | HIGH | Upload docs | 85-95% acc | Multi-approach routing |
| **RAGBench** | Enterprise | ⚠️ Add | MEDIUM | 4-6 hrs | 85-95% | Cost + confidence |
| **LiveRAG** | Web | ❌ No | LOW | 40-80 hrs | N/A | Not applicable |
| **MedQA** | Medical | ⚠️ Partial | LOW | 8-16 hrs | 80-90% | DKR medical packs |
| **FinanceBench** | Finance | ❌ No | LOW | N/A | N/A | Not applicable |
| **InfiniteBench** | Extreme Long | ⚠️ Maybe | LOW | 2-4 hrs | Varies | Extreme compression |

**Key**:
- ✅ Ready: Infrastructure exists, needs data/models only
- ⚠️ Can Add: Achievable with implementation effort
- ❌ No: Not supported or not applicable

---

## Recommended Testing Roadmap

### Phase 1: Quick Validation (1-2 days)

**Goal**: Validate infrastructure works end-to-end

**Tasks**:
1. **Install dependencies**:
   ```bash
   pip install beir datasets numpy scipy ragas deepeval
   ```

2. **Run BEIR quick test** (placeholder mode):
   ```bash
   cd servers/rot_reasoning/benchmarks
   python run_benchmarks.py --quick-test
   ```
   - Expected: Framework works, placeholder results
   - Validates: Statistical aggregation, result saving

3. **Generate custom golden set**:
   ```bash
   cd ../../..  # Back to root
   python TheVault/scripts/generate_eval.py --samples 10
   ```
   - Upload 1-2 test PDFs first
   - Expected: 10 Q/A pairs generated
   - Validates: Document ingestion, LLM generation

**Success Criteria**:
- ✅ Quick test completes without errors
- ✅ Results JSON saved with proper format
- ✅ Golden set generated from real documents

---

### Phase 2: Core Benchmarks (1-2 weeks)

**Goal**: Establish baseline SOTA comparison (after RoT training)

**Tasks**:
4. **Download BEIR datasets**:
   ```bash
   python -c "from beir import util; util.download_and_unzip('nfcorpus', 'datasets/beir')"
   python -c "from beir import util; util.download_and_unzip('scifact', 'datasets/beir')"
   python -c "from beir import util; util.download_and_unzip('fiqa', 'datasets/beir')"
   ```

5. **Train RoT model** (see MODEL_SETUP.md):
   - Stage 1: Text-to-image training
   - Stage 2: Visual compression training
   - Checkpoint: `checkpoints/stage2/checkpoint_step_16000/`

6. **Run full BEIR evaluation**:
   ```bash
   python run_benchmarks.py --benchmarks BEIR --baselines vanilla --runs 3
   ```
   - Expected: 3-6 hours runtime
   - Target: nDCG@10 ≥0.45 (90% of baseline)

7. **Download and run CRAG**:
   ```bash
   python -c "from datasets import load_dataset; load_dataset('crag', cache_dir='datasets/crag')"
   python run_benchmarks.py --benchmarks CRAG --baselines vanilla --runs 3
   ```
   - Target: Faithfulness ≥0.90

8. **Run efficiency benchmarks**:
   ```bash
   python run_benchmarks.py --benchmarks Efficiency --runs 3
   ```
   - Target: 3×/2×/70% (compression/speedup/cost)

**Success Criteria**:
- ✅ BEIR: nDCG@10 within 5-10% of vanilla
- ✅ CRAG: Faithfulness ≥0.85
- ✅ Efficiency: Compression ≥3.0×, Speedup ≥2.0×
- ✅ Statistical significance: p < 0.05 for key metrics

**SOTA Evaluation**:
- **Tier 1** (Production Ready): Achieved if accuracy ≥90%, compression ≥2×
- **Tier 2** (Competitive SOTA): Achieved if accuracy ≥95%, compression ≥3×, cost ≥70%
- **Tier 3** (Clear SOTA): Achieved if accuracy ≥100%, compression ≥3.5×, novel capability

---

### Phase 3: Extended Evaluation (2-4 weeks)

**Goal**: Comprehensive SOTA claim with additional benchmarks

**Tasks**:
9. **Run LongBench** (download first):
   ```bash
   python -c "from datasets import load_dataset; load_dataset('longbench', 'rag', cache_dir='datasets/longbench')"
   python run_benchmarks.py --benchmarks LongBench --runs 3
   ```
   - Target: Accuracy 75-85% (competitive with GraphRAG)

10. **Add MTEB** (if claiming retrieval SOTA):
    - Implement MTEB integration (4-8 hours)
    - Test IBM Granite embeddings
    - Compare to Cohere embed-v4 SOTA

11. **Custom golden set** (50-100 samples):
    ```bash
    python TheVault/scripts/generate_eval.py --samples 50
    python TheVault/scripts/run_eval.py
    ```
    - Upload domain-specific documents
    - Test multi-approach routing
    - Measure improvement vs. single-method RAG

12. **Optional: MedQA** (if medical focus):
    - Download MedQA dataset
    - Integrate with DKR medical packs
    - Compare to MedBioRAG (80-90%)

**Success Criteria**:
- ✅ LongBench: Accuracy competitive with GraphRAG
- ✅ MTEB: nDCG@10 ≥60-70% (if added)
- ✅ Golden Set: 85-95% accuracy on real docs
- ✅ Multi-approach: 10-20% improvement over single method

---

## SOTA Claim Strategy

### Scenario 1: Compression-Focused SOTA

**If Results**:
- Compression: 3.5-4.0×
- Speedup: 2.5-3.0×
- Cost reduction: 75%+
- Accuracy retention: ≥90%

**Claim**:
> "newragcity achieves state-of-the-art compression (3.5-4.0×) with ≥90% accuracy retention on BEIR and CRAG benchmarks, outperforming existing compressed RAG methods by 10-20% in efficiency while maintaining competitive accuracy."

**Tier**: **Tier 2-3 SOTA** (Competitive to Clear SOTA for compressed RAG)

---

### Scenario 2: Multi-Approach SOTA

**If Results**:
- BEIR: nDCG@10 ≥0.50 (≥100% of vanilla)
- CRAG: Faithfulness ≥0.92 (top 5%)
- Golden Set: 90%+ accuracy with multi-approach routing
- Compression: 3.0×+

**Claim**:
> "newragcity's multi-approach framework (DKR + Ersatz + RoT) achieves SOTA performance on CRAG (92% faithfulness) and real-world golden sets (90%+ accuracy) while providing 3× compression, demonstrating that intelligent routing outperforms single-method RAG across diverse query types."

**Tier**: **Tier 3 SOTA** (Novel capability: multi-approach routing)

---

### Scenario 3: Long-Context SOTA

**If Results**:
- LongBench: 85%+ accuracy
- Compression: 4.0×+ on long documents
- Speedup: 3.0×+ vs. GraphRAG

**Claim**:
> "newragcity sets new SOTA for long-context RAG with 85% accuracy on LongBench while achieving 4× compression and 3× speedup over GraphRAG, enabling efficient processing of >100k token documents."

**Tier**: **Tier 3 SOTA** (Clear SOTA for long-context compressed RAG)

---

## Evaluation Tools and Frameworks

### Already Integrated

**From benchmark_possible.md recommendations**:

1. **BEIR** (`pip install beir`)
   - Status: ✅ Configured in `run_benchmarks.py`
   - Usage: Standard retrieval evaluation

2. **Ragas** (`pip install ragas`)
   - Status: 📋 Not yet integrated
   - Purpose: Faithfulness, context relevance, answer similarity
   - Add to: CRAG and Golden Set evaluations

3. **DeepEval** (`pip install deepeval`)
   - Status: 📋 Not yet integrated
   - Purpose: End-to-end testing with custom metrics
   - Add to: Custom golden set evaluation

### Recommended Additions

4. **LangSmith / Arize Phoenix**
   - Purpose: Production monitoring (latency, cost, accuracy)
   - Add to: Docker deployment for live monitoring

5. **Maxim AI**
   - Purpose: Comprehensive RAG eval, A/B testing
   - Add to: Enterprise deployment (optional)

---

## Statistical Rigor

### Current Implementation

From `run_benchmarks.py`:
- **Multiple runs**: 3+ with different random seeds (default: [42, 123, 456])
- **Aggregation**: Mean ± standard deviation for all metrics
- **Output format**: JSON with per-run results

**Example**:
```json
{
  "ndcg@10": {
    "mean": 0.463,
    "std": 0.012,
    "runs": [0.455, 0.468, 0.466]
  }
}
```

### Recommended Additions

1. **T-tests** (p-value < 0.05):
   ```python
   from scipy.stats import ttest_ind
   p_value = ttest_ind(rot_scores, baseline_scores).pvalue
   ```

2. **Confidence intervals** (95% CI):
   ```python
   from scipy.stats import t
   ci_95 = t.interval(0.95, len(scores)-1, mean, std/sqrt(len(scores)))
   ```

3. **Effect size** (Cohen's d):
   ```python
   cohens_d = (mean_rot - mean_baseline) / pooled_std
   ```

**Why Add**:
- Required for publication (NeurIPS, ACL, etc.)
- Demonstrates statistical significance
- Industry standard for SOTA claims

---

## Next Immediate Actions

### Action 1: Validate Infrastructure (Today)
```bash
cd servers/rot_reasoning/benchmarks
python run_benchmarks.py --quick-test --verbose
```
**Expected output**: Results JSON with placeholder metrics

---

### Action 2: Download Core Datasets (This Week)
```bash
pip install beir datasets
python -c "from beir import util; util.download_and_unzip('nfcorpus', 'datasets/beir')"
python -c "from datasets import load_dataset; load_dataset('crag', cache_dir='datasets/crag')"
```

---

### Action 3: Train RoT Model (See MODEL_SETUP.md)
Required before real benchmark results.

---

### Action 4: Run Phase 2 Benchmarks (After Training)
```bash
python run_benchmarks.py --benchmarks BEIR,CRAG,Efficiency --baselines vanilla --runs 3
```

---

## Conclusion

**newragcity is well-positioned for SOTA evaluation**:

1. ✅ **Core infrastructure ready**: BEIR, CRAG, LongBench, Efficiency
2. ✅ **Novel capabilities**: Multi-approach routing, confidence gating, compression
3. ⚠️ **Needs completion**: RoT model training, dataset downloads
4. ✅ **Statistical rigor**: Multiple runs, mean ± std, extensible to t-tests

**SOTA Tier Prediction**:
- **Conservative**: Tier 1-2 (Production to Competitive)
- **Optimistic**: Tier 2-3 (Competitive to Clear SOTA)
- **Differentiator**: Multi-approach routing + compression (novel combination)

**Recommended Focus**:
1. BEIR + CRAG + Efficiency (core SOTA claim)
2. Custom Golden Set (real-world validation)
3. LongBench or MTEB (extended claim)

With successful execution, newragcity can claim **SOTA for compressed, multi-approach RAG with confidence gating** across 4-5 major benchmarks.

---

**Document Status**: ✅ Complete
**Last Updated**: January 25, 2026
**Next Review**: After Phase 1 validation (quick tests)
