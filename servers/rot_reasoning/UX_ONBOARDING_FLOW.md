# RoT Onboarding & Usage Flow

**Updated**: January 24, 2026
**Version**: v0.2.0
**Status**: ✅ Implemented

---

## User Experience Flow

This document describes the complete user onboarding experience from git clone to chatbot integration.

### Overview

```
1. Git clone
   ↓
2. Run setup.py
   ↓
3. Preliminary install (fastmcp, PyYAML, requests)
   ↓
4. Interactive questions (framework, models, data folder)
   ↓
5. Full install via checklist (debug mode)
   ↓
6. Brief validation test
   ↓
7. Usage instructions (data folder, chatbot, REST API)
   ↓
8. Ready to use!
```

---

## Step-by-Step Flow

### Step 1: Git Clone

**User action**:
```bash
git clone https://github.com/YOUR_USERNAME/UltraRAG-main.git
cd UltraRAG-main/servers/rot_reasoning
```

**Time**: ~2-5 minutes (depending on connection)

---

### Step 2: Run Setup Script

**User action**:
```bash
python setup.py
# or with debug mode:
python setup.py --debug
```

**What happens**:
- Script displays welcome header
- Begins interactive setup wizard

**Time**: <1 second

---

### Step 3: Preliminary Install

**What the script does** (automatically, before asking questions):

```
[Step 0] Preliminary Setup
ℹ Installing preliminary dependencies...
ℹ This will install basic tools: fastmcp, PyYAML, requests
✓ Preliminary dependencies installed
```

**Why this matters**:
- Ensures all setup tools are available
- Fast install (3 small packages, ~10-30 seconds)
- Happens BEFORE user answers questions
- User doesn't need to pre-install anything

**Packages installed**:
- `fastmcp>=2.14.4` - MCP framework
- `pyyaml` - Configuration parsing
- `requests` - HTTP utilities

**Time**: 10-30 seconds

**Debug mode output**:
```
Debug: Installing packages: fastmcp>=2.14.4, pyyaml, requests
```

---

### Step 4: Interactive Questions

#### 4a. System Check

```
[Step 1] System Check
✓ Python 3.11 detected
ℹ OS: Darwin (arm64)
✓ Apple Silicon detected (Metal Performance Shaders available)
✓ Disk space: 250GB available
```

**What's checked**:
- Python version (3.11+ required)
- Operating system and architecture
- GPU availability (CUDA, MPS)
- Disk space (50GB minimum)

**Time**: <5 seconds

---

#### 4b. LLM Framework Selection

```
[Step 2] LLM Framework Selection

Which framework would you like to use?
  1. MLX-LM (recommended for Apple Silicon - fastest on M1/M2/M3)
  2. Ollama (easy setup, good compatibility)
  3. HuggingFace Transformers (most flexible)

Your choice [1-3] (default: 1):
```

**Frameworks offered**:

**On macOS Apple Silicon**:
1. MLX-LM (recommended) - Fastest on M1/M2/M3
2. Ollama - Easy setup
3. HuggingFace - Most flexible

**On other systems**:
1. Ollama (recommended) - Easiest setup, CPU/GPU
2. VLLM - Production, GPU-only, fastest inference
3. HuggingFace - Most flexible

**User selects**: One option (or accepts default)
**Time**: 5-10 seconds

---

#### 4c. Model Detection and Selection

```
[Step 3] Model Detection
ℹ Scanning for existing multimodal models...
✓ Found 2 multimodal model(s)

Select a model:
  1. Use qwen2.5-vl:7b (ollama)
  2. Use llava:latest (ollama)
  3. Download default: Qwen2.5-VL-7B-Instruct (recommended)
  4. Skip model setup (configure later)

Your choice [1-4] (default: 3):
```

**What happens**:
1. Script scans for existing models:
   - Ollama models (if Ollama selected)
   - HuggingFace cache models
   - MLX models (if MLX-LM selected)
2. Filters for **multimodal models only** (vision + language)
3. Presents choices:
   - Use existing model (if found)
   - Download default Qwen2.5-VL-7B-Instruct
   - Skip (configure later)

**User selects**: One option

**If download chosen**:
```
ℹ Downloading default model: Qwen2.5-VL-7B-Instruct
ℹ This is a ~15GB download and may take 15-60 minutes...
[Progress bar or status updates]
✓ Model downloaded successfully
```

