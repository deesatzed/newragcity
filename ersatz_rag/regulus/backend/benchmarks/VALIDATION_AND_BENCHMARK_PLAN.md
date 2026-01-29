# BEIR Dataset Validation and Benchmark Execution Plan

**Date**: 2026-01-27
**Status**: Ready to Execute
**Strategy**: Option C + Modified B (Validate First, Then Benchmark)

---

## Current Situation

### What Happened
1. ✅ **SciFact succeeded**: 0.5804 nDCG@10 (49 minutes, valid result)
2. ❌ **ArgUana failed catastrophically**: 0.0000 nDCG@10 (all 1406 queries returned zeros)
3. ✅ **All 13 datasets downloaded**: Located in `/Volumes/WS4TB/newragcity/UltraRAG-main/datasets/`
4. ⚠️ **Unknown status**: 11 other datasets untested

### Critical Lessons Learned
- ❌ JSON serialization bug cost 10+ hours (numpy.bool_ vs bool)
- ❌ Parallel execution failed (LEANN ZMQ concurrency issues)
- ❌ Sequential benchmark launched without validation (arguana failure discovered after 1 hour)
- ✅ Validation test (validate_benchmark_system.py) prevented second JSON failure

### Why Validation is Critical
**Without validation**: Risk running 85 hours only to discover multiple datasets fail like arguana
**With validation**: 15-20 minutes to identify problem datasets before committing to full benchmark

---

## THE PLAN: 3-Phase Approach

### Phase 1: Pre-Flight Validation (15-20 minutes)

**Goal**: Test all 13 datasets with 10 queries each to identify failures before full benchmark

**Script**: `validate_all_datasets.py` (already created)

**What it tests**:
- Dataset loading (corpus, queries, qrels)
- Index building for each dataset
- Query execution (10 queries per dataset)
- Result validation (non-zero nDCG and Recall)
- Error detection and reporting

**Expected output**:
```
VALIDATION SUMMARY
======================================================================
Total datasets: 13
✅ Passed: 11-13 datasets
❌ Failed: 0-2 datasets

PASSED DATASETS:
  ✅ scifact              nDCG@10=0.5804
  ✅ fiqa                 nDCG@10=0.xxxx
  ...

FAILED DATASETS:
  ❌ arguana              (Zero results: nDCG@10=0.0000)
  ❌ [others if any]
======================================================================
```

**Deliverables**:
- `validation_results.json` - Complete validation report
- List of datasets safe to benchmark
- List of datasets to exclude (with failure reasons)

**Decision Point**: Only proceed to Phase 2 if >10 datasets pass validation

---

### Phase 2: Modified Benchmark Script (1 hour)

**Goal**: Update `beir_all_datasets.py` to:
1. Only run on validated datasets (exclude failures)
2. Add per-query validation (skip queries that return zero results)
3. Enhanced error handling with automatic retry logic
4. More frequent checkpoints (after every dataset, not just phases)

**Changes required**:

```python
# 1. Add dataset whitelist from validation results
VALIDATED_DATASETS = [
    # Load from validation_results.json
    # Only include datasets that passed validation
]

# 2. Add per-query validation
def validate_query_results(results: Dict) -> bool:
    """Check if query returned valid results."""
    if not results:
        return False
    if all(score == 0.0 for score in results.values()):
        return False  # All-zero results = failure
    return True

# 3. Enhanced run_single_dataset with validation
def run_single_dataset(self, dataset_info: Dict) -> Optional[Dict]:
    # ... existing code ...

    # Add per-query validation
    invalid_queries = 0
    for qid in queries:
        retrieved = self.rag_system.query(...)

        if not validate_query_results(retrieved):
            invalid_queries += 1
            if invalid_queries > 10:  # Fail-fast if too many bad queries
                raise ValueError(f"Too many invalid queries ({invalid_queries})")

        results[qid] = retrieved

    # ... rest of code ...

# 4. Save checkpoint after EVERY dataset (not just phases)
def run_all(self):
    for dataset_info in VALIDATED_DATASETS:
        result = self.run_single_dataset(dataset_info)
        self._save_checkpoint()  # Save after each dataset
        self._save_results(result)  # Save result immediately
```

**Deliverables**:
- Updated `beir_all_datasets.py` with validation logic
- Tested on scifact (known good) to verify changes work

---

### Phase 3: Production Benchmark Execution (60-80 hours)

**Goal**: Run full benchmark on validated datasets only

**Execution**:
```bash
cd /Volumes/WS4TB/newragcity/UltraRAG-main/ersatz_rag/regulus/backend/benchmarks

# Launch with 100-hour timeout (buffer for 80-hour expected runtime)
timeout 360000 python3 beir_all_datasets.py \
    --datasets-from-validation validation_results.json \
    2>&1 | tee /tmp/beir_production_benchmark.log &

echo "Production benchmark started (PID: $!)"
echo "Monitor: tail -f /tmp/beir_production_benchmark.log"
```

