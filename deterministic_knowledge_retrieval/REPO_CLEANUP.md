# Repository Cleanup Guide

**Preparing a clean repo for sharing and distribution**

---

## Files to KEEP (Essential for Running & Testing)

### Core Application Files

```
✅ src/                          # All source code
   ├── __init__.py
   ├── agents/                   # Agent modules
   │   ├── __init__.py
   │   ├── toc_agent.py
   │   ├── loader_agent.py
   │   ├── answer_verifier_agent.py
   │   └── confidence_validator.py
   ├── domain_adapters/          # Multi-domain support
   │   ├── __init__.py
   │   ├── base_adapter.py
   │   ├── healthcare_adapter.py
   │   ├── generic_adapter.py
   │   └── registry.py
   ├── pydantic_schemas.py       # Data contracts
   ├── ingestion_workflow.py     # Ingestion pipeline
   ├── data_loader.py            # Document loaders
   ├── policy_enforcer.py        # Security enforcement
   ├── llm_providers.py          # LLM abstraction
   ├── service.py                # FastAPI service
   └── main.py                   # Application entrypoint
```

### Test Suite

```
✅ tests/                        # All tests
   ├── __init__.py
   ├── test_data_loader.py
   ├── test_design_alignment.py
   ├── test_fallback_service.py
   ├── test_ingestion_workflow.py
   ├── test_llm_providers.py
   └── test_policy_enforcement.py
```

### Documentation

```
✅ docs/                         # All documentation
   ├── QUICKSTART.md             # Getting started
   ├── BLOG.md                   # Deep dive
   ├── MULTI_DOMAIN.md           # Multi-domain guide
   ├── HYBRID_CONFIDENCE.md      # Hybrid confidence
   ├── UKP_FUTURE_FEATURES.md    # Roadmap
   ├── INGESTION_TO_RETRIEVAL.md # Complete flow
   └── SERVICE_AUDIT.md          # Service audit
```

### Sample Data (Healthcare Domain)

```
✅ pneumonia.json                # Example infection disease data
✅ neutropenic_fever.json        # Example infection disease data
✅ meningitis.json               # Example infection disease data
✅ sepsis_unknown_origin.json   # Example infection disease data
✅ urinary_tract.json            # Example infection disease data
```

**Note**: Keep 3-5 sample JSON files for testing. Remove duplicates and backups.

### Configuration & Dependencies

```
✅ requirements.txt              # Python dependencies
✅ requirements-dev.txt          # Development dependencies
✅ .gitignore                    # Git ignore rules
✅ .env.example                  # Example environment config (create this)
```

### Design Documents

```
✅ README.md                     # Main readme
✅ AJrag.txt                     # System blueprint
✅ agnoMCPnanobot.txt            # Implementation spec
✅ domain_agnostic_knowledge_pack.md  # UKP vision
```

---

## Files to REMOVE (Not Needed for Clean Repo)

### Build Artifacts & Caches

```
❌ .DS_Store                     # macOS metadata
❌ .pytest_cache/                # Test cache
❌ .venv/                        # Virtual environment
❌ __pycache__/                  # Python cache (everywhere)
❌ *.pyc                         # Compiled Python
❌ /tmp/                         # Temporary files
```

### Old/Deprecated Folders

```
❌ atlasforge_consolidated/      # Old build artifacts
❌ atlasforge_mcp_integration/   # Old build artifacts
❌ atlasforge_os_enterprise_pack_hardened/  # Old build artifacts
❌ atlasforge_os_starter_next_steps/        # Old build artifacts
❌ atlasforge_os_starter_plus_autonomous/   # Old build artifacts
```

### Backup & Duplicate Files

```
❌ abx_SourceBU.json             # Backup file
❌ *BU.json                      # Any backup files
❌ *.backup                      # Backup files
❌ *.bak                         # Backup files
```

### Temporary/Status Files

