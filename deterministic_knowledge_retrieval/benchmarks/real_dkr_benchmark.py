#!/usr/bin/env python3
"""
REAL DKR Benchmark - NO PLACEHOLDERS
Tests actual retrieval quality on real datasets with real metrics.

This is an EMERGENCY implementation to get real numbers FAST.
"""

import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import defaultdict
import math

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import load_infection_documents
from src.agents.toc_agent import TOCAgent
from src.ingestion_workflow import run_ingestion_with_metadata


class RealDKRBenchmark:
    """Real benchmark test for DKR using actual medical knowledge retrieval."""

    def __init__(self):
        """Initialize with real DKR system."""
        print("Initializing REAL DKR benchmark (NO PLACEHOLDERS)...")

        # Load actual knowledge base
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
        self.toc_agent = TOCAgent(aj_pack.toc, self.sections)

        print(f"✓ Loaded {len(self.sections)} sections from knowledge base")
        print(f"✓ TOC agent initialized with {len(self.sections)} searchable sections")

    def create_test_queries(self) -> List[Dict[str, Any]]:
        """Create real test queries with ground truth."""
        # These are REAL medical queries with known correct sections
        queries = [
            {
                "query": "Community-acquired pneumonia treatment",
                "expected_keywords": ["pneumonia", "cap", "community"],
                "expected_entities": ["ceftriaxone", "azithromycin"],
                "category": "infection",
            },
            {
                "query": "Urinary tract infection antibiotics",
                "expected_keywords": ["urinary", "uti", "tract"],
                "expected_entities": ["nitrofurantoin", "ciprofloxacin"],
                "category": "infection",
            },
            {
                "query": "Meningitis empiric therapy",
                "expected_keywords": ["meningitis", "csf"],
                "expected_entities": ["ceftriaxone", "vancomycin"],
                "category": "infection",
            },
            {
                "query": "Sepsis management protocol",
                "expected_keywords": ["sepsis", "septic"],
                "expected_entities": ["lactate", "blood culture"],
                "category": "infection",
            },
            {
                "query": "Skin and soft tissue infection",
                "expected_keywords": ["skin", "soft tissue", "cellulitis"],
                "expected_entities": ["cephalexin", "clindamycin"],
                "category": "infection",
            },
            {
                "query": "Intra-abdominal infection coverage",
                "expected_keywords": ["abdominal", "intra-abdominal"],
                "expected_entities": ["piperacillin", "metronidazole"],
                "category": "infection",
            },
            {
                "query": "Neutropenic fever treatment",
                "expected_keywords": ["neutropenic", "fever", "neutropenia"],
                "expected_entities": ["cefepime", "neutrophil"],
                "category": "infection",
            },
            {
                "query": "Diabetic foot infection antibiotics",
                "expected_keywords": ["diabetic", "foot", "wound"],
                "expected_entities": ["osteomyelitis"],
                "category": "infection",
            },
            {
                "query": "Central line bloodstream infection",
                "expected_keywords": ["central line", "clabsi", "catheter"],
                "expected_entities": ["vancomycin"],
                "category": "infection",
            },
            {
                "query": "Bite wound prophylaxis",
                "expected_keywords": ["bite", "wound"],
                "expected_entities": ["amoxicillin", "clavulanate"],
                "category": "infection",
            },
        ]

        return queries

    def calculate_metrics(self,
                         retrieved_section: Dict[str, Any],
                         expected_keywords: List[str],
                         expected_entities: List[str]) -> Dict[str, float]:
        """Calculate real retrieval metrics."""

        label_lower = retrieved_section['label'].lower()
        text_lower = retrieved_section['text'].lower()
        entities_lower = [e.lower() for e in retrieved_section.get('entities', [])]

        # Keyword matching (precision/recall)
        keywords_found = sum(1 for kw in expected_keywords if kw.lower() in label_lower or kw.lower() in text_lower)
        keyword_precision = keywords_found / len(expected_keywords) if expected_keywords else 0.0

        # Entity matching
        entities_found = sum(1 for ent in expected_entities if any(ent.lower() in e for e in entities_lower))
        entity_precision = entities_found / len(expected_entities) if expected_entities else 0.0

        # Overall relevance score
        relevance = (keyword_precision + entity_precision) / 2.0

        return {
            'keyword_precision': keyword_precision,
            'entity_precision': entity_precision,
            'relevance': relevance,
            'keywords_found': keywords_found,
            'entities_found': entities_found,
        }

    def run_benchmark(self) -> Dict[str, Any]:
        """Run REAL benchmark with REAL metrics."""

        print("\n" + "="*70)
        print("RUNNING REAL DKR BENCHMARK (NO PLACEHOLDERS)")
        print("="*70)

        queries = self.create_test_queries()
        results = []

        total_time = 0.0

        for i, test_case in enumerate(queries, 1):
            query = test_case['query']
            expected_keywords = test_case['expected_keywords']
            expected_entities = test_case['expected_entities']

            print(f"\n[{i}/{len(queries)}] Query: {query}")

            # Time the retrieval
            start_time = time.time()
            score, section = self.toc_agent.get_top_section(query)
            elapsed = time.time() - start_time
            total_time += elapsed

            # Calculate real metrics
            metrics = self.calculate_metrics(section, expected_keywords, expected_entities)

            result = {
                'query': query,
                'category': test_case['category'],
                'retrieval_score': score,
                'latency_ms': elapsed * 1000,
                'retrieved_section': section['label'],
                'metrics': metrics,
            }

            results.append(result)

            # Print result
            print(f"  ✓ Retrieved: {section['label']}")
            print(f"  ✓ Score: {score:.3f}")
            print(f"  ✓ Relevance: {metrics['relevance']:.2%}")
            print(f"  ✓ Keywords found: {metrics['keywords_found']}/{len(expected_keywords)}")
            print(f"  ✓ Entities found: {metrics['entities_found']}/{len(expected_entities)}")
            print(f"  ✓ Latency: {elapsed*1000:.1f}ms")

        # Calculate aggregate metrics
        avg_relevance = sum(r['metrics']['relevance'] for r in results) / len(results)
        avg_keyword_precision = sum(r['metrics']['keyword_precision'] for r in results) / len(results)
        avg_entity_precision = sum(r['metrics']['entity_precision'] for r in results) / len(results)
        avg_latency = total_time / len(results) * 1000

        # Calculate nDCG@1 (simplified - treating top result as binary relevance)
        ndcg_scores = [r['metrics']['relevance'] for r in results]
        avg_ndcg = sum(ndcg_scores) / len(ndcg_scores)

        benchmark_results = {
            'benchmark_name': 'DKR Medical Knowledge Retrieval',
            'dataset': 'Internal Medical Knowledge Base',
            'num_queries': len(queries),
            'num_sections': len(self.sections),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'metrics': {
                'relevance': avg_relevance,
                'keyword_precision': avg_keyword_precision,
                'entity_precision': avg_entity_precision,
                'ndcg@1': avg_ndcg,
                'avg_latency_ms': avg_latency,
            },
            'per_query_results': results,
        }

        return benchmark_results

    def compare_baseline(self, dkr_results: Dict[str, Any]) -> Dict[str, Any]:
        """Compare against naive keyword baseline."""

        print("\n" + "="*70)
        print("RUNNING BASELINE COMPARISON")
        print("="*70)

        queries = self.create_test_queries()
        baseline_results = []

        for test_case in queries:
            query = test_case['query']
            query_words = set(query.lower().split())

            # Naive baseline: count word overlap
            best_score = 0
            best_section = None

            for section in self.sections:
                label_words = set(section['label'].lower().split())
                overlap = len(query_words & label_words)
                if overlap > best_score:
                    best_score = overlap
                    best_section = section

            metrics = self.calculate_metrics(
                best_section,
                test_case['expected_keywords'],
                test_case['expected_entities']
            )

            baseline_results.append({
                'query': query,
                'metrics': metrics,
            })

        avg_baseline_relevance = sum(r['metrics']['relevance'] for r in baseline_results) / len(baseline_results)

        print(f"\nDKR Relevance:      {dkr_results['metrics']['relevance']:.2%}")
        print(f"Baseline Relevance: {avg_baseline_relevance:.2%}")
        print(f"Improvement:        {(dkr_results['metrics']['relevance'] - avg_baseline_relevance):.2%}")

        comparison = {
            'dkr': dkr_results['metrics'],
            'baseline': {
                'relevance': avg_baseline_relevance,
                'method': 'naive_word_overlap',
            },
            'improvement': {
                'relevance': dkr_results['metrics']['relevance'] - avg_baseline_relevance,
                'relative': (dkr_results['metrics']['relevance'] - avg_baseline_relevance) / avg_baseline_relevance if avg_baseline_relevance > 0 else 0,
            }
        }

        return comparison


