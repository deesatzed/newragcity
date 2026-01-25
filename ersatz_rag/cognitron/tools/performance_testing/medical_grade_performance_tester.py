#!/usr/bin/env python3
"""
Medical-Grade Performance Testing Framework
Comprehensive performance testing with medical-grade requirements and zero-tolerance for regressions.
"""

import asyncio
import time
import psutil
import statistics
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import concurrent.futures
from contextlib import asynccontextmanager


@dataclass
class PerformanceBenchmark:
    """Performance benchmark definition."""
    name: str
    metric_type: str  # "latency", "throughput", "memory", "cpu"
    target_value: float
    tolerance: float  # Allowed deviation (e.g., 0.1 = 10%)
    direction: str  # "lower_better", "higher_better"
    unit: str


@dataclass
class PerformanceResult:
    """Result of a performance test."""
    test_name: str
    application: str
    metric_name: str
    measured_value: float
    benchmark_value: float
    within_tolerance: bool
    deviation_percent: float
    execution_time: float
    resource_usage: Dict[str, float]
    timestamp: str
    test_conditions: Dict[str, Any]


class MedicalGradePerformanceTester:
    """Medical-grade performance testing with zero-tolerance for regressions."""
    
    def __init__(self, application: str):
        self.application = application
        self.logger = self._setup_logging()
        self.results: List[PerformanceResult] = []
        
        # Define medical-grade performance benchmarks
        self.benchmarks = self._define_performance_benchmarks()
        
        # Load baseline metrics
        self.baseline_metrics = self._load_baseline_metrics()
        
        # Performance limits (zero tolerance)
        self.REGRESSION_TOLERANCE = 0.05  # 5% max regression
        self.MEMORY_LEAK_THRESHOLD = 50   # MB per hour
        self.CPU_EFFICIENCY_MIN = 0.80    # 80% minimum efficiency
    
    def _setup_logging(self) -> logging.Logger:
        """Set up performance test logging."""
        logger = logging.getLogger(f"performance_{self.application}")
        logger.setLevel(logging.DEBUG)
        
        handler = logging.FileHandler(f"performance_{self.application}.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _define_performance_benchmarks(self) -> Dict[str, Dict[str, PerformanceBenchmark]]:
        """Define performance benchmarks for each application."""
        benchmarks = {
            "cognitron-core": {
                "query_response_time": PerformanceBenchmark(
                    name="Query Response Time",
                    metric_type="latency",
                    target_value=1000.0,  # 1 second
                    tolerance=0.1,        # 10% tolerance
                    direction="lower_better",
                    unit="milliseconds"
                ),
                "confidence_calculation_time": PerformanceBenchmark(
                    name="Confidence Calculation Time",
                    metric_type="latency", 
                    target_value=100.0,   # 100ms
                    tolerance=0.05,       # 5% tolerance
                    direction="lower_better",
                    unit="milliseconds"
                ),
                "memory_retrieval_time": PerformanceBenchmark(
                    name="Memory Retrieval Time",
                    metric_type="latency",
                    target_value=500.0,   # 500ms
                    tolerance=0.1,
                    direction="lower_better", 
                    unit="milliseconds"
                ),
                "memory_usage": PerformanceBenchmark(
                    name="Memory Usage",
                    metric_type="memory",
                    target_value=300.0,   # 300MB
                    tolerance=0.15,       # 15% tolerance
                    direction="lower_better",
                    unit="megabytes"
                ),
                "query_throughput": PerformanceBenchmark(
                    name="Query Throughput",
                    metric_type="throughput",
                    target_value=10.0,    # 10 queries/second
                    tolerance=0.1,
                    direction="higher_better",
                    unit="queries_per_second"
                )
            },
            
            "cognitron-temporal": {
                "pattern_recognition_time": PerformanceBenchmark(
                    name="Pattern Recognition Time",
                    metric_type="latency",
                    target_value=2000.0,  # 2 seconds
                    tolerance=0.1,
                    direction="lower_better",
                    unit="milliseconds"
                ),
                "context_resurrection_time": PerformanceBenchmark(
                    name="Context Resurrection Time",
                    metric_type="latency",
                    target_value=1500.0,  # 1.5 seconds
                    tolerance=0.1,
                    direction="lower_better",
                    unit="milliseconds"
                ),
                "memory_decay_processing_time": PerformanceBenchmark(
                    name="Memory Decay Processing Time",
                    metric_type="latency",
                    target_value=500.0,   # 500ms
                    tolerance=0.1,
                    direction="lower_better",
                    unit="milliseconds"
                ),
                "pattern_crystallization_time": PerformanceBenchmark(
                    name="Pattern Crystallization Time",
                    metric_type="latency",
                    target_value=3000.0,  # 3 seconds
                    tolerance=0.15,
                    direction="lower_better",
                    unit="milliseconds"
                ),
                "temporal_memory_usage": PerformanceBenchmark(
                    name="Temporal Memory Usage",
                    metric_type="memory",
                    target_value=500.0,   # 500MB
                    tolerance=0.2,
                    direction="lower_better",
                    unit="megabytes"
                )
            },
            
            "cognitron-platform": {
                "indexing_speed": PerformanceBenchmark(
                    name="Indexing Speed",
                    metric_type="throughput",
                    target_value=100.0,   # 100 docs/second
                    tolerance=0.1,
                    direction="higher_better",
                    unit="documents_per_second"
                ),
                "search_latency": PerformanceBenchmark(
                    name="Search Latency",
                    metric_type="latency",
                    target_value=300.0,   # 300ms
                    tolerance=0.1,
                    direction="lower_better",
                    unit="milliseconds"
                ),
                "topic_generation_time": PerformanceBenchmark(
                    name="Topic Generation Time",
                    metric_type="latency",
                    target_value=5000.0,  # 5 seconds
                    tolerance=0.15,
                    direction="lower_better",
                    unit="milliseconds"
                ),
                "connector_sync_time": PerformanceBenchmark(
                    name="Connector Sync Time",
                    metric_type="latency",
                    target_value=2000.0,  # 2 seconds
                    tolerance=0.1,
                    direction="lower_better",
                    unit="milliseconds"
                ),
                "platform_memory_usage": PerformanceBenchmark(
                    name="Platform Memory Usage",
                    metric_type="memory",
                    target_value=1000.0,  # 1GB
                    tolerance=0.15,
                    direction="lower_better",
                    unit="megabytes"
                )
            }
        }
        
        return benchmarks.get(self.application, {})
    
    def _load_baseline_metrics(self) -> Dict[str, float]:
        """Load baseline performance metrics."""
        baseline_file = Path(f"baselines/{self.application}_performance_baseline.json")
        if baseline_file.exists():
            with open(baseline_file) as f:
                return json.load(f)
        return {}
    
    async def run_comprehensive_performance_suite(self) -> Dict[str, Any]:
        """Execute comprehensive performance testing suite."""
        self.logger.info(f"Starting comprehensive performance testing for {self.application}")
        
        start_time = time.time()
        
        test_results = {
            "application": self.application,
            "test_start": start_time,
            "test_environment": self._get_test_environment_info(),
            "benchmark_results": [],
            "load_test_results": {},
            "stress_test_results": {},
            "memory_leak_test": {},
            "regression_analysis": {},
            "medical_grade_compliance": False
        }
        
        try:
            # 1. Baseline Performance Tests
            self.logger.info("Running baseline performance tests")
            baseline_results = await self._run_baseline_tests()
            test_results["benchmark_results"] = baseline_results
            
            # 2. Load Testing
            self.logger.info("Running load tests")
            load_results = await self._run_load_tests()
            test_results["load_test_results"] = load_results
            
            # 3. Stress Testing
            self.logger.info("Running stress tests") 
            stress_results = await self._run_stress_tests()
            test_results["stress_test_results"] = stress_results
            
            # 4. Memory Leak Testing
            self.logger.info("Running memory leak tests")
            memory_results = await self._run_memory_leak_tests()
            test_results["memory_leak_test"] = memory_results
            
            # 5. Performance Regression Analysis
            self.logger.info("Running regression analysis")
            regression_results = await self._run_regression_analysis()
            test_results["regression_analysis"] = regression_results
            
            # 6. Medical-Grade Compliance Validation
            test_results["medical_grade_compliance"] = self._validate_medical_grade_compliance(test_results)
            
        except Exception as e:
            self.logger.error(f"Performance testing failed: {e}")
            test_results["error"] = str(e)
        
        finally:
            test_results["test_end"] = time.time()
            test_results["total_duration"] = test_results["test_end"] - test_results["test_start"]
        
        await self._generate_performance_report(test_results)
        return test_results
    
    def _get_test_environment_info(self) -> Dict[str, Any]:
        """Get test environment information."""
        return {
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
            "python_version": psutil.Process().exe,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _run_baseline_tests(self) -> List[PerformanceResult]:
        """Run baseline performance tests for all benchmarks."""
        baseline_results = []
        
        for benchmark_name, benchmark in self.benchmarks.items():
            self.logger.info(f"Testing {benchmark_name}")
            
            # Run performance test
            result = await self._measure_performance(benchmark_name, benchmark)
            baseline_results.append(result)
            
            # Validate against benchmark
            if not result.within_tolerance:
                self.logger.warning(f"Benchmark failed: {benchmark_name} - {result.deviation_percent:.2f}% deviation")
        
        return baseline_results
    
    async def _measure_performance(self, test_name: str, benchmark: PerformanceBenchmark) -> PerformanceResult:
        """Measure performance for a specific test."""
        # Get initial system state
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        initial_cpu = psutil.cpu_percent()
        
        # Execute performance test
        start_time = time.time()
        measured_value = await self._execute_performance_test(test_name)
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Get final system state
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        final_cpu = psutil.cpu_percent()
        
        # Calculate deviation
        if benchmark.direction == "lower_better":
            deviation_percent = (measured_value - benchmark.target_value) / benchmark.target_value
        else:
            deviation_percent = (benchmark.target_value - measured_value) / benchmark.target_value
        
        within_tolerance = abs(deviation_percent) <= benchmark.tolerance
        
        return PerformanceResult(
            test_name=test_name,
            application=self.application,
            metric_name=benchmark.name,
            measured_value=measured_value,
            benchmark_value=benchmark.target_value,
            within_tolerance=within_tolerance,
            deviation_percent=deviation_percent * 100,
            execution_time=execution_time,
            resource_usage={
                "memory_delta_mb": final_memory - initial_memory,
                "cpu_usage_percent": final_cpu - initial_cpu
            },
            timestamp=datetime.now().isoformat(),
            test_conditions={
                "load_level": "baseline",
                "concurrent_users": 1,
                "test_duration_ms": execution_time
            }
        )
    
    async def _execute_performance_test(self, test_name: str) -> float:
        """Execute specific performance test and return measured value."""
        # This would contain actual test implementation
        # For now, simulate with random values around benchmarks
        
        if "query_response" in test_name:
            await asyncio.sleep(0.8)  # Simulate query processing
            return 800.0  # 800ms response time
        
        elif "confidence_calculation" in test_name:
            await asyncio.sleep(0.08)  # Simulate confidence calculation
            return 80.0   # 80ms calculation time
            
        elif "memory_retrieval" in test_name:
            await asyncio.sleep(0.4)  # Simulate memory retrieval
            return 400.0  # 400ms retrieval time
            
        elif "pattern_recognition" in test_name:
            await asyncio.sleep(1.8)  # Simulate pattern analysis
            return 1800.0 # 1.8s pattern recognition
            
        elif "indexing_speed" in test_name:
            await asyncio.sleep(1.0)  # Simulate indexing 100 documents
            return 100.0  # 100 docs/second
            
        else:
            await asyncio.sleep(0.1)
            return 100.0
    
    async def _run_load_tests(self) -> Dict[str, Any]:
        """Run load testing scenarios."""
        load_scenarios = [
            {"concurrent_users": 5, "duration_seconds": 30},
            {"concurrent_users": 10, "duration_seconds": 60},
            {"concurrent_users": 25, "duration_seconds": 120},
            {"concurrent_users": 50, "duration_seconds": 180}
        ]
        
        load_results = {}
        
        for scenario in load_scenarios:
            scenario_name = f"load_{scenario['concurrent_users']}_users"
            self.logger.info(f"Running load test: {scenario_name}")
            
            scenario_result = await self._execute_load_scenario(scenario)
            load_results[scenario_name] = scenario_result
            
            # Check if system degrades under load
            if scenario_result["average_response_time"] > 2000:  # 2s threshold
                self.logger.warning(f"Performance degradation detected in {scenario_name}")
        
        return load_results
    
    async def _execute_load_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a load testing scenario."""
        concurrent_users = scenario["concurrent_users"]
        duration_seconds = scenario["duration_seconds"]
        
        # Simulate concurrent users
        tasks = []
        for _ in range(concurrent_users):
            task = asyncio.create_task(self._simulate_user_load(duration_seconds))
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        successful_requests = [r for r in results if not isinstance(r, Exception)]
        response_times = [r["response_time"] for r in successful_requests]
        
        return {
            "concurrent_users": concurrent_users,
            "duration_seconds": duration_seconds,
            "total_requests": len(results),
            "successful_requests": len(successful_requests),
            "failed_requests": len(results) - len(successful_requests),
            "success_rate": len(successful_requests) / len(results) * 100,
            "average_response_time": statistics.mean(response_times) if response_times else 0,
            "median_response_time": statistics.median(response_times) if response_times else 0,
            "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0,
            "p99_response_time": statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else 0
        }
    
    async def _simulate_user_load(self, duration_seconds: int) -> Dict[str, Any]:
        """Simulate user load for specified duration."""
        end_time = time.time() + duration_seconds
        requests = []
        
        while time.time() < end_time:
            start_time = time.time()
            
            # Simulate user request
            await self._execute_performance_test("query_response")
            
            response_time = (time.time() - start_time) * 1000
            requests.append({"response_time": response_time})
            
            # Small delay between requests
            await asyncio.sleep(0.1)
        
        return {
            "requests": len(requests),
            "response_time": statistics.mean([r["response_time"] for r in requests])
        }
    
    async def _run_stress_tests(self) -> Dict[str, Any]:
        """Run stress testing to find breaking points."""
        stress_results = {
            "memory_stress": await self._test_memory_stress(),
            "cpu_stress": await self._test_cpu_stress(),
            "concurrent_load_stress": await self._test_concurrent_stress()
        }
        
        return stress_results
    
    async def _test_memory_stress(self) -> Dict[str, Any]:
        """Test memory usage under stress."""
        self.logger.info("Running memory stress test")
        
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        peak_memory = initial_memory
        
        # Simulate memory-intensive operations
        large_data_sets = []
        
        for i in range(100):
            # Create large data structure
            large_data = [{"id": j, "data": "x" * 1000} for j in range(1000)]
            large_data_sets.append(large_data)
            
            # Monitor memory
            current_memory = psutil.Process().memory_info().rss / 1024 / 1024
            peak_memory = max(peak_memory, current_memory)
            
            # Process data
            await self._execute_performance_test("memory_operation")
            
            # Clean up some data to test garbage collection
            if i % 10 == 0:
                large_data_sets = large_data_sets[-50:]  # Keep only last 50
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        return {
            "initial_memory_mb": initial_memory,
            "peak_memory_mb": peak_memory,
            "final_memory_mb": final_memory,
            "memory_growth_mb": final_memory - initial_memory,
            "memory_efficiency": "good" if final_memory - initial_memory < 100 else "concerning"
        }
    
    async def _test_cpu_stress(self) -> Dict[str, Any]:
        """Test CPU usage under stress."""
        self.logger.info("Running CPU stress test")
        
        # Run CPU-intensive operations
        start_time = time.time()
        cpu_samples = []
        
        # Create CPU-intensive tasks
        with concurrent.futures.ThreadPoolExecutor(max_workers=psutil.cpu_count()) as executor:
            # Submit CPU-intensive tasks
            futures = []
            for _ in range(psutil.cpu_count() * 2):
                future = executor.submit(self._cpu_intensive_task)
                futures.append(future)
            
            # Monitor CPU usage
            for _ in range(30):  # 30 seconds of monitoring
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_samples.append(cpu_percent)
            
            # Wait for tasks to complete
            concurrent.futures.wait(futures, timeout=30)
        
        return {
            "test_duration_seconds": time.time() - start_time,
            "average_cpu_percent": statistics.mean(cpu_samples),
            "peak_cpu_percent": max(cpu_samples),
            "cpu_efficiency": statistics.mean(cpu_samples) / 100.0
        }
    
    def _cpu_intensive_task(self) -> float:
        """CPU-intensive computation task."""
        result = 0
        for i in range(1000000):
            result += i ** 0.5
        return result
    
    async def _test_concurrent_stress(self) -> Dict[str, Any]:
        """Test system behavior under high concurrency."""
        self.logger.info("Running concurrent stress test")
        
        # Gradually increase concurrent load
        results = {}
        
        for concurrent_users in [10, 25, 50, 100, 200]:
            self.logger.info(f"Testing {concurrent_users} concurrent users")
            
            start_time = time.time()
            
            # Create concurrent tasks
            tasks = []
            for _ in range(concurrent_users):
                task = asyncio.create_task(self._execute_performance_test("stress_query"))
                tasks.append(task)
            
            # Wait for completion or timeout
            try:
                await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=60)
                success = True
                response_time = time.time() - start_time
            except asyncio.TimeoutError:
                success = False
                response_time = 60.0
            
            results[f"{concurrent_users}_users"] = {
                "success": success,
                "response_time_seconds": response_time,
                "requests_per_second": concurrent_users / response_time if success else 0
            }
            
            # Stop if system is failing
            if not success:
                self.logger.warning(f"System failed at {concurrent_users} concurrent users")
                break
        
        return results
    
    async def _run_memory_leak_tests(self) -> Dict[str, Any]:
        """Run memory leak detection tests."""
        self.logger.info("Running memory leak tests")
        
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_samples = [initial_memory]
        
        # Run operations for extended period
        for iteration in range(100):
            await self._execute_performance_test("leak_test_operation")
            
            if iteration % 10 == 0:
                current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                memory_samples.append(current_memory)
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_growth = final_memory - initial_memory
        
        # Analyze memory growth trend
        if len(memory_samples) > 2:
            # Linear regression to detect memory growth trend
            x = list(range(len(memory_samples)))
            y = memory_samples
            
            # Simple linear regression
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(x[i] ** 2 for i in range(n))
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
            
            # Slope represents MB per iteration
            memory_leak_rate = slope * 10  # MB per 10 iterations
        else:
            memory_leak_rate = 0
        
        return {
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "total_growth_mb": memory_growth,
            "memory_leak_rate_mb_per_hour": memory_leak_rate * 360,  # Approximate hourly rate
            "leak_detected": memory_leak_rate > self.MEMORY_LEAK_THRESHOLD / 360,
            "memory_samples": memory_samples
        }
    
    async def _run_regression_analysis(self) -> Dict[str, Any]:
        """Run performance regression analysis against baselines."""
        self.logger.info("Running performance regression analysis")
        
        regression_results = {
            "baseline_comparison": {},
            "regressions_detected": [],
            "improvements_detected": [],
            "overall_trend": "stable"
        }
        
        # Compare current results with baseline
        for result in self.results:
            if result.metric_name in self.baseline_metrics:
                baseline_value = self.baseline_metrics[result.metric_name]
                current_value = result.measured_value
                
                change_percent = (current_value - baseline_value) / baseline_value * 100
                
                regression_results["baseline_comparison"][result.metric_name] = {
                    "baseline_value": baseline_value,
                    "current_value": current_value,
                    "change_percent": change_percent,
                    "regression": abs(change_percent) > self.REGRESSION_TOLERANCE * 100
                }
                
                if change_percent > self.REGRESSION_TOLERANCE * 100:
                    regression_results["regressions_detected"].append({
                        "metric": result.metric_name,
                        "regression_percent": change_percent,
                        "severity": "critical" if change_percent > 20 else "warning"
                    })
                elif change_percent < -self.REGRESSION_TOLERANCE * 100:
                    regression_results["improvements_detected"].append({
                        "metric": result.metric_name,
                        "improvement_percent": abs(change_percent)
                    })
        
        # Determine overall trend
        if regression_results["regressions_detected"]:
            regression_results["overall_trend"] = "regressing"
        elif regression_results["improvements_detected"]:
            regression_results["overall_trend"] = "improving"
        
        return regression_results
    
    def _validate_medical_grade_compliance(self, test_results: Dict[str, Any]) -> bool:
        """Validate medical-grade performance compliance."""
        self.logger.info("Validating medical-grade performance compliance")
        
        compliance_checks = {
            "all_benchmarks_met": True,
            "no_regressions": True,
            "memory_leak_free": True,
            "load_test_passed": True
        }
        
        # Check benchmark compliance
        for result in test_results["benchmark_results"]:
            if not result.within_tolerance:
                compliance_checks["all_benchmarks_met"] = False
        
        # Check for regressions
        if test_results["regression_analysis"]["regressions_detected"]:
            compliance_checks["no_regressions"] = False
        
        # Check memory leak test
        if test_results["memory_leak_test"].get("leak_detected", False):
            compliance_checks["memory_leak_free"] = False
        
        # Check load test results
        for scenario_result in test_results["load_test_results"].values():
            if scenario_result["success_rate"] < 99:  # 99% success rate required
                compliance_checks["load_test_passed"] = False
        
        # Overall compliance
        overall_compliance = all(compliance_checks.values())
        
        if overall_compliance:
            self.logger.info("✅ Medical-grade performance compliance achieved")
        else:
            self.logger.error(f"❌ Medical-grade compliance failed: {compliance_checks}")
        
        return overall_compliance
    
    async def _generate_performance_report(self, results: Dict[str, Any]):
        """Generate comprehensive performance test report."""
        report_path = Path(f"reports/performance_{self.application}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert PerformanceResult objects to dictionaries
        if "benchmark_results" in results:
            serializable_benchmarks = []
            for result in results["benchmark_results"]:
                if hasattr(result, '__dict__'):
                    serializable_benchmarks.append(asdict(result))
                else:
                    serializable_benchmarks.append(result)
            results["benchmark_results"] = serializable_benchmarks
        
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.logger.info(f"Performance test report saved: {report_path}")


class PerformanceRegressionDetector:
    """Detect and analyze performance regressions."""
    
    def __init__(self, application: str):
        self.application = application
        self.regression_threshold = 0.05  # 5% regression threshold
    
    def detect_regressions(self, current_metrics: Dict[str, float], baseline_metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """Detect performance regressions by comparing current metrics to baseline."""
        regressions = []
        
        for metric_name, current_value in current_metrics.items():
            if metric_name in baseline_metrics:
                baseline_value = baseline_metrics[metric_name]
                
                # Calculate regression percentage
                regression_percent = (current_value - baseline_value) / baseline_value
                
                if regression_percent > self.regression_threshold:
                    severity = "critical" if regression_percent > 0.2 else "warning"
                    
                    regressions.append({
                        "metric": metric_name,
                        "baseline_value": baseline_value,
                        "current_value": current_value,
                        "regression_percent": regression_percent * 100,
                        "severity": severity,
                        "recommendation": self._get_regression_recommendation(metric_name, regression_percent)
                    })
        
        return regressions
    
    def _get_regression_recommendation(self, metric_name: str, regression_percent: float) -> str:
        """Get recommendation for addressing performance regression."""
        if "memory" in metric_name.lower():
            return "Investigate memory leaks or inefficient data structures"
        elif "latency" in metric_name.lower() or "time" in metric_name.lower():
            return "Profile code to identify performance bottlenecks"
        elif "throughput" in metric_name.lower():
            return "Analyze concurrent processing and resource utilization"
        else:
            return f"Investigate root cause of {regression_percent:.1f}% performance degradation"


if __name__ == "__main__":
    async def main():
        # Test all applications
        applications = ["cognitron-core", "cognitron-temporal", "cognitron-platform"]
        
        for app in applications:
            print(f"\n🚀 Running performance tests for {app}")
            print("=" * 60)
            
            tester = MedicalGradePerformanceTester(app)
            results = await tester.run_comprehensive_performance_suite()
            
            print(f"Medical-Grade Compliance: {'✅' if results['medical_grade_compliance'] else '❌'}")
            print(f"Test Duration: {results['total_duration']:.2f}s")
            print(f"Benchmarks Tested: {len(results['benchmark_results'])}")
            
            if results['medical_grade_compliance']:
                print("🏥 Medical-grade performance standards met")
            else:
                print("⚠️  Performance issues detected - review required")
    
    # Run performance test suite
    asyncio.run(main())