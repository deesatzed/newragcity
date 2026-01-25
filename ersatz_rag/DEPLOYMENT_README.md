# ERSATZ RAG - Deployment Guide

## Overview
ERSATZ RAG is a comprehensive medical AI pipeline with real microservices for document intelligence, vector search, and confidence validation.

## Architecture
- **PageIndex**: Gemini Flash 2.5 document structure extraction
- **LEANN**: Qdrant vector database with SentenceTransformers
- **deepConf**: LLM log-probability confidence calculation
- **Thalamus**: Medical AI pipeline orchestration
- **Qdrant**: Vector database backend

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.13+
- 4GB+ RAM recommended
- API keys (see Environment Setup)

### 1. Environment Setup
```bash
# Copy environment template
cp .env.example regulus/.env

# Edit with your API keys
nano regulus/.env
```

### 2. Full Deployment
```bash
# Make deployment script executable
chmod +x deploy.sh

# Deploy all services
./deploy.sh deploy
```

### 3. Verify Deployment
```bash
# Check service health
./deploy.sh status

# View logs
./deploy.sh logs

# Run tests
./deploy.sh test
```

## Service Endpoints

| Service | URL | Description |
|---------|-----|-------------|
| PageIndex | http://localhost:8000 | Document intelligence |
| LEANN | http://localhost:8001 | Vector operations |
| deepConf | http://localhost:8002 | Confidence validation |
| Thalamus | http://localhost:8003 | Medical AI pipeline |
| Qdrant | http://localhost:6333 | Vector database |

## Manual Service Management

### Build Services
```bash
./deploy.sh build
```

### Start Services
```bash
./deploy.sh start
```

### Stop Services
```bash
./deploy.sh stop
```

### Restart Services
```bash
./deploy.sh restart
```

### View Logs
```bash
# All services
./deploy.sh logs

# Specific service
./deploy.sh logs pageindex
```

## Testing

### Run Test Suite
```bash
./deploy.sh test
```

### Manual Testing
```bash
# Test PageIndex
curl -X POST "http://localhost:8000/extract_structure" \
  -F "file=@WS_ED/Acceptable Uses and Governance of Artificial Intelligence Policy_FINAL_2-14-24.pdf"

# Test LEANN
curl -X POST "http://localhost:8001/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "medical policy", "limit": 5}'

# Test deepConf
curl http://localhost:8002/health
```

## Configuration

### Environment Variables
See `.env.example` for all available configuration options.

### Required API Keys
- `GEMINI_API_KEY`: Google Gemini API key for document intelligence

### Optional API Keys (for future features)
- `MEDPLUM_CLIENT_ID`: Medplum FHIR API access
- `PUBMED_API_KEY`: PubMed literature search
- `CLINICALTRIALS_API_KEY`: ClinicalTrials.gov access

## Troubleshooting

### Service Won't Start
```bash
# Check logs
./deploy.sh logs [service_name]

# Check Docker containers
docker ps -a

# Check Docker logs
docker logs ersatz_rag_[service_name]
```

### Port Conflicts
```bash
# Check what's using ports
lsof -i :8000
lsof -i :8001
lsof -i :8002
lsof -i :8003
lsof -i :6333
```

### Memory Issues
```bash
# Check memory usage
docker stats

# Increase Docker memory limit in Docker Desktop settings
```

### API Key Issues
```bash
# Verify .env file
cat regulus/.env

# Test API key validity
curl -H "Authorization: Bearer $GEMINI_API_KEY" \
  "https://generativelanguage.googleapis.com/v1beta/models"
```

## Development

### Local Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Start individual services
cd pageindex_service && uvicorn app:app --port 8000
cd leann_service && uvicorn app:app --port 8001
cd deepconf_service && uvicorn app:app --port 8002
```

### Running Tests Locally
```bash
cd tests
pip install -r requirements.txt
python -m pytest -v
```

## Production Deployment

### Security Considerations
- Use environment variables for all secrets
- Implement API key rotation
- Use HTTPS in production
- Implement rate limiting
- Monitor service logs

### Scaling
- Services can be scaled independently
- Use Docker Swarm or Kubernetes for orchestration
- Implement load balancing
- Monitor resource usage

### Backup
```bash
# Backup Qdrant data
docker run --rm -v ersatz_rag_qdrant_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/qdrant_backup.tar.gz -C /data .
```

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review service logs with `./deploy.sh logs`
3. Verify configuration in `regulus/.env`
4. Ensure all prerequisites are installed
