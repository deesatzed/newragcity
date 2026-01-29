# Parallel BEIR Benchmark Execution Guide

**3x Faster**: Run 13 datasets in ~28-32 hours instead of 85-95 hours

---

## Overview

The parallel execution system runs 3 datasets concurrently to maximize throughput while avoiding resource contention.

### Architecture

```
beir_parallel_runner.py (master process)
    ├─> beir_single_dataset.py (worker 1: scifact)
    ├─> beir_single_dataset.py (worker 2: arguana)
    └─> beir_single_dataset.py (worker 3: fiqa)

All workers share:
- results/all_beir_datasets/ (results directory)
- checkpoint.json (coordination file)

Each worker has:
- /tmp/beir_parallel_logs/<dataset>.log (individual log)
```

### Time Savings

| Execution Mode | Time | Speedup |
|----------------|------|---------|
| Sequential | 85-95 hours | 1x |
| Parallel (3 workers) | 28-32 hours | **~3x** |

**Calculation**: With 3 concurrent workers, total time ≈ (total sequential time) / 3

---

## Files Created

### Core Components

1. **beir_parallel_runner.py** - Master orchestrator
   - Spawns 3 worker processes
   - Manages shared checkpoint
   - Coordinates dataset scheduling
   - Generates BEIR aggregate results

2. **beir_single_dataset.py** - Worker script
   - Runs benchmark on one dataset
   - Called by parallel runner
   - Saves results independently
   - Updates shared checkpoint

3. **monitor_parallel.sh** - Real-time dashboard
   - Shows global progress (X/13 datasets)
   - Lists active workers with PIDs
   - Displays recent completions
   - Shows live log snippets

4. **validate_parallel_system.py** - Validation test
   - Tests worker script execution
   - Validates JSON serialization
   - Verifies checkpoint coordination
   - Confirms no race conditions

---

## Usage

### Step 1: Run Validation (REQUIRED)

```bash
cd /Volumes/WS4TB/newragcity/UltraRAG-main/ersatz_rag/regulus/backend/benchmarks

# Validate system works (5-10 minutes)
python3 validate_parallel_system.py
```

**Expected output**:
```
✅ PARALLEL SYSTEM VALIDATION PASSED
System components verified:
  ✅ Worker script execution
  ✅ JSON serialization (Python native types)
  ✅ Result file creation
  ✅ Checkpoint coordination
```

### Step 2: Launch Parallel Benchmark

```bash
# Start parallel benchmark (3 concurrent workers)
python3 beir_parallel_runner.py --workers 3 > /tmp/beir_parallel_master.log 2>&1 &

# Note the PID
echo "Master PID: $!"
```

**Arguments**:
- `--workers 3` - Number of concurrent workers (default: 3)
- `--datasets-dir /path` - BEIR datasets location (optional)
- `--results-dir /path` - Results directory (optional)
- `--no-resume` - Start fresh instead of resuming (optional)

### Step 3: Monitor Progress

```bash
# Run dashboard once
./monitor_parallel.sh

# Or continuously (updates every 60 seconds)
watch -n 60 './monitor_parallel.sh'

# View specific worker log
tail -f /tmp/beir_parallel_logs/scifact.log
```

**Dashboard shows**:
- Master process status
- Active workers (3 running)
- Global progress (X/13 datasets, Y% complete)
- Recent completions with nDCG scores
- Live log snippets from active workers

### Step 4: Verify Progress (Within 30 Minutes)

```bash
# Check checkpoint after 30 minutes
cat results/all_beir_datasets/checkpoint.json

# Should show at least 1 completed dataset
# Example:
# {
#   "completed_datasets": ["scifact"],
#   "failed_datasets": [],
#   "last_updated": "2026-01-27T..."
# }
```

**CRITICAL**: If `completed_datasets` is still empty after 30 minutes, investigate immediately.

---

## Monitoring Dashboard Example

```
=======================================================================
PARALLEL BEIR BENCHMARK MONITORING - Mon Jan 27 15:30:00 PST 2026
=======================================================================

✅ Master process is RUNNING
   PID: 12345  Elapsed: 2:30:15

🔧 ACTIVE WORKERS:
-------------------------------------------------------------------
   3 workers currently running:
      [scifact] PID: 12346, Elapsed: 0:15:23
      [arguana] PID: 12347, Elapsed: 0:15:23
      [fiqa] PID: 12348, Elapsed: 0:15:23

📊 GLOBAL PROGRESS:
-------------------------------------------------------------------
   Progress: 3 / 13 datasets (23%)
   Failed: 0 datasets

   [████░░░░░░░░░░░░░░░░] 23%

   ✅ Completed datasets:
      - trec-covid
      - scidocs
      - nfcorpus

📁 COMPLETED RESULTS:
-------------------------------------------------------------------
   Total result files: 3

   Recent completions (last 5):
      ✅ nfcorpus: nDCG@10 = 0.5086, Time = 8.2h
      ✅ scidocs: nDCG@10 = 0.3421, Time = 2.1h
      ✅ trec-covid: nDCG@10 = 0.7234, Time = 1.8h

📝 ACTIVE WORKER LOGS (last 3 lines each):
-------------------------------------------------------------------
   [scifact]:
      Processing query 50/300...
      nDCG@10 (running): 0.6542
      Estimated completion: 0:45:00

   [arguana]:
      Processing query 120/1406...
      nDCG@10 (running): 0.4123
      Estimated completion: 2:15:00

   [fiqa]:
      Processing query 35/648...
      nDCG@10 (running): 0.5234
      Estimated completion: 1:30:00

=======================================================================
Commands:
  Monitor continuously:  watch -n 60 './monitor_parallel.sh'
  View specific log:     tail -f /tmp/beir_parallel_logs/<dataset>.log
  Check checkpoint:      cat results/all_beir_datasets/checkpoint.json
=======================================================================
```

---

## Expected Timeline

### Phase Breakdown (3 concurrent workers)

| Phase | Datasets | Sequential Time | Parallel Time | Details |
|-------|----------|-----------------|---------------|---------|
| **Phase 1** | 5 small | ~34h | ~11-12h | scifact, arguana, fiqa, trec-covid, scidocs |
| **Phase 2** | 2 medium | ~17h | ~6-7h | nfcorpus, dbpedia-entity |
| **Phase 3** | 6 large | ~34h | ~11-13h | hotpotqa, climate-fever, fever, nq, quora, msmarco |
| **TOTAL** | 13 datasets | ~85h | ~28-32h | ~3x speedup |

### Progress Checkpoints

| Time Elapsed | Expected Completed | Progress |
|--------------|-------------------|----------|
| 4 hours | 1-2 datasets | 8-15% |
| 8 hours | 3-4 datasets | 23-31% |
| 12 hours | 5-6 datasets | 38-46% |
| 24 hours | 9-11 datasets | 69-85% |
| 32 hours | 13 datasets | 100% |

**If you're behind schedule**: Check `monitor_parallel.sh` for failed datasets or slow workers.

---

## Resource Usage

### Concurrency Considerations

**Why 3 workers?**
- CPU: Each worker uses ~2-4 cores → 3 workers = 6-12 cores (safe on 8+ core systems)
- Memory: Each worker uses ~8-12GB → 3 workers = 24-36GB (safe on 64GB systems)
- Disk I/O: LEANN index reads are cached, minimal contention
- Network: Embeddings/LLM calls are rate-limited per worker

**Scaling Options**:
- **2 workers**: ~42-47 hours (safer on 32GB RAM)
- **3 workers**: ~28-32 hours (recommended for 64GB RAM)
- **4 workers**: ~21-24 hours (only if you have 128GB+ RAM and 16+ cores)

### System Requirements

**Minimum**:
- 8 CPU cores (4 physical cores with hyperthreading)
- 64GB RAM
- 500GB free disk space
- Stable internet connection

**Recommended**:
- 12+ CPU cores
- 128GB RAM
- 1TB free disk space
- Fast SSD (NVMe)

---

## Troubleshooting

### Issue: No workers starting

**Symptom**: Master process runs but no worker processes appear

**Check**:
```bash
ps aux | grep beir_single_dataset.py
```

**Fix**:
1. Check master log: `tail -50 /tmp/beir_parallel_master.log`
2. Verify datasets exist: `ls /Volumes/WS4TB/newragcity/UltraRAG-main/datasets/`
3. Check Python path: `which python3`

### Issue: Workers failing immediately

**Symptom**: Workers start then exit with error code

**Check**:
```bash
# View worker logs
ls -lh /tmp/beir_parallel_logs/
tail -50 /tmp/beir_parallel_logs/scifact.log
```

**Common causes**:
- JSON serialization bug (check LESSONS_LEARNED_JSON_BUG.md)
- Missing dependencies
- Dataset not downloaded
- LEANN backend not running

### Issue: Checkpoint not updating

**Symptom**: `completed_datasets` stays empty after 30+ minutes

**Fix**:
1. Stop benchmark immediately:
   ```bash
   pkill -f beir_parallel_runner.py
   pkill -f beir_single_dataset.py
   ```

2. Check worker logs for errors:
   ```bash
   grep -i error /tmp/beir_parallel_logs/*.log
   ```

3. Verify validation test passed:
   ```bash
   python3 validate_parallel_system.py
   ```

4. Review `LESSONS_LEARNED_JSON_BUG.md` for prevention measures

### Issue: One worker stuck/slow

**Symptom**: 2 workers completing normally, 1 worker taking 3x longer

**Check**:
```bash
./monitor_parallel.sh
# Look at "Elapsed" times for each worker
```

**Options**:
1. **Wait**: Large datasets (msmarco, hotpotqa) naturally take longer
2. **Kill slow worker**: If clearly stuck (no progress in 30+ minutes)
   ```bash
   kill <PID>
   # Parallel runner will mark as failed and continue
   ```

### Issue: Out of memory

**Symptom**: System becomes unresponsive, workers killed

**Fix**:
1. Reduce workers from 3 to 2:
   ```bash
   python3 beir_parallel_runner.py --workers 2
   ```