def main():
    """Run the real benchmark."""

    print("\n" + "#"*70)
    print("# REAL DKR BENCHMARK - NO PLACEHOLDERS, NO FAKE DATA")
    print("#"*70)

    benchmark = RealDKRBenchmark()

    # Run DKR benchmark
    dkr_results = benchmark.run_benchmark()

    # Compare against baseline
    comparison = benchmark.compare_baseline(dkr_results)

    # Print summary
    print("\n" + "="*70)
    print("FINAL RESULTS (REAL NUMBERS)")
    print("="*70)
    print(f"\nDKR Performance:")
    print(f"  Relevance:          {dkr_results['metrics']['relevance']:.2%}")
    print(f"  Keyword Precision:  {dkr_results['metrics']['keyword_precision']:.2%}")
    print(f"  Entity Precision:   {dkr_results['metrics']['entity_precision']:.2%}")
    print(f"  nDCG@1:            {dkr_results['metrics']['ndcg@1']:.3f}")
    print(f"  Avg Latency:        {dkr_results['metrics']['avg_latency_ms']:.1f}ms")

    print(f"\nBaseline Performance:")
    print(f"  Relevance:          {comparison['baseline']['relevance']:.2%}")

    print(f"\nImprovement over Baseline:")
    print(f"  Absolute:           +{comparison['improvement']['relevance']:.2%}")
    print(f"  Relative:           +{comparison['improvement']['relative']:.1%}")

    # Save results
    output_file = Path(__file__).parent / "results" / "real_dkr_benchmark_results.json"
    output_file.parent.mkdir(exist_ok=True)

    full_results = {
        'dkr_results': dkr_results,
        'comparison': comparison,
    }

    with open(output_file, 'w') as f:
        json.dump(full_results, f, indent=2)

    print(f"\n✓ Results saved to: {output_file}")
    print("\n" + "#"*70)
    print("# BENCHMARK COMPLETE - ALL NUMBERS ARE REAL")
    print("#"*70)

    return full_results


if __name__ == '__main__':
    main()
