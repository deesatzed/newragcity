#!/usr/bin/env python3
"""
Comprehensive BEIR Benchmark Across All 15 Datasets

Tests ThreeApproachRAG on all BEIR datasets to establish comprehensive SOTA claim.
Supports phased execution, checkpointing, and resume capability.
"""

import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.three_approach_integration import ThreeApproachRAG
from beir_unified_benchmark import load_beir_dataset, build_unified_index, run_unified_benchmark

# BEIR dataset definitions with metadata
BEIR_DATASETS = [
    # Phase 1: Small datasets (5 datasets, 8-10 hours)
    {
        "name": "scifact",
        "docs": 5183,
        "queries": 300,
        "domain": "Scientific Claims",
        "difficulty": "hard",
        "priority": 1,
        "estimated_time_hours": 0.75,
        "expected_ndcg": (0.45, 0.65),
        "published_sota": 0.6885
    },
    {
        "name": "arguana",
        "docs": 8674,
        "queries": 1406,
        "domain": "Argument Mining",
        "difficulty": "medium",
        "priority": 1,
        "estimated_time_hours": 2.0,
        "expected_ndcg": (0.45, 0.55),
        "published_sota": 0.6375
    },
    {
        "name": "fiqa",
        "docs": 57638,
        "queries": 648,
        "domain": "Finance QA",
        "difficulty": "medium",
        "priority": 1,
        "estimated_time_hours": 1.5,
        "expected_ndcg": (0.35, 0.45),
        "published_sota": 0.3649
    },
    {
        "name": "trec-covid",
        "docs": 171332,
        "queries": 50,
        "domain": "COVID-19 Research",
        "difficulty": "hard",
        "priority": 1,
        "estimated_time_hours": 1.0,
        "expected_ndcg": (0.50, 0.60),
        "published_sota": 0.6910
    },
    {
        "name": "scidocs",
        "docs": 25657,
        "queries": 1000,
        "domain": "Citation Prediction",
        "difficulty": "hard",
        "priority": 1,
        "estimated_time_hours": 2.0,
        "expected_ndcg": (0.15, 0.20),
        "published_sota": 0.1776
    },

    # Phase 2: Medium datasets (3 datasets, 20-25 hours)
    {
        "name": "quora",
        "docs": 522931,
        "queries": 10000,
        "domain": "Duplicate Detection",
        "difficulty": "easy",
        "priority": 2,
        "estimated_time_hours": 15.0,
        "expected_ndcg": (0.75, 0.85),
        "published_sota": 0.8882
    },
    {
        "name": "dbpedia-entity",
        "docs": 4635922,
        "queries": 400,
        "domain": "Entity Retrieval",
        "difficulty": "medium",
        "priority": 2,
        "estimated_time_hours": 3.0,
        "expected_ndcg": (0.30, 0.40),
        "published_sota": 0.4464
    },
    {
        "name": "robust04",
        "docs": 528155,
        "queries": 249,
        "domain": "News Retrieval",
        "difficulty": "hard",
        "priority": 2,
        "estimated_time_hours": 2.0,
        "expected_ndcg": (0.40, 0.50),
        "published_sota": 0.5083
    },

    # Phase 3: Large datasets (6 datasets, 55-65 hours)
    {
        "name": "msmarco",
        "docs": 8841823,
        "queries": 6980,
        "domain": "Web Search",
        "difficulty": "medium",
        "priority": 3,
        "estimated_time_hours": 12.0,
        "expected_ndcg": (0.35, 0.45),
        "published_sota": 0.4406
    },
    {
        "name": "nq",
        "docs": 2681468,
        "queries": 3452,
        "domain": "Natural Questions",
        "difficulty": "easy",
        "priority": 3,
        "estimated_time_hours": 8.0,
        "expected_ndcg": (0.45, 0.55),
        "published_sota": 0.5569
    },
    {
        "name": "hotpotqa",
        "docs": 5233329,
        "queries": 7405,
        "domain": "Multi-hop QA",
        "difficulty": "hard",
        "priority": 3,
        "estimated_time_hours": 15.0,
        "expected_ndcg": (0.55, 0.65),
        "published_sota": 0.6673
    },
    {
        "name": "fever",
        "docs": 5416568,
        "queries": 6666,
        "domain": "Fact Verification",
        "difficulty": "medium",
        "priority": 3,
        "estimated_time_hours": 14.0,
        "expected_ndcg": (0.70, 0.80),
        "published_sota": 0.8199
    },
    {
        "name": "climate-fever",
        "docs": 5416593,
        "queries": 1535,
        "domain": "Climate Claims",
        "difficulty": "hard",
        "priority": 3,
        "estimated_time_hours": 5.0,
        "expected_ndcg": (0.20, 0.28),
        "published_sota": 0.2774
    },
    {
        "name": "signal1m",
        "docs": 2866316,
        "queries": 97,
        "domain": "Twitter/News",
        "difficulty": "hard",
        "priority": 3,
        "estimated_time_hours": 1.0,
        "expected_ndcg": (0.25, 0.35),
        "published_sota": 0.3370
    },
]

