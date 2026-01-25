# Hybrid Confidence Assessment

## Overview

The AJ Pack system uses **deterministic routing** (TF-IDF + metadata) as its primary mechanism. However, you can optionally enable **semantic validation** to improve confidence calibration.

## Architecture

```
Query: "What is the treatment for DKA?"
         ↓
┌────────────────────────────────────────────────┐
│ TOC Agent (Deterministic Routing)             │
│ - TF-IDF keyword matching                     │
│ - Alias matching (weight: 3)                  │
│ - Entity matching (weight: 1)                 │
│ - Disambiguation rules (+100)                 │
│ Result: Section "ch04_se2", Score: 85         │
└────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────┐
│ Confidence Validator (Optional)               │
│ - Calculate semantic similarity (embeddings)  │
│ - Compare with deterministic score            │
│ - Boost/reduce confidence based on agreement  │
│ Result: Combined confidence: 0.92             │
└────────────────────────────────────────────────┘
```

## Why Hybrid?

### Deterministic Routing (Primary)
✅ **Explainable**: "Matched because query contains 'DKA' (alias) and 'treatment' (text)"  
✅ **Reproducible**: Same query → Same results, always  
✅ **Auditable**: Complete trace of why section was selected  
✅ **Fast**: <10ms, no API calls  
✅ **Compliant**: No model drift, stable citations  

### Semantic Validation (Secondary)
✅ **Confidence calibration**: Validates routing decisions  
✅ **Edge case detection**: Flags potential routing errors  
✅ **Agreement scoring**: High agreement → boost confidence  
✅ **Conflict detection**: High keyword, low semantic → reduce confidence  

## Configuration

### Disable Semantic Validation (Default)

```bash
# .env file (or omit the variable entirely)
ENABLE_SEMANTIC_VALIDATION=false
```

**Result**: Pure deterministic routing. Confidence based only on TF-IDF scores.

### Enable Semantic Validation

```bash
# .env file
ENABLE_SEMANTIC_VALIDATION=true
```

**Requirements**:
```bash
pip install sentence-transformers
```

**Result**: Hybrid confidence assessment. Deterministic routing validated by semantic similarity.

## How It Works

### 1. Deterministic Score (Primary)

```python
# Query: "What is the treatment for DKA?"
# Section: "DKA Management" (aliases: ["DKA", "diabetic ketoacidosis"])

Score breakdown:
- Alias hit: "DKA" → +3 points
- Text hit: "treatment" → +2 points
- Text hit: "management" → +2 points
Total: 7 points

Deterministic confidence: 7 / 100 = 0.07 (normalized)
```

### 2. Semantic Similarity (Optional)

```python
# Calculate embedding similarity
query_embedding = encode("What is the treatment for DKA?")
section_embedding = encode("DKA Management: Initial therapy...")

semantic_similarity = cosine_similarity(query_embedding, section_embedding)
# Result: 0.82
```

### 3. Agreement Calculation

```python
deterministic = 0.85
semantic = 0.82
difference = |0.85 - 0.82| = 0.03

Agreement: HIGH (difference < 0.15)
```

### 4. Combined Confidence

```python
if agreement == 'high':
    # Both signals agree - boost confidence
    combined = deterministic * 0.7 + semantic * 0.3
    combined *= 1.1  # Small boost for agreement
    # Result: 0.92

elif agreement == 'conflict':
    # High keyword, low semantic - reduce confidence
    combined = min(deterministic, semantic) * 0.6
    # Flags potential routing error
```

## Agreement Levels

| Agreement | Condition | Action |
|-----------|-----------|--------|
| **High** | `|deterministic - semantic| < 0.15` | Boost confidence (+10%) |
| **Medium** | `|deterministic - semantic| < 0.30` | Use deterministic (slight semantic influence) |
| **Low** | `|deterministic - semantic| ≥ 0.30` | Reduce confidence (-15%) |
| **Conflict** | High deterministic, low semantic (or vice versa) | Significantly reduce confidence (-40%) |

