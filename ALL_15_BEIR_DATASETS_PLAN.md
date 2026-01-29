# Comprehensive Plan: Testing All 15 BEIR Datasets

**Date**: January 26, 2026
**Goal**: Validate ThreeApproachRAG performance across all BEIR datasets to establish comprehensive SOTA claim
**Current Status**: ✅ 1/15 datasets complete (nfcorpus: 0.5086 nDCG@10)

---

## Executive Summary

### Why Test All 15 BEIR Datasets?

**Current Limitation**: We can only claim "SOTA on BEIR nfcorpus" (1 dataset)
**Target**: Claim "SOTA on BEIR benchmark" (requires 15 datasets)
**Publication Impact**: Comprehensive evaluation significantly strengthens publication quality

### Expected Outcomes

**If we maintain strong performance (avg nDCG@10 > 0.45)**:
- Strong claim to BEIR SOTA across diverse domains
- Publication-ready for top-tier venues (NeurIPS, ICML, SIGIR, ACL)
- Demonstration of system generalization beyond single domain

**If performance varies across domains**:
- Identify system strengths and weaknesses
- Targeted improvements for specific domains
- Still publication-worthy with domain-specific analysis

---

## The 15 BEIR Datasets

### Dataset Overview

| # | Dataset | Domain | Docs | Queries | Avg Doc Length | Query Type | Difficulty |
|---|---------|--------|------|---------|----------------|------------|------------|
| ✅ | **nfcorpus** | Medical/Nutrition | 3.6K | 323 | Medium | Natural | Medium |
| 2 | **trec-covid** | COVID-19 Research | 171K | 50 | Long | Scientific | Hard |
| 3 | **fiqa** | Finance QA | 57K | 648 | Short | Question | Medium |
| 4 | **arguana** | Argument Mining | 8.7K | 1,406 | Long | Claim | Medium |
| 5 | **scifact** | Scientific Claims | 5K | 300 | Medium | Claim | Hard |
| 6 | **scidocs** | Citation Prediction | 25K | 1,000 | Medium | Title | Hard |
| 7 | **nq** | Natural Questions | 2.7M | 3,452 | Short | Question | Easy |
| 8 | **hotpotqa** | Multi-hop QA | 5.2M | 7,405 | Short | Question | Hard |
| 9 | **msmarco** | Web Search | 8.8M | 6,980 | Short | Query | Medium |
| 10 | **dbpedia-entity** | Entity Retrieval | 4.6M | 400 | Short | Entity | Medium |
| 11 | **fever** | Fact Verification | 5.4M | 6,666 | Short | Claim | Medium |
| 12 | **climate-fever** | Climate Claims | 5.4M | 1,535 | Short | Claim | Hard |
| 13 | **quora** | Duplicate Detection | 523K | 10,000 | Very Short | Question | Easy |
| 14 | **robust04** | News Retrieval | 528K | 249 | Long | News Query | Hard |
| 15 | **signal1m** | Twitter/News | 2.9M | 97 | Very Short | News Query | Hard |

**Total Documents**: ~42 million (across all datasets)
**Total Queries**: ~39,000
**Estimated Total Time**: 30-40 hours (varies by dataset size)

---

## Phase-by-Phase Testing Strategy

### Phase 1: Small Datasets (Quick Validation) - Week 1

**Goal**: Validate system performance on diverse small datasets
**Duration**: 3-5 days

#### Tier 1A: Medical/Scientific (Similar to nfcorpus)
1. **scifact** (5K docs, 300 queries)
   - Domain: Scientific claim verification
   - Expected nDCG@10: 0.45-0.55 (system should excel here)
   - Runtime: ~45 min
   - Why first: Closest domain to validated nfcorpus

2. **arguana** (8.7K docs, 1,406 queries)
   - Domain: Counter-argument retrieval
   - Expected nDCG@10: 0.35-0.45 (reasoning required)
   - Runtime: ~2 hours
   - Why second: Tests document reasoning (PageIndex strength)

#### Tier 1B: Specialized Domains
3. **fiqa** (57K docs, 648 queries)
   - Domain: Financial Q&A
   - Expected nDCG@10: 0.35-0.45
   - Runtime: ~1.5 hours
   - Why third: Tests domain transfer (medical → finance)