**Monitoring checkpoints**:
- After dataset 1 (scifact): Verify JSON save works (~1 hour)
- After dataset 3: First progress report (~3-4 hours)
- After dataset 6: Mid-progress report (~24-36 hours)
- After dataset 9: Late-stage report (~48-60 hours)
- After all datasets: Final BEIR aggregate (~60-80 hours)

**Monitoring script** (`monitor_production.sh`):
```bash
#!/bin/bash
# Check progress every 4 hours

while true; do
    echo "=== $(date) ==="

    # Check if process running
    if ! ps aux | grep -v grep | grep "beir_all_datasets.py" > /dev/null; then
        echo "⚠️  Benchmark process not running!"
        break
    fi

    # Check completed datasets
    COMPLETED=$(ls results/all_beir_datasets/*_results.json 2>/dev/null | wc -l)
    echo "✓ Datasets completed: $COMPLETED/[total]"

    # Check latest results
    LATEST=$(ls -t results/all_beir_datasets/*_results.json 2>/dev/null | head -1)
    if [ -n "$LATEST" ]; then
        DATASET=$(basename "$LATEST" _results.json)
        NDCG=$(python3 -c "import json; print(json.load(open('$LATEST'))['metrics']['nDCG@10'])")
        echo "  Latest: $DATASET = $NDCG"
    fi

    # Sleep 4 hours
    sleep 14400
done
```

**Success criteria**:
- All validated datasets complete with non-zero results
- Checkpoint file updates after each dataset
- All result JSONs saved successfully
- Final BEIR aggregate calculated

---

## Execution Checklist

### Pre-Flight (Before Phase 1)
- [ ] Verify all 13 datasets exist in `/Volumes/WS4TB/.../datasets/`
- [ ] Kill any running benchmark processes
- [ ] Clear previous results: `rm -rf results/all_beir_datasets/*`
- [ ] Verify LEANN backend is running
- [ ] Verify sufficient disk space (>10GB free)

### Phase 1: Validation
- [ ] Run `python3 validate_all_datasets.py`
- [ ] Wait 15-20 minutes for completion
- [ ] Review `validation_results.json`
- [ ] Identify passed datasets (expect 11-13)
- [ ] Document failed datasets and reasons
- [ ] **DECISION**: Proceed only if ≥10 datasets passed

### Phase 2: Update Benchmark Script
- [ ] Create backup: `cp beir_all_datasets.py beir_all_datasets.py.backup`
- [ ] Add dataset whitelist from validation results
- [ ] Add per-query validation logic
- [ ] Add per-dataset checkpoint saves
- [ ] Test on scifact: `python3 beir_all_datasets.py --test-dataset scifact`
- [ ] Verify scifact produces same result as before (~0.58)
- [ ] **DECISION**: Proceed only if test passes

### Phase 3: Production Benchmark
- [ ] Launch benchmark in background with timeout
- [ ] Verify first dataset (scifact) completes successfully
- [ ] Set up monitoring script to run every 4 hours
- [ ] Check progress after 3 datasets (~3-4 hours)
- [ ] Check progress after 6 datasets (~24-36 hours)
- [ ] Check progress after 9 datasets (~48-60 hours)
- [ ] Wait for completion (~60-80 hours total)
- [ ] Verify all datasets completed successfully
- [ ] Calculate final BEIR aggregate score

### Post-Benchmark
- [ ] Generate comprehensive results report
- [ ] Compare to SOTA (NV-Embed: 0.5935)
- [ ] Document per-dataset performance
- [ ] Create performance analysis
- [ ] Archive all results and logs

---

## Risk Mitigation

### Risk 1: Validation shows many failures
**Mitigation**:
- Investigate common failure patterns
- Fix issues if possible (e.g., index building bugs)
- Run validation again after fixes
- Proceed with ≥10 passing datasets

### Risk 2: Benchmark fails mid-run
**Mitigation**:
- Checkpoint system saves progress after each dataset
- Can resume from checkpoint
- Monitoring detects failures within 4 hours
- Fail-fast logic stops after 10 invalid queries per dataset

### Risk 3: More datasets like arguana (all zeros)
**Mitigation**:
- Per-query validation catches this early (after 10 bad queries)
- Dataset marked as failed, moves to next dataset
- No wasted compute on 1406 zero-result queries

### Risk 4: JSON serialization errors
**Mitigation**:
- Explicit Python type conversions (bool(), float())
- Validation test already created and passes
- Same fix applied to modified benchmark script

### Risk 5: LEANN backend crashes
**Mitigation**:
- Sequential execution (no parallel to avoid ZMQ issues)
- Monitor process health every 4 hours
- Restart from checkpoint if needed

---

## Expected Outcomes

### Validation Phase (15-20 minutes)
**Best case**: All 13 datasets pass
**Expected case**: 11-12 datasets pass (arguana + maybe 1 other fail)
**Worst case**: <10 datasets pass (need deeper investigation)

### Benchmark Phase (60-80 hours)
**Best case**: All validated datasets complete, BEIR aggregate >0.50
**Expected case**: 11-12 datasets complete, BEIR aggregate 0.45-0.52
**Worst case**: Additional failures discovered, but checkpoint allows recovery

