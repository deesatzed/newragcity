#!/usr/bin/env python3
"""
Development Environment Setup Script

Sets up a complete development environment for the Cognitron monorepo including:
- Virtual environment creation
- Package installation in development mode
- Pre-commit hooks setup
- IDE configuration
- Development tools and utilities
"""

import subprocess
import sys
import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional


class DevelopmentEnvironmentSetup:
    """Sets up complete development environment."""
    
    def __init__(self, root_dir: Path, python_version: str = "3.11"):
        self.root_dir = Path(root_dir)
        self.python_version = python_version
        self.venv_dir = self.root_dir / ".venv"
        self.vscode_dir = self.root_dir / ".vscode"
        
        # Development tools to install
        self.dev_tools = [
            "build>=0.10.0",
            "twine>=4.0.0",
            "ruff>=0.1.0",
            "mypy>=1.5.0",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "bandit>=1.7.5",
            "pre-commit>=3.0.0",
            "ipython>=8.0.0",
            "jupyter>=1.0.0"
        ]
        
        self.setup_results = []
    
    def run_command(self, command: List[str], cwd: Path = None, env: Dict[str, str] = None) -> Dict[str, Any]:
        """Run command with proper environment."""
        full_env = os.environ.copy()
        if env:
            full_env.update(env)
        
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.root_dir,
                capture_output=True,
                text=True,
                env=full_env,
                check=False
            )
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(command)
            }
            
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "command": " ".join(command)
            }
    
    def check_python_version(self) -> bool:
        """Check if correct Python version is available."""
        print(f"🐍 Checking Python {self.python_version}...")
        
        # Try python, python3, and specific version
        python_commands = ["python", "python3", f"python{self.python_version}"]
        
        for cmd in python_commands:
            result = self.run_command([cmd, "--version"])
            if result["success"]:
                version_output = result["stdout"].strip()
                if self.python_version in version_output:
                    print(f"✅ Found {version_output}")
                    return True
        
        print(f"❌ Python {self.python_version} not found")
        print("Please install Python 3.11+ before running this script")
        return False
    
    def create_virtual_environment(self) -> bool:
        """Create virtual environment."""
        print(f"🔧 Creating virtual environment at {self.venv_dir}...")
        
        if self.venv_dir.exists():
            print("Virtual environment already exists, removing...")
            shutil.rmtree(self.venv_dir)
        
        result = self.run_command(["python", "-m", "venv", str(self.venv_dir)])
        
        if result["success"]:
            print("✅ Virtual environment created")
            return True
        else:
            print(f"❌ Failed to create virtual environment: {result['stderr']}")
            return False
    
    def get_venv_python(self) -> str:
        """Get path to virtual environment Python."""
        if sys.platform == "win32":
            return str(self.venv_dir / "Scripts" / "python.exe")
        else:
            return str(self.venv_dir / "bin" / "python")
    
    def get_venv_pip(self) -> str:
        """Get path to virtual environment pip."""
        if sys.platform == "win32":
            return str(self.venv_dir / "Scripts" / "pip.exe")
        else:
            return str(self.venv_dir / "bin" / "pip")
    
    def upgrade_pip(self) -> bool:
        """Upgrade pip in virtual environment."""
        print("📦 Upgrading pip...")
        
        result = self.run_command([
            self.get_venv_python(), "-m", "pip", "install", "--upgrade", "pip"
        ])
        
        if result["success"]:
            print("✅ pip upgraded")
            return True
        else:
            print(f"❌ Failed to upgrade pip: {result['stderr']}")
            return False
    
    def install_development_tools(self) -> bool:
        """Install development tools."""
        print("🛠️ Installing development tools...")
        
        for tool in self.dev_tools:
            print(f"  Installing {tool}...")
            result = self.run_command([
                self.get_venv_pip(), "install", tool
            ])
            
            if not result["success"]:
                print(f"❌ Failed to install {tool}: {result['stderr']}")
                return False
        
        print("✅ Development tools installed")
        return True
    
    def install_cognitron_packages(self) -> bool:
        """Install Cognitron packages in development mode."""
        print("📦 Installing Cognitron packages...")
        
        # Package installation order
        packages = [
            "cognitron-core",
            "cognitron-temporal",
            "cognitron-indexing", 
            "cognitron-connectors",
            "cognitron-cli"
        ]
        
        for package in packages:
            package_dir = self.root_dir / "packages" / package
            if not package_dir.exists():
                print(f"⚠️ Package directory not found: {package}")
                continue
            
            print(f"  Installing {package} in development mode...")
            result = self.run_command([
                self.get_venv_pip(), "install", "-e", f"{package_dir}[dev]"
            ])
            
            if not result["success"]:
                print(f"❌ Failed to install {package}: {result['stderr']}")
                return False
        
        # Install root package if it exists
        root_pyproject = self.root_dir / "pyproject.toml"
        if root_pyproject.exists():
            print("  Installing root package...")
            result = self.run_command([
                self.get_venv_pip(), "install", "-e", f"{self.root_dir}[dev]"
            ])
            
            if not result["success"]:
                print(f"❌ Failed to install root package: {result['stderr']}")
                return False
        
        print("✅ Cognitron packages installed")
        return True
    
    def setup_pre_commit_hooks(self) -> bool:
        """Setup pre-commit hooks."""
        print("🪝 Setting up pre-commit hooks...")
        
        # Install pre-commit hooks
        result = self.run_command([
            self.get_venv_python(), "-m", "pre_commit", "install"
        ])
        
        if result["success"]:
            print("✅ Pre-commit hooks installed")
            return True
        else:
            print(f"❌ Failed to install pre-commit hooks: {result['stderr']}")
            return False
    
    def create_vscode_configuration(self) -> bool:
        """Create VSCode configuration."""
        print("💻 Creating VSCode configuration...")
        
        self.vscode_dir.mkdir(exist_ok=True)
        
        # Settings
        settings = {
            "python.defaultInterpreterPath": str(self.get_venv_python()),
            "python.terminal.activateEnvironment": True,
            "python.linting.enabled": True,
            "python.linting.ruffEnabled": True,
            "python.linting.mypyEnabled": True,
            "python.testing.pytestEnabled": True,
            "python.testing.unittestEnabled": False,
            "python.testing.pytestArgs": ["--tb=short"],
            "editor.formatOnSave": True,
            "python.formatting.provider": "none",
            "[python]": {
                "editor.defaultFormatter": "charliermarsh.ruff",
                "editor.codeActionsOnSave": {
                    "source.organizeImports": True,
                    "source.fixAll": True
                }
            },
            "files.exclude": {
                "**/__pycache__": True,
                "**/*.pyc": True,
                ".pytest_cache": True,
                ".mypy_cache": True,
                "dist": True,
                "build": True,
                "*.egg-info": True
            },
            "search.exclude": {
                "**/node_modules": True,
                "**/bower_components": True,
                "**/*.code-search": True,
                "dist": True,
                "build": True,
                ".venv": True
            }
        }
        
        settings_file = self.vscode_dir / "settings.json"
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=4)
        
        # Launch configuration
        launch_config = {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "Python: Current File",
                    "type": "python",
                    "request": "launch",
                    "program": "${file}",
                    "console": "integratedTerminal",
                    "cwd": "${workspaceFolder}",
                    "env": {
                        "PYTHONPATH": "${workspaceFolder}"
                    }
                },
                {
                    "name": "Cognitron CLI",
                    "type": "python",
                    "request": "launch",
                    "module": "cognitron_cli.cli",
                    "args": ["--help"],
                    "console": "integratedTerminal",
                    "cwd": "${workspaceFolder}"
                },
                {
                    "name": "Run Tests",
                    "type": "python",
                    "request": "launch",
                    "module": "pytest",
                    "args": ["-v"],
                    "console": "integratedTerminal",
                    "cwd": "${workspaceFolder}"
                }
            ]
        }
        
        launch_file = self.vscode_dir / "launch.json"
        with open(launch_file, "w") as f:
            json.dump(launch_config, f, indent=4)
        
        # Tasks
        tasks_config = {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "Test All",
                    "type": "shell",
                    "command": "${workspaceFolder}/.venv/bin/python",
                    "args": ["scripts/test_all.py"],
                    "group": {
                        "kind": "test",
                        "isDefault": True
                    },
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "shared"
                    },
                    "problemMatcher": "$python"
                },
                {
                    "label": "Build All",
                    "type": "shell",
                    "command": "${workspaceFolder}/.venv/bin/python",
                    "args": ["scripts/build_all.py"],
                    "group": {
                        "kind": "build",
                        "isDefault": True
                    },
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "shared"
                    },
                    "problemMatcher": "$python"
                },
                {
                    "label": "Medical-Grade Validation",
                    "type": "shell",
                    "command": "${workspaceFolder}/.venv/bin/python",
                    "args": ["scripts/medical_grade_validation.py", "--strict"],
                    "group": "test",
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "shared"
                    },
                    "problemMatcher": "$python"
                },
                {
                    "label": "Format Code",
                    "type": "shell",
                    "command": "${workspaceFolder}/.venv/bin/python",
                    "args": ["-m", "ruff", "format", "."],
                    "group": "build",
                    "presentation": {
                        "echo": True,
                        "reveal": "silent",
                        "focus": False,
                        "panel": "shared"
                    }
                },
                {
                    "label": "Lint Code",
                    "type": "shell",
                    "command": "${workspaceFolder}/.venv/bin/python",
                    "args": ["-m", "ruff", "check", "."],
                    "group": "test",
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "shared"
                    },
                    "problemMatcher": {
                        "owner": "ruff",
                        "fileLocation": "absolute",
                        "pattern": {
                            "regexp": "^(.+?):(\\d+):(\\d+): (\\w+) (.+)$",
                            "file": 1,
                            "line": 2,
                            "column": 3,
                            "severity": 4,
                            "message": 5
                        }
                    }
                }
            ]
        }
        
        tasks_file = self.vscode_dir / "tasks.json"
        with open(tasks_file, "w") as f:
            json.dump(tasks_config, f, indent=4)
        
        # Extensions recommendations
        extensions = {
            "recommendations": [
                "ms-python.python",
                "ms-python.vscode-pylance",
                "charliermarsh.ruff",
                "ms-python.pytest", 
                "ms-toolsai.jupyter",
                "redhat.vscode-yaml",
                "yzhang.markdown-all-in-one",
                "eamodio.gitlens",
                "ms-vscode.test-adapter-converter",
                "littlefoxteam.vscode-python-test-adapter"
            ]
        }
        
        extensions_file = self.vscode_dir / "extensions.json"
        with open(extensions_file, "w") as f:
            json.dump(extensions, f, indent=4)
        
        print("✅ VSCode configuration created")
        return True
    
    def create_development_scripts(self) -> bool:
        """Create convenient development scripts."""
        print("📜 Creating development scripts...")
        
        scripts_dir = self.root_dir / "dev-scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        # Development server script
        dev_server_script = '''#!/bin/bash
# Development server with hot reloading
export PYTHONPATH="${PWD}:${PYTHONPATH}"
source .venv/bin/activate
python -m cognitron_cli.cli serve --dev --reload
'''
        
        dev_server_file = scripts_dir / "dev-server.sh"
        dev_server_file.write_text(dev_server_script)
        dev_server_file.chmod(0o755)
        
        # Quick test script
        quick_test_script = '''#!/bin/bash
# Quick test run for development
source .venv/bin/activate
python scripts/test_all.py --no-coverage
'''
        
        quick_test_file = scripts_dir / "quick-test.sh"
        quick_test_file.write_text(quick_test_script)
        quick_test_file.chmod(0o755)
        
        # Development reset script
        reset_script = '''#!/bin/bash
# Reset development environment
echo "🧹 Cleaning development environment..."
rm -rf .venv
rm -rf dist/
rm -rf build/
find . -name "*.pyc" -delete
find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
echo "✅ Development environment cleaned"
echo "Run './scripts/setup_development.py' to recreate"
'''
        
        reset_file = scripts_dir / "reset-dev.sh"
        reset_file.write_text(reset_script)
        reset_file.chmod(0o755)
        
        print("✅ Development scripts created")
        return True
    
    def create_makefile(self) -> bool:
        """Create Makefile for common development tasks."""
        print("🔨 Creating Makefile...")
        
        makefile_content = '''# Cognitron Development Makefile
SHELL := /bin/bash
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: help install test build clean format lint type-check security dev-setup

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \\033[36m%-15s\\033[0m %s\\n", $$1, $$2}' $(MAKEFILE_LIST)

install: $(VENV) ## Install all packages in development mode
	$(PYTHON) scripts/install_all.py --dev

$(VENV): ## Create virtual environment
	python -m venv $(VENV)
	$(PIP) install --upgrade pip

test: ## Run all tests
	$(PYTHON) scripts/test_all.py

test-quick: ## Run tests without coverage
	$(PYTHON) scripts/test_all.py --no-coverage

build: ## Build all packages
	$(PYTHON) scripts/build_all.py

clean: ## Clean build artifacts
	rm -rf dist/
	rm -rf build/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

format: ## Format code with ruff
	$(PYTHON) -m ruff format .

lint: ## Lint code with ruff
	$(PYTHON) -m ruff check .

type-check: ## Run type checking
	$(PYTHON) -m mypy packages/*/src

security: ## Run security scan
	$(PYTHON) -m bandit -r packages/*/src

medical-grade: ## Run medical-grade validation
	$(PYTHON) scripts/medical_grade_validation.py --strict

dev-setup: $(VENV) ## Complete development setup
	$(PYTHON) scripts/setup_development.py

dev-reset: ## Reset development environment
	./dev-scripts/reset-dev.sh

pre-commit: ## Run pre-commit hooks
	$(PYTHON) -m pre_commit run --all-files

cognitron: ## Run cognitron CLI
	$(PYTHON) -m cognitron_cli.cli

jupyter: ## Start Jupyter notebook
	$(PYTHON) -m jupyter notebook

# Development targets
.PHONY: dev-server dev-test dev-docs

dev-server: ## Start development server
	./dev-scripts/dev-server.sh

dev-test: ## Run development tests
	./dev-scripts/quick-test.sh

dev-docs: ## Generate documentation
	$(PYTHON) scripts/generate_docs.py
'''
        
        makefile_path = self.root_dir / "Makefile"
        makefile_path.write_text(makefile_content)
        
        print("✅ Makefile created")
        return True
    
    def run_setup(self) -> bool:
        """Run complete development environment setup."""
        print("🚀 Setting up Cognitron development environment...")
        print("=" * 60)
        
        setup_steps = [
            ("Python Version Check", self.check_python_version),
            ("Virtual Environment", self.create_virtual_environment),
            ("Pip Upgrade", self.upgrade_pip),
            ("Development Tools", self.install_development_tools),
            ("Cognitron Packages", self.install_cognitron_packages),
            ("Pre-commit Hooks", self.setup_pre_commit_hooks),
            ("VSCode Configuration", self.create_vscode_configuration),
            ("Development Scripts", self.create_development_scripts),
            ("Makefile", self.create_makefile)
        ]
        
        successful_steps = 0
        
        for step_name, step_func in setup_steps:
            try:
                success = step_func()
                if success:
                    successful_steps += 1
                    self.setup_results.append((step_name, True, None))
                else:
                    self.setup_results.append((step_name, False, "Setup failed"))
            except Exception as e:
                print(f"❌ Exception in {step_name}: {e}")
                self.setup_results.append((step_name, False, str(e)))
        
        # Print summary
        print()
        print("=" * 60)
        print("📊 SETUP SUMMARY")
        print("=" * 60)
        
        for step_name, success, error in self.setup_results:
            status = "✅" if success else "❌"
            print(f"{status} {step_name}")
            if error:
                print(f"    Error: {error}")
        
        print()
        print(f"Completed: {successful_steps}/{len(setup_steps)} steps")
        
        if successful_steps == len(setup_steps):
            print("🎉 Development environment setup complete!")
            self.print_next_steps()
            return True
        else:
            print("❌ Setup incomplete - check errors above")
            return False
    
    def print_next_steps(self) -> None:
        """Print next steps for developer."""
        print()
        print("🎯 NEXT STEPS:")
        print("=" * 40)
        print("1. Activate virtual environment:")
        print(f"   source {self.venv_dir}/bin/activate")
        print()
        print("2. Verify installation:")
        print("   cognitron --help")
        print()
        print("3. Run tests:")
        print("   make test")
        print()
        print("4. Start development:")
        print("   make dev-server")
        print()
        print("5. VSCode users:")
        print("   code .  # Opens with correct configuration")
        print()
        print("📚 Available commands:")
        print("   make help          # Show all available commands")
        print("   make medical-grade # Run full quality validation")
        print("   make format        # Format code")
        print("   make lint          # Lint code")
        print("   make build         # Build all packages")


def main():
    """Main setup entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup Cognitron development environment")
    parser.add_argument("--root", type=Path, default=Path.cwd(),
                       help="Root directory (default: current directory)")
    parser.add_argument("--python-version", default="3.11",
                       help="Python version to use (default: 3.11)")
    
    args = parser.parse_args()
    
    setup = DevelopmentEnvironmentSetup(args.root, args.python_version)
    success = setup.run_setup()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()