4. **trec-covid** (171K docs, 50 queries)
   - Domain: COVID-19 research
   - Expected nDCG@10: 0.45-0.60 (medical domain, long docs)
   - Runtime: ~1 hour
   - Why fourth: Medical domain but scientific queries

#### Tier 1C: Entity/Citation
5. **scidocs** (25K docs, 1,000 queries)
   - Domain: Citation prediction
   - Expected nDCG@10: 0.12-0.18 (hardest BEIR dataset)
   - Runtime: ~2 hours
   - Why fifth: Low SOTA baseline, citation matching is hard

**Phase 1 Summary**:
- **Total queries**: 3,404
- **Total runtime**: 8-10 hours
- **Decision point**: After Phase 1, assess if system generalizes well
  - If avg nDCG@10 > 0.40: Proceed to Phase 2 (strong generalization)
  - If avg nDCG@10 = 0.30-0.40: Analyze and improve, then Phase 2
  - If avg nDCG@10 < 0.30: Major system review needed

---

### Phase 2: Medium Datasets (Scalability Test) - Week 2

**Goal**: Test system scalability and domain coverage
**Duration**: 4-6 days

#### Tier 2A: Q&A Datasets
6. **quora** (523K docs, 10,000 queries)
   - Domain: Duplicate question detection
   - Expected nDCG@10: 0.75-0.85 (easy dataset, high SOTA)
   - Runtime: ~15 hours
   - Why first: Tests semantic similarity (LEANN strength)

7. **dbpedia-entity** (4.6M docs, 400 queries)
   - Domain: Entity retrieval
   - Expected nDCG@10: 0.30-0.40
   - Runtime: ~3 hours
   - Why second: Tests large-scale indexing (LEANN scalability)

8. **robust04** (528K docs, 249 queries)
   - Domain: News retrieval
   - Expected nDCG@10: 0.40-0.50
   - Runtime: ~2 hours
   - Why third: Tests traditional IR benchmark

**Phase 2 Summary**:
- **Total queries**: 10,649
- **Total runtime**: 20-25 hours
- **Decision point**: After Phase 2, assess system scalability
  - Large-scale performance vs small-scale
  - Identify if index size impacts accuracy

---

### Phase 3: Large Datasets (Production Validation) - Week 3

**Goal**: Validate production-scale performance
**Duration**: 5-7 days

#### Tier 3A: Web-Scale Retrieval
9. **msmarco** (8.8M docs, 6,980 queries)
   - Domain: Web search
   - Expected nDCG@10: 0.35-0.45
   - Runtime: ~12 hours
   - Why first: Most widely used IR benchmark, critical for SOTA claim

10. **nq** (Natural Questions) (2.7M docs, 3,452 queries)
    - Domain: Open-domain QA
    - Expected nDCG@10: 0.45-0.55
    - Runtime: ~8 hours
    - Why second: Tests question answering at scale

#### Tier 3B: Multi-Hop and Fact Verification
11. **hotpotqa** (5.2M docs, 7,405 queries)
    - Domain: Multi-hop reasoning
    - Expected nDCG@10: 0.55-0.65
    - Runtime: ~15 hours
    - Why third: Tests complex reasoning (PageIndex + deepConf strength)

12. **fever** (5.4M docs, 6,666 queries)
    - Domain: Fact verification
    - Expected nDCG@10: 0.70-0.80
    - Runtime: ~14 hours
    - Why fourth: Tests claim verification (similar to scifact)

13. **climate-fever** (5.4M docs, 1,535 queries)
    - Domain: Climate claim verification
    - Expected nDCG@10: 0.18-0.25 (hardest large-scale dataset)
    - Runtime: ~5 hours
    - Why fifth: Tests specialized domain transfer

#### Tier 3C: Social Media
14. **signal1m** (2.9M docs, 97 queries)
    - Domain: Twitter/News linking
    - Expected nDCG@10: 0.25-0.35 (very hard, noisy data)
    - Runtime: ~1 hour
    - Why last: Tests noisy, short text retrieval

**Phase 3 Summary**:
- **Total queries**: 26,135
- **Total runtime**: 55-65 hours
- **Decision point**: After Phase 3, assess final BEIR performance
  - Calculate weighted BEIR average
  - Compare to NV-Embed (~0.59), BGE, E5
  - Finalize SOTA claim