**Time**:
- Model scan: 1-3 seconds
- User choice: 5-10 seconds
- Download (if needed): 15-60 minutes

---

#### 4d. Data Folder Configuration

```
[Step 4] Data Folder Configuration
ℹ Default data folder: /path/to/UltraRAG-main/servers/rot_reasoning/data
ℹ This folder will store your documents for RoT processing

Supported document types:
  ✓ Text: .txt, .md, .markdown, .rst
  ✓ PDF: .pdf (with text extraction)
  ✓ Office: .docx, .doc, .rtf
  ✓ Images: .png, .jpg, .jpeg, .webp (multimodal)
  ✓ Data: .json, .jsonl, .csv

Is this location okay for your documents? [Y/n]:
```

**What happens**:
1. Shows default data folder location
2. Lists all supported document types
3. Asks user to confirm or provide custom path
4. Creates folder if it doesn't exist
5. Checks for existing files

**If user provides custom path**:
```
Enter your data folder path (default: /path/to/data): /Users/me/Documents/my_data
✓ Data folder created: /Users/me/Documents/my_data
ℹ Data folder is empty. Add documents to get started!
```

**If folder has files**:
```
✓ Data folder created: /path/to/data
ℹ Found 5 existing file(s) in data folder
```

**Time**: 5-15 seconds

---

### Step 5: Full Installation

```
[Step 5] Installation (Full Setup)
ℹ Installing full setup (includes training dependencies)...
ℹ This may take 10-30 minutes depending on your connection.
ℹ Using uv for fast installation...
✓ Dependencies installed
```

**What's installed**:
- Core dependencies (PyTorch, Transformers, etc.)
- Training tools (DeepSpeed, accelerate)
- Framework-specific packages (MLX-LM, VLLM, etc.)

**Installation methods**:
1. If `uv` is available: Fast parallel installation
2. Otherwise: Standard pip installation

**Debug mode output**:
```
Debug: Installation checklist:
  [1/3] Installing core dependencies (PyTorch, Transformers, etc.)
  [2/3] Installing training tools (DeepSpeed, accelerate)
  [3/3] Installing mlx-specific packages

Debug: Using uv for fast installation
Debug: Running 'uv sync --all-extras'
✓ Dependencies installed
```

**Time**: 10-30 minutes (first time)

---

### Step 6: Configuration

```
[Step 6] Configuration
✓ Configuration saved to config.yaml
```

**What's created**:
```yaml
framework: ollama
model_path: ollama:qwen2.5-vl:7b
data_folder: /path/to/data
version: 0.2.0
```

**Time**: <1 second

---

### Step 7: Validation Tests

```
[Step 7] Validation
ℹ Running validation tests...
✓ MCP server imports successfully
✓ Basic functionality tests passed
```

**What's tested**:
1. MCP server can be imported
2. Basic functionality works (get_model_info, assess_complexity)
3. Server is ready for use

**If tests fail**:
```
⚠ Some tests failed, but server may still work
Continue with setup? [Y/n]:
```

**Time**: 5-10 seconds

---

### Step 8: Usage Instructions

The script displays comprehensive usage instructions for:

#### 8a. Claude Desktop Integration

```
[Step 1] Using with Claude Desktop (MCP)

Add this to your Claude Desktop config:

# macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
# Windows: %APPDATA%/Claude/claude_desktop_config.json

{
  "mcpServers": {
    "rot-reasoning": {
      "command": "python",
      "args": ["/path/to/src/rot_reasoning.py"],
      "env": {
        "DATA_FOLDER": "/path/to/data",
        "MODEL_PATH": "ollama:qwen2.5-vl:7b",
        "FRAMEWORK": "ollama"
      }
    }
  }
}

After adding, restart Claude Desktop. You'll see RoT tools available in the chat.
```

---

#### 8b. Data Folder Usage

```
[Step 2] Using with Your Data

Your data folder: /path/to/data

Supported document types:
  ✓ Text Documents: .txt, .md, .markdown, .rst
  ✓ PDF Documents: .pdf (with text extraction)
  ✓ Office Documents: .docx, .doc, .rtf
  ✓ Images: .png, .jpg, .jpeg, .webp (multimodal analysis)
  ✓ Structured Data: .json, .jsonl, .csv

Data folder location:
  Absolute path: /absolute/path/to/data

To use your data:
  1. Copy documents to the data folder
  2. RoT will automatically index and compress them
  3. Query via Claude Desktop or Python API
  4. Documents are processed with 3-4× compression for efficiency
```

