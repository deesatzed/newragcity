#!/usr/bin/env python3
"""
Pre-commit Medical-Grade Validation Hook

Lightweight validation that runs before commits to ensure medical-grade quality.
Focuses on fast checks that prevent obviously broken code from being committed.
"""

import subprocess
import sys
import time
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Set


class PreCommitMedicalValidator:
    """Fast pre-commit validation for medical-grade quality."""
    
    def __init__(self, root_dir: Path):
        self.root_dir = Path(root_dir)
        self.staged_files = self.get_staged_files()
        self.python_files = self.filter_python_files(self.staged_files)
        
        # Quick validation thresholds
        self.MAX_CYCLOMATIC_COMPLEXITY = 10
        self.MAX_FUNCTION_LENGTH = 50
        self.MAX_FILE_LENGTH = 500
        self.REQUIRED_DOCSTRING_COVERAGE = 80.0
        
        self.errors = []
        self.warnings = []
    
    def run_command(self, command: List[str], cwd: Path = None, timeout: int = 30) -> Dict[str, Any]:
        """Run command with short timeout for pre-commit."""
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.root_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": "Command timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e)
            }
    
    def get_staged_files(self) -> List[Path]:
        """Get list of staged files for commit."""
        result = self.run_command(["git", "diff", "--cached", "--name-only"])
        
        if result["success"]:
            files = result["stdout"].strip().split('\n')
            return [Path(f) for f in files if f.strip()]
        
        return []
    
    def filter_python_files(self, files: List[Path]) -> List[Path]:
        """Filter for Python files only."""
        python_files = []
        
        for file_path in files:
            full_path = self.root_dir / file_path
            
            # Check if file exists (might be deleted)
            if not full_path.exists():
                continue
            
            # Check if it's a Python file
            if file_path.suffix == '.py':
                python_files.append(file_path)
            elif full_path.is_file():
                # Check shebang for Python files without .py extension
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        first_line = f.readline()
                        if 'python' in first_line.lower():
                            python_files.append(file_path)
                except (UnicodeDecodeError, IOError):
                    pass
        
        return python_files
    
    def validate_syntax(self) -> bool:
        """Validate Python syntax for all staged files."""
        print("🔍 Checking Python syntax...")
        
        syntax_valid = True
        
        for file_path in self.python_files:
            full_path = self.root_dir / file_path
            
            # Check syntax with python -m py_compile
            result = self.run_command(["python", "-m", "py_compile", str(full_path)])
            
            if not result["success"]:
                syntax_valid = False
                self.errors.append(f"Syntax error in {file_path}: {result['stderr']}")
        
        return syntax_valid
    
    def validate_imports(self) -> bool:
        """Validate that imports are resolvable."""
        print("📦 Checking imports...")
        
        imports_valid = True
        
        for file_path in self.python_files:
            full_path = self.root_dir / file_path
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract import statements
                import_lines = re.findall(r'^(?:from .+ )?import .+$', content, re.MULTILINE)
                
                for import_line in import_lines:
                    # Skip relative imports and standard library
                    if any(skip in import_line for skip in ['.', 'typing', 'pathlib', 'os', 'sys', 'json', 'time']):
                        continue
                    
                    # Try to resolve import (basic check)
                    try:
                        # This is a simplified check - in production you'd use ast parsing
                        module_name = import_line.split()[-1].split('.')[0]
                        
                        # Check if it's a known cognitron module
                        if module_name.startswith('cognitron') and not self.check_internal_import(module_name, file_path):
                            self.warnings.append(f"Potential import issue in {file_path}: {import_line}")
                            
                    except Exception:
                        pass  # Skip complex import analysis in pre-commit
                        
            except (UnicodeDecodeError, IOError) as e:
                self.warnings.append(f"Could not read {file_path}: {e}")
        
        return imports_valid
    
    def check_internal_import(self, module_name: str, file_path: Path) -> bool:
        """Check if internal cognitron import exists."""
        # Simple heuristic check - could be improved with proper module resolution
        parts = module_name.replace('cognitron_', '').split('.')
        
        if len(parts) >= 2:
            package_name = f"cognitron-{parts[0]}"
            package_dir = self.root_dir / "packages" / package_name
            
            return package_dir.exists()
        
        return True  # Assume it's valid for now
    
    def validate_code_quality(self) -> bool:
        """Run quick code quality checks."""
        print("📊 Checking code quality...")
        
        quality_passed = True
        
        # Run ruff on staged files only
        if self.python_files:
            file_paths = [str(self.root_dir / f) for f in self.python_files]
            
            # Run ruff linting
            result = self.run_command(["ruff", "check"] + file_paths)
            
            if not result["success"]:
                quality_passed = False
                self.errors.append("Code quality issues found (run 'ruff check' for details)")
                
                # Parse ruff output for specific issues
                if result["stdout"]:
                    lines = result["stdout"].split('\n')[:10]  # First 10 issues only
                    for line in lines:
                        if line.strip():
                            self.errors.append(f"  {line}")
        
        return quality_passed
    
    def validate_security_basics(self) -> bool:
        """Run basic security checks on staged files."""
        print("🔒 Checking security basics...")
        
        security_passed = True
        security_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password detected"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key detected"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret detected"),
            (r'eval\s*\(', "Use of eval() detected"),
            (r'exec\s*\(', "Use of exec() detected"),
            (r'__import__\s*\(', "Use of __import__() detected"),
            (r'pickle\.loads?\s*\(', "Use of pickle detected (potential security risk)"),
            (r'shell\s*=\s*True', "Shell=True in subprocess detected"),
        ]
        
        for file_path in self.python_files:
            full_path = self.root_dir / file_path
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for pattern, message in security_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        self.warnings.append(f"Security warning in {file_path}:{line_num}: {message}")
                        
            except (UnicodeDecodeError, IOError):
                pass
        
        return security_passed
    
    def validate_test_files(self) -> bool:
        """Check if test files are included for new code."""
        print("🧪 Checking test coverage...")
        
        new_python_files = [f for f in self.python_files if not str(f).startswith('test_')]
        new_source_files = [f for f in new_python_files if '/test' not in str(f) and 'scripts/' not in str(f)]
        
        if new_source_files:
            # Check if corresponding test files exist or are being added
            for source_file in new_source_files:
                # Generate expected test file path
                test_file_name = f"test_{source_file.stem}.py"
                
                # Look for test file in various locations
                possible_test_locations = [
                    source_file.parent / "tests" / test_file_name,
                    source_file.parent.parent / "tests" / test_file_name,
                    self.root_dir / "tools" / "test" / test_file_name
                ]
                
                test_exists = any(loc.exists() for loc in possible_test_locations)
                test_being_added = any(test_file_name in str(f) for f in self.staged_files)
                
                if not test_exists and not test_being_added:
                    self.warnings.append(f"No test file found for {source_file}")
        
        return True  # Don't fail commit, but warn
    
    def validate_docstrings(self) -> bool:
        """Check for basic docstring coverage."""
        print("📝 Checking documentation...")
        
        for file_path in self.python_files:
            full_path = self.root_dir / file_path
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find function and class definitions
                functions = re.findall(r'^\s*def\s+(\w+)\s*\(', content, re.MULTILINE)
                classes = re.findall(r'^\s*class\s+(\w+).*:', content, re.MULTILINE)
                
                # Count docstrings (simple heuristic)
                docstring_count = len(re.findall(r'""".*?"""', content, re.DOTALL))
                docstring_count += len(re.findall(r"'''.*?'''", content, re.DOTALL))
                
                total_definitions = len(functions) + len(classes)
                
                if total_definitions > 0:
                    coverage = (docstring_count / total_definitions) * 100
                    if coverage < self.REQUIRED_DOCSTRING_COVERAGE:
                        self.warnings.append(
                            f"Low docstring coverage in {file_path}: "
                            f"{coverage:.1f}% (required: {self.REQUIRED_DOCSTRING_COVERAGE}%)"
                        )
                        
            except (UnicodeDecodeError, IOError):
                pass
        
        return True  # Don't fail commit for documentation
    
    def run_validation(self) -> bool:
        """Run all pre-commit validations."""
        start_time = time.time()
        
        print("🏥 Pre-commit Medical-Grade Validation")
        print("=" * 50)
        
        if not self.staged_files:
            print("No files staged for commit")
            return True
        
        if not self.python_files:
            print("No Python files staged for commit")
            return True
        
        print(f"Validating {len(self.python_files)} Python files...")
        print()
        
        # Run validation checks
        validations = [
            ("Syntax", self.validate_syntax),
            ("Imports", self.validate_imports),
            ("Code Quality", self.validate_code_quality),
            ("Security", self.validate_security_basics),
            ("Tests", self.validate_test_files),
            ("Documentation", self.validate_docstrings)
        ]
        
        passed_validations = 0
        total_validations = len(validations)
        
        for name, validation_func in validations:
            try:
                success = validation_func()
                if success:
                    passed_validations += 1
                    print(f"✅ {name}")
                else:
                    print(f"❌ {name}")
            except Exception as e:
                print(f"❌ {name} (Exception: {e})")
        
        execution_time = time.time() - start_time
        
        # Print summary
        print()
        print("=" * 50)
        print(f"Validation completed in {execution_time:.2f}s")
        print(f"Passed: {passed_validations}/{total_validations}")
        
        # Show errors and warnings
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
        
        if self.warnings:
            print(f"\n⚠️ WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # Show first 10 warnings
                print(f"  {warning}")
            
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more warnings")
        
        # Determine overall success
        has_critical_errors = len(self.errors) > 0
        
        if has_critical_errors:
            print("\n❌ COMMIT BLOCKED: Critical errors must be fixed")
            print("Fix the errors above and try committing again.")
            return False
        elif self.warnings:
            print("\n⚠️ COMMIT ALLOWED WITH WARNINGS")
            print("Consider addressing the warnings before committing.")
            return True
        else:
            print("\n✅ ALL VALIDATIONS PASSED")
            return True


def main():
    """Main pre-commit validation entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pre-commit medical-grade validation")
    parser.add_argument("--root", type=Path, default=Path.cwd(),
                       help="Root directory (default: current directory)")
    
    args = parser.parse_args()
    
    validator = PreCommitMedicalValidator(args.root)
    success = validator.run_validation()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()