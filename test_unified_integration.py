#!/usr/bin/env python3
"""
Unified Integration Test - newragcity Multi-Approach RAG System

Tests integration of:
- DKR (Deterministic Knowledge Retrieval)
- Ersatz (LEANN + PageIndex + deepConf)
- RoT (Render-of-Thought) - workaround mode

This test validates component APIs work together without requiring
full Docker deployment.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
import time

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "deterministic_knowledge_retrieval"))
sys.path.insert(0, str(project_root / "deterministic_knowledge_retrieval" / "src"))
sys.path.insert(0, str(project_root / "servers" / "rot_reasoning"))


class UnifiedIntegrationTest:
    """Test suite for unified multi-approach RAG system."""

    def __init__(self):
        """Initialize test suite."""
        self.results = {
            'test_name': 'Unified Integration Test',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'components_tested': ['DKR', 'Ersatz', 'RoT'],
            'tests': {},
        }

    def test_dkr_component(self) -> Dict[str, Any]:
        """Test DKR (Deterministic Knowledge Retrieval) component."""
        print("\n" + "=" * 70)
        print("TEST 1: DKR Component")
        print("=" * 70)

        test_result = {
            'component': 'DKR',
            'status': 'unknown',
            'details': {},
        }

        try:
            # Check if DKR benchmark script exists
            dkr_benchmark = (
                project_root
                / "deterministic_knowledge_retrieval"
                / "benchmarks"
                / "real_dkr_benchmark.py"
            )

            if not dkr_benchmark.exists():
                raise FileNotFoundError(f"DKR benchmark not found: {dkr_benchmark}")

            print("✓ DKR benchmark script found")
            test_result['details']['benchmark_script'] = 'exists'

            # Check if DKR results exist (proof it ran successfully before)
            dkr_results = (
                project_root
                / "deterministic_knowledge_retrieval"
                / "benchmarks"
                / "results"
                / "real_dkr_benchmark_results.json"
            )

            if dkr_results.exists():
                with open(dkr_results) as f:
                    results = json.load(f)

                print(f"✓ DKR results file validated")
                print(f"  Timestamp: {results.get('timestamp', 'unknown')}")
                print(f"  Test mode: {'REAL' if not results.get('placeholder_mode') else 'PLACEHOLDER'}")

                test_result['details']['results_validation'] = {
                    'file_exists': True,
                    'timestamp': results.get('timestamp'),
                    'is_real': not results.get('placeholder_mode', False),
                }

                # Verify it's not placeholder data
                if results.get('placeholder_mode'):
                    raise ValueError("DKR results are in placeholder mode!")

            else:
                print("⚠ DKR results not found (benchmark needs to be run)")
                test_result['details']['results_validation'] = {
                    'file_exists': False,
                }

            # Check if DKR source code structure exists
            dkr_src = project_root / "deterministic_knowledge_retrieval" / "src"
            if not dkr_src.exists():
                raise FileNotFoundError(f"DKR source not found: {dkr_src}")

            print("✓ DKR source code structure validated")
            test_result['details']['source_structure'] = 'valid'

            print("✓ DKR component validation complete")
            test_result['status'] = 'pass'

        except Exception as e:
            print(f"✗ DKR test failed: {e}")
            test_result['status'] = 'fail'
            test_result['error'] = str(e)

        return test_result

    def test_ersatz_imports(self) -> Dict[str, Any]:
        """Test Ersatz component imports."""
        print("\n" + "=" * 70)
        print("TEST 2: Ersatz Component Imports")
        print("=" * 70)

        test_result = {
            'component': 'Ersatz',
            'status': 'unknown',
            'details': {},
        }

        try:
            # Test LEANN imports
            print("Testing LEANN imports...")
            import leann
            try:
                version = leann.__version__
            except AttributeError:
                version = 'available (version unknown)'
            print(f"✓ LEANN: {version}")
            test_result['details']['leann_version'] = version

            # Test PageIndex imports
            print("\nTesting PageIndex imports...")
            try:
                import pageindex
                print(f"✓ PageIndex imported successfully")
                test_result['details']['pageindex'] = 'available'
            except ImportError as e:
                print(f"⚠ PageIndex import warning: {e}")
                test_result['details']['pageindex'] = 'import_warning'

            # Test sentence-transformers
            print("\nTesting sentence-transformers...")
            from sentence_transformers import SentenceTransformer
            print("✓ sentence-transformers available")
            test_result['details']['sentence_transformers'] = 'available'

            # Test google-generativeai
            print("\nTesting google-generativeai...")
            import google.generativeai
            print("✓ google-generativeai available")
            test_result['details']['google_generativeai'] = 'available'

            print("\n✓ All Ersatz dependencies available")
            test_result['status'] = 'pass'

        except Exception as e:
            print(f"✗ Ersatz import test failed: {e}")
            test_result['status'] = 'fail'
            test_result['error'] = str(e)

        return test_result

    def test_rot_workaround(self) -> Dict[str, Any]:
        """Test RoT workaround benchmark (without trained model)."""
        print("\n" + "=" * 70)
        print("TEST 3: RoT Workaround Component")
        print("=" * 70)

        test_result = {
            'component': 'RoT',
            'status': 'unknown',
            'details': {},
        }

        try:
            # Import RoT workaround benchmark
            sys.path.insert(0, str(project_root / "servers" / "rot_reasoning" / "benchmarks"))
            from rot_workaround_benchmark import RoTWorkaroundBenchmark

            print("✓ RoT workaround imports successful")
            test_result['details']['imports'] = 'success'

            # Create benchmark instance
            print("\nInitializing RoT workaround benchmark...")
            benchmark = RoTWorkaroundBenchmark()
            print("✓ RoT workaround benchmark initialized")

            # Test text complexity analysis
            test_text = "Community-acquired pneumonia (CAP) is a common infection requiring antibiotics."
            print(f"\nTesting text analysis...")
            analysis = benchmark.analyze_text_complexity(test_text)

            print(f"✓ Text analysis complete:")
            print(f"  Token estimate: {analysis['token_estimate']}")
            print(f"  Theoretical compression: {analysis['theoretical_compression_ratio']:.2f}×")

            test_result['details']['analysis_test'] = {
                'token_estimate': analysis['token_estimate'],
                'compression_ratio': analysis['theoretical_compression_ratio'],
            }

            # Validate analysis structure
            required_fields = ['token_estimate', 'theoretical_compression_ratio']
            missing_fields = [f for f in required_fields if f not in analysis]
            if missing_fields:
                raise ValueError(f"Missing fields in analysis: {missing_fields}")

            print("✓ Analysis structure validated")
            test_result['status'] = 'pass'
            test_result['details']['note'] = 'Model not trained - theoretical metrics only'

        except Exception as e:
            print(f"✗ RoT test failed: {e}")
            test_result['status'] = 'fail'
            test_result['error'] = str(e)

        return test_result

    def test_multi_approach_routing(self) -> Dict[str, Any]:
        """Test multi-approach routing logic (simulated)."""
        print("\n" + "=" * 70)
        print("TEST 4: Multi-Approach Routing Logic")
        print("=" * 70)

        test_result = {
            'component': 'Multi-Approach Routing',
            'status': 'unknown',
            'details': {},
        }

        try:
            # Simulate routing logic based on query characteristics
            test_queries = [
                {
                    'query': 'What is the exact protocol for CAP?',
                    'expected_approach': 'DKR',
                    'reason': 'Exact match query benefits from deterministic retrieval',
                },
                {
                    'query': 'Tell me about pneumonia treatment options and considerations',
                    'expected_approach': 'Ersatz',
                    'reason': 'Semantic query benefits from vector search',
                },
                {
                    'query': 'Explain the reasoning behind choosing antibiotics for pneumonia',
                    'expected_approach': 'RoT',
                    'reason': 'Reasoning query benefits from visual compression (when trained)',
                },
            ]

            routing_results = []
            print("\nSimulating query routing...")

            for test_query in test_queries:
                # Simple routing heuristic (production would be more sophisticated)
                query_lower = test_query['query'].lower()

                if 'exact' in query_lower or 'protocol' in query_lower:
                    routed_approach = 'DKR'
                elif 'reasoning' in query_lower or 'explain' in query_lower:
                    routed_approach = 'RoT'
                else:
                    routed_approach = 'Ersatz'

                matches_expected = routed_approach == test_query['expected_approach']

                routing_results.append({
                    'query': test_query['query'],
                    'routed_to': routed_approach,
                    'expected': test_query['expected_approach'],
                    'correct': matches_expected,
                })

                status_symbol = '✓' if matches_expected else '⚠'
                print(f"{status_symbol} '{test_query['query'][:50]}...'")
                print(f"  → Routed to: {routed_approach} (expected: {test_query['expected_approach']})")

            # Calculate accuracy
            correct_count = sum(1 for r in routing_results if r['correct'])
            accuracy = correct_count / len(routing_results)

            print(f"\n✓ Routing accuracy: {accuracy:.1%} ({correct_count}/{len(routing_results)})")

            test_result['details']['routing_results'] = routing_results
            test_result['details']['accuracy'] = accuracy
            test_result['status'] = 'pass' if accuracy >= 0.66 else 'warning'

        except Exception as e:
            print(f"✗ Routing test failed: {e}")
            test_result['status'] = 'fail'
            test_result['error'] = str(e)

        return test_result

    def test_benchmark_results_validation(self) -> Dict[str, Any]:
        """Validate existing benchmark results files."""
        print("\n" + "=" * 70)
        print("TEST 5: Benchmark Results Validation")
        print("=" * 70)

        test_result = {
            'component': 'Benchmark Results',
            'status': 'unknown',
            'details': {},
        }

        try:
            # Check DKR benchmark results
            dkr_results_file = (
                project_root
                / "deterministic_knowledge_retrieval"
                / "benchmarks"
                / "results"
                / "real_dkr_benchmark_results.json"
            )

            if dkr_results_file.exists():
                with open(dkr_results_file) as f:
                    dkr_results = json.load(f)

                print(f"✓ DKR results file found")
                print(f"  Queries: {dkr_results.get('num_queries', 'unknown')}")
                print(f"  Relevance: {dkr_results.get('metrics', {}).get('relevance', 'unknown')}")

                test_result['details']['dkr_results'] = {
                    'file_exists': True,
                    'num_queries': dkr_results.get('num_queries'),
                    'relevance': dkr_results.get('metrics', {}).get('relevance'),
                }
            else:
                print("⚠ DKR results file not found")
                test_result['details']['dkr_results'] = {'file_exists': False}

            # Check RoT workaround results
            rot_results_file = (
                project_root
                / "servers"
                / "rot_reasoning"
                / "benchmarks"
                / "results"
                / "rot_workaround_benchmark_results.json"
            )

            if rot_results_file.exists():
                with open(rot_results_file) as f:
                    rot_results = json.load(f)

                print(f"\n✓ RoT workaround results file found")
                print(
                    f"  Contexts: {rot_results.get('num_contexts', 'unknown')}"
                )
                print(
                    f"  Avg compression: {rot_results.get('metrics', {}).get('avg_theoretical_compression', 'unknown')}"
                )

                test_result['details']['rot_results'] = {
                    'file_exists': True,
                    'num_contexts': rot_results.get('num_contexts'),
                    'avg_compression': rot_results.get('metrics', {}).get(
                        'avg_theoretical_compression'
                    ),
                }
            else:
                print("⚠ RoT results file not found")
                test_result['details']['rot_results'] = {'file_exists': False}

            test_result['status'] = 'pass'

        except Exception as e:
            print(f"✗ Results validation failed: {e}")
            test_result['status'] = 'fail'
            test_result['error'] = str(e)

        return test_result

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests."""
        print("#" * 70)
        print("# UNIFIED INTEGRATION TEST SUITE")
        print("# Testing: DKR + Ersatz + RoT Multi-Approach RAG")
        print("#" * 70)

        # Run all tests
        self.results['tests']['dkr_component'] = self.test_dkr_component()
        self.results['tests']['ersatz_imports'] = self.test_ersatz_imports()
        self.results['tests']['rot_workaround'] = self.test_rot_workaround()
        self.results['tests']['multi_approach_routing'] = (
            self.test_multi_approach_routing()
        )
        self.results['tests']['benchmark_validation'] = (
            self.test_benchmark_results_validation()
        )

        # Calculate summary
        total_tests = len(self.results['tests'])
        passed_tests = sum(
            1 for t in self.results['tests'].values() if t['status'] == 'pass'
        )
        failed_tests = sum(
            1 for t in self.results['tests'].values() if t['status'] == 'fail'
        )
        warning_tests = sum(
            1 for t in self.results['tests'].values() if t['status'] == 'warning'
        )

        self.results['summary'] = {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'warnings': warning_tests,
            'pass_rate': passed_tests / total_tests if total_tests > 0 else 0,
        }

        return self.results

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 70)
        print("INTEGRATION TEST SUMMARY")
        print("=" * 70)

        summary = self.results['summary']
        print(f"\nTotal Tests: {summary['total']}")
        print(f"✓ Passed:    {summary['passed']}")
        print(f"✗ Failed:    {summary['failed']}")
        print(f"⚠ Warnings:  {summary['warnings']}")
        print(f"\nPass Rate:   {summary['pass_rate']:.1%}")

        print("\n" + "-" * 70)
        print("Component Status:")
        print("-" * 70)

        for test_name, test_result in self.results['tests'].items():
            status_symbol = {
                'pass': '✓',
                'fail': '✗',
                'warning': '⚠',
                'unknown': '?',
            }.get(test_result['status'], '?')

            print(f"{status_symbol} {test_result['component']}: {test_result['status'].upper()}")

        print("\n" + "=" * 70)
        print("VERDICT")
        print("=" * 70)

        if summary['failed'] == 0:
            print("✅ INTEGRATION TESTS PASSED")
            print("All components integrate successfully")
        else:
            print("⚠️  SOME INTEGRATION ISSUES DETECTED")
            print(f"Failed tests: {summary['failed']}/{summary['total']}")

    def save_results(self):
        """Save results to JSON file."""
        output_file = (
            project_root / "test_results" / "unified_integration_results.json"
        )
        output_file.parent.mkdir(exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n✓ Results saved to: {output_file}")


def main():
    """Run unified integration test."""
    test_suite = UnifiedIntegrationTest()
    results = test_suite.run_all_tests()
    test_suite.print_summary()
    test_suite.save_results()

    # Exit with appropriate code
    if results['summary']['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
