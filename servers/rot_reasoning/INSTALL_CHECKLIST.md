# RoT Reasoning Server - Installation Checklist

**Version**: v0.2.0
**Date**: January 24, 2026
**Estimated Time**: 30-60 minutes (depending on internet speed and GPU drivers)

---

## Prerequisites Checklist

### System Requirements

- [ ] **Python 3.11 or 3.12** installed
  ```bash
  python3 --version  # Should show 3.11.x or 3.12.x
  ```

- [ ] **Git** installed (for cloning repositories)
  ```bash
  git --version
  ```

- [ ] **uv** package manager installed (recommended)
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  uv --version
  ```

- [ ] **GPU (Optional but Recommended)**
  - NVIDIA GPU with 8GB+ VRAM for model training
  - CUDA 11.8 or 12.1 installed
  - CPU-only mode works but is slower

- [ ] **Disk Space**
  - 10GB for dependencies
  - 50GB+ for LLM models (Qwen2.5-VL-7B, DeepSeek-OCR)
  - 20GB+ for training checkpoints

---

## Installation Steps

### Step 1: Clone Repository

- [ ] Navigate to workspace
  ```bash
  cd /Volumes/WS4TB/newragcity
  ```

- [ ] Verify UltraRAG repository exists
  ```bash
  ls -la UltraRAG-main/
  ```

- [ ] Navigate to RoT server directory
  ```bash
  cd UltraRAG-main/servers/rot_reasoning
  ```

### Step 2: Python Environment Setup

Choose **ONE** method:

#### Option A: Using uv (Recommended)

- [ ] Initialize uv environment
  ```bash
  uv sync
  ```

- [ ] Verify environment created
  ```bash
  uv run python --version
  ```

#### Option B: Using venv

- [ ] Create virtual environment
  ```bash
  python3 -m venv venv
  ```

- [ ] Activate environment
  ```bash
  source venv/bin/activate  # macOS/Linux
  # OR
  venv\Scripts\activate     # Windows
  ```

- [ ] Install dependencies
  ```bash
  pip install -r requirements.txt
  ```

#### Option C: Using Docker (See Dockerfile section)

- [ ] Build Docker image (see Step 6)

### Step 3: Core Dependencies Verification

- [ ] Verify fastmcp installed
  ```bash
  uv run python -c "import fastmcp; print('fastmcp:', fastmcp.__version__)"
  # OR
  python -c "import fastmcp; print('fastmcp:', fastmcp.__version__)"
  ```

- [ ] Verify PyTorch installed
  ```bash
  uv run python -c "import torch; print('PyTorch:', torch.__version__)"
  ```

- [ ] Verify CUDA available (if using GPU)
  ```bash
  uv run python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
  ```

- [ ] Verify Transformers installed
  ```bash
  uv run python -c "import transformers; print('Transformers:', transformers.__version__)"
  ```

### Step 4: LLM Model Setup

See [MODEL_SETUP.md](MODEL_SETUP.md) for detailed model download and configuration.

- [ ] Choose model source:
  - [ ] **Option A**: HuggingFace (requires HF account and token)
  - [ ] **Option B**: Ollama (simpler, CPU-friendly)
  - [ ] **Option C**: Local model files (if already downloaded)

- [ ] Set up model paths in `parameter.yaml`
  ```bash
  # Edit parameter.yaml
  vim parameter.yaml

  # Update these paths:
  # llm_model_path: "path/to/your/llm/model"
  # ocr_model_path: "path/to/your/ocr/model"
  ```

- [ ] Verify model paths exist
  ```bash
  # Example for HuggingFace cache
  ls -la ~/.cache/huggingface/hub/
  ```

### Step 5: Run Tests

- [ ] Run standalone server test
  ```bash
  cd src
  uv run python rot_reasoning.py --test
  # OR
  python rot_reasoning.py --test
  ```

- [ ] Verify output shows:
  ```
  Test 1: get_model_info()
  ✓ Model info: {...}

  Test 2: assess_complexity()
  ✓ Complexity: {...}

  Core tests passed! ✅
  ```

- [ ] Run unit tests (optional)
  ```bash
  cd ..
  uv run pytest tests/ -v
  # OR
  pytest tests/ -v
  ```

### Step 6: Docker Setup (Optional)

If using Docker instead of local installation:

- [ ] Verify Docker installed
  ```bash
  docker --version
  docker-compose --version
  ```

- [ ] Build Docker image
  ```bash
  docker build -t rot-reasoning-server:latest .
  ```

- [ ] Run Docker container
  ```bash
  docker run -it --rm \
    --gpus all \
    -p 8000:8000 \
    -v $(pwd)/checkpoints:/app/checkpoints \
    rot-reasoning-server:latest --test
  ```

- [ ] Verify container works
  ```bash
  docker logs <container-id>
  # Should show "Core tests passed! ✅"
  ```

---

## Post-Installation Verification

### Checklist

- [ ] **All imports work**
  ```bash
  uv run python -c "
  from src.rot_reasoning import get_rot_compressor
  from src.model_manager import RoTModelManager
  from src.rot_compressor import RoTCompressor
  print('All imports successful ✅')
  "
  ```

- [ ] **Local UltraRAG detected**
  ```bash
  uv run python src/rot_reasoning.py --test 2>&1 | grep "Using local UltraRAG"
  # Should output: "Using local UltraRAG: True"
  ```

- [ ] **MCP server starts** (if running as server)
  ```bash
  uv run python src/rot_reasoning.py --port 8000 &
  sleep 5
  curl http://localhost:8000/health || echo "Server check (optional)"
  ```

- [ ] **Configuration valid**
  ```bash
  uv run python -c "
  import yaml
  from pathlib import Path
  with open('parameter.yaml') as f:
      config = yaml.safe_load(f)
  print('Config loaded:', config.keys())
  "
  ```

---

## Model Training Setup (Optional)

Only required if you want full 3-4× compression functionality.

### Training Checklist

- [ ] **GPU with 16GB+ VRAM** (or multi-GPU setup)
  ```bash
  nvidia-smi
  ```

- [ ] **DeepSpeed installed**
  ```bash
  uv run python -c "import deepspeed; print('DeepSpeed:', deepspeed.__version__)"
  ```

- [ ] **Training dataset downloaded**
  - GSM8K-Aug-NL dataset
  - See [MODEL_SETUP.md](MODEL_SETUP.md) for download instructions

- [ ] **Checkpoints directory structure**
  ```bash
  mkdir -p checkpoints/stage1
  mkdir -p checkpoints/stage2
  ls -la checkpoints/
  ```

- [ ] **Training scripts accessible**
  ```bash
  ls -la /Volumes/WS4TB/RoT-main/run_train_stage1.sh
  ls -la /Volumes/WS4TB/RoT-main/run_train_stage2.sh
  ```

See [ROT_INTEGRATION_TECHNICAL_PLAN.md](../ROT_INTEGRATION_TECHNICAL_PLAN.md) for full training guide.

---

## Common Issues & Solutions

### Issue: `ModuleNotFoundError: No module named 'fastmcp'`

**Solution:**
```bash
uv sync
# OR
pip install fastmcp>=2.0.0
```

### Issue: `CUDA out of memory`

**Solutions:**
1. Reduce batch size in parameter.yaml
2. Use CPU instead: Set `device: "cpu"` in parameter.yaml
3. Use smaller models

### Issue: `ImportError: attempted relative import`

**Solution:** Already fixed in v0.2.0. Update to latest version.

### Issue: `No module named 'ultrarag.server'`

**Solution:**
```bash
# Verify local UltraRAG source exists
ls -la ../../src/ultrarag/server.py