**Key information provided**:
- All supported document types
- Absolute path to data folder
- How to use the data (4-step process)
- Compression benefits

---

#### 8c. REST API Chatbot Integration

```
[Step 3] Using with Chatbots (REST API)

RoT is an MCP server, but can be wrapped as a REST API for chatbot integration.

Quick REST API wrapper example:

Create rest_api_wrapper.py:

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
sys.path.insert(0, "src")
from rot_reasoning import _assess_complexity_impl, get_rot_compressor

app = FastAPI(title="RoT Reasoning API")

class QueryRequest(BaseModel):
    query: str
    context: list[str]
    max_tokens: int = 256

@app.post("/compress_and_generate")
async def compress_and_generate(req: QueryRequest):
    try:
        compressor = get_rot_compressor()
        result = await compressor.compress_and_generate(
            prompt=req.query,
            compressed_state=None,
            max_tokens=req.max_tokens
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/assess_complexity")
def assess_complexity(req: QueryRequest):
    return _assess_complexity_impl(req.query, req.context)

# Run: uvicorn rest_api_wrapper:app --reload --port 8000

Then integrate with your chatbot:
  POST http://localhost:8000/compress_and_generate
  POST http://localhost:8000/assess_complexity

For direct MCP integration:
  - Claude Desktop (native MCP support)
  - Any MCP-compatible client
  - Python API (see examples/example_usage.py)
```

**What this provides**:
- Complete working REST API wrapper code
- FastAPI-based implementation
- Two endpoints: compress_and_generate and assess_complexity
- Instructions to run the server
- Chatbot integration URLs

---

#### 8d. Testing and Examples

```
[Step 4] Testing and Examples

Run example usage:
  python examples/example_usage.py

Run benchmarks:
  python benchmarks/run_benchmarks.py --quick-test

Test with your own query:
  python src/rot_reasoning.py --query "Your question here"
```

---

#### 8e. Next Steps

```
[Step 5] Next Steps

To train a custom model:
  - See MODEL_TRAINING.md for detailed guide
  - Requires ~8-16 hours on GPU
  - Checkpoints will be saved to checkpoints/

Documentation:
  - QUICK_START.md - Tutorials and examples
  - BENCHMARK_PLAN.md - Evaluation and SOTA comparison
  - MODEL_SETUP.md - Advanced model configuration
  - TROUBLESHOOTING.md - Common issues and solutions
```

---

## Complete Flow Summary

```
┌──────────────────────────────────────────────────────────┐
│ Step 1: Git Clone                                        │
│   git clone https://github.com/.../UltraRAG-main         │
│   Time: 2-5 minutes                                      │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ Step 2: Run Setup                                        │
│   python setup.py                                        │
│   Time: <1 second                                        │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ Step 3: Preliminary Install (AUTOMATIC)                 │
│   ℹ Installing fastmcp, PyYAML, requests                │
│   ✓ Done                                                 │
│   Time: 10-30 seconds                                    │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ Step 4: Interactive Questions                            │
│   ├─ System check (automatic)                           │
│   ├─ Select framework (Ollama/MLX-LM/VLLM/HF)           │
│   ├─ Select model (existing or download Qwen2.5-VL)     │
│   └─ Configure data folder                              │
│   Time: 1-2 minutes (or 15-60 min if downloading model) │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ Step 5: Full Install (AUTOMATIC)                        │
│   ℹ Installing PyTorch, Transformers, DeepSpeed...      │
│   Time: 10-30 minutes                                    │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ Step 6: Configuration (AUTOMATIC)                       │
│   ✓ config.yaml created                                 │
│   Time: <1 second                                        │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ Step 7: Validation (AUTOMATIC)                          │
│   ✓ MCP server tests passed                             │
│   Time: 5-10 seconds                                     │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ Step 8: Usage Instructions (DISPLAYED)                  │
│   1. Claude Desktop MCP config                          │
│   2. Data folder usage (document types, location)       │
│   3. REST API chatbot integration                       │
│   4. Testing examples                                    │
│   5. Next steps (training, docs)                        │
│   Time: 2-5 minutes to read                             │
└──────────────────────────────────────────────────────────┘
                         ↓
                  ✅ READY TO USE!
```

---

