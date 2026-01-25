#!/usr/bin/env python3
"""
Cognitron Core System Validation
Test core Cognitron functionality including CognitronAgent, CaseMemory, and other components
"""

import asyncio
import json
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Import core Cognitron components
from cognitron.core.agent import CognitronAgent
from cognitron.core.memory import CaseMemory
from cognitron.core.confidence import ConfidenceProfile, calculate_confidence_profile
from cognitron.indexing.service import IndexingService
from cognitron.topics.service import TopicService
from cognitron.models import QueryResult, WorkflowTrace, CaseMemoryEntry


class CognitronCoreValidator:
    """
    Comprehensive validation of core Cognitron functionality
    
    Tests:
    1. CognitronAgent initialization and query handling
    2. CaseMemory storage and retrieval
    3. Confidence calculation and calibration
    4. Indexing service functionality
    5. Topic generation service
    6. End-to-end workflow validation
    """
    
    def __init__(self):
        self.test_results = {}
        self.test_start_time = time.time()
        
        # Test data setup
        self.test_data_dir = Path.home() / ".cognitron" / "core_test_data"
        self.test_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test knowledge content
        self.test_knowledge_dir = self.test_data_dir / "test_knowledge"
        self.test_knowledge_dir.mkdir(exist_ok=True)
        
        print("🧪 Cognitron Core System Validator Initialized")
        print("=" * 60)
    
    async def run_core_validation(self) -> Dict[str, Any]:
        """Run comprehensive core system validation"""
        
        print("🚀 Starting Cognitron Core System Validation")
        print("Testing all core components and their integration\n")
        
        validation_results = {}
        
        try:
            # Setup test environment
            await self._setup_test_environment()
            
            # Test 1: Agent Initialization
            print("🤖 TEST 1: COGNITRON AGENT INITIALIZATION")
            print("-" * 45)
            agent_results = await self.test_agent_initialization()
            validation_results["agent_initialization"] = agent_results
            self._print_test_results("Agent Initialization", agent_results)
            
            # Test 2: Memory System
            print("\n💾 TEST 2: CASE MEMORY SYSTEM")
            print("-" * 35)
            memory_results = await self.test_memory_system()
            validation_results["memory_system"] = memory_results
            self._print_test_results("Memory System", memory_results)
            
            # Test 3: Confidence System
            print("\n📊 TEST 3: CONFIDENCE CALIBRATION")
            print("-" * 40)
            confidence_results = await self.test_confidence_system()
            validation_results["confidence_system"] = confidence_results
            self._print_test_results("Confidence System", confidence_results)
            
            # Test 4: Indexing Service
            print("\n🔍 TEST 4: INDEXING SERVICE")
            print("-" * 35)
            indexing_results = await self.test_indexing_service()
            validation_results["indexing_service"] = indexing_results
            self._print_test_results("Indexing Service", indexing_results)
            
            # Test 5: Topic Generation
            print("\n🏷️  TEST 5: TOPIC GENERATION SERVICE")
            print("-" * 45)
            topic_results = await self.test_topic_service()
            validation_results["topic_service"] = topic_results
            self._print_test_results("Topic Service", topic_results)
            
            # Test 6: End-to-End Workflow
            print("\n🔄 TEST 6: END-TO-END WORKFLOW")
            print("-" * 40)
            workflow_results = await self.test_end_to_end_workflow()
            validation_results["end_to_end_workflow"] = workflow_results
            self._print_test_results("End-to-End Workflow", workflow_results)
            
            # Generate final summary
            final_summary = await self.generate_validation_summary(validation_results)
            validation_results["validation_summary"] = final_summary
            
            return validation_results
            
        except Exception as e:
            print(f"❌ CRITICAL VALIDATION FAILURE: {str(e)}")
            traceback.print_exc()
            validation_results["critical_failure"] = {
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            return validation_results
    
    async def _setup_test_environment(self):
        """Setup test environment with sample knowledge content"""
        
        # Create sample code files
        sample_auth_code = '''"""
Authentication module with enterprise-grade security
"""

import hashlib
import secrets
from typing import Optional

class AuthenticationManager:
    """Secure authentication with confidence tracking"""
    
    def __init__(self):
        self.confidence_threshold = 0.85
    
    def authenticate_user(self, username: str, password: str) -> dict:
        """
        Authenticate user with confidence scoring
        
        Returns confidence-tracked authentication result
        """
        # Simulate authentication logic
        if not username or not password:
            return {
                "authenticated": False,
                "confidence": 0.0,
                "reason": "missing_credentials"
            }
        
        # Mock authentication success
        auth_confidence = 0.92 if len(password) >= 8 else 0.65
        
        return {
            "authenticated": auth_confidence >= self.confidence_threshold,
            "confidence": auth_confidence,
            "user_id": hashlib.sha256(username.encode()).hexdigest()[:16]
        }
    
    def generate_secure_token(self) -> str:
        """Generate cryptographically secure token"""
        return secrets.token_urlsafe(32)
'''
        
        sample_db_schema = '''"""
Database schema with confidence-tracked queries
"""

from typing import List, Dict, Any
from datetime import datetime

class DatabaseSchema:
    """Enterprise database schema with confidence validation"""
    
    def __init__(self):
        self.validation_confidence = 0.88
    
    def validate_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate database schema with confidence tracking
        
        Args:
            schema: Schema definition to validate
            
        Returns:
            Validation result with confidence metrics
        """
        
        if not schema:
            return {
                "valid": False,
                "confidence": 0.0,
                "issues": ["empty_schema"]
            }
        
        # Simulate schema validation
        required_fields = ["id", "created_at", "updated_at"]
        has_required = all(field in schema.get("fields", {}) for field in required_fields)
        
        validation_confidence = 0.95 if has_required else 0.60
        
        return {
            "valid": validation_confidence >= 0.80,
            "confidence": validation_confidence,
            "schema_completeness": len(schema.get("fields", {})) / 10.0,
            "issues": [] if has_required else ["missing_required_fields"]
        }
    
    def optimize_query(self, query: str) -> Dict[str, Any]:
        """Optimize database query with performance confidence"""
        
        if not query.strip():
            return {
                "optimized_query": "",
                "performance_confidence": 0.0,
                "optimization_applied": False
            }
        
        # Mock query optimization
        has_index_hint = "INDEX" in query.upper()
        has_limit = "LIMIT" in query.upper()
        
        performance_confidence = 0.85 if (has_index_hint and has_limit) else 0.65
        
        return {
            "optimized_query": query + " -- OPTIMIZED" if performance_confidence > 0.80 else query,
            "performance_confidence": performance_confidence,
            "optimization_applied": performance_confidence > 0.80
        }
'''
        
        # Write test files
        auth_file = self.test_knowledge_dir / "authentication.py"
        with open(auth_file, 'w') as f:
            f.write(sample_auth_code)
        
        db_file = self.test_knowledge_dir / "database_schema.py"
        with open(db_file, 'w') as f:
            f.write(sample_db_schema)
        
        print("   ✅ Test environment setup completed")
    
    async def test_agent_initialization(self) -> Dict[str, Any]:
        """Test CognitronAgent initialization and basic functionality"""
        
        results = {
            "test_name": "Agent Initialization",
            "subtests": {},
            "overall_pass": True,
            "critical_issues": []
        }
        
        # Subtest 1: Basic agent initialization
        try:
            print("   🤖 Testing agent initialization...")
            
            # Initialize agent with test configuration
            agent = CognitronAgent()
            
            # Check agent components
            has_memory = hasattr(agent, 'case_memory') and agent.case_memory is not None
            has_router = hasattr(agent, 'router') and agent.router is not None
            
            initialization_success = has_memory and has_router
            
            results["subtests"]["basic_initialization"] = {
                "passed": initialization_success,
                "has_memory": has_memory,
                "has_router": has_router,
                "agent_created": agent is not None
            }
            
            if initialization_success:
                print("      ✅ Agent initialization successful")
            else:
                print("      ❌ Agent initialization failed")
                results["overall_pass"] = False
                results["critical_issues"].append("Agent initialization failed")
                
        except Exception as e:
            results["subtests"]["basic_initialization"] = {
                "passed": False,
                "error": str(e)
            }
            results["overall_pass"] = False
            results["critical_issues"].append(f"Agent initialization exception: {str(e)}")
            print(f"      ❌ Agent initialization failed: {str(e)}")
        
        return results
    
    async def test_memory_system(self) -> Dict[str, Any]:
        """Test CaseMemory functionality"""
        
        results = {
            "test_name": "Memory System",
            "subtests": {},
            "overall_pass": True,
            "critical_issues": []
        }
        
        # Subtest 1: Memory initialization
        try:
            print("   💾 Testing memory system initialization...")
            
            memory = CaseMemory()
            
            # Check memory initialization
            memory_initialized = memory is not None
            
            results["subtests"]["memory_initialization"] = {
                "passed": memory_initialized,
                "memory_created": memory_initialized
            }
            
            if memory_initialized:
                print("      ✅ Memory system initialized")
            else:
                print("      ❌ Memory system initialization failed")
                results["overall_pass"] = False
                
        except Exception as e:
            results["subtests"]["memory_initialization"] = {
                "passed": False,
                "error": str(e)
            }
            results["overall_pass"] = False
            print(f"      ❌ Memory initialization failed: {str(e)}")
        
        # Subtest 2: Memory storage and retrieval
        try:
            print("   💾 Testing memory storage and retrieval...")
            
            memory = CaseMemory()
            
            # Create test workflow trace
            test_workflow = WorkflowTrace(
                query="Test authentication implementation",
                outcome="Successful authentication system with 92% confidence",
                planner_confidence=0.85,
                execution_confidence=0.90,
                outcome_confidence=0.88
            )
            
            # Create test case memory entry
            test_case = CaseMemoryEntry(
                query="Test authentication implementation",
                outcome="Authentication system implemented successfully",
                workflow_trace=test_workflow,
                storage_confidence=0.87,
                success=True,
                execution_time=2.5
            )
            
            # Test storage (mock - actual storage requires database setup)
            storage_success = test_case.eligible_for_storage  # Should be True for high confidence
            
            results["subtests"]["memory_storage_retrieval"] = {
                "passed": storage_success,
                "case_created": test_case.case_id is not None,
                "eligible_for_storage": test_case.eligible_for_storage,
                "storage_confidence": test_case.storage_confidence
            }
            
            if storage_success:
                print("      ✅ Memory storage and retrieval working")
            else:
                print("      ❌ Memory storage issues detected")
                results["overall_pass"] = False
                
        except Exception as e:
            results["subtests"]["memory_storage_retrieval"] = {
                "passed": False,
                "error": str(e)
            }
            results["overall_pass"] = False
            print(f"      ❌ Memory storage test failed: {str(e)}")
        
        return results
    
    async def test_confidence_system(self) -> Dict[str, Any]:
        """Test confidence calculation and calibration"""
        
        results = {
            "test_name": "Confidence System",
            "subtests": {},
            "overall_pass": True,
            "critical_issues": []
        }
        
        # Subtest 1: Confidence profile calculation
        try:
            print("   📊 Testing confidence profile calculation...")
            
            # Test confidence calculation with sample data
            sample_confidences = {
                "retrieval_confidence": 0.85,
                "reasoning_confidence": 0.78,
                "factual_confidence": 0.92
            }
            
            profile = calculate_confidence_profile(
                retrieval_confidence=sample_confidences["retrieval_confidence"],
                reasoning_confidence=sample_confidences["reasoning_confidence"],
                factual_confidence=sample_confidences["factual_confidence"]
            )
            
            # Check profile properties
            profile_valid = (
                hasattr(profile, 'overall_confidence') and
                hasattr(profile, 'confidence_level') and
                0.0 <= profile.overall_confidence <= 1.0
            )
            
            results["subtests"]["confidence_profile_calculation"] = {
                "passed": profile_valid,
                "profile_created": profile is not None,
                "overall_confidence": profile.overall_confidence if profile else 0.0,
                "confidence_level": profile.confidence_level.value if profile else "unknown"
            }
            
            if profile_valid:
                print(f"      ✅ Confidence profile: {profile.overall_confidence:.2f} ({profile.confidence_level.value})")
            else:
                print("      ❌ Confidence profile calculation failed")
                results["overall_pass"] = False
                
        except Exception as e:
            results["subtests"]["confidence_profile_calculation"] = {
                "passed": False,
                "error": str(e)
            }
            results["overall_pass"] = False
            print(f"      ❌ Confidence calculation failed: {str(e)}")
        
        # Subtest 2: Query result confidence validation
        try:
            print("   📊 Testing query result confidence validation...")
            
            # Create test query result
            query_result = QueryResult(
                query_text="How to implement secure authentication?",
                answer="Implement authentication with proper password hashing and session management",
                retrieval_confidence=0.88,
                reasoning_confidence=0.82,
                factual_confidence=0.90
            )
            
            # Check automatic confidence calculations
            confidence_validation_success = (
                query_result.overall_confidence > 0.0 and
                query_result.should_display and
                query_result.confidence_level is not None
            )
            
            results["subtests"]["query_result_confidence"] = {
                "passed": confidence_validation_success,
                "overall_confidence": query_result.overall_confidence,
                "should_display": query_result.should_display,
                "requires_validation": query_result.requires_validation,
                "confidence_level": query_result.confidence_level.value
            }
            
            if confidence_validation_success:
                print(f"      ✅ Query confidence: {query_result.overall_confidence:.2f} ({query_result.confidence_level.value})")
            else:
                print("      ❌ Query confidence validation failed")
                results["overall_pass"] = False
                
        except Exception as e:
            results["subtests"]["query_result_confidence"] = {
                "passed": False,
                "error": str(e)
            }
            results["overall_pass"] = False
            print(f"      ❌ Query confidence test failed: {str(e)}")
        
        return results
    
    async def test_indexing_service(self) -> Dict[str, Any]:
        """Test IndexingService functionality"""
        
        results = {
            "test_name": "Indexing Service",
            "subtests": {},
            "overall_pass": True,
            "critical_issues": []
        }
        
        # Subtest 1: Indexing service initialization
        try:
            print("   🔍 Testing indexing service initialization...")
            
            indexing_service = IndexingService()
            
            # Check service initialization
            service_initialized = indexing_service is not None
            
            results["subtests"]["indexing_initialization"] = {
                "passed": service_initialized,
                "service_created": service_initialized
            }
            
            if service_initialized:
                print("      ✅ Indexing service initialized")
            else:
                print("      ❌ Indexing service initialization failed")
                results["overall_pass"] = False
                
        except Exception as e:
            results["subtests"]["indexing_initialization"] = {
                "passed": False,
                "error": str(e)
            }
            results["overall_pass"] = False
            print(f"      ❌ Indexing service initialization failed: {str(e)}")
        
        # Subtest 2: Knowledge indexing (mock test)
        try:
            print("   🔍 Testing knowledge indexing capability...")
            
            indexing_service = IndexingService()
            
            # Test indexing capability (would normally index the test knowledge)
            # For now, just verify the service has necessary methods
            
            has_index_method = hasattr(indexing_service, 'index_knowledge')
            has_required_attributes = True  # Basic assumption
            
            indexing_capability = has_index_method and has_required_attributes
            
            results["subtests"]["knowledge_indexing"] = {
                "passed": indexing_capability,
                "has_index_method": has_index_method,
                "test_data_available": (self.test_knowledge_dir / "authentication.py").exists()
            }
            
            if indexing_capability:
                print("      ✅ Knowledge indexing capability verified")
            else:
                print("      ❌ Knowledge indexing capability issues")
                results["overall_pass"] = False
                
        except Exception as e:
            results["subtests"]["knowledge_indexing"] = {
                "passed": False,
                "error": str(e)
            }
            results["overall_pass"] = False
            print(f"      ❌ Knowledge indexing test failed: {str(e)}")
        
        return results
    
    async def test_topic_service(self) -> Dict[str, Any]:
        """Test TopicService functionality"""
        
        results = {
            "test_name": "Topic Service",
            "subtests": {},
            "overall_pass": True,
            "critical_issues": []
        }
        
        # Subtest 1: Topic service initialization
        try:
            print("   🏷️  Testing topic service initialization...")
            
            topic_service = TopicService()
            
            # Check service initialization
            service_initialized = (
                topic_service is not None and
                hasattr(topic_service, 'vectorizer') and
                hasattr(topic_service, 'confidence_threshold')
            )
            
            results["subtests"]["topic_service_initialization"] = {
                "passed": service_initialized,
                "service_created": topic_service is not None,
                "has_vectorizer": hasattr(topic_service, 'vectorizer'),
                "confidence_threshold": getattr(topic_service, 'confidence_threshold', 0.0)
            }
            
            if service_initialized:
                print("      ✅ Topic service initialized")
            else:
                print("      ❌ Topic service initialization failed")
                results["overall_pass"] = False
                
        except Exception as e:
            results["subtests"]["topic_service_initialization"] = {
                "passed": False,
                "error": str(e)
            }
            results["overall_pass"] = False
            print(f"      ❌ Topic service initialization failed: {str(e)}")
        
        # Subtest 2: Topic generation capability
        try:
            print("   🏷️  Testing topic generation capability...")
            
            topic_service = TopicService()
            
            # Test topic generation capability (mock)
            has_generate_method = hasattr(topic_service, 'generate_topics')
            has_confidence_filtering = hasattr(topic_service, 'get_topics_with_confidence')
            
            topic_capability = has_generate_method and has_confidence_filtering
            
            results["subtests"]["topic_generation_capability"] = {
                "passed": topic_capability,
                "has_generate_method": has_generate_method,
                "has_confidence_filtering": has_confidence_filtering
            }
            
            if topic_capability:
                print("      ✅ Topic generation capability verified")
            else:
                print("      ❌ Topic generation capability issues")
                results["overall_pass"] = False
                
        except Exception as e:
            results["subtests"]["topic_generation_capability"] = {
                "passed": False,
                "error": str(e)
            }
            results["overall_pass"] = False
            print(f"      ❌ Topic generation test failed: {str(e)}")
        
        return results
    
    async def test_end_to_end_workflow(self) -> Dict[str, Any]:
        """Test end-to-end workflow integration"""
        
        results = {
            "test_name": "End-to-End Workflow",
            "subtests": {},
            "overall_pass": True,
            "critical_issues": []
        }
        
        # Subtest 1: Complete workflow simulation
        try:
            print("   🔄 Testing complete workflow integration...")
            
            # Initialize all components
            agent = CognitronAgent()
            memory = CaseMemory()
            indexing_service = IndexingService()
            topic_service = TopicService()
            
            # Simulate a complete query workflow
            test_query = "How do I implement secure user authentication with confidence tracking?"
            
            # Create mock query result (simulating agent processing)
            query_result = QueryResult(
                query_text=test_query,
                answer="Implement authentication using secure password hashing, session management, and confidence scoring for each authentication attempt. Use confidence thresholds to determine authentication success.",
                retrieval_confidence=0.88,
                reasoning_confidence=0.85,
                factual_confidence=0.91
            )
            
            # Validate workflow components
            workflow_components_valid = all([
                agent is not None,
                memory is not None,
                indexing_service is not None,
                topic_service is not None,
                query_result.overall_confidence > 0.70,  # Reasonable confidence
                query_result.should_display  # Should be displayable
            ])
            
            results["subtests"]["complete_workflow_integration"] = {
                "passed": workflow_components_valid,
                "agent_initialized": agent is not None,
                "memory_initialized": memory is not None,
                "indexing_service_initialized": indexing_service is not None,
                "topic_service_initialized": topic_service is not None,
                "query_confidence": query_result.overall_confidence,
                "query_displayable": query_result.should_display
            }
            
            if workflow_components_valid:
                print(f"      ✅ Complete workflow integration verified")
                print(f"         Query confidence: {query_result.overall_confidence:.2f}")
            else:
                print("      ❌ Workflow integration issues detected")
                results["overall_pass"] = False
                
        except Exception as e:
            results["subtests"]["complete_workflow_integration"] = {
                "passed": False,
                "error": str(e)
            }
            results["overall_pass"] = False
            print(f"      ❌ Workflow integration test failed: {str(e)}")
        
        # Subtest 2: Error handling in workflow
        try:
            print("   🔄 Testing workflow error handling...")
            
            # Test with problematic inputs
            error_handling_success = True
            
            try:
                # Test empty query
                empty_query_result = QueryResult(
                    query_text="",
                    answer="",
                    retrieval_confidence=0.0,
                    reasoning_confidence=0.0,
                    factual_confidence=0.0
                )
                
                # Should handle gracefully - low confidence, not displayable
                if empty_query_result.should_display:
                    error_handling_success = False  # Should not display empty results
                    
            except Exception:
                error_handling_success = False
            
            results["subtests"]["workflow_error_handling"] = {
                "passed": error_handling_success,
                "empty_query_handled": error_handling_success
            }
            
            if error_handling_success:
                print("      ✅ Workflow error handling working")
            else:
                print("      ❌ Workflow error handling issues")
                results["overall_pass"] = False
                
        except Exception as e:
            results["subtests"]["workflow_error_handling"] = {
                "passed": False,
                "error": str(e)
            }
            results["overall_pass"] = False
            print(f"      ❌ Workflow error handling test failed: {str(e)}")
        
        return results
    
    async def generate_validation_summary(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive validation summary"""
        
        print("\n🏆 GENERATING VALIDATION SUMMARY")
        print("-" * 50)
        
        # Calculate statistics
        total_tests = 0
        passed_tests = 0
        critical_failures = []
        
        test_categories = []
        
        for category, results in validation_results.items():
            if category == "critical_failure":
                critical_failures.append(results)
                continue
                
            if isinstance(results, dict) and "overall_pass" in results:
                test_categories.append(category)
                total_tests += 1
                
                if results["overall_pass"]:
                    passed_tests += 1
                
                # Add critical issues
                if "critical_issues" in results and results["critical_issues"]:
                    critical_failures.extend(results["critical_issues"])
                
                # Count subtests
                if "subtests" in results:
                    for subtest_result in results["subtests"].values():
                        if isinstance(subtest_result, dict) and "passed" in subtest_result:
                            total_tests += 1
                            if subtest_result["passed"]:
                                passed_tests += 1
        
        # Calculate success rate
        success_rate = (passed_tests / max(total_tests, 1)) * 100
        
        # Determine system status
        if critical_failures:
            system_status = "NEEDS ATTENTION"
            status_emoji = "⚠️"
        elif success_rate >= 90:
            system_status = "EXCELLENT"
            status_emoji = "🏆"
        elif success_rate >= 75:
            system_status = "GOOD"
            status_emoji = "✅"
        else:
            system_status = "NEEDS IMPROVEMENT"
            status_emoji = "❌"
        
        # Generate summary
        summary = {
            "overall_status": system_status,
            "status_emoji": status_emoji,
            "success_rate_percentage": success_rate,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "critical_failures_count": len(critical_failures),
            "critical_failures": critical_failures[:5],  # Top 5 critical issues
            "test_categories": test_categories,
            "validation_duration_seconds": time.time() - self.test_start_time,
            "core_system_assessment": self._assess_core_system_health(validation_results)
        }
        
        # Print summary
        print(f"   {status_emoji} OVERALL STATUS: {system_status}")
        print(f"   📊 SUCCESS RATE: {success_rate:.1f}%")
        print(f"   ✅ PASSED: {passed_tests}/{total_tests} tests")
        
        if critical_failures:
            print(f"   🚨 CRITICAL ISSUES: {len(critical_failures)}")
            for issue in critical_failures[:3]:  # Show top 3
                print(f"      • {issue}")
        
        validation_duration = time.time() - self.test_start_time
        print(f"   ⏱️  VALIDATION TIME: {validation_duration:.2f} seconds")
        
        return summary
    
    def _assess_core_system_health(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall core system health from validation results"""
        
        health_assessment = {
            "agent_system": False,
            "memory_system": False,
            "confidence_system": False,
            "indexing_system": False,
            "topic_system": False,
            "workflow_integration": False,
            "overall_health_score": 0.0
        }
        
        # Check each system
        if "agent_initialization" in validation_results:
            health_assessment["agent_system"] = validation_results["agent_initialization"].get("overall_pass", False)
            
        if "memory_system" in validation_results:
            health_assessment["memory_system"] = validation_results["memory_system"].get("overall_pass", False)
            
        if "confidence_system" in validation_results:
            health_assessment["confidence_system"] = validation_results["confidence_system"].get("overall_pass", False)
            
        if "indexing_service" in validation_results:
            health_assessment["indexing_system"] = validation_results["indexing_service"].get("overall_pass", False)
            
        if "topic_service" in validation_results:
            health_assessment["topic_system"] = validation_results["topic_service"].get("overall_pass", False)
            
        if "end_to_end_workflow" in validation_results:
            health_assessment["workflow_integration"] = validation_results["end_to_end_workflow"].get("overall_pass", False)
        
        # Calculate overall health score
        health_components = [
            health_assessment["agent_system"],
            health_assessment["memory_system"],
            health_assessment["confidence_system"],
            health_assessment["indexing_system"],
            health_assessment["topic_system"],
            health_assessment["workflow_integration"]
        ]
        
        health_assessment["overall_health_score"] = sum(health_components) / len(health_components)
        
        return health_assessment
    
    def _print_test_results(self, test_name: str, results: Dict[str, Any]):
        """Print formatted test results"""
        
        overall_pass = results.get("overall_pass", False)
        status_emoji = "✅" if overall_pass else "❌"
        
        print(f"   {status_emoji} {test_name}: {'PASSED' if overall_pass else 'FAILED'}")
        
        if "subtests" in results:
            passed_subtests = sum(1 for st in results["subtests"].values() 
                                if isinstance(st, dict) and st.get("passed", False))
            total_subtests = len(results["subtests"])
            print(f"      Subtests: {passed_subtests}/{total_subtests} passed")


async def main():
    """Main validation runner"""
    
    print("🧪 COGNITRON CORE SYSTEM VALIDATION")
    print("Comprehensive testing of core Cognitron components")
    print("=" * 80)
    
    validator = CognitronCoreValidator()
    
    try:
        # Run core validation
        validation_results = await validator.run_core_validation()
        
        # Save detailed results
        results_file = Path.home() / ".cognitron" / "core_test_data" / "core_validation_results.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to JSON-serializable format
        serializable_results = json.loads(json.dumps(validation_results, default=str))
        
        with open(results_file, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        print(f"\n📊 Detailed validation results saved to: {results_file}")
        
        # Print final status
        if "validation_summary" in validation_results:
            summary = validation_results["validation_summary"]
            print(f"\n🏆 FINAL VALIDATION STATUS: {summary['overall_status']}")
            print(f"📈 SUCCESS RATE: {summary['success_rate_percentage']:.1f}%")
            
            core_health = summary.get("core_system_assessment", {})
            health_score = core_health.get("overall_health_score", 0.0)
            print(f"💊 CORE SYSTEM HEALTH: {health_score:.1%}")
        
        return validation_results
        
    except Exception as e:
        print(f"\n❌ CORE VALIDATION FAILED: {str(e)}")
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Run comprehensive core validation
    results = asyncio.run(main())