```
❌ STATUS.md                     # Temporary status file
❌ AGENTS.md                     # Superseded by docs/
❌ Drift_Mitigation_ReBuild_Steps.md  # Internal planning doc
```

### Environment & Secrets

```
❌ .env                          # Contains secrets (create .env.example instead)
```

### Redundant Data Files

Keep only 3-5 representative samples. Remove:

```
❌ abx_Source.json               # Duplicate/large file
❌ abx_med_dose.json             # Duplicate/large file
❌ bite_wounds.json              # (keep if representative)
❌ central_line_infection.json   # (keep if representative)
❌ infected_diabetic_wound.json  # (keep if representative)
❌ infection_cap.json            # (keep if representative)
❌ intra-abdominal.json          # (keep if representative)
❌ septic_arthritis.json         # (keep if representative)
❌ skin_and_soft_tissue.json     # (keep if representative)
```

**Recommendation**: Keep `pneumonia.json`, `neutropenic_fever.json`, `meningitis.json`, `sepsis_unknown_origin.json`, `urinary_tract.json` as representative samples.

---

## Cleanup Commands

### Step 1: Remove Build Artifacts

```bash
# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete

# Remove test cache
rm -rf .pytest_cache/

# Remove virtual environment
rm -rf .venv/

# Remove macOS metadata
find . -name ".DS_Store" -delete

# Remove temporary files
rm -rf /tmp/
```

### Step 2: Remove Old Folders

```bash
# Remove old build artifacts
rm -rf atlasforge_consolidated/
rm -rf atlasforge_mcp_integration/
rm -rf atlasforge_os_enterprise_pack_hardened/
rm -rf atlasforge_os_starter_next_steps/
rm -rf atlasforge_os_starter_plus_autonomous/
```

### Step 3: Remove Backup Files

```bash
# Remove backup files
rm -f *BU.json
rm -f *.backup
rm -f *.bak
rm -f abx_SourceBU.json
```

### Step 4: Remove Temporary Docs

```bash
# Remove temporary/internal docs
rm -f STATUS.md
rm -f AGENTS.md
rm -f Drift_Mitigation_ReBuild_Steps.md
```

### Step 5: Create .env.example

```bash
# Create example environment file (without secrets)
cat > .env.example << 'EOF'
# LLM Provider Configuration
LLM_PROVIDER=mock  # Options: mock, openai, anthropic, ollama

# OpenAI Configuration (if using)
# OPENAI_API_KEY=sk-...

# Anthropic Configuration (if using)
# ANTHROPIC_API_KEY=sk-ant-...

# Ollama Configuration (if using)
# OLLAMA_BASE_URL=http://localhost:11434

# Optional: Enable semantic validation for hybrid confidence
ENABLE_SEMANTIC_VALIDATION=false  # Set to 'true' to enable
EOF

# Remove actual .env (contains secrets)
rm -f .env
```

### Step 6: Keep Representative Sample Data

```bash
# Keep only these sample files
KEEP_FILES=(
    "pneumonia.json"
    "neutropenic_fever.json"
    "meningitis.json"
    "sepsis_unknown_origin.json"
    "urinary_tract.json"
)

# Remove other JSON files (optional - adjust as needed)
# This is commented out - review and uncomment if desired
# for file in *.json; do
#     if [[ ! " ${KEEP_FILES[@]} " =~ " ${file} " ]]; then
#         echo "Removing: $file"
#         rm -f "$file"
#     fi
# done
```

---

## Final Clean Repo Structure

