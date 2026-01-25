#!/usr/bin/env python3
"""
CI/CD Configuration Generator

Creates GitHub Actions workflows and other CI/CD configurations
for the Cognitron monorepo with medical-grade quality requirements.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List


class CICDConfigGenerator:
    """Generates CI/CD configuration files."""
    
    def __init__(self, root_dir: Path):
        self.root_dir = Path(root_dir)
        self.github_workflows_dir = self.root_dir / ".github" / "workflows"
        self.github_workflows_dir.mkdir(parents=True, exist_ok=True)
    
    def create_main_ci_workflow(self) -> Dict[str, Any]:
        """Create main CI workflow for medical-grade quality assurance."""
        return {
            "name": "Medical-Grade CI/CD Pipeline",
            "on": {
                "push": {
                    "branches": ["main", "develop"]
                },
                "pull_request": {
                    "branches": ["main", "develop"]
                }
            },
            "env": {
                "PYTHON_VERSION": "3.11",
                "MEDICAL_GRADE_REQUIRED": "true",
                "TEST_SUCCESS_RATE_REQUIRED": "100"
            },
            "jobs": {
                "quality-gates": {
                    "name": "Medical-Grade Quality Gates",
                    "runs-on": "ubuntu-latest",
                    "strategy": {
                        "matrix": {
                            "python-version": ["3.11", "3.12", "3.13"]
                        }
                    },
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Set up Python ${{ matrix.python-version }}",
                            "uses": "actions/setup-python@v4",
                            "with": {
                                "python-version": "${{ matrix.python-version }}"
                            }
                        },
                        {
                            "name": "Install dependencies",
                            "run": "python scripts/install_all.py --dev"
                        },
                        {
                            "name": "Security scan (Bandit)", 
                            "run": "bandit -r packages/ -f json -o security-report.json || true"
                        },
                        {
                            "name": "Lint check (Ruff)",
                            "run": "python scripts/lint_all.py --check"
                        },
                        {
                            "name": "Type check (MyPy)",
                            "run": "python scripts/type_check_all.py"
                        },
                        {
                            "name": "Format check (Ruff)",
                            "run": "python scripts/format_all.py --check"
                        },
                        {
                            "name": "Run unit tests",
                            "run": "python scripts/test_all.py --coverage --junit"
                        },
                        {
                            "name": "Medical-Grade Validation",
                            "run": "python scripts/medical_grade_validation.py --strict"
                        },
                        {
                            "name": "Upload coverage reports",
                            "uses": "codecov/codecov-action@v3",
                            "with": {
                                "files": "./coverage.xml",
                                "fail_ci_if_error": True
                            }
                        }
                    ]
                },
                "integration-tests": {
                    "name": "Integration Testing",
                    "runs-on": "ubuntu-latest",
                    "needs": "quality-gates",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v4",
                            "with": {
                                "python-version": "3.11"
                            }
                        },
                        {
                            "name": "Install all packages",
                            "run": "python scripts/install_all.py --dev"
                        },
                        {
                            "name": "Run integration tests",
                            "run": "python scripts/integration_test_all.py"
                        },
                        {
                            "name": "End-to-end testing",
                            "run": "python scripts/e2e_test_all.py"
                        },
                        {
                            "name": "Performance benchmarks", 
                            "run": "python scripts/benchmark_all.py"
                        }
                    ]
                },
                "build-and-publish": {
                    "name": "Build and Publish",
                    "runs-on": "ubuntu-latest",
                    "needs": ["quality-gates", "integration-tests"],
                    "if": "github.ref == 'refs/heads/main'",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v4",
                            "with": {
                                "python-version": "3.11"
                            }
                        },
                        {
                            "name": "Build all packages",
                            "run": "python scripts/build_all.py"
                        },
                        {
                            "name": "Test built packages",
                            "run": "python scripts/test_built_packages.py"
                        },
                        {
                            "name": "Publish to PyPI",
                            "if": "startsWith(github.ref, 'refs/tags/')",
                            "run": "python scripts/publish_all.py",
                            "env": {
                                "TWINE_USERNAME": "__token__",
                                "TWINE_PASSWORD": "${{ secrets.PYPI_API_TOKEN }}"
                            }
                        }
                    ]
                }
            }
        }
    
    def create_pre_commit_config(self) -> Dict[str, Any]:
        """Create pre-commit hooks configuration."""
        return {
            "repos": [
                {
                    "repo": "https://github.com/pre-commit/pre-commit-hooks",
                    "rev": "v4.5.0",
                    "hooks": [
                        {"id": "trailing-whitespace"},
                        {"id": "end-of-file-fixer"},
                        {"id": "check-yaml"},
                        {"id": "check-json"},
                        {"id": "check-toml"},
                        {"id": "check-merge-conflict"},
                        {"id": "check-docstring-first"},
                        {"id": "debug-statements"},
                        {"id": "name-tests-test", "args": ["--pytest-test-first"]}
                    ]
                },
                {
                    "repo": "https://github.com/astral-sh/ruff-pre-commit",
                    "rev": "v0.1.6",
                    "hooks": [
                        {"id": "ruff", "args": ["--fix", "--exit-non-zero-on-fix"]},
                        {"id": "ruff-format"}
                    ]
                },
                {
                    "repo": "https://github.com/pre-commit/mirrors-mypy",
                    "rev": "v1.7.1",
                    "hooks": [
                        {
                            "id": "mypy",
                            "additional_dependencies": ["types-all"],
                            "args": ["--strict", "--show-error-codes"]
                        }
                    ]
                },
                {
                    "repo": "https://github.com/PyCQA/bandit",
                    "rev": "1.7.5",
                    "hooks": [
                        {
                            "id": "bandit",
                            "args": ["-c", "pyproject.toml", "-ll"],
                            "additional_dependencies": ["bandit[toml]"]
                        }
                    ]
                },
                {
                    "repo": "local",
                    "hooks": [
                        {
                            "id": "medical-grade-validation",
                            "name": "Medical-Grade Quality Validation",
                            "entry": "python scripts/pre_commit_medical_validation.py",
                            "language": "python",
                            "pass_filenames": False,
                            "always_run": True
                        }
                    ]
                }
            ]
        }
    
    def create_dependabot_config(self) -> Dict[str, Any]:
        """Create Dependabot configuration for dependency updates."""
        return {
            "version": 2,
            "updates": [
                {
                    "package-ecosystem": "pip",
                    "directory": "/",
                    "schedule": {"interval": "weekly"},
                    "open-pull-requests-limit": 5,
                    "reviewers": ["@cognitron-team"],
                    "commit-message": {
                        "prefix": "deps:",
                        "include": "scope"
                    }
                }
            ] + [
                {
                    "package-ecosystem": "pip",
                    "directory": f"/packages/cognitron-{package}",
                    "schedule": {"interval": "weekly"},
                    "open-pull-requests-limit": 3
                }
                for package in ["core", "temporal", "indexing", "cli", "connectors"]
            ] + [
                {
                    "package-ecosystem": "github-actions",
                    "directory": "/",
                    "schedule": {"interval": "weekly"},
                    "commit-message": {
                        "prefix": "ci:",
                        "include": "scope"
                    }
                }
            ]
        }
    
    def create_release_workflow(self) -> Dict[str, Any]:
        """Create automated release workflow."""
        return {
            "name": "Release Workflow",
            "on": {
                "push": {
                    "tags": ["v*"]
                }
            },
            "jobs": {
                "release": {
                    "name": "Create Release",
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v4",
                            "with": {
                                "python-version": "3.11"
                            }
                        },
                        {
                            "name": "Install dependencies",
                            "run": "python scripts/install_all.py --dev"
                        },
                        {
                            "name": "Run complete test suite",
                            "run": "python scripts/full_medical_grade_test.py"
                        },
                        {
                            "name": "Build all packages",
                            "run": "python scripts/build_all.py --release"
                        },
                        {
                            "name": "Generate release notes",
                            "run": "python scripts/generate_release_notes.py"
                        },
                        {
                            "name": "Create GitHub Release",
                            "uses": "actions/create-release@v1",
                            "env": {
                                "GITHUB_TOKEN": "${{ secrets.GITHUB_TOKEN }}"
                            },
                            "with": {
                                "tag_name": "${{ github.ref }}",
                                "release_name": "Release ${{ github.ref }}",
                                "body_path": "RELEASE_NOTES.md",
                                "draft": False,
                                "prerelease": False
                            }
                        },
                        {
                            "name": "Publish to PyPI",
                            "run": "python scripts/publish_all.py --production",
                            "env": {
                                "TWINE_USERNAME": "__token__",
                                "TWINE_PASSWORD": "${{ secrets.PYPI_API_TOKEN }}"
                            }
                        }
                    ]
                }
            }
        }
    
    def create_docker_workflow(self) -> Dict[str, Any]:
        """Create Docker image build and publish workflow."""
        return {
            "name": "Docker Build and Publish",
            "on": {
                "push": {
                    "branches": ["main"],
                    "tags": ["v*"]
                }
            },
            "env": {
                "REGISTRY": "ghcr.io",
                "IMAGE_NAME": "${{ github.repository }}"
            },
            "jobs": {
                "build-and-push": {
                    "runs-on": "ubuntu-latest",
                    "permissions": {
                        "contents": "read",
                        "packages": "write"
                    },
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Set up Docker Buildx",
                            "uses": "docker/setup-buildx-action@v3"
                        },
                        {
                            "name": "Log in to Container Registry",
                            "uses": "docker/login-action@v3",
                            "with": {
                                "registry": "${{ env.REGISTRY }}",
                                "username": "${{ github.actor }}",
                                "password": "${{ secrets.GITHUB_TOKEN }}"
                            }
                        },
                        {
                            "name": "Extract metadata",
                            "id": "meta",
                            "uses": "docker/metadata-action@v5",
                            "with": {
                                "images": "${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}"
                            }
                        },
                        {
                            "name": "Build and push Docker image",
                            "uses": "docker/build-push-action@v5",
                            "with": {
                                "context": ".",
                                "platforms": "linux/amd64,linux/arm64",
                                "push": True,
                                "tags": "${{ steps.meta.outputs.tags }}",
                                "labels": "${{ steps.meta.outputs.labels }}"
                            }
                        }
                    ]
                }
            }
        }
    
    def generate_all_configs(self) -> None:
        """Generate all CI/CD configuration files."""
        print("🔧 Generating CI/CD configurations...")
        
        # GitHub Actions workflows
        workflows = {
            "ci.yml": self.create_main_ci_workflow(),
            "release.yml": self.create_release_workflow(),
            "docker.yml": self.create_docker_workflow()
        }
        
        for workflow_name, workflow_config in workflows.items():
            workflow_path = self.github_workflows_dir / workflow_name
            with open(workflow_path, "w") as f:
                yaml.dump(workflow_config, f, default_flow_style=False, sort_keys=False)
            print(f"✓ Created GitHub workflow: {workflow_name}")
        
        # Pre-commit configuration
        precommit_config = self.create_pre_commit_config()
        precommit_path = self.root_dir / ".pre-commit-config.yaml"
        with open(precommit_path, "w") as f:
            yaml.dump(precommit_config, f, default_flow_style=False)
        print("✓ Created pre-commit configuration")
        
        # Dependabot configuration
        dependabot_config = self.create_dependabot_config()
        dependabot_dir = self.root_dir / ".github"
        dependabot_dir.mkdir(exist_ok=True)
        dependabot_path = dependabot_dir / "dependabot.yml"
        with open(dependabot_path, "w") as f:
            yaml.dump(dependabot_config, f, default_flow_style=False)
        print("✓ Created Dependabot configuration")
        
        # Create Dockerfile
        dockerfile_content = """FROM python:3.11-slim

