#!/usr/bin/env python3
"""
RoT Reasoning Server - Example Usage

This script demonstrates how to use the RoT server directly from Python
without MCP integration. Useful for testing and custom integrations.
"""

import sys
from pathlib import Path

# Add parent src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rot_reasoning import (
    _get_model_info_impl,
    _assess_complexity_impl,
)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}\n")


def example_1_model_info():
    """Example 1: Get model information."""
    print_section("Example 1: Get Model Information")

    info = _get_model_info_impl()
    print(f"Model loaded: {info['model_loaded']}")
    print(f"Status: {info['status']}")
    print(f"Using local UltraRAG: {info['using_local_ultrarag']}")

    if info['model_loaded']:
        print(f"\nModel details:")
        for key, value in info.items():
            if key not in ['model_loaded', 'status', 'using_local_ultrarag']:
                print(f"  {key}: {value}")


def example_2_assess_complexity():
    """Example 2: Assess query complexity."""
    print_section("Example 2: Assess Query Complexity")

    # Simple query
    simple_query = "What is the capital of France?"
    result = _assess_complexity_impl(simple_query, ["Geography basics"])
    print(f"Query: {simple_query}")
    print(f"  Complexity: {result['complexity']:.2f}")
    print(f"  Is complex: {result['is_complex']}")
    print(f"  Recommended compression: {result['recommended_compression']:.1f}x")
    print(f"  Recommended max steps: {result['recommended_max_steps']}")

    print()

    # Complex query
    complex_query = """
    Analyze the relationship between climate change, agricultural production,
    and food security in Southeast Asia over the next 20 years. Consider
    multiple factors including rainfall patterns, crop yields, population
    growth, and economic development.
    """
    result = _assess_complexity_impl(complex_query, ["Climate research papers", "Agricultural data"])
    print(f"Query: {complex_query.strip()}")
    print(f"  Complexity: {result['complexity']:.2f}")
    print(f"  Is complex: {result['is_complex']}")
    print(f"  Recommended compression: {result['recommended_compression']:.1f}x")
    print(f"  Recommended max steps: {result['recommended_max_steps']}")


def example_3_compress_and_generate():
    """Example 3: Compress context and generate response."""
    print_section("Example 3: Compress and Generate (Placeholder Mode)")

    query = "What are the key benefits of using RoT compression?"
    context = """
    Render-of-Thought (RoT) is a novel approach to reasoning that compresses
    textual reasoning chains into visual representations. This approach offers
    several key benefits:

    1. Compression: RoT achieves 3-4x token compression compared to traditional
       chain-of-thought reasoning, significantly reducing computational costs.

    2. Speed: By compressing reasoning states into images, RoT can process
       complex multi-hop queries faster than text-based approaches.

    3. Cost Reduction: The compression leads to 70%+ reduction in inference
       costs for large language models.

    4. Maintained Accuracy: Despite compression, RoT maintains high accuracy
       on retrieval and reasoning tasks, typically ≥90% of baseline performance.

    5. State Carryover: Compressed visual states can be carried across multiple
       reasoning steps, enabling efficient multi-hop reasoning.
    """

    print(f"Query: {query}")
    print(f"\nContext ({len(context)} chars):")
    print(context[:200] + "...")

    print(f"\n⊘ Skipped - requires trained model checkpoints")
    print(f"\nIn placeholder mode, compress_and_generate would:")
    print(f"  1. Compress {len(context)} chars of context")
    print(f"  2. Apply 3-4× token compression")
    print(f"  3. Generate response using compressed reasoning")
    print(f"  4. Return answer + savings metrics")

    print(f"\nExpected output structure:")
    print(f"  {{")
    print(f"    'response': 'Generated answer...',")
    print(f"    'original_tokens': 1000,")
    print(f"    'compressed_tokens': 300,")
    print(f"    'compression_ratio': 3.33,")
    print(f"    'tokens_saved': 700")
    print(f"  }}")

    print(f"\nTo use with real model:")
    print("  1. Train RoT model (see MODEL_TRAINING.md)")
    print("  2. Copy checkpoints to checkpoints/")
    print("  3. Run this example again")


def example_4_data_folder_usage():
    """Example 4: Using RoT with custom data folder."""
    print_section("Example 4: Using Custom Data Folder")

    import os

    # Get configured data folder
    data_folder = os.environ.get('DATA_FOLDER', str(Path.cwd() / 'data'))

    print(f"Configured data folder: {data_folder}")
    print(f"\nTo use RoT with your documents:")
    print(f"  1. Place documents in: {data_folder}")
    print(f"  2. Supported formats: PDF, TXT, MD, DOCX, images")
    print(f"  3. RoT will automatically compress and index them")

    # Check if data folder exists and has files
    data_path = Path(data_folder)
    if data_path.exists():
        files = list(data_path.glob('*'))
        if files:
            print(f"\nFound {len(files)} file(s) in data folder:")
            for f in files[:5]:  # Show first 5
                print(f"  - {f.name} ({f.stat().st_size / 1024:.1f} KB)")
            if len(files) > 5:
                print(f"  ... and {len(files) - 5} more")
        else:
            print(f"\nData folder is empty. Add documents to get started!")
    else:
        print(f"\nData folder doesn't exist yet. It will be created on first use.")


def example_5_mcp_integration():
    """Example 5: Understanding MCP integration."""
    print_section("Example 5: MCP Integration Guide")

    print("RoT is an MCP (Model Context Protocol) server.")
    print("\nWhat this means:")
    print("  - Can be used with Claude Desktop")
    print("  - Can be used with any MCP-compatible client")
    print("  - Provides tools that AI models can call")

    print("\nAvailable MCP tools:")
    print("  1. compress_and_generate - Main reasoning function")
    print("  2. assess_complexity - Analyze query complexity")
    print("  3. get_model_info - Check model status")

    print("\nTo use with Claude Desktop:")
    print("  1. Add RoT to claude_desktop_config.json (see setup output)")
    print("  2. Restart Claude Desktop")
    print("  3. Ask Claude to use RoT for complex reasoning")

    print("\nExample conversation with Claude:")
    print('  You: "Use RoT to analyze this document: [paste doc]"')
    print('  Claude: [Uses compress_and_generate tool internally]')
    print('  Claude: "Based on RoT analysis, ..."')


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("RoT Reasoning Server - Example Usage")
    print("="*60)

    print("\nThis script demonstrates various ways to use RoT.")
    print("Running all examples...\n")

    try:
        example_1_model_info()
        example_2_assess_complexity()
        example_3_compress_and_generate()
        example_4_data_folder_usage()
        example_5_mcp_integration()

        print("\n" + "="*60)
        print("Examples Complete!")
        print("="*60)

        print("\nNext steps:")
        print("  - Train RoT model (see MODEL_TRAINING.md)")
        print("  - Integrate with Claude Desktop (see setup output)")
        print("  - Run benchmarks (python benchmarks/run_benchmarks.py)")
        print("  - Read QUICK_START.md for more tutorials")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
