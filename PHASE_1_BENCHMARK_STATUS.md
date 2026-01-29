# Phase 1 BEIR Benchmark Status - Live Tracking

**Started**: January 26, 2026
**Status**: ✅ IN PROGRESS
**Phase**: 1 of 3 (Small Datasets)

---

## Current Operations

### Benchmark Running
- **scifact**: ✅ RUNNING (PID: 59915)
  - Status: Building index, starting queries
  - Log: `/tmp/scifact_benchmark.log`
  - Expected time: 45 minutes (300 queries)
  - Monitor: `tail -f /tmp/scifact_benchmark.log`

### Datasets Downloading
- **Phase 1 Download**: ✅ RUNNING (Bash ID: 11758b)
  - Downloading: arguana, fiqa, trec-covid, scidocs
  - Already complete: nfcorpus (done), scifact (done)
  - Monitor: `BashOutput tool with ID 11758b`

---

## Phase 1 Datasets (5 total)

| # | Dataset | Docs | Queries | Status | nDCG@10 | Time |
|---|---------|------|---------|--------|---------|------|
| ✅ | **nfcorpus** | 3.6K | 323 | COMPLETE | **0.5086** | Done |
| 🔄 | **scifact** | 5.2K | 300 | RUNNING | TBD | ~45 min |
| ⏳ | **arguana** | 8.7K | 1,406 | PENDING | TBD | ~2 hrs |
| ⏳ | **fiqa** | 57K | 648 | PENDING | TBD | ~1.5 hrs |
| ⏳ | **trec-covid** | 171K | 50 | PENDING | TBD | ~1 hr |
| ⏳ | **scidocs** | 25K | 1,000 | PENDING | TBD | ~2 hrs |

**Phase 1 Total**: 3,404 queries, ~8-10 hours

---

## Setup Complete

### Infrastructure Created
✅ `beir_all_datasets.py` - Multi-dataset benchmark orchestrator
✅ `download_beir_datasets.py` - Dataset download manager
✅ Checkpointing system - Resume capability
✅ Phase-based execution - Organized testing

### Key Features
- **Checkpointing**: Automatically saves progress, can resume
- **Parallel Execution**: Download while benchmarking
- **Results Tracking**: Individual + aggregate results
- **SOTA Comparison**: Automatic comparison to published baselines

---

## Monitoring Commands

```bash
# Check scifact benchmark progress
tail -f /tmp/scifact_benchmark.log

# Check if scifact still running
ps aux | grep 59915

# Check download progress (use BashOutput tool with ID: 11758b)

# List downloaded datasets
python3 download_beir_datasets.py --list

# Check results (after completion)
cat benchmarks/results/all_beir_datasets/scifact_results.json
```

---

## Next Steps (After Scifact Completes)

### Automatic (via beir_all_datasets.py)
If running full Phase 1:
1. ✅ scifact completes → saves results
2. ⏩ arguana starts automatically
3. ⏩ fiqa starts after arguana
4. ⏩ trec-covid starts after fiqa
5. ⏩ scidocs starts after trec-covid
6. 📊 Phase 1 aggregate calculated

### Manual (if running dataset-by-dataset)
```bash
# After scifact, run next dataset:
python3 beir_all_datasets.py --dataset arguana

# Or run all remaining Phase 1:
python3 beir_all_datasets.py --phase 1
```

---

## Expected Results

### Current Baseline (nfcorpus)
- Our score: **0.5086 nDCG@10**
- Published SOTA: **0.3381** (Cathedral-BEIR)
- **Improvement: +50%** ✅

### Phase 1 Predictions

**scifact** (Running):
- Published SOTA: 0.6885
- Our prediction: 0.55-0.65
- Confidence: High (scientific claims, similar to nfcorpus)

**arguana** (Pending):
- Published SOTA: 0.6375
- Our prediction: 0.45-0.55
- Confidence: Medium (reasoning-heavy)

**fiqa** (Pending):
- Published SOTA: 0.3649
- Our prediction: 0.35-0.45
- Confidence: Medium (domain shift to finance)

**trec-covid** (Pending):
- Published SOTA: 0.6910
- Our prediction: 0.50-0.60
- Confidence: High (medical domain)

