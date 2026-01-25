#!/usr/bin/env python3
"""
Format All Packages Script

Comprehensive code formatting across all packages using ruff.
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class FormatResult:
    """Format result for a package."""
    package: str
    success: bool
    files_formatted: int
    execution_time: float
    error_message: str = None


class CodeFormatter:
    """Comprehensive code formatting system."""
    
    def __init__(self, root_dir: Path, check_only: bool = False):
        self.root_dir = Path(root_dir)
        self.packages_dir = self.root_dir / "packages"
        self.check_only = check_only
        
        self.packages = [
            "cognitron-core",
            "cognitron-temporal",
            "cognitron-indexing",
            "cognitron-connectors", 
            "cognitron-cli"
        ]
        
        self.format_results: List[FormatResult] = []
    
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
    
    def format_package(self, package_name: str) -> FormatResult:
        """Format a single package."""
        package_dir = self.packages_dir / package_name
        src_dir = package_dir / "src"
        tests_dir = package_dir / "tests"
        
        if not src_dir.exists():
            return FormatResult(
                package=package_name,
                success=True,
                files_formatted=0,
                execution_time=0,
                error_message="No src directory found"
            )
        
        # Collect directories to format
        format_dirs = [str(src_dir)]
        if tests_dir.exists():
            format_dirs.append(str(tests_dir))
        
        if self.check_only:
            print(f"📝 Checking format for {package_name}...")
            ruff_cmd = ["ruff", "format", "--check"] + format_dirs
        else:
            print(f"📝 Formatting {package_name}...")
            ruff_cmd = ["ruff", "format"] + format_dirs
        
        # Run ruff format
        result = self.run_command(ruff_cmd, package_dir)
        
        # Count files that would be/were formatted
        files_formatted = 0
        if result["stdout"]:
            # Count lines that mention files (ruff format output)
            lines = result["stdout"].split('\n')
            files_formatted = len([l for l in lines if l.strip() and not l.startswith('would')])
        
        # In check mode, returncode 1 means files need formatting
        if self.check_only:
            success = result["returncode"] == 0
            if not success:
                files_formatted = result["stdout"].count("would reformat")
        else:
            success = result["returncode"] == 0
        
        format_result = FormatResult(
            package=package_name,
            success=success,
            files_formatted=files_formatted,
            execution_time=result["execution_time"],
            error_message=result["stderr"] if not success else None
        )
        
        # Print result
        if success:
            if self.check_only:
                print(f"✅ {package_name}: Format OK ({result['execution_time']:.2f}s)")
            else:
                if files_formatted > 0:
                    print(f"✅ {package_name}: {files_formatted} files formatted ({result['execution_time']:.2f}s)")
                else:
                    print(f"✅ {package_name}: Already formatted ({result['execution_time']:.2f}s)")
        else:
            if self.check_only:
                print(f"❌ {package_name}: {files_formatted} files need formatting ({result['execution_time']:.2f}s)")
            else:
                print(f"❌ {package_name}: Format failed ({result['execution_time']:.2f}s)")
                if result["stderr"]:
                    print(f"   Error: {result['stderr']}")
        
        return format_result
    
    def format_additional_files(self) -> FormatResult:
        """Format additional Python files in the root."""
        print("📝 Formatting additional files...")
        
        # Find Python files in scripts and root
        additional_files = []
        
        # Scripts directory
        scripts_dir = self.root_dir / "scripts"
        if scripts_dir.exists():
            additional_files.extend(scripts_dir.glob("*.py"))
        
        # Root Python files
        for py_file in self.root_dir.glob("*.py"):
            additional_files.append(py_file)
        
        if not additional_files:
            return FormatResult(
                package="additional_files",
                success=True,
                files_formatted=0,
                execution_time=0
            )
        
        file_paths = [str(f) for f in additional_files]
        
        if self.check_only:
            ruff_cmd = ["ruff", "format", "--check"] + file_paths
        else:
            ruff_cmd = ["ruff", "format"] + file_paths
        
        result = self.run_command(ruff_cmd)
        
        # Count formatted files
        files_formatted = len(additional_files) if result["success"] and not self.check_only else 0
        if self.check_only and not result["success"]:
            files_formatted = result["stdout"].count("would reformat")
        
        success = result["returncode"] == 0 if not self.check_only else result["returncode"] == 0
        
        format_result = FormatResult(
            package="additional_files",
            success=success,
            files_formatted=files_formatted,
            execution_time=result["execution_time"],
            error_message=result["stderr"] if not success else None
        )
        
        if success:
            if self.check_only:
                print(f"✅ Additional files: Format OK ({result['execution_time']:.2f}s)")
            else:
                print(f"✅ Additional files: {len(additional_files)} files processed ({result['execution_time']:.2f}s)")
        else:
            if self.check_only:
                print(f"❌ Additional files: {files_formatted} files need formatting ({result['execution_time']:.2f}s)")
            else:
                print(f"❌ Additional files: Format failed ({result['execution_time']:.2f}s)")
        
        return format_result
    
    def format_all(self) -> bool:
        """Format all packages and additional files."""
        print("📝 Starting code formatting...")
        print(f"Mode: {'Check only' if self.check_only else 'Format'}")
        print(f"Packages: {', '.join(self.packages)}")
        print()
        
        # Format each package
        for package_name in self.packages:
            result = self.format_package(package_name)
            self.format_results.append(result)
        
        # Format additional files
        additional_result = self.format_additional_files()
        self.format_results.append(additional_result)
        
        # Generate report
        return self.generate_format_report()
    
    def generate_format_report(self) -> bool:
        """Generate formatting report."""
        total_files = sum(r.files_formatted for r in self.format_results)
        successful_formats = len([r for r in self.format_results if r.success])
        total_formats = len(self.format_results)
        total_time = sum(r.execution_time for r in self.format_results)
        
        overall_success = successful_formats == total_formats
        
        # Print summary
        print()
        print("=" * 60)
        print("📝 FORMATTING REPORT")
        print("=" * 60)
        
        status = "✅ PASS" if overall_success else "❌ FAIL"
        print(f"Overall result: {status}")
        
        if self.check_only:
            needs_formatting = sum(r.files_formatted for r in self.format_results if not r.success)
            print(f"Files needing format: {needs_formatting}")
        else:
            print(f"Files formatted: {total_files}")
        
        print(f"Successful operations: {successful_formats}/{total_formats}")
        print(f"Total execution time: {total_time:.2f}s")
        print()
        
        # Detailed results
        print("📋 DETAILED RESULTS:")
        for result in self.format_results:
            status_icon = "✅" if result.success else "❌"
            
            if self.check_only:
                if result.success:
                    print(f"  {status_icon} {result.package}: Format OK ({result.execution_time:.2f}s)")
                else:
                    print(f"  {status_icon} {result.package}: {result.files_formatted} files need formatting ({result.execution_time:.2f}s)")
            else:
                if result.files_formatted > 0:
                    print(f"  {status_icon} {result.package}: {result.files_formatted} files formatted ({result.execution_time:.2f}s)")
                else:
                    print(f"  {status_icon} {result.package}: No changes needed ({result.execution_time:.2f}s)")
            
            if result.error_message:
                print(f"      Error: {result.error_message}")
        
        print()
        
        if not overall_success:
            print("❌ FORMATTING ISSUES FOUND")
            failed_packages = [r.package for r in self.format_results if not r.success]
            print(f"   Failed packages: {', '.join(failed_packages)}")
            
            if self.check_only:
                print("\n💡 Run without --check to format the files")
        else:
            if self.check_only:
                print("🎉 ALL FILES PROPERLY FORMATTED!")
            else:
                print("🎉 FORMATTING COMPLETED SUCCESSFULLY!")
        
        return overall_success


def main():
    """Main formatting entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Format all Cognitron packages")
    parser.add_argument("--root", type=Path, default=Path.cwd(),
                       help="Root directory (default: current directory)")
    parser.add_argument("--check", action="store_true",
                       help="Check formatting without making changes")
    parser.add_argument("--package", type=str,
                       help="Format specific package only")
    
    args = parser.parse_args()
    
    formatter = CodeFormatter(
        root_dir=args.root,
        check_only=args.check
    )
    
    if args.package:
        # Format specific package
        if args.package not in formatter.packages:
            print(f"Unknown package: {args.package}")
            print(f"Available packages: {', '.join(formatter.packages)}")
            sys.exit(1)
        
        formatter.packages = [args.package]
    
    success = formatter.format_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()