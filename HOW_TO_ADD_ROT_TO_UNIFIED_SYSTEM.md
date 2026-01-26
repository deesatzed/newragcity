# How to Add RoT to the Unified System

**Current Status**: ThreeApproachRAG (PageIndex + LEANN + deepConf)
**Target**: FourApproachRAG (PageIndex + LEANN + deepConf + RoT)
**Timeline**: After RoT model is trained (2-5 days)

---

## Overview

The unified system currently integrates 3 approaches:
1. **PageIndex**: Document structure extraction with reasoning
2. **LEANN**: Vector search with dense embeddings
3. **deepConf**: Multi-factor confidence scoring

**RoT (Render-of-Thought)** will add visual compression of reasoning chains as a 4th approach.

---

## Prerequisites

### 1. Train RoT Model

**Required before integration:**

```bash
cd /Volumes/WS4TB/newragcity/UltraRAG-main/servers/rot_reasoning

# Stage 1: Train OCR + text rendering (1-2 days)
python train_stage1.py \
  --epochs 2 \
  --batch-size 32 \
  --learning-rate 1e-4 \
  --gpu cuda \
  --output checkpoints/stage1/

# Stage 2: Train reasoning compression (1-3 days)
python train_stage2.py \
  --stage1-checkpoint checkpoints/stage1/checkpoint_epoch_2 \
  --steps 16000 \
  --batch-size 16 \
  --learning-rate 5e-5 \
  --gpu cuda \
  --output checkpoints/stage2/
```

**Requirements**:
- GPU: A100 or similar (40GB+ VRAM)
- Time: 2-5 days total
- Cost: $500-2000 GPU time
- Dataset: Synthetic CoT examples (need to generate)

**Validation**:
```bash
# Test model loads correctly
python -c "
from src.model_manager import RoTModelManager
manager = RoTModelManager(
    checkpoint_path='checkpoints/stage2/checkpoint_step_16000',
    stage1_checkpoint='checkpoints/stage1/checkpoint_epoch_2',
    device='cuda'
)
print('✓ RoT model loaded successfully')
"
```

---

## Integration Steps

### Step 1: Fix Import Errors

**Current Issue**: Missing Qwen3VL support in transformers

**Solution 1** (Update transformers):
```bash
pip install --upgrade transformers>=4.42.0
# Or use development version with Qwen3VL support
pip install git+https://github.com/huggingface/transformers.git
```

**Solution 2** (Use compatible model):
```python
# In src/model_manager.py, replace Qwen3VL with Qwen2VL
from transformers import Qwen2VLForConditionalGeneration  # Instead of Qwen3VL
```

**Verify**:
```bash
python -c "
import sys
sys.path.insert(0, 'src')
from model_manager import RoTModelManager
print('✓ Imports working')
"
```

---

### Step 2: Update ThreeApproachRAG to FourApproachRAG

**File**: `ersatz_rag/regulus/backend/app/three_approach_integration.py`

**Add RoT initialization**:

```python
class FourApproachRAG(ThreeApproachRAG):  # Inherit from existing
    """
    Complete RAG system using PageIndex + LEANN + deepConf + RoT
    """

    def __init__(
        self,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        confidence_threshold: float = 0.80,
        enable_streaming: bool = True,
        rot_checkpoint_path: Optional[str] = None,  # NEW
        enable_rot: bool = False,  # NEW
    ):
        # Call parent initialization (PageIndex + LEANN + deepConf)
        super().__init__(
            embedding_model=embedding_model,
            confidence_threshold=confidence_threshold,
            enable_streaming=enable_streaming
        )

        # 4️⃣ Initialize RoT (Reasoning compression)
        self.rot_manager = None
        self.rot_compressor = None

        if enable_rot and rot_checkpoint_path:
            try:
                from servers.rot_reasoning.src.model_manager import RoTModelManager
                from servers.rot_reasoning.src.rot_compressor import RoTCompressor

                self.rot_manager = RoTModelManager(
                    checkpoint_path=f"{rot_checkpoint_path}/checkpoint_step_16000",
                    stage1_checkpoint=f"{rot_checkpoint_path}/../stage1/checkpoint_epoch_2",
                    ocr_model_path="DeepSeek-OCR/ocr_model",
                    llm_model_path="Qwen/Qwen2.5-VL-7B-Instruct",
                    device="cuda",
                    dtype="bfloat16",
                )
                self.rot_compressor = RoTCompressor(self.rot_manager)
                print("✅ RoT initialized (visual reasoning compression)")

            except Exception as e:
                print(f"⚠️ RoT initialization failed: {e}")
                print("   Continuing without RoT...")
        else:
            print("⚠️ RoT disabled (no checkpoint path or enable_rot=False)")

        print("\n🎯 Enhanced 4-Approach System Ready:")
        print("   1️⃣ PageIndex: Document reasoning and structure")
        print("   2️⃣ LEANN + Hybrid: Vector + Lexical + Reranking search")
        print("   3️⃣ deepConf + Calibration: Advanced confidence with historical learning")
        if self.rot_compressor:
            print("   4️⃣ RoT: Visual reasoning compression")
```

