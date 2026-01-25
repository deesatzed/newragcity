# Service.py Architecture Audit

**Date**: October 13, 2025  
**Purpose**: Map every function in `src/service.py` to the corresponding agent/concept in the design documents.

**References**:
- `AJrag.txt` - System blueprint
- `agnoMCPnanobot.txt` - Implementation spec

---

## Executive Summary

The current `service.py` implements a **fallback FastAPI service** that provides the core retrieval functionality without the full Agno AgentOS stack. It is a **simulation** of the agent-based architecture described in the design documents.

**Overall Alignment**: ⚠️ **Partially Aligned** (70%)

**Key Findings**:
- ✅ Core vectorless retrieval logic is correctly implemented
- ✅ TOC-driven routing with disambiguation rules works as designed
- ⚠️ LLM synthesis is present but not wrapped in an Agent class
- ❌ No policy enforcement (PHI/PII/residency checks)
- ❌ No loader budget management

---

## Function-by-Function Audit

### Module-Level Code

| Code Element | Current Implementation | Design Spec Reference | Alignment Status | Notes |
|--------------|----------------------|----------------------|------------------|-------|
| `load_dotenv()` | Loads environment variables from `.env` | `AGENTS.md` - Security best practices | ✅ **Aligned** | Critical for API key management |
| `llm_provider` initialization | Creates LLM provider at module load | `agnoMCPnanobot.txt` lines 443-455 (Answer/Verifier Agent) | ⚠️ **Partial** | Should be instantiated per-request or in an Agent class, not at module level |

**Recommendation**: Move `llm_provider` initialization into the `build_fallback_app()` function or into a dedicated Agent class.

---

### Helper Functions (Private)

#### `_normalise(text: str) -> Sequence[str]`

| Attribute | Value |
|-----------|-------|
| **Current Role** | Tokenizes query text into lowercase alphanumeric tokens |
| **Design Spec** | `agnoMCPnanobot.txt` lines 431-441 - TOC Agent preprocessing |
| **Alignment** | ✅ **Fully Aligned** |
| **Code Quality** | Clean, simple, deterministic |
| **Action Required** | None - keep as-is |

**Analysis**: This function is a perfect implementation of the "query normalization" step that the TOC Agent would perform. It's deterministic, fast, and follows the vectorless philosophy.

---

#### `_alias_hits(tokens: Sequence[str], aliases: Iterable[str]) -> int`

| Attribute | Value |
|-----------|-------|
| **Current Role** | Counts how many query tokens match section aliases |
| **Design Spec** | `AJrag.txt §2.2 Step 4` - TOC metadata with aliases |
| **Alignment** | ✅ **Fully Aligned** |
| **Code Quality** | Efficient set-based matching |
| **Action Required** | None - keep as-is |

**Analysis**: This implements the alias matching feature described in the design. The weighted scoring (alias hits × 3) gives appropriate priority to alias matches.

---

#### `_entity_hits(tokens: Sequence[str], entities: Iterable[str]) -> int`

| Attribute | Value |
|-----------|-------|
| **Current Role** | Counts how many query tokens match section entities |
| **Design Spec** | `AJrag.txt §2.2 Step 1` - Entity extraction and tagging |
| **Alignment** | ✅ **Fully Aligned** |
| **Code Quality** | Mirrors `_alias_hits()` pattern |
| **Action Required** | None - keep as-is |

**Analysis**: Correctly implements entity-based routing. Entities are a core part of the TOC metadata strategy.

---

#### `_text_hits(tokens: Sequence[str], text: str) -> int`

| Attribute | Value |
|-----------|-------|
| **Current Role** | Counts how many query tokens appear in section text |
| **Design Spec** | Implied by `AJrag.txt §3.1` - TOC Agent routing |
| **Alignment** | ✅ **Fully Aligned** |
| **Code Quality** | Simple keyword matching |
| **Action Required** | Consider adding TF-IDF weighting in Phase 2 |

**Analysis**: This is the baseline keyword matching. It's deterministic and fast, which aligns with the vectorless philosophy. Could be enhanced with TF-IDF for better accuracy.

---

#### `_apply_disambiguation(toc: TOC, tokens: Sequence[str]) -> List[Tuple[str, str]]`

| Attribute | Value |
|-----------|-------|
| **Current Role** | Applies TOC disambiguation rules to boost preferred sections |
| **Design Spec** | `AJrag.txt §5.2` - Disambiguation rules in TOC |
| **Alignment** | ✅ **Fully Aligned** |
| **Code Quality** | Clean implementation of rule matching |
| **Action Required** | None - this is a **novel, core feature** |

