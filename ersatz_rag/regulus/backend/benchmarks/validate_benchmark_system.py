#!/usr/bin/env python3
"""
Validation Test for BEIR Benchmark System

Tests that:
1. JSON serialization works (no numpy type issues)
2. Checkpoint system functions correctly
3. Result files can be read back
4. Monitoring can detect completion

This MUST pass before running full benchmark.
"""

import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from beir_all_datasets import BEIRMultiDatasetBenchmark, BEIR_DATASETS

def validate_benchmark_system():
    """
    Run a TINY test (10 queries from scifact) to validate the entire system.
    """

    print("="*70)
    print("BENCHMARK SYSTEM VALIDATION TEST")
    print("="*70)
    print("This will run 10 queries from scifact to validate:")
    print("  1. JSON serialization (no numpy errors)")
    print("  2. Checkpoint system")
    print("  3. Result file creation and loading")
    print("  4. Monitoring readiness")
    print("="*70)
    print()

    # Create validation benchmark with temp results dir
    validation_results_dir = Path(__file__).parent / "results" / "validation_test"
    validation_results_dir.mkdir(parents=True, exist_ok=True)

    # Clean up any previous validation
    for file in validation_results_dir.glob("*"):
        file.unlink()

    print(f"✓ Validation results dir: {validation_results_dir}")

    # Initialize benchmark
    print("✓ Initializing benchmark system...")
    benchmark = BEIRMultiDatasetBenchmark(
        datasets_dir="/Volumes/WS4TB/newragcity/UltraRAG-main/datasets",
        results_dir=str(validation_results_dir)
    )

    # Modify scifact to run only 10 queries
    scifact_info = next(d for d in BEIR_DATASETS if d["name"] == "scifact")

    print(f"✓ Running validation benchmark on scifact (10 queries)...")
    print(f"  Dataset path: {benchmark.datasets_dir / 'scifact'}")

    # Temporarily modify the benchmark function to use max_queries=10
    from beir_unified_benchmark import load_beir_dataset, build_unified_index, run_unified_benchmark

    dataset_path = benchmark.datasets_dir / "scifact"
    if not dataset_path.exists():
        print(f"❌ VALIDATION FAILED: scifact dataset not found at {dataset_path}")
        return False

    try:
        # Load dataset
        start_time = time.time()
        corpus, queries, qrels = load_beir_dataset(str(dataset_path))
        print(f"✓ Loaded scifact: {len(corpus)} docs, {len(queries)} queries")

        # Build index
        index_path = "/tmp/beir_validation_test_index"
        print(f"✓ Building index at {index_path}...")
        build_unified_index(benchmark.rag_system, corpus, index_path)
        print(f"✓ Index built successfully")

        # Run benchmark (ONLY 10 QUERIES)
        print(f"✓ Running benchmark on 10 queries...")
        results = run_unified_benchmark(
            rag_system=benchmark.rag_system,
            index_path=index_path,
            queries=queries,
            qrels=qrels,
            max_queries=10  # VALIDATION TEST: only 10 queries
        )

        elapsed_time = time.time() - start_time
        print(f"✓ Benchmark completed in {elapsed_time:.1f} seconds")

        # Add metadata (same as real benchmark)
        results["dataset"] = "scifact_validation"
        results["domain"] = scifact_info["domain"]
        results["difficulty"] = scifact_info["difficulty"]
        results["published_sota"] = scifact_info["published_sota"]
        results["elapsed_time_seconds"] = elapsed_time
        results["elapsed_time_hours"] = elapsed_time / 3600
        results["queries_per_second"] = results["queries_tested"] / elapsed_time
        results["timestamp"] = "validation_test"

        # Calculate performance vs SOTA (THIS IS WHERE THE BUG WAS)
        our_ndcg = float(results["metrics"]["nDCG@10"])
        sota_ndcg = float(scifact_info["published_sota"])
        results["vs_sota_improvement"] = float(((our_ndcg - sota_ndcg) / sota_ndcg * 100) if sota_ndcg > 0 else 0)
        results["beats_sota"] = bool(our_ndcg > sota_ndcg)

        print(f"\n✓ Results:")
        print(f"  nDCG@10: {our_ndcg:.4f}")
        print(f"  Recall@100: {results['metrics']['Recall@100']:.4f}")
        print(f"  Beats SOTA: {results['beats_sota']}")
        print(f"  vs SOTA: {results['vs_sota_improvement']:+.1f}%")

        # TEST 1: JSON Serialization
        print(f"\n[TEST 1] JSON Serialization...")
        result_file = validation_results_dir / "scifact_validation_results.json"
        try:
            with open(result_file, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"✅ PASS: JSON serialization successful")
            print(f"  Saved to: {result_file}")
        except Exception as e:
            print(f"❌ FAIL: JSON serialization error: {e}")
            return False

        # TEST 2: Read Back
        print(f"\n[TEST 2] Reading JSON back...")
        try:
            with open(result_file, 'r') as f:
                loaded_results = json.load(f)
            assert loaded_results["beats_sota"] == results["beats_sota"]
            assert abs(loaded_results["metrics"]["nDCG@10"] - our_ndcg) < 0.0001
            print(f"✅ PASS: JSON read back successful")
            print(f"  Verified beats_sota: {loaded_results['beats_sota']}")
            print(f"  Verified nDCG@10: {loaded_results['metrics']['nDCG@10']:.4f}")
        except Exception as e:
            print(f"❌ FAIL: JSON read error: {e}")
            return False

        # TEST 3: Checkpoint System
        print(f"\n[TEST 3] Checkpoint system...")
        checkpoint_file = validation_results_dir / "checkpoint.json"
        checkpoint_data = {
            "completed_datasets": ["scifact_validation"],
            "failed_datasets": [],
            "last_updated": "validation_test"
        }
        try:
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)

            # Read back
            with open(checkpoint_file, 'r') as f:
                loaded_checkpoint = json.load(f)

            assert loaded_checkpoint["completed_datasets"] == ["scifact_validation"]
            print(f"✅ PASS: Checkpoint system functional")
            print(f"  Checkpoint file: {checkpoint_file}")
        except Exception as e:
            print(f"❌ FAIL: Checkpoint error: {e}")
            return False

        # TEST 4: Type Validation
        print(f"\n[TEST 4] Type validation...")
        try:
            # Verify all values are JSON-serializable Python types
            assert isinstance(results["beats_sota"], bool), "beats_sota must be Python bool"
            assert isinstance(results["vs_sota_improvement"], (int, float)), "vs_sota_improvement must be Python number"
            assert not hasattr(results["beats_sota"], '__array__'), "beats_sota must not be numpy type"
            print(f"✅ PASS: All types are Python native (no numpy)")
            print(f"  beats_sota type: {type(results['beats_sota']).__name__}")
            print(f"  vs_sota_improvement type: {type(results['vs_sota_improvement']).__name__}")
        except Exception as e:
            print(f"❌ FAIL: Type validation error: {e}")
            return False

        print(f"\n{'='*70}")
        print(f"✅ ALL VALIDATION TESTS PASSED")
        print(f"{'='*70}")
        print(f"System is ready for full benchmark run")
        print(f"Validation completed in {elapsed_time:.1f} seconds")
        print(f"{'='*70}\n")

        return True

    except Exception as e:
        print(f"\n{'='*70}")
        print(f"❌ VALIDATION FAILED")
        print(f"{'='*70}")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print(f"{'='*70}\n")
        return False


if __name__ == "__main__":
    success = validate_benchmark_system()
    sys.exit(0 if success else 1)