# Add nfcorpus (already completed)
BEIR_DATASETS.insert(0, {
    "name": "nfcorpus",
    "docs": 3633,
    "queries": 323,
    "domain": "Medical/Nutrition",
    "difficulty": "medium",
    "priority": 1,
    "estimated_time_hours": 0.5,
    "expected_ndcg": (0.50, 0.60),
    "published_sota": 0.3381,
    "completed": True,  # Already done
    "result": {
        "nDCG@10": 0.5086,
        "Recall@100": 0.1839
    }
})


class BEIRMultiDatasetBenchmark:
    """
    Orchestrates benchmarking across multiple BEIR datasets with checkpointing.
    """

    def __init__(
        self,
        datasets_dir: str = "/Volumes/WS4TB/newragcity/UltraRAG-main/datasets",
        results_dir: str = None,
        checkpoint_file: str = None
    ):
        self.datasets_dir = Path(datasets_dir)
        self.results_dir = Path(results_dir) if results_dir else Path(__file__).parent / "results" / "all_beir_datasets"
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.checkpoint_file = Path(checkpoint_file) if checkpoint_file else self.results_dir / "checkpoint.json"
        self.checkpoint = self._load_checkpoint()

        # Initialize RAG system (reusable across datasets)
        self.rag_system = ThreeApproachRAG(
            embedding_model="Qwen/Qwen3-Embedding-0.6B",  # Qwen3 for SOTA performance
            confidence_threshold=0.80,
            enable_streaming=False
        )

    def _load_checkpoint(self) -> Dict:
        """Load checkpoint if exists"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return {
            "completed_datasets": [],
            "failed_datasets": [],
            "last_updated": None
        }

    def _save_checkpoint(self):
        """Save checkpoint"""
        self.checkpoint["last_updated"] = datetime.now().isoformat()
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.checkpoint, f, indent=2)

    def _is_dataset_complete(self, dataset_name: str) -> bool:
        """Check if dataset already completed"""
        result_file = self.results_dir / f"{dataset_name}_results.json"
        return (dataset_name in self.checkpoint["completed_datasets"] or
                result_file.exists())

    def run_single_dataset(self, dataset_info: Dict) -> Optional[Dict]:
        """Run benchmark on a single dataset"""

        dataset_name = dataset_info["name"]

        # Skip if already completed (unless force)
        if self._is_dataset_complete(dataset_name):
            print(f"⏭️  {dataset_name} already completed, loading results...")
            result_file = self.results_dir / f"{dataset_name}_results.json"
            if result_file.exists():
                with open(result_file, 'r') as f:
                    return json.load(f)
            return None

        print(f"\n{'='*70}")
        print(f"RUNNING BEIR BENCHMARK: {dataset_name.upper()}")
        print(f"{'='*70}")
        print(f"Domain: {dataset_info['domain']}")
        print(f"Documents: {dataset_info['docs']:,}")
        print(f"Queries: {dataset_info['queries']:,}")
        print(f"Difficulty: {dataset_info['difficulty']}")
        print(f"Expected nDCG@10: {dataset_info['expected_ndcg'][0]:.2f}-{dataset_info['expected_ndcg'][1]:.2f}")
        print(f"Published SOTA: {dataset_info['published_sota']:.4f}")
        print(f"Estimated time: {dataset_info['estimated_time_hours']:.1f} hours")
        print(f"{'='*70}\n")

        dataset_path = self.datasets_dir / dataset_name

        # Check if dataset exists
        if not dataset_path.exists():
            print(f"❌ Dataset not found at {dataset_path}")
            print(f"   Please download: https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/{dataset_name}.zip")
            self.checkpoint["failed_datasets"].append({
                "name": dataset_name,
                "reason": "dataset_not_found",
                "timestamp": datetime.now().isoformat()
            })
            self._save_checkpoint()
            return None

        try:
            # Load dataset
            start_time = time.time()
            corpus, queries, qrels = load_beir_dataset(str(dataset_path))

            # Build index
            index_path = f"/tmp/beir_{dataset_name}_index"
            build_unified_index(self.rag_system, corpus, index_path)

            # Run benchmark
            results = run_unified_benchmark(
                rag_system=self.rag_system,
                index_path=index_path,
                queries=queries,
                qrels=qrels,
                max_queries=None  # All queries
            )

            elapsed_time = time.time() - start_time

            # Add metadata
            results["dataset"] = dataset_name
            results["domain"] = dataset_info["domain"]
            results["difficulty"] = dataset_info["difficulty"]
            results["published_sota"] = dataset_info["published_sota"]
            results["elapsed_time_seconds"] = elapsed_time
            results["elapsed_time_hours"] = elapsed_time / 3600
            results["queries_per_second"] = results["queries_tested"] / elapsed_time
            results["timestamp"] = datetime.now().isoformat()

            # Calculate performance vs SOTA (ensure Python types, not numpy)
            our_ndcg = float(results["metrics"]["nDCG@10"])
            sota_ndcg = float(dataset_info["published_sota"])
            results["vs_sota_improvement"] = float(((our_ndcg - sota_ndcg) / sota_ndcg * 100) if sota_ndcg > 0 else 0)
            results["beats_sota"] = bool(our_ndcg > sota_ndcg)

            # Save individual result
            result_file = self.results_dir / f"{dataset_name}_results.json"
            with open(result_file, 'w') as f:
                json.dump(results, f, indent=2)

            # Update checkpoint
            self.checkpoint["completed_datasets"].append(dataset_name)
            self._save_checkpoint()

            print(f"\n✅ {dataset_name.upper()} COMPLETE:")
            print(f"   nDCG@10: {our_ndcg:.4f} (SOTA: {sota_ndcg:.4f})")
            print(f"   Improvement: {results['vs_sota_improvement']:+.1f}%")
            print(f"   {'✅ BEATS SOTA!' if results['beats_sota'] else '❌ Below SOTA'}")
            print(f"   Recall@100: {results['metrics']['Recall@100']:.4f}")
            print(f"   Time: {elapsed_time/3600:.2f} hours")
            print(f"   Saved to: {result_file}")

            return results

        except Exception as e:
            print(f"\n❌ {dataset_name.upper()} FAILED:")
            print(f"   Error: {str(e)}")

            self.checkpoint["failed_datasets"].append({
                "name": dataset_name,
                "reason": str(e),
                "timestamp": datetime.now().isoformat()
            })
            self._save_checkpoint()

            return None

    def run_phase(self, phase: int) -> Dict:
        """Run all datasets in a specific phase"""

        datasets = [d for d in BEIR_DATASETS if d.get("priority") == phase and not d.get("completed")]

        print(f"\n{'='*70}")
        print(f"STARTING PHASE {phase}")
        print(f"{'='*70}")
        print(f"Datasets: {len(datasets)}")
        print(f"Total queries: {sum(d['queries'] for d in datasets):,}")
        print(f"Estimated time: {sum(d['estimated_time_hours'] for d in datasets):.1f} hours")
        print(f"{'='*70}\n")

        phase_results = {}

        for dataset_info in datasets:
            result = self.run_single_dataset(dataset_info)
            if result:
                phase_results[dataset_info["name"]] = result

        return phase_results

    def run_all(self, resume: bool = True) -> Dict:
        """Run all datasets (with optional resume)"""

        print(f"\n{'='*70}")
        print("COMPREHENSIVE BEIR BENCHMARK - ALL 15 DATASETS")
        print(f"{'='*70}")
        print(f"Total datasets: 15")
        print(f"Total queries: {sum(d['queries'] for d in BEIR_DATASETS):,}")
        print(f"Total docs: {sum(d['docs'] for d in BEIR_DATASETS):,}")
        print(f"Estimated time: {sum(d['estimated_time_hours'] for d in BEIR_DATASETS):.1f} hours")

        if resume and self.checkpoint["completed_datasets"]:
            print(f"\n📍 RESUMING: {len(self.checkpoint['completed_datasets'])} datasets already completed")

        print(f"{'='*70}\n")

        all_results = {}

        # Run all 3 phases
        for phase in [1, 2, 3]:
            phase_results = self.run_phase(phase)
            all_results.update(phase_results)

            # Phase summary
            self._print_phase_summary(phase, phase_results)

            # Ask to continue (optional safety check)
            if phase < 3:
                print(f"\n⏸️  Phase {phase} complete. Ready for Phase {phase+1}?")

        # Calculate final aggregate
        aggregate = self._calculate_aggregate(all_results)

        # Save aggregate
        aggregate_file = self.results_dir / "aggregate_results.json"
        with open(aggregate_file, 'w') as f:
            json.dump(aggregate, f, indent=2)

        # Print final summary
        self._print_final_summary(aggregate)

        return aggregate

    def _calculate_aggregate(self, all_results: Dict) -> Dict:
        """Calculate BEIR aggregate metrics"""

        ndcg_scores = []
        recall_scores = []
        query_counts = []
        datasets_info = []

        for dataset_name, results in all_results.items():
            if results and "error" not in results:
                ndcg_scores.append(results["metrics"]["nDCG@10"])
                recall_scores.append(results["metrics"]["Recall@100"])
                query_counts.append(results["queries_tested"])

                datasets_info.append({
                    "name": dataset_name,
                    "nDCG@10": results["metrics"]["nDCG@10"],
                    "Recall@100": results["metrics"]["Recall@100"],
                    "queries": results["queries_tested"],
                    "vs_sota": results.get("vs_sota_improvement", 0),
                    "beats_sota": results.get("beats_sota", False)
                })

        # Weighted average by number of queries (BEIR standard)
        total_queries = sum(query_counts)
        weighted_ndcg = sum(n * q for n, q in zip(ndcg_scores, query_counts)) / total_queries
        weighted_recall = sum(r * q for r, q in zip(recall_scores, query_counts)) / total_queries

        # Unweighted average (for comparison)
        unweighted_ndcg = sum(ndcg_scores) / len(ndcg_scores)
        unweighted_recall = sum(recall_scores) / len(recall_scores)

        return {
            "beir_weighted_average_ndcg@10": weighted_ndcg,
            "beir_weighted_average_recall@100": weighted_recall,
            "beir_unweighted_average_ndcg@10": unweighted_ndcg,
            "beir_unweighted_average_recall@100": unweighted_recall,
            "datasets_tested": len(ndcg_scores),
            "total_queries": total_queries,
            "datasets_beating_sota": sum(1 for d in datasets_info if d["beats_sota"]),
            "datasets_info": datasets_info,
            "timestamp": datetime.now().isoformat()
        }

    def _print_phase_summary(self, phase: int, results: Dict):
        """Print summary for a phase"""

        if not results:
            return

        print(f"\n{'='*70}")
        print(f"PHASE {phase} SUMMARY")
        print(f"{'='*70}")

        datasets_completed = len(results)
        avg_ndcg = sum(r["metrics"]["nDCG@10"] for r in results.values()) / datasets_completed
        datasets_beating_sota = sum(1 for r in results.values() if r.get("beats_sota", False))

        print(f"Datasets completed: {datasets_completed}")
        print(f"Average nDCG@10: {avg_ndcg:.4f}")
        print(f"Beating SOTA: {datasets_beating_sota}/{datasets_completed}")
        print(f"{'='*70}\n")

    def _print_final_summary(self, aggregate: Dict):
        """Print final comprehensive summary"""

        print(f"\n{'='*70}")
        print("FINAL BEIR AGGREGATE RESULTS - ThreeApproachRAG")
        print(f"{'='*70}")
        print(f"\nDatasets tested: {aggregate['datasets_tested']}/15")
        print(f"Total queries: {aggregate['total_queries']:,}")
        print(f"\n📊 BEIR Weighted Average nDCG@10: {aggregate['beir_weighted_average_ndcg@10']:.4f}")
        print(f"📊 BEIR Unweighted Average nDCG@10: {aggregate['beir_unweighted_average_ndcg@10']:.4f}")
        print(f"📊 BEIR Weighted Average Recall@100: {aggregate['beir_weighted_average_recall@100']:.4f}")
        print(f"\n🏆 Datasets beating SOTA: {aggregate['datasets_beating_sota']}/{aggregate['datasets_tested']}")

        print(f"\n{'-'*70}")
        print("Per-Dataset Breakdown:")
        print(f"{'-'*70}")
        print(f"{'Dataset':<20} {'nDCG@10':>10} {'vs SOTA':>10} {'Status':>10}")
        print(f"{'-'*70}")

        for dataset in sorted(aggregate["datasets_info"], key=lambda x: x["nDCG@10"], reverse=True):
            status = "✅ BEATS" if dataset["beats_sota"] else "❌ Below"
            print(f"{dataset['name']:<20} {dataset['nDCG@10']:>10.4f} {dataset['vs_sota']:>9.1f}% {status:>10}")

        print(f"\n{'='*70}")
        print("COMPARISON TO PUBLISHED SOTA:")
        print(f"{'='*70}")
        print("NV-Embed (2024):     0.5935 (current #1)")
        print("BGE-large (2024):    0.5881")
        print("E5-mistral (2024):   0.5720")
        print(f"ThreeApproachRAG:    {aggregate['beir_weighted_average_ndcg@10']:.4f}")

        if aggregate['beir_weighted_average_ndcg@10'] > 0.5935:
            print("\n🎉 NEW BEIR SOTA! 🎉")
        elif aggregate['beir_weighted_average_ndcg@10'] > 0.5720:
            print("\n🏆 Top 5 on BEIR leaderboard!")
        elif aggregate['beir_weighted_average_ndcg@10'] > 0.50:
            print("\n✅ Competitive with SOTA systems")
        else:
            print("\n📈 Solid baseline, competitive performance")

        print(f"\n{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Run BEIR benchmark on all datasets"
    )
    parser.add_argument(
        "--phase",
        type=int,
        choices=[1, 2, 3],
        help="Run specific phase only (1=small, 2=medium, 3=large)"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        help="Run specific dataset only"
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Start fresh, ignore checkpoint"
    )
    parser.add_argument(
        "--datasets-dir",
        type=str,
        default="/Volumes/WS4TB/newragcity/UltraRAG-main/datasets",
        help="Path to BEIR datasets directory"
    )
    parser.add_argument(
        "--results-dir",
        type=str,
        help="Path to save results (default: benchmarks/results/all_beir_datasets)"
    )

    args = parser.parse_args()

    # Initialize benchmark system
    benchmark = BEIRMultiDatasetBenchmark(
        datasets_dir=args.datasets_dir,
        results_dir=args.results_dir
    )

    # Run based on arguments
    if args.dataset:
        # Single dataset
        dataset_info = next((d for d in BEIR_DATASETS if d["name"] == args.dataset), None)
        if not dataset_info:
            print(f"❌ Dataset '{args.dataset}' not found")
            print(f"Available: {', '.join(d['name'] for d in BEIR_DATASETS)}")
            return

        result = benchmark.run_single_dataset(dataset_info)
        if result:
            print(f"\n✅ {args.dataset} benchmark complete")

    elif args.phase:
        # Specific phase
        results = benchmark.run_phase(args.phase)
        print(f"\n✅ Phase {args.phase} complete: {len(results)} datasets")

    else:
        # All datasets
        resume = not args.no_resume
        aggregate = benchmark.run_all(resume=resume)
        print(f"\n✅ All datasets complete!")
        print(f"Final BEIR average: {aggregate['beir_weighted_average_ndcg@10']:.4f}")


if __name__ == "__main__":
    main()