**Analysis**: This is one of the most important functions in the entire system. It implements the "smart routing" that makes the vectorless approach viable. The logic is:
1. Check if ALL triggers in a rule are present in the query
2. If yes, boost the preferred sections by +100 points

This is exactly as designed in `AJrag.txt §5.2`.

---

#### `_build_context(sections: List[Dict], all_ranked: List[Tuple]) -> str`

| Attribute | Value |
|-----------|-------|
| **Current Role** | Assembles context from top-ranked sections |
| **Design Spec** | `AJrag.txt §3.1` - Loader Agent `REQUEST_LOAD` verb |
| **Alignment** | ⚠️ **Partially Aligned** |
| **Code Quality** | Functional but lacks budget awareness |
| **Action Required** | **REFACTOR** - Move to dedicated Loader Agent module |

**Analysis**: This function does what a Loader Agent should do (assemble context), but it's missing critical features:
- ❌ No token budget enforcement
- ❌ No `REQUEST_LOAD` / `RELEASE` verb simulation
- ❌ No thrash detection

**Recommendation**: Create `src/agents/loader_agent.py` and move this logic there, adding budget management.

---

### Main Application Function

#### `build_fallback_app() -> FastAPI`

| Attribute | Value |
|-----------|-------|
| **Current Role** | Builds the FastAPI application with all endpoints |
| **Design Spec** | `agnoMCPnanobot.txt` - Doc-MCP Server architecture |
| **Alignment** | ⚠️ **Partially Aligned** |
| **Code Quality** | Well-structured but missing agent pattern |
| **Action Required** | **REFACTOR** - Implement agent-based architecture |

**Analysis**: This function is the heart of the fallback service. It correctly:
- ✅ Runs ingestion to create the AJ Pack
- ✅ Builds section and TOC indexes
- ✅ Exposes `/meta`, `/sections`, `/query`, `/health` endpoints

However, it's missing:
- ❌ Agent class instantiation (TOC Agent, Loader Agent, Answer/Verifier Agent)
- ❌ Policy enforcement before query processing
- ❌ Proper separation of concerns (routing, loading, synthesis)

---

### Endpoint Handlers

#### `GET /meta`

| Attribute | Value |
|-----------|-------|
| **Current Role** | Returns dataset metadata and ingestion warnings |
| **Design Spec** | `agnoMCPnanobot.txt` - Health/metrics endpoints |
| **Alignment** | ✅ **Fully Aligned** |
| **Action Required** | None |

---

#### `GET /sections`

| Attribute | Value |
|-----------|-------|
| **Current Role** | Lists all sections in the AJ Pack |
| **Design Spec** | Implied by MCP tool design |
| **Alignment** | ✅ **Aligned** |
| **Action Required** | None |

---

#### `POST /query`

| Attribute | Value |
|-----------|-------|
| **Current Role** | Main query endpoint - routes query and generates answer |
| **Design Spec** | `agnoMCPnanobot.txt` lines 99 - `atlas.ask()` tool |
| **Alignment** | ⚠️ **Partially Aligned** |
| **Action Required** | **REFACTOR** - Implement agent delegation pattern |

**Current Flow**:
1. Tokenize query
2. Apply disambiguation rules
3. Score all sections
4. Rank sections
5. **Directly call LLM** to generate answer
6. Return response

**Design Spec Flow** (`agnoMCPnanobot.txt` lines 461-469):
1. Delegate query to **TOC Agent** to identify sections
2. Delegate identified sections to **Answer/Verifier Agent** to synthesize answer
3. Format output with trace

**Gap Analysis**:
- ❌ No agent delegation
- ❌ No trace of agent actions
- ❌ LLM is called directly instead of through an Agent
- ❌ No policy enforcement before processing

**Critical Issue**: The current implementation bypasses the agent architecture entirely. While it works, it doesn't match the design's vision of a team of specialized agents collaborating.

---

#### `GET /health`

| Attribute | Value |
|-----------|-------|
| **Current Role** | Returns service health status |
| **Design Spec** | `agnoMCPnanobot.txt` line 100 - `atlas.health()` tool |
| **Alignment** | ✅ **Fully Aligned** |
| **Action Required** | None |

---

## Missing Components

### 1. Policy Enforcement

**Design Spec**: `AJrag.txt §7` - Security & Compliance

**Status**: ❌ **Not Implemented**

**Impact**: **Critical** - Service could leak PHI/PII data

**Evidence**:
```python
# Current code in /query endpoint:
# No check for security metadata before processing query
```

