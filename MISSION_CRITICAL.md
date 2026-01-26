# MISSION CRITICAL: newragcity Product Definition

**READ THIS FILE BEFORE ANY TASK - NO EXCEPTIONS**

**Last Updated**: January 25, 2026
**Purpose**: Prevent catastrophic drift by maintaining absolute clarity on what newragcity IS

---

## ABSOLUTE TRUTH #1: newragcity is ONE UNIFIED SYSTEM

**Product Name**: **newragcity**

**Architecture**: Multi-approach RAG system integrating four specialized components:
1. **DKR** (Deterministic Knowledge Retrieval) - The Auditor
2. **Ersatz** (LEANN + PageIndex + deepConf) - The Scholar
3. **RoT** (Render-of-Thought) - The Compressor
4. **UltraRAG** (MCP Orchestration) - The Conductor

**Deployment Model**: Docker Compose with 10 services working TOGETHER
- ultrarag (orchestration)
- dkr-server
- ersatz-server
- leann-service
- deepconf-service
- pageindex-service
- rot-server
- postgres
- redis
- ollama

**User Interface**: Single unified endpoint
- REST API: http://localhost:8000
- Web UI: http://localhost:5050

**User Experience**: Upload documents → Query system → Get response with ALL approaches integrated

---

## ABSOLUTE TRUTH #2: NEVER Work on Components in Isolation

### ❌ FORBIDDEN PATTERNS (Cause of All 5 Drifts)

**NEVER say or do**:
- "Let's benchmark DKR alone"
- "Let's benchmark Ersatz alone"
- "Let's benchmark RoT alone"
- "Let's implement dkr_evaluator.py for isolated testing"
- "Let's implement ersatz_evaluator.py for isolated testing"
- "Let's test LEANN separately"
- "Let's test PageIndex separately"
- "Let's run the DKR server by itself"
- "We can test the existing components individually"
- "Let's validate each component before integration"

**WHY FORBIDDEN**: These patterns treat newragcity as 4 separate apps. It is NOT 4 apps. It is ONE app with 4 specialized subsystems that work TOGETHER.

### ✅ REQUIRED PATTERNS (Prevent Drift)

**ALWAYS say or do**:
- "Let's run the newragcity system"
- "Let's start docker-compose up"
- "Let's run The Vault pipeline"
- "Let's benchmark the complete integrated system"
- "Let's test the end-to-end workflow"
- "Let's query the unified API endpoint"
- "Let's test multi-approach routing"
- "Let's validate DKR + Ersatz + RoT working together"

**WHY REQUIRED**: These patterns recognize newragcity as the UNIFIED SYSTEM it was designed to be.

---

## DRIFT DETECTION QUESTIONS

**Before starting ANY task, answer these 4 questions**:

### Question 1: Am I working on newragcity as a unified system?
- ✅ **YES** = Proceeding correctly (e.g., "docker-compose up", "test end-to-end query")
- ❌ **NO** = DRIFT DETECTED - Stop and re-read this file

### Question 2: Am I treating components as separate apps?
- ✅ **NO** = Proceeding correctly (components are subsystems of ONE app)
- ❌ **YES** = DRIFT DETECTED - Stop and re-read this file

### Question 3: Would this work make sense to an end user of newragcity?
- ✅ **YES** = Proceeding correctly (users care about the complete system)
- ❌ **NO** = DRIFT DETECTED - Stop and re-read this file

### Question 4: Am I following docker-compose.yml architecture?
- ✅ **YES** = Proceeding correctly (docker-compose.yml defines how system runs)
- ❌ **NO** = DRIFT DETECTED - Stop and re-read this file

**If ANY answer triggers drift → STOP IMMEDIATELY and ask user for clarification**

---

## THE 5 CATASTROPHIC DRIFTS (Learn From History)

### Drift #1: [Date Unknown] - Component Separation
**What happened**: Treated DKR, Ersatz, RoT as separate projects requiring individual validation
**Impact**: Lost sight of integrated system architecture
**Root cause**: Focused on component-level implementation without unified testing
**Lesson**: Components are subsystems, not standalone apps