---

### Step 3: Add RoT to Query Processing Pipeline

**Modify `broad_then_deep_search` method**:

```python
def broad_then_deep_search_with_rot(
    self,
    query: str,
    index_path: str,
    top_k: int = 10,
    enable_rot_compression: bool = True
) -> Dict[str, Any]:
    """
    Broad-then-Deep with optional RoT compression
    """

    # Step 1: Existing Broad-then-Deep search
    results = self.broad_then_deep_search(query, index_path, top_k)

    if not enable_rot_compression or not self.rot_compressor:
        return results

    # Step 2: RoT compression on high-confidence results
    print("🎨 Applying RoT visual reasoning compression...")

    compressed_results = []
    for result in results['results']:
        try:
            # Extract reasoning chain from result
            reasoning_text = self._extract_reasoning_chain(result)

            # Compress with RoT
            compressed = self.rot_compressor.compress(
                reasoning_text=reasoning_text,
                compression_level="adaptive"  # or "aggressive", "conservative"
            )

            # Add RoT metrics to result
            result['rot_compression'] = {
                'original_tokens': len(reasoning_text.split()),
                'compressed_tokens': compressed['token_count'],
                'compression_ratio': compressed['compression_ratio'],
                'visual_representation': compressed['image_path'],
                'ocr_confidence': compressed['ocr_confidence']
            }

            compressed_results.append(result)

        except Exception as e:
            print(f"   Warning: RoT compression failed for result: {e}")
            compressed_results.append(result)  # Keep original

    # Update approach summary
    results['results'] = compressed_results
    results['approach_summary']['total_approaches_used'] = 4
    results['approach_summary']['rot_compression'] = 'enabled'

    return results

def _extract_reasoning_chain(self, result: Dict[str, Any]) -> str:
    """Extract reasoning chain from result for RoT compression"""

    # Combine content + confidence reasoning
    reasoning = f"{result['content']}\n\n"
    reasoning += "Confidence Analysis:\n"

    for factor, score in result['confidence_profile'].items():
        if factor != 'composite_confidence':
            reasoning += f"- {factor}: {score:.3f}\n"

    return reasoning
```

---

### Step 4: Update Benchmark to Test RoT

**Modify `benchmarks/beir_unified_benchmark.py`**:

```python
def run_unified_benchmark_with_rot(
    rag_system: FourApproachRAG,  # Use FourApproachRAG
    index_path: str,
    queries: Dict,
    qrels: Dict,
    max_queries: int = None,
    enable_rot: bool = True  # NEW
) -> Dict:
    """
    Run BEIR benchmark on unified system with optional RoT
    """

    # ... existing code ...

    # Use RoT-enhanced search if available
    try:
        if enable_rot and rag_system.rot_compressor:
            results = rag_system.broad_then_deep_search_with_rot(
                query=query_text,
                index_path=index_path,
                top_k=100,
                enable_rot_compression=True
            )
        else:
            results = rag_system.broad_then_deep_search(
                query=query_text,
                index_path=index_path,
                top_k=100
            )

        # ... rest of benchmark code ...

    # Add RoT metrics to results
    if enable_rot and rag_system.rot_compressor:
        compression_ratios = []
        for query_results in all_results:
            for result in query_results['results']:
                if 'rot_compression' in result:
                    compression_ratios.append(result['rot_compression']['compression_ratio'])

        results['rot_metrics'] = {
            'average_compression_ratio': np.mean(compression_ratios) if compression_ratios else 0.0,
            'queries_compressed': len(compression_ratios),
            'total_queries': len(all_results)
        }
```

---

### Step 5: Update System Status

**Modify `get_system_status` method**:

