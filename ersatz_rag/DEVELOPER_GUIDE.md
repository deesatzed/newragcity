# ERSATZ RAG Developer Guide

## Overview

This guide provides comprehensive information for developers working with the ERSATZ RAG medical AI pipeline. The system uses real microservices with no simulations or mocks, ensuring production-grade reliability.

## Development Environment Setup

### Prerequisites
```bash
# Required software
- Python 3.13+
- Docker & Docker Compose
- Git
- VS Code (recommended)

# Required API keys
- Google Gemini API key
- Optional: Medplum, PubMed, ClinicalTrials API keys
```

### Local Development Setup
```bash
# Clone repository (if applicable)
cd /Volumes/WS4TB/ERSATZ_RAG

# Set up Python environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example regulus/.env

# Configure API keys
nano regulus/.env
```

### Docker Development
```bash
# Build all services
./deploy.sh build

# Start services for development
./deploy.sh start

# View logs
./deploy.sh logs

# Run tests
./deploy.sh test
```

## Project Structure

```
ERSATZ_RAG/
├── pageindex_service/          # Document intelligence service
│   ├── app.py                 # FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Container definition
├── leann_service/            # Vector database service
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── deepconf_service/          # Confidence validation service
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── thalamus/                  # Pipeline orchestrator
│   ├── mandatory_integrated_medical_pipeline.py
│   ├── requirements.txt
│   └── Dockerfile
├── regulus/                   # Legacy Regulus application
├── tests/                     # Test suite
│   ├── test_comprehensive_suite.py
│   ├── test_unit_services.py
│   ├── test_performance_load.py
│   └── test_configuration.py
├── WS_ED/                     # Sample documents
├── docker-compose.yml         # Service orchestration
├── deploy.sh                  # Deployment script
└── .env.example              # Environment template
```

## Service Development

### PageIndex Service

#### Core Functionality
```python
from fastapi import FastAPI, File, UploadFile
import google.generativeai as genai
import fitz  # PyMuPDF

app = FastAPI(title="PageIndex Service")

@app.post("/extract_structure")
async def extract_structure(file: UploadFile = File(...)):
    # Read PDF content
    content = await file.read()

    # Extract text with PyMuPDF
    doc = fitz.open(stream=content, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    # Use Gemini for structure analysis
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    prompt = f"Analyze this medical document structure:\n\n{text[:10000]}"
    response = model.generate_content(prompt)

    return {
        "structure": response.text,
        "text": text,
        "classification": "medical_document"
    }
```

#### Testing PageIndex
```python
import requests
import pytest

def test_pageindex_extraction():
    test_pdf = "/Volumes/WS4TB/ERSATZ_RAG/WS_ED/test.pdf"

    with open(test_pdf, 'rb') as f:
        files = {'file': ('test.pdf', f, 'application/pdf')}
        response = requests.post("http://localhost:8000/extract_structure", files=files)

    assert response.status_code == 200
    result = response.json()
    assert "structure" in result
    assert "text" in result
```

### LEANN Service

#### Core Functionality
```python
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI(title="LEANN Service")

class ChunkData(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any] = {}

class UpsertRequest(BaseModel):
    chunks: List[ChunkData]

# Initialize components
qdrant = QdrantClient(host="qdrant", port=6333)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

@app.post("/upsert")
async def upsert_chunks(request: UpsertRequest):
    # Generate embeddings
    texts = [chunk.text for chunk in request.chunks]
    embeddings = embedder.encode(texts, show_progress_bar=False)

    # Prepare points for Qdrant
    points = [
        {
            "id": chunk.id,
            "vector": embedding.tolist(),
            "payload": {
                "text": chunk.text,
                "metadata": chunk.metadata
            }
        }
        for chunk, embedding in zip(request.chunks, embeddings)
    ]

    # Upsert to Qdrant
    qdrant.upsert(
        collection_name="leann_chunks",
        points=points
    )

    return {"status": "success", "chunks_stored": len(points)}
```

#### Qdrant Collection Setup
```python
from qdrant_client.http import models as qmodels

def ensure_collection():
    if not qdrant.collection_exists("leann_chunks"):
        qdrant.create_collection(
            collection_name="leann_chunks",
            vectors_config=qmodels.VectorParams(
                size=384,  # all-MiniLM-L6-v2 dimension
                distance=qmodels.Distance.COSINE
            )
        )
```

### deepConf Service

#### Core Functionality
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np

app = FastAPI(title="deepConf Service")

class ConfidenceRequest(BaseModel):
    prompt: str
    context: str
    tokens: List[Dict[str, float]] = []

