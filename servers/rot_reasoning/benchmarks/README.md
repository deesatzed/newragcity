# RoT Reasoning Benchmarks

**Status**: Framework ready, implementation pending model training
**Version**: 1.0.0

---

## Quick Start

### Prerequisites

```bash
# Install benchmark dependencies
pip install ragas deepeval beir datasets numpy scipy
```

### Run Benchmarks

```bash
# Quick smoke test (recommended first)
python run_benchmarks.py --quick-test

# Full benchmark suite
python run_benchmarks.py --benchmarks all --baselines vanilla,graph

# Specific benchmarks
python run_benchmarks.py --benchmarks BEIR,CRAG --runs 5
```

---

## Directory Structure

```
benchmarks/
├── __init__.py                 # Package init
├── README.md                   # This file
├── run_benchmarks.py           # Main benchmark runner (implemented)
├── rot_evaluator.py            # RoT evaluation implementation (TODO)
├── baselines.py                # Baseline RAG implementations (TODO)
├── metrics.py                  # Custom metric implementations (TODO)
├── datasets/                   # Downloaded benchmark datasets
│   ├── beir/
│   ├── crag/
│   └── ...
└── results/                    # Benchmark results (generated)
    └── benchmark_results_*.json
```

---

## Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| `run_benchmarks.py` | ✅ Complete | Main orchestration script |
| `rot_evaluator.py` | ⏳ Template | Needs RoT model integration |
| `baselines.py` | ⏳ Template | Vanilla RAG, GraphRAG implementations |
| `metrics.py` | ⏳ Template | Compression, speedup, cost metrics |
| Dataset loaders | 📋 Pending | BEIR, CRAG integration |

---

## Next Steps (After Model Training)

### 1. Implement RoT Evaluator

Edit `rot_evaluator.py`:

```python
class RoTEvaluator:
    def __init__(self):
        # Load trained RoT model
        from model_manager import RoTModelManager
        self.model_manager = RoTModelManager(
            checkpoint_path="checkpoints/stage2/checkpoint_step_16000",
            stage1_checkpoint="checkpoints/stage1/checkpoint_epoch_2",
            # ... other params
        )

    def evaluate(self, datasets, metrics, seed, sample_size=None):
        # Run evaluation on datasets
        # Return dict of metric scores
        pass
```

### 2. Implement Baselines

Edit `baselines.py`:

```python
class VanillaRAG:
    def evaluate(self, datasets, metrics, seed, sample_size=None):
        # Standard RAG without compression
        pass

class GraphRAG:
    def evaluate(self, datasets, metrics, seed, sample_size=None):
        # Graph-based RAG
        pass
```

### 3. Download Benchmark Datasets

```bash
# BEIR datasets
python -c "from beir import util; util.download_and_unzip('nfcorpus', 'datasets/beir')"

# CRAG dataset (from Hugging Face)
python -c "from datasets import load_dataset; load_dataset('crag', cache_dir='datasets/crag')"
```

### 4. Run Initial Tests

```bash
# Smoke test
python run_benchmarks.py --quick-test --verbose

# If passing, run full suite
python run_benchmarks.py --benchmarks all --runs 3
```

---

## Benchmark Descriptions

### BEIR (Retrieval)

**Purpose**: Standard retrieval quality benchmark
**Datasets**: 18 diverse tasks (nfcorpus, scifact, fiqa, etc.)
**Metrics**: nDCG@10, Recall@100, MRR
**SOTA**: ~68-75% nDCG@10 average

**Expected RoT Performance**:
- ≥90% of vanilla RAG accuracy
- Maintained retrieval precision despite compression

### CRAG (End-to-End RAG)

**Purpose**: Challenging multi-hop and unanswerable queries
**Datasets**: CRAG multi-hop QA
**Metrics**: Faithfulness, Accuracy, F1
**SOTA**: 85-95% faithfulness

**Expected RoT Performance**:
- Faithfulness ≥0.90
- Accuracy within 5% of vanilla RAG
- Better performance on complex multi-hop queries

### Efficiency (RoT-Specific)

**Purpose**: Measure compression and speed gains
**Metrics**:
- Compression ratio (tokens_original / tokens_compressed)
- Speedup (time_baseline / time_rot)
- Cost reduction (%)

**Expected RoT Performance**:
- Compression: ≥3.0×
- Speedup: ≥2.0×
- Cost reduction: ≥70%

### LongBench (Long-Context)

**Purpose**: Evaluate on long documents
**Datasets**: LongBench RAG tasks
**Metrics**: Recall@K, Accuracy
**SOTA**: 70-90%

