# Drift Mitigation & Rebuild Steps

**Created**: October 13, 2025  
**Purpose**: Document the architectural drift that occurred and provide a comprehensive recovery plan to restore alignment with the original design vision.

---

## Executive Summary

During Week 1 of the MVP build, significant architectural drift occurred. The implemented changes (LLM synthesis layer) were not aligned with the core "vectorless, deterministic RAG" philosophy documented in `AJrag.txt` and `agnoMCPnanobot.txt`. This document provides:

1. **Root Cause Analysis** of the drift
2. **Current State Assessment** of what was actually built
3. **Recovery Plan** with prioritized, actionable steps
4. **Alignment Checklist** to prevent future drift

---

## Part 1: Root Cause Analysis

### What Drift Occurred?

| Drift Area | What Was Implemented | What Should Have Been Built | Impact |
|------------|---------------------|----------------------------|--------|
| **Architecture Misunderstanding** | Added LLM synthesis as a "Week 1 MVP" feature, suggesting vector DB for "Week 2" | Should have focused on completing the **deterministic, vectorless** retrieval pipeline first | **High**: Violated core architectural principle |
| **Design Document Disconnect** | Made changes without first consulting `AJrag.txt` and `agnoMCPnanobot.txt` | All changes must reference design documents per `AGENTS.md` guidelines | **Critical**: Lost the "north star" |
| **Feature Prioritization Error** | Prioritized LLM answer generation over core TOC-driven routing | Should have built: Policy enforcement, Disambiguation rule engine, TOC Agent simulation | **Medium**: Built "nice-to-have" before "must-have" |
| **Testing Misalignment** | Created `test_llm_providers.py` focused on API key validation | Should have: Expanded TOC routing tests, added disambiguation rule tests, built AJ Pack round-trip tests per `AJrag.txt §8` | **Medium**: Test suite doesn't validate core features |

### Why Did This Happen?

1. **Lack of Design Document Review**: The assistant did not thoroughly review `AJrag.txt` and `agnoMCPnanobot.txt` before proposing solutions.
2. **Pattern Matching to Generic RAG**: The assistant defaulted to "typical RAG" patterns (vector search + LLM synthesis) instead of understanding the novel architecture.
3. **Incremental Optimization Trap**: Focused on making the existing `service.py` "better" rather than asking "is this aligned with the vision?"

---

## Part 2: Current State Assessment

### What Was Actually Built (and Is It Salvageable?)

#### ✅ **Good Additions (Keep & Integrate)**

1. **`llm_providers.py`** (100 lines)
   - **Status**: Well-architected, clean abstraction
   - **Alignment**: Matches the "Answer/Verifier Agent" concept from `agnoMCPnanobot.txt`
   - **Action**: **KEEP**. This is the synthesis layer for the eventual Answer Agent.

2. **`load_dotenv()` in `service.py`**
   - **Status**: Critical for loading API keys and environment config
   - **Alignment**: Matches security best practices from `AGENTS.md`
   - **Action**: **KEEP**.

3. **Updated `pydantic_schemas.py`**
   - **Status**: Added `QueryRequest`, `QueryResponse`, `SectionSummary`
   - **Alignment**: Follows data contract guidelines from `AGENTS.md`
   - **Action**: **KEEP**.

4. **Test Infrastructure Improvements**
   - **Status**: Tests now properly load environment variables
   - **Alignment**: Supports production-ready deployment
   - **Action**: **KEEP**.

#### ⚠️ **Problematic Changes (Needs Refactoring)**

1. **Modified `service.py` to use LLM synthesis**
   - **Issue**: The current implementation directly integrates the LLM into the query flow, making it the *primary* answer generation method. This bypasses the agent-based architecture.
   - **What It Should Be**: The LLM should be called by an "Answer/Verifier Agent," not directly in the endpoint.
   - **Action**: **REFACTOR**. Implement the Agent pattern from `doc_mcp_team.py` spec.

2. **`_build_context()` function placement**
   - **Issue**: This is a helper function inside the FastAPI app, not part of an agent.
   - **Action**: **MOVE** to a dedicated "Loader Agent" module.

#### ❌ **Missing Core Features (Critical Gaps)**

1. **No TOC Agent Implementation**
   - **Spec**: `agnoMCPnanobot.txt` lines 431-441 define a `TOC_Agent` with knowledge search tools.
   - **Current**: Only a simple `_apply_disambiguation()` function exists.
   - **Impact**: **Critical**. This is the "brain" of the routing system.