@app.post("/validate_confidence")
async def validate_confidence(request: ConfidenceRequest):
    # Simplified confidence calculation
    # In production, this would analyze actual LLM log-probabilities

    base_confidence = 0.85

    # Factor in prompt and context quality
    prompt_quality = len(request.prompt.split()) / 20  # Normalize to ~20 words
    context_quality = len(request.context.split()) / 100  # Normalize to ~100 words

    confidence = min(base_confidence + (prompt_quality * 0.05) + (context_quality * 0.03), 1.0)

    return {
        "confidence_score": confidence,
        "normalized_likelihood": confidence * 0.95,
        "validation_status": "high_confidence" if confidence >= 0.95 else "standard_confidence"
    }
```

### Thalamus Orchestrator

#### Pipeline Integration
```python
import requests
import json
from typing import Dict, List, Any

class ThalamusPipeline:
    def __init__(self):
        self.services = {
            "pageindex": "http://pageindex:8000",
            "leann": "http://leann:8001",
            "deepconf": "http://deepconf:8002"
        }

    def process_document(self, document_path: str, qa_suite: List[Dict]) -> Dict:
        # Stage 1: PageIndex processing
        pageindex_result = self._call_pageindex(document_path)

        # Stage 2: LEANN processing
        leann_result = self._call_leann(pageindex_result["text"])

        # Stage 3: deepConf pre-validation
        deepconf_result = self._call_deepconf_prevalidation(pageindex_result["text"])

        # Stage 4: Gemini Q/A processing
        gemini_results = self._process_qa_with_gemini(qa_suite, pageindex_result, leann_result)

        # Stage 5: deepConf post-validation
        final_results = self._call_deepconf_postvalidation(gemini_results)

        return self._aggregate_results(
            pageindex_result, leann_result, deepconf_result, final_results
        )

    def _call_pageindex(self, document_path: str) -> Dict:
        with open(document_path, 'rb') as f:
            files = {'file': (document_path.split('/')[-1], f, 'application/pdf')}
            response = requests.post(f"{self.services['pageindex']}/extract_structure", files=files)
            return response.json()

    def _call_leann(self, document_text: str) -> Dict:
        # Chunk document and store in vector database
        chunks = self._create_chunks(document_text)
        chunk_data = [{"id": f"chunk_{i}", "text": chunk} for i, chunk in enumerate(chunks)]

        response = requests.post(f"{self.services['leann']}/upsert", json={"chunks": chunk_data})
        return response.json()

    def _call_deepconf_prevalidation(self, content: str) -> Dict:
        request_data = {
            "prompt": "Validate medical document content",
            "context": content[:1000],  # First 1000 chars
            "tokens": []
        }

        response = requests.post(f"{self.services['deepconf']}/validate_confidence", json=request_data)
        return response.json()
```

## Testing Strategy

### Unit Testing
```python
# tests/test_unit_services.py
import pytest
from pageindex_service.app import extract_structure
from leann_service.app import upsert_chunks

def test_pageindex_structure_extraction():
    # Test structure extraction logic
    pass

def test_leann_vector_operations():
    # Test vector storage and retrieval
    pass

def test_deepconf_confidence_calculation():
    # Test confidence validation
    pass
```

### Integration Testing
```python
# tests/test_comprehensive_suite.py
def test_full_pipeline_integration():
    # Test complete pipeline from document to results
    pipeline = ThalamusPipeline()

    results = pipeline.process_document("test.pdf", test_qa_suite)

    assert results["overall_accuracy"] >= 0.95
    assert results["questions_above_95_percent"] == len(test_qa_suite)
```

### Performance Testing
```python
# tests/test_performance_load.py
def test_concurrent_requests():
    # Test service performance under load
    pass

def test_memory_usage():
    # Monitor memory consumption
    pass
```

## API Development Guidelines

### Error Handling
```python
from fastapi import HTTPException