## Time Estimates

**Minimum time** (all defaults, no model download, fast connection):
- Git clone: 2 min
- Preliminary install: 10 sec
- Questions: 30 sec (all defaults)
- Full install: 10 min
- Validation: 5 sec
- **Total**: ~12-13 minutes

**Typical time** (some customization, existing model):
- Git clone: 3 min
- Preliminary install: 20 sec
- Questions: 2 min (some interaction)
- Full install: 15 min
- Validation: 10 sec
- **Total**: ~20 minutes

**Maximum time** (custom settings, model download, slow connection):
- Git clone: 5 min
- Preliminary install: 30 sec
- Questions + model download: 60 min
- Full install: 30 min
- Validation: 10 sec
- **Total**: ~95 minutes (1.5 hours)

---

## Debug Mode

For troubleshooting, run with debug flag:

```bash
python setup.py --debug
```

**Additional debug output**:
```
Debug: Installing packages: fastmcp>=2.14.4, pyyaml, requests

Debug: Installation checklist:
  [1/3] Installing core dependencies (PyTorch, Transformers, etc.)
  [2/3] Installing training tools (DeepSpeed, accelerate)
  [3/3] Installing ollama-specific packages

Debug: Using uv for fast installation
Debug: Running 'uv sync --all-extras'
```

---

## Key UX Improvements

### Before (v0.1.0)
1. ❌ No setup script
2. ❌ Manual dependency installation (15+ commands)
3. ❌ No model detection
4. ❌ No data folder guidance
5. ❌ No chatbot integration examples
6. ❌ 5+ documents to read
7. ❌ 120+ minutes or never completes

### After (v0.2.0)
1. ✅ Single command: `python setup.py`
2. ✅ Automatic preliminary install (before questions)
3. ✅ Automatic model scanning and selection
4. ✅ Interactive data folder config with document types
5. ✅ Complete REST API wrapper example
6. ✅ All information in one flow
7. ✅ 12-95 minutes (average 20 minutes)

---

## Document Types Reference

### Supported Formats

**Text Documents**:
- `.txt` - Plain text files
- `.md`, `.markdown` - Markdown documents
- `.rst` - reStructuredText

**PDF Documents**:
- `.pdf` - Portable Document Format (with text extraction)

**Office Documents**:
- `.docx` - Microsoft Word (modern)
- `.doc` - Microsoft Word (legacy)
- `.rtf` - Rich Text Format

**Images** (multimodal analysis):
- `.png` - Portable Network Graphics
- `.jpg`, `.jpeg` - JPEG images
- `.webp` - WebP images

**Structured Data**:
- `.json` - JSON files
- `.jsonl` - JSON Lines (one JSON object per line)
- `.csv` - Comma-Separated Values

### Data Folder Location

**Default**: `<installation_directory>/data`
**Custom**: User can specify any absolute path
**Displayed**: Always shows absolute path for clarity

---

## Chatbot Integration Methods

### Method 1: Claude Desktop (MCP)
- **Best for**: Claude Desktop users
- **Setup**: Add JSON config to claude_desktop_config.json
- **Effort**: 1 minute (copy-paste)
- **Benefits**: Native integration, no code needed

### Method 2: REST API Wrapper
- **Best for**: Custom chatbots, non-MCP clients
- **Setup**: Create rest_api_wrapper.py with provided code
- **Effort**: 2-3 minutes (copy-paste, run uvicorn)
- **Benefits**: Works with any HTTP client, language-agnostic

### Method 3: Python API
- **Best for**: Python-based chatbots
- **Setup**: Import and use directly
- **Effort**: 5 minutes (see examples/example_usage.py)
- **Benefits**: Most flexible, no HTTP overhead

---

## Success Criteria

User should be able to:

1. ✅ Clone repository
2. ✅ Run one command (`python setup.py`)
3. ✅ Answer 3-4 simple questions
4. ✅ Wait for automatic installation
5. ✅ Receive complete usage instructions
6. ✅ Integrate with Claude Desktop OR chatbot via REST API
7. ✅ Start using RoT reasoning within 12-95 minutes

**Total user actions**: ~5-10 (down from 30+ in v0.1.0)
**Success rate target**: >95% of users complete setup
**User satisfaction**: "Professional, polished, production-ready"

---

**Document Version**: 1.0
**Created**: January 24, 2026
**Last Updated**: January 24, 2026