2. **No Policy Enforcement**
   - **Spec**: `AJrag.txt` §7 requires PHI/PII/residency enforcement.
   - **Current**: `SecurityMetadata` exists in schemas but is never checked.
   - **Impact**: **High**. Service could leak restricted data.

3. **No Loader Budget Management**
   - **Spec**: `AJrag.txt` §3.1 describes Loader-1 and Loader-2 agents that manage token budgets.
   - **Current**: Context is built without any budget awareness.
   - **Impact**: **Medium**. Could violate cost/performance targets.

4. **No Agentic Structure Audit**
   - **Spec**: `AJrag.txt` §2.2 step 5 describes a simulation that validates routing.
   - **Current**: No simulation or audit capability.
   - **Impact**: **Medium**. Can't validate that the system is working as designed.

---

## Part 3: Recovery Plan

### Guiding Principles for Recovery

1. **Design Documents Are Truth**: Every change must reference a section in `AJrag.txt` or `agnoMCPnanobot.txt`.
2. **Vectorless First**: Do not add vector search unless it's explicitly an *optional fallback*.
3. **Build Core, Then Polish**: Prioritize the TOC Agent, Loader Agents, and policy enforcement before optimizing answer quality.
4. **Test What Matters**: Focus tests on routing accuracy, disambiguation correctness, and policy compliance.

---

### Phase 1: Immediate Stabilization (1-2 days)

**Goal**: Stop the drift. Document current state. Restore confidence.

#### Step 1.1: Create Missing Design Alignment Tests

**Reference**: `AJrag.txt §8` - Testing & Quality Gates

**Action**: Create `tests/test_design_alignment.py`

```python
"""
Tests that validate the system matches AJrag.txt specifications.
These are NOT unit tests; they are design compliance checks.
"""

def test_toc_routing_matches_spec():
    """AJrag.txt §2.2: TOC routing must use aliases and disambiguation rules."""
    # Test that a query with "DKA" and "electrolytes" triggers the right section
    pass

def test_security_metadata_enforced():
    """AJrag.txt §7: PHI/PII/residency must be checked before returning answers."""
    # Test that a query for PHI-flagged data is blocked
    pass

def test_stable_citations():
    """AJrag.txt §9: Citations must be immutable section_ids."""
    # Test that section_ids don't change across ingestion runs
    pass
```

**Deliverable**: A failing test suite that defines what "success" looks like.

---

#### Step 1.2: Audit Current `service.py` Against Spec

**Action**: Create `docs/SERVICE_AUDIT.md`

Document every function in `service.py` and map it to the corresponding agent/concept in `agnoMCPnanobot.txt`.

| Function | Current Role | Spec Equivalent | Alignment Status |
|----------|-------------|-----------------|------------------|
| `_normalise()` | Tokenizes query | TOC Agent preprocessing | ✅ Aligned |
| `_apply_disambiguation()` | Applies TOC rules | TOC Agent routing logic | ✅ Aligned |
| `_alias_hits()`, `_entity_hits()` | Scoring | TOC Agent candidate ranking | ✅ Aligned |
| `llm_provider.generate()` | Direct LLM call | Answer/Verifier Agent | ❌ **Should be wrapped in Agent class** |
| `_build_context()` | Context assembly | Loader Agent | ❌ **Should be a separate Loader module** |

**Deliverable**: Clear understanding of what needs to be refactored.

---

### Phase 2: Implement Missing Core Features (1-2 weeks)

**Goal**: Build the agent-based architecture as designed.

#### Step 2.1: Implement Policy Enforcement

**Reference**: `AJrag.txt §7` - Security & Compliance

**Action**: Create `src/policy_enforcer.py`

```python
"""
Policy enforcement module.
Checks AJ Pack security metadata before allowing context loads.
"""

from pydantic_schemas import SecurityMetadata, AJPack

class PolicyEnforcer:
    """Enforces security policies defined in AJ Pack metadata."""
    
    def __init__(self, security_metadata: SecurityMetadata):
        self.metadata = security_metadata
    
    def check_residency(self, user_region: str) -> bool:
        """Check if user's region is allowed to access this data."""
        if self.metadata.residency and self.metadata.residency != user_region:
            return False
        return True
    
    def check_phi_access(self, user_has_phi_clearance: bool) -> bool:
        """Check if user is cleared for PHI data."""
        if self.metadata.phi and not user_has_phi_clearance:
            return False
        return True
    
    def enforce(self, user_region: str, user_has_phi_clearance: bool) -> tuple[bool, str]:
        """
        Enforce all policies. Returns (allowed, reason).
        """
        if not self.check_residency(user_region):
            return False, f"Data residency violation. Data is {self.metadata.residency}-only."
        
        if not self.check_phi_access(user_has_phi_clearance):
            return False, "PHI access denied. User lacks required clearance."
        
        return True, "Access granted."
```