```python
def get_system_status(self) -> Dict[str, Any]:
    """Get status of all 4 approaches"""

    status = super().get_system_status()  # Get 3-approach status

    # Add RoT status
    status['approaches']['rot'] = {
        'status': 'enabled' if self.rot_compressor else 'disabled',
        'checkpoint_available': self.rot_manager is not None,
        'description': 'Visual reasoning compression for efficient inference'
    }

    status['integration_level'] = sum([
        1 if self.pageindex_client else 0,
        1 if self.leann_searcher else 0,
        1 if self.confidence_calibrator else 0,
        1 if self.rot_compressor else 0,  # NEW
    ])

    status['ready_for_production'] = status['integration_level'] >= 3  # Minimum 3 approaches

    return status
```

---

## Testing RoT Integration

### Unit Tests

**Create**: `ersatz_rag/regulus/backend/tests/test_rot_integration.py`

```python
import pytest
from app.three_approach_integration import FourApproachRAG

def test_rot_initialization_with_checkpoint():
    """Test RoT initializes when checkpoint is available"""

    rag = FourApproachRAG(
        enable_rot=True,
        rot_checkpoint_path="/path/to/checkpoints/stage2"
    )

    assert rag.rot_compressor is not None
    assert rag.rot_manager is not None

def test_rot_initialization_without_checkpoint():
    """Test RoT gracefully handles missing checkpoint"""

    rag = FourApproachRAG(
        enable_rot=True,
        rot_checkpoint_path=None
    )

    assert rag.rot_compressor is None
    assert rag.rot_manager is None

def test_rot_compression_on_results():
    """Test RoT compression adds expected metrics"""

    rag = FourApproachRAG(
        enable_rot=True,
        rot_checkpoint_path="/path/to/checkpoints/stage2"
    )

    # Build test index
    # ... setup code ...

    # Run query with RoT
    results = rag.broad_then_deep_search_with_rot(
        query="test query",
        index_path="/tmp/test_index",
        enable_rot_compression=True
    )

    assert 'rot_compression' in results['results'][0]
    assert results['approach_summary']['total_approaches_used'] == 4
    assert results['approach_summary']['rot_compression'] == 'enabled'
```

### Integration Test

```bash
cd /Volumes/WS4TB/newragcity/UltraRAG-main/ersatz_rag/regulus/backend

# Test with RoT enabled
python -c "
from app.three_approach_integration import FourApproachRAG

rag = FourApproachRAG(
    enable_rot=True,
    rot_checkpoint_path='../../servers/rot_reasoning/checkpoints/stage2'
)

status = rag.get_system_status()
print(f'Integration level: {status['integration_level']}/4')
print(f'RoT status: {status['approaches']['rot']['status']}')
"
```

---

## Performance Expectations

### Before RoT (3 Approaches)

- **nDCG@10**: 0.5865
- **Recall@100**: 0.0637
- **Latency**: ~100-200ms per query
- **Cost**: Standard embedding + LLM inference

### After RoT (4 Approaches)

**Expected Improvements**:
- **Compression Ratio**: 3-4× (from RoT paper claims, need to validate)
- **Latency Reduction**: 2-2.5× faster (fewer LLM tokens)
- **Cost Reduction**: 70-75% (compressed reasoning chains)
- **Quality**: Maintained or improved (visual reasoning preservation)

**Trade-offs**:
- **RoT Overhead**: ~50-100ms for compression
- **Total Latency**: May increase initially, but saves on downstream LLM calls
- **Memory**: +2-3GB for RoT model

**Benchmark Comparison**:
```
ThreeApproachRAG:  nDCG@10 = 0.5865, Latency = 150ms
FourApproachRAG:   nDCG@10 = ? (need to measure), Latency = ? (need to measure)
```

---

## Expected Results Structure

### Query Result With RoT

```json
{
  "content": "Document content...",
  "metadata": {...},
  "confidence_profile": {
    "semantic_confidence": 0.87,
    "source_authority": 0.92,
    "content_relevance": 0.75,
    "structure_confidence": 0.85,
    "model_confidence": 0.92,
    "composite_confidence": 0.864
  },
  "rot_compression": {
    "original_tokens": 1250,
    "compressed_tokens": 380,
    "compression_ratio": 3.29,
    "visual_representation": "/tmp/rot_compressed_abc123.png",
    "ocr_confidence": 0.94
  },
  "approach_summary": {
    "total_approaches_used": 4,
    "pageindex_reasoning": "enabled",
    "leann_embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "deepconf_gating": "enabled",
    "rot_compression": "enabled"
  }
}
```

---

## Debugging Common Issues

### Issue 1: Import Errors

**Symptom**:
```python
ImportError: cannot import name 'Qwen3VLForConditionalGeneration'
```