LABEL org.opencontainers.image.source=https://github.com/cognitron-ai/cognitron
LABEL org.opencontainers.image.description="Cognitron Knowledge Management System"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY pyproject.toml ./
COPY packages/ ./packages/
RUN pip install --no-cache-dir -e ".[all]"

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash cognitron
USER cognitron

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD cognitron health-check || exit 1

# Run the application
CMD ["cognitron", "serve"]
"""
        
        dockerfile_path = self.root_dir / "Dockerfile"
        dockerfile_path.write_text(dockerfile_content)
        print("✓ Created Dockerfile")
        
        # Create .dockerignore
        dockerignore_content = """.git
.github
*.pyc
__pycache__
.pytest_cache
.mypy_cache
.coverage
htmlcov/
dist/
build/
*.egg-info/
.venv/
.env
README.md
docs/
tests/
*.md
"""
        
        dockerignore_path = self.root_dir / ".dockerignore"
        dockerignore_path.write_text(dockerignore_content)
        print("✓ Created .dockerignore")
        
        # Create GitHub issue templates
        issue_templates_dir = self.root_dir / ".github" / "ISSUE_TEMPLATE"
        issue_templates_dir.mkdir(parents=True, exist_ok=True)
        
        bug_template = """---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: 'bug, needs-triage'
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Medical-Grade Impact**
- [ ] This bug affects test success rate
- [ ] This bug affects data integrity
- [ ] This bug affects security
- [ ] This bug affects performance