**Integration**: Modify `service.py` to call `PolicyEnforcer.enforce()` before processing queries.

**Test**: Add `test_policy_enforcement.py` with cases for residency violations and PHI access denials.

**Deliverable**: Service rejects unauthorized queries with clear error messages.

---

#### Step 2.2: Build the TOC Agent (Simulation)

**Reference**: `agnoMCPnanobot.txt` lines 431-441

**Action**: Create `src/agents/toc_agent.py`

```python
"""
TOC Agent: Router and Oracle.
Uses the TOC to find the most relevant sections for a query.
"""

from pydantic_schemas import TOC, SectionTOC
from typing import List, Tuple

class TOCAgent:
    """
    The TOC Agent is responsible for:
    1. Understanding query intent
    2. Applying disambiguation rules
    3. Ranking candidate sections
    4. Recommending sections to the Loader Agent
    """
    
    def __init__(self, toc: TOC):
        self.toc = toc
    
    def route_query(self, query: str) -> List[Tuple[str, str, float]]:
        """
        Routes a query to the most relevant sections.
        
        Returns:
            List of (file_id, section_id, score) tuples, ranked by relevance.
        """
        # Use existing logic from service.py
        # This is the "simulation" version until we integrate Agno
        pass
```

**Integration**: Refactor `service.py` to instantiate `TOCAgent` and call `route_query()`.

**Test**: Add `test_toc_agent.py` with routing accuracy tests.

**Deliverable**: A clean separation between routing logic and API endpoints.

---

#### Step 2.3: Build the Loader Agent (Simulation)

**Reference**: `AJrag.txt §3.1` - Loader-1 / Loader-2

**Action**: Create `src/agents/loader_agent.py`

```python
"""
Loader Agent: Manages context under strict token budgets.
"""

class LoaderAgent:
    """
    Simulates the REQUEST_LOAD / RELEASE verbs from AJrag.txt.
    In production, this would coordinate with a cache.
    """
    
    def __init__(self, budget_tokens: int = 4000):
        self.budget = budget_tokens
        self.loaded_sections = {}
        self.current_usage = 0
    
    def request_load(self, file_id: str, section_id: str, content: str, token_estimate: int) -> bool:
        """
        Attempt to load a section into context.
        Returns True if successful, False if budget exceeded.
        """
        if self.current_usage + token_estimate > self.budget:
            return False
        
        self.loaded_sections[(file_id, section_id)] = content
        self.current_usage += token_estimate
        return True
    
    def get_context(self) -> str:
        """Return all loaded sections as a single context string."""
        return "\n\n".join(self.loaded_sections.values())
    
    def release(self, file_id: str, section_id: str):
        """Release a section from context."""
        if (file_id, section_id) in self.loaded_sections:
            # In a real implementation, we'd track token counts per section
            del self.loaded_sections[(file_id, section_id)]
```

**Integration**: Use `LoaderAgent` instead of `_build_context()`.

**Test**: Add `test_loader_agent.py` with budget enforcement tests.

**Deliverable**: Context loading respects token budgets.

---

#### Step 2.4: Wrap LLM in Answer/Verifier Agent

**Reference**: `agnoMCPnanobot.txt` lines 443-455

**Action**: Create `src/agents/answer_verifier_agent.py`

```python
"""
Answer/Verifier Agent: Synthesizes and verifies answers.
"""

from llm_providers import LLMProvider

class AnswerVerifierAgent:
    """
    The Answer/Verifier Agent:
    1. Receives context from the Loader Agent
    2. Synthesizes a comprehensive answer using an LLM
    3. Verifies the answer is fully supported by the context
    4. Generates citations
    """
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
    
    def synthesize_answer(self, query: str, context: str, citations: List[str]) -> dict:
        """
        Synthesize an answer and verify it's supported by the context.
        """
        answer = self.llm.generate(
            query=query,
            context=context,
            citations=citations,
            max_tokens=500
        )
        
        # TODO: Add verification logic (check that answer statements
        # are grounded in the provided context)
        
        confidence = self._calculate_confidence(answer, context)
        
        return {
            "answer": answer,
            "confidence": confidence,
            "citations": citations,
            "trace": "Answer synthesized by Answer/Verifier Agent"
        }
    
    def _calculate_confidence(self, answer: str, context: str) -> float:
        """Calculate confidence score based on answer-context alignment."""
        # Simplified confidence calculation
        # In production, this would use semantic similarity or fact-checking
        return 0.85
```

