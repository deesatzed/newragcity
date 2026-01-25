#!/usr/bin/env python3
"""
Lint All Packages Script

Comprehensive linting across all packages with configurable rules and reporting.
"""

import subprocess
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass 
class LintResult:
    """Lint result for a package or file."""
    target: str
    success: bool
    issues_count: int
    errors_count: int
    warnings_count: int
    execution_time: float
    issues: List[Dict[str, Any]] = None


class ComprehensiveLinter:
    """Comprehensive linting system."""
    
    def __init__(self, root_dir: Path, fix_issues: bool = False, check_only: bool = False):
        self.root_dir = Path(root_dir)
        self.packages_dir = self.root_dir / "packages"
        self.fix_issues = fix_issues
        self.check_only = check_only
        
        self.packages = [
            "cognitron-core",
            "cognitron-temporal",
            "cognitron-indexing", 
            "cognitron-connectors",
            "cognitron-cli"
        ]
        
        self.lint_results: List[LintResult] = []
    
    def run_command(self, command: List[str], cwd: Path = None) -> Dict[str, Any]:
        """Run command and capture results."""
        try:
            start_time = time.time()
            result = subprocess.run(
                command,
                cwd=cwd or self.root_dir,
                capture_output=True,
                text=True,
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
            
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "execution_time": 0,
                "command": " ".join(command)
            }
    
    def lint_package_with_ruff(self, package_name: str) -> LintResult:
        """Lint a package with ruff."""
        package_dir = self.packages_dir / package_name
        src_dir = package_dir / "src"
        
        if not src_dir.exists():
            return LintResult(
                target=package_name,
                success=True,
                issues_count=0,
                errors_count=0,
                warnings_count=0,
                execution_time=0,
                issues=[]
            )
        
        print(f"🔍 Linting {package_name} with ruff...")
        
        # Build ruff command
        ruff_cmd = ["ruff", "check", str(src_dir)]
        
        if self.fix_issues:
            ruff_cmd.append("--fix")
        
        # Add output format for parsing
        ruff_cmd.extend(["--output-format", "json"])
        
        # Run ruff
        result = self.run_command(ruff_cmd, package_dir)
        
        # Parse results
        issues = []
        errors_count = 0
        warnings_count = 0
        
        if result["stdout"]:
            try:
                # Ruff outputs one JSON object per line
                lines = result["stdout"].strip().split('\n')
                for line in lines:
                    if line.strip():
                        issue = json.loads(line)
                        issues.append(issue)
                        
                        # Categorize issue severity
                        if issue.get("level") == "error":
                            errors_count += 1
                        else:
                            warnings_count += 1
                            
            except json.JSONDecodeError as e:
                print(f"Warning: Could not parse ruff output for {package_name}: {e}")
        
        success = result["returncode"] == 0 or (self.fix_issues and result["returncode"] == 1)
        
        lint_result = LintResult(
            target=package_name,
            success=success,
            issues_count=len(issues),
            errors_count=errors_count,
            warnings_count=warnings_count,
            execution_time=result["execution_time"],
            issues=issues
        )
        
        # Print summary
        if success and lint_result.issues_count == 0:
            print(f"✅ {package_name}: Clean ({result['execution_time']:.2f}s)")
        elif success and self.fix_issues:
            print(f"🔧 {package_name}: {lint_result.issues_count} issues fixed ({result['execution_time']:.2f}s)")
        else:
            print(f"❌ {package_name}: {lint_result.issues_count} issues found ({result['execution_time']:.2f}s)")
        
        return lint_result
    
    def format_package_with_ruff(self, package_name: str) -> LintResult:
        """Format a package with ruff."""
        package_dir = self.packages_dir / package_name
        src_dir = package_dir / "src"
        
        if not src_dir.exists():
            return LintResult(
                target=f"{package_name} (format)",
                success=True,
                issues_count=0,
                errors_count=0,
                warnings_count=0,
                execution_time=0
            )
        
        if self.check_only:
            print(f"📝 Checking format for {package_name}...")
            ruff_cmd = ["ruff", "format", "--check", str(src_dir)]
        else:
            print(f"📝 Formatting {package_name}...")
            ruff_cmd = ["ruff", "format", str(src_dir)]
        
        result = self.run_command(ruff_cmd, package_dir)
        
        # For format checking, non-zero exit means files need formatting
        if self.check_only:
            success = result["returncode"] == 0
            issues_count = 1 if not success else 0
        else:
            success = result["returncode"] == 0
            issues_count = 0  # Formatting always succeeds if no syntax errors
        
        format_result = LintResult(
            target=f"{package_name} (format)",
            success=success,
            issues_count=issues_count,
            errors_count=issues_count if not success else 0,
            warnings_count=0,
            execution_time=result["execution_time"]
        )
        
        if success:
            if self.check_only:
                print(f"✅ {package_name}: Format OK ({result['execution_time']:.2f}s)")
            else:
                print(f"✅ {package_name}: Formatted ({result['execution_time']:.2f}s)")
        else:
            if self.check_only:
                print(f"❌ {package_name}: Needs formatting ({result['execution_time']:.2f}s)")
            else:
                print(f"❌ {package_name}: Format failed ({result['execution_time']:.2f}s)")
        
        return format_result
    
    def lint_all_packages(self) -> bool:
        """Lint all packages."""
        print("🔍 Starting comprehensive linting...")
        print(f"Fix issues: {self.fix_issues}")
        print(f"Check only: {self.check_only}")
        print(f"Packages: {', '.join(self.packages)}")
        print()
        
        # Run linting for each package
        for package_name in self.packages:
            # Lint with ruff
            lint_result = self.lint_package_with_ruff(package_name)
            self.lint_results.append(lint_result)
            
            # Format with ruff
            format_result = self.format_package_with_ruff(package_name)
            self.lint_results.append(format_result)
        
        # Generate comprehensive report
        return self.generate_lint_report()
    
    def generate_lint_report(self) -> bool:
        """Generate comprehensive lint report."""
        total_issues = sum(r.issues_count for r in self.lint_results)
        total_errors = sum(r.errors_count for r in self.lint_results)
        total_warnings = sum(r.warnings_count for r in self.lint_results)
        
        successful_lints = len([r for r in self.lint_results if r.success])
        total_lints = len(self.lint_results)
        
        overall_success = total_errors == 0 and successful_lints == total_lints
        
        # Create detailed report
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "configuration": {
                "fix_issues": self.fix_issues,
                "check_only": self.check_only
            },
            "summary": {
                "overall_success": overall_success,
                "total_issues": total_issues,
                "total_errors": total_errors,
                "total_warnings": total_warnings,
                "successful_lints": successful_lints,
                "total_lints": total_lints
            },
            "results": [
                {
                    "target": r.target,
                    "success": r.success,
                    "issues_count": r.issues_count,
                    "errors_count": r.errors_count,
                    "warnings_count": r.warnings_count,
                    "execution_time": r.execution_time,
                    "issues": r.issues if r.issues else []
                }
                for r in self.lint_results
            ]
        }
        
        # Save report
        report_path = self.root_dir / "lint_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print()
        print("=" * 60)
        print("🔍 LINTING REPORT")
        print("=" * 60)
        
        status = "✅ PASS" if overall_success else "❌ FAIL"
        print(f"Overall result: {status}")
        print(f"Total issues: {total_issues}")
        print(f"Errors: {total_errors}")
        print(f"Warnings: {total_warnings}")
        print(f"Successful lints: {successful_lints}/{total_lints}")
        print()
        
        # Detailed results
        print("📋 DETAILED RESULTS:")
        for result in self.lint_results:
            status_icon = "✅" if result.success else "❌" 
            print(f"  {status_icon} {result.target}: {result.issues_count} issues "
                  f"({result.execution_time:.2f}s)")
            
            if result.issues and len(result.issues) <= 5:
                # Show first few issues
                for issue in result.issues[:5]:
                    filename = issue.get("filename", "unknown")
                    line = issue.get("line", "?")
                    code = issue.get("code", "?")
                    message = issue.get("message", "No message")
                    print(f"      {filename}:{line} {code}: {message}")
            elif result.issues and len(result.issues) > 5:
                print(f"      ... showing first 5 of {len(result.issues)} issues")
                for issue in result.issues[:5]:
                    filename = issue.get("filename", "unknown")
                    line = issue.get("line", "?")
                    code = issue.get("code", "?")
                    message = issue.get("message", "No message")
                    print(f"      {filename}:{line} {code}: {message}")
        
        print()
        
        if not overall_success:
            print("❌ LINTING ISSUES FOUND")
            if total_errors > 0:
                print(f"   {total_errors} errors must be fixed")
            if total_warnings > 0:
                print(f"   {total_warnings} warnings should be addressed")
            
            if not self.fix_issues:
                print("\n💡 Run with --fix to automatically fix issues")
        else:
            print("🎉 ALL LINTING CHECKS PASSED!")
        
        print(f"\n📋 Detailed report: {report_path}")
        
        return overall_success


def main():
    """Main linting entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive linting for Cognitron")
    parser.add_argument("--root", type=Path, default=Path.cwd(),
                       help="Root directory (default: current directory)")
    parser.add_argument("--fix", action="store_true",
                       help="Automatically fix issues where possible")
    parser.add_argument("--check", action="store_true",
                       help="Check only, don't modify files")
    parser.add_argument("--package", type=str,
                       help="Lint specific package only")
    
    args = parser.parse_args()
    
    linter = ComprehensiveLinter(
        root_dir=args.root,
        fix_issues=args.fix,
        check_only=args.check
    )
    
    if args.package:
        # Lint specific package
        if args.package not in linter.packages:
            print(f"Unknown package: {args.package}")
            print(f"Available packages: {', '.join(linter.packages)}")
            sys.exit(1)
        
        linter.packages = [args.package]
    
    success = linter.lint_all_packages()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()