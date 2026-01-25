# Document Ingestion to Retrieval: Complete Flow

**How documents become queryable knowledge in the UKP system**

---

## Overview

The UKP system transforms raw documents into queryable knowledge through a deterministic pipeline:

```
Raw Documents → JSON Extraction → Metadata Enrichment → UKP Format → Agent-Based Retrieval
```

---

## Phase 1: Document to JSON Conversion

### Input: Raw Documents

The system accepts documents in various formats depending on the domain adapter:

**Healthcare Domain**:
- Infection disease JSON files
- Clinical guidelines (PDF → JSON)
- Medical protocols (DOCX → JSON)

**Generic Domain**:
- Any JSON with `sections` array
- Array of objects
- Single object

**Future Domains**:
- Finance: 10-K filings, earnings reports (PDF/XLSX → JSON)
- Policy: Regulations, contracts (PDF/DOCX → JSON)
- Code: Source files (AST → JSON)

### Step 1.1: Domain Adapter Selection

```python
from src.domain_adapters import get_adapter

# Automatic selection based on domain
adapter = get_adapter('healthcare')  # or 'generic', 'finance', etc.
```

### Step 1.2: Section Extraction

The adapter extracts sections from the source document:

```python
# Example: Healthcare adapter
sections = adapter.extract_sections('pneumonia.json')

# Output: List of section dictionaries
[
  {
    'file_id': 'pneumonia',
    'section_id': 'pneumonia_ch01_se1',
    'label': 'Overview',
    'text': 'Pneumonia is an infection of the lungs...',
    'entities': [],  # Will be enriched
    'metadata': {}
  },
  {
    'file_id': 'pneumonia',
    'section_id': 'pneumonia_ch02_se1',
    'label': 'Initial Therapy',
    'text': 'Initial empiric therapy for community-acquired pneumonia...',
    'entities': [],
    'metadata': {}
  }
]
```

**Key Points**:
- Each section gets a unique `section_id` (stable, never changes)
- `file_id` identifies the source document
- `label` is human-readable
- `text` contains the full content (lossless)

---

## Phase 2: Metadata Enrichment

### Step 2.1: Entity Extraction

The adapter extracts domain-specific entities:

```python
sections = adapter.enrich_metadata(sections)

# Healthcare example:
{
  'section_id': 'pneumonia_ch02_se1',
  'entities': [
    'pneumonia',
    'empiric therapy',
    'community-acquired',
    'antibiotics',
    'ceftriaxone',
    'azithromycin'
  ]
}
```

**How it works**:
- Medical terms extracted from text
- Drug names identified
- Procedures and diagnoses tagged
- Domain-specific NER (Named Entity Recognition)

### Step 2.2: Alias Generation

Aliases are synonyms and abbreviations that improve routing:

```python
# Healthcare example:
{
  'section_id': 'diabetes_ch04_se2',
  'label': 'DKA Management',
  'aliases': [
    'DKA',
    'diabetic ketoacidosis',
    'ketoacidosis',
    'DKA treatment',
    'DKA therapy'
  ]
}
```

**Sources**:
- Expert-curated synonym lists
- Medical abbreviation databases
- Section labels and headings
- Common variations

### Step 2.3: Token Estimation

Each section's token count is estimated for budget management:

```python
from src.agents.loader_agent import estimate_tokens

token_estimate = estimate_tokens(section['text'])
# Simple heuristic: ~4 characters per token
# Production: Use tiktoken for accurate counts

section['token_estimate'] = token_estimate
```

---

## Phase 3: Universal Knowledge Pack (UKP) Creation

### Step 3.1: Build Table of Contents (TOC)

The TOC is the routing index:

```python
from src.pydantic_schemas import TOC, TOCNode

toc = TOC(
    sections=[
        TOCNode(
            file_id='pneumonia',
            section_id='pneumonia_ch02_se1',
            label='Initial Therapy',
            aliases=['initial treatment', 'empiric therapy', 'first-line'],
            entities=['pneumonia', 'antibiotics', 'ceftriaxone'],
            token_estimate=450
        ),
        # ... more sections
    ],
    disambiguation=[
        DisambiguationRule(
            if_all=['pneumonia', 'severe'],
            prefer=[('pneumonia', 'pneumonia_ch03_se1')]  # ICU management
        )
    ],
    security=SecurityMetadata(
        phi=True,
        pii=False,
        residency='US'
    )
)
```

**TOC Components**:
1. **Sections**: List of all addressable sections
2. **Disambiguation Rules**: Expert-defined routing preferences
3. **Security Metadata**: Access control policies

### Step 3.2: Build Manifest

The manifest describes the dataset:

```python
from src.pydantic_schemas import Manifest

manifest = Manifest(
    dataset_id='pneumonia_guidelines',
    version='1.0.0',
    description='Clinical guidelines for pneumonia management',
    created_at='2024-10-13T00:00:00Z'
)
```

### Step 3.3: Assemble Complete UKP

```python
from src.pydantic_schemas import AJPack

aj_pack = AJPack(
    manifest=manifest,
    toc=toc,
    sections=sections  # Full text content
)
```

**UKP Structure**:
```json
{
  "manifest": {
    "dataset_id": "pneumonia_guidelines",
    "version": "1.0.0",
    "description": "...",
    "created_at": "2024-10-13T00:00:00Z"
  },
  "toc": {
    "sections": [
      {
        "file_id": "pneumonia",
        "section_id": "pneumonia_ch02_se1",
        "label": "Initial Therapy",
        "aliases": ["initial treatment", "empiric therapy"],
        "entities": ["pneumonia", "antibiotics"],
        "token_estimate": 450
      }
    ],
    "disambiguation": [
      {
        "if_all": ["pneumonia", "severe"],
        "prefer": [["pneumonia", "pneumonia_ch03_se1"]]
      }
    ],
    "security": {
      "phi": true,
      "pii": false,
      "residency": "US"
    }
  },
  "sections": [
    {
      "file_id": "pneumonia",
      "section_id": "pneumonia_ch02_se1",
      "label": "Initial Therapy",
      "text": "Initial empiric therapy for community-acquired pneumonia..."
    }
  ]
}
```

---

## Phase 4: Query Processing & Retrieval

### Step 4.1: Policy Enforcement

**First line of defense**: Check security policies before routing.

```python
from src.policy_enforcer import PolicyEnforcer

policy_enforcer = PolicyEnforcer(aj_pack.toc.security)

# Extract user context from HTTP headers
user_region = request.headers.get('X-User-Region')  # "US"
user_has_phi = request.headers.get('X-PHI-Clearance') == 'true'
user_has_pii = request.headers.get('X-PII-Clearance') == 'true'

# Enforce policies
allowed, reason = policy_enforcer.enforce(
    user_region=user_region,
    user_has_phi_clearance=user_has_phi,
    user_has_pii_clearance=user_has_pii
)

if not allowed:
    return {"answer": f"Access denied: {reason}", "confidence": 0.0}
```

**Policy Checks**:
1. **Residency**: User region matches data residency requirement
2. **PHI**: User has clearance for Protected Health Information
3. **PII**: User has clearance for Personally Identifiable Information

### Step 4.2: TOC Agent Routing

**Deterministic routing** using TF-IDF + metadata.

```python
from src.agents.toc_agent import TOCAgent

toc_agent = TOCAgent(aj_pack.toc, sections)

# User query
query = "What is the initial therapy for pneumonia?"

# Route to best section
ranked_sections = toc_agent.route_query(query)
# Returns: [(file_id, section_id, score, section_metadata), ...]

best_file_id, best_section_id, best_score, best_section = ranked_sections[0]
```

**Routing Algorithm**:

```python
# 1. Normalize query
tokens = normalize(query)
# Result: ['initial', 'therapy', 'pneumonia']

# 2. Apply disambiguation rules
if all(trigger in tokens for trigger in ['pneumonia', 'severe']):
    boost_sections = [('pneumonia', 'pneumonia_ch03_se1')]
else:
    boost_sections = []

# 3. Score each section
for section in sections:
    # Text hits (weight: 2)
    text_score = count_matches(tokens, section['text']) * 2
    
    # Alias hits (weight: 3)
    alias_score = count_matches(tokens, section['aliases']) * 3
    
    # Entity hits (weight: 1)
    entity_score = count_matches(tokens, section['entities']) * 1
    
    # Disambiguation boost
    if section in boost_sections:
        disambiguation_boost = 100
    else:
        disambiguation_boost = 0
    
    total_score = text_score + alias_score + entity_score + disambiguation_boost

# 4. Sort by score (highest first)
ranked = sorted(sections, key=lambda s: s.score, reverse=True)
```

**Example Scoring**:
```
Query: "What is the initial therapy for pneumonia?"
Tokens: ['initial', 'therapy', 'pneumonia']

Section: pneumonia_ch02_se1 "Initial Therapy"
- Text hits: 'initial' (1), 'therapy' (1), 'pneumonia' (1) = 3 * 2 = 6
- Alias hits: 'initial therapy' (2 tokens) = 2 * 3 = 6
- Entity hits: 'pneumonia' (1) = 1 * 1 = 1
- Disambiguation: 0
- Total: 6 + 6 + 1 = 13

Section: pneumonia_ch03_se1 "ICU Management"
- Text hits: 'pneumonia' (1) = 1 * 2 = 2
- Alias hits: 0
- Entity hits: 'pneumonia' (1) = 1 * 1 = 1
- Disambiguation: 0
- Total: 2 + 0 + 1 = 3

Winner: pneumonia_ch02_se1 (score: 13)
```

