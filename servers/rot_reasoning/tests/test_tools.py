"""
Unit tests for RoT MCP tools.
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add server to path
server_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(server_path))

from rot_reasoning import (
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
    assert 'token_savings' in result
    assert 'compression_ratios' in result

    print("✅ compress_and_generate test passed")
    print(f"   Answer: {result['ans_ls'][0]}")
    print(f"   Token savings: {result['token_savings']}")
    print(f"   Compression ratio: {result['compression_ratios'][0]:.2f}")


@pytest.mark.asyncio
async def test_compress_and_generate_with_state():
    """Test compression with state carryover."""
    prompt_ls = ["Continue the reasoning"]
    compressed_state = ["previous_reasoning_state"]

    result = await compress_and_generate(
        prompt_ls=prompt_ls,
        compressed_state=compressed_state,
        max_tokens=50
    )

    assert 'ans_ls' in result
    assert 'compressed_states' in result
    assert len(result['compressed_states']) == 1

    print("✅ compress_and_generate with state test passed")


@pytest.mark.asyncio
async def test_assess_complexity():
    """Test complexity assessment."""
    result = await assess_complexity(
        query="Explain quantum entanglement and its applications in computing",
        context=["Quantum physics is...", "Quantum computing uses..."]
    )

    assert 'complexity' in result
    assert 0.0 <= result['complexity'] <= 1.0
    assert 'recommended_compression' in result
    assert 'recommended_max_steps' in result

    print("✅ assess_complexity test passed")
    print(f"   Complexity: {result['complexity']:.2f}")
    print(f"   Recommended compression: {result['recommended_compression']:.1f}×")
    print(f"   Recommended max steps: {result['recommended_max_steps']}")


@pytest.mark.asyncio
async def test_assess_complexity_simple_query():
    """Test complexity assessment for simple query."""
    result = await assess_complexity(
        query="What is 2 + 2?",
        context=["Math basics"]
    )

    # Simple query should have low complexity
    assert result['complexity'] < 0.5
    assert result['recommended_compression'] <= 2.0

    print("✅ assess_complexity (simple) test passed")
    print(f"   Complexity: {result['complexity']:.2f} (low as expected)")


@pytest.mark.asyncio
async def test_get_model_info():
    """Test model info retrieval."""
    result = await get_model_info()

    assert 'model_loaded' in result
    assert 'status' in result or 'device' in result

    print("✅ get_model_info test passed")
    print(f"   Model loaded: {result.get('model_loaded', False)}")


@pytest.mark.asyncio
async def test_multiple_prompts():
    """Test batch processing of multiple prompts."""
    prompt_ls = [
        "What is 2 + 2?",
        "What is 3 + 5?",
        "What is 10 - 4?"
    ]

    result = await compress_and_generate(
        prompt_ls=prompt_ls,
        max_tokens=50
    )

    assert len(result['ans_ls']) == 3
    assert len(result['compression_ratios']) == 3
    assert result['token_savings'] >= 0

    print("✅ multiple prompts test passed")
    print(f"   Processed {len(prompt_ls)} prompts")
    print(f"   Total token savings: {result['token_savings']}")


if __name__ == "__main__":
    # Run tests
    print("Running RoT server unit tests...\n")
    pytest.main([__file__, "-v", "-s"])