**Solutions**:
1. Update transformers: `pip install --upgrade transformers>=4.42.0`
2. Use Qwen2VL instead of Qwen3VL
3. Check transformers version supports model: `python -c "from transformers import Qwen3VLForConditionalGeneration"`

### Issue 2: Checkpoint Not Found

**Symptom**:
```python
FileNotFoundError: checkpoints/stage2/checkpoint_step_16000 not found
```

**Solutions**:
1. Verify checkpoint path: `ls -la /path/to/checkpoints/stage2/`
2. Train model first (see Prerequisites)
3. Use absolute paths instead of relative
4. Check checkpoint naming matches code

### Issue 3: CUDA Out of Memory

**Symptom**:
```python
RuntimeError: CUDA out of memory
```

**Solutions**:
1. Reduce batch size in RoT inference
2. Use `dtype="float16"` instead of `"bfloat16"`
3. Offload RoT to CPU: `device="cpu"`
4. Use model parallelism for large batches

### Issue 4: RoT Compression Fails

**Symptom**:
```python
Exception in rot_compressor.compress()
```

**Solutions**:
1. Check OCR model is loaded: `self.rot_manager.ocr_model is not None`
2. Verify input text format (must be string)
3. Check compression level is valid: `"adaptive"`, `"aggressive"`, or `"conservative"`
4. Enable debug logging: `logging.basicConfig(level=logging.DEBUG)`

---

## Timeline and Milestones

### Week 1: Model Training

- [ ] Day 1-2: Train Stage 1 (OCR + text rendering)
- [ ] Day 3-5: Train Stage 2 (reasoning compression)
- [ ] Day 6: Validate model checkpoints
- [ ] Day 7: Fix any import errors

### Week 2: Integration

- [ ] Day 1-2: Update ThreeApproachRAG to FourApproachRAG
- [ ] Day 3: Add RoT to query processing pipeline
- [ ] Day 4: Update benchmark to test RoT
- [ ] Day 5: Write unit tests
- [ ] Day 6: Run integration tests
- [ ] Day 7: Performance profiling

### Week 3: Validation

- [ ] Day 1-2: Run BEIR benchmark with RoT (323 queries)
- [ ] Day 3: Analyze compression ratios and quality
- [ ] Day 4: Measure latency and cost improvements
- [ ] Day 5: Compare vs 3-approach baseline
- [ ] Day 6: Fix any performance issues
- [ ] Day 7: Final validation and documentation

---

## Success Criteria

### Minimum Viable

✅ RoT model trains without errors
✅ FourApproachRAG initializes with RoT enabled
✅ Benchmark runs on 10+ queries with RoT
✅ Results include rot_compression metrics
✅ No degradation in nDCG@10 vs 3-approach baseline

### Full Success

✅ All 323 BEIR queries tested with RoT
✅ Compression ratio ≥ 3.0× achieved
✅ Latency improvement ≥ 1.5× measured
✅ Cost reduction ≥ 60% validated
✅ nDCG@10 maintained or improved vs baseline
✅ Production deployment ready

---

## Alternative: RoT as Optional Enhancement

If RoT training is delayed or unavailable, keep it as **optional**:

```python
# Initialize without RoT (falls back to 3-approach)
rag = FourApproachRAG(
    enable_rot=False  # Still works as ThreeApproachRAG
)

# Add RoT later when ready
rag.enable_rot(checkpoint_path="/path/to/trained/model")
```

This allows:
- Immediate deployment with 3 approaches (0.5865 nDCG@10)
- RoT addition as enhancement (target: ≥0.5865 + compression benefits)
- A/B testing: 3-approach vs 4-approach performance

---

## Conclusion

RoT integration into the unified system requires:
1. **Model training** (2-5 days, $500-2000)
2. **Code integration** (1-2 days)
3. **Testing and validation** (1 week)

**Total timeline**: 2-3 weeks from start of training to production deployment

**Expected benefits**:
- 3-4× compression ratio
- 1.5-2.5× latency reduction
- 60-75% cost savings
- Maintained or improved quality

**Risk mitigation**:
- Keep RoT optional (fallback to 3-approach)
- Validate on small query set first
- Monitor quality metrics closely
- A/B test before full deployment

---

**Document Created**: January 26, 2026
**Current System**: ThreeApproachRAG (PageIndex + LEANN + deepConf)
**Target System**: FourApproachRAG (+ RoT)
**Status**: RoT model training required before integration

---

*This guide provides a complete roadmap for adding RoT to the unified system once the model is trained.*
