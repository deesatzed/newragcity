# RoT Reasoning Server - LLM Model Setup Guide

**Version**: v0.2.0
**Date**: January 24, 2026

---

## Overview

The RoT Reasoning Server requires two types of models:

1. **Vision-Language Model (VLM)** - For language generation and reasoning
2. **OCR Vision Encoder** - For compressing visual representations of text

This guide covers multiple options for obtaining and configuring these models.

---

## Model Requirements

### Minimum Requirements

| Component | Requirement | Disk Space | RAM/VRAM |
|-----------|-------------|------------|----------|
| LLM (Base) | Qwen2.5-VL-7B or similar | ~15GB | 16GB VRAM (GPU) / 32GB RAM (CPU) |
| OCR Encoder | DeepSeek-OCR or CLIP | ~5GB | 4GB VRAM / 8GB RAM |
| **Total** | | **~20GB** | **20GB VRAM** or **40GB RAM** |

### Recommended for Training

| Component | Requirement | Disk Space | RAM/VRAM |
|-----------|-------------|------------|----------|
| LLM (Training) | Qwen2.5-VL-7B | ~15GB | 40GB+ VRAM (multi-GPU) |
| Training Data | GSM8K-Aug-NL | ~2GB | N/A |
| Checkpoints | Stage 1 + Stage 2 | ~30GB | N/A |
| **Total** | | **~47GB** | **40GB+ VRAM** |

---

## Option 1: HuggingFace Models (Recommended)

### Prerequisites