# If missing, install fastmcp as fallback
uv sync
```

### Issue: Docker GPU not accessible

**Solution:**
```bash
# Install nvidia-docker2
sudo apt-get install nvidia-docker2
sudo systemctl restart docker

# Verify GPU available in Docker
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

---

## Environment Variables (Optional)

Create `.env` file for configuration:

- [ ] Create `.env` file
  ```bash
  cat > .env << 'EOF'
  # Model paths
  LLM_MODEL_PATH=/path/to/llm/model
  OCR_MODEL_PATH=/path/to/ocr/model

  # Device configuration
  DEVICE=cuda  # or "cpu"
  DTYPE=bfloat16  # or "float16", "float32"

  # Checkpoint paths
  STAGE1_CHECKPOINT=checkpoints/stage1/checkpoint_epoch_2
  STAGE2_CHECKPOINT=checkpoints/stage2/checkpoint_step_16000

  # HuggingFace token (optional)
  HF_TOKEN=hf_your_token_here
  EOF
  ```

- [ ] Load environment variables
  ```bash
  source .env
  # OR automatically loaded by python-dotenv
  ```

---

## Final Verification Checklist

Before proceeding to git/GitHub:

- [ ] ✅ All dependencies installed without errors
- [ ] ✅ Standalone test passes (`python rot_reasoning.py --test`)
- [ ] ✅ Using local UltraRAG: True
- [ ] ✅ No import errors
- [ ] ✅ Configuration file valid
- [ ] ✅ Models downloaded (or path to download documented)
- [ ] ✅ Tests pass (2/2 core tests)
- [ ] ✅ Documentation complete (README.md, INSTALL.md, FIXES.md)
- [ ] ✅ Docker build successful (if using Docker)
- [ ] ✅ venv/uv environment works
- [ ] ✅ `.gitignore` configured properly

---

## Ready for Git/GitHub

Once all checkboxes above are complete:

- [ ] Review `.gitignore` (see .gitignore section below)
- [ ] Create git commit
- [ ] Push to GitHub repository
- [ ] Create GitHub release (v0.2.0)
- [ ] Tag release with version

See [GIT_SETUP.md](GIT_SETUP.md) for git configuration and GitHub push instructions.

---

## Installation Time Estimates

| Step | Time (uv) | Time (venv) | Time (Docker) |
|------|-----------|-------------|---------------|
| Environment setup | 2-5 min | 5-10 min | 10-20 min |
| Dependencies | 5-10 min | 10-20 min | Included in build |
| Model download | 20-40 min | 20-40 min | 20-40 min |
| Verification | 2-5 min | 2-5 min | 5-10 min |
| **Total** | **30-60 min** | **40-75 min** | **35-70 min** |

*Times vary based on internet speed and system performance.*

---

## Support

- **Installation Issues**: See [INSTALL.md](INSTALL.md)
- **Import Errors**: See [FIXES.md](FIXES.md)
- **Model Setup**: See [MODEL_SETUP.md](MODEL_SETUP.md)
- **Training**: See [ROT_INTEGRATION_TECHNICAL_PLAN.md](../ROT_INTEGRATION_TECHNICAL_PLAN.md)

---

**Last Updated**: January 24, 2026
**Version**: v0.2.0
**Status**: ✅ Ready for Installation
