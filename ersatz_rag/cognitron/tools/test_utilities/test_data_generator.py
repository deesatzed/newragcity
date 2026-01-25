#!/usr/bin/env python3
"""
Medical-Grade Test Data Generator
Generate realistic, diverse test data for medical-grade testing across all Cognitron applications.
"""

import random
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import string


@dataclass
class QueryScenario:
    """Test query scenario with expected confidence and response characteristics."""
    query: str
    domain: str
    expected_confidence_range: Tuple[float, float]
    expected_response_type: str
    complexity: str  # "simple", "medium", "complex"
    context_required: bool
    test_case_id: str
    tags: List[str]


@dataclass
class TemporalPattern:
    """Temporal development pattern for testing temporal intelligence."""
    pattern_id: str
    pattern_type: str  # "problem_solving", "feature_development", "debugging"
    time_sequence: List[Dict[str, Any]]
    context_evolution: List[Dict[str, Any]]
    expected_crystallization: Dict[str, Any]
    complexity: str


@dataclass
class KnowledgeDocument:
    """Knowledge document for platform testing."""
    doc_id: str
    title: str
    content: str
    doc_type: str  # "code", "documentation", "configuration"
    metadata: Dict[str, Any]
    quality_indicators: Dict[str, float]
    indexing_complexity: str


