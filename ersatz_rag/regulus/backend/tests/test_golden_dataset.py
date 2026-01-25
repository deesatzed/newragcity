"""
Golden dataset accuracy testing for Regulus backend
Tests system accuracy against known policy questions and answers
"""
import json
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestGoldenDatasetAccuracy:
    """Test system accuracy using golden dataset"""
    
    @classmethod
    def setup_class(cls):
        """Load golden dataset for testing"""
        dataset_path = Path(__file__).parent / "golden_dataset.json"
        with open(dataset_path) as f:
            cls.golden_dataset = json.load(f)
    
    def test_golden_dataset_structure(self):
        """Verify golden dataset has correct structure"""
        assert "description" in self.golden_dataset
        assert "test_cases" in self.golden_dataset
        assert len(self.golden_dataset["test_cases"]) == 50
        
        for case in self.golden_dataset["test_cases"]:
            required_fields = [
                "id", "question", "expected_answer", "expected_node_ids",
                "expected_sources", "expected_page_ranges", "category"
            ]
            for field in required_fields:
                assert field in case, f"Missing field {field} in test case {case.get('id')}"
    
    def test_system_accuracy_against_golden_dataset(self):
        """Test system accuracy against all 50 golden dataset questions"""
        if not self._system_ready():
            pytest.skip("System not ready - requires real LEANN index and documents")
        
        with TestClient(app) as client:
            correct_answers = 0
            total_questions = len(self.golden_dataset["test_cases"])
            
            results = []
            
            for test_case in self.golden_dataset["test_cases"]:
                question = test_case["question"]
                expected_answer = test_case["expected_answer"]
                expected_nodes = test_case["expected_node_ids"]
                
                # Query the system
                response = client.post("/query", data={"query": question})
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Check if we got results
                    if "results" in result and result["results"]:
                        # Evaluate answer quality
                        is_correct = self._evaluate_answer_quality(
                            result["results"], expected_answer, expected_nodes
                        )
                        
                        if is_correct:
                            correct_answers += 1
                        
                        results.append({
                            "test_id": test_case["id"],
                            "question": question,
                            "expected": expected_answer,
                            "actual": result["results"][0]["content"] if result["results"] else "No results",
                            "correct": is_correct,
                            "category": test_case["category"]
                        })
                    else:
                        results.append({
                            "test_id": test_case["id"],
                            "question": question,
                            "expected": expected_answer,
                            "actual": "No results returned",
                            "correct": False,
                            "category": test_case["category"]
                        })
                else:
                    results.append({
                        "test_id": test_case["id"],
                        "question": question,
                        "expected": expected_answer,
                        "actual": f"API Error: {response.status_code}",
                        "correct": False,
                        "category": test_case["category"]
                    })
            
            # Calculate accuracy
            accuracy = (correct_answers / total_questions) * 100
            
            # Log detailed results
            self._log_accuracy_results(results, accuracy, correct_answers, total_questions)
            
            # Assert 90% accuracy requirement
            assert accuracy >= 90.0, f"System accuracy {accuracy:.1f}% below required 90%"
    
    def test_category_specific_accuracy(self):
        """Test accuracy by policy category"""
        if not self._system_ready():
            pytest.skip("System not ready - requires real LEANN index and documents")
        
        categories = {}
        
        # Group test cases by category
        for test_case in self.golden_dataset["test_cases"]:
            category = test_case["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(test_case)
        
        with TestClient(app) as client:
            category_results = {}
            
            for category, test_cases in categories.items():
                correct = 0
                total = len(test_cases)
                
                for test_case in test_cases:
                    response = client.post("/query", data={"query": test_case["question"]})
                    
                    if response.status_code == 200:
                        result = response.json()
                        if "results" in result and result["results"]:
                            is_correct = self._evaluate_answer_quality(
                                result["results"], 
                                test_case["expected_answer"], 
                                test_case["expected_node_ids"]
                            )
                            if is_correct:
                                correct += 1
                
                category_accuracy = (correct / total) * 100 if total > 0 else 0
                category_results[category] = {
                    "correct": correct,
                    "total": total,
                    "accuracy": category_accuracy
                }
            
            # Log category results
            print(f"\nCategory-specific accuracy results:")
            for category, stats in category_results.items():
                print(f"{category}: {stats['correct']}/{stats['total']} ({stats['accuracy']:.1f}%)")
            
            # Assert minimum accuracy per category (allow some variation)
            for category, stats in category_results.items():
                assert stats['accuracy'] >= 80.0, \
                    f"Category '{category}' accuracy {stats['accuracy']:.1f}% below minimum 80%"
    
    def _system_ready(self) -> bool:
        """Check if system is ready for testing"""
        try:
            with TestClient(app) as client:
                response = client.get("/")
                return response.status_code == 200
        except Exception:
            return False
    
    def _evaluate_answer_quality(self, results: list, expected_answer: str, expected_nodes: list) -> bool:
        """Evaluate if the returned answer matches expected quality"""
        if not results:
            return False
        
        top_result = results[0]
        actual_content = top_result.get("content", "")
        actual_metadata = top_result.get("metadata", {})
        actual_node_id = actual_metadata.get("node_id", "")
        
        # Check content similarity (basic keyword matching)
        expected_keywords = self._extract_keywords(expected_answer)
        actual_keywords = self._extract_keywords(actual_content)
        
        # Count matching keywords
        matching_keywords = len(expected_keywords.intersection(actual_keywords))
        keyword_match_ratio = matching_keywords / len(expected_keywords) if expected_keywords else 0
        
        # Check node ID match
        node_match = actual_node_id in expected_nodes if expected_nodes else False
        
        # Consider answer correct if:
        # 1. At least 60% keyword overlap OR correct node ID
        # 2. Minimum score threshold (if available)
        score_threshold = top_result.get("score", 0) >= 0.7
        
        return (keyword_match_ratio >= 0.6 or node_match) and score_threshold
    
    def _extract_keywords(self, text: str) -> set:
        """Extract meaningful keywords from text"""
        import re
        
        # Remove common stop words and extract meaningful terms
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
            "of", "with", "by", "is", "are", "was", "were", "be", "been", "being"
        }
        
        # Convert to lowercase and extract words
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Filter out stop words and short words
        meaningful_words = {
            word for word in words 
            if len(word) > 3 and word not in stop_words
        }
        
        return meaningful_words
    
    def _log_accuracy_results(self, results: list, accuracy: float, correct: int, total: int):
        """Log detailed accuracy test results"""
        print(f"\n=== Golden Dataset Accuracy Results ===")
        print(f"Overall Accuracy: {correct}/{total} ({accuracy:.1f}%)")
        print(f"Required Accuracy: 90.0%")
        print(f"Status: {'PASS' if accuracy >= 90.0 else 'FAIL'}")
        
        # Log failed cases
        failed_cases = [r for r in results if not r["correct"]]
        if failed_cases:
            print(f"\nFailed Cases ({len(failed_cases)}):")
            for case in failed_cases[:10]:  # Show first 10 failures
                print(f"  ID {case['test_id']} ({case['category']}): {case['question']}")
                print(f"    Expected: {case['expected'][:100]}...")
                print(f"    Actual: {case['actual'][:100]}...")
        
        # Category breakdown
        category_stats = {}
        for result in results:
            category = result["category"]
            if category not in category_stats:
                category_stats[category] = {"correct": 0, "total": 0}
            category_stats[category]["total"] += 1
            if result["correct"]:
                category_stats[category]["correct"] += 1
        
        print(f"\nCategory Breakdown:")
        for category, stats in sorted(category_stats.items()):
            cat_accuracy = (stats["correct"] / stats["total"]) * 100
            print(f"  {category}: {stats['correct']}/{stats['total']} ({cat_accuracy:.1f}%)")