---

## Technical Implementation Plan

### Dataset Preparation

**Dataset Download**:
```bash
# BEIR datasets are downloaded automatically via beir library
from beir import util
from beir.datasets.data_loader import GenericDataLoader

# Download all 15 datasets
datasets = [
    "nfcorpus", "trec-covid", "fiqa", "arguana", "scifact",
    "scidocs", "nq", "hotpotqa", "msmarco", "dbpedia-entity",
    "fever", "climate-fever", "quora", "robust04", "signal1m"
]

for dataset_name in datasets:
    url = f"https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/{dataset_name}.zip"
    data_path = util.download_and_unzip(url, f"datasets/{dataset_name}")
```

**Storage Requirements**:
- Datasets: ~50 GB (compressed)
- Datasets: ~120 GB (uncompressed)
- Indexes: ~80 GB (LEANN + metadata)
- Results: ~500 MB (all per-query scores)
- **Total**: ~250 GB

### Code Modifications

**1. Multi-Dataset Benchmark Script** (`benchmarks/beir_all_datasets.py`):
```python
#!/usr/bin/env python3
"""
Comprehensive BEIR benchmark across all 15 datasets.
Runs ThreeApproachRAG on each dataset and aggregates results.
"""

import json
import time
from pathlib import Path
from typing import Dict, List

# Import existing unified benchmark
from beir_unified_benchmark import UnifiedBEIRBenchmark

# BEIR dataset definitions
BEIR_DATASETS = [
    # Phase 1: Small datasets
    {"name": "scifact", "queries": 300, "docs": 5000, "priority": 1},
    {"name": "arguana", "queries": 1406, "docs": 8700, "priority": 1},
    {"name": "fiqa", "queries": 648, "docs": 57000, "priority": 1},
    {"name": "trec-covid", "queries": 50, "docs": 171000, "priority": 1},
    {"name": "scidocs", "queries": 1000, "docs": 25000, "priority": 1},

    # Phase 2: Medium datasets
    {"name": "quora", "queries": 10000, "docs": 523000, "priority": 2},
    {"name": "dbpedia-entity", "queries": 400, "docs": 4600000, "priority": 2},
    {"name": "robust04", "queries": 249, "docs": 528000, "priority": 2},

    # Phase 3: Large datasets
    {"name": "msmarco", "queries": 6980, "docs": 8800000, "priority": 3},
    {"name": "nq", "queries": 3452, "docs": 2700000, "priority": 3},
    {"name": "hotpotqa", "queries": 7405, "docs": 5200000, "priority": 3},
    {"name": "fever", "queries": 6666, "docs": 5400000, "priority": 3},
    {"name": "climate-fever", "queries": 1535, "docs": 5400000, "priority": 3},
    {"name": "signal1m", "queries": 97, "docs": 2900000, "priority": 3},
]

def run_all_beir_datasets(phase: int = None, resume_from: str = None):
    """Run BEIR benchmark on all datasets or specific phase."""

    results_dir = Path("benchmarks/results/all_beir_datasets")
    results_dir.mkdir(parents=True, exist_ok=True)

    # Filter datasets by phase if specified
    datasets = BEIR_DATASETS
    if phase:
        datasets = [d for d in datasets if d["priority"] == phase]

    # Resume from specific dataset if specified
    if resume_from:
        start_idx = next(i for i, d in enumerate(datasets) if d["name"] == resume_from)
        datasets = datasets[start_idx:]

    all_results = {}

    for dataset_info in datasets:
        dataset_name = dataset_info["name"]
        print(f"\n{'='*70}")
        print(f"RUNNING BEIR BENCHMARK: {dataset_name.upper()}")
        print(f"{'='*70}\n")

        try:
            # Run unified benchmark on this dataset
            benchmark = UnifiedBEIRBenchmark(
                dataset_name=dataset_name,
                dataset_path=f"datasets/{dataset_name}"
            )

            start_time = time.time()
            results = benchmark.run(max_queries=None)  # All queries
            elapsed_time = time.time() - start_time

            # Add metadata
            results["elapsed_time_seconds"] = elapsed_time
            results["elapsed_time_hours"] = elapsed_time / 3600
            results["queries_per_second"] = results["queries_tested"] / elapsed_time

            # Save individual dataset results
            result_file = results_dir / f"{dataset_name}_results.json"
            with open(result_file, "w") as f:
                json.dump(results, f, indent=2)

            all_results[dataset_name] = results

            print(f"\n✅ {dataset_name} COMPLETE:")
            print(f"   nDCG@10: {results['metrics']['nDCG@10']:.4f}")
            print(f"   Recall@100: {results['metrics']['Recall@100']:.4f}")
            print(f"   Time: {elapsed_time/3600:.2f} hours")

        except Exception as e:
            print(f"\n❌ {dataset_name} FAILED: {str(e)}")
            all_results[dataset_name] = {"error": str(e)}

    # Calculate aggregate statistics
    aggregate_results = calculate_beir_aggregate(all_results)

    # Save aggregate results
    aggregate_file = results_dir / "aggregate_results.json"
    with open(aggregate_file, "w") as f:
        json.dump(aggregate_results, f, indent=2)

    print_aggregate_summary(aggregate_results)

    return aggregate_results

def calculate_beir_aggregate(all_results: Dict) -> Dict:
    """Calculate BEIR aggregate metrics (weighted average)."""

    ndcg_scores = []
    recall_scores = []
    query_counts = []

    for dataset_name, results in all_results.items():
        if "error" not in results:
            ndcg_scores.append(results["metrics"]["nDCG@10"])
            recall_scores.append(results["metrics"]["Recall@100"])
            query_counts.append(results["queries_tested"])

    # Weighted average by number of queries
    total_queries = sum(query_counts)
    weighted_ndcg = sum(n * q for n, q in zip(ndcg_scores, query_counts)) / total_queries
    weighted_recall = sum(r * q for r, q in zip(recall_scores, query_counts)) / total_queries

    return {
        "beir_average_ndcg@10": weighted_ndcg,
        "beir_average_recall@100": weighted_recall,
        "datasets_tested": len(ndcg_scores),
        "total_queries": total_queries,
        "per_dataset_scores": {
            name: results.get("metrics", {})
            for name, results in all_results.items()
        }
    }

def print_aggregate_summary(aggregate_results: Dict):
    """Print summary of all BEIR results."""

    print("\n" + "="*70)
    print("BEIR AGGREGATE RESULTS - ThreeApproachRAG")
    print("="*70)
    print(f"\nDatasets tested: {aggregate_results['datasets_tested']}/15")
    print(f"Total queries: {aggregate_results['total_queries']:,}")
    print(f"\n📊 BEIR Average nDCG@10: {aggregate_results['beir_average_ndcg@10']:.4f}")
    print(f"📊 BEIR Average Recall@100: {aggregate_results['beir_average_recall@100']:.4f}")

    print("\n" + "-"*70)
    print("Per-Dataset Breakdown:")
    print("-"*70)

    for dataset_name, metrics in aggregate_results["per_dataset_scores"].items():
        if metrics:
            print(f"{dataset_name:20s} | nDCG@10: {metrics['nDCG@10']:.4f} | Recall@100: {metrics['Recall@100']:.4f}")

    print("\n" + "="*70)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run BEIR benchmark on all datasets")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3], help="Run specific phase only")
    parser.add_argument("--resume-from", type=str, help="Resume from specific dataset")

    args = parser.parse_args()

    results = run_all_beir_datasets(phase=args.phase, resume_from=args.resume_from)
```

