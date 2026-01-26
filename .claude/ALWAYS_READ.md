# ALWAYS READ FIRST

**This file is auto-injected into every Claude Code interaction**

---

## Before Responding to ANY User Request

**MANDATORY STEPS** (in order):

1. **Read `/Volumes/WS4TB/newragcity/UltraRAG-main/MISSION_CRITICAL.md`**
   - Contains absolute truths about what newragcity IS
   - Documents all 5 catastrophic drifts
   - Provides drift detection questions

2. **Answer the 4 Drift Detection Questions**:
   - Am I working on newragcity as a UNIFIED system? (YES required)
   - Am I treating components as separate apps? (NO required)
   - Would this make sense to an end user? (YES required)
   - Am I following docker-compose.yml? (YES required)

3. **If ANY Drift Detected**:
   - STOP immediately
   - Re-read MISSION_CRITICAL.md
   - Ask user for clarification
   - Do NOT proceed until alignment confirmed

---

## One-Line Truth

**newragcity = DKR + Ersatz + RoT + UltraRAG (TOGETHER as ONE unified system)**

**NOT**: DKR alone, Ersatz alone, RoT alone

---

## Quick Drift Check

**Are you about to**:
- ❌ Benchmark components individually?
- ❌ Implement component-specific evaluators?
- ❌ Test DKR/Ersatz/RoT in isolation?
- ❌ Ignore docker-compose.yml architecture?

**If YES to any** → DRIFT DETECTED → Read MISSION_CRITICAL.md

---

## Correct Patterns

**User says**: "Run the benchmarks"
**You think**: "Test the complete newragcity system end-to-end via docker-compose"

**User says**: "Test the system"
**You think**: "Start docker-compose up and run queries through unified API"

**User says**: "How does it work?"
**You think**: "Explain the unified system, not individual components"

---

## Recovery

**If user runs `/check-drift`**:
1. Acknowledge any drift
2. Read MISSION_CRITICAL.md aloud (summarize)
3. Propose correct unified approach
4. Wait for user confirmation

---

**Last Updated**: January 25, 2026
**Purpose**: Prevent treating newragcity as 4 separate apps when it is ONE unified system
