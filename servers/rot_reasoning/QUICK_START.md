# RoT Reasoning Server - Quick Start Guide

**Version**: 0.2.0
**Status**: Post-Setup Usage Guide
**Last Updated**: January 24, 2026

---

## 🎯 You're Set Up! Now What?

If you've completed `setup.py`, you're ready to use RoT. This guide shows you how.

---

## Quick Navigation

1. [Test Your Installation](#1-test-your-installation)
2. [Use with Claude Desktop](#2-use-with-claude-desktop)
3. [Use with Your Documents](#3-use-with-your-documents)
4. [Python API Usage](#4-python-api-usage)
5. [Run Benchmarks](#5-run-benchmarks)
6. [Train Custom Model](#6-train-custom-model)

---

## 1. Test Your Installation

### Run Example Scripts

```bash
# Test all examples
python examples/example_usage.py

# Quick server test
python src/rot_reasoning.py --test

# Quick benchmark test
python benchmarks/run_benchmarks.py --quick-test
```

**Expected output:**
```
✓ Model info retrieved
✓ Complexity assessment working
✓ Core tests passed
```

---

## 2. Use with Claude Desktop

### Step 1: Locate Your Config File

**macOS:**
```bash
open ~/Library/Application\ Support/Claude/
# Edit claude_desktop_config.json
```

**Windows:**
```bash
# Navigate to: %APPDATA%\Claude\
# Edit claude_desktop_config.json
```

### Step 2: Add RoT Server

Your setup already showed you the exact config. It looks like:

```json
{
  "mcpServers": {
    "rot-reasoning": {
      "command": "python",
      "args": ["/full/path/to/servers/rot_reasoning/src/rot_reasoning.py"],
      "env": {
        "DATA_FOLDER": "/path/to/your/data",
        "MODEL_PATH": "your-model-path",
        "FRAMEWORK": "ollama"
      }
    }
  }
}
```

### Step 3: Restart Claude Desktop

Fully quit and restart Claude Desktop.

### Step 4: Test It

In Claude Desktop, try:

```
Can you use the RoT reasoning tools to analyze complexity?
```

Claude will see these tools:
- `compress_and_generate` - Main reasoning with compression
- `assess_complexity` - Query complexity analysis
- `get_model_info` - Model status check

---

## 3. Use with Your Documents

### Add Documents to Data Folder

Your data folder (configured during setup):
```bash
# Default location (unless you changed it)
cd data/

# Add your documents
cp ~/Documents/research-paper.pdf .
cp ~/Downloads/financial-report.xlsx .
cp -r ~/Projects/documentation/ .
```

### Supported Formats

**Text:**
- `.txt`, `.md`, `.rst`
- `.pdf` (text extraction)
- `.docx`, `.doc`

**Multimodal:**
- `.png`, `.jpg`, `.jpeg` (with vision models)
- `.pdf` (with images)

**Structured:**
- `.json`, `.csv`, `.xlsx`

### Example Query

In Claude Desktop:
```
I've added a 50-page research paper to the data folder.
Can you use RoT compression to summarize the key findings?
```

RoT will:
1. Load the document
2. Assess complexity (long document = high complexity)
3. Apply 3-4x compression
4. Generate response using compressed reasoning

---

## 4. Python API Usage

### Direct Python Integration

```python
import sys
sys.path.insert(0, 'src')

from rot_reasoning import (
    compress_and_generate,
    assess_complexity,
    get_model_info
)

# Check model status
info = get_model_info()
print(f"Model loaded: {info['model_loaded']}")

# Assess complexity
query = "Complex multi-hop question about climate change..."
complexity = assess_complexity(query)
print(f"Complexity: {complexity['complexity']:.2f}")
print(f"Recommended compression: {complexity['recommended_compression']}x")

# Compress and generate
context = "Long document text here..."
result = compress_and_generate(
    query=query,
    context=context,
    max_steps=3,
    compression_level=3.5
)

print(result['response'])
```

### Custom Integration Example

```python
# Build a custom RAG pipeline with RoT compression

from rot_reasoning import compress_and_generate
from your_retriever import retrieve_documents

def rag_with_rot(user_query: str):
    # Step 1: Retrieve relevant documents
    docs = retrieve_documents(user_query, top_k=10)

    # Step 2: Concatenate context (could be very long)
    context = "\n\n".join([doc['text'] for doc in docs])

    # Step 3: Use RoT compression
    result = compress_and_generate(
        query=user_query,
        context=context,
        max_steps=2,
        compression_level=3.0  # 3x compression
    )

    return result['response']

# Use it
answer = rag_with_rot("What are the key findings?")
print(answer)
```

---

## 5. Run Benchmarks

### Quick Test (Recommended First)

```bash
# Fast smoke test (~1 minute)
python benchmarks/run_benchmarks.py --quick-test
```

**Output:**
```
BENCHMARK RESULTS SUMMARY
================================================================================

BEIR_Small:
  Method          Accuracy        Compression     Speedup
  ----------------------------------------------------------------------
  RoT             0.463 ± 0.000   3.40×           2.20×
  vanilla         0.457 ± 0.000   1.00×           1.00×
```

### Full Benchmark Suite

```bash
# Complete evaluation (requires trained model, ~2-4 hours)
python benchmarks/run_benchmarks.py \
  --benchmarks all \
  --baselines vanilla,graph \
  --runs 5
```

### Compare Against SOTA

After training your model, run comprehensive benchmarks:

```bash
# BEIR (retrieval quality)
python benchmarks/run_benchmarks.py --benchmarks BEIR --runs 3

# CRAG (challenging RAG)
python benchmarks/run_benchmarks.py --benchmarks CRAG --runs 3

# Efficiency metrics
python benchmarks/run_benchmarks.py --benchmarks Efficiency --runs 3
```

See `BENCHMARK_PLAN.md` for SOTA comparison criteria.

---

## 6. Train Custom Model

### Prerequisites

- ✅ GPU with 16GB+ VRAM (24GB recommended)
- ✅ Training data prepared
- ✅ 50GB+ disk space
- ✅ 8-16 hours training time

### Training Workflow

**Stage 1: Projection Head Training (4-8 hours)**

```bash
# Edit parameter.yaml to configure training
nano parameter.yaml

# Start Stage 1 training
python training/train_stage1.py \
  --config parameter.yaml \
  --output checkpoints/stage1/
```

**Stage 2: Language Model Fine-tuning (8-12 hours)**

```bash
# Start Stage 2 training (requires Stage 1 checkpoint)
python training/train_stage2.py \
  --config parameter.yaml \
  --stage1-checkpoint checkpoints/stage1/checkpoint_epoch_2 \
  --output checkpoints/stage2/
```

**Use Trained Model:**

```bash
# Update config.yaml with your checkpoint path
echo "checkpoint_path: checkpoints/stage2/checkpoint_step_16000" >> config.yaml

# Test with trained model
python src/rot_reasoning.py --test

# Run benchmarks
python benchmarks/run_benchmarks.py --benchmarks all
```

See `MODEL_TRAINING.md` for detailed training guide.

---

## Common Workflows

### Workflow 1: Daily Research Assistant

```bash
# 1. Add research papers to data folder
cp ~/Downloads/papers/*.pdf data/

# 2. Use with Claude Desktop
# Ask: "Summarize the key findings from the papers in the data folder"
```

### Workflow 2: Long Document Analysis

```python
# Use RoT to compress and analyze 100+ page documents

from rot_reasoning import compress_and_generate

with open('long-document.txt', 'r') as f:
    doc_text = f.read()  # Could be 50,000+ tokens

result = compress_and_generate(
    query="What are the main conclusions?",
    context=doc_text,
    compression_level=4.0  # Aggressive compression for very long docs
)

# RoT compresses 50k tokens → 12.5k tokens
# Saves 37.5k tokens of inference cost
```

### Workflow 3: Multi-Hop Reasoning

```python
# Complex query requiring multiple reasoning steps

query = """
Based on the financial reports, what is the relationship between
R&D spending, patent filings, and revenue growth over the past 5 years?
Are there any notable patterns or anomalies?
"""

result = compress_and_generate(
    query=query,
    context=financial_reports_text,
    max_steps=4,  # Allow multiple reasoning hops
    compression_level=3.0
)

# RoT will:
# 1. Compress initial context
# 2. Reason about R&D spending (hop 1)
# 3. Carry compressed state to analyze patents (hop 2)
# 4. Carry state to correlate with revenue (hop 3)
# 5. Identify patterns (hop 4)
```

---

## Tips and Best Practices

### 🎯 When to Use RoT

**Ideal for:**
- Long documents (10k+ tokens)
- Multi-hop reasoning
- Cost-sensitive applications (API usage limits)
- Repeated queries over same documents

**Not ideal for:**
- Very short queries (<100 tokens)
- Single-step factual lookups
- When compression might lose critical details

### ⚡ Performance Optimization

**Compression Level:**
- `1.5-2.0x` - Safe, minimal quality loss
- `2.0-3.0x` - Recommended, good balance
- `3.0-4.0x` - Aggressive, use for very long docs
- `4.0+x` - Extreme, may lose details

**Max Steps:**
- `1` - Simple queries
- `2-3` - Standard multi-hop reasoning
- `4-5` - Complex multi-hop queries
- `6+` - Very complex reasoning chains (experimental)

### 📊 Monitor Performance

```python
result = compress_and_generate(query, context)

print(f"Original tokens: {result['original_tokens']}")
print(f"Compressed tokens: {result['compressed_tokens']}")
print(f"Compression ratio: {result['compression_ratio']:.2f}x")
print(f"Processing time: {result['processing_time_ms']}ms")
```

---

## Troubleshooting

### Issue: "Model not loaded"

**Solution:**
```bash
# Check config.yaml
cat config.yaml

# Verify model path exists
ls -lh /path/to/model

# Re-run setup if needed
python setup.py
```

### Issue: "CUDA out of memory"

**Solution:**
```python
# Reduce compression level (less GPU memory)
result = compress_and_generate(
    query=query,
    context=context,
    compression_level=2.0  # Lower = less memory
)
```

Or use CPU mode:
```bash
export CUDA_VISIBLE_DEVICES=""
python src/rot_reasoning.py --test
```

### Issue: "Claude Desktop doesn't see RoT tools"

**Checklist:**
- [ ] Config file in correct location
- [ ] JSON syntax valid (use jsonlint)
- [ ] Full path to rot_reasoning.py (not relative)
- [ ] Claude Desktop fully restarted (quit + reopen)
- [ ] Check Claude Desktop logs

**Check logs (macOS):**
```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

---

## Next Steps

### Beginner Path
1. ✅ Run `python examples/example_usage.py`
2. ✅ Add RoT to Claude Desktop
3. ✅ Test with sample documents
4. ✅ Read this guide's workflows

### Intermediate Path
1. ✅ Run quick benchmarks
2. ✅ Integrate RoT into custom Python app
3. ✅ Experiment with compression levels
4. ✅ Analyze performance metrics

### Advanced Path
1. ✅ Train custom RoT model
2. ✅ Run full SOTA benchmarks
3. ✅ Optimize for your specific use case
4. ✅ Contribute improvements

---

## Additional Resources

**Documentation:**
- `BENCHMARK_PLAN.md` - SOTA evaluation strategy
- `MODEL_SETUP.md` - Advanced model configuration
- `MODEL_TRAINING.md` - Custom training guide
- `TROUBLESHOOTING.md` - Detailed problem solving

**Examples:**
- `examples/example_usage.py` - Python API examples
- `examples/custom_integration.py` - Custom RAG pipeline
- `examples/chatbot_wrapper.py` - Chatbot integration

**Community:**
- GitHub Issues - Report bugs, request features
- Discussions - Ask questions, share use cases

---

**Happy reasoning with RoT! 🧠✨**

For questions or issues, see `TROUBLESHOOTING.md` or open a GitHub issue.