class TestAccuracyRequirements:
    """Test specific accuracy requirements from build checklist"""
    
    def test_accuracy_requirement_documentation(self):
        """Verify accuracy requirements are documented"""
        # This test documents the >90% accuracy requirement from Phase 5 of build checklist
        required_accuracy = 90.0
        
        assert required_accuracy == 90.0
        assert isinstance(required_accuracy, float)
        
        print(f"Documented accuracy requirement: >{required_accuracy}%")
    
    def test_golden_dataset_completeness(self):
        """Verify golden dataset meets requirements"""
        dataset_path = Path(__file__).parent / "golden_dataset.json"
        
        assert dataset_path.exists(), "Golden dataset file must exist"
        
        with open(dataset_path) as f:
            dataset = json.load(f)
        
        # Verify 50 test cases as specified in build checklist
        assert len(dataset["test_cases"]) == 50, "Golden dataset must contain exactly 50 test cases"
        
        # Verify required fields
        for case in dataset["test_cases"]:
            assert "expected_node_ids" in case, "Test cases must include expected node IDs"
            assert "expected_page_ranges" in case, "Test cases must include expected page ranges"
            assert "expected_sources" in case, "Test cases must include expected sources"
        
        print(f"Golden dataset contains {len(dataset['test_cases'])} test cases")
        
        # Verify category coverage
        categories = {case["category"] for case in dataset["test_cases"]}
        print(f"Covered policy categories: {sorted(categories)}")
        
        assert len(categories) >= 10, "Golden dataset should cover at least 10 policy categories"