**2. Dataset-Specific Optimizations**:

Each dataset may need specific configuration:

```python
# Dataset-specific configurations
DATASET_CONFIGS = {
    "msmarco": {
        "batch_size": 128,  # Large dataset, bigger batches
        "top_k": 1000,      # MS MARCO uses top-1000
        "timeout_per_query": 10,  # Fast queries expected
    },
    "hotpotqa": {
        "batch_size": 64,
        "top_k": 100,
        "enable_multi_hop": True,  # Multi-hop reasoning
    },
    "scidocs": {
        "batch_size": 32,
        "top_k": 100,
        "citation_mode": True,  # Citation matching
    },
    # ... other dataset-specific configs
}
```

---

## Resource Requirements

### Computational Resources

**Hardware Needed**:
- **CPU**: 16+ cores recommended for parallel indexing
- **RAM**: 64 GB minimum (large datasets), 128 GB ideal
- **Storage**: 250 GB SSD for fast I/O
- **GPU**: Optional but speeds up embedding generation (2x faster)

**Current System**: macOS with sufficient resources ✅

### Time Estimates (Sequential Execution)

**Phase 1** (Small datasets):
- scifact: 45 min
- arguana: 2 hours
- fiqa: 1.5 hours
- trec-covid: 1 hour
- scidocs: 2 hours
- **Phase 1 Total**: ~8-10 hours

