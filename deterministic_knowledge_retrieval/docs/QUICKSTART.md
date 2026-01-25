# Quick Start Guide

Get DKR (Deterministic Knowledge Retrieval) running in 5 minutes.

---

## Prerequisites

- Python 3.10 or higher
- `pip` or `conda`
- (Optional) OpenAI API key for LLM synthesis

---

## Installation

### Step 1: Clone and Setup Environment

```bash
# Clone the repository
cd /path/to/aMCPagnoBot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment (Optional)

Create a `.env` file:

```bash
# LLM Provider (default: mock - no API key needed)
LLM_PROVIDER=mock

# If using OpenAI:
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk-...

# If using Anthropic:
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=sk-ant-...

# Optional: Enable semantic validation
ENABLE_SEMANTIC_VALIDATION=false
```

**Note**: The system works perfectly with the mock provider (no API keys needed).

---

## Running the System

### Step 3: Run Tests

```bash
# Run all tests
pytest tests/ -v

# Expected output: 38 passed, 3 skipped
```

### Step 4: Start the Service

```bash
# Start the FastAPI server
uvicorn src.main:agent_os_app --reload

# Server starts at: http://localhost:8000
```

### Step 5: Query the System

```bash
# Example query (healthcare domain)
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -H "X-User-Region: US" \
  -H "X-PHI-Clearance: true" \
  -H "X-PII-Clearance: true" \
  -d '{
    "question": "What is the initial therapy for pneumonia?"
  }'
```

**Response**:
```json
{
  "answer": "Initial therapy for community-acquired pneumonia includes...",
  "citations": ["pneumonia_ch02_se1"],
  "confidence": 0.85,
  "section_id": "pneumonia_ch02_se1",
  "label": "Initial Therapy"
}
```

---

## API Endpoints

### 1. Query Endpoint

**`POST /query`**

Query the knowledge base with security headers.

**Headers**:
- `X-User-Region`: User's region (e.g., "US", "EU")
- `X-PHI-Clearance`: "true" if user can access PHI
- `X-PII-Clearance`: "true" if user can access PII

**Request**:
```json
{
  "question": "Your question here"
}
```

**Response**:
```json
{
  "answer": "Generated answer with citations",
  "citations": ["section_id_1", "section_id_2"],
  "confidence": 0.85,
  "section_id": "section_id_1",
  "label": "Section Label"
}
```

### 2. Metadata Endpoint

**`GET /meta`**

Get dataset metadata and ingestion warnings.

**Response**:
```json
{
  "dataset_id": "diabetes_handbook",
  "version": "1.0.0",
  "sections": "15",
  "warnings": []
}
```

### 3. Sections Endpoint

**`GET /sections`**

List all indexed sections.

**Response**:
```json
[
  {
    "section_id": "ch01_se1",
    "label": "Introduction",
    "file_id": "diabetes_handbook",
    "aliases": ["intro", "overview"],
    "entities": ["diabetes", "glucose"]
  }
]
```

### 4. Health Endpoint

**`GET /health`**

Check system health.

**Response**:
```json
{
  "status": "ok",
  "warnings": [],
  "sections": 15,
  "dataset_id": "diabetes_handbook",
  "version": "1.0.0"
}
```

---

## Adding Your Own Data

### Healthcare Domain

1. Create a JSON file following the infection disease format:

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

2. Place it in the project root (e.g., `your_condition.json`)

3. Restart the service - it will auto-discover and ingest the file

### Generic JSON Domain

1. Create a JSON file with sections:

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

2. Use the generic adapter:

```python
from src.domain_adapters import get_adapter

adapter = get_adapter('generic')
sections = adapter.extract_sections('my_knowledge.json')
```

---

## Testing Your Setup

### Test 1: Basic Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -H "X-User-Region: US" \
  -H "X-PHI-Clearance: true" \
  -H "X-PII-Clearance: true" \
  -d '{"question": "What is DKA?"}'
```

**Expected**: Answer about diabetic ketoacidosis with citations.

### Test 2: Policy Enforcement

```bash
# Query without clearance (should be denied)
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -H "X-User-Region: UNKNOWN" \
  -d '{"question": "What is DKA?"}'
```

**Expected**: "Access denied" message.

### Test 3: Health Check

```bash
curl http://localhost:8000/health
```

**Expected**: `{"status": "ok", ...}`

---

## Next Steps

1. **Read the Blog Post**: `docs/BLOG.md` - Deep dive into the architecture
2. **Multi-Domain Guide**: `docs/MULTI_DOMAIN.md` - Add new domains
3. **Hybrid Confidence**: `docs/HYBRID_CONFIDENCE.md` - Enable semantic validation
4. **Future Features**: `docs/UKP_FUTURE_FEATURES.md` - See what's coming

---

## Troubleshooting

### Issue: Tests Failing

**Solution**: Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: Import Errors

**Solution**: Make sure you're in the project root and virtual environment is activated:
```bash
source .venv/bin/activate
cd /path/to/aMCPagnoBot
```

### Issue: No Sections Found

**Solution**: Check that JSON files are in the project root and properly formatted:
```bash
ls *.json
pytest tests/test_data_loader.py -v
```

### Issue: Policy Violation Errors

**Solution**: Include required security headers in your requests:
```bash
-H "X-User-Region: US" \
-H "X-PHI-Clearance: true" \
-H "X-PII-Clearance: true"
```

---

## Performance Tips

1. **Use Mock Provider for Development**: No API costs, instant responses
2. **Enable Semantic Validation Selectively**: Only when you need confidence calibration
3. **Monitor Token Usage**: Check `/meta` endpoint for budget stats
4. **Cache Responses**: Implement caching layer for repeated queries

---

**You're ready to go! 🚀**

For more details, see the full documentation in `docs/`.
