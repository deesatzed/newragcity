Perform a comprehensive drift detection check before continuing with the current task.

## Drift Detection Protocol

### Step 1: Read Mission Critical Documentation
Read `/Volumes/WS4TB/newragcity/UltraRAG-main/MISSION_CRITICAL.md` and summarize:
- What newragcity IS (one unified system)
- The 5 catastrophic drifts that occurred
- Forbidden patterns vs required patterns

### Step 2: Answer Drift Detection Questions

For the CURRENT TASK you're working on, answer these 4 questions honestly:

1. **Am I working on newragcity as a unified system?**
   - YES = Good (e.g., testing docker-compose, end-to-end queries)
   - NO = DRIFT DETECTED

2. **Am I treating components as separate apps?**
   - NO = Good (components are subsystems of ONE app)
   - YES = DRIFT DETECTED

3. **Would this work make sense to an end user of newragcity?**
   - YES = Good (users care about the complete system)
   - NO = DRIFT DETECTED

4. **Am I following docker-compose.yml architecture?**
   - YES = Good (docker-compose defines how system runs)
   - NO = DRIFT DETECTED

### Step 3: Report Findings

**If NO DRIFT detected**:
- Confirm: "✅ No drift detected. Current approach aligns with newragcity as a unified system."
- Summarize what you're working on and why it's correct
- Continue with task

**If DRIFT detected**:
- Acknowledge: "❌ DRIFT DETECTED"
- Explain what you were doing wrong (which pattern from MISSION_CRITICAL.md)
- Explain what you should be doing instead (correct unified approach)
- Propose corrected plan
- Ask user to confirm before proceeding

### Step 4: Course Correction (If Drift Detected)

- Stop current approach
- Re-read MISSION_CRITICAL.md in full
- Propose approach that treats newragcity as ONE unified system
- Reference docker-compose.yml for how system actually runs
- Wait for user confirmation

---

## Example Drift Detection

**Current task**: "Implement dkr_evaluator.py for isolated DKR benchmarking"

**Drift Check**:
1. Am I working on unified system? NO - working on DKR alone
2. Am I treating components as separate? YES - benchmarking DKR in isolation
3. Would this make sense to end user? NO - users query one system, not components
4. Am I following docker-compose.yml? NO - ignoring integrated architecture

**Result**: ❌ DRIFT DETECTED (Matches Drift #5 pattern)

**Corrected approach**: "Run docker-compose up and benchmark end-to-end queries through unified API to test how DKR + Ersatz + RoT work together"

---

**User Trigger**: Run `/check-drift` anytime you sense I'm drifting away from the unified system concept
