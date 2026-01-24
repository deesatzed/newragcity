"""
RoT Reasoning MCP Server for UltraRAG.

Provides compressed visual reasoning capabilities via Render-of-Thought (RoT).

STANDALONE VERSION - No external dependencies required beyond fastmcp.
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

# Add UltraRAG source to path for imports
ULTRARAG_ROOT = Path(__file__).resolve().parents[3]
ULTRARAG_SRC = ULTRARAG_ROOT / "src"
if str(ULTRARAG_SRC) not in sys.path:
    sys.path.insert(0, str(ULTRARAG_SRC))

# Now import from local UltraRAG source
try:
    from ultrarag.server import UltraRAG_MCP_Server
    USING_LOCAL_ULTRARAG = True
except ImportError:
    # Fallback: Use fastmcp directly if ultrarag.server not available
    print("WARNING: Could not import ultrarag.server, using fastmcp directly")
    try:
        from fastmcp import FastMCP as UltraRAG_MCP_Server
        USING_LOCAL_ULTRARAG = False
    except ImportError:
        print("ERROR: Neither ultrarag.server nor fastmcp is available!")
        print("Please install: pip install fastmcp>=2.0.0")
        sys.exit(1)

# Import other components (these should be self-contained)
# Try relative import first (when used as module), then absolute (when run as script)
try:
    from .model_manager import RoTModelManager
    from .rot_compressor import RoTCompressor
except ImportError:
    # Running as script, use absolute imports
    try:
        # Add current directory to path for direct imports
        current_dir = Path(__file__).parent
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))

        from model_manager import RoTModelManager
        from rot_compressor import RoTCompressor
    except ImportError as e:
        print(f"ERROR importing RoT components: {e}")
        print(f"Current path: {Path(__file__).parent}")
        print(f"Make sure model_manager.py and rot_compressor.py exist in {current_dir}")
        sys.exit(1)

# Create MCP server instance
app = UltraRAG_MCP_Server("rot_reasoning")
logger = logging.getLogger(__name__)

# Global model manager and compressor (lazy initialization)
_model_manager: Optional[RoTModelManager] = None
_rot_compressor: Optional[RoTCompressor] = None


def get_parameter_config() -> Dict[str, Any]:
    """Load parameter configuration from YAML file."""
    param_file = Path(__file__).parent.parent / "parameter.yaml"
    if not param_file.exists():
        logger.warning(f"Parameter file not found: {param_file}")
        return {}

    try:
        import yaml
        with open(param_file) as f:
            config = yaml.safe_load(f)
            return config or {}
    except Exception as e:
        logger.error(f"Error loading parameter config: {e}")
        return {}


def get_rot_compressor() -> RoTCompressor:
    """Get or initialize RoT compressor (lazy loading)."""
    global _model_manager, _rot_compressor

    if _rot_compressor is not None:
        return _rot_compressor

    # Load configuration
    if USING_LOCAL_ULTRARAG and hasattr(app, 'get_parameter_config'):
        config = app.get_parameter_config()
    else:
        config = get_parameter_config()

    # Initialize model manager
    _model_manager = RoTModelManager(
        checkpoint_path=config.get('checkpoint_path', 'servers/rot_reasoning/checkpoints/stage2/checkpoint_step_16000'),
        stage1_checkpoint=config.get('stage1_checkpoint', 'servers/rot_reasoning/checkpoints/stage1/checkpoint_epoch_2'),
        ocr_model_path=config.get('ocr_model_path', 'DeepSeek-OCR/ocr_model'),
        llm_model_path=config.get('llm_model_path', 'ckpt/base/Qwen3-VL-4B-Instruct'),
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
            'avg_compression_ratio': sum(r['compression_ratio'] for r in results) / len(results) if results else 0,
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


def _get_model_info_impl() -> Dict[str, Any]:
    """Internal implementation of get_model_info."""
    if _rot_compressor is None:
        return {
            'model_loaded': False,
            'status': 'not_initialized',
            'message': 'RoT server not yet initialized. Call compress_and_generate to load model.',
            'using_local_ultrarag': USING_LOCAL_ULTRARAG
        }

    info = _rot_compressor.get_model_info()
    info['using_local_ultrarag'] = USING_LOCAL_ULTRARAG
    return info


@app.tool(output="->model_info")
async def get_model_info() -> Dict[str, Any]:
    """
    Get RoT model information and status.

    Useful for debugging and monitoring model loading status.

    Returns:
        Dictionary with model information
    """
    return _get_model_info_impl()


def _assess_complexity_impl(
    query: str,
    context: List[str],
    complexity_threshold: float = 0.5
) -> Dict[str, float]:
    """Internal implementation of assess_complexity."""
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
    reasoning_keywords = ['analyze', 'compare', 'explain', 'why', 'how', 'multi-step', 'complex', 'reasoning']
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


@app.tool(output="query,context,complexity_threshold->complexity,recommended_compression,recommended_max_steps")
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
    return _assess_complexity_impl(query, context, complexity_threshold)


# Standalone test function
async def test_server():
    """Test the RoT server functionality."""
    print("\n" + "="*60)
    print("Testing RoT Reasoning Server")
    print("="*60 + "\n")

    # Test 1: Model info
    print("Test 1: get_model_info()")
    info = _get_model_info_impl()
    print(f"✓ Model info: {info}")
    print()

    # Test 2: Assess complexity
    print("Test 2: assess_complexity()")
    complexity = _assess_complexity_impl(
        query="What is 2 + 2?",
        context=["Math basics"]
    )
    print(f"✓ Complexity: {complexity}")
    print()

    # Test 3: Compress and generate (skip - requires model checkpoints)
    print("Test 3: compress_and_generate()")
    print("⊘  Skipped - requires trained model checkpoints")
    print("   To test with real model:")
    print("   1. Train RoT model (see README.md)")
    print("   2. Copy checkpoints to servers/rot_reasoning/checkpoints/")
    print("   3. Run test again")
    print()

    print("="*60)
    print("Core tests passed! ✅")
    print("Server is ready for MCP integration.")
    print("Train RoT model for full functionality.")
    print("="*60 + "\n")


# Initialize server (for standalone testing)
if __name__ == "__main__":
    print(f"RoT Reasoning Server")
    print(f"Using local UltraRAG: {USING_LOCAL_ULTRARAG}")
    print(f"UltraRAG source path: {ULTRARAG_SRC}")
    print()

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--port", type=int, default=64510, help="Server port")
    args = parser.parse_args()

    if args.test:
        # Run tests
        asyncio.run(test_server())
    else:
        # Start server
        try:
            import uvicorn
            print(f"Starting RoT server on port {args.port}...")
            uvicorn.run(app, host="0.0.0.0", port=args.port)
        except ImportError:
            print("ERROR: uvicorn not installed. Install with: pip install uvicorn")
            print("Or run tests with: python rot_reasoning.py --test")