**Environment:**
 - OS: [e.g. iOS]
 - Python Version: [e.g. 3.11]
 - Cognitron Version: [e.g. 0.1.0]

**Additional context**
Add any other context about the problem here.
"""
        
        (issue_templates_dir / "bug_report.md").write_text(bug_template)
        
        feature_template = """---
name: Feature request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: 'enhancement, needs-triage'
assignees: ''

---

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Medical-Grade Requirements**
- [ ] This feature must maintain 100% test success rate
- [ ] This feature requires comprehensive testing
- [ ] This feature affects data integrity
- [ ] This feature affects security

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
"""
        
        (issue_templates_dir / "feature_request.md").write_text(feature_template)
        print("✓ Created GitHub issue templates")
        
        print()
        print("✅ All CI/CD configurations generated!")
        print("\nGenerated files:")
        print("  - .github/workflows/ci.yml")
        print("  - .github/workflows/release.yml")
        print("  - .github/workflows/docker.yml")
        print("  - .pre-commit-config.yaml")
        print("  - .github/dependabot.yml")
        print("  - Dockerfile")
        print("  - .dockerignore")
        print("  - .github/ISSUE_TEMPLATE/")


def main():
    """Main CI/CD configuration generator entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate CI/CD configurations")
    parser.add_argument("--root", type=Path, default=Path.cwd(),
                       help="Root directory (default: current directory)")
    
    args = parser.parse_args()
    
    generator = CICDConfigGenerator(args.root)
    generator.generate_all_configs()


if __name__ == "__main__":
    main()