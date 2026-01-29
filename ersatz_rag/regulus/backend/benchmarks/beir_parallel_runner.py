#!/usr/bin/env python3
"""
Parallel BEIR Benchmark Runner

Runs 3 datasets concurrently to maximize throughput while avoiding resource contention.

Key Features:
- 3 concurrent workers (configurable)
- Shared checkpoint system across all workers
- Individual log files per dataset
- Global progress tracking
- Automatic batch scheduling

Time Savings:
- Sequential: ~85-95 hours
- Parallel (3x): ~28-32 hours (3x faster)
"""

import sys
import json
import time
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from beir_all_datasets import BEIR_DATASETS, BEIRMultiDatasetBenchmark


class ParallelBEIRRunner:
    """
    Orchestrates parallel execution of BEIR benchmarks.

    Architecture:
    - Master process spawns 3 worker processes
    - Each worker runs beir_single_dataset.py on one dataset
    - Shared checkpoint file coordinates progress
    - Individual log files prevent output mixing
    """

    def __init__(
        self,
        datasets_dir: str = "/Volumes/WS4TB/newragcity/UltraRAG-main/datasets",
        results_dir: str = None,
        max_workers: int = 3,
        resume: bool = True
    ):
        self.datasets_dir = Path(datasets_dir)
        self.results_dir = Path(results_dir) if results_dir else Path(__file__).parent / "results" / "all_beir_datasets"
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.max_workers = max_workers
        self.resume = resume

        self.checkpoint_file = self.results_dir / "checkpoint.json"
        self.checkpoint = self._load_checkpoint()

        # Log directory for individual dataset logs
        self.log_dir = Path("/tmp/beir_parallel_logs")
        self.log_dir.mkdir(exist_ok=True)

        print(f"Parallel BEIR Runner initialized:")
        print(f"  Results dir: {self.results_dir}")
        print(f"  Max workers: {self.max_workers}")
        print(f"  Resume mode: {self.resume}")
        print(f"  Log dir: {self.log_dir}")

    def _load_checkpoint(self) -> Dict:
        """Load checkpoint or create new one."""
        if self.checkpoint_file.exists() and self.resume:
            with open(self.checkpoint_file, 'r') as f:
                checkpoint = json.load(f)
                print(f"Loaded checkpoint: {len(checkpoint['completed_datasets'])} completed, {len(checkpoint['failed_datasets'])} failed")
                return checkpoint
        else:
            print("Starting fresh (no checkpoint)")
            return {
                "completed_datasets": [],
                "failed_datasets": [],
                "last_updated": None
            }

    def _save_checkpoint(self):
        """Save checkpoint to disk."""
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.checkpoint, f, indent=2)

    def _get_pending_datasets(self) -> List[Dict]:
        """Get list of datasets that haven't been completed yet."""
        completed_names = {ds for ds in self.checkpoint["completed_datasets"]}
        failed_names = {fail["name"] for fail in self.checkpoint["failed_datasets"]}

        pending = []
        for dataset_info in BEIR_DATASETS:
            if dataset_info["name"] not in completed_names and dataset_info["name"] not in failed_names:
                pending.append(dataset_info)

        return pending

    def run_single_dataset(self, dataset_info: Dict) -> Dict:
        """
        Run benchmark on a single dataset (called by worker process).

        This runs as a separate Python process to avoid GIL contention and
        ensure clean memory isolation between datasets.
        """
        dataset_name = dataset_info["name"]
        log_file = self.log_dir / f"{dataset_name}.log"

        print(f"[{dataset_name}] Starting benchmark (log: {log_file})")

        start_time = time.time()

        # Create worker script command
        cmd = [
            sys.executable,
            str(Path(__file__).parent / "beir_single_dataset.py"),
            "--dataset", dataset_name,
            "--datasets-dir", str(self.datasets_dir),
            "--results-dir", str(self.results_dir)
        ]

        try:
            # Run as subprocess with dedicated log file
            with open(log_file, 'w') as f:
                result = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    timeout=36000  # 10 hour timeout per dataset
                )

            elapsed = time.time() - start_time

            if result.returncode == 0:
                print(f"[{dataset_name}] ✅ SUCCESS in {elapsed/3600:.1f} hours")
                return {"status": "success", "dataset": dataset_name, "elapsed": elapsed}
            else:
                print(f"[{dataset_name}] ❌ FAILED (exit code {result.returncode})")
                return {"status": "failed", "dataset": dataset_name, "reason": f"Exit code {result.returncode}"}

        except subprocess.TimeoutExpired:
            print(f"[{dataset_name}] ❌ TIMEOUT after 10 hours")
            return {"status": "failed", "dataset": dataset_name, "reason": "Timeout (>10 hours)"}
        except Exception as e:
            print(f"[{dataset_name}] ❌ ERROR: {e}")
            return {"status": "failed", "dataset": dataset_name, "reason": str(e)}

    def run_all_parallel(self):
        """
        Run all pending datasets in parallel batches.

        Strategy:
        - Get list of pending datasets
        - Submit 3 at a time to ProcessPoolExecutor
        - As each completes, submit next one
        - Update checkpoint after each completion
        """
        pending = self._get_pending_datasets()

        if not pending:
            print("✅ All datasets already completed!")
            return self._generate_summary()

        print(f"\n{'='*70}")
        print(f"PARALLEL BEIR BENCHMARK - {len(pending)} datasets remaining")
        print(f"{'='*70}")
        print(f"Concurrency: {self.max_workers} workers")
        print(f"Estimated time: {len(pending) / self.max_workers * 6.8:.1f} hours (at 6.8h per dataset)")
        print(f"{'='*70}\n")

        total_start = time.time()
        completed_count = 0
        failed_count = 0

        # Use ProcessPoolExecutor for true parallelism (avoids GIL)
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all pending datasets
            future_to_dataset = {
                executor.submit(self.run_single_dataset, ds_info): ds_info
                for ds_info in pending
            }

            # Process completions as they finish
            for future in as_completed(future_to_dataset):
                dataset_info = future_to_dataset[future]
                dataset_name = dataset_info["name"]

                try:
                    result = future.result()

                    if result["status"] == "success":
                        # Update checkpoint with success
                        self.checkpoint["completed_datasets"].append(dataset_name)
                        self.checkpoint["last_updated"] = datetime.now().isoformat()
                        completed_count += 1

                        print(f"\n{'='*70}")
                        print(f"✅ COMPLETED: {dataset_name}")
                        print(f"Progress: {completed_count + len(self.checkpoint['completed_datasets'])} / {len(BEIR_DATASETS)} total datasets")
                        print(f"{'='*70}\n")
                    else:
                        # Update checkpoint with failure
                        self.checkpoint["failed_datasets"].append({
                            "name": dataset_name,
                            "reason": result["reason"],
                            "timestamp": datetime.now().isoformat()
                        })
                        failed_count += 1

                        print(f"\n{'='*70}")
                        print(f"❌ FAILED: {dataset_name}")
                        print(f"Reason: {result['reason']}")
                        print(f"{'='*70}\n")

                    # Save checkpoint after each completion
                    self._save_checkpoint()

                except Exception as e:
                    print(f"\n❌ Exception processing {dataset_name}: {e}")
                    self.checkpoint["failed_datasets"].append({
                        "name": dataset_name,
                        "reason": f"Exception: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    })
                    failed_count += 1
                    self._save_checkpoint()

        total_elapsed = time.time() - total_start

        print(f"\n{'='*70}")
        print(f"PARALLEL BENCHMARK COMPLETE")
        print(f"{'='*70}")
        print(f"Total time: {total_elapsed/3600:.1f} hours")
        print(f"Completed: {completed_count}")
        print(f"Failed: {failed_count}")
        print(f"{'='*70}\n")

        return self._generate_summary()

    def _generate_summary(self) -> Dict:
        """Generate final summary with BEIR aggregate."""
        print("\nGenerating BEIR aggregate results...")

        # Load all individual results
        all_results = {}
        total_queries = 0
        weighted_ndcg_sum = 0.0

        for dataset_name in self.checkpoint["completed_datasets"]:
            result_file = self.results_dir / f"{dataset_name}_results.json"
            if result_file.exists():
                with open(result_file, 'r') as f:
                    results = json.load(f)
                    all_results[dataset_name] = results

                    # Weight by number of queries tested
                    queries = results.get("queries_tested", 0)
                    ndcg = results["metrics"]["nDCG@10"]

                    total_queries += queries
                    weighted_ndcg_sum += ndcg * queries

        # Calculate BEIR aggregate (weighted average)
        beir_aggregate = weighted_ndcg_sum / total_queries if total_queries > 0 else 0.0

        summary = {
            "beir_aggregate_ndcg10": float(beir_aggregate),
            "total_datasets_completed": len(self.checkpoint["completed_datasets"]),
            "total_datasets_failed": len(self.checkpoint["failed_datasets"]),
            "total_queries_tested": total_queries,
            "completed_datasets": self.checkpoint["completed_datasets"],
            "failed_datasets": self.checkpoint["failed_datasets"],
            "per_dataset_results": all_results,
            "timestamp": datetime.now().isoformat()
        }

        # Compare to SOTA (NV-Embed: 0.5935)
        sota_beir_aggregate = 0.5935
        summary["vs_sota_improvement"] = float(((beir_aggregate - sota_beir_aggregate) / sota_beir_aggregate * 100) if sota_beir_aggregate > 0 else 0)
        summary["beats_sota"] = bool(beir_aggregate > sota_beir_aggregate)

        # Save summary
        summary_file = self.results_dir / "beir_aggregate_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n{'='*70}")
        print(f"BEIR AGGREGATE RESULTS")
        print(f"{'='*70}")
        print(f"BEIR Average nDCG@10: {beir_aggregate:.4f}")
        print(f"SOTA (NV-Embed):      {sota_beir_aggregate:.4f}")
        print(f"vs SOTA:              {summary['vs_sota_improvement']:+.1f}%")
        print(f"Beats SOTA:           {'✅ YES' if summary['beats_sota'] else '❌ NO'}")
        print(f"")
        print(f"Datasets completed:   {len(self.checkpoint['completed_datasets'])}")
        print(f"Total queries tested: {total_queries}")
        print(f"{'='*70}\n")

        return summary


def main():
    parser = argparse.ArgumentParser(description="Run BEIR benchmarks in parallel")
    parser.add_argument("--datasets-dir", default="/Volumes/WS4TB/newragcity/UltraRAG-main/datasets",
                        help="Directory containing BEIR datasets")
    parser.add_argument("--results-dir", default=None,
                        help="Directory to save results")
    parser.add_argument("--workers", type=int, default=3,
                        help="Number of concurrent workers (default: 3)")
    parser.add_argument("--no-resume", action="store_true",
                        help="Start fresh instead of resuming from checkpoint")

    args = parser.parse_args()

    runner = ParallelBEIRRunner(
        datasets_dir=args.datasets_dir,
        results_dir=args.results_dir,
        max_workers=args.workers,
        resume=not args.no_resume
    )

    try:
        summary = runner.run_all_parallel()
        sys.exit(0 if summary["total_datasets_failed"] == 0 else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Progress saved to checkpoint.")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