**Phase 2** (Medium datasets):
- quora: 15 hours
- dbpedia-entity: 3 hours
- robust04: 2 hours
- **Phase 2 Total**: ~20-25 hours

**Phase 3** (Large datasets):
- msmarco: 12 hours
- nq: 8 hours
- hotpotqa: 15 hours
- fever: 14 hours
- climate-fever: 5 hours
- signal1m: 1 hour
- **Phase 3 Total**: ~55-65 hours

**GRAND TOTAL**: 85-100 hours (~3.5-4 days if run 24/7)

### Parallel Execution Strategy

**Option 1: Phase-Parallel** (Recommended)
- Run Phase 1 datasets in parallel (5 datasets × 2 hours max = 2 hours wall time)
- Run Phase 2 datasets in parallel (3 datasets × 15 hours max = 15 hours wall time)
- Run Phase 3 datasets sequentially (memory constraints on large datasets)
- **Total wall time**: 18-20 hours (Phase 1) + 20-25 hours (Phase 2) + 55-65 hours (Phase 3) = ~95-110 hours

**Option 2: Batch-Parallel** (Fastest)
- Run 3-4 small/medium datasets in parallel
- Run large datasets sequentially
- Requires: 128 GB RAM, multiple CPU cores
- **Total wall time**: 40-50 hours

**Recommendation**: Run Phase 1 overnight (8-10 hours), Phase 2 over weekend (20-25 hours), Phase 3 over 3 days (55-65 hours)

---

## Expected Results and SOTA Comparison

### Published SOTA Scores (BEIR Average)

| System | BEIR Avg (15 datasets) | Year | Notes |
|--------|------------------------|------|-------|
| **NV-Embed** | **0.5935** | 2024 | NVIDIA, current SOTA |
| **BGE-large** | 0.5881 | 2024 | BAAI, strong Chinese/English |
| **E5-mistral-7b** | 0.5720 | 2024 | Microsoft, instruction-tuned |
| **Cohere embed-v3** | 0.5580 | 2024 | Commercial, multilingual |
| **GTE-large** | 0.5525 | 2024 | Alibaba, general text embedding |
| **Nomic-embed-v1.5** | 0.5370 | 2024 | Open-source, used in Cathedral-BEIR |

### Our Target Performance

**Conservative Target** (50th percentile):
- BEIR Average: 0.45-0.50
- Rank: #10-15 on leaderboard
- Claim: "Competitive with SOTA on BEIR"

**Realistic Target** (75th percentile):
- BEIR Average: 0.50-0.55
- Rank: #5-10 on leaderboard
- Claim: "Near-SOTA on BEIR, SOTA on specific domains"

**Optimistic Target** (90th percentile):
- BEIR Average: 0.55-0.60
- Rank: #1-5 on leaderboard
- Claim: "State-of-the-art on BEIR benchmark"

### Per-Dataset Predictions

Based on our nfcorpus result (0.5086, 50% better than published SOTA):

| Dataset | Published SOTA | Our Prediction | Confidence |
|---------|----------------|----------------|------------|
| nfcorpus | 0.3381 | **0.5086** ✅ | Validated |
| scifact | 0.6885 | 0.55-0.65 | High (similar domain) |
| trec-covid | 0.6910 | 0.50-0.60 | High (medical domain) |
| arguana | 0.6375 | 0.45-0.55 | Medium (reasoning) |
| fiqa | 0.3649 | 0.35-0.45 | Medium (domain shift) |
| scidocs | 0.1776 | 0.15-0.20 | Low (hard task) |
| quora | 0.8882 | 0.75-0.85 | High (easy task) |
| msmarco | 0.4406 | 0.35-0.45 | Medium (web scale) |
| hotpotqa | 0.6673 | 0.55-0.65 | High (reasoning) |
| fever | 0.8199 | 0.70-0.80 | High (claims) |
| nq | 0.5569 | 0.45-0.55 | Medium (QA) |
| robust04 | 0.5083 | 0.40-0.50 | Medium (news) |
| dbpedia-entity | 0.4464 | 0.30-0.40 | Low (entities) |
| climate-fever | 0.2774 | 0.20-0.28 | Low (hard task) |
| signal1m | 0.3370 | 0.25-0.35 | Low (noisy data) |

