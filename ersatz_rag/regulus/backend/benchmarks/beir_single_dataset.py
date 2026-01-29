#!/usr/bin/env python3
"""
Single Dataset BEIR Benchmark Worker

Runs benchmark on a single BEIR dataset. Designed to be called by parallel runner.

Usage:
    python beir_single_dataset.py --dataset scifact --datasets-dir /path/to/datasets --results-dir /path/to/results
"""

import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from beir_all_datasets import BEIR_DATASETS, BEIRMultiDatasetBenchmark


def run_single_dataset(
    dataset_name: str,
    datasets_dir: str,
    results_dir: str
) -> bool:
    """
    Run benchmark on a single dataset.

    Returns:
        True if successful, False if failed
    """
    # Find dataset info
    dataset_info = None
    for ds in BEIR_DATASETS:
        if ds["name"] == dataset_name:
            dataset_info = ds
            break

    if not dataset_info:
        print(f"❌ Unknown dataset: {dataset_name}")
        return False

    print(f"{'='*70}")
    print(f"BEIR BENCHMARK - {dataset_name}")
    print(f"{'='*70}")
    print(f"Domain: {dataset_info['domain']}")
    print(f"Difficulty: {dataset_info['difficulty']}")
    print(f"Published SOTA: {dataset_info['published_sota']:.4f}")
    print(f"{'='*70}\n")

    # Initialize benchmark system
    benchmark = BEIRMultiDatasetBenchmark(
        datasets_dir=datasets_dir,
        results_dir=results_dir
    )

    # Run benchmark
    start_time = time.time()

    try:
        results = benchmark.run_single_dataset(dataset_info)

        if results:
            elapsed = time.time() - start_time

            print(f"\n{'='*70}")
            print(f"✅ BENCHMARK COMPLETE - {dataset_name}")
            print(f"{'='*70}")
            print(f"nDCG@10:         {results['metrics']['nDCG@10']:.4f}")
            print(f"Recall@100:      {results['metrics']['Recall@100']:.4f}")
            print(f"Published SOTA:  {dataset_info['published_sota']:.4f}")
            print(f"vs SOTA:         {results['vs_sota_improvement']:+.1f}%")
            print(f"Beats SOTA:      {'✅ YES' if results['beats_sota'] else '❌ NO'}")
            print(f"Elapsed time:    {elapsed/3600:.2f} hours")
            print(f"Queries tested:  {results['queries_tested']}")
            print(f"{'='*70}\n")

            return True
        else:
            print(f"\n❌ Benchmark failed for {dataset_name}")
            return False

    except Exception as e:
        print(f"\n❌ Exception during benchmark: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description="Run BEIR benchmark on single dataset")
    parser.add_argument("--dataset", required=True, help="Dataset name (e.g., scifact)")
    parser.add_argument("--datasets-dir", required=True, help="Directory containing BEIR datasets")
    parser.add_argument("--results-dir", required=True, help="Directory to save results")

    args = parser.parse_args()

    success = run_single_dataset(
        dataset_name=args.dataset,
        datasets_dir=args.datasets_dir,
        results_dir=args.results_dir
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