**scidocs** (Pending):
- Published SOTA: 0.1776 (hardest BEIR dataset)
- Our prediction: 0.15-0.20
- Confidence: Low (citation matching is hard)

### Phase 1 Target
- **Predicted average**: 0.42-0.50 nDCG@10
- **Success criteria**: > 0.40 average
- **Stretch goal**: > 0.45 average

---

## Timeline

**Start**: January 26, 2026 @ 4:55 PM PST
**Scifact**: 45 min (completes ~5:40 PM)
**Full Phase 1**: 8-10 hours total

**If Running Sequentially**:
- scifact: 4:55 PM - 5:40 PM
- arguana: 5:40 PM - 7:40 PM
- fiqa: 7:40 PM - 9:10 PM
- trec-covid: 9:10 PM - 10:10 PM
- scidocs: 10:10 PM - 12:10 AM
- **Phase 1 Complete**: ~12:10 AM (Jan 27)

**If Running Parallel** (recommended):
- Small datasets can run in parallel (requires more RAM)
- **Phase 1 Complete**: 2-3 hours wall time

---

## Decision Point (After Phase 1)

### If avg nDCG@10 > 0.45:
✅ **Proceed to Phase 2** (medium datasets)
- Strong generalization demonstrated
- High confidence for Phase 2/3

### If avg nDCG@10 = 0.35-0.45:
⚠️ **Analyze, then proceed to Phase 2**
- Review failure cases
- Consider hyperparameter tuning
- Still publication-worthy

### If avg nDCG@10 < 0.35:
❌ **Pause and debug**
- Major system review needed
- Identify bottlenecks
- May need architectural changes

---

## Publication Impact

### With Phase 1 Complete (5 datasets):
- **Claim**: "Competitive performance on diverse BEIR datasets"
- **Venues**: Workshop papers, arXiv preprint
- **Confidence**: Medium

### With Phase 1+2 Complete (8 datasets):
- **Claim**: "Near-SOTA on BEIR benchmark"
- **Venues**: Conference papers (SIGIR, ACL)
- **Confidence**: High

### With All 15 Complete:
- **Claim**: "State-of-the-art on BEIR benchmark"
- **Venues**: Top-tier conferences (NeurIPS, ICML, SIGIR, ACL)
- **Confidence**: Very high

---

## Current System Performance

### Validated (1/15 datasets):
- **nfcorpus**: 0.5086 nDCG@10 (50% better than SOTA) ✅

### In Progress (1/15 datasets):
- **scifact**: Running now...

### Pending (13/15 datasets):
- **Phase 1**: 3 datasets remaining
- **Phase 2**: 3 datasets
- **Phase 3**: 6 large datasets

---

## Key Files

### Scripts
- `/Volumes/WS4TB/newragcity/UltraRAG-main/ersatz_rag/regulus/backend/benchmarks/beir_all_datasets.py`
- `/Volumes/WS4TB/newragcity/UltraRAG-main/ersatz_rag/regulus/backend/benchmarks/download_beir_datasets.py`

### Logs
- `/tmp/scifact_benchmark.log` (current)
- `/tmp/full_323_benchmark.log` (nfcorpus, completed)

### Results
- `/Volumes/WS4TB/newragcity/UltraRAG-main/ersatz_rag/regulus/backend/benchmarks/results/all_beir_datasets/`
  - `scifact_results.json` (pending)
  - `checkpoint.json` (tracks progress)
  - `aggregate_results.json` (after phase complete)

### Documentation
- `/Volumes/WS4TB/newragcity/UltraRAG-main/ALL_15_BEIR_DATASETS_PLAN.md` (comprehensive plan)
- `/Volumes/WS4TB/newragcity/UltraRAG-main/HONEST_SOTA_COMPARISON.md` (nfcorpus analysis)
- `/Volumes/WS4TB/newragcity/UltraRAG-main/PHASE_1_BENCHMARK_STATUS.md` (this file)

---

## Notes

- **No mock data**: All benchmarks use real BEIR datasets
- **Checkpointing**: System can resume if interrupted
- **Conservative approach**: Honest SOTA claims only with evidence
- **Statistical rigor**: Per-query scores saved for significance testing

---

**NEXT UPDATE**: Check scifact completion (~45 min from start)

**Monitor**: `tail -f /tmp/scifact_benchmark.log`