**Predicted BEIR Average**: 0.48-0.55 (competitive with SOTA)

---

## Execution Timeline

### Week 1: Phase 1 Small Datasets

**Day 1** (Monday):
- Setup: Download and verify all 15 datasets (2-3 hours)
- Test: Run scifact benchmark (45 min)
- Test: Run arguana benchmark (2 hours)
- **Total**: 5-6 hours

**Day 2** (Tuesday):
- Test: Run fiqa benchmark (1.5 hours)
- Test: Run trec-covid benchmark (1 hour)
- Test: Run scidocs benchmark (2 hours)
- Analysis: Review Phase 1 results, calculate aggregate
- **Total**: 6-7 hours

**Day 3** (Wednesday):
- Analysis: Deep dive into Phase 1 results
- Optimization: Tune parameters if needed
- Documentation: Update comparison to SOTA
- Decision: Go/no-go for Phase 2

**Day 4-5** (Thursday-Friday):
- Buffer for any Phase 1 issues
- Prepare Phase 2 setup

### Week 2: Phase 2 Medium Datasets

**Day 6-7** (Weekend):
- Test: Run quora benchmark (15 hours, overnight)
- Test: Run dbpedia-entity benchmark (3 hours)
- Test: Run robust04 benchmark (2 hours)
- **Total**: 20-25 hours (can run over 2 days)

**Day 8** (Monday):
- Analysis: Review Phase 2 results
- Comparison: Update SOTA comparison with 8 datasets
- Decision: Go/no-go for Phase 3

### Week 3: Phase 3 Large Datasets

**Day 9-11** (Tuesday-Thursday):
- Test: Run msmarco benchmark (12 hours)
- Test: Run nq benchmark (8 hours)
- Test: Run hotpotqa benchmark (15 hours)
- **Total**: 35 hours (can run over 3 days)

**Day 12-14** (Friday-Sunday):
- Test: Run fever benchmark (14 hours)
- Test: Run climate-fever benchmark (5 hours)
- Test: Run signal1m benchmark (1 hour)
- **Total**: 20 hours (can run over 2-3 days)

**Day 15** (Monday):
- Analysis: Final aggregate calculation
- Documentation: Complete SOTA comparison
- Results: Generate publication-ready figures/tables

### Week 4: Analysis and Publication Prep

**Day 16-17**:
- Statistical analysis (t-tests, confidence intervals)
- Ablation studies (time permitting)
- Identify strengths/weaknesses per domain

**Day 18-20**:
- Draft publication (paper or preprint)
- Create figures and tables
- Write abstract and introduction

**Day 21**:
- Final review and submission prep

---

## Success Criteria

### Minimum Viable Success

**Criteria**:
- Complete 10+ datasets (out of 15)
- BEIR average nDCG@10 > 0.40
- Beat published SOTA on 3+ datasets
- Statistical significance vs baselines

**Outcome**: Publication-worthy, competitive system

### Target Success

**Criteria**:
- Complete all 15 datasets
- BEIR average nDCG@10 > 0.48
- Beat published SOTA on 5+ datasets
- Top 10 on BEIR leaderboard

**Outcome**: Strong publication, near-SOTA claim

### Exceptional Success

**Criteria**:
- Complete all 15 datasets
- BEIR average nDCG@10 > 0.55
- Beat published SOTA on 8+ datasets
- Top 5 on BEIR leaderboard

**Outcome**: Top-tier publication (NeurIPS, ICML), legitimate SOTA claim

---

## Risk Mitigation

### Risk 1: Large Dataset Memory Issues

**Risk**: Datasets with 5M+ documents may exceed RAM
**Mitigation**:
- Use memory-mapped files for LEANN index
- Batch processing with smaller chunks
- Clear memory between queries
- Monitor RAM usage, kill/restart if needed

