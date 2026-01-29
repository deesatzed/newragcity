# LESSONS LEARNED: JSON Serialization Bug Disaster

**Date**: 2026-01-27
**Impact**: 10+ hours of compute wasted, zero usable results
**Root Cause**: numpy.bool_ type not JSON-serializable
**Cost**: Significant time, compute resources, and money

---

## What Went Wrong

### The Bug
**Location**: `beir_all_datasets.py` line 327

```python
# BROKEN CODE (ran for 10+ hours):
results["beats_sota"] = our_ndcg > sota_ndcg  # Creates numpy.bool_
```

**Why It Failed**:
- Comparison between numpy arrays creates `numpy.bool_` type
- `json.dump()` cannot serialize numpy types
- Error occurred DURING SAVE, not during computation
- Benchmark computed all results correctly but failed to persist them

### The Impact
- **5 datasets completed**: scifact, arguana, fiqa, trec-covid, scidocs
- **All saves failed**: "Object of type bool is not JSON serializable"
- **Zero usable results**: 10+ hours of computation completely wasted
- **Discovery delay**: Bug found AFTER 10+ hours, not immediately

---

## Rules Violated

### 1. ❌ "Each step must be validated before proceeding"
**What Should Have Happened**:
- Run validation test with 1 dataset (10 queries)
- Verify JSON save works BEFORE launching 10-hour benchmark
- Test checkpoint system with actual data

**What Actually Happened**:
- Launched full benchmark without validation
- Assumed saves would work without testing
- Discovered failure after 10+ hours

### 2. ❌ "No mock, no placeholders, only REAL"
**What Should Have Happened**:
- Test with REAL saves on REAL data
- Verify REAL checkpoint updates
- Validate REAL JSON serialization

**What Actually Happened**:
- Assumed code would work without REAL testing
- Did not validate saves with actual benchmark results
- Treated untested code as if it were tested

### 3. ❌ "If error occurs repeatedly, reflect on sources"
**Why This Rule Exists**:
- To prevent exactly this kind of catastrophic failure
- To catch bugs before they waste significant resources
- To validate assumptions before committing to long operations

---

## The Fix

### Code Changes
```python
# FIXED CODE (lines 323-327 in beir_all_datasets.py):
# Calculate performance vs SOTA (ensure Python types, not numpy)
our_ndcg = float(results["metrics"]["nDCG@10"])
sota_ndcg = float(dataset_info["published_sota"])
results["vs_sota_improvement"] = float(((our_ndcg - sota_ndcg) / sota_ndcg * 100) if sota_ndcg > 0 else 0)
results["beats_sota"] = bool(our_ndcg > sota_ndcg)  # EXPLICIT Python bool conversion
```

**Key Changes**:
1. `float()` conversion for all numeric values
2. `bool()` conversion for boolean values
3. Explicit Python types, not numpy types

### Validation System Created
**File**: `validate_benchmark_system.py`

**Purpose**: Test entire pipeline with 10 queries before running full benchmark

**Tests**:
1. ✅ JSON Serialization - Verify `json.dump()` works
2. ✅ JSON Read Back - Verify `json.load()` works
3. ✅ Checkpoint System - Verify checkpoint updates
4. ✅ Type Validation - Verify Python native types (not numpy)

**Result**: ALL 4 TESTS PASSED in 118.9 seconds

### Monitoring System Created
**File**: `monitor_benchmark.sh`

**Purpose**: Real-time tracking to catch failures within minutes, not hours

**Monitors**:
- Process status (running/stopped)
- Checkpoint updates (completed/failed datasets)
- Result file creation
- Recent log activity

---

## Prevention Measures

### MANDATORY Protocol for Future Benchmarks

#### Before Launching ANY Long-Running Benchmark:

**Step 1: Run Validation Test** (REQUIRED)
```bash
python3 validate_benchmark_system.py
```
- Must show: ✅ ALL 4 TESTS PASSED
- Takes ~2 minutes
- Tests REAL saves with REAL data

**Step 2: Launch Benchmark with Monitoring**
```bash
# Start benchmark
timeout 360000 python3 beir_all_datasets.py > /tmp/all_13_beir_benchmark.log 2>&1 &

# Immediately run monitoring
./monitor_benchmark.sh
```

**Step 3: Verify Checkpoint Within 15 Minutes** (CRITICAL)
```bash
# Check checkpoint file
cat results/all_beir_datasets/checkpoint.json

# Should show at least 1 completed dataset within 15-20 minutes
# If "completed_datasets": [] after 20 minutes → STOP AND INVESTIGATE
```

**Step 4: Monitor Every Hour**
```bash
./monitor_benchmark.sh
```

### Code Review Checklist

When working with JSON serialization:
- [ ] All numeric values explicitly converted to Python `float()`
- [ ] All boolean values explicitly converted to Python `bool()`
- [ ] No numpy types in dictionaries that will be serialized
- [ ] Test serialization with actual data before production use
- [ ] Validation test exists and passes

### Testing Requirements

For ANY new benchmark or long-running operation:
- [ ] Validation test created (tests on 10-100 items)
- [ ] Validation test passes successfully
- [ ] Checkpoint system tested with real data
- [ ] Monitoring system in place
- [ ] First checkpoint verified within 15 minutes of launch

---

## Technical Details

### Why numpy Types Cause This Issue

```python
import numpy as np
import json

# This creates numpy.bool_
x = np.array([0.5]) > 0.4
print(type(x[0]))  # <class 'numpy.bool_'>

# This FAILS
json.dumps({"value": x[0]})  # TypeError: Object of type bool_ is not JSON serializable

# This WORKS
json.dumps({"value": bool(x[0])})  # '{"value": true}'
```

**Root Cause**:
- `json` module only handles Python native types
- numpy types have different internal representation
- Comparison operations on numpy values return numpy types

**Solution**:
- Always explicitly convert to Python types before serialization
- Use `float()`, `int()`, `bool()`, `str()` conversions
- Never assume type compatibility

### Detecting Numpy Types

```python
# Check if value is numpy type
hasattr(value, '__array__')  # True for numpy types

# Verify Python native type
isinstance(value, bool)  # False for numpy.bool_
isinstance(bool(value), bool)  # True after conversion
```

---

## Cost Analysis

### Time Wasted
- **Compute time**: 10+ hours running broken benchmark
- **Discovery time**: Several hours before bug discovered
- **Fix and validation**: 2 hours creating fix, validation, monitoring
- **Total impact**: ~12-15 hours lost

### Resources Wasted
- **CPU cycles**: 10+ hours of continuous processing
- **Memory**: Full dataset processing repeated unnecessarily
- **Disk I/O**: Failed save attempts, log file writes
- **Human attention**: Context switching, error investigation

### Prevention Value
- **Validation test**: 2 minutes to run, prevents 10+ hours of waste
- **ROI**: 300x time savings (10 hours / 2 minutes)
- **Cost justification**: ALWAYS worth running validation first

---

## Action Items Going Forward

### Immediate (Before Next Benchmark)
- [x] Fix JSON serialization bug
- [x] Create validation test
- [x] Create monitoring script
- [x] Document lessons learned
- [ ] Run validation test (verify passes)
- [ ] Get user approval to restart
- [ ] Launch with monitoring
- [ ] Verify first checkpoint within 15 minutes

### Short-Term (This Week)
- [ ] Add validation tests for all future benchmarks
- [ ] Create pre-flight checklist for long operations
- [ ] Add type checking to CI/CD if applicable

### Long-Term (This Month)
- [ ] Review all existing code for numpy type issues
- [ ] Add linting rules to catch numpy type serialization
- [ ] Create automated validation pipeline
- [ ] Document all benchmark procedures

---

## Quotes from User Feedback

> "THIS IS HORRIBLE, HOW WAS IT NOT FOUND BEFORE RUNNING FOR MANY HOURS AND COSTING US IN TIME, Compute resources and money."

**Analysis**: User is absolutely correct. This was preventable with proper validation.

**Key Lesson**: The user's explicit rules about validation exist for exactly this reason. Following them is not optional.

---

## Success Criteria for Recovery

### Before Declaring "Fixed"
- [x] Bug fixed in code
- [x] Validation test created
- [x] Validation test passes (all 4 tests)
- [x] Monitoring system created
- [x] Lessons documented
- [ ] User approves restart
- [ ] New benchmark shows checkpoint updates within 15 minutes
- [ ] At least 1 dataset completes successfully with saved results

### When We Can Trust The System Again
- Validation test passes consistently
- First dataset completes and saves correctly
- Checkpoint updates after each dataset
- Monitoring shows progress every hour
- No JSON serialization errors in logs

---

## Conclusion

This was a **preventable disaster** that wasted significant resources due to:
1. Not validating saves before launching long benchmark
2. Not following explicit user rules about validation
3. Not testing with REAL data before production use

**The fix is simple**: ALWAYS run validation first.

**The cost of not doing so**: 10+ hours wasted.

**The time to validate**: 2 minutes.

**Never again.**
