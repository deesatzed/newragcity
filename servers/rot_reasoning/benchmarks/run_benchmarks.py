#!/usr/bin/env python3
"""
RoT Reasoning Server - Automated Benchmark Runner

Usage:
    python run_benchmarks.py --benchmarks all --output results/
    python run_benchmarks.py --benchmarks BEIR,CRAG --baselines vanilla,graph
    python run_benchmarks.py --quick-test  # Fast smoke test
"""

import argparse
import json
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from rot_evaluator import RoTEvaluator
    from baselines import VanillaRAG, GraphRAG
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error("Make sure evaluator modules are implemented in benchmarks/")
    sys.exit(1)


# Benchmark configurations
BENCHMARKS = {
    'BEIR': {
        'datasets': ['nfcorpus', 'scifact', 'fiqa'],
        'metrics': ['ndcg@10', 'recall@100', 'mrr'],
        'description': 'Standard retrieval benchmark (18 datasets)',
    },
    'CRAG': {
        'datasets': ['crag_multi_hop'],
        'metrics': ['faithfulness', 'accuracy', 'f1'],
        'description': 'Challenging end-to-end RAG benchmark',
    },
    'Efficiency': {
        'datasets': ['custom_efficiency'],
        'metrics': ['compression_ratio', 'speedup', 'cost_reduction'],
        'description': 'RoT-specific efficiency metrics',
    },
    'LongBench': {
        'datasets': ['longbench_rag'],
        'metrics': ['recall@k', 'accuracy'],
        'description': 'Long-context RAG evaluation',
    },
}

# Quick test configuration (for smoke testing)
QUICK_TEST = {
    'BEIR_Small': {
        'datasets': ['nfcorpus'],
        'metrics': ['ndcg@10'],
        'sample_size': 100,  # Use only 100 queries
    },
}