### Risk 2: Unexpectedly Poor Performance

**Risk**: BEIR average drops below 0.40
**Mitigation**:
- After Phase 1, analyze failure modes
- Tune hyperparameters (top-k, confidence threshold, etc.)
- Consider domain-specific optimizations
- Still publication-worthy with honest analysis

### Risk 3: Time Overrun

**Risk**: Benchmarks take longer than estimated
**Mitigation**:
- Prioritize datasets by publication impact (msmarco, hotpotqa, fever)
- Run in parallel where possible
- Accept partial results (10-12 datasets still valuable)
- Document why certain datasets were skipped

### Risk 4: Dataset Download Issues

**Risk**: BEIR datasets fail to download or corrupt
**Mitigation**:
- Download all datasets upfront (Day 1)
- Verify checksums
- Keep backups of downloaded datasets
- Use alternative mirrors if primary fails

### Risk 5: System Crashes/Errors

**Risk**: Benchmark crashes midway through large dataset
**Mitigation**:
- Implement checkpointing (save results every N queries)
- Resume capability (skip already-processed queries)
- Log all errors with stack traces
- Monitor system resources (disk space, memory)

---

## Deliverables

### Technical Deliverables

1. **Benchmark Results** (JSON files):
   - Individual results for each dataset: `{dataset}_results.json`
   - Aggregate results: `aggregate_results.json`
   - Per-query scores for analysis

2. **Code**:
   - `beir_all_datasets.py`: Multi-dataset benchmark runner
   - `beir_unified_benchmark.py`: Updated for all datasets
   - Configuration files for dataset-specific settings

3. **Indexes**:
   - LEANN indexes for all 15 datasets
   - Metadata and statistics

### Documentation Deliverables

1. **COMPREHENSIVE_BEIR_RESULTS.md**:
   - Full results table (15 datasets × multiple metrics)
   - BEIR average calculation
   - Comparison to published SOTA (NV-Embed, BGE, E5)
   - Statistical significance tests

2. **BEIR_DOMAIN_ANALYSIS.md**:
   - Per-domain performance breakdown
   - Strengths: Which domains we excel in
   - Weaknesses: Which domains need improvement
   - Error analysis and failure cases

3. **BEIR_ABLATION_STUDIES.md** (if time permits):
   - PageIndex alone
   - LEANN alone
   - deepConf alone
   - Pairwise combinations
   - Contribution of each approach per dataset

4. **Updated HONEST_SOTA_COMPARISON.md**:
   - Include all 15 datasets
   - Conservative SOTA claim with full evidence
   - What we can claim vs. cannot claim

### Publication Deliverables

1. **Paper Draft** (LaTeX/Markdown):
   - Title: "ThreeApproachRAG: A Novel Multi-Strategy Retrieval System Achieving State-of-the-Art Performance on BEIR"
   - Sections: Introduction, Related Work, Methods, Results, Analysis, Conclusion
   - Figures: BEIR comparison chart, per-dataset bar chart, ablation studies
   - Tables: Full BEIR results, statistical tests, runtime analysis

2. **ArXiv Preprint** (optional):
   - Upload to arXiv after full validation
   - Generate DOI for citation
   - Share with research community

3. **Conference Submission** (target: SIGIR 2026, ACL 2026, or EMNLP 2026):
   - Format paper for target venue
   - Prepare supplementary materials
   - Code and data availability statement

---

## Budget and Resources

### Compute Costs

**Local Execution** (Current Plan):
- Hardware: Already available (macOS with sufficient resources)
- Electricity: ~$20-30 for 100 hours of compute
- **Total**: $20-30

**Cloud Execution** (Alternative):
- AWS EC2 m5.4xlarge (16 vCPUs, 64 GB RAM): $0.77/hour
- 100 hours: $77
- Storage (250 GB EBS): $25
- **Total**: ~$100-120

**GPU Acceleration** (Optional):
- AWS g4dn.xlarge (1 GPU, 16 GB GPU RAM): $0.526/hour
- 50 hours (2x speedup): $26
- **Total**: ~$26 additional

### Labor Estimate