**Integration**: Refactor `service.py` to use `AnswerVerifierAgent` instead of calling `llm_provider` directly.

**Test**: Add `test_answer_verifier_agent.py`.

**Deliverable**: Clean agent-based architecture matching the design.

---

### Phase 3: Restore Testing Alignment (3-5 days)

**Goal**: Ensure test suite validates design compliance, not just code correctness.

#### Step 3.1: Implement AJrag.txt §8 Test Suite

**Reference**: `AJrag.txt §8` - Testing & Quality Gates

**Action**: Create the following test files:

1. `tests/test_schema_validation.py`
   - JSON Schema validation for AJ Packs
   - Pointer resolution checks
   - Manifest checksum verification

2. `tests/test_routing_accuracy.py`
   - Canonical intent → expected section mapping
   - Disambiguation rule correctness
   - Alias and entity hit accuracy

3. `tests/test_support_verification.py`
   - Answers must be fully supported by loaded context
   - Citation accuracy (section_ids match source)

4. `tests/test_performance_budgets.py`
   - p95 token load < 4000
   - Mean hops < 3
   - Context thrash < 5%

**Deliverable**: Test suite that validates the *design*, not just the code.

---

#### Step 3.2: Refactor Existing Tests

**Action**: Update `tests/test_llm_providers.py` to focus on **agent behavior**, not API keys.

**Current Problem**: Tests validate that providers can be instantiated with API keys. This is useful but not aligned with design goals.

**Better Approach**: Test that the `AnswerVerifierAgent` produces answers that meet quality thresholds.

```python
def test_answer_verifier_produces_supported_answers():
    """
    The Answer/Verifier Agent must only produce answers that are
    fully supported by the provided context.
    """
    agent = AnswerVerifierAgent(llm_provider=create_provider("mock"))
    
    context = "Metformin causes gastrointestinal side effects."
    query = "What are the side effects of Metformin?"
    
    result = agent.synthesize_answer(query, context, ["ch04_se2"])
    
    assert "gastrointestinal" in result["answer"].lower()
    assert result["confidence"] > 0.7
    assert "ch04_se2" in result["citations"]
```

**Deliverable**: Tests that validate agent behavior, not infrastructure.

---

### Phase 4: Documentation Synchronization (2-3 days)

**Goal**: Ensure all code changes are reflected in design documents.

#### Step 4.1: Update `AJrag.txt` with Implementation Notes

**Action**: Add a new section: `§10: Implementation Notes (Oct 2025)`

Document:
- What was built in `src/`
- Deviations from the original spec (if any)
- Lessons learned
- Known limitations

#### Step 4.2: Update `STATUS.md`

**Action**: Replace current content with:

```markdown
# Build Status Report (Updated: Oct 13, 2025)

## Current State
- ✅ AJ Pack schemas fully implemented and validated
- ✅ Deterministic, vectorless retrieval working as designed
- ✅ LLM synthesis layer added (Answer/Verifier Agent)
- ✅ Policy enforcement implemented (PHI/PII/residency checks)
- ✅ TOC Agent, Loader Agent, Answer/Verifier Agent architecture in place
- ⚠️ Agno AgentOS integration deferred (using simulation agents)
- ❌ Nanobot orchestrator not started
- ❌ Containerization not implemented

## Test Coverage
- ✅ Schema validation (round-trip AJ Packs)
- ✅ Routing accuracy (TOC disambiguation rules)
- ✅ Policy enforcement (security metadata checks)
- ✅ Performance budgets (token limits, hop counts)
- ⚠️ Support verification (partial - needs improvement)

## Next Steps (Priority Order)
1. Build the Nanobot orchestrator for fleet management
2. Implement containerization (Dockerfile + nanobot.yaml)
3. Integrate real Agno AgentOS (replace simulation agents)
4. Add support verification and confidence tuning
```

#### Step 4.3: Create Alignment Checklist

**Action**: Create `docs/ALIGNMENT_CHECKLIST.md`

```markdown
# Design Alignment Checklist

Use this checklist before implementing any new feature.

## Pre-Implementation
- [ ] I have read the relevant sections of `AJrag.txt`
- [ ] I have read the relevant sections of `agnoMCPnanobot.txt`
- [ ] I can cite which design section supports this change
- [ ] This change preserves the "vectorless first" principle
- [ ] This change maintains deterministic, auditable behavior

## Implementation
- [ ] Code is placed in the correct module per `AGENTS.md`
- [ ] Pydantic schemas updated if data contracts changed
- [ ] Agent responsibilities clearly defined in docstrings
- [ ] Stable IDs preserved (no breaking changes to section_ids)

## Testing
- [ ] Tests validate design compliance, not just code correctness
- [ ] Performance budgets checked (tokens, hops, thrash)
- [ ] Security policies tested (PHI/PII/residency)
- [ ] Citations are stable and traceable

## Documentation
- [ ] `STATUS.md` updated with current state
- [ ] Design docs updated if behavior changed
- [ ] Commit message references design section (e.g., "feat: implement TOC Agent per AJrag §3.1")
```

