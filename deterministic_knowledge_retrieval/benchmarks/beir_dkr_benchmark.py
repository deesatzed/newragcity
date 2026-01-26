#!/usr/bin/env python3
"""
BEIR Benchmark for DKR (Deterministic Knowledge Retrieval)

This benchmark evaluates DKR against the official BEIR nfcorpus dataset,
which contains 323 medical/nutrition queries with relevance judgments.

NOTE: DKR is specialized for antibiotic/infection treatment, while BEIR
nfcorpus covers broader medical topics. This may result in lower scores
for out-of-domain queries, but provides honest external validation.
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.toc_agent import TOCAgent
from src.ingestion_workflow import run_ingestion_with_metadata
from beir.datasets.data_loader import GenericDataLoader


class BEIRDKRBenchmark:
    """Evaluate DKR on BEIR nfcorpus dataset."""

    def __init__(self, beir_data_path: str):
        """
        Initialize benchmark.

        Args:
            beir_data_path: Path to BEIR nfcorpus dataset directory
        """
        print("Initializing BEIR DKR Benchmark...")
        print(f"Dataset path: {beir_data_path}")

        # Load BEIR dataset
        self.corpus, self.queries, self.qrels = GenericDataLoader(
            data_folder=beir_data_path
        ).load(split="test")

        print(f"Loaded {len(self.corpus)} BEIR documents")
        print(f"Loaded {len(self.queries)} BEIR queries")
        print(f"Loaded relevance judgments for {len(self.qrels)} queries")

        # Initialize DKR knowledge base (same as real_dkr_benchmark.py)
        print("\nLoading DKR knowledge base...")
        aj_pack, warnings = run_ingestion_with_metadata()

        # Build sections list
        self.sections = []
        for file_content in aj_pack.content:
            for section in file_content.content:
                self.sections.append({
                    'file_id': file_content.file_id,
                    'section_id': section.section_id,
                    'label': section.label,
                    'text': section.text_or_data,
                    'entities': section.entities,
                })

        # Initialize TOC agent
        self.agent = TOCAgent(aj_pack.toc, self.sections)

        print(f"✓ DKR initialized with {len(self.sections)} knowledge sections")

    def calculate_ndcg_at_k(
        self, relevant_docs: Dict[str, int], retrieved_ranks: List[str], k: int = 10
    ) -> float:
        """
        Calculate nDCG@k metric.

        Args:
            relevant_docs: Dict mapping doc_id to relevance score
            retrieved_ranks: List of retrieved doc IDs in rank order
            k: Cutoff for nDCG calculation

        Returns:
            nDCG@k score
        """
        # DCG@k
        dcg = 0.0
        for i, doc_id in enumerate(retrieved_ranks[:k]):
            if doc_id in relevant_docs:
                relevance = relevant_docs[doc_id]
                dcg += (2**relevance - 1) / ((i + 1) ** 2 + 1)

        # IDCG@k (ideal DCG)
        ideal_relevances = sorted(relevant_docs.values(), reverse=True)[:k]
        idcg = sum(
            (2**rel - 1) / ((i + 1) ** 2 + 1) for i, rel in enumerate(ideal_relevances)
        )

        # nDCG
        if idcg == 0:
            return 0.0
        return dcg / idcg

    def calculate_recall_at_k(
        self, relevant_docs: set, retrieved_docs: List[str], k: int = 100
    ) -> float:
        """
        Calculate Recall@k metric.

        Args:
            relevant_docs: Set of relevant doc IDs
            retrieved_docs: List of retrieved doc IDs
            k: Cutoff for recall calculation

        Returns:
            Recall@k score
        """
        if len(relevant_docs) == 0:
            return 0.0

        retrieved_set = set(retrieved_docs[:k])
        found = len(relevant_docs & retrieved_set)
        return found / len(relevant_docs)

    def map_dkr_result_to_corpus(self, dkr_result: Dict[str, Any]) -> List[str]:
        """
        Map DKR retrieval result to BEIR corpus document IDs.

        Since DKR uses its own knowledge base, we need to find matching
        documents in the BEIR corpus based on content similarity.

        Args:
            dkr_result: DKR query result with retrieved content

        Returns:
            List of BEIR corpus doc IDs (ranked by relevance)
        """
        # Simple approach: search BEIR corpus for documents containing
        # keywords from DKR result
        dkr_content = dkr_result.get('content', '').lower()
        dkr_label = dkr_result.get('label', '').lower()

        # Extract key terms
        key_terms = set(dkr_label.split()) | set(dkr_content.split()[:100])
        key_terms = {t for t in key_terms if len(t) > 3}  # Filter short words

        # Score each corpus document
        scores = []
        for doc_id, doc in self.corpus.items():
            doc_text = (
                doc.get('title', '') + ' ' + doc.get('text', '')
            ).lower()

            # Simple overlap score
            matches = sum(1 for term in key_terms if term in doc_text)
            if matches > 0:
                scores.append((doc_id, matches))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)

        # Return top matches
        return [doc_id for doc_id, _ in scores[:100]]

    def run_benchmark(self, max_queries: int = None) -> Dict[str, Any]:
        """
        Run BEIR benchmark on DKR.

        Args:
            max_queries: Optional limit on number of queries to test

        Returns:
            Benchmark results dictionary
        """
        print("\n" + "=" * 70)
        print("RUNNING BEIR BENCHMARK ON DKR")
        print("=" * 70)

        query_ids = list(self.queries.keys())
        if max_queries:
            query_ids = query_ids[:max_queries]

        print(f"\nProcessing {len(query_ids)} queries...")

        results = []
        ndcg_scores = []
        recall_scores = []

        for i, query_id in enumerate(query_ids, 1):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(query_ids)} queries")

            query_text = self.queries[query_id]

            # Get DKR result
            score, section = self.agent.get_top_section(query_text)

            # Build result dict for mapping function
            dkr_result = {
                'label': section['label'],
                'content': section['text'],
                'score': score,
            }

            # Map to BEIR corpus
            retrieved_docs = self.map_dkr_result_to_corpus(dkr_result)

            # Get ground truth relevant docs
            relevant_docs = self.qrels.get(query_id, {})

            # Calculate metrics
            ndcg_10 = self.calculate_ndcg_at_k(relevant_docs, retrieved_docs, k=10)
            recall_100 = self.calculate_recall_at_k(
                set(relevant_docs.keys()), retrieved_docs, k=100
            )

            ndcg_scores.append(ndcg_10)
            recall_scores.append(recall_100)

            results.append(
                {
                    'query_id': query_id,
                    'query': query_text,
                    'dkr_label': dkr_result['label'],
                    'dkr_score': dkr_result['score'],
                    'num_retrieved': len(retrieved_docs),
                    'num_relevant': len(relevant_docs),
                    'ndcg@10': ndcg_10,
                    'recall@100': recall_100,
                }
            )

        # Calculate average metrics
        avg_ndcg = sum(ndcg_scores) / len(ndcg_scores) if ndcg_scores else 0
        avg_recall = sum(recall_scores) / len(recall_scores) if recall_scores else 0

        benchmark_results = {
            'benchmark_name': 'BEIR nfcorpus - DKR Evaluation',
            'dataset': 'nfcorpus',
            'num_queries_tested': len(query_ids),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'metrics': {
                'ndcg@10': avg_ndcg,
                'recall@100': avg_recall,
            },
            'per_query_results': results,
            'notes': [
                'DKR is specialized for antibiotic/infection treatment',
                'BEIR nfcorpus covers broader medical/nutrition topics',
                'Lower scores expected for out-of-domain queries',
                'Mapping from DKR knowledge to BEIR corpus is approximate',
            ],
        }

        return benchmark_results

    def print_summary(self, results: Dict[str, Any]):
        """Print benchmark summary."""
        print("\n" + "=" * 70)
        print("BEIR BENCHMARK RESULTS")
        print("=" * 70)

        print(f"\nDataset: {results['dataset']}")
        print(f"Queries tested: {results['num_queries_tested']}")
        print()
        print("Metrics:")
        print(f"  nDCG@10:     {results['metrics']['ndcg@10']:.4f}")
        print(f"  Recall@100:  {results['metrics']['recall@100']:.4f}")

        print("\nNotes:")
        for note in results['notes']:
            print(f"  • {note}")

        # Show some sample results
        print("\nSample Query Results:")
        for i, result in enumerate(results['per_query_results'][:5], 1):
            print(f"\n{i}. {result['query'][:60]}...")
            print(f"   DKR result: {result['dkr_label']}")
            print(f"   nDCG@10: {result['ndcg@10']:.4f}, Recall@100: {result['recall@100']:.4f}")


def main():
    """Run BEIR DKR benchmark."""
    # Determine dataset path
    dataset_path = Path(__file__).parent.parent.parent / "datasets" / "nfcorpus"

    if not dataset_path.exists():
        print(f"ERROR: BEIR dataset not found at {dataset_path}")
        print("Run download_beir_dataset.py first to download the dataset")
        sys.exit(1)

    # Create benchmark
    benchmark = BEIRDKRBenchmark(str(dataset_path))

    # Run benchmark (limiting to 50 queries for quick test)
    # Remove max_queries parameter to test all 323 queries
    results = benchmark.run_benchmark(max_queries=50)

    # Print summary
    benchmark.print_summary(results)

    # Save results
    output_file = Path(__file__).parent / "results" / "beir_dkr_benchmark_results.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Results saved to: {output_file}")
    print()


if __name__ == '__main__':
    main()