**Expected RoT Performance**:
- Maintained accuracy on long contexts
- Potentially better due to compression efficiency

---

## Metrics Explained

### Accuracy Metrics

**nDCG@10** (Normalized Discounted Cumulative Gain):
- Measures ranking quality of retrieved documents
- Range: 0-1 (higher is better)
- Industry standard for retrieval

**Faithfulness**:
- How well the answer is grounded in retrieved context
- Computed via LLM-as-judge or NLI models
- Range: 0-1 (higher is better)

**Answer Relevance**:
- How directly the answer addresses the query
- Semantic similarity based
- Range: 0-1 (higher is better)

### Efficiency Metrics

**Compression Ratio**:
```python
compression_ratio = original_tokens / compressed_tokens
# Target: ≥3.0×
```

**Speedup**:
```python
speedup = baseline_latency_ms / rot_latency_ms
# Target: ≥2.0×
```

**Cost Reduction**:
```python
cost_reduction = (baseline_cost - rot_cost) / baseline_cost * 100
# Target: ≥70%
```

---

## Statistical Significance

All benchmark runs include:
- **Multiple runs**: 3+ with different random seeds
- **Mean ± std dev**: For all metrics
- **T-tests**: p-value < 0.05 for significance
- **Confidence intervals**: 95% CI reported

Example output:
```
RoT vs Vanilla on CRAG:
- Faithfulness: 0.92 ± 0.02 vs 0.90 ± 0.03 (p=0.04) ✓ Significant
- Compression: 3.4× ± 0.3× vs 1.0× (p<0.001) ✓ Highly significant
```

---

## Results Format

Benchmark results are saved as JSON:

```json
{
  "metadata": {
    "timestamp": "2026-01-24T10:30:00",
    "benchmark_names": ["BEIR", "CRAG"],
    "runs_per_experiment": 3
  },
  "benchmarks": {
    "BEIR": {
      "RoT": {
        "ndcg@10": {
          "mean": 0.463,
          "std": 0.012,
          "runs": [0.455, 0.468, 0.466]
        },
        "compression_ratio": {
          "mean": 3.4,
          "std": 0.3
        }
      },
      "vanilla": {
        "ndcg@10": {
          "mean": 0.457,
          "std": 0.015
        }
      }
    }
  }
}
```

---

## SOTA Criteria

### Tier 1: Production Ready
- Accuracy retention: ≥90% of baseline
- Compression: ≥2.0×
- Speedup: ≥1.5×

### Tier 2: Competitive (Strong SOTA Candidate)
- Accuracy retention: ≥95% of baseline
- Compression: ≥3.0×
- Speedup: ≥2.0×
- Cost reduction: ≥70%

### Tier 3: State-of-the-Art
- Accuracy improvement: ≥100% (equal or better)
- Compression: ≥3.5×
- Speedup: ≥2.5×
- Novel capability: New SOTA on ≥1 benchmark

---

## Troubleshooting

### Issue: Import errors

```bash
# Install missing dependencies
pip install ragas deepeval beir datasets numpy scipy

# Check imports
python -c "import ragas; import deepeval; import beir; print('OK')"
```

### Issue: Dataset download fails

```bash
# Manual download for BEIR
git clone https://github.com/beir-cellar/beir.git
cd beir
python -m beir.datasets.download nfcorpus

# For CRAG, use Hugging Face Hub
huggingface-cli download crag --repo-type dataset
```

### Issue: Benchmark runs but no RoT results

```bash
# Check if RoT model is trained
ls -la ../checkpoints/stage2/checkpoint_step_16000/

# If not trained, see MODEL_SETUP.md and ROT_INTEGRATION_TECHNICAL_PLAN.md
```

---

## Contributing

To add new benchmarks:

1. Add to `BENCHMARKS` dict in `run_benchmarks.py`
2. Implement dataset loader
3. Define metrics
4. Update this README

Example:
```python
BENCHMARKS['NewBench'] = {
    'datasets': ['dataset1', 'dataset2'],
    'metrics': ['custom_metric1', 'custom_metric2'],
    'description': 'New benchmark for X',
}
```

---

## References

- BEIR: https://github.com/beir-cellar/beir
- Ragas: https://docs.ragas.io/
- DeepEval: https://docs.confident-ai.com/
- CRAG: https://www.aicrowd.com/challenges/meta-comprehensive-rag-benchmark

---

**Last Updated**: January 24, 2026
**Status**: Framework complete, awaiting model training
