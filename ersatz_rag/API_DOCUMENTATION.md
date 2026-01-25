# ERSATZ RAG API Documentation

## Overview
ERSATZ RAG provides a comprehensive medical AI pipeline with real microservices for document intelligence, vector search, and confidence validation.

## Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PageIndex     │    │     LEANN       │    │   deepConf      │
│                 │    │                 │    │                 │
│ • Gemini Flash  │    │ • Qdrant DB     │    │ • Log-Prob      │
│ • Doc Structure │    │ • Vector Search │    │ • Confidence    │
│ • PDF Analysis  │    │ • Embeddings    │    │ • Validation    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Thalamus      │
                    │                 │
                    │ • Pipeline      │
                    │ • Orchestration │
                    │ • Q/A Engine    │
                    └─────────────────┘
```

## Service Endpoints

### PageIndex Service (Port 8000)
**Base URL:** `http://localhost:8000`

#### POST /extract_structure
Extract document structure and content using Gemini Flash 2.5.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (PDF file)

**Response:**
```json
{
  "structure": {
    "headers": ["Header 1", "Header 2"],
    "sections": ["Section 1", "Section 2"],
    "metadata": {
      "page_count": 10,
      "word_count": 2500
    }
  },
  "text": "Extracted document text...",
  "classification": "medical_policy"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/extract_structure" \
  -F "file=@document.pdf"
```

### LEANN Service (Port 8001)
**Base URL:** `http://localhost:8001`

#### POST /upsert
Store document chunks in vector database.

**Request:**
```json
{
  "chunks": [
    {
      "id": "chunk_1",
      "text": "Document content...",
      "metadata": {
        "document_type": "policy",
        "chunk_index": 0
      }
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Upserted 5 chunks"
}
```

#### POST /search
Search for similar content in vector database.

**Request:**
```json
{
  "query": "medical policy compliance",
  "limit": 5
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "chunk_1",
      "text": "Content...",
      "metadata": {...},
      "score": 0.85
    }
  ]
}
```

### deepConf Service (Port 8002)
**Base URL:** `http://localhost:8002`

#### POST /validate_confidence
Validate confidence for LLM responses.

**Request:**
```json
{
  "prompt": "What is the policy?",
  "context": "Relevant context...",
  "tokens": [
    {
      "token": "word",
      "logprob": -0.5
    }
  ]
}
```

**Response:**
```json
{
  "confidence_score": 0.85,
  "normalized_likelihood": 0.82,
  "validation_status": "high_confidence"
}
```

### Thalamus Service (Port 8003)
**Base URL:** `http://localhost:8003`

#### POST /process_pipeline
Execute complete medical AI pipeline.

**Request:**
```json
{
  "document_path": "/path/to/document.pdf",
  "qa_suite": [
    {
      "question": "What is the policy?",
      "expected_answer": "Policy details...",
      "complexity": "basic",
      "category": "policy_overview"
    }
  ],
  "document_name": "Policy Document"
}
```

**Response:**
```json
{
  "pipeline_architecture": "PageIndex_Real → LEANN_Real → DeepConf_Real → Enhanced_Gemini → DeepConf_Validation",
  "overall_accuracy": 0.95,
  "questions_above_95_percent": 8,
  "mandatory_component_benefits": {
    "pageindex_benefits_achieved": {
      "real_gemini_integration": true,
      "no_simulation_used": true
    },
    "leann_benefits_achieved": {
      "real_vector_storage": true,
      "qdrant_integration": true,
      "no_simulation_used": true
    },
    "deepconf_benefits_achieved": {
      "real_confidence_calculation": true,
      "no_simulation_used": true
    }
  }
}
```

## Error Handling

All services return standardized error responses:

```json
{
  "error": "Error description",
  "status_code": 500,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Common HTTP Status Codes
- `200`: Success
- `400`: Bad Request (invalid input)
- `422`: Validation Error (FastAPI)
- `500`: Internal Server Error
- `503`: Service Unavailable

## Authentication

Currently, services use environment variables for API keys:
- `GEMINI_API_KEY`: Google Gemini API access
- `MEDPLUM_CLIENT_ID`: Medplum API access (future)
- `PUBMED_API_KEY`: PubMed API access (future)

## Rate Limiting

- PageIndex: 10 requests/minute
- LEANN: 100 requests/minute
- deepConf: 50 requests/minute
- Thalamus: 5 pipeline runs/minute

## Data Formats

### Document Classification Types
- `clinical_record`: Patient medical records
- `administrative_policy`: Hospital policies
- `medical_bylaws`: Medical staff bylaws
- `research_paper`: Medical research papers

### Complexity Levels
- `basic`: Simple factual questions
- `intermediate`: Moderate analysis required
- `advanced`: Complex reasoning required

### Quality Metrics
- `content_quality_score`: 0.0-1.0
- `confidence_score`: 0.0-1.0
- `validation_accuracy`: 0.0-1.0

## Monitoring

### Health Endpoints
All services provide health check endpoints:
```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

### Metrics
- Request count and latency
- Error rates
- Resource utilization
- Pipeline performance metrics

## SDK Examples

### Python Client
```python
import requests

class ERSATZClient:
    def __init__(self, base_url="http://localhost"):
        self.pageindex = f"{base_url}:8000"
        self.leann = f"{base_url}:8001"
        self.deepconf = f"{base_url}:8002"
        self.thalamus = f"{base_url}:8003"

    def process_document(self, pdf_path, questions):
        # Upload document
        with open(pdf_path, 'rb') as f:
            files = {'file': f}
            pi_response = requests.post(f"{self.pageindex}/extract_structure", files=files)

        # Store in vector DB
        chunks = self._create_chunks(pi_response.json()['text'])
        requests.post(f"{self.leann}/upsert", json={"chunks": chunks})

        # Process Q/A pipeline
        pipeline_data = {
            "document_path": pdf_path,
            "qa_suite": questions,
            "document_name": "Test Document"
        }

        return requests.post(f"{self.thalamus}/process_pipeline", json=pipeline_data)
```

### JavaScript Client
```javascript
class ERSATZAPI {
    constructor(baseURL = 'http://localhost') {
        this.pageindexURL = `${baseURL}:8000`;
        this.leannURL = `${baseURL}:8001`;
        this.deepconfURL = `${baseURL}:8002`;
        this.thalamusURL = `${baseURL}:8003`;
    }

    async processDocument(file, questions) {
        // Extract structure
        const formData = new FormData();
        formData.append('file', file);

        const structure = await fetch(`${this.pageindexURL}/extract_structure`, {
            method: 'POST',
            body: formData
        });

        // Store chunks
        const chunks = this.createChunks(await structure.json());
        await fetch(`${this.leannURL}/upsert`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({chunks})
        });

        // Process pipeline
        const result = await fetch(`${this.thalamusURL}/process_pipeline`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                document_path: file.name,
                qa_suite: questions,
                document_name: file.name
            })
        });

        return result.json();
    }
}
```

## Troubleshooting

### Common Issues

1. **Service Unavailable**
   - Check Docker containers: `docker ps`
   - View logs: `./deploy.sh logs [service]`
   - Restart services: `./deploy.sh restart`

2. **API Key Errors**
   - Verify `.env` file exists and contains valid keys
   - Check API key permissions and quotas
   - Test API keys directly with provider

3. **Memory Issues**
   - Monitor Docker stats: `docker stats`
   - Increase Docker memory limits
   - Reduce batch sizes or concurrent requests

4. **Network Issues**
   - Check service connectivity: `curl http://localhost:8000/health`
   - Verify Docker network: `docker network ls`
   - Check firewall settings

### Debug Mode
Enable debug logging by setting environment variable:
```bash
LOG_LEVEL=DEBUG ./deploy.sh restart
```

## Version History

### v1.0.0 (Current)
- Real microservice architecture
- Gemini Flash 2.5 integration
- Qdrant vector database
- LLM confidence validation
- Docker containerization
- Comprehensive test suite

### Future Versions
- Medplum FHIR integration
- BioMCP medical literature search
- Kubernetes orchestration
- Advanced monitoring and alerting
- Multi-tenant support