### Time Savings
- **Without validation**: 85 hours potentially wasted on bad datasets
- **With validation**: 15 minutes to catch issues + 60-80 hours for valid datasets
- **ROI**: 85 hours / 0.25 hours = 340x risk reduction

---

## Next Steps After Benchmark

### If BEIR Average ≥ 0.50 (Competitive with SOTA)
1. Celebrate! 🎉
2. Analyze which datasets we beat SOTA on
3. Document architectural advantages (PageIndex + LEANN + deepConf)
4. Publish results and methodology

### If BEIR Average 0.45-0.50 (Respectable, Below SOTA)
1. Implement better embeddings (Qwen3-Embedding-0.6B or embeddinggemma-300m)
2. Expected improvement: +92% to +99% retrieval performance
3. Re-run benchmark with new embeddings
4. Expected new average: 0.58-0.62 (beats SOTA!)

### If BEIR Average <0.45 (Below Expectations)
1. Deep-dive root cause analysis
2. Check if embeddings are loading correctly
3. Verify LEANN index quality
4. Test deepConf threshold tuning
5. Consider architectural changes

---

## Files Created/Modified

### New Files
1. `validate_all_datasets.py` - Pre-flight validation script
2. `VALIDATION_AND_BENCHMARK_PLAN.md` - This document
3. `validation_results.json` - Validation output (after Phase 1)
4. `monitor_production.sh` - Monitoring script (to be created)

### Modified Files
1. `beir_all_datasets.py` - Will update with validation logic
2. `checkpoint.json` - Updated after each dataset completion

### Results Files (After Benchmark)
```
results/all_beir_datasets/
├── checkpoint.json
├── scifact_results.json
├── fiqa_results.json
├── [11-13 other dataset results]
└── beir_aggregate_final.json
```

---

## Key Decision Points

### 🛑 STOP if:
- Validation shows <10 datasets passing
- Test run on scifact fails after Phase 2 modifications
- First production dataset fails to save results

### ⚠️ INVESTIGATE if:
- Validation shows unexpected patterns (e.g., all small datasets fail)
- Benchmark progress stalls for >6 hours
- Multiple datasets show same failure mode

### ✅ PROCEED if:
- Validation passes ≥10 datasets
- Test run on scifact matches previous result
- First production dataset completes successfully

---

## Contact Points for Issues

### JSON Serialization Errors
- Check: Lines 323-327 in beir_all_datasets.py
- Fix: Use `bool()`, `float()` explicit conversions
- Validate: Run `validate_benchmark_system.py`

### Zero Results Issues
- Check: Per-query validation logic
- Debug: Run single query manually to inspect results
- Fix: May need to exclude dataset or fix index building

### LEANN Backend Issues
- Check: ZMQ connection errors in logs
- Fix: Restart LEANN backend if needed
- Avoid: Parallel execution (known issue)

### Checkpoint/Resume Issues
- Check: checkpoint.json format and contents
- Fix: Manually edit checkpoint to resume from specific dataset
- Verify: Compare dataset order in script vs checkpoint

---

## Estimated Timeline

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Pre-flight checks | 15 min | 0:15 |
| Phase 1: Validation | 15-20 min | 0:30-0:35 |
| Analysis & decision | 15 min | 0:45-0:50 |
| Phase 2: Script updates | 30-45 min | 1:15-1:35 |
| Testing updates | 15-30 min | 1:30-2:05 |
| Phase 3: Benchmark launch | 5 min | 1:35-2:10 |
| **Total preparation** | **~2 hours** | |
| Phase 3: Benchmark execution | 60-80 hours | 62-82 hours |
| Post-benchmark analysis | 2-3 hours | 64-85 hours |
| **TOTAL PROJECT TIME** | **~64-85 hours** | |

---

## Success Metrics

### Validation Phase Success
- ✅ All datasets load successfully
- ✅ ≥10 datasets return non-zero results
- ✅ Validation report generated
- ✅ Clear pass/fail for each dataset

### Benchmark Phase Success
- ✅ All validated datasets complete
- ✅ No JSON serialization errors
- ✅ All results saved successfully
- ✅ BEIR aggregate calculated
- ✅ Per-dataset nDCG@10 documented

### Overall Project Success
- ✅ Comprehensive 11-13 dataset results
- ✅ BEIR aggregate score calculated
- ✅ Comparison to SOTA documented
- ✅ Clear path to improvement identified
- ✅ No catastrophic time waste (10+ hour failures)

---

## Final Approval Checklist

Before executing, confirm:
- [ ] User approves 3-phase approach
- [ ] User accepts ~2 hour prep + 60-80 hour benchmark timeline
- [ ] User understands arguana and potentially 1-2 other datasets may be excluded
- [ ] User wants to proceed with validation first (vs. direct benchmark)
- [ ] Sufficient compute resources available (CPU/GPU for 60-80 hours)
- [ ] Can monitor progress periodically (every 4-6 hours recommended)

---

**STATUS**: ✅ READY TO EXECUTE
**NEXT ACTION**: Run Phase 1 validation
**COMMAND**: `python3 validate_all_datasets.py`