2. Monitor memory usage:
   ```bash
   watch -n 5 'free -h'  # Linux
   watch -n 5 'vm_stat'  # macOS
   ```

---

## Recovery and Resume

### Resuming After Interruption

The checkpoint system automatically enables resume:

```bash
# Start/restart parallel benchmark
python3 beir_parallel_runner.py --workers 3

# Checkpoint shows:
# "Loaded checkpoint: 5 completed, 1 failed"
# "8 datasets remaining"
```

### Starting Fresh

```bash
# Delete checkpoint and results
rm -rf results/all_beir_datasets/*

# Start fresh
python3 beir_parallel_runner.py --workers 3 --no-resume
```

---

## Final Results

### Location

```
results/all_beir_datasets/
├── checkpoint.json                    # Progress tracking
├── beir_aggregate_summary.json        # Final BEIR average
├── scifact_results.json              # Individual results
├── arguana_results.json
├── ...                               # (13 total)
```

### BEIR Aggregate

**File**: `results/all_beir_datasets/beir_aggregate_summary.json`

**Example**:
```json
{
  "beir_aggregate_ndcg10": 0.5821,
  "total_datasets_completed": 13,
  "total_datasets_failed": 0,
  "total_queries_tested": 8456,
  "vs_sota_improvement": -1.9,
  "beats_sota": false,
  "completed_datasets": [
    "scifact", "arguana", "fiqa", "trec-covid", "scidocs",
    "nfcorpus", "dbpedia-entity", "hotpotqa", "climate-fever",
    "fever", "nq", "quora", "msmarco"
  ],
  "timestamp": "2026-01-27T18:45:00.123456"
}
```

**SOTA Comparison**: NV-Embed = 0.5935

---

## Comparison: Sequential vs Parallel

| Aspect | Sequential (beir_all_datasets.py) | Parallel (beir_parallel_runner.py) |
|--------|-----------------------------------|-----------------------------------|
| **Time** | 85-95 hours | 28-32 hours |
| **Throughput** | 1 dataset at a time | 3 datasets concurrently |
| **Monitoring** | monitor_benchmark.sh | monitor_parallel.sh |
| **Logs** | Single log file | Individual per dataset |
| **Resource usage** | Low (1x) | High (3x) |
| **Resume** | ✅ Yes | ✅ Yes |
| **Risk** | Low (isolated failures) | Medium (shared resources) |

**When to use sequential**:
- Limited RAM (<64GB)
- Limited CPU (<8 cores)
- Prefer safety over speed
- Running other intensive tasks

**When to use parallel**:
- Sufficient resources (64GB+ RAM, 8+ cores)
- Want results 3x faster
- Monitored environment
- Dedicated machine

---

## Commands Summary

```bash
# 1. VALIDATE SYSTEM (required, 5-10 minutes)
python3 validate_parallel_system.py

# 2. LAUNCH PARALLEL BENCHMARK (28-32 hours)
python3 beir_parallel_runner.py --workers 3 > /tmp/beir_parallel_master.log 2>&1 &

# 3. MONITOR PROGRESS (run periodically)
./monitor_parallel.sh

# 4. CONTINUOUS MONITORING
watch -n 60 './monitor_parallel.sh'

# 5. CHECK CHECKPOINT (verify progress)
cat results/all_beir_datasets/checkpoint.json

# 6. VIEW WORKER LOG
tail -f /tmp/beir_parallel_logs/<dataset>.log

# 7. VIEW MASTER LOG
tail -f /tmp/beir_parallel_master.log

# 8. VIEW FINAL RESULTS
cat results/all_beir_datasets/beir_aggregate_summary.json

# 9. KILL IF NEEDED
pkill -f beir_parallel_runner.py
pkill -f beir_single_dataset.py
```

---

## Next Steps

After parallel benchmark completes:

1. **Verify results**:
   ```bash
   cat results/all_beir_datasets/beir_aggregate_summary.json
   ```

2. **Compare to SOTA**:
   - Our result: X.XXXX
   - NV-Embed: 0.5935
   - Improvement: +Y.Y%

3. **Analyze per-dataset**:
   ```bash
   grep -A5 '"metrics"' results/all_beir_datasets/*_results.json
   ```

4. **Archive results**:
   ```bash
   tar -czf beir_results_$(date +%Y%m%d).tar.gz results/all_beir_datasets/
   ```

5. **Clean up logs**:
   ```bash
   rm -rf /tmp/beir_parallel_logs/
   rm /tmp/beir_parallel_master.log
   ```

---

## Key Advantages

✅ **3x faster** - Complete in ~30 hours instead of ~90 hours

✅ **Validated system** - Proven with validation test

✅ **Real-time monitoring** - Know exactly what's happening

✅ **Resume capability** - Checkpoint system prevents data loss

✅ **Individual logs** - Easy to debug failures

✅ **Shared checkpoint** - No race conditions or corruption

✅ **Resource efficient** - 3 workers balances speed and safety

---

**Ready to run?** Follow the 4-step process above and monitor with `monitor_parallel.sh` every hour!