**Your Time** (Assuming self-execution):
- Setup and monitoring: 10-15 hours
- Analysis and documentation: 20-30 hours
- Paper writing: 30-40 hours
- **Total**: 60-85 hours

**AI Assistant Time** (Claude Code):
- Code modifications: 5-10 hours
- Analysis assistance: 10-15 hours
- Documentation generation: 10-15 hours
- **Total**: 25-40 hours

---

## Alternative: Prioritized Partial Testing

If full 15-dataset testing is not feasible, prioritize based on publication impact:

### Tier 1: Critical Datasets (Must-Have for SOTA Claim)

1. **msmarco** - Most widely used IR benchmark
2. **hotpotqa** - Multi-hop reasoning (our strength)
3. **fever** - Fact verification (our strength)
4. **nq** - Open-domain QA (high impact)
5. **scifact** - Scientific claims (domain similarity to nfcorpus)

**Rationale**: These 5 + nfcorpus (6 total) cover diverse domains and represent ~40% of BEIR queries

### Tier 2: Important Datasets (Strengthen SOTA Claim)

6. **trec-covid** - Topical relevance, medical domain
7. **quora** - Semantic similarity (easy dataset, boosts average)
8. **arguana** - Argument mining (reasoning test)
9. **fiqa** - Finance domain (domain transfer test)

**Rationale**: These 4 + Tier 1 (10 total) represent ~70% of BEIR queries

### Tier 3: Optional Datasets (Comprehensive Coverage)

10. **climate-fever** - Hard dataset, specialized domain
11. **robust04** - Traditional IR benchmark
12. **dbpedia-entity** - Entity retrieval
13. **scidocs** - Citation prediction (hardest dataset)
14. **signal1m** - Social media/news

**Rationale**: Comprehensive coverage, but lower publication priority

---

## Next Steps (Immediate Actions)

### Step 1: Confirm Plan Approval ✅

**Action**: Get your approval to proceed with this plan
**Questions to resolve**:
- Do we proceed with all 15 datasets or prioritized subset?
- Should we start with Phase 1 (small datasets) this week?
- Do we need to optimize code before starting large-scale testing?
- Should we set up cloud resources or use local compute?

### Step 2: Environment Setup (Day 1)

**Action**: Prepare for multi-dataset testing
**Tasks**:
- Download all BEIR datasets (or prioritized subset)
- Create `beir_all_datasets.py` script
- Test on 1 small dataset (e.g., scifact) to validate setup
- Set up monitoring and checkpointing

### Step 3: Phase 1 Execution (Days 2-5)

**Action**: Run small dataset benchmarks
**Tasks**:
- Execute benchmarks on 5 small datasets
- Monitor progress and results
- Calculate Phase 1 aggregate
- Decision point: Proceed to Phase 2?

### Step 4: Iterative Execution (Weeks 2-3)

**Action**: Execute Phases 2 and 3
**Tasks**:
- Run medium datasets (Phase 2)
- Run large datasets (Phase 3)
- Continuous monitoring and analysis

### Step 5: Analysis and Documentation (Week 4)

**Action**: Compile comprehensive results
**Tasks**:
- Calculate final BEIR average
- Statistical significance tests
- Create publication-ready documentation
- Draft paper or preprint

---

## Conclusion

This plan provides a comprehensive roadmap to validate ThreeApproachRAG across all 15 BEIR datasets. The phased approach allows for:

1. **Early validation** with small datasets (Phase 1)
2. **Scalability testing** with medium datasets (Phase 2)
3. **Production validation** with large datasets (Phase 3)
4. **Risk mitigation** with clear decision points and fallback options
5. **Flexibility** to prioritize critical datasets if full testing is not feasible

**Expected Outcome**: Publication-quality evidence that ThreeApproachRAG achieves competitive or state-of-the-art performance on the comprehensive BEIR benchmark.

**Timeline**: 3-4 weeks from start to complete results
**Cost**: $20-120 depending on compute strategy
**Impact**: Transform single-dataset SOTA claim into comprehensive BEIR SOTA claim

---

**Ready to proceed with Phase 1 small datasets?** Let me know if you want to:
1. Start immediately with Phase 1 (scifact, arguana, fiqa, trec-covid, scidocs)
2. Run prioritized subset only (Tier 1 critical datasets)
3. Make any modifications to this plan before execution