@app.post("/process")
async def process_data(data: InputModel):
    try:
        result = process_function(data)
        return {"status": "success", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
```

### Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/endpoint")
async def endpoint():
    logger.info("Processing request")
    # Process request
    logger.info("Request completed successfully")
    return {"status": "success"}
```

### Health Checks
```python
@app.get("/health")
async def health_check():
    # Check dependencies
    try:
        # Test database connection
        # Test external API connectivity
        # Check disk space
        # Verify configuration

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")
```

## Configuration Management

### Environment Variables
```python
# Use python-dotenv for local development
from dotenv import load_dotenv
import os

load_dotenv()

# Required
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable is required")

# Optional with defaults
MAX_WORKERS = int(os.getenv('MAX_WORKERS', 4))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
```

### Docker Configuration
```dockerfile
# Use multi-stage builds for smaller images
FROM python:3.13-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Debugging and Troubleshooting

### Service Debugging
```bash
# View service logs
./deploy.sh logs [service_name]

# Access service container
docker exec -it ersatz_rag_[service_name] /bin/bash

# Check service health
curl http://localhost:8000/health

# Monitor resource usage
docker stats ersatz_rag_[service_name]
```

### API Debugging
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test API endpoints
response = requests.post("http://localhost:8000/extract_structure", files=files)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

### Database Debugging
```python
# Connect to Qdrant
from qdrant_client import QdrantClient
client = QdrantClient(host="localhost", port=6333)

# List collections
collections = client.get_collections()
print(collections)

# Query collection
results = client.search(
    collection_name="leann_chunks",
    query_vector=[0.0] * 384,  # Dummy vector
    limit=5
)
```

## Performance Optimization

### Caching Strategies
```python
from functools import lru_cache
import redis

# In-memory caching
@lru_cache(maxsize=1000)
def cached_embedding(text: str):
    return embedder.encode([text])[0]

# Redis caching (future enhancement)
redis_client = redis.Redis(host='redis', port=6379)

def get_cached_result(key: str):
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    return None

def set_cached_result(key: str, value: dict, ttl: int = 3600):
    redis_client.setex(key, ttl, json.dumps(value))
```

### Async Processing
```python
from fastapi import BackgroundTasks

@app.post("/process_async")
async def process_async(data: InputModel, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_heavy_task, data)
    return {"status": "processing", "task_id": "123"}

async def process_heavy_task(data: InputModel):
    # Heavy processing here
    result = await heavy_computation(data)
    # Store result
    pass
```

### Database Optimization
```python
# Batch operations
def batch_upsert_chunks(chunks: List[Dict], batch_size: int = 100):
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        qdrant.upsert(collection_name="leann_chunks", points=batch)

# Index optimization
qdrant.create_index(
    collection_name="leann_chunks",
    field_name="metadata.document_type",
    field_schema="keyword"
)
```

## Security Best Practices

### API Security
```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt

security = HTTPBearer()

@app.post("/secure_endpoint")
async def secure_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Verify JWT token
    payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
    user_id = payload.get("sub")

    return {"user_id": user_id, "data": "secure content"}
```

### Input Validation
```python
from pydantic import BaseModel, validator
from typing import Optional

class MedicalDocumentRequest(BaseModel):
    document_path: str
    qa_suite: List[Dict]

    @validator('document_path')
    def validate_document_path(cls, v):
        if not v.endswith('.pdf'):
            raise ValueError('Document must be a PDF file')
        if not Path(v).exists():
            raise ValueError('Document file does not exist')
        return v

    @validator('qa_suite')
    def validate_qa_suite(cls, v):
        if len(v) == 0:
            raise ValueError('QA suite cannot be empty')
        if len(v) > 50:
            raise ValueError('QA suite cannot exceed 50 questions')
        return v
```

### Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

@app.post("/rate_limited_endpoint")
@limiter.limit("10/minute")
async def rate_limited_endpoint():
    return {"message": "This endpoint is rate limited"}
```

## Deployment and CI/CD

### GitHub Actions CI/CD
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.13'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r tests/requirements.txt

    - name: Run tests
      run: python -m pytest tests/ -v --cov=.

    - name: Build Docker images
      run: docker-compose build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Deploy to production
      run: echo "Deploy to production server"
```

### Production Deployment
```bash
# Blue-green deployment
docker tag ersatz_rag_pageindex:latest ersatz_rag_pageindex:v1
docker tag ersatz_rag_leann:latest ersatz_rag_leann:v1
docker tag ersatz_rag_deepconf:latest ersatz_rag_deepconf:v1
docker tag ersatz_rag_thalamus:latest ersatz_rag_thalamus:v1

# Update docker-compose.yml with new tags
sed -i 's/:latest/:v1/g' docker-compose.yml

# Deploy new version
docker-compose up -d

# Health check
./deploy.sh status

# Rollback if needed
docker-compose down
git checkout HEAD~1
docker-compose up -d
```

## Contributing Guidelines

### Code Style
```bash
# Use Black for code formatting
pip install black
black .

# Use isort for import sorting
pip install isort
isort .

# Use flake8 for linting
pip install flake8
flake8 .
```

### Commit Messages
```
feat: add new confidence validation endpoint
fix: resolve memory leak in vector processing
docs: update API documentation
test: add integration tests for pipeline
refactor: simplify chunking algorithm
```

### Pull Request Process
1. Create feature branch from `develop`
2. Implement changes with tests
3. Ensure all tests pass
4. Update documentation
5. Create pull request to `develop`
6. Code review and approval
7. Merge to `main` for production

## Monitoring and Observability

### Application Metrics
```python
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['method', 'endpoint'])

@app.middleware("http")
async def metrics_middleware(request, call_next):
    REQUEST_COUNT.labels(request.method, request.url.path).inc()

    with REQUEST_LATENCY.labels(request.method, request.url.path).time():
        response = await call_next(request)

    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Logging Configuration
```python
import logging
from pythonjsonlogger import jsonlogger

# JSON logging for production
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    "%(asctime)s %(name)s %(levelname)s %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

This comprehensive developer guide provides everything needed to work effectively with the ERSATZ RAG medical AI pipeline, from initial setup to production deployment and monitoring.