- [ ] HuggingFace account created (https://huggingface.co/join)
- [ ] HuggingFace CLI installed
  ```bash
  pip install huggingface-hub
  ```
- [ ] Login to HuggingFace
  ```bash
  huggingface-cli login
  # Enter your HF token when prompted
  ```

### Download Qwen2.5-VL-7B (LLM)

```bash
# Using HuggingFace CLI
huggingface-cli download \
  Qwen/Qwen2.5-VL-7B-Instruct \
  --local-dir ~/.cache/huggingface/hub/Qwen2.5-VL-7B-Instruct \
  --local-dir-use-symlinks False

# Verify download
ls -lh ~/.cache/huggingface/hub/Qwen2.5-VL-7B-Instruct/
```

**Alternative: Automatic download on first use**

```python
# The model will auto-download when first accessed
# Just set the path in parameter.yaml:
# llm_model_path: "Qwen/Qwen2.5-VL-7B-Instruct"
```

### Download DeepSeek-OCR (Vision Encoder)

```bash
# Using HuggingFace CLI
huggingface-cli download \
  deepseek-ai/deepseek-ocr \
  --local-dir ~/.cache/huggingface/hub/deepseek-ocr \
  --local-dir-use-symlinks False

# Verify download
ls -lh ~/.cache/huggingface/hub/deepseek-ocr/
```

### Configure parameter.yaml

```yaml
# Edit servers/rot_reasoning/parameter.yaml

llm_model_path: "~/.cache/huggingface/hub/Qwen2.5-VL-7B-Instruct"
# OR use HF path for auto-download:
# llm_model_path: "Qwen/Qwen2.5-VL-7B-Instruct"

ocr_model_path: "~/.cache/huggingface/hub/deepseek-ocr"
# OR use HF path:
# ocr_model_path: "deepseek-ai/deepseek-ocr"

device: "cuda"  # or "cpu" for CPU-only
dtype: "bfloat16"  # or "float16", "float32"
```

---

## Option 2: Ollama (CPU-Friendly, Easier Setup)

Ollama provides easier model management and CPU-optimized inference.

### Install Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version
```

### Download Models via Ollama

```bash
# Download Qwen2.5 (7B variant)
ollama pull qwen2.5:7b

# Verify models
ollama list
```

### Configure for Ollama

**Note**: Ollama integration requires an adapter. For now, use HuggingFace models directly. Ollama support coming in future versions.

---

## Option 3: Pre-downloaded Models (Local Files)

If you already have models downloaded:

### Directory Structure

```
/your/model/directory/
├── llm/
│   ├── Qwen2.5-VL-7B-Instruct/
│   │   ├── config.json
│   │   ├── model.safetensors (or pytorch_model.bin)
│   │   ├── tokenizer.json
│   │   └── ...
└── ocr/
    ├── deepseek-ocr/
    │   ├── config.json
    │   ├── pytorch_model.bin
    │   └── ...
```

### Configure parameter.yaml

```yaml
llm_model_path: "/your/model/directory/llm/Qwen2.5-VL-7B-Instruct"
ocr_model_path: "/your/model/directory/ocr/deepseek-ocr"
device: "cuda"
dtype: "bfloat16"
```

---

## Option 4: Alternative Models (Compatible Substitutes)

If Qwen2.5-VL or DeepSeek-OCR are unavailable:

### Alternative LLMs

| Model | HuggingFace Path | Size | Notes |
|-------|------------------|------|-------|
| **Qwen2-VL-7B** | `Qwen/Qwen2-VL-7B-Instruct` | ~15GB | Older version, compatible |
| **LLaVA-v1.6** | `liuhaotian/llava-v1.6-vicuna-7b` | ~14GB | Vision-language model |
| **InternVL2** | `OpenGVLab/InternVL2-8B` | ~16GB | Strong vision capabilities |

### Alternative OCR/Vision Encoders

| Model | HuggingFace Path | Size | Notes |
|-------|------------------|------|-------|
| **CLIP ViT-L** | `openai/clip-vit-large-patch14` | ~1.7GB | Smaller, faster |
| **SigLIP** | `google/siglip-so400m-patch14-384` | ~1.5GB | Improved CLIP variant |

### Using Alternative Models

```yaml
# Example: Using LLaVA + CLIP
llm_model_path: "liuhaotian/llava-v1.6-vicuna-7b"
ocr_model_path: "openai/clip-vit-large-patch14"

# May require code adjustments in src/ocr_wrapper.py and src/cot_compressor_v2.py
```

---

## Model Testing & Validation

### Test Model Loading

Create a test script:

```python
# test_models.py
import torch
from transformers import AutoModel, AutoTokenizer

def test_llm_model(model_path):
    print(f"Testing LLM: {model_path}")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        model = AutoModel.from_pretrained(model_path, trust_remote_code=True)
        print(f"✅ LLM loaded successfully")
        print(f"   Model type: {model.__class__.__name__}")
        print(f"   Parameters: {sum(p.numel() for p in model.parameters()) / 1e9:.2f}B")
        del model, tokenizer
        torch.cuda.empty_cache()
        return True
    except Exception as e:
        print(f"❌ LLM loading failed: {e}")
        return False

def test_ocr_model(model_path):
    print(f"\nTesting OCR: {model_path}")
    try:
        model = AutoModel.from_pretrained(model_path, trust_remote_code=True)
        print(f"✅ OCR model loaded successfully")
        print(f"   Model type: {model.__class__.__name__}")
        del model
        torch.cuda.empty_cache()
        return True
    except Exception as e:
        print(f"❌ OCR loading failed: {e}")
        return False

if __name__ == "__main__":
    import yaml
    from pathlib import Path

    # Load config
    with open("parameter.yaml") as f:
        config = yaml.safe_load(f)

    llm_ok = test_llm_model(config['llm_model_path'])
    ocr_ok = test_ocr_model(config['ocr_model_path'])

    if llm_ok and ocr_ok:
        print("\n🎉 All models loaded successfully!")
    else:
        print("\n⚠️  Some models failed to load. Check paths in parameter.yaml")
```

Run the test:

```bash
cd servers/rot_reasoning
uv run python test_models.py
```

---

## Training Dataset Setup

Required only for training RoT from scratch.

### GSM8K-Aug-NL Dataset

```bash
# Download from HuggingFace
huggingface-cli download \
  gsm8k \
  --repo-type dataset \
  --local-dir ~/.cache/huggingface/datasets/gsm8k

# OR use datasets library
uv run python -c "
from datasets import load_dataset
dataset = load_dataset('gsm8k', 'main')
print(f'Downloaded {len(dataset[\"train\"])} training examples')
"
```

### Configure Training Data Path

Edit `/Volumes/WS4TB/RoT-main/run_train_stage1.sh`:

```bash
# Update DATA_PATH
DATA_PATH="~/.cache/huggingface/datasets/gsm8k"
```

See [ROT_INTEGRATION_TECHNICAL_PLAN.md](../ROT_INTEGRATION_TECHNICAL_PLAN.md) for full training instructions.

---

## GPU Configuration

### CUDA Setup

```bash
# Check CUDA version
nvcc --version

# Check PyTorch CUDA
uv run python -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f}GB')
"
```

### CPU-Only Mode

If no GPU available:

```yaml
# parameter.yaml
device: "cpu"
dtype: "float32"  # bfloat16 not supported on CPU for some models

