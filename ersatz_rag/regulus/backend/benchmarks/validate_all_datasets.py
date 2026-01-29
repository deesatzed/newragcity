#!/usr/bin/env python3
"""
PRE-FLIGHT VALIDATION: Test All BEIR Datasets Before Full Benchmark

Tests 10 queries per dataset to catch issues like:
- Missing/corrupted datasets
- Index building failures
- Zero-result problems (like arguana)
- LEANN backend issues

Prevents wasting 85+ hours on broken datasets.

Usage:
    python3 validate_all_datasets.py

Expected runtime: 15-20 minutes for 13 datasets
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.three_approach_integration import ThreeApproachRAG
from beir import util
from beir.datasets.data_loader import GenericDataLoader
from beir.retrieval.evaluation import EvaluateRetrieval


@dataclass
class ValidationResult:
    """Results from validating a single dataset."""
    dataset: str
    passed: bool
    queries_tested: int
    avg_ndcg: float
    avg_recall: float
    non_zero_results: int
    elapsed_seconds: float
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "dataset": self.dataset,
            "passed": self.passed,
            "queries_tested": self.queries_tested,
            "avg_ndcg": float(self.avg_ndcg),
            "avg_recall": float(self.avg_recall),
            "non_zero_results": self.non_zero_results,
            "elapsed_seconds": float(self.elapsed_seconds),
            "error": self.error
        }


class DatasetValidator:
    """Validates BEIR datasets before full benchmark."""

    # All 13 available BEIR datasets
    DATASETS = [
        {"name": "scifact", "queries": 300},
        {"name": "arguana", "queries": 1406},
        {"name": "fiqa", "queries": 648},
        {"name": "trec-covid", "queries": 50},
        {"name": "nfcorpus", "queries": 323},
        {"name": "scidocs", "queries": 1000},
        {"name": "hotpotqa", "queries": 7405},
        {"name": "dbpedia-entity", "queries": 400},
        {"name": "fever", "queries": 6666},
        {"name": "climate-fever", "queries": 1535},
        {"name": "nq", "queries": 3452},
        {"name": "quora", "queries": 10000},
        {"name": "webis-touche2020", "queries": 49},
    ]

    def __init__(
        self,
        datasets_dir: str = "/Volumes/WS4TB/newragcity/UltraRAG-main/datasets",
        num_test_queries: int = 10
    ):
        """
        Args:
            datasets_dir: Directory containing BEIR datasets
            num_test_queries: Number of queries to test per dataset
        """
        self.datasets_dir = Path(datasets_dir)
        self.num_test_queries = num_test_queries
        self.results: List[ValidationResult] = []

    def validate_single_dataset(self, dataset_info: Dict) -> ValidationResult:
        """
        Validate a single dataset by testing N queries.

        Args:
            dataset_info: Dict with 'name' and 'queries' count

        Returns:
            ValidationResult with pass/fail and metrics
        """
        dataset_name = dataset_info["name"]
        print(f"\n{'='*70}")
        print(f"VALIDATING: {dataset_name}")
        print(f"{'='*70}")

        start_time = time.time()

        try:
            # Load dataset
            dataset_path = self.datasets_dir / dataset_name
            if not dataset_path.exists():
                return ValidationResult(
                    dataset=dataset_name,
                    passed=False,
                    queries_tested=0,
                    avg_ndcg=0.0,
                    avg_recall=0.0,
                    non_zero_results=0,
                    elapsed_seconds=time.time() - start_time,
                    error=f"Dataset directory not found: {dataset_path}"
                )

            print(f"Loading dataset from {dataset_path}...")
            corpus, queries, qrels = GenericDataLoader(
                data_folder=str(dataset_path)
            ).load(split="test")

            print(f"✓ Dataset loaded:")
            print(f"  - Corpus: {len(corpus)} documents")
            print(f"  - Queries: {len(queries)} total")
            print(f"  - Qrels: {len(qrels)} query-document pairs")

            # Select test queries (first N)
            test_query_ids = list(queries.keys())[:self.num_test_queries]
            test_queries = {qid: queries[qid] for qid in test_query_ids}
            test_qrels = {qid: qrels[qid] for qid in test_query_ids if qid in qrels}

            print(f"\nTesting {len(test_query_ids)} queries...")

            # Initialize ThreeApproachRAG
            print("Initializing ThreeApproachRAG...")
            rag_system = ThreeApproachRAG()

            # Build index
            print(f"Building index for {dataset_name}...")
            index_name = f"beir_{dataset_name}_validation"

            # Convert corpus to passages format
            passages = []
            for doc_id, doc_data in corpus.items():
                title = doc_data.get("title", "")
                text = doc_data.get("text", "")
                content = f"{title}\n{text}".strip() if title else text

                passages.append({
                    "id": doc_id,
                    "content": content,
                    "metadata": {
                        "source": dataset_name,
                        "doc_id": doc_id
                    }
                })

            rag_system.build_index(passages, index_name)
            print(f"✓ Index built: {len(passages)} passages indexed")

            # Run queries
            print(f"\nRunning {len(test_query_ids)} test queries...")
            results = {}
            non_zero_count = 0

            for i, qid in enumerate(test_query_ids, 1):
                query_text = test_queries[qid]
                print(f"  Query {i}/{len(test_query_ids)}: {query_text[:80]}...")

                # Query the system
                retrieved = rag_system.query(
                    query=query_text,
                    index_name=index_name,
                    top_k=100
                )

                # Convert to BEIR format: {doc_id: score}
                results[qid] = {
                    r["id"]: float(r.get("score", 1.0 - i/100))  # Use confidence or rank-based score
                    for i, r in enumerate(retrieved)
                }

                if len(results[qid]) > 0:
                    non_zero_count += 1

                print(f"    → Retrieved {len(results[qid])} documents")

            # Evaluate with BEIR metrics
            print(f"\nEvaluating with BEIR metrics...")
            evaluator = EvaluateRetrieval()
            ndcg, _map, recall, precision = evaluator.evaluate(
                test_qrels,
                results,
                [1, 3, 5, 10, 100, 1000]
            )

            avg_ndcg = ndcg.get("NDCG@10", 0.0)
            avg_recall = recall.get("Recall@100", 0.0)

            elapsed = time.time() - start_time

            # Validation criteria
            passed = (
                non_zero_count > 0 and  # At least some results
                avg_ndcg > 0.0 and      # Non-zero nDCG
                avg_recall > 0.0        # Non-zero recall
            )

            result = ValidationResult(
                dataset=dataset_name,
                passed=passed,
                queries_tested=len(test_query_ids),
                avg_ndcg=avg_ndcg,
                avg_recall=avg_recall,
                non_zero_results=non_zero_count,
                elapsed_seconds=elapsed
            )

            # Print results
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"\n{status} - {dataset_name}")
            print(f"  nDCG@10:     {avg_ndcg:.4f}")
            print(f"  Recall@100:  {avg_recall:.4f}")
            print(f"  Non-zero results: {non_zero_count}/{len(test_query_ids)}")
            print(f"  Elapsed: {elapsed:.1f}s")

            return result

        except Exception as e:
            elapsed = time.time() - start_time
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"\n❌ ERROR - {dataset_name}")
            print(f"  {error_msg}")

            return ValidationResult(
                dataset=dataset_name,
                passed=False,
                queries_tested=0,
                avg_ndcg=0.0,
                avg_recall=0.0,
                non_zero_results=0,
                elapsed_seconds=elapsed,
                error=error_msg
            )

    def validate_all(self) -> Dict:
        """
        Validate all datasets.

        Returns:
            Summary dict with pass/fail for each dataset
        """
        print("="*70)
        print("BEIR DATASET VALIDATION")
        print("="*70)
        print(f"Datasets: {len(self.DATASETS)}")
        print(f"Test queries per dataset: {self.num_test_queries}")
        print(f"Datasets directory: {self.datasets_dir}")
        print("="*70)

        start_time = time.time()

        for dataset_info in self.DATASETS:
            result = self.validate_single_dataset(dataset_info)
            self.results.append(result)

        total_elapsed = time.time() - start_time

        # Generate summary
        passed = [r for r in self.results if r.passed]
        failed = [r for r in self.results if not r.passed]

        summary = {
            "total_datasets": len(self.DATASETS),
            "passed": len(passed),
            "failed": len(failed),
            "total_elapsed_seconds": total_elapsed,
            "passed_datasets": [r.dataset for r in passed],
            "failed_datasets": [r.dataset for r in failed],
            "results": [r.to_dict() for r in self.results]
        }

        # Print summary
        print("\n" + "="*70)
        print("VALIDATION SUMMARY")
        print("="*70)
        print(f"Total datasets: {len(self.DATASETS)}")
        print(f"✅ Passed: {len(passed)}")
        print(f"❌ Failed: {len(failed)}")
        print(f"Total time: {total_elapsed/60:.1f} minutes")
        print()

        if passed:
            print("PASSED DATASETS:")
            for r in passed:
                print(f"  ✅ {r.dataset:20s} nDCG@10={r.avg_ndcg:.4f}")

        if failed:
            print("\nFAILED DATASETS:")
            for r in failed:
                error_info = f" ({r.error[:50]}...)" if r.error else ""
                print(f"  ❌ {r.dataset:20s}{error_info}")

        print("="*70)

        return summary

    def save_results(self, output_path: str = "validation_results.json"):
        """Save validation results to JSON file."""
        summary = {
            "total_datasets": len(self.DATASETS),
            "passed": sum(1 for r in self.results if r.passed),
            "failed": sum(1 for r in self.results if not r.passed),
            "passed_datasets": [r.dataset for r in self.results if r.passed],
            "failed_datasets": [r.dataset for r in self.results if not r.passed],
            "results": [r.to_dict() for r in self.results]
        }

        output_file = Path(output_path)
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n✓ Results saved to: {output_file}")


def main():
    """Run validation on all datasets."""
    validator = DatasetValidator(num_test_queries=10)
    summary = validator.validate_all()
    validator.save_results("validation_results.json")

    # Exit with error code if any datasets failed
    if summary["failed"] > 0:
        print(f"\n⚠️  WARNING: {summary['failed']} datasets failed validation")
        print("Review failures before running full benchmark!")
        sys.exit(1)
    else:
        print(f"\n✅ SUCCESS: All {summary['passed']} datasets passed validation")
        print("Ready to run full benchmark!")
        sys.exit(0)


if __name__ == "__main__":
    main()