```
aMCPagnoBot/
├── .gitignore                   # Git ignore rules
├── .env.example                 # Example environment config
├── README.md                    # Main readme
├── AJrag.txt                    # System blueprint
├── agnoMCPnanobot.txt           # Implementation spec
├── domain_agnostic_knowledge_pack.md  # UKP vision
├── requirements.txt             # Dependencies
├── requirements-dev.txt         # Dev dependencies
│
├── docs/                        # Documentation
│   ├── QUICKSTART.md
│   ├── BLOG.md
│   ├── MULTI_DOMAIN.md
│   ├── HYBRID_CONFIDENCE.md
│   ├── UKP_FUTURE_FEATURES.md
│   ├── INGESTION_TO_RETRIEVAL.md
│   └── SERVICE_AUDIT.md
│
├── src/                         # Source code
│   ├── __init__.py
│   ├── agents/
│   ├── domain_adapters/
│   ├── pydantic_schemas.py
│   ├── ingestion_workflow.py
│   ├── data_loader.py
│   ├── policy_enforcer.py
│   ├── llm_providers.py
│   ├── service.py
│   └── main.py
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── test_data_loader.py
│   ├── test_design_alignment.py
│   ├── test_fallback_service.py
│   ├── test_ingestion_workflow.py
│   ├── test_llm_providers.py
│   └── test_policy_enforcement.py
│
└── Sample Data (3-5 JSON files)
    ├── pneumonia.json
    ├── neutropenic_fever.json
    ├── meningitis.json
    ├── sepsis_unknown_origin.json
    └── urinary_tract.json
```

---

## Verification Checklist

After cleanup, verify the repo is ready:

### ✅ 1. No Secrets

```bash
# Check for API keys
grep -r "sk-" . --exclude-dir=.git --exclude-dir=.venv
grep -r "API_KEY" . --exclude-dir=.git --exclude-dir=.venv --exclude=".env.example"

# Should only find .env.example (commented out)
```

### ✅ 2. No Build Artifacts

```bash
# Check for cache directories
find . -type d -name "__pycache__" -o -name ".pytest_cache"

# Should return nothing
```

### ✅ 3. Tests Pass

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Should see: 38 passed, 3 skipped
```

### ✅ 4. Service Starts

```bash
# Start service
uvicorn src.main:agent_os_app --reload

# Should start without errors
```

### ✅ 5. Documentation Complete

```bash
# Check all docs exist
ls docs/QUICKSTART.md
ls docs/BLOG.md
ls docs/MULTI_DOMAIN.md
ls docs/HYBRID_CONFIDENCE.md
ls docs/UKP_FUTURE_FEATURES.md
ls docs/INGESTION_TO_RETRIEVAL.md

# All should exist
```

### ✅ 6. Sample Data Works

```bash
# Test ingestion
curl http://localhost:8000/meta

# Should return dataset info with sections
```

---

## Creating Distribution Archive

### Option 1: Git Repository

```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: UKP System v1.0"

# Push to GitHub/GitLab
git remote add origin <your-repo-url>
git push -u origin main
```

### Option 2: ZIP Archive

```bash
# Create clean archive
cd ..
zip -r ukp-system-v1.0.zip aMCPagnoBot/ \
    -x "*.pyc" \
    -x "*__pycache__*" \
    -x "*.DS_Store" \
    -x ".venv/*" \
    -x ".pytest_cache/*" \
    -x ".env"
```

---

## Post-Cleanup Instructions for Users

Include this in your README or QUICKSTART:

```markdown
## Installation

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd aMCPagnoBot
   ```

2. Create virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your API keys if using OpenAI/Anthropic
   ```

5. Run tests:
   ```bash
   pytest tests/ -v
   ```

6. Start the service:
   ```bash
   uvicorn src.main:agent_os_app --reload
   ```

7. Query the system:
   ```bash
   curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -H "X-User-Region: US" \
     -H "X-PHI-Clearance: true" \
     -H "X-PII-Clearance: true" \
     -d '{"question": "What is the treatment for pneumonia?"}'
   ```
```

---

## Summary

**Total Size After Cleanup**: ~5-10 MB (vs ~500+ MB with old artifacts)

**Files Removed**: ~50+ unnecessary files and folders

**Result**: Clean, professional, shareable repository ready for distribution

---

**Last updated**: 2025-10-13