class BenchmarkRunner:
    """Main benchmark orchestration class."""

    def __init__(
        self,
        output_dir: str = "results",
        runs_per_experiment: int = 3,
        random_seeds: List[int] = None,
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.runs_per_experiment = runs_per_experiment
        self.random_seeds = random_seeds or [42, 123, 456]

        logger.info(f"Benchmark runner initialized")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Runs per experiment: {self.runs_per_experiment}")

    def run_all_benchmarks(
        self,
        benchmark_names: List[str],
        baseline_names: List[str],
        quick_test: bool = False,
    ) -> Dict[str, Any]:
        """Run all specified benchmarks."""

        results = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'benchmark_names': benchmark_names,
                'baseline_names': baseline_names,
                'runs_per_experiment': self.runs_per_experiment,
                'quick_test': quick_test,
            },
            'benchmarks': {},
        }

        # Initialize evaluators
        logger.info("Initializing evaluators...")
        evaluators = self._init_evaluators(baseline_names)

        # Select benchmark configs
        configs = QUICK_TEST if quick_test else BENCHMARKS

        # Run each benchmark
        for bench_name in benchmark_names:
            if bench_name not in configs:
                logger.warning(f"Unknown benchmark: {bench_name}, skipping")
                continue

            logger.info(f"\n{'='*60}")
            logger.info(f"Running {bench_name}")
            logger.info(f"{'='*60}")

            bench_config = configs[bench_name]
            bench_results = {}

            # Evaluate each method
            for method_name, evaluator in evaluators.items():
                logger.info(f"\nEvaluating {method_name}...")
                start_time = time.time()

                try:
                    method_results = self._run_single_benchmark(
                        evaluator=evaluator,
                        config=bench_config,
                    )
                    bench_results[method_name] = method_results

                    elapsed = time.time() - start_time
                    logger.info(f"✓ {method_name} completed in {elapsed:.2f}s")

                except Exception as e:
                    logger.error(f"✗ {method_name} failed: {e}")
                    bench_results[method_name] = {'error': str(e)}

            results['benchmarks'][bench_name] = bench_results

        # Save results
        self._save_results(results)

        # Print summary
        self._print_summary(results)

        return results

    def _init_evaluators(self, baseline_names: List[str]) -> Dict[str, Any]:
        """Initialize RoT and baseline evaluators."""
        evaluators = {}

        # Always include RoT
        try:
            evaluators['RoT'] = RoTEvaluator()
            logger.info("✓ RoT evaluator initialized")
        except Exception as e:
            logger.error(f"✗ Failed to initialize RoT: {e}")
            raise

        # Initialize baselines
        baseline_classes = {
            'vanilla': VanillaRAG,
            'graph': GraphRAG,
        }

        for name in baseline_names:
            if name in baseline_classes:
                try:
                    evaluators[name] = baseline_classes[name]()
                    logger.info(f"✓ {name} evaluator initialized")
                except Exception as e:
                    logger.warning(f"✗ Failed to initialize {name}: {e}")
            else:
                logger.warning(f"Unknown baseline: {name}")

        return evaluators

    def _run_single_benchmark(
        self,
        evaluator: Any,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run a single benchmark with multiple runs for statistical significance."""

        all_runs = []

        for i, seed in enumerate(self.random_seeds[:self.runs_per_experiment]):
            logger.info(f"  Run {i+1}/{self.runs_per_experiment} (seed={seed})")

            run_results = evaluator.evaluate(
                datasets=config['datasets'],
                metrics=config['metrics'],
                seed=seed,
                sample_size=config.get('sample_size'),  # For quick tests
            )

            all_runs.append(run_results)

        # Aggregate results across runs
        aggregated = self._aggregate_runs(all_runs, config['metrics'])

        return aggregated

    def _aggregate_runs(
        self,
        runs: List[Dict[str, Any]],
        metrics: List[str],
    ) -> Dict[str, Any]:
        """Compute mean and std dev across multiple runs."""
        import numpy as np

        aggregated = {}

        for metric in metrics:
            values = [run.get(metric, 0.0) for run in runs]
            aggregated[metric] = {
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'runs': values,
            }

        return aggregated

    def _save_results(self, results: Dict[str, Any]) -> None:
        """Save results to JSON file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f'benchmark_results_{timestamp}.json'

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"\n✓ Results saved to {output_file}")

    def _print_summary(self, results: Dict[str, Any]) -> None:
        """Print formatted summary table."""
        print(f"\n{'='*80}")
        print("BENCHMARK RESULTS SUMMARY")
        print(f"{'='*80}\n")

        for bench_name, bench_results in results['benchmarks'].items():
            print(f"\n{bench_name}:")
            print(f"  {'Method':<15} {'Accuracy':<15} {'Compression':<15} {'Speedup'}")
            print(f"  {'-'*70}")

            for method, metrics in bench_results.items():
                if 'error' in metrics:
                    print(f"  {method:<15} ERROR: {metrics['error']}")
                    continue

                # Extract key metrics (adapt based on benchmark)
                acc = metrics.get('accuracy', metrics.get('ndcg@10', {}))
                if isinstance(acc, dict):
                    acc_str = f"{acc.get('mean', 0):.3f} ± {acc.get('std', 0):.3f}"
                else:
                    acc_str = f"{acc:.3f}"

                comp = metrics.get('compression_ratio', {})
                if isinstance(comp, dict):
                    comp_str = f"{comp.get('mean', 1.0):.2f}×"
                else:
                    comp_str = f"{comp:.2f}×" if comp > 0 else "N/A"

                speed = metrics.get('speedup', {})
                if isinstance(speed, dict):
                    speed_str = f"{speed.get('mean', 1.0):.2f}×"
                else:
                    speed_str = f"{speed:.2f}×" if speed > 0 else "N/A"

                print(f"  {method:<15} {acc_str:<15} {comp_str:<15} {speed_str}")

        print(f"\n{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description='RoT Reasoning Server Benchmark Suite',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        '--benchmarks',
        default='all',
        help='Comma-separated benchmark names or "all" (default: all)',
    )

    parser.add_argument(
        '--baselines',
        default='vanilla',
        help='Comma-separated baseline names: vanilla, graph (default: vanilla)',
    )

    parser.add_argument(
        '--output',
        default='results',
        help='Output directory for results (default: results/)',
    )

    parser.add_argument(
        '--runs',
        type=int,
        default=3,
        help='Number of runs per experiment for statistical significance (default: 3)',
    )

    parser.add_argument(
        '--quick-test',
        action='store_true',
        help='Run quick smoke test (smaller datasets, fewer samples)',
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging',
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Parse benchmark names
    if args.benchmarks == 'all':
        if args.quick_test:
            benchmark_names = list(QUICK_TEST.keys())
        else:
            benchmark_names = list(BENCHMARKS.keys())
    else:
        benchmark_names = args.benchmarks.split(',')

    # Parse baseline names
    baseline_names = args.baselines.split(',')

    # Create runner
    runner = BenchmarkRunner(
        output_dir=args.output,
        runs_per_experiment=args.runs,
    )

    # Run benchmarks
    try:
        results = runner.run_all_benchmarks(
            benchmark_names=benchmark_names,
            baseline_names=baseline_names,
            quick_test=args.quick_test,
        )

        logger.info("\n✓ All benchmarks completed successfully!")
        sys.exit(0)

    except Exception as e:
        logger.error(f"\n✗ Benchmark suite failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
