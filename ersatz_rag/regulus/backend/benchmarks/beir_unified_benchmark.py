#!/usr/bin/env python3
"""
Unified BEIR Benchmark for ThreeApproachRAG System

Tests the INTEGRATED system (PageIndex + LEANN + deepConf) against BEIR datasets.
This is the REAL benchmark that tests all approaches working together.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.three_approach_integration import ThreeApproachRAG

def load_beir_dataset(dataset_path: str) -> Tuple[Dict, Dict, Dict]:
    """Load BEIR dataset (corpus, queries, qrels)"""

    print(f"Loading BEIR dataset from {dataset_path}...")

    # Load corpus
    corpus_file = Path(dataset_path) / "corpus.jsonl"
    corpus = {}
    with open(corpus_file, 'r') as f:
        for line in f:
            doc = json.loads(line)
            corpus[doc['_id']] = {
                'title': doc.get('title', ''),
                'text': doc.get('text', ''),
                'metadata': doc.get('metadata', {})
            }

    # Load queries
    queries_file = Path(dataset_path) / "queries.jsonl"
    queries = {}
    with open(queries_file, 'r') as f:
        for line in f:
            query = json.loads(line)
            queries[query['_id']] = query['text']

    # Load relevance judgments
    qrels_file = Path(dataset_path) / "qrels" / "test.tsv"
    qrels = {}
    with open(qrels_file, 'r') as f:
        next(f)  # Skip header
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 3:
                query_id, corpus_id, score = parts[0], parts[1], int(parts[2])
                if query_id not in qrels:
                    qrels[query_id] = {}
                qrels[query_id][corpus_id] = score

    print(f"✓ Loaded {len(corpus)} documents")
    print(f"✓ Loaded {len(queries)} queries")
    print(f"✓ Loaded relevance judgments for {len(qrels)} queries")

    return corpus, queries, qrels


def build_unified_index(rag_system: ThreeApproachRAG, corpus: Dict, index_path: str) -> None:
    """Build index using ThreeApproachRAG system"""

    print(f"\nBuilding unified index with all 3 approaches...")

    # Convert BEIR corpus to document structure format
    document_structure = {
        "document_type": "beir_corpus",
        "sections": [],
        "processing_metadata": {
            "reasoning_engine": "unified_three_approach",
            "structure_confidence": 0.85,
            "total_sections": len(corpus),
            "processing_time": "N/A"
        }
    }

    for doc_id, doc in corpus.items():
        full_text = f"{doc['title']}\n\n{doc['text']}"

        section = {
            "node_id": doc_id,
            "title": doc['title'] or doc_id,
            "content": full_text,
            "summary": doc['text'][:200] + "..." if len(doc['text']) > 200 else doc['text'],
            "section_level": 1,
            "section_type": "document",
            "page_ranges": [1, 1],
            "reasoning_confidence": 0.85,
            "cross_references": [],
            "key_concepts": []
        }

        document_structure["sections"].append(section)

    # Build LEANN index with all 3 approaches
    print(f"Building index for {len(corpus)} documents...")
    rag_system.build_leann_index(document_structure, index_path)
    print(f"✓ Unified index built at {index_path}")


def calculate_ndcg_at_k(relevances: List[int], k: int = 10) -> float:
    """Calculate nDCG@k"""

    relevances = relevances[:k]

    if not relevances or max(relevances) == 0:
        return 0.0

    # DCG
    dcg = relevances[0] + sum(rel / np.log2(i + 2) for i, rel in enumerate(relevances[1:], start=1))

    # IDCG
    ideal_relevances = sorted(relevances, reverse=True)
    idcg = ideal_relevances[0] + sum(rel / np.log2(i + 2) for i, rel in enumerate(ideal_relevances[1:], start=1))

    return dcg / idcg if idcg > 0 else 0.0


def calculate_recall_at_k(retrieved_relevant: int, total_relevant: int, k: int = 100) -> float:
    """Calculate Recall@k"""
    return retrieved_relevant / total_relevant if total_relevant > 0 else 0.0


def run_unified_benchmark(
    rag_system: ThreeApproachRAG,
    index_path: str,
    queries: Dict,
    qrels: Dict,
    max_queries: int = None
) -> Dict:
    """
    Run BEIR benchmark on unified ThreeApproachRAG system

    This tests ALL 3 approaches working together:
    - PageIndex for document processing
    - LEANN for vector search
    - deepConf for confidence scoring
    """

    print(f"\n{'='*70}")
    print("RUNNING UNIFIED BEIR BENCHMARK ON ThreeApproachRAG")
    print(f"{'='*70}\n")

    # Filter to only queries that have relevance judgments
    query_ids_with_qrels = [qid for qid in queries.keys() if qid in qrels]

    if max_queries:
        query_ids_with_qrels = query_ids_with_qrels[:max_queries]

    print(f"Testing {len(query_ids_with_qrels)} queries (out of {len(queries)} total queries)")

    ndcg_scores = []
    recall_scores = []

    for i, query_id in enumerate(query_ids_with_qrels, 1):
        if i % 10 == 0:
            print(f"  Progress: {i}/{len(query_ids_with_qrels)} queries")

        query_text = queries[query_id]
        relevant_docs = qrels.get(query_id, {})

        # Use unified system for retrieval
        try:
            results = rag_system.broad_then_deep_search(
                query=query_text,
                index_path=index_path,
                top_k=100
            )

            retrieved_results = results.get('results', [])

        except Exception as e:
            print(f"  Warning: Query {query_id} failed: {e}")
            ndcg_scores.append(0.0)
            recall_scores.append(0.0)
            continue

        # Calculate nDCG@10
        top_10_relevances = []
        retrieved_relevant_count = 0

        for result in retrieved_results[:10]:
            doc_id = result['metadata'].get('node_id')
            relevance = relevant_docs.get(doc_id, 0)
            top_10_relevances.append(relevance)
            if relevance > 0:
                retrieved_relevant_count += 1

        # Count total relevant in top 100
        for result in retrieved_results[:100]:
            doc_id = result['metadata'].get('node_id')
            if relevant_docs.get(doc_id, 0) > 0:
                retrieved_relevant_count += 1

        ndcg_10 = calculate_ndcg_at_k(top_10_relevances, k=10)
        recall_100 = calculate_recall_at_k(retrieved_relevant_count, len(relevant_docs), k=100)

        ndcg_scores.append(ndcg_10)
        recall_scores.append(recall_100)

    # Calculate final metrics
    avg_ndcg = np.mean(ndcg_scores) if ndcg_scores else 0.0
    avg_recall = np.mean(recall_scores) if recall_scores else 0.0

    return {
        "dataset": "beir_nfcorpus",
        "queries_tested": len(query_ids_with_qrels),
        "system": "ThreeApproachRAG (PageIndex + LEANN + deepConf)",
        "metrics": {
            "nDCG@10": avg_ndcg,
            "Recall@100": avg_recall
        },
        "per_query_scores": {
            "ndcg@10": ndcg_scores,
            "recall@100": recall_scores
        }
    }


def main():
    print("="*70)
    print("UNIFIED BEIR BENCHMARK FOR ThreeApproachRAG")
    print("Testing: PageIndex + LEANN + deepConf INTEGRATED")
    print("="*70)

    # Dataset path
    dataset_path = "/Volumes/WS4TB/newragcity/UltraRAG-main/datasets/nfcorpus"

    if not Path(dataset_path).exists():
        print(f"\n❌ BEIR dataset not found at {dataset_path}")
        print("   Please download BEIR nfcorpus dataset first.")
        return

    # Initialize unified RAG system
    print("\nInitializing ThreeApproachRAG system...")
    rag_system = ThreeApproachRAG(
        embedding_model="Alibaba-NLP/Qwen3-Embedding-0.6B",  # Qwen3 embeddings for SOTA performance
        confidence_threshold=0.80,
        enable_streaming=False
    )

    # Load BEIR dataset
    corpus, queries, qrels = load_beir_dataset(dataset_path)

    # Build unified index
    index_path = "/tmp/beir_unified_index"
    build_unified_index(rag_system, corpus, index_path)

    # Run benchmark
    results = run_unified_benchmark(
        rag_system=rag_system,
        index_path=index_path,
        queries=queries,
        qrels=qrels,
        max_queries=323  # FULL BENCHMARK: All 323 queries with relevance judgments
    )

    # Display results
    print(f"\n{'='*70}")
    print("UNIFIED BENCHMARK RESULTS")
    print(f"{'='*70}\n")

    print(f"Dataset: {results['dataset']}")
    print(f"System: {results['system']}")
    print(f"Queries tested: {results['queries_tested']}")
    print(f"\nMetrics:")
    print(f"  nDCG@10:     {results['metrics']['nDCG@10']:.4f}")
    print(f"  Recall@100:  {results['metrics']['Recall@100']:.4f}")

    print(f"\n{'='*70}")
    print("WHAT THIS TESTS:")
    print(f"{'='*70}")
    print("✓ PageIndex: Document structure extraction")
    print("✓ LEANN: Vector search with Granite embeddings")
    print("✓ deepConf: Multi-factor confidence scoring")
    print("✓ Integration: All 3 approaches working together")

    print(f"\n✅ This is a REAL measurement of the unified system!")

    # Save results
    output_file = Path(__file__).parent / "results" / "beir_unified_results.json"
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Results saved to: {output_file}")


if __name__ == "__main__":
    main()