# Reduce memory usage
image_size: 384  # instead of 512
batch_size: 1
```

**Note**: CPU inference will be 10-50× slower than GPU.

---

## Model Caching & Storage

### HuggingFace Cache Location

Default cache: `~/.cache/huggingface/hub/`

To change:

```bash
export HF_HOME=/path/to/your/cache
export TRANSFORMERS_CACHE=/path/to/your/cache
```

Add to `.env`:

```bash
# .env
HF_HOME=/path/to/your/cache
TRANSFORMERS_CACHE=/path/to/your/cache
```

### Disk Space Management

```bash
# Check HuggingFace cache size
du -sh ~/.cache/huggingface/

# Clean old models (optional)
huggingface-cli delete-cache

# Keep specific models
huggingface-cli delete-cache --keep "Qwen*" "deepseek*"
```

---

## Troubleshooting

### Issue: Model download times out

**Solution:**
```bash
# Use mirror (China users)
export HF_ENDPOINT=https://hf-mirror.com

# Or download in chunks with resume
huggingface-cli download Qwen/Qwen2.5-VL-7B-Instruct --resume-download
```

### Issue: `Out of memory` when loading model

**Solutions:**
1. Use smaller model (Qwen2-7B instead of 14B)
2. Enable CPU offloading:
   ```python
   model = AutoModel.from_pretrained(
       model_path,
       device_map="auto",
       load_in_8bit=True  # Quantization
   )
   ```
3. Close other applications using VRAM

### Issue: `torch not compiled with CUDA`

**Solution:**
```bash
# Reinstall PyTorch with CUDA support
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### Issue: Model files corrupted

**Solution:**
```bash
# Clear cache and re-download
rm -rf ~/.cache/huggingface/hub/models--Qwen--Qwen2.5-VL-7B-Instruct
huggingface-cli download Qwen/Qwen2.5-VL-7B-Instruct
```

---

## Security & Licensing

### Model Licenses

| Model | License | Commercial Use |
|-------|---------|----------------|
| Qwen2.5-VL | Apache 2.0 | ✅ Yes |
| DeepSeek-OCR | MIT | ✅ Yes |
| CLIP | MIT | ✅ Yes |

Always check license before commercial deployment.

### HuggingFace Token Security

```bash
# Store token securely
huggingface-cli login
# Token stored in: ~/.cache/huggingface/token

# Never commit token to git
echo ".cache/" >> .gitignore
echo "*.token" >> .gitignore
```

---

## Quick Start Summary

### Fastest Setup (Auto-download on first use)

```yaml
# parameter.yaml - Minimal config
llm_model_path: "Qwen/Qwen2.5-VL-7B-Instruct"
ocr_model_path: "openai/clip-vit-large-patch14"  # Smaller, faster
device: "cuda"
dtype: "bfloat16"
```

```bash
# Models will auto-download when server starts
uv run python src/rot_reasoning.py --test

# First run downloads models (~20GB, 15-30 minutes)
# Subsequent runs use cached models
```

---

## Model Onboarding Checklist

- [ ] HuggingFace account created and logged in
- [ ] LLM model downloaded (Qwen2.5-VL or alternative)
- [ ] OCR model downloaded (DeepSeek-OCR or CLIP)
- [ ] `parameter.yaml` configured with correct paths
- [ ] Model loading test passed (`test_models.py`)
- [ ] GPU/CUDA verified (if using GPU)
- [ ] Disk space sufficient (~20GB minimum)
- [ ] Model licenses reviewed

---

**Ready for testing once models are configured!**

See [INSTALL_CHECKLIST.md](INSTALL_CHECKLIST.md) for next steps.

---

**Last Updated**: January 24, 2026
**Version**: v0.2.0