## Example Scenarios

### Scenario 1: High Agreement (Ideal)

```
Query: "What are the electrolyte abnormalities in DKA?"
Section: "DKA Management - Electrolyte Replacement"

Deterministic: 0.88 (strong alias + text matches)
Semantic: 0.85 (high similarity)
Agreement: HIGH
Combined: 0.92 ✅ (boosted)
```

### Scenario 2: Conflict (Potential Error)

```
Query: "What is the prognosis for DKA?"
Section: "DKA Management - Initial Therapy"

Deterministic: 0.75 (matches "DKA" alias)
Semantic: 0.35 (section is about treatment, not prognosis)
Agreement: CONFLICT
Combined: 0.35 ⚠️ (significantly reduced)
```

This flags that while keywords match, the semantic content doesn't align with the query intent.

### Scenario 3: Low Agreement (Uncertainty)

```
Query: "How do I manage hyperglycemia?"
Section: "DKA Management"

Deterministic: 0.60 (matches "management", "hyperglycemia" in text)
Semantic: 0.40 (DKA is specific, query is general)
Agreement: LOW
Combined: 0.51 (moderately reduced)
```

## Performance Impact

| Mode | Latency | Cost | Model Drift Risk |
|------|---------|------|------------------|
| **Deterministic Only** | <10ms | $0 | None |
| **Hybrid (Semantic Enabled)** | 50-100ms | $0 (local model) | Low (model is frozen) |

**Note**: Semantic validation uses a local model (`all-MiniLM-L6-v2`), so there are no API costs.

## When to Enable Semantic Validation

### ✅ Enable When:
- You want improved confidence calibration
- You have queries with ambiguous keywords
- You want to detect routing edge cases
- Performance impact (50-100ms) is acceptable

### ❌ Disable When:
- Compliance requires pure deterministic routing
- You need <10ms latency
- You want zero model dependencies
- Explainability is paramount

## Monitoring

### Check Validation Status

```python
from src.agents.confidence_validator import create_confidence_validator

validator = create_confidence_validator()
print(validator.get_validation_summary())
# Output: "Semantic validation: ENABLED (model: all-MiniLM-L6-v2)"
```

### Validation Metadata

Each query returns validation metadata:

```json
{
  "answer": "...",
  "confidence": 0.92,
  "citations": ["ch04_se2"],
  "validation_metadata": {
    "deterministic_confidence": 0.85,
    "semantic_similarity": 0.82,
    "agreement": "high",
    "validation_enabled": true
  }
}
```

## Best Practices

1. **Start with deterministic only** - Validate that routing works correctly
2. **Enable semantic validation** - Improve confidence calibration
3. **Monitor agreement levels** - Track how often scores conflict
4. **Investigate conflicts** - High conflict rate may indicate metadata issues
5. **Tune thresholds** - Adjust agreement thresholds based on your domain

## Technical Details

### Model: all-MiniLM-L6-v2
- **Size**: 80MB
- **Speed**: ~50ms per query
- **Quality**: Good for general-purpose similarity
- **License**: Apache 2.0

### Why This Model?
- Lightweight and fast
- Good balance of quality and performance
- No API dependencies
- Widely used and validated

### Alternative Models

For better quality (slower):
```python
# In confidence_validator.py, change model:
self.model = SentenceTransformer('all-mpnet-base-v2')
```

For faster performance (lower quality):
```python
self.model = SentenceTransformer('all-MiniLM-L12-v2')
```

## Summary

**Hybrid confidence assessment gives you the best of both worlds:**

- ✅ **Deterministic routing** remains primary (explainable, auditable, compliant)
- ✅ **Semantic validation** improves confidence calibration
- ✅ **Optional** - disable for compliance-critical deployments
- ✅ **No API costs** - uses local model
- ✅ **Conflict detection** - flags potential routing errors

**Default behavior**: Semantic validation is **disabled**. The system works perfectly with pure deterministic routing.
