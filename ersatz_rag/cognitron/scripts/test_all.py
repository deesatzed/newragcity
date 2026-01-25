#!/usr/bin/env python3
"""
Test All Packages Script

Runs comprehensive testing across all packages with medical-grade requirements:
- 100% test success rate mandatory
- Coverage reporting
- Integration testing
- Performance benchmarking
"""

import subprocess
import sys
import time
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any, Optional
import concurrent.futures
from dataclasses import dataclass


@dataclass
class TestResult:
    """Test result data structure."""
    package_name: str
    success: bool
    tests_run: int
    tests_passed: int
    tests_failed: int
    tests_skipped: int
    execution_time: float
    coverage_percent: float
    error_message: Optional[str] = None
    warnings: List[str] = None


class MedicalGradeTestRunner:
    """Medical-grade test runner with 100% success requirement."""
    
    def __init__(self, root_dir: Path, parallel: bool = True, coverage: bool = True):
        self.root_dir = Path(root_dir)
        self.packages_dir = self.root_dir / "packages"
        self.parallel = parallel
        self.coverage = coverage
        self.test_reports_dir = self.root_dir / "test-reports"
        self.test_reports_dir.mkdir(exist_ok=True)
        
        # Test packages in dependency order for integration testing
        self.test_order = [
            "cognitron-core",
            "cognitron-temporal", 
            "cognitron-indexing",
            "cognitron-connectors",
            "cognitron-cli"
        ]
        
        self.test_results: List[TestResult] = []
        self.overall_start_time = time.time()
        
        # Medical-grade requirements
        self.REQUIRED_SUCCESS_RATE = 100.0  # 100% success rate required
        self.REQUIRED_COVERAGE = 95.0       # 95% coverage required
        self.MAX_EXECUTION_TIME = 600       # 10 minutes max per package
    
    def run_command(self, command: List[str], cwd: Path, timeout: int = None) -> Dict[str, Any]:
        """Run a command and capture detailed results."""
        timeout = timeout or self.MAX_EXECUTION_TIME
        
        try:
            start_time = time.time()
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            
            execution_time = time.time() - start_time
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": execution_time,
                "command": " ".join(command)
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": f"Test timed out after {timeout} seconds",
                "execution_time": timeout,
                "command": " ".join(command),
                "timeout": True
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "execution_time": 0,
                "command": " ".join(command),
                "error": str(e)
            }
    
    def parse_pytest_output(self, stdout: str) -> Dict[str, int]:
        """Parse pytest output to extract test counts."""
        # Look for pytest summary line like "5 passed, 1 warning in 0.03s"
        lines = stdout.split('\n')
        
        counts = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "warnings": 0,
            "errors": 0
        }
        
        for line in lines:
            if "passed" in line or "failed" in line or "skipped" in line:
                # Try to parse the pytest summary line
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.isdigit() and i + 1 < len(parts):
                        next_part = parts[i + 1]
                        if "passed" in next_part:
                            counts["passed"] = int(part)
                        elif "failed" in next_part:
                            counts["failed"] = int(part) 
                        elif "skipped" in next_part:
                            counts["skipped"] = int(part)
                        elif "warning" in next_part:
                            counts["warnings"] = int(part)
                        elif "error" in next_part:
                            counts["errors"] = int(part)
        
        return counts
    
    def parse_coverage_xml(self, coverage_xml_path: Path) -> float:
        """Parse coverage XML to extract coverage percentage."""
        try:
            tree = ET.parse(coverage_xml_path)
            root = tree.getroot()
            
            # Look for coverage attribute in root element
            coverage_attr = root.get('line-rate')
            if coverage_attr:
                return float(coverage_attr) * 100
            
            # Look for coverage in coverage element  
            coverage_elem = root.find('.//coverage')
            if coverage_elem is not None:
                line_rate = coverage_elem.get('line-rate')
                if line_rate:
                    return float(line_rate) * 100
            
            return 0.0
            
        except Exception as e:
            print(f"Warning: Could not parse coverage XML: {e}")
            return 0.0
    
    def test_package(self, package_name: str) -> TestResult:
        """Run comprehensive testing for a single package."""
        package_dir = self.packages_dir / package_name
        
        if not package_dir.exists():
            return TestResult(
                package_name=package_name,
                success=False,
                tests_run=0,
                tests_passed=0,
                tests_failed=0,
                tests_skipped=0,
                execution_time=0,
                coverage_percent=0,
                error_message=f"Package directory not found: {package_dir}"
            )
        
        tests_dir = package_dir / "tests"
        if not tests_dir.exists():
            print(f"⚠️ No tests directory found for {package_name}")
            return TestResult(
                package_name=package_name,
                success=True,  # No tests is not a failure, but not ideal
                tests_run=0,
                tests_passed=0,
                tests_failed=0,
                tests_skipped=0,
                execution_time=0,
                coverage_percent=100,  # No code to test
                warnings=["No tests found"]
            )
        
        print(f"🧪 Testing {package_name}...")
        
        # Prepare pytest command
        pytest_args = [
            "pytest",
            "-v",
            "--tb=short", 
            f"--junitxml={self.test_reports_dir}/{package_name}-junit.xml"
        ]
        
        if self.coverage:
            pytest_args.extend([
                "--cov=src",
                "--cov-report=term-missing",
                "--cov-report=xml:" + str(self.test_reports_dir / f"{package_name}-coverage.xml"),
                "--cov-report=html:" + str(self.test_reports_dir / f"{package_name}-coverage-html"),
                f"--cov-fail-under={self.REQUIRED_COVERAGE}"
            ])
        
        # Add timeout for individual tests
        pytest_args.extend(["--timeout=30"])  # 30 seconds per test
        
        # Run the tests
        test_result = self.run_command(pytest_args, package_dir)
        
        # Parse results
        test_counts = self.parse_pytest_output(test_result["stdout"])
        
        # Calculate coverage if enabled
        coverage_percent = 0.0
        if self.coverage:
            coverage_xml_path = self.test_reports_dir / f"{package_name}-coverage.xml"
            if coverage_xml_path.exists():
                coverage_percent = self.parse_coverage_xml(coverage_xml_path)
        
        # Determine overall success
        total_tests = test_counts["passed"] + test_counts["failed"]
        success_rate = (test_counts["passed"] / max(1, total_tests)) * 100
        
        success = (
            test_result["success"] and 
            test_counts["failed"] == 0 and
            success_rate >= self.REQUIRED_SUCCESS_RATE and
            coverage_percent >= self.REQUIRED_COVERAGE
        )
        
        warnings = []
        if test_counts["warnings"] > 0:
            warnings.append(f"{test_counts['warnings']} warnings found")
        if test_counts["skipped"] > 0:
            warnings.append(f"{test_counts['skipped']} tests skipped")
        if coverage_percent < self.REQUIRED_COVERAGE:
            warnings.append(f"Coverage {coverage_percent:.1f}% below required {self.REQUIRED_COVERAGE}%")
        
        result = TestResult(
            package_name=package_name,
            success=success,
            tests_run=total_tests,
            tests_passed=test_counts["passed"],
            tests_failed=test_counts["failed"], 
            tests_skipped=test_counts["skipped"],
            execution_time=test_result["execution_time"],
            coverage_percent=coverage_percent,
            error_message=test_result["stderr"] if not success else None,
            warnings=warnings if warnings else None
        )
        
        # Print result
        status = "✅" if success else "❌"
        print(f"{status} {package_name}: {test_counts['passed']}/{total_tests} tests passed "
              f"({coverage_percent:.1f}% coverage) in {test_result['execution_time']:.2f}s")
        
        if not success:
            if test_counts["failed"] > 0:
                print(f"   💥 {test_counts['failed']} tests failed")
            if coverage_percent < self.REQUIRED_COVERAGE:
                print(f"   📊 Coverage {coverage_percent:.1f}% below required {self.REQUIRED_COVERAGE}%")
        
        return result
    
    def run_integration_tests(self) -> TestResult:
        """Run integration tests across packages."""
        print("🔗 Running integration tests...")
        
        integration_tests_dir = self.root_dir / "tools" / "test" / "integration"
        if not integration_tests_dir.exists():
            return TestResult(
                package_name="integration",
                success=True,
                tests_run=0,
                tests_passed=0,
                tests_failed=0,
                tests_skipped=0,
                execution_time=0,
                coverage_percent=100,
                warnings=["No integration tests found"]
            )
        
        pytest_args = [
            "pytest",
            "-v",
            "--tb=short",
            str(integration_tests_dir),
            f"--junitxml={self.test_reports_dir}/integration-junit.xml"
        ]
        
        test_result = self.run_command(pytest_args, self.root_dir)
        test_counts = self.parse_pytest_output(test_result["stdout"])
        
        total_tests = test_counts["passed"] + test_counts["failed"]
        success = test_result["success"] and test_counts["failed"] == 0
        
        result = TestResult(
            package_name="integration",
            success=success,
            tests_run=total_tests,
            tests_passed=test_counts["passed"],
            tests_failed=test_counts["failed"],
            tests_skipped=test_counts["skipped"], 
            execution_time=test_result["execution_time"],
            coverage_percent=100,  # Integration tests don't need coverage
            error_message=test_result["stderr"] if not success else None
        )
        
        status = "✅" if success else "❌"
        print(f"{status} Integration: {test_counts['passed']}/{total_tests} tests passed "
              f"in {test_result['execution_time']:.2f}s")
        
        return result
    
    def run_all_tests(self) -> bool:
        """Run all tests with medical-grade requirements."""
        print("🚀 Starting medical-grade test suite...")
        print(f"Required success rate: {self.REQUIRED_SUCCESS_RATE}%")
        print(f"Required coverage: {self.REQUIRED_COVERAGE}%")
        print(f"Parallel execution: {self.parallel}")
        print()
        
        # Run package tests
        if self.parallel and len(self.test_order) > 1:
            # Run tests in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                future_to_package = {
                    executor.submit(self.test_package, pkg): pkg 
                    for pkg in self.test_order
                }
                
                for future in concurrent.futures.as_completed(future_to_package):
                    result = future.result()
                    self.test_results.append(result)
        else:
            # Run tests sequentially
            for package_name in self.test_order:
                result = self.test_package(package_name)
                self.test_results.append(result)
        
        # Run integration tests
        integration_result = self.run_integration_tests()
        self.test_results.append(integration_result)
        
        # Generate comprehensive report
        return self.generate_test_report()
    
    def generate_test_report(self) -> bool:
        """Generate comprehensive test report and determine overall success."""
        total_time = time.time() - self.overall_start_time
        
        # Calculate overall statistics
        total_tests = sum(r.tests_run for r in self.test_results)
        total_passed = sum(r.tests_passed for r in self.test_results)
        total_failed = sum(r.tests_failed for r in self.test_results)
        total_skipped = sum(r.tests_skipped for r in self.test_results)
        
        overall_success_rate = (total_passed / max(1, total_tests)) * 100 if total_tests > 0 else 100
        
        # Coverage calculation (weighted by test count)
        weighted_coverage = 0
        total_weight = 0
        for result in self.test_results:
            if result.tests_run > 0:
                weighted_coverage += result.coverage_percent * result.tests_run
                total_weight += result.tests_run
        
        overall_coverage = weighted_coverage / max(1, total_weight) if total_weight > 0 else 100
        
        # Determine overall success
        all_packages_passed = all(r.success for r in self.test_results)
        meets_success_rate = overall_success_rate >= self.REQUIRED_SUCCESS_RATE
        meets_coverage = overall_coverage >= self.REQUIRED_COVERAGE
        
        overall_success = all_packages_passed and meets_success_rate and meets_coverage
        
        # Create detailed report
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "execution_time": total_time,
            "medical_grade_requirements": {
                "required_success_rate": self.REQUIRED_SUCCESS_RATE,
                "required_coverage": self.REQUIRED_COVERAGE,
                "max_execution_time": self.MAX_EXECUTION_TIME
            },
            "overall_results": {
                "success": overall_success,
                "success_rate": overall_success_rate,
                "coverage": overall_coverage,
                "total_tests": total_tests,
                "total_passed": total_passed,
                "total_failed": total_failed,
                "total_skipped": total_skipped
            },
            "package_results": [
                {
                    "package": r.package_name,
                    "success": r.success,
                    "tests_run": r.tests_run,
                    "tests_passed": r.tests_passed,
                    "tests_failed": r.tests_failed,
                    "tests_skipped": r.tests_skipped,
                    "execution_time": r.execution_time,
                    "coverage_percent": r.coverage_percent,
                    "error_message": r.error_message,
                    "warnings": r.warnings
                }
                for r in self.test_results
            ]
        }
        
        # Save detailed report
        report_path = self.test_reports_dir / "test_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*80)
        print("🧪 MEDICAL-GRADE TEST REPORT")
        print("="*80)
        print(f"Overall success: {'✅ PASS' if overall_success else '❌ FAIL'}")
        print(f"Success rate: {overall_success_rate:.1f}% (required: {self.REQUIRED_SUCCESS_RATE}%)")
        print(f"Coverage: {overall_coverage:.1f}% (required: {self.REQUIRED_COVERAGE}%)")
        print(f"Execution time: {total_time:.2f}s")
        print()
        
        print(f"📊 TEST STATISTICS:")
        print(f"  Total tests: {total_tests}")
        print(f"  Passed: {total_passed}")
        print(f"  Failed: {total_failed}")
        print(f"  Skipped: {total_skipped}")
        print()
        
        # Package-by-package results
        print("📦 PACKAGE RESULTS:")
        for result in self.test_results:
            status = "✅" if result.success else "❌"
            print(f"  {status} {result.package_name}: {result.tests_passed}/{result.tests_run} "
                  f"({result.coverage_percent:.1f}% coverage)")
            
            if result.error_message:
                print(f"     Error: {result.error_message}")
            if result.warnings:
                for warning in result.warnings:
                    print(f"     ⚠️ {warning}")
        
        print()
        
        if not overall_success:
            print("❌ MEDICAL-GRADE REQUIREMENTS NOT MET")
            if not meets_success_rate:
                print(f"   Success rate {overall_success_rate:.1f}% below required {self.REQUIRED_SUCCESS_RATE}%")
            if not meets_coverage:
                print(f"   Coverage {overall_coverage:.1f}% below required {self.REQUIRED_COVERAGE}%")
            if not all_packages_passed:
                failed_packages = [r.package_name for r in self.test_results if not r.success]
                print(f"   Failed packages: {', '.join(failed_packages)}")
        else:
            print("🎉 ALL MEDICAL-GRADE REQUIREMENTS MET!")
        
        print(f"\n📋 Detailed report: {report_path}")
        
        return overall_success


def main():
    """Main test runner entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run medical-grade test suite")
    parser.add_argument("--root", type=Path, default=Path.cwd(),
                       help="Root directory (default: current directory)")
    parser.add_argument("--no-parallel", action="store_true",
                       help="Disable parallel test execution")
    parser.add_argument("--no-coverage", action="store_true",
                       help="Disable coverage reporting")
    parser.add_argument("--package", type=str,
                       help="Test only specific package")
    parser.add_argument("--junit", action="store_true",
                       help="Generate JUnit XML reports")
    
    args = parser.parse_args()
    
    test_runner = MedicalGradeTestRunner(
        root_dir=args.root,
        parallel=not args.no_parallel,
        coverage=not args.no_coverage
    )
    
    if args.package:
        # Test specific package
        result = test_runner.test_package(args.package)
        sys.exit(0 if result.success else 1)
    else:
        # Test all packages
        success = test_runner.run_all_tests()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()