### Drift #2: [Date Unknown] - Individual Benchmarking
**What happened**: Proposed benchmarking each component separately before integration
**Impact**: Created evaluator implementations that didn't test the actual product
**Root cause**: Forgot that users query ONE system, not three separate systems
**Lesson**: Benchmark the product users interact with

### Drift #3: [Date Unknown] - Isolated Development
**What happened**: Worked on DKR server without considering Ersatz/RoT integration
**Impact**: Created functionality that didn't align with orchestration layer
**Root cause**: Treated MCP servers as independent services instead of coordinated subsystems
**Lesson**: All development must consider UltraRAG orchestration

### Drift #4: [Date Unknown] - Missing Docker Context
**What happened**: Proposed running components via Python scripts instead of Docker
**Impact**: Lost production deployment model (docker-compose.yml)
**Root cause**: Forgot that newragcity is a dockerable system
**Lesson**: Always reference docker-compose.yml for how system runs

### Drift #5: January 25, 2026 - Benchmark Framework Isolation
**What happened**: User said "run the benchmarks" → I analyzed `servers/rot_reasoning/benchmarks/` in isolation → Proposed implementing evaluators for DKR and Ersatz separately
**Impact**: Created 559-line document (BENCHMARK_EXECUTION_REPORT.md) about isolated component benchmarking
**Root cause**: Focused on RoT-specific benchmark framework instead of unified system testing
**Lesson**: "Run benchmarks" means "test the complete newragcity system end-to-end"
**User feedback**: "why can't we run it as a single app that includes DKR, ErSatz, UltraRag, RoT and others? I'm confused as that was our overall purpose"

---

## CORRECT WORKFLOW EXAMPLES

### Example 1: User Says "Run the benchmarks"

❌ **WRONG (Drift Pattern)**:
```
1. Read servers/rot_reasoning/benchmarks/run_benchmarks.py
2. Notice rot_evaluator.py is placeholder
3. Propose: "Let's implement dkr_evaluator.py and ersatz_evaluator.py"
4. Create isolated component benchmarks
5. DRIFT: Forgot this is ONE unified system
```

✅ **CORRECT (Unified System)**:
```
1. Read MISSION_CRITICAL.md (this file)
2. Understand: User wants to benchmark THE COMPLETE SYSTEM
3. Check docker-compose.yml for how system runs
4. Propose: "Let's run docker-compose up and test end-to-end queries"
5. Measure: Query latency, confidence accuracy, multi-approach routing
6. SUCCESS: Tested the actual product users interact with
```

### Example 2: User Says "Test the system"

❌ **WRONG (Drift Pattern)**:
```
1. Test DKR alone with unit tests
2. Test Ersatz alone with unit tests
3. Test RoT alone with unit tests
4. Report: "All components pass tests"
5. DRIFT: Components work but system integration untested
```

✅ **CORRECT (Unified System)**:
```
1. Start complete system: docker-compose up -d
2. Upload test document via REST API
3. Run test query through unified endpoint
4. Verify: DKR + Ersatz + RoT all participated
5. Validate: Response quality, confidence scores, citations
6. SUCCESS: Tested end-to-end integration
```

### Example 3: User Says "How do I run newragcity?"

❌ **WRONG (Drift Pattern)**:
```
1. Explain how to run DKR server
2. Explain how to run Ersatz server
3. Explain how to run RoT server
4. User confused: "How do they work together?"
5. DRIFT: Presented components as separate apps
```

✅ **CORRECT (Unified System)**:
```
1. Point to QUICK_START.md
2. Explain 3-step process:
   a. docker-compose up -d
   b. Initialize Ollama model
   c. Access http://localhost:5050
3. User successful: Complete system running
4. SUCCESS: User has ONE app, not four separate apps
```

---

## WHAT IS newragcity? (Reference)

### Product Definition
newragcity is a **unified multi-approach RAG system** that intelligently combines four specialized retrieval and reasoning methods to provide high-confidence, well-cited answers to user queries.

### Architecture (From docker-compose.yml)
```
User Query
    ↓
REST API (port 8000) / Web UI (port 5050)
    ↓
UltraRAG Orchestrator
    ↓
┌───────────┬────────────┬───────────┐
│    DKR    │   Ersatz   │    RoT    │
│ (Auditor) │ (Scholar)  │(Compress) │
└───────────┴────────────┴───────────┘
    ↓           ↓              ↓
Exact Match   LEANN       Visual
TF-IDF        PageIndex   Reasoning
              deepConf    Compression
    ↓           ↓              ↓
┌─────────────────────────────────┐
│    Results Aggregation          │
│    Confidence Scoring           │
│    Citation Formatting          │
└─────────────────────────────────┘
    ↓
Response with:
  - Answer
  - Confidence score
  - Source citations
  - Audit trail
```

### User Journey
1. **Setup**: `docker-compose up -d` (ONE command)
2. **Upload**: POST to `/upload` endpoint
3. **Query**: POST to `/query` endpoint
4. **Receive**: Integrated response from ALL approaches

### Key Files
- `docker-compose.yml` - Defines complete system (10 services)
- `QUICK_START.md` - User deployment guide
- `NEWRAGCITY_ARCHITECTURE.md` - Complete system architecture
- `TheVault/run_vault.sh` - Alternative execution method
- `TheVault/pipeline/vault_main.yaml` - Integration pipeline

---

## WHEN TO READ THIS FILE

**ALWAYS read before**:
- Starting any task
- Responding to user requests
- Proposing implementation plans
- Creating new code or documentation
- Running tests or benchmarks

**ESPECIALLY read when**:
- User mentions "DKR", "Ersatz", or "RoT" individually
- User says "run benchmarks" or "test the system"
- You're about to create component-specific evaluators
- You catch yourself thinking "let's test X separately"
- User asks how to deploy or run newragcity

---

## DRIFT RECOVERY PROCEDURE

**If you detect drift in your own thinking**:
1. STOP immediately
2. Re-read this entire file
3. Re-answer the 4 drift detection questions
4. If still uncertain, ASK USER for clarification
5. Do NOT proceed until alignment confirmed

**If user detects drift and runs `/check-drift`**:
1. Acknowledge drift occurred
2. Read this file aloud (summarize key points)
3. Explain what you were doing wrong
4. Propose correct approach (unified system)
5. Ask user to confirm before proceeding

---

## ENFORCEMENT MECHANISMS

### 1. This File (MISSION_CRITICAL.md)
- Single source of truth
- Must read before ANY task
- Contains complete drift history

### 2. .claude/ALWAYS_READ.md
- Auto-injected context
- Reminds to read this file
- Quick drift check

### 3. /check-drift Slash Command
- User-invokable drift detector
- Forces automated drift check
- Reports findings to user

### 4. CLAUDE.md Checklist
- Mandatory pre-task checklist
- 5 verification questions
- Failure mode: Ask user

---

## SUCCESS METRICS

**You are on track when**:
- ✅ Working on docker-compose.yml-defined system
- ✅ Testing end-to-end query workflows
- ✅ Measuring integrated system performance
- ✅ Considering all 4 approaches together
- ✅ User feedback: "Yes, that's what I meant"

**You have drifted when**:
- ❌ Creating component-specific evaluators
- ❌ Proposing isolated component testing
- ❌ Treating DKR/Ersatz/RoT as separate apps
- ❌ Ignoring docker-compose.yml architecture
- ❌ User feedback: "That's not what I meant, we're a unified system"

---

## FINAL REMINDER

**newragcity = DKR + Ersatz + RoT + UltraRAG (TOGETHER)**

**NOT**: DKR (alone), Ersatz (alone), RoT (alone)

**This is ONE app, not four apps.**

**Users run**: `docker-compose up -d`
**NOT**: `python dkr_server.py`, `python ersatz_server.py`, `python rot_server.py`

**When in doubt**: Read this file again. Ask user for clarification.

---

**Document Status**: ✅ Active Guardrail
**Effectiveness**: Will be measured by zero future drifts
**Review**: After any drift incident or major system changes