**Required Implementation**:
```python
# Before processing query:
policy_enforcer = PolicyEnforcer(aj_pack.toc.security)
allowed, reason = policy_enforcer.enforce(
    user_region=request.headers.get("X-User-Region", "UNKNOWN"),
    user_has_phi_clearance=request.headers.get("X-PHI-Clearance") == "true"
)
if not allowed:
    return QueryResponse(
        answer=f"Access denied: {reason}",
        citations=[],
        confidence=0.0,
        section_id="",
        label=""
    )
```

---

### 2. TOC Agent Class

**Design Spec**: `agnoMCPnanobot.txt` lines 431-441

**Status**: ❌ **Not Implemented** (logic exists but not wrapped in Agent class)

**Impact**: **High** - Architecture doesn't match design

**Current State**: Routing logic is scattered across helper functions

**Required Implementation**: Create `src/agents/toc_agent.py` with:
- `TOCAgent` class
- `route_query()` method that encapsulates all routing logic
- Clear interface for the team lead to call

---

### 3. Loader Agent Class

**Design Spec**: `AJrag.txt §3.1` - Loader-1 / Loader-2

**Status**: ❌ **Not Implemented**

**Impact**: **Medium** - No budget enforcement, potential cost overruns

**Current State**: `_build_context()` function has no budget awareness

**Required Implementation**: Create `src/agents/loader_agent.py` with:
- Token budget tracking
- `REQUEST_LOAD` / `RELEASE` verb simulation
- Thrash detection

---

### 4. Answer/Verifier Agent Class

**Design Spec**: `agnoMCPnanobot.txt` lines 443-455

**Status**: ⚠️ **Partially Implemented** (LLM synthesis exists but not wrapped)

**Impact**: **Medium** - Missing verification and confidence calculation

**Current State**: LLM is called directly in the query endpoint

**Required Implementation**: Create `src/agents/answer_verifier_agent.py` with:
- Answer synthesis
- Verification that answer is supported by context
- Confidence calculation
- Citation generation

---

## Scoring Summary

| Category | Score | Weight | Weighted Score |
|----------|-------|--------|----------------|
| **Core Retrieval Logic** | 95% | 30% | 28.5% |
| **TOC Routing** | 90% | 25% | 22.5% |
| **Agent Architecture** | 30% | 25% | 7.5% |
| **Security & Compliance** | 20% | 15% | 3.0% |
| **Testing & Validation** | 60% | 5% | 3.0% |
| **Overall** | - | - | **64.5%** |

---

## Recommendations (Prioritized)

### Priority 1: Critical (Must Fix Before Production)

1. **Implement Policy Enforcement**
   - **Effort**: 2-3 hours
   - **Impact**: Critical security gap
   - **Reference**: `Drift_Mitigation_ReBuild_Steps.md` Phase 2.1

2. **Create TOC Agent Class**
   - **Effort**: 4-6 hours
   - **Impact**: Architectural alignment
   - **Reference**: `Drift_Mitigation_ReBuild_Steps.md` Phase 2.2

### Priority 2: High (Needed for Design Compliance)

3. **Create Loader Agent Class**
   - **Effort**: 3-4 hours
   - **Impact**: Budget enforcement, cost control
   - **Reference**: `Drift_Mitigation_ReBuild_Steps.md` Phase 2.3

4. **Wrap LLM in Answer/Verifier Agent**
   - **Effort**: 2-3 hours
   - **Impact**: Verification, confidence scoring
   - **Reference**: `Drift_Mitigation_ReBuild_Steps.md` Phase 2.4

### Priority 3: Medium (Quality Improvements)

5. **Add TF-IDF Weighting to Text Scoring**
   - **Effort**: 2-3 hours
   - **Impact**: Improved retrieval accuracy
   - **Reference**: Future enhancement

6. **Implement Trace Logging**
   - **Effort**: 1-2 hours
   - **Impact**: Better observability
   - **Reference**: `agnoMCPnanobot.txt` line 103

---

## Conclusion

The current `service.py` is a **functional but incomplete** implementation of the Doc-MCP vision. It correctly implements the novel "vectorless, deterministic retrieval" core, but it lacks the agent-based architecture and security features described in the design documents.

**The good news**: The hardest part (the retrieval logic) is done and working well.

**The work ahead**: Wrapping this logic in the proper agent classes and adding policy enforcement.

**Estimated Total Effort**: 14-19 hours to reach full design compliance.

---

**Next Steps**: Proceed to Phase 2 of the drift mitigation plan to implement the missing components.
