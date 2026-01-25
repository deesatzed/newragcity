# newragcity Quick Start Guide

**Get up and running in 5-10 minutes!**

---

## Prerequisites

- **Docker** and **Docker Compose** installed ([Get Docker](https://docs.docker.com/get-docker/))
- **8GB RAM minimum** (16GB recommended)
- **20GB disk space** for Docker images and models
- **GPU optional** (NVIDIA GPU recommended for faster RoT reasoning, but CPU works fine)

---

## Quick Start (3 Steps)

### Step 1: Clone and Configure

```bash
# Clone the repository
git clone https://github.com/deesatzed/newragcity.git
cd newragcity

# Copy environment configuration
cp .env.example .env

# Edit .env with your text editor
nano .env  # or vim, code, etc.
```

**Minimum required**: Add your `OPENAI_API_KEY` (or leave empty to use local Ollama)

### Step 2: Start the System

```bash
# Start all services in the background
docker-compose up -d

# View logs to confirm services are starting
docker-compose logs -f
```

**Wait 2-3 minutes** for all services to initialize.

### Step 3: Initialize Ollama (If Using Local LLM)

```bash
# Pull the multimodal model for RoT reasoning
docker-compose exec ollama ollama pull qwen2.5-vl:7b

# This downloads ~4.5GB, takes 5-10 minutes
```

**Done!** Your system is ready.

---

## Access the System

### Web UI (Recommended)
Open your browser: **http://localhost:5050**

### REST API
Base URL: **http://localhost:8000**

---

## Try It Out

### 1. Upload a Document (Web UI)

1. Go to http://localhost:5050
2. Click "Upload Document"
3. Select a PDF, TXT, or DOCX file
4. Wait for processing (30 seconds - 2 minutes depending on size)
5. Document is now indexed and searchable!

### 2. Upload a Document (REST API)

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@my_document.pdf"
```

### 3. Query the System (Web UI)

1. Enter your question in the search box
2. Click "Search" or press Enter
3. View results with:
   - Answer with complete context
   - Confidence score
   - Source citations
   - Audit trail (which approaches were used)

### 4. Query the System (REST API)

```bash
# Simple query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the incident response procedure?"
  }'

# Query with confidence threshold
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain data sovereignty requirements",
    "confidence_threshold": 0.90
  }'

# Query with specific approach
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Find section 3.2.1",
    "approach": "dkr"
  }'
```

---

## Understanding Your Results

### Confidence Scores

Every response includes a confidence score (0.0-1.0):

| Score | Level | Meaning | Example Use Case |
|-------|-------|---------|------------------|
| **≥0.95** | 🔴 **Critical** | Safe for automated decisions | Medical diagnoses, legal advice |
| **≥0.85** | 🟠 **High** | Production-ready, verify for critical use | Compliance checks, policy answers |
| **≥0.70** | 🟡 **Medium** | Reasonable, requires verification | Research queries, general info |
| **0.50-0.70** | ⚪ **Low** | Significant uncertainty, use cautiously | Ambiguous questions |
| **<0.50** | ⚫ **Insufficient** | Too unreliable, system won't display | - |

### Approach Used (Audit Trail)

The system shows which approaches were used:

- **DKR** (Auditor): Exact/deterministic lookup was used
- **Ersatz** (Scholar): Semantic search with LEANN/PageIndex/deepConf
- **RoT** (Compressor): Complex reasoning with visual compression

**Example**:
```json
{
  "answer": "Incident response requires...",
  "confidence": 0.87,
  "sources": [
    "DKR:Manual#Section4.2",
    "Ersatz:Policy_v2.1#Chapter3"
  ],
  "audit_trail": {
    "dkr_used": true,
    "ersatz_used": true,
    "rot_used": false
  }
}
```

---

## Common Tasks

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ultrarag
docker-compose logs -f ersatz-server
docker-compose logs -f rot-server
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart ultrarag
```

### Stop the System

```bash
# Stop all services (keeps data)
docker-compose down

# Stop and remove all data (complete reset)
docker-compose down -v
```

### Update the System

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

### Monitor Resources

```bash
# View resource usage
docker stats

# View running containers
docker-compose ps
```

---

## Configuration Options

### Adjust Confidence Thresholds

Edit `.env`:
```bash
# Lower threshold for more results (may include uncertain answers)
CONFIDENCE_THRESHOLD=0.70

# Raise threshold for higher quality (fewer but more confident results)
CONFIDENCE_THRESHOLD=0.90
```

Restart services:
```bash
docker-compose restart
```

### Use Different LLM

#### Option 1: Use Claude (Anthropic)

Edit `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

#### Option 2: Use OpenRouter (Multiple Models)

Edit `.env`:
```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

#### Option 3: Use Different Ollama Model

