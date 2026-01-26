# RoT Integration Technical Implementation Plan

**Date:** January 23, 2026
**Project:** newragcity (UltraRAG v3.0 → v3.1)
**Phase:** MVP Implementation (Weeks 1-4)
**Developer Guide:** Step-by-step implementation instructions

---

## Overview

This document provides detailed technical specifications and implementation steps for integrating RoT (Render-of-Thought) into UltraRAG as an MCP server.

**Target Audience:** ML/NLP engineers implementing the integration
**Prerequisites:**
- Familiarity with UltraRAG MCP server architecture
- PyTorch and DeepSpeed experience
- Understanding of transformer models and vision encoders

---

## Table of Contents

1. [Architecture Design](#1-architecture-design)
2. [File Structure](#2-file-structure)
3. [Implementation Steps](#3-implementation-steps)
4. [Configuration Schema](#4-configuration-schema)
5. [Tool Specifications](#5-tool-specifications)
6. [Training Pipeline](#6-training-pipeline)
7. [Testing Strategy](#7-testing-strategy)
8. [Deployment Guide](#8-deployment-guide)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Architecture Design

### 1.1 System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    UltraRAG Client (Orchestrator)               │
└────────────────┬────────────────────────────────────────────────┘
                 │ MCP Protocol
                 ├─────────────────┬─────────────────┬────────────
                 │                 │                 │
┌────────────────▼──────┐  ┌──────▼──────┐  ┌──────▼──────────┐
│   Retriever Server    │  │   Prompt    │  │  RoT Reasoning  │
│   (existing)          │  │   Server    │  │  Server (NEW)   │
└───────────────────────┘  └─────────────┘  └─────────┬───────┘
                                                       │
                                                       │ Loads
                                                       │
                                            ┌──────────▼────────┐
                                            │  RoT Compressor   │
                                            │  - Projection Head│
                                            │  - LLM Backbone   │
                                            │  - Text Renderer  │
                                            └───────────────────┘
                                                       │
                                                       │ Uses
                                                       │
                                            ┌──────────▼────────┐
                                            │   Checkpoints     │
                                            │  - Stage 1        │
                                            │  - Stage 2        │
                                            └───────────────────┘
```

### 1.2 Data Flow

**Training Phase:**
```
Text CoT → Render → Image → Vision Encoder → Visual Embedding
                                                       ↓
LLM Forward Pass → Hidden States → Projection Head → Aligned
                                                       ↓
                                              Alignment Loss
```

**Inference Phase:**
```
User Query → Prompt → LLM Forward (no rendering)
                            ↓
                   Projection Head (frozen)
                            ↓
                   Compressed Latent Reasoning
                            ↓
                   LM Head → Final Answer
```

### 1.3 Key Design Decisions

**Decision 1: Lazy Model Loading**
- **Rationale:** RoT models are large (~8GB VRAM). Load only when first tool is called.
- **Implementation:** Global `_rot_model` variable, initialized on first use.

**Decision 2: Checkpoint Management**
- **Rationale:** Two-stage training produces two checkpoint sets. Need both for inference.
- **Implementation:** `parameter.yaml` specifies both `checkpoint_path` (Stage 2) and `stage1_checkpoint`.

**Decision 3: State Carryover in Loops**
- **Rationale:** Loop pipelines need to carry compressed reasoning across iterations.
- **Implementation:** Tool returns `compressed_states` list that can be passed as `compressed_state` input.

**Decision 4: Backward Compatibility**
- **Rationale:** Existing pipelines must work without modification.
- **Implementation:** RoT server is purely additive. `generation` server unchanged.

---

## 2. File Structure

### 2.1 Directory Layout

```
servers/rot_reasoning/
├── src/
│   ├── __init__.py
│   ├── rot_reasoning.py           # Main MCP server
│   ├── rot_compressor.py          # Model wrapper
│   ├── text_to_image.py           # Text rendering (from RoT)
│   ├── ocr_wrapper.py             # Vision encoder wrapper (from RoT)
│   ├── model_manager.py           # Checkpoint loading
│   └── utils.py                   # Helper functions
├── parameter.yaml                  # Default configuration
├── checkpoints/
│   ├── stage1/
│   │   └── checkpoint_epoch_2/    # Projection head weights
│   └── stage2/
│       └── checkpoint_step_16000/ # Fine-tuned LM weights
├── tests/
│   ├── test_tools.py              # Unit tests for MCP tools
│   ├── test_compression.py        # Compression ratio tests
│   └── test_integration.py        # Integration with other servers
├── examples/
│   ├── rot_simple.yaml            # Basic usage
│   ├── rot_loop.yaml              # Loop-based reasoning
│   └── rot_branch.yaml            # Branching logic
├── README.md                       # Server documentation
└── TRAINING.md                     # Training guide
```

### 2.2 Key Files Description

**rot_reasoning.py** (Main Entry Point)
- Defines MCP server instance
- Implements all MCP tools
- Handles parameter loading
- Manages model lifecycle

**rot_compressor.py** (Model Wrapper)
- Wraps `CoTCompressorV2` from RoT
- Provides simplified interface for MCP tools
- Handles checkpoint loading and device management
- Implements compression logic

**model_manager.py** (Checkpoint Management)
- Loads Stage 1 and Stage 2 checkpoints
- Handles DeepSpeed checkpoint format
- Manages model state and freezing
- Provides checkpoint validation

**text_to_image.py** (Rendering - from RoT)
- Copy from `/Volumes/WS4TB/RoT-main/models/text_to_image.py`
- No modifications needed
- Renders text CoT into single-line images

**ocr_wrapper.py** (Vision Encoder - from RoT)
- Copy from `/Volumes/WS4TB/RoT-main/models/ocr_wrapper.py`
- No modifications needed
- Wraps DeepSeek-OCR or equivalent

---

## 3. Implementation Steps

### 3.1 Step 1: Copy RoT Source Code (Day 1)

```bash
# Navigate to UltraRAG root
cd /Volumes/WS4TB/newragcity/UltraRAG-main

# Create server structure
mkdir -p servers/rot_reasoning/src
mkdir -p servers/rot_reasoning/checkpoints/{stage1,stage2}
mkdir -p servers/rot_reasoning/tests
mkdir -p servers/rot_reasoning/examples

# Copy RoT model files
cp /Volumes/WS4TB/RoT-main/models/text_to_image.py servers/rot_reasoning/src/
cp /Volumes/WS4TB/RoT-main/models/ocr_wrapper.py servers/rot_reasoning/src/
cp /Volumes/WS4TB/RoT-main/models/loss.py servers/rot_reasoning/src/
cp /Volumes/WS4TB/RoT-main/models/__init__.py servers/rot_reasoning/src/models_init.py

# Copy core compressor (will be adapted)
cp /Volumes/WS4TB/RoT-main/models/cot_compressor_v2.py servers/rot_reasoning/src/
```

### 3.2 Step 2: Create Model Manager (Day 1-2)

**File:** `servers/rot_reasoning/src/model_manager.py`

```python
"""
Checkpoint loading and model initialization for RoT server.
"""

import torch
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from .cot_compressor_v2 import CoTCompressorV2

logger = logging.getLogger(__name__)


class RoTModelManager:
    """Manages RoT model lifecycle: loading, validation, device management."""

    def __init__(
        self,
        checkpoint_path: str,
        stage1_checkpoint: str,
        ocr_model_path: str,
        llm_model_path: str,
        device: str = "cuda",
        dtype: str = "bfloat16",
        **kwargs
    ):
        self.checkpoint_path = Path(checkpoint_path)
        self.stage1_checkpoint = Path(stage1_checkpoint)
        self.ocr_model_path = ocr_model_path
        self.llm_model_path = llm_model_path
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.dtype = getattr(torch, dtype)
        self.kwargs = kwargs

        self.model: Optional[CoTCompressorV2] = None

        self._validate_checkpoints()

    def _validate_checkpoints(self):
        """Validate checkpoint paths exist."""
        if not self.checkpoint_path.exists():
            raise FileNotFoundError(f"Stage 2 checkpoint not found: {self.checkpoint_path}")

        if not self.stage1_checkpoint.exists():
            raise FileNotFoundError(f"Stage 1 checkpoint not found: {self.stage1_checkpoint}")

        logger.info(f"Checkpoints validated: Stage 1 = {self.stage1_checkpoint}, Stage 2 = {self.checkpoint_path}")

    def load_model(self) -> CoTCompressorV2:
        """Load RoT model with trained checkpoints."""
        if self.model is not None:
            logger.info("Model already loaded, returning cached instance")
            return self.model

        logger.info("Loading RoT model...")

        # Initialize model in Stage 2 mode
        self.model = CoTCompressorV2(
            ocr_model_path=self.ocr_model_path,
            llm_model_path=self.llm_model_path,
            device=self.device,
            image_size=self.kwargs.get('image_size', 512),
            font_size=self.kwargs.get('font_size', 16),
            freeze_vision=True,  # Always freeze vision encoder
            use_projection_head=True,
            projection_hidden_dim=self.kwargs.get('projection_hidden_dim', 2048),
            enable_lora=self.kwargs.get('enable_lora', False),
            full_finetuning=self.kwargs.get('full_finetuning', False),
            lora_r=self.kwargs.get('lora_r', 16),
            lora_alpha=self.kwargs.get('lora_alpha', 32),
            lora_dropout=self.kwargs.get('lora_dropout', 0.05),
            lora_target_modules=self.kwargs.get('lora_target_modules', None),
            use_custom_llm=self.kwargs.get('use_custom_llm', True),
            loss_type=self.kwargs.get('loss_type', 'mse_only'),
            stage2_mode=True,  # Critical: Stage 2 inference mode
            freeze_projection_head=True,  # Freeze projection head (trained in Stage 1)
            include_vision_loss=False,  # No vision loss at inference
            include_img_end_loss=False,  # No img_end loss at inference
        )

        # Load Stage 1 checkpoint (projection head)
        logger.info(f"Loading Stage 1 checkpoint: {self.stage1_checkpoint}")
        stage1_state = torch.load(
            self.stage1_checkpoint / "mp_rank_00_model_states.pt",
            map_location=self.device
        )
        # Extract projection head weights and load
        proj_head_state = self._extract_projection_head(stage1_state)
        self.model.projection_head.load_state_dict(proj_head_state)

        # Load Stage 2 checkpoint (fine-tuned LM)
        logger.info(f"Loading Stage 2 checkpoint: {self.checkpoint_path}")
        stage2_state = torch.load(
            self.checkpoint_path / "mp_rank_00_model_states.pt",
            map_location=self.device
        )
        # Extract LM weights and load
        lm_state = self._extract_lm_state(stage2_state)
        self.model.language_model.load_state_dict(lm_state)

        # Load special tokens (if any)
        special_tokens_path = self.stage1_checkpoint / "special_tokens.bin"
        if special_tokens_path.exists():
            special_tokens = torch.load(special_tokens_path, map_location=self.device)
            self._load_special_tokens(special_tokens)

        # Set to eval mode
        self.model.eval()
        self.model.to(self.device).to(self.dtype)

        logger.info("RoT model loaded successfully")
        return self.model

    def _extract_projection_head(self, state_dict: Dict) -> Dict:
        """Extract projection head weights from checkpoint."""
        # DeepSpeed format: state_dict['module']['projection_head']
        if 'module' in state_dict:
            module_state = state_dict['module']
        else:
            module_state = state_dict

        proj_head_keys = [k for k in module_state.keys() if 'projection_head' in k]
        proj_head_state = {
            k.replace('projection_head.', ''): module_state[k]
            for k in proj_head_keys
        }
        return proj_head_state

    def _extract_lm_state(self, state_dict: Dict) -> Dict:
        """Extract language model weights from checkpoint."""
        if 'module' in state_dict:
            module_state = state_dict['module']
        else:
            module_state = state_dict

        lm_keys = [k for k in module_state.keys() if 'language_model' in k]
        lm_state = {
            k.replace('language_model.', ''): module_state[k]
            for k in lm_keys
        }
        return lm_state

    def _load_special_tokens(self, special_tokens: Dict):
        """Load special token embeddings."""
        # Add special tokens to tokenizer and model embeddings
        # Implementation depends on model architecture
        pass

    def get_model(self) -> CoTCompressorV2:
        """Get model instance (loads if not already loaded)."""
        if self.model is None:
            return self.load_model()
        return self.model

    def unload_model(self):
        """Unload model to free GPU memory."""
        if self.model is not None:
            del self.model
            self.model = None
            torch.cuda.empty_cache()
            logger.info("RoT model unloaded")
```

### 3.3 Step 3: Create RoT Compressor Wrapper (Day 2)

**File:** `servers/rot_reasoning/src/rot_compressor.py`

```python
"""
High-level wrapper for RoT compression and generation.
"""

import torch
from typing import List, Dict, Any, Optional
import logging

from .model_manager import RoTModelManager

logger = logging.getLogger(__name__)


class RoTCompressor:
    """Wrapper for RoT compression with simplified interface."""

    def __init__(self, model_manager: RoTModelManager):
        self.model_manager = model_manager
        self.model = None  # Lazy loading

    def _ensure_model_loaded(self):
        """Ensure model is loaded before use."""
        if self.model is None:
            self.model = self.model_manager.get_model()

    async def compress_and_generate(
        self,
        prompt: str,
        compressed_state: Optional[str] = None,
        max_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.8,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate answer with compressed reasoning.

        Args:
            prompt: Input prompt
            compressed_state: Previous compressed reasoning (for loops)
            max_tokens: Max tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling threshold

        Returns:
            Dictionary with answer, compressed state, and metrics
        """
        self._ensure_model_loaded()

        # Prepare input
        input_text = prompt
        if compressed_state:
            # Incorporate previous reasoning state
            input_text = f"{compressed_state}\n{prompt}"

        # Generate with RoT compression
        with torch.no_grad():
            output = self.model.generate(
                prompt=input_text,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                **kwargs
            )

        # Extract answer and compressed representation
        answer = output.get('text', '')
        compressed_repr = output.get('compressed_representation', '')

        # Calculate metrics
        original_tokens = self._estimate_tokens(prompt + answer)  # Hypothetical full CoT
        compressed_tokens = output.get('actual_tokens', 0)
        compression_ratio = original_tokens / compressed_tokens if compressed_tokens > 0 else 1.0
        tokens_saved = original_tokens - compressed_tokens

        return {
            'answer': answer,
            'compressed_state': compressed_repr,
            'compression_ratio': compression_ratio,
            'tokens_saved': tokens_saved,
            'original_tokens_estimated': original_tokens,
            'compressed_tokens': compressed_tokens
        }

    async def visual_reasoning_trace(
        self,
        reasoning_steps: List[str]
    ) -> Dict[str, Any]:
        """
        Generate visual reasoning trace for debugging.

        Args:
            reasoning_steps: List of reasoning step texts

        Returns:
            Dictionary with rendered images and metadata
        """
        self._ensure_model_loaded()

        rendered_images = []
        for step in reasoning_steps:
            # Render using text_to_image
            image = self.model.text_renderer.render(step)
            rendered_images.append(image)

        return {
            'images': rendered_images,
            'count': len(rendered_images),
            'format': 'PIL.Image'
        }

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        # Simple heuristic: ~4 chars per token for English
        # For production, use actual tokenizer
        return len(text) // 4

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and status."""
        return {
            'model_loaded': self.model is not None,
            'device': str(self.model_manager.device),
            'checkpoint_path': str(self.model_manager.checkpoint_path),
            'stage1_checkpoint': str(self.model_manager.stage1_checkpoint)
        }
```

### 3.4 Step 4: Implement MCP Server (Day 2-3)

**File:** `servers/rot_reasoning/src/rot_reasoning.py`

```python
"""
RoT Reasoning MCP Server for UltraRAG.

Provides compressed visual reasoning capabilities via Render-of-Thought (RoT).
"""

import os
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

from ultrarag.server import UltraRAG_MCP_Server
from .model_manager import RoTModelManager
from .rot_compressor import RoTCompressor

# Create MCP server instance
app = UltraRAG_MCP_Server("rot_reasoning")
logger = logging.getLogger(__name__)

# Global model manager and compressor (lazy initialization)
_model_manager: Optional[RoTModelManager] = None
_rot_compressor: Optional[RoTCompressor] = None


def get_rot_compressor() -> RoTCompressor:
    """Get or initialize RoT compressor (lazy loading)."""
    global _model_manager, _rot_compressor

    if _rot_compressor is not None:
        return _rot_compressor

    # Load configuration
    config = app.get_parameter_config()

    # Initialize model manager
    _model_manager = RoTModelManager(
        checkpoint_path=config['checkpoint_path'],
        stage1_checkpoint=config['stage1_checkpoint'],
        ocr_model_path=config['ocr_model_path'],
        llm_model_path=config['llm_model_path'],
        device=config.get('device', 'cuda'),
        dtype=config.get('dtype', 'bfloat16'),
        image_size=config.get('image_size', 512),
        font_size=config.get('font_size', 16),
        projection_hidden_dim=config.get('projection_hidden_dim', 2048),
        enable_lora=config.get('enable_lora', False),
        full_finetuning=config.get('full_finetuning', False),
        use_custom_llm=config.get('use_custom_llm', True),
    )

    # Initialize compressor
    _rot_compressor = RoTCompressor(_model_manager)

    logger.info("RoT compressor initialized")
    return _rot_compressor


@app.tool(output="prompt_ls,compressed_state,compression_ratio,max_tokens,temperature,top_p->ans_ls,compressed_states,token_savings")
async def compress_and_generate(
    prompt_ls: List[str],
    compressed_state: Optional[List[str]] = None,
    compression_ratio: float = 3.5,
    max_tokens: int = 256,
    temperature: float = 0.7,
    top_p: float = 0.8
) -> Dict[str, Any]:
    """
    Generate answers with compressed visual reasoning.

    This is the main tool for RoT-based generation. It replaces or augments
    the standard `generation.generate` tool with compressed reasoning.

    Args:
        prompt_ls: List of prompts
        compressed_state: Previous compressed reasoning states (for loops)
        compression_ratio: Target compression ratio (informational, model is pre-trained)
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature (0.0 = deterministic)
        top_p: Nucleus sampling threshold

    Returns:
        Dictionary with:
        - ans_ls: List of generated answers
        - compressed_states: List of compressed reasoning states
        - token_savings: Total tokens saved via compression

    Example:
        ```yaml
        - rot_reasoning.compress_and_generate:
            input:
              prompt_ls: questions
              compression_ratio: 3.5
            output:
              ans_ls: answers
              compressed_states: reasoning_states
        ```
    """
    compressor = get_rot_compressor()

    results = []
    for i, prompt in enumerate(prompt_ls):
        # Get previous state if available
        prev_state = None
        if compressed_state and i < len(compressed_state):
            prev_state = compressed_state[i]

        # Generate with compression
        result = await compressor.compress_and_generate(
            prompt=prompt,
            compressed_state=prev_state,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p
        )
        results.append(result)

    # Aggregate results
    return {
        'ans_ls': [r['answer'] for r in results],
        'compressed_states': [r['compressed_state'] for r in results],
        'token_savings': sum(r['tokens_saved'] for r in results),
        'compression_ratios': [r['compression_ratio'] for r in results],
        'metrics': {
            'total_original_tokens': sum(r['original_tokens_estimated'] for r in results),
            'total_compressed_tokens': sum(r['compressed_tokens'] for r in results),
            'avg_compression_ratio': sum(r['compression_ratio'] for r in results) / len(results),
            'total_tokens_saved': sum(r['tokens_saved'] for r in results)
        }
    }


@app.tool(output="reasoning_steps->images,count")
async def visual_reasoning_trace(
    reasoning_steps: List[str]
) -> Dict[str, Any]:
    """
    Generate visual reasoning trace for debugging and interpretability.

    Renders reasoning steps as images to visualize the compressed reasoning process.

    Args:
        reasoning_steps: List of reasoning step texts

    Returns:
        Dictionary with rendered images and metadata

    Example:
        ```yaml
        - rot_reasoning.visual_reasoning_trace:
            input:
              reasoning_steps: cot_steps
            output:
              images: reasoning_images
        ```
    """
    compressor = get_rot_compressor()
    return await compressor.visual_reasoning_trace(reasoning_steps)


@app.tool(output="->model_info")
async def get_model_info() -> Dict[str, Any]:
    """
    Get RoT model information and status.

    Useful for debugging and monitoring model loading status.

    Returns:
        Dictionary with model information
    """
    if _rot_compressor is None:
        return {
            'model_loaded': False,
            'status': 'not_initialized'
        }

    return _rot_compressor.get_model_info()


@app.tool(output="complexity_threshold->complexity,recommended_compression,recommended_max_steps")
async def assess_complexity(
    query: str,
    context: List[str],
    complexity_threshold: float = 0.5
) -> Dict[str, float]:
    """
    Assess query complexity for adaptive compression strategies.

    Analyzes query and context to recommend compression parameters.

    Args:
        query: User query
        context: Retrieved context passages
        complexity_threshold: Threshold for complex vs. simple (0.0-1.0)

    Returns:
        Dictionary with complexity score and recommendations

    Example:
        ```yaml
        - rot_reasoning.assess_complexity:
            input:
              query: user_question
              context: retrieved_passages
            output:
              complexity: query_complexity
              recommended_compression: compression_ratio
        ```
    """
    # Simple heuristic: query length, context length, keyword detection
    query_length = len(query.split())
    context_length = sum(len(c.split()) for c in context)

    # Complexity scoring heuristics
    complexity = 0.0

    # Query length factor
    if query_length > 50:
        complexity += 0.3
    elif query_length > 20:
        complexity += 0.2
    else:
        complexity += 0.1

    # Context length factor
    if context_length > 1000:
        complexity += 0.3
    elif context_length > 500:
        complexity += 0.2
    else:
        complexity += 0.1

    # Keyword detection (multi-step, reasoning, analysis, etc.)
    reasoning_keywords = ['analyze', 'compare', 'explain', 'why', 'how', 'multi-step', 'complex']
    if any(kw in query.lower() for kw in reasoning_keywords):
        complexity += 0.4

    # Clamp to [0.0, 1.0]
    complexity = min(1.0, complexity)

    # Recommendations based on complexity
    if complexity < 0.3:
        recommended_compression = 1.0  # No compression (simple query)
        recommended_max_steps = 1
    elif complexity < 0.6:
        recommended_compression = 2.0  # Light compression
        recommended_max_steps = 3
    else:
        recommended_compression = 3.5  # Full compression
        recommended_max_steps = 10

    return {
        'complexity': complexity,
        'recommended_compression': recommended_compression,
        'recommended_max_steps': recommended_max_steps,
        'is_complex': complexity >= complexity_threshold
    }


# Initialize server (called by UltraRAG client)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=64510)
```

### 3.5 Step 5: Create Configuration (Day 3)

**File:** `servers/rot_reasoning/parameter.yaml`

```yaml
# servers/rot_reasoning/parameter.yaml

# Model checkpoints
checkpoint_path: "servers/rot_reasoning/checkpoints/stage2/checkpoint_step_16000"
stage1_checkpoint: "servers/rot_reasoning/checkpoints/stage1/checkpoint_epoch_2"

# Base models
ocr_model_path: "DeepSeek-OCR/ocr_model"
llm_model_path: "ckpt/base/Qwen3-VL-4B-Instruct"

# Device configuration
device: "cuda"
dtype: "bfloat16"
gpu_ids: "0,1"

# Rendering configuration
image_size: 512
font_size: 16
background_color: "white"
text_color: "black"

# Model architecture
projection_hidden_dim: 2048
use_custom_llm: true

# Training configuration (used during training, not inference)
enable_lora: false
full_finetuning: false
lora_r: 16
lora_alpha: 32
lora_dropout: 0.05
lora_target_modules:
  - "q_proj"
  - "k_proj"
  - "v_proj"
  - "o_proj"

# Generation parameters (defaults, can be overridden in pipeline)
max_tokens: 256
temperature: 0.7
top_p: 0.8
compression_ratio: 3.5  # Target (informational, model is pre-trained)

# Performance
batch_size: 8
use_vllm: false  # Use vLLM for accelerated inference (optional)

# Reasoning configuration
max_reasoning_steps: 10
enable_visual_trace: true  # Save reasoning images for debugging
adaptive_compression: true  # Adjust compression based on complexity

# Monitoring
log_compression_metrics: true
log_token_usage: true
```

### 3.6 Step 6: Create Pipeline Examples (Day 3-4)

**File:** `servers/rot_reasoning/examples/rot_simple.yaml`

```yaml
# Simple compressed reasoning example

servers:
  retriever: servers/retriever
  rot_reasoning: servers/rot_reasoning
  prompt: servers/prompt
  evaluation: servers/evaluation
  benchmark: servers/benchmark

pipeline:
  # Load data
  - benchmark.get_data:
      input:
        dataset_name: "gsm8k"

  # Initialize retriever
  - retriever.retriever_init

  # Retrieve context
  - retriever.retriever_search

  # Format prompt
  - prompt.qa_rag_boxed

  # Generate with RoT compression (replaces generation.generate)
  - rot_reasoning.compress_and_generate:
      input:
        prompt_ls: prompt_ls
        compression_ratio: 3.5
        max_tokens: 256
      output:
        ans_ls: answers
        token_savings: total_token_savings

  # Evaluate
  - evaluation.evaluate
```

**File:** `servers/rot_reasoning/examples/rot_loop.yaml`

```yaml
# Multi-step reasoning with state carryover

servers:
  retriever: servers/retriever
  rot_reasoning: servers/rot_reasoning
  prompt: servers/prompt
  custom: servers/custom

pipeline:
  - retriever.retriever_init
  - retriever.retriever_search

  # Compressed iterative reasoning (state carries across iterations)
  - loop:
      times: 5
      steps:
        # Generate sub-question
        - prompt.gen_subq

        # Generate with compression (carries previous reasoning)
        - rot_reasoning.compress_and_generate:
            input:
              prompt_ls: subq_prompts
              compressed_state: reasoning_state  # Previous iteration state
              max_tokens: 150
            output:
              ans_ls: subq_answers
              compressed_states: reasoning_state  # Updated for next iteration
              token_savings: iteration_savings

        # Retrieve for next iteration
        - retriever.retriever_search:
            input:
              query_list: subq_answers
            output:
              ret_psg: temp_psg

        # Merge passages
        - custom.merge_passages

  # Final answer generation
  - prompt.qa_rag_boxed
  - rot_reasoning.compress_and_generate
  - evaluation.evaluate
```

**File:** `servers/rot_reasoning/examples/rot_branch.yaml`

```yaml
# Adaptive compression based on query complexity

servers:
  retriever: servers/retriever
  rot_reasoning: servers/rot_reasoning
  generation: servers/generation  # Standard generation for simple queries
  prompt: servers/prompt
  custom: servers/custom

pipeline:
  - retriever.retriever_init
  - retriever.retriever_search

  # Assess query complexity
  - rot_reasoning.assess_complexity:
      input:
        query: user_question
        context: retrieved_passages
      output:
        complexity: query_complexity
        recommended_compression: compression_ratio

  # Branch based on complexity
  - branch:
      router:
        - custom.route_by_field:
            field: query_complexity
            threshold: 0.5  # Simple vs. complex
      branches:
        simple:  # Low complexity - skip compression overhead
          - generation.generate:
              input:
                prompt_ls: prompt_ls
                max_tokens: 128
              output:
                ans_ls: answers

        complex:  # High complexity - use full RoT compression
          - rot_reasoning.compress_and_generate:
              input:
                prompt_ls: prompt_ls
                compression_ratio: compression_ratio
                max_tokens: 256
              output:
                ans_ls: answers
                token_savings: savings

  - evaluation.evaluate
```

---

## 4. Configuration Schema

### 4.1 Required Parameters

```yaml
# Checkpoint paths (REQUIRED)
checkpoint_path: "path/to/stage2/checkpoint"       # Stage 2 (LM fine-tuned)
stage1_checkpoint: "path/to/stage1/checkpoint"     # Stage 1 (projection head)

# Model paths (REQUIRED)
ocr_model_path: "path/to/ocr/model"                # Vision encoder
llm_model_path: "path/to/llm/model"                # Base LLM
```

### 4.2 Optional Parameters

```yaml
# Device
device: "cuda"                 # or "cpu"
dtype: "bfloat16"              # or "float16", "float32"
gpu_ids: "0,1"                 # Multi-GPU support

# Rendering
image_size: 512                # Image width (height is fixed at 32px)
font_size: 16                  # Font size for rendering
background_color: "white"
text_color: "black"

# Architecture
projection_hidden_dim: 2048    # Projection head hidden dimension

# Generation
max_tokens: 256                # Default max tokens
temperature: 0.7               # Sampling temperature
top_p: 0.8                     # Nucleus sampling

# Reasoning
max_reasoning_steps: 10
enable_visual_trace: true
adaptive_compression: true

# Performance
batch_size: 8
use_vllm: false
```

### 4.3 Environment Variables

```bash
# Optional: Override checkpoint paths via environment
export ROT_CHECKPOINT_PATH="/path/to/stage2"
export ROT_STAGE1_CHECKPOINT="/path/to/stage1"

# Optional: Model cache directories
export HF_HOME="/path/to/huggingface/cache"
export TORCH_HOME="/path/to/torch/cache"
```

---

## 5. Tool Specifications

### 5.1 Tool: compress_and_generate

**Primary generation tool with RoT compression.**

**Inputs:**
- `prompt_ls` (List[str], required): Prompts to generate from
- `compressed_state` (List[str], optional): Previous compressed reasoning
- `compression_ratio` (float, optional): Target ratio (informational)
- `max_tokens` (int, optional): Max tokens to generate
- `temperature` (float, optional): Sampling temperature
- `top_p` (float, optional): Nucleus sampling threshold

**Outputs:**
- `ans_ls` (List[str]): Generated answers
- `compressed_states` (List[str]): Compressed reasoning states
- `token_savings` (int): Total tokens saved

**Example:**
```yaml
- rot_reasoning.compress_and_generate:
    input:
      prompt_ls: ["Solve x^2 + 5x + 6 = 0"]
      max_tokens: 200
    output:
      ans_ls: answers
      compressed_states: states
```

### 5.2 Tool: visual_reasoning_trace

**Generate visual representations of reasoning steps.**

**Inputs:**
- `reasoning_steps` (List[str], required): Reasoning texts to visualize

**Outputs:**
- `images` (List[PIL.Image]): Rendered reasoning images
- `count` (int): Number of images

**Example:**
```yaml
- rot_reasoning.visual_reasoning_trace:
    input:
      reasoning_steps: ["Step 1: ...", "Step 2: ..."]
    output:
      images: reasoning_images
```

### 5.3 Tool: assess_complexity

**Assess query complexity for adaptive compression.**

**Inputs:**
- `query` (str, required): User query
- `context` (List[str], required): Retrieved passages
- `complexity_threshold` (float, optional): Threshold for branching

**Outputs:**
- `complexity` (float): Complexity score (0.0-1.0)
- `recommended_compression` (float): Recommended compression ratio
- `recommended_max_steps` (int): Recommended max reasoning steps

**Example:**
```yaml
- rot_reasoning.assess_complexity:
    input:
      query: user_question
      context: passages
    output:
      complexity: query_complexity
```

### 5.4 Tool: get_model_info

**Get model status and information.**

**Inputs:** None

**Outputs:**
- `model_info` (Dict): Model status and configuration

**Example:**
```yaml
- rot_reasoning.get_model_info:
    output:
      model_info: info
```

---

## 6. Training Pipeline

### 6.1 Data Preparation

**Step 1: Download Datasets**
```bash
cd /Volumes/WS4TB/RoT-main/data

# Download GSM8K-Aug-NL
wget https://example.com/gsm8k_aug_nl.tar.gz
tar -xzf gsm8k_aug_nl.tar.gz

# Download Math-500
wget https://example.com/math500.tar.gz
tar -xzf math500.tar.gz
```

**Step 2: Validate Data Format**
```python
# data/validate_data.py
import jsonlines

def validate_gsm8k(file_path):
    with jsonlines.open(file_path) as reader:
        for obj in reader:
            assert 'id' in obj
            assert 'question' in obj
            assert 'cot' in obj  # Chain-of-thought reasoning
            assert 'answer' in obj
    print(f"✅ {file_path} validated")

validate_gsm8k('data/GSM8k-Aug-NL/train.jsonl')
validate_gsm8k('data/GSM8k-Aug-NL/test.jsonl')
```

### 6.2 Stage 1: Projection Head Training

**Objective:** Align LLM hidden states with vision encoder embeddings

**Command:**
```bash
cd /Volumes/WS4TB/RoT-main

bash run_train_stage1.sh \
    --num_gpus 2 \
    --config configs/stage1_config_qwen3vl_4b.yaml \
    --dataset gsm8kaug \
    --batch_size 16 \
    --num_epochs 2 \
    --lr 2e-5 \
    --save_interval 200
```

**Expected Output:**
```
Epoch 1/2:
  Step 100/1000: Loss = 0.523, Vision Loss = 0.412, LM Loss = 0.111
  Step 200/1000: Loss = 0.489, Vision Loss = 0.381, LM Loss = 0.108
  ...
  Step 1000/1000: Loss = 0.402, Vision Loss = 0.298, LM Loss = 0.104
  Checkpoint saved: output/checkpoints/stage1/checkpoint_step_1000/

Epoch 2/2:
  Step 100/1000: Loss = 0.385, Vision Loss = 0.283, LM Loss = 0.102
  ...
  Final checkpoint saved: output/checkpoints/stage1/checkpoint_epoch_2/
```

**Duration:** ~4-8 hours on 2× A100 GPUs

**Validation:**
```bash
# Test checkpoint loading
python scripts/validate_checkpoint.py \
    --checkpoint output/checkpoints/stage1/checkpoint_epoch_2

# Expected output:
# ✅ Checkpoint structure valid
# ✅ Projection head weights loaded
# ✅ Special tokens present
```

### 6.3 Stage 2: Language Model Fine-tuning

**Objective:** Fine-tune LM for answer generation with frozen projection head

**Command:**
```bash
bash run_train_stage2.sh \
    --num_gpus 2 \
    --config configs/stage2_config_qwen3vl_4b.yaml \
    --dataset gsm8kaug \
    --batch_size 16 \
    --num_epochs 2 \
    --lr 2e-5 \
    --save_interval 200 \
    --stage1_checkpoint output/checkpoints/stage1/checkpoint_epoch_2
```

**Expected Output:**
```
Stage 2 Training:
  Loading Stage 1 checkpoint: output/checkpoints/stage1/checkpoint_epoch_2
  ✅ Projection head loaded and frozen

Epoch 1/2:
  Step 100/2000: Loss = 1.234, LM Loss = 1.234
  Step 200/2000: Loss = 1.012, LM Loss = 1.012
  ...
  Checkpoint saved: output/checkpoints/stage2/checkpoint_step_2000/

Epoch 2/2:
  ...
  Final checkpoint saved: output/checkpoints/stage2/checkpoint_step_16000/
```

**Duration:** ~8-12 hours on 2× A100 GPUs

**Validation:**
```bash
# Evaluate on test set
python scripts/evaluate.py \
    --checkpoint output/checkpoints/stage2/checkpoint_step_16000 \
    --stage1_checkpoint output/checkpoints/stage1/checkpoint_epoch_2 \
    --dataset gsm8k \
    --split test \
    --max_samples 100

# Expected output:
# Accuracy: 0.92
# Compression ratio: 3.5×
# Tokens saved: 65%
```

### 6.4 Checkpoint Deployment

**Step 1: Copy to RoT Server**
```bash
# From RoT training directory
cp -r output/checkpoints/stage1/checkpoint_epoch_2 \
      /Volumes/WS4TB/newragcity/UltraRAG-main/servers/rot_reasoning/checkpoints/stage1/

cp -r output/checkpoints/stage2/checkpoint_step_16000 \
      /Volumes/WS4TB/newragcity/UltraRAG-main/servers/rot_reasoning/checkpoints/stage2/
```

**Step 2: Update Configuration**
```yaml
# servers/rot_reasoning/parameter.yaml
checkpoint_path: "servers/rot_reasoning/checkpoints/stage2/checkpoint_step_16000"
stage1_checkpoint: "servers/rot_reasoning/checkpoints/stage1/checkpoint_epoch_2"
```

**Step 3: Test Loading**
```bash
cd /Volumes/WS4TB/newragcity/UltraRAG-main

# Test MCP server tool
python -c "
from servers.rot_reasoning.src.rot_reasoning import get_rot_compressor
compressor = get_rot_compressor()
print('✅ RoT model loaded successfully')
print(compressor.get_model_info())
"
```

---

## 7. Testing Strategy

### 7.1 Unit Tests

**File:** `servers/rot_reasoning/tests/test_tools.py`

```python
"""
Unit tests for RoT MCP tools.
"""

import pytest
import asyncio
from servers.rot_reasoning.src.rot_reasoning import (
    compress_and_generate,
    assess_complexity,
    get_model_info
)


@pytest.mark.asyncio
async def test_compress_and_generate():
    """Test basic compression and generation."""
    prompt_ls = ["What is 2 + 2?"]

    result = await compress_and_generate(
        prompt_ls=prompt_ls,
        max_tokens=50
    )

    assert 'ans_ls' in result
    assert len(result['ans_ls']) == 1
    assert result['token_savings'] > 0
    print(f"✅ compress_and_generate test passed")
    print(f"   Answer: {result['ans_ls'][0]}")
    print(f"   Token savings: {result['token_savings']}")


@pytest.mark.asyncio
async def test_assess_complexity():
    """Test complexity assessment."""
    result = await assess_complexity(
        query="Explain quantum entanglement",
        context=["Quantum physics is..."]
    )

    assert 'complexity' in result
    assert 0.0 <= result['complexity'] <= 1.0
    assert 'recommended_compression' in result
    print(f"✅ assess_complexity test passed")
    print(f"   Complexity: {result['complexity']:.2f}")


@pytest.mark.asyncio
async def test_model_info():
    """Test model info retrieval."""
    result = await get_model_info()

    assert 'model_loaded' in result
    print(f"✅ get_model_info test passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### 7.2 Integration Tests

**File:** `servers/rot_reasoning/tests/test_integration.py`

```python
"""
Integration tests with other MCP servers.
"""

import pytest
import yaml
from pathlib import Path
from ultrarag.client import Configuration, PipelineExecutor


@pytest.mark.integration
async def test_simple_pipeline():
    """Test simple pipeline with RoT."""
    config_path = "servers/rot_reasoning/examples/rot_simple.yaml"
    config = Configuration.load_config(config_path)

    executor = PipelineExecutor(config)
    result = await executor.run()

    assert result['status'] == 'success'
    assert 'token_savings' in result
    print(f"✅ Simple pipeline test passed")
    print(f"   Token savings: {result['token_savings']}")


@pytest.mark.integration
async def test_loop_pipeline():
    """Test loop pipeline with state carryover."""
    config_path = "servers/rot_reasoning/examples/rot_loop.yaml"
    config = Configuration.load_config(config_path)

    executor = PipelineExecutor(config)
    result = await executor.run()

    assert result['status'] == 'success'
    assert result['loop_iterations'] == 5
    print(f"✅ Loop pipeline test passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
```

### 7.3 Performance Benchmarks

**File:** `servers/rot_reasoning/tests/test_compression.py`

```python
"""
Performance benchmarks for RoT compression.
"""

import pytest
import asyncio
import time
from servers.rot_reasoning.src.rot_reasoning import compress_and_generate
from servers.generation.src.generation import generate  # Standard generation


@pytest.mark.benchmark
async def test_compression_ratio():
    """Measure compression ratio on GSM8K test set."""
    # Load test queries
    with open('data/GSM8k-Aug-NL/test.jsonl') as f:
        test_data = [json.loads(line) for line in f][:100]  # First 100 samples

    total_original = 0
    total_compressed = 0

    for item in test_data:
        prompt = item['question']

        result = await compress_and_generate(
            prompt_ls=[prompt],
            max_tokens=256
        )

        total_original += result['metrics']['total_original_tokens']
        total_compressed += result['metrics']['total_compressed_tokens']

    compression_ratio = total_original / total_compressed
    print(f"✅ Compression ratio test passed")
    print(f"   Compression ratio: {compression_ratio:.2f}×")
    print(f"   Original tokens: {total_original}")
    print(f"   Compressed tokens: {total_compressed}")

    assert compression_ratio >= 3.0, f"Compression ratio too low: {compression_ratio}"


@pytest.mark.benchmark
async def test_inference_speed():
    """Measure inference speedup."""
    prompt = "Solve the equation: 3x + 7 = 22"

    # Standard generation
    start = time.time()
    _ = await generate(prompt_ls=[prompt], max_tokens=200)
    standard_time = time.time() - start

    # RoT compression
    start = time.time()
    _ = await compress_and_generate(prompt_ls=[prompt], max_tokens=200)
    rot_time = time.time() - start

    speedup = standard_time / rot_time
    print(f"✅ Inference speed test passed")
    print(f"   Standard time: {standard_time:.2f}s")
    print(f"   RoT time: {rot_time:.2f}s")
    print(f"   Speedup: {speedup:.2f}×")

    assert speedup >= 1.5, f"Speedup too low: {speedup}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "benchmark"])
```

### 7.4 Running Tests

```bash
# Unit tests (fast)
pytest servers/rot_reasoning/tests/test_tools.py -v

# Integration tests (requires servers running)
pytest servers/rot_reasoning/tests/test_integration.py -v -m integration

# Performance benchmarks (slow)
pytest servers/rot_reasoning/tests/test_compression.py -v -m benchmark

# All tests
pytest servers/rot_reasoning/tests/ -v
```

---

## 8. Deployment Guide

### 8.1 Local Development Deployment

```bash
# 1. Ensure checkpoints are in place
ls servers/rot_reasoning/checkpoints/stage1/checkpoint_epoch_2/
ls servers/rot_reasoning/checkpoints/stage2/checkpoint_step_16000/

# 2. Test model loading
python -m servers.rot_reasoning.src.rot_reasoning

# 3. Run simple pipeline
ultrarag run servers/rot_reasoning/examples/rot_simple.yaml

# 4. Check logs
tail -f logs/rot_reasoning.log
```

### 8.2 Production Deployment (Docker)

**Dockerfile:**
```dockerfile
# Dockerfile for RoT server
FROM nvidia/cuda:12.1-base-ubuntu22.04

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    git \
    wget

# Install UltraRAG
WORKDIR /app
COPY . /app
RUN pip install -e ".[all]"

# Download checkpoints (or mount as volume)
# COPY checkpoints/ /app/servers/rot_reasoning/checkpoints/

# Expose MCP server port
EXPOSE 64510

# Run server
CMD ["python", "-m", "servers.rot_reasoning.src.rot_reasoning"]
```

**Build and Run:**
```bash
# Build image
docker build -t ultrarag-rot:v3.1 .

# Run container with GPU
docker run --gpus all -p 64510:64510 -v $(pwd)/checkpoints:/app/servers/rot_reasoning/checkpoints ultrarag-rot:v3.1
```

### 8.3 Kubernetes Deployment

**rot-reasoning-deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rot-reasoning-server
spec:
  replicas: 2
  selector:
    matchLabels:
      app: rot-reasoning
  template:
    metadata:
      labels:
        app: rot-reasoning
    spec:
      containers:
      - name: rot-reasoning
        image: ultrarag-rot:v3.1
        resources:
          limits:
            nvidia.com/gpu: 1
          requests:
            nvidia.com/gpu: 1
        ports:
        - containerPort: 64510
        volumeMounts:
        - name: checkpoints
          mountPath: /app/servers/rot_reasoning/checkpoints
          readOnly: true
      volumes:
      - name: checkpoints
        persistentVolumeClaim:
          claimName: rot-checkpoints-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: rot-reasoning-service
spec:
  selector:
    app: rot-reasoning
  ports:
  - protocol: TCP
    port: 64510
    targetPort: 64510
  type: LoadBalancer
```

**Deploy:**
```bash
kubectl apply -f rot-reasoning-deployment.yaml
kubectl get pods -l app=rot-reasoning
```

---

## 9. Troubleshooting

### 9.1 Common Issues

#### Issue 1: Checkpoint Not Found
**Error:** `FileNotFoundError: Stage 2 checkpoint not found`

**Solution:**
```bash
# Verify checkpoint path in parameter.yaml
cat servers/rot_reasoning/parameter.yaml | grep checkpoint_path

# Check if checkpoints exist
ls -la servers/rot_reasoning/checkpoints/stage2/checkpoint_step_16000/

# If missing, copy from training output
cp -r /path/to/RoT/output/checkpoints/stage2/checkpoint_step_16000 \
      servers/rot_reasoning/checkpoints/stage2/
```

#### Issue 2: CUDA Out of Memory
**Error:** `RuntimeError: CUDA out of memory`

**Solution:**
```yaml
# Reduce batch size in parameter.yaml
batch_size: 4  # Down from 8

# Or use model quantization
dtype: "int8"  # Down from "bfloat16"

# Or use CPU (slow)
device: "cpu"
```

#### Issue 3: Low Compression Ratio
**Problem:** Compression ratio < 3×

**Solution:**
```bash
# Check if using Stage 2 checkpoint (not Stage 1)
grep "stage2_mode: True" servers/rot_reasoning/src/model_manager.py

# Verify training completed successfully
python scripts/evaluate.py \
    --checkpoint checkpoints/stage2/checkpoint_step_16000 \
    --stage1_checkpoint checkpoints/stage1/checkpoint_epoch_2

# If poor results, retrain with more data or epochs
```

#### Issue 4: Model Loading Timeout
**Problem:** Model takes >5 minutes to load

**Solution:**
```python
# Enable lazy loading (already implemented)
# Model loads on first tool call, not server start

# Or pre-load in background thread
import threading

def preload_model():
    compressor = get_rot_compressor()
    logger.info("Model pre-loaded")

threading.Thread(target=preload_model, daemon=True).start()
```

### 9.2 Debug Mode

Enable verbose logging:
```yaml
# servers/rot_reasoning/parameter.yaml
logging:
  level: "DEBUG"
  log_compression_metrics: true
  log_token_usage: true
  save_intermediate_outputs: true
```

Check logs:
```bash
tail -f logs/rot_reasoning.log
```

### 9.3 Performance Profiling

```python
# Add profiling to tools
import cProfile
import pstats

def profile_tool(func):
    async def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = await func(*args, **kwargs)
        profiler.disable()
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        stats.print_stats(20)  # Top 20 functions
        return result
    return wrapper

# Apply to compress_and_generate
@profile_tool
@app.tool()
async def compress_and_generate(...):
    ...
```

---

## 10. Next Steps

### After Completing This Implementation

**Week 1:**
- ✅ Create server structure
- ✅ Implement MCP tools
- ✅ Configure parameters

**Week 2:**
- ✅ Train Stage 1 and 2 models
- ✅ Validate checkpoints
- ✅ Deploy to server

**Week 3:**
- ✅ Integration testing
- ✅ Performance benchmarking
- ✅ Bug fixes

**Week 4:**
- ✅ Documentation
- ✅ Alpha release
- ✅ Community feedback

### Moving to Phase 2 (Advanced Integration)

Once MVP is complete:
1. Extract deepConf from ersatz_rag
2. Integrate with RoT for confidence-gated compression
3. Add PageIndex and LEANN MCP servers
4. Create unified advanced pipeline examples

---

## Appendix: Quick Reference

### Commands Cheat Sheet

```bash
# Training
bash run_train_stage1.sh --num_gpus 2 --dataset gsm8kaug
bash run_train_stage2.sh --num_gpus 2 --stage1_checkpoint checkpoints/stage1/checkpoint_epoch_2

# Testing
pytest servers/rot_reasoning/tests/ -v
ultrarag run servers/rot_reasoning/examples/rot_simple.yaml

# Deployment
docker build -t ultrarag-rot:v3.1 .
docker run --gpus all -p 64510:64510 ultrarag-rot:v3.1

# Debugging
tail -f logs/rot_reasoning.log
python -m pdb servers/rot_reasoning/src/rot_reasoning.py
```

### File Paths Reference

```
/Volumes/WS4TB/RoT-main/                                 # RoT source code
/Volumes/WS4TB/newragcity/UltraRAG-main/                 # UltraRAG main
  ├── servers/rot_reasoning/                              # New RoT server
  │   ├── src/rot_reasoning.py                           # MCP server
  │   ├── parameter.yaml                                  # Configuration
  │   └── checkpoints/                                    # Model weights
  └── examples/                                            # Pipeline examples
```

### Configuration Template

```yaml
checkpoint_path: "servers/rot_reasoning/checkpoints/stage2/checkpoint_step_16000"
stage1_checkpoint: "servers/rot_reasoning/checkpoints/stage1/checkpoint_epoch_2"
ocr_model_path: "DeepSeek-OCR/ocr_model"
llm_model_path: "ckpt/base/Qwen3-VL-4B-Instruct"
device: "cuda"
dtype: "bfloat16"
max_tokens: 256
temperature: 0.7
compression_ratio: 3.5
```

### Pipeline Template

```yaml
servers:
  rot_reasoning: servers/rot_reasoning

pipeline:
  - rot_reasoning.compress_and_generate:
      input:
        prompt_ls: questions
      output:
        ans_ls: answers
        token_savings: savings
```

---

**END OF TECHNICAL IMPLEMENTATION PLAN**

For questions or support, refer to:
- `servers/rot_reasoning/README.md` - Server documentation
- `servers/rot_reasoning/TRAINING.md` - Training guide
- GitHub Issues: https://github.com/OpenBMB/UltraRAG/issues