**Deliverable**: A checklist that prevents future drift.

---

## Part 4: Success Metrics

### How We'll Know the Drift is Resolved

1. **All Tests Reference Design Docs**
   - Every test file has a docstring citing the relevant `AJrag.txt` section.

2. **Service Matches Architecture Diagram**
   - `service.py` instantiates `TOCAgent`, `LoaderAgent`, and `AnswerVerifierAgent`.
   - No direct LLM calls in endpoints.

3. **100% Schema Compliance**
   - AJ Packs validate against the spec.
   - All section_ids are stable across runs.

4. **Policy Enforcement Active**
   - Queries for PHI-flagged data without clearance are rejected.
   - Residency violations return clear errors.

5. **Design Documents Synchronized**
   - `STATUS.md` accurately reflects what's built.
   - No code exists that isn't referenced in a design doc.

---

## Part 5: Preventing Future Drift

### Process Changes

1. **Mandatory Design Review**
   - Before implementing any feature, the implementer must:
     1. Read the relevant design doc section
     2. Write a 1-paragraph summary of what the design requires
     3. Get approval that the summary is correct

2. **Design-First Development**
   - New features start with a design doc update, not code.
   - Code changes that don't match any design doc are rejected.

3. **Weekly Alignment Audits**
   - Every week, run: `pytest tests/test_design_alignment.py`
   - If tests fail, stop new feature work and fix alignment first.

---

## Appendix A: File-by-File Recovery Actions

| File | Action | Priority | Estimated Effort |
|------|--------|----------|------------------|
| `src/service.py` | Refactor to use Agent classes | High | 4-6 hours |
| `src/llm_providers.py` | No changes needed | N/A | 0 hours |
| `src/pydantic_schemas.py` | No changes needed | N/A | 0 hours |
| `src/policy_enforcer.py` | **CREATE** | High | 2-3 hours |
| `src/agents/toc_agent.py` | **CREATE** | High | 4-6 hours |
| `src/agents/loader_agent.py` | **CREATE** | High | 3-4 hours |
| `src/agents/answer_verifier_agent.py` | **CREATE** | Medium | 2-3 hours |
| `tests/test_design_alignment.py` | **CREATE** | High | 3-4 hours |
| `tests/test_policy_enforcement.py` | **CREATE** | High | 2-3 hours |
| `tests/test_toc_agent.py` | **CREATE** | Medium | 2-3 hours |
| `tests/test_llm_providers.py` | Refactor to test agent behavior | Medium | 1-2 hours |
| `docs/ALIGNMENT_CHECKLIST.md` | **CREATE** | High | 1 hour |
| `docs/SERVICE_AUDIT.md` | **CREATE** | High | 2 hours |

**Total Estimated Effort**: 26-36 hours (3-5 working days for one person)

---

## Appendix B: Communication Plan

### Stakeholder Updates

**To Team**: "We've identified architectural drift. Here's what happened and how we're fixing it."

**To Leadership**: "The core product vision is sound. We've course-corrected and are now building exactly what was designed."

### Commit Message Format

All recovery commits should use this format:

```
fix(drift): [Component] - [Action] per [Design Doc Reference]

Example:
fix(drift): service.py - refactor to use TOCAgent per AJrag §3.1

- Moved routing logic from query() endpoint to TOCAgent class
- Added policy enforcement before query processing
- Updated tests to validate routing accuracy

Resolves: Drift recovery Phase 2, Step 2.2
```

---

## Conclusion

This drift was significant but recoverable. The good news:

1. **The design documents are excellent** - They provide a clear north star.
2. **The core architecture (AJ Pack, TOC, vectorless retrieval) is implemented** - This is the hardest part.
3. **The LLM integration, while misplaced, is salvageable** - It just needs to be wrapped in the Agent pattern.

By following this recovery plan, we will:
- Restore alignment with the original vision
- Build the agent-based architecture as designed
- Prevent future drift through process changes

**The project will be stronger for having identified and corrected this drift early.**

---

**Next Action**: Implement Phase 1, Step 1.1 - Create `tests/test_design_alignment.py`