### Step 4.3: Confidence Validation (Optional)

**Hybrid confidence** using semantic similarity.

```python
from src.agents.confidence_validator import create_confidence_validator

confidence_validator = create_confidence_validator()

# Validate routing decision
routing_confidence, validation_metadata = confidence_validator.validate_routing(
    query=query,
    section_text=best_section['text'],
    deterministic_score=best_score,
    section_label=best_section['label']
)
```

**Validation Process**:
```python
# 1. Normalize deterministic score
deterministic_confidence = min(1.0, best_score / 100.0)
# Result: 13 / 100 = 0.13

# 2. Calculate semantic similarity (if enabled)
if ENABLE_SEMANTIC_VALIDATION:
    semantic_similarity = calculate_embedding_similarity(query, section_text)
    # Result: 0.85 (high similarity)
    
    # 3. Check agreement
    agreement = calculate_agreement(deterministic_confidence, semantic_similarity)
    # Result: 'high' (both agree)
    
    # 4. Combine scores
    combined_confidence = deterministic_confidence * 0.7 + semantic_similarity * 0.3
    # Result: 0.13 * 0.7 + 0.85 * 0.3 = 0.35
else:
    combined_confidence = deterministic_confidence
```

### Step 4.4: Loader Agent Context Management

**Load section into context** under strict token budget.

```python
from src.agents.loader_agent import LoaderAgent, estimate_tokens

loader_agent = LoaderAgent(budget_tokens=4000)

# Clear previous context
loader_agent.clear()

# Load best section
token_estimate = best_section.get('token_estimate', estimate_tokens(best_section['text']))

success, reason = loader_agent.request_load(
    file_id=best_section['file_id'],
    section_id=best_section['section_id'],
    content=best_section['text'],
    token_estimate=token_estimate,
    metadata={'label': best_section['label']}
)

if success:
    # Get assembled context
    context = loader_agent.get_context()
    # Format: "[section_id] Label\nContent"
```

**Budget Management**:
```python
# Budget: 4000 tokens
# Section: 450 tokens
# Remaining: 3550 tokens

# Can load more sections if needed:
for file_id, section_id, score, section in ranked_sections[1:5]:
    token_estimate = section.get('token_estimate', 500)
    success, reason = loader_agent.request_load(
        file_id=file_id,
        section_id=section_id,
        content=section['text'],
        token_estimate=token_estimate,
        metadata={'label': section['label']}
    )
    if not success:
        break  # Budget exceeded
```

### Step 4.5: Answer/Verifier Agent Synthesis

**Generate and verify answer** using LLM.

```python
from src.agents.answer_verifier_agent import AnswerVerifierAgent

answer_agent = AnswerVerifierAgent(llm_provider)

# Synthesize answer with verification
result = answer_agent.synthesize_with_verification(
    query=query,
    context=context,
    citations=loader_agent.get_loaded_section_ids(),
    routing_confidence=routing_confidence,
    max_tokens=500
)

answer = result['answer']
confidence = result['confidence']
citations = result['citations']
```

**Synthesis Process**:
```python
# 1. Generate answer via LLM
answer = llm_provider.generate(
    query="What is the initial therapy for pneumonia?",
    context="[pneumonia_ch02_se1] Initial Therapy\nInitial empiric therapy...",
    citations=['pneumonia_ch02_se1'],
    max_tokens=500
)
# Result: "Initial empiric therapy for community-acquired pneumonia includes..."

# 2. Verify grounding
is_grounded, verification_confidence = verify_answer(answer, context)
# Checks: Answer words overlap with context words
# Result: is_grounded=True, verification_confidence=0.88

# 3. Combine confidences
combined_confidence = (
    verification_confidence * 0.6 +  # 0.88 * 0.6 = 0.528
    routing_confidence * 0.4          # 0.35 * 0.4 = 0.14
)
# Result: 0.668

# 4. Return result
return {
    'answer': answer,
    'confidence': 0.668,
    'citations': ['pneumonia_ch02_se1'],
    'metadata': {
        'routing_confidence': 0.35,
        'verification_confidence': 0.88,
        'combined_confidence': 0.668
    }
}
```

### Step 4.6: Response Assembly

**Final response** to user:

```json
{
  "answer": "Initial empiric therapy for community-acquired pneumonia includes beta-lactam antibiotics (such as ceftriaxone) combined with a macrolide (such as azithromycin). This combination provides coverage for typical and atypical pathogens.",
  "citations": ["pneumonia_ch02_se1"],
  "confidence": 0.668,
  "section_id": "pneumonia_ch02_se1",
  "label": "Initial Therapy"
}
```

---

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ 1. RAW DOCUMENT                                             │
│    pneumonia.json (infection disease format)               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. DOMAIN ADAPTER                                           │
│    HealthcareAdapter.extract_sections()                     │
│    → Parses JSON structure                                  │
│    → Extracts chapters and sections                         │
│    → Assigns stable section_ids                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. METADATA ENRICHMENT                                      │
│    HealthcareAdapter.enrich_metadata()                      │
│    → Extract entities (drugs, procedures, diagnoses)        │
│    → Generate aliases (abbreviations, synonyms)             │
│    → Estimate tokens                                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. UKP ASSEMBLY                                             │
│    → Build TOC (sections + disambiguation + security)       │
│    → Build Manifest (dataset_id, version, metadata)         │
│    → Create AJPack (manifest + toc + sections)              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. QUERY ARRIVES                                            │
│    POST /query {"question": "What is the initial therapy?"} │
│    Headers: X-User-Region, X-PHI-Clearance, X-PII-Clearance│
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. POLICY ENFORCEMENT                                       │
│    PolicyEnforcer.enforce()                                 │
│    → Check residency (US == US) ✓                          │
│    → Check PHI clearance (true == true) ✓                  │
│    → Check PII clearance (false, not required) ✓           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. TOC AGENT ROUTING                                        │
│    TOCAgent.route_query()                                   │
│    → Normalize: ['initial', 'therapy', 'pneumonia']         │
│    → Score sections: text + alias + entity + disambiguation │
│    → Rank: pneumonia_ch02_se1 (score: 13)                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 8. CONFIDENCE VALIDATION (Optional)                         │
│    ConfidenceValidator.validate_routing()                   │
│    → Deterministic: 0.13                                    │
│    → Semantic: 0.85 (if enabled)                            │
│    → Combined: 0.35                                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 9. LOADER AGENT                                             │
│    LoaderAgent.request_load()                               │
│    → Check budget: 450 tokens < 4000 ✓                     │
│    → Load section into context                              │
│    → Assemble context string                                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 10. ANSWER/VERIFIER AGENT                                   │
│     AnswerVerifierAgent.synthesize_with_verification()      │
│     → Generate answer via LLM                               │
│     → Verify grounding in context                           │
│     → Calculate combined confidence                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 11. RESPONSE                                                │
│     {                                                       │
│       "answer": "Initial empiric therapy...",               │
│       "citations": ["pneumonia_ch02_se1"],                  │
│       "confidence": 0.668                                   │
│     }                                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Takeaways

### 1. Lossless Transformation
- Original document → JSON → UKP (no information lost)
- Full text preserved in `sections`
- Metadata enriches without replacing

### 2. Deterministic Routing
- Same query → Same routing decision, always
- Explainable: "Matched 'initial therapy' alias (6 points)"
- No model drift, no black boxes

### 3. Policy-First Security
- Enforcement happens BEFORE routing
- Metadata-driven (baked into UKP)
- Impossible to bypass

### 4. Agent-Based Architecture
- Each agent has single responsibility
- Composable and testable
- Easy to extend and debug

### 5. Hybrid Confidence
- Deterministic routing (primary)
- Semantic validation (optional)
- Best of both worlds

---

## Adding Your Own Documents

### Step 1: Prepare Source Document

**Healthcare**:
```json
{
  "disease": "your_condition",
  "chapters": [
    {
      "chapter_number": 1,
      "title": "Overview",
      "sections": [
        {
          "section_number": 1,
          "heading": "Introduction",
          "content": "Your content here..."
        }
      ]
    }
  ]
}
```

**Generic**:
```json
{
  "dataset_id": "my_knowledge",
  "sections": [
    {
      "id": "sec1",
      "title": "Section Title",
      "content": "Your content here..."
    }
  ]
}
```

### Step 2: Run Ingestion

```python
from src.domain_adapters import get_adapter
from src.ingestion_workflow import run_ingestion_with_metadata

# Use appropriate adapter
adapter = get_adapter('healthcare')  # or 'generic'

# Run ingestion
aj_pack, warnings = run_ingestion_with_metadata('your_document.json')

# Check for warnings
if warnings:
    print(f"Warnings: {warnings}")
```

### Step 3: Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -H "X-User-Region: US" \
  -H "X-PHI-Clearance: true" \
  -H "X-PII-Clearance: true" \
  -d '{"question": "Your question here"}'
```

---

**The system is now fully documented from ingestion to retrieval!**