```bash
# Pull different model
docker-compose exec ollama ollama pull llava:13b

# Update .env
MULTIMODAL_MODEL=llava:13b
```

Restart services:
```bash
docker-compose restart
```

### Adjust Logging

Edit `.env`:
```bash
# More detailed logs
LOG_LEVEL=debug

# Less verbose logs
LOG_LEVEL=warning
```

---

## Troubleshooting

### Services Won't Start

```bash
# Check logs for errors
docker-compose logs

# Ensure ports are not in use
sudo lsof -i :5050
sudo lsof -i :8000
sudo lsof -i :11434

# Restart Docker daemon
sudo systemctl restart docker  # Linux
# or restart Docker Desktop (macOS/Windows)
```

### "Out of Memory" Errors

Increase Docker memory limit:
- **Docker Desktop**: Settings → Resources → Memory → 8GB minimum

Or disable Ollama and use cloud API:
```yaml
# Comment out in docker-compose.yml
# ollama:
#   ...
```

Update `.env`:
```bash
OPENAI_API_KEY=your-key-here
MODEL_FRAMEWORK=openai
```

### Ollama Model Download Fails

```bash
# Retry pull
docker-compose exec ollama ollama pull qwen2.5-vl:7b

# Check available space
df -h

# Use smaller model if space limited
docker-compose exec ollama ollama pull llava:7b
```

### Slow Query Performance

**Normal latencies**:
- Exact lookup (DKR): <1 second
- Semantic search (Ersatz): 2-8 seconds
- Complex reasoning (RoT): 5-15 seconds

**If slower**:
1. Check `docker stats` for resource usage
2. Increase Docker CPU/memory allocation
3. Use GPU if available (edit docker-compose.yml)
4. Use cloud API instead of local Ollama

### "Insufficient Confidence" Responses

Your query threshold may be too high. Try:

1. **Lower threshold** in request:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "...",
    "confidence_threshold": 0.70
  }'
```

2. **Add more documents** with relevant information

3. **Rephrase query** to be more specific

### PostgreSQL Connection Errors

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres

# If persistent, reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
```

---

## Advanced Usage

### Batch Upload Documents

```bash
# Upload all PDFs in a directory
for file in /path/to/documents/*.pdf; do
  curl -X POST http://localhost:8000/upload \
    -F "file=@$file"
  echo "Uploaded: $file"
done
```

### Export Results

```bash
# Query and save to file
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "..."}' \
  > results.json
```

### Run Benchmarks

```bash
# Enter ultrarag container
docker-compose exec ultrarag bash

# Run benchmark suite
cd benchmarks
python run_benchmarks.py --quick-test

# Full benchmark (takes 30-60 minutes)
python run_benchmarks.py
```

---

## Next Steps

### 1. Read the Architecture Guide
**NEWRAGCITY_ARCHITECTURE.md** - Understand how all components work together

### 2. Customize for Your Use Case

- **Medical/Legal**: Set `DEVELOPER_THRESHOLD=0.98` for ultra-high confidence
- **Research**: Set `CONFIDENCE_THRESHOLD=0.70` for broader results
- **Code Documentation**: Enable code-aware PageIndex processing

### 3. Integrate with Your Application

See API documentation: **API_DOCUMENTATION.md** (coming soon)

### 4. Scale to Production

- Use PostgreSQL replication for high availability
- Add load balancer for multiple ultrarag instances
- Use external LLM API for better performance
- Configure monitoring and alerting

---

## Getting Help

### Documentation

- **NEWRAGCITY_ARCHITECTURE.md** - Complete system architecture
- **PROOF_OF_FUNCTIONALITY.md** - Test results and validation
- **README.md** - Project overview

### Community

- **GitHub Issues**: https://github.com/deesatzed/newragcity/issues
- **Discussions**: https://github.com/deesatzed/newragcity/discussions

### Debug Mode

Enable detailed logging:
```bash
# Edit .env
LOG_LEVEL=debug

# Restart
docker-compose restart

# View detailed logs
docker-compose logs -f
```

---

## Summary

**Minimum Setup** (No API keys required):
```bash
git clone https://github.com/deesatzed/newragcity.git
cd newragcity
cp .env.example .env
docker-compose up -d
docker-compose exec ollama ollama pull qwen2.5-vl:7b
# Open http://localhost:5050
```

**Recommended Setup** (With API keys for better performance):
```bash
git clone https://github.com/deesatzed/newragcity.git
cd newragcity
cp .env.example .env
nano .env  # Add OPENAI_API_KEY
docker-compose up -d
# Open http://localhost:5050
```

**You're ready to build powerful, confident RAG applications!** 🚀

---

**Last Updated**: January 25, 2026
**Version**: 1.0.0