class MedicalGradeTestDataGenerator:
    """Generate realistic, diverse test data for medical-grade testing."""
    
    def __init__(self, seed: int = 42):
        """Initialize with reproducible random seed for consistent testing."""
        random.seed(seed)
        self.generation_timestamp = datetime.now()
        
        # Domain-specific vocabularies
        self.technical_terms = [
            "authentication", "authorization", "database", "API", "microservice",
            "container", "deployment", "monitoring", "logging", "caching",
            "security", "encryption", "performance", "scalability", "reliability"
        ]
        
        self.code_concepts = [
            "function", "class", "method", "variable", "parameter", "return",
            "loop", "condition", "exception", "interface", "inheritance",
            "polymorphism", "abstraction", "encapsulation", "async", "await"
        ]
        
        self.problem_types = [
            "bug_fix", "feature_implementation", "performance_optimization",
            "security_enhancement", "refactoring", "integration", "testing",
            "documentation", "configuration", "deployment_issue"
        ]
    
    def generate_comprehensive_test_suite(self, scale: str = "medium") -> Dict[str, Any]:
        """Generate comprehensive test data suite for all applications."""
        
        scale_multipliers = {
            "small": 0.5,
            "medium": 1.0,
            "large": 2.0,
            "enterprise": 5.0
        }
        
        multiplier = scale_multipliers.get(scale, 1.0)
        base_counts = {
            "query_scenarios": int(1000 * multiplier),
            "temporal_patterns": int(200 * multiplier),
            "knowledge_documents": int(500 * multiplier)
        }
        
        return {
            "metadata": {
                "generation_timestamp": self.generation_timestamp.isoformat(),
                "scale": scale,
                "total_items": sum(base_counts.values()),
                "generator_version": "1.0.0"
            },
            
            "core_application_data": {
                "query_scenarios": self.generate_query_scenarios(base_counts["query_scenarios"]),
                "confidence_profiles": self.generate_confidence_profiles(),
                "memory_test_cases": self.generate_memory_test_cases(),
                "workflow_traces": self.generate_workflow_traces()
            },
            
            "temporal_application_data": {
                "temporal_patterns": self.generate_temporal_patterns(base_counts["temporal_patterns"]),
                "context_scenarios": self.generate_context_scenarios(),
                "decay_test_cases": self.generate_decay_test_cases(),
                "crystallization_examples": self.generate_crystallization_examples()
            },
            
            "platform_application_data": {
                "knowledge_documents": self.generate_knowledge_documents(base_counts["knowledge_documents"]),
                "indexing_scenarios": self.generate_indexing_scenarios(),
                "topic_generation_cases": self.generate_topic_generation_cases(),
                "connector_test_data": self.generate_connector_test_data()
            },
            
            "integration_test_data": {
                "cross_app_scenarios": self.generate_cross_app_scenarios(),
                "workflow_integration": self.generate_workflow_integration_cases(),
                "data_flow_tests": self.generate_data_flow_tests()
            }
        }
    
    def generate_query_scenarios(self, count: int = 1000) -> List[QueryScenario]:
        """Generate diverse query scenarios for core application testing."""
        scenarios = []
        
        # High-confidence scenarios (30% - medical-grade responses expected)
        high_conf_count = int(count * 0.3)
        scenarios.extend(self._generate_high_confidence_queries(high_conf_count))
        
        # Medium-confidence scenarios (40% - warning responses expected)
        medium_conf_count = int(count * 0.4)
        scenarios.extend(self._generate_medium_confidence_queries(medium_conf_count))
        
        # Low-confidence scenarios (30% - suppression expected)
        low_conf_count = count - high_conf_count - medium_conf_count
        scenarios.extend(self._generate_low_confidence_queries(low_conf_count))
        
        return scenarios
    
    def _generate_high_confidence_queries(self, count: int) -> List[QueryScenario]:
        """Generate high-confidence query scenarios."""
        scenarios = []
        
        high_confidence_templates = [
            "How do I implement {concept} in this {context}?",
            "What is the {technical_term} configuration for {system}?",
            "Show me the {code_concept} implementation in {file_type}",
            "Explain the {process} workflow step by step",
            "What are the security requirements for {feature}?"
        ]
        
        for i in range(count):
            template = random.choice(high_confidence_templates)
            query = template.format(
                concept=random.choice(self.code_concepts),
                context=random.choice(["codebase", "project", "system", "application"]),
                technical_term=random.choice(self.technical_terms),
                system=random.choice(["database", "API", "service", "component"]),
                code_concept=random.choice(self.code_concepts),
                file_type=random.choice(["Python", "JavaScript", "TypeScript", "configuration"]),
                process=random.choice(["authentication", "deployment", "testing", "build"]),
                feature=random.choice(self.technical_terms)
            )
            
            scenarios.append(QueryScenario(
                query=query,
                domain=random.choice(["development", "architecture", "security", "deployment"]),
                expected_confidence_range=(0.85, 0.95),
                expected_response_type="detailed_explanation",
                complexity=random.choice(["simple", "medium"]),
                context_required=random.choice([True, False]),
                test_case_id=f"high_conf_{i:04d}",
                tags=["high_confidence", "medical_grade", "production_ready"]
            ))
        
        return scenarios
    
    def _generate_medium_confidence_queries(self, count: int) -> List[QueryScenario]:
        """Generate medium-confidence query scenarios."""
        scenarios = []
        
        medium_confidence_templates = [
            "What might be causing {issue} in the {system}?",
            "How should I approach {problem_type}?",
            "What are some options for {technical_decision}?",
            "Compare {approach1} vs {approach2} for {use_case}",
            "What are the trade-offs of {solution}?"
        ]
        
        for i in range(count):
            template = random.choice(medium_confidence_templates)
            query = template.format(
                issue=random.choice(["performance issues", "memory leaks", "connection errors"]),
                system=random.choice(["database", "API", "frontend", "backend"]),
                problem_type=random.choice(self.problem_types),
                technical_decision=random.choice(["database design", "architecture pattern", "deployment strategy"]),
                approach1=random.choice(["microservices", "monolith", "serverless"]),
                approach2=random.choice(["containerized", "traditional", "cloud-native"]),
                use_case=random.choice(["high throughput", "low latency", "high availability"]),
                solution=random.choice(["caching strategy", "load balancing", "data partitioning"])
            )
            
            scenarios.append(QueryScenario(
                query=query,
                domain=random.choice(["troubleshooting", "architecture", "optimization"]),
                expected_confidence_range=(0.70, 0.85),
                expected_response_type="options_with_warnings",
                complexity=random.choice(["medium", "complex"]),
                context_required=True,
                test_case_id=f"med_conf_{i:04d}",
                tags=["medium_confidence", "guidance", "context_dependent"]
            ))
        
        return scenarios
    
    def _generate_low_confidence_queries(self, count: int) -> List[QueryScenario]:
        """Generate low-confidence query scenarios (should trigger suppression)."""
        scenarios = []
        
        low_confidence_templates = [
            "What will happen if {vague_action}?",
            "Should I {ambiguous_decision}?",
            "Why is {undefined_problem} happening?",
            "How do I fix {non_specific_issue}?",
            "What's the best {subjective_choice}?"
        ]
        
        for i in range(count):
            template = random.choice(low_confidence_templates)
            query = template.format(
                vague_action="I change this configuration",
                ambiguous_decision="use this library or that one",
                undefined_problem="the system slow sometimes",
                non_specific_issue="everything",
                subjective_choice="programming language for everything"
            )
            
            scenarios.append(QueryScenario(
                query=query,
                domain="ambiguous",
                expected_confidence_range=(0.30, 0.70),
                expected_response_type="suppression",
                complexity="ambiguous",
                context_required=True,
                test_case_id=f"low_conf_{i:04d}",
                tags=["low_confidence", "suppression_expected", "ambiguous"]
            ))
        
        return scenarios
    
    def generate_temporal_patterns(self, count: int = 200) -> List[TemporalPattern]:
        """Generate realistic temporal development patterns."""
        patterns = []
        
        pattern_types = [
            "problem_solving_sequence",
            "feature_development_lifecycle",
            "debugging_investigation",
            "refactoring_progression",
            "learning_curve_evolution"
        ]
        
        for i in range(count):
            pattern_type = random.choice(pattern_types)
            
            if pattern_type == "problem_solving_sequence":
                pattern = self._generate_problem_solving_pattern(i)
            elif pattern_type == "feature_development_lifecycle":
                pattern = self._generate_feature_development_pattern(i)
            elif pattern_type == "debugging_investigation":
                pattern = self._generate_debugging_pattern(i)
            elif pattern_type == "refactoring_progression":
                pattern = self._generate_refactoring_pattern(i)
            else:
                pattern = self._generate_learning_pattern(i)
            
            patterns.append(pattern)
        
        return patterns
    
    def _generate_problem_solving_pattern(self, index: int) -> TemporalPattern:
        """Generate a problem-solving sequence pattern."""
        problem = random.choice([
            "API timeout issues",
            "Memory leak investigation",
            "Performance bottleneck",
            "Authentication failures",
            "Database connection problems"
        ])
        
        time_sequence = [
            {
                "timestamp": (datetime.now() - timedelta(hours=4)).isoformat(),
                "action": "problem_identification",
                "description": f"Noticed {problem} in production",
                "confidence": 0.6,
                "tools_used": ["logs", "monitoring"]
            },
            {
                "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
                "action": "investigation",
                "description": "Analyzed error patterns and system metrics",
                "confidence": 0.7,
                "tools_used": ["profiler", "debugger", "database_query"]
            },
            {
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "action": "hypothesis_formation",
                "description": "Identified potential root cause",
                "confidence": 0.8,
                "tools_used": ["code_analysis", "documentation_review"]
            },
            {
                "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
                "action": "solution_implementation",
                "description": "Applied fix and tested solution",
                "confidence": 0.9,
                "tools_used": ["code_editor", "testing_framework"]
            }
        ]
        
        return TemporalPattern(
            pattern_id=f"problem_solving_{index:04d}",
            pattern_type="problem_solving_sequence",
            time_sequence=time_sequence,
            context_evolution=[
                {"phase": "detection", "context": "production_monitoring"},
                {"phase": "analysis", "context": "development_environment"},
                {"phase": "solution", "context": "testing_environment"}
            ],
            expected_crystallization={
                "pattern_name": f"{problem} Resolution Protocol",
                "steps": len(time_sequence),
                "success_indicators": ["reduced_error_rate", "improved_performance"],
                "tools_sequence": ["monitoring", "analysis", "implementation", "validation"]
            },
            complexity="medium"
        )
    
    def generate_knowledge_documents(self, count: int = 500) -> List[KnowledgeDocument]:
        """Generate diverse knowledge documents for platform testing."""
        documents = []
        
        doc_types = ["code", "documentation", "configuration", "specification", "tutorial"]
        
        for i in range(count):
            doc_type = random.choice(doc_types)
            
            if doc_type == "code":
                doc = self._generate_code_document(i)
            elif doc_type == "documentation":
                doc = self._generate_documentation_document(i)
            elif doc_type == "configuration":
                doc = self._generate_configuration_document(i)
            elif doc_type == "specification":
                doc = self._generate_specification_document(i)
            else:
                doc = self._generate_tutorial_document(i)
            
            documents.append(doc)
        
        return documents
    
    def _generate_code_document(self, index: int) -> KnowledgeDocument:
        """Generate a code document."""
        language = random.choice(["Python", "JavaScript", "TypeScript", "Go", "Rust"])
        component = random.choice(self.technical_terms)
        
        content = f"""
# {component.title()} Implementation in {language}

This module implements the {component} functionality for the system.

## Overview

The {component} component provides core functionality for:
- Data processing and validation
- Integration with external services  
- Error handling and recovery
- Performance monitoring

## Usage

```{language.lower()}
def {component}_handler(data):
    \"\"\"Process {component} data with validation.\"\"\"
    if not validate_input(data):
        raise ValueError("Invalid input data")
    
    result = process_{component}(data)
    return result

class {component.title()}Manager:
    \"\"\"Manages {component} operations.\"\"\"
    
    def __init__(self, config):
        self.config = config
        self.metrics = MetricsCollector()
    
    def execute(self, request):
        \"\"\"Execute {component} operation.\"\"\"
        with self.metrics.timer():
            return self._process_request(request)
```

## Configuration

Required configuration parameters:
- `{component}_timeout`: Operation timeout in seconds
- `{component}_retries`: Number of retry attempts
- `{component}_batch_size`: Processing batch size

## Error Handling

Common error scenarios and handling:
- Connection timeouts: Retry with backoff
- Validation errors: Return detailed error messages
- Resource constraints: Implement circuit breaker

## Testing

Run tests with:
```bash
pytest tests/test_{component}.py -v
```
        """
        
        return KnowledgeDocument(
            doc_id=f"code_{index:04d}",
            title=f"{component.title()} Implementation",
            content=content.strip(),
            doc_type="code",
            metadata={
                "language": language,
                "component": component,
                "file_path": f"src/{component}/{component}.py",
                "lines_of_code": content.count('\n'),
                "complexity": random.choice(["low", "medium", "high"]),
                "last_modified": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            },
            quality_indicators={
                "documentation_coverage": random.uniform(0.7, 0.95),
                "test_coverage": random.uniform(0.8, 0.98),
                "code_quality_score": random.uniform(0.75, 0.95),
                "maintainability_index": random.uniform(0.7, 0.9)
            },
            indexing_complexity="medium"
        )
    
    def generate_confidence_profiles(self) -> List[Dict[str, Any]]:
        """Generate confidence profile test cases."""
        profiles = []
        
        # High confidence profiles
        for i in range(50):
            profiles.append({
                "profile_id": f"high_conf_{i:03d}",
                "confidence_score": random.uniform(0.90, 0.98),
                "factors": {
                    "semantic_similarity": random.uniform(0.85, 0.95),
                    "factual_consistency": random.uniform(0.90, 0.98),
                    "source_reliability": random.uniform(0.85, 0.95),
                    "context_relevance": random.uniform(0.80, 0.95)
                },
                "calibration_data": {
                    "predicted_accuracy": random.uniform(0.90, 0.98),
                    "actual_accuracy": random.uniform(0.88, 0.96),
                    "calibration_error": random.uniform(0.01, 0.05)
                }
            })
        
        # Medium confidence profiles  
        for i in range(50):
            profiles.append({
                "profile_id": f"medium_conf_{i:03d}",
                "confidence_score": random.uniform(0.70, 0.85),
                "factors": {
                    "semantic_similarity": random.uniform(0.60, 0.80),
                    "factual_consistency": random.uniform(0.70, 0.85),
                    "source_reliability": random.uniform(0.65, 0.85),
                    "context_relevance": random.uniform(0.55, 0.80)
                },
                "calibration_data": {
                    "predicted_accuracy": random.uniform(0.70, 0.85),
                    "actual_accuracy": random.uniform(0.68, 0.82),
                    "calibration_error": random.uniform(0.02, 0.08)
                }
            })
        
        return profiles
    
    def save_test_data_suite(self, test_suite: Dict[str, Any], output_dir: Path):
        """Save comprehensive test data suite to files."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save metadata
        with open(output_dir / "metadata.json", 'w') as f:
            json.dump(test_suite["metadata"], f, indent=2)
        
        # Save each application's test data
        for app_name, app_data in test_suite.items():
            if app_name == "metadata":
                continue
                
            app_dir = output_dir / app_name
            app_dir.mkdir(exist_ok=True)
            
            for data_type, data_list in app_data.items():
                file_path = app_dir / f"{data_type}.json"
                
                if isinstance(data_list, list):
                    # Convert dataclasses to dicts
                    serializable_data = []
                    for item in data_list:
                        if hasattr(item, '__dict__'):
                            serializable_data.append(asdict(item))
                        else:
                            serializable_data.append(item)
                    
                    with open(file_path, 'w') as f:
                        json.dump(serializable_data, f, indent=2)
                else:
                    with open(file_path, 'w') as f:
                        json.dump(data_list, f, indent=2)
        
        print(f"Test data suite saved to: {output_dir}")
    
    def generate_cross_app_scenarios(self) -> List[Dict[str, Any]]:
        """Generate cross-application integration scenarios."""
        scenarios = []
        
        # Core + Temporal integration scenarios
        scenarios.extend([
            {
                "scenario_id": "core_temporal_001",
                "description": "Query with temporal pattern learning",
                "flow": [
                    {"app": "core", "action": "receive_query", "data": "How do I debug memory leaks?"},
                    {"app": "temporal", "action": "analyze_patterns", "context": "previous_debugging_sessions"},
                    {"app": "temporal", "action": "predict_next_steps", "confidence": 0.85},
                    {"app": "core", "action": "generate_response", "enhanced_by": "temporal_insights"}
                ],
                "expected_outcome": "Enhanced response with personalized debugging approach"
            },
            {
                "scenario_id": "core_temporal_002", 
                "description": "Context resurrection for interrupted workflow",
                "flow": [
                    {"app": "temporal", "action": "detect_context_switch", "trigger": "new_session"},
                    {"app": "temporal", "action": "resurrect_context", "timepoint": "2_hours_ago"},
                    {"app": "core", "action": "restore_workflow_state", "context": "resurrected_context"}
                ],
                "expected_outcome": "Seamless workflow continuation"
            }
        ])
        
        # Core + Platform integration scenarios  
        scenarios.extend([
            {
                "scenario_id": "core_platform_001",
                "description": "Query with dynamic knowledge indexing",
                "flow": [
                    {"app": "core", "action": "receive_query", "data": "Explain the new API changes"},
                    {"app": "platform", "action": "detect_knowledge_gap", "query_analysis": True},
                    {"app": "platform", "action": "trigger_indexing", "target": "recent_commits"},
                    {"app": "core", "action": "retry_query", "enhanced_knowledge": True}
                ],
                "expected_outcome": "Up-to-date response with latest changes"
            }
        ])
        
        return scenarios
    
    def generate_performance_baselines(self) -> Dict[str, Dict[str, float]]:
        """Generate performance baseline data for testing."""
        return {
            "cognitron_core": {
                "query_response_time_ms": 800.0,
                "confidence_calculation_ms": 75.0,
                "memory_retrieval_ms": 450.0,
                "case_storage_ms": 180.0,
                "memory_usage_mb": 250.0
            },
            "cognitron_temporal": {
                "pattern_recognition_ms": 1800.0,
                "context_resurrection_ms": 1200.0,
                "memory_decay_processing_ms": 400.0,
                "pattern_crystallization_ms": 2500.0,
                "memory_usage_mb": 400.0
            },
            "cognitron_platform": {
                "indexing_speed_docs_per_sec": 150.0,
                "search_latency_ms": 250.0,
                "topic_generation_ms": 4000.0,
                "connector_sync_ms": 1500.0,
                "memory_usage_mb": 800.0
            }
        }


if __name__ == "__main__":
    # Generate comprehensive test data suite
    generator = MedicalGradeTestDataGenerator(seed=42)
    
    # Generate different scales of test data
    scales = ["small", "medium", "large"]
    
    for scale in scales:
        print(f"Generating {scale} scale test data...")
        
        test_suite = generator.generate_comprehensive_test_suite(scale)
        output_dir = Path(f"test_data/{scale}_scale")
        
        generator.save_test_data_suite(test_suite, output_dir)
        
        print(f"✅ {scale.title()} scale test data generated:")
        print(f"   - {len(test_suite['core_application_data']['query_scenarios'])} query scenarios")
        print(f"   - {len(test_suite['temporal_application_data']['temporal_patterns'])} temporal patterns")
        print(f"   - {len(test_suite['platform_application_data']['knowledge_documents'])} knowledge documents")
    
    print("\n🎯 Test data generation complete!")
    print("   Use generated data in your test fixtures and validation scenarios.")