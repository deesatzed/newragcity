#!/usr/bin/env python3
"""
Package Configuration Generator

Creates pyproject.toml files for each package in the monorepo
with appropriate dependencies, build settings, and quality tools.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
import toml


class PackageConfigGenerator:
    """Generates configuration files for monorepo packages."""
    
    def __init__(self, root_dir: Path):
        self.root_dir = Path(root_dir)
        self.packages_dir = self.root_dir / "packages"
        
        # Common dependencies and configuration
        self.common_dev_deps = [
            "ruff>=0.1.0",
            "mypy>=1.5.0",
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "pre-commit>=3.0.0"
        ]
        
        self.common_build_config = {
            "build-system": {
                "requires": ["hatchling"],
                "build-backend": "hatchling.build"
            }
        }
        
        self.common_tool_config = {
            "tool": {
                "ruff": {
                    "target-version": "py311",
                    "line-length": 100,
                    "select": ["E", "F", "W", "I", "N", "B", "A", "C4", "EM", "UP"],
                    "ignore": ["E501", "B008", "B904"],
                    "exclude": [
                        ".git", "__pycache__", "build", "dist", 
                        ".venv", ".pytest_cache", ".mypy_cache"
                    ]
                },
                "mypy": {
                    "python_version": "3.11",
                    "warn_return_any": True,
                    "warn_unused_configs": True,
                    "disallow_untyped_defs": True,
                    "disallow_incomplete_defs": True,
                    "check_untyped_defs": True,
                    "disallow_untyped_decorators": True
                },
                "pytest": {
                    "ini_options": {
                        "minversion": "7.0",
                        "addopts": "-ra -q --strict-markers --strict-config",
                        "testpaths": ["tests"],
                        "asyncio_mode": "auto"
                    }
                },
                "coverage": {
                    "run": {
                        "source": ["src"],
                        "omit": ["tests/*"]
                    },
                    "report": {
                        "exclude_lines": [
                            "pragma: no cover",
                            "def __repr__",
                            "if self.debug:",
                            "if settings.DEBUG",
                            "raise AssertionError", 
                            "raise NotImplementedError",
                            "if 0:",
                            "if __name__ == .__main__.:"
                        ]
                    }
                }
            }
        }
    
    def create_core_package_config(self) -> Dict[str, Any]:
        """Create configuration for cognitron-core package."""
        return {
            **self.common_build_config,
            "project": {
                "name": "cognitron-core",
                "version": "0.1.0",
                "description": "Core functionality for Cognitron knowledge management system",
                "authors": [{"name": "Cognitron Team", "email": "team@cognitron.ai"}],
                "license": {"text": "Apache-2.0"},
                "readme": "README.md",
                "requires-python": ">=3.11",
                "keywords": ["ai", "knowledge-management", "core", "agent", "memory"],
                "classifiers": [
                    "Development Status :: 3 - Alpha",
                    "Intended Audience :: Developers", 
                    "License :: OSI Approved :: Apache Software License",
                    "Programming Language :: Python :: 3.11",
                    "Programming Language :: Python :: 3.12",
                    "Programming Language :: Python :: 3.13",
                    "Topic :: Software Development :: Documentation",
                    "Topic :: Scientific/Engineering :: Artificial Intelligence"
                ],
                "dependencies": [
                    "pydantic>=2.0.0",
                    "scikit-learn>=1.3.0",
                    "sqlite-utils>=3.34.0",
                    "numpy>=1.24.0",
                    "pandas>=2.0.0"
                ],
                "optional-dependencies": {
                    "dev": self.common_dev_deps,
                    "llm": [
                        "openai>=1.0.0",
                        "google-generativeai>=0.8.0",
                        "transformers>=4.30.0",
                        "sentence-transformers>=2.2.0",
                        "tiktoken>=0.7.0"
                    ]
                }
            },
            **self.common_tool_config
        }
    
    def create_temporal_package_config(self) -> Dict[str, Any]:
        """Create configuration for cognitron-temporal package."""
        return {
            **self.common_build_config,
            "project": {
                "name": "cognitron-temporal",
                "version": "0.1.0", 
                "description": "Temporal intelligence and pattern recognition for Cognitron",
                "authors": [{"name": "Cognitron Team", "email": "team@cognitron.ai"}],
                "license": {"text": "Apache-2.0"},
                "readme": "README.md",
                "requires-python": ">=3.11",
                "keywords": ["ai", "temporal", "patterns", "memory-decay", "intelligence"],
                "classifiers": [
                    "Development Status :: 3 - Alpha",
                    "Intended Audience :: Developers",
                    "License :: OSI Approved :: Apache Software License", 
                    "Programming Language :: Python :: 3.11",
                    "Programming Language :: Python :: 3.12",
                    "Programming Language :: Python :: 3.13",
                    "Topic :: Scientific/Engineering :: Artificial Intelligence"
                ],
                "dependencies": [
                    "cognitron-core>=0.1.0",
                    "numpy>=1.24.0",
                    "pandas>=2.0.0",
                    "scikit-learn>=1.3.0",
                    "hdbscan>=0.8.33",
                    "watchdog>=3.0.0"
                ],
                "optional-dependencies": {
                    "dev": self.common_dev_deps
                }
            },
            **self.common_tool_config
        }
    
    def create_indexing_package_config(self) -> Dict[str, Any]:
        """Create configuration for cognitron-indexing package."""
        return {
            **self.common_build_config,
            "project": {
                "name": "cognitron-indexing",
                "version": "0.1.0",
                "description": "Knowledge indexing and search capabilities for Cognitron",
                "authors": [{"name": "Cognitron Team", "email": "team@cognitron.ai"}],
                "license": {"text": "Apache-2.0"},
                "readme": "README.md", 
                "requires-python": ">=3.11",
                "keywords": ["indexing", "search", "knowledge", "retrieval", "topics"],
                "classifiers": [
                    "Development Status :: 3 - Alpha",
                    "Intended Audience :: Developers",
                    "License :: OSI Approved :: Apache Software License",
                    "Programming Language :: Python :: 3.11", 
                    "Programming Language :: Python :: 3.12",
                    "Programming Language :: Python :: 3.13",
                    "Topic :: Text Processing :: Indexing"
                ],
                "dependencies": [
                    "cognitron-core>=0.1.0",
                    "leann-core>=0.3.2",
                    "leann-backend-hnsw>=0.3.2",
                    "sentence-transformers>=2.2.0",
                    "PyMuPDF>=1.23.0",
                    "aiofiles>=24.0.0"
                ],
                "optional-dependencies": {
                    "dev": self.common_dev_deps
                }
            },
            **self.common_tool_config
        }
    
    def create_cli_package_config(self) -> Dict[str, Any]:
        """Create configuration for cognitron-cli package.""" 
        return {
            **self.common_build_config,
            "project": {
                "name": "cognitron-cli",
                "version": "0.1.0",
                "description": "Command-line interface for Cognitron knowledge management",
                "authors": [{"name": "Cognitron Team", "email": "team@cognitron.ai"}],
                "license": {"text": "Apache-2.0"},
                "readme": "README.md",
                "requires-python": ">=3.11",
                "keywords": ["cli", "command-line", "knowledge-management", "cognitron"],
                "classifiers": [
                    "Development Status :: 3 - Alpha",
                    "Intended Audience :: Developers",
                    "License :: OSI Approved :: Apache Software License",
                    "Programming Language :: Python :: 3.11",
                    "Programming Language :: Python :: 3.12", 
                    "Programming Language :: Python :: 3.13",
                    "Environment :: Console"
                ],
                "dependencies": [
                    "cognitron-core>=0.1.0",
                    "cognitron-temporal>=0.1.0",
                    "cognitron-indexing>=0.1.0", 
                    "cognitron-connectors>=0.1.0",
                    "typer>=0.12.0",
                    "rich>=13.0.0",
                    "python-dotenv>=1.0.0"
                ],
                "optional-dependencies": {
                    "dev": self.common_dev_deps
                },
                "scripts": {
                    "cognitron": "cognitron_cli.cli:main"
                }
            },
            **self.common_tool_config
        }
    
    def create_connectors_package_config(self) -> Dict[str, Any]:
        """Create configuration for cognitron-connectors package."""
        return {
            **self.common_build_config,
            "project": {
                "name": "cognitron-connectors",
                "version": "0.1.0",
                "description": "Workspace connectors for Cognitron (Git, IDE, Filesystem, etc.)",
                "authors": [{"name": "Cognitron Team", "email": "team@cognitron.ai"}],
                "license": {"text": "Apache-2.0"},
                "readme": "README.md",
                "requires-python": ">=3.11",
                "keywords": ["connectors", "workspace", "git", "ide", "filesystem"],
                "classifiers": [
                    "Development Status :: 3 - Alpha",
                    "Intended Audience :: Developers",
                    "License :: OSI Approved :: Apache Software License",
                    "Programming Language :: Python :: 3.11",
                    "Programming Language :: Python :: 3.12",
                    "Programming Language :: Python :: 3.13",
                    "Topic :: Software Development :: Version Control"
                ],
                "dependencies": [
                    "cognitron-core>=0.1.0",
                    "aiofiles>=24.0.0",
                    "watchdog>=3.0.0",
                    "GitPython>=3.1.0"
                ],
                "optional-dependencies": {
                    "dev": self.common_dev_deps,
                    "ide": [
                        "pynvim>=0.4.0"  # For Neovim integration
                    ],
                    "advanced": [
                        "tree-sitter>=0.20.0",  # For code parsing
                        "tree-sitter-python>=0.20.0"
                    ]
                }
            },
            **self.common_tool_config
        }
    
    def create_workspace_config(self) -> Dict[str, Any]:
        """Create workspace configuration file."""
        return {
            "name": "cognitron-workspace",
            "version": "0.1.0",
            "description": "Cognitron monorepo workspace configuration",
            "workspaces": {
                "packages": [
                    "packages/cognitron-core",
                    "packages/cognitron-temporal", 
                    "packages/cognitron-indexing",
                    "packages/cognitron-cli",
                    "packages/cognitron-connectors"
                ],
                "apps": [
                    "apps/cognitron-desktop"
                ]
            },
            "scripts": {
                "build-all": "python scripts/build_all.py",
                "test-all": "python scripts/test_all.py",
                "lint-all": "python scripts/lint_all.py", 
                "format-all": "python scripts/format_all.py",
                "install-all": "python scripts/install_all.py",
                "clean-all": "python scripts/clean_all.py"
            },
            "quality_gates": {
                "test_success_rate": 100,  # Medical-grade requirement
                "coverage_minimum": 95,
                "type_check_required": True,
                "lint_errors_allowed": 0,
                "security_scan_required": True
            },
            "dependencies": {
                "python": ">=3.11",
                "build_tools": [
                    "hatchling",
                    "build",
                    "twine"
                ],
                "quality_tools": [
                    "ruff",
                    "mypy", 
                    "pytest",
                    "pytest-cov",
                    "pre-commit",
                    "bandit"  # Security scanning
                ]
            }
        }
    
    def generate_all_configs(self) -> None:
        """Generate all package configuration files."""
        print("🔧 Generating package configurations...")
        
        # Package configurations
        package_configs = {
            "cognitron-core": self.create_core_package_config(),
            "cognitron-temporal": self.create_temporal_package_config(),
            "cognitron-indexing": self.create_indexing_package_config(),
            "cognitron-cli": self.create_cli_package_config(),
            "cognitron-connectors": self.create_connectors_package_config()
        }
        
        # Create package directories and configs
        for package_name, config in package_configs.items():
            package_dir = self.packages_dir / package_name
            package_dir.mkdir(parents=True, exist_ok=True)
            
            # Write pyproject.toml
            pyproject_path = package_dir / "pyproject.toml"
            with open(pyproject_path, "w") as f:
                toml.dump(config, f)
            
            # Create basic README
            readme_path = package_dir / "README.md"
            readme_content = f"""# {package_name}

{config['project']['description']}

## Installation

```bash
pip install {package_name}
```

## Development

```bash
pip install -e ".[dev]"
```

## Testing  

```bash
pytest
```
"""
            readme_path.write_text(readme_content)
            
            print(f"✓ Created configuration for {package_name}")
        
        # Create workspace configuration
        workspace_config = self.create_workspace_config()
        workspace_path = self.root_dir / "workspace.json"
        with open(workspace_path, "w") as f:
            json.dump(workspace_config, f, indent=2)
        
        print("✓ Created workspace configuration")
        
        # Create root pyproject.toml for monorepo management
        root_config = {
            **self.common_build_config,
            "project": {
                "name": "cognitron-monorepo",
                "version": "0.1.0",
                "description": "Cognitron Knowledge Management System - Monorepo",
                "authors": [{"name": "Cognitron Team", "email": "team@cognitron.ai"}],
                "license": {"text": "Apache-2.0"},
                "requires-python": ">=3.11",
                "dependencies": [
                    "cognitron-core>=0.1.0",
                    "cognitron-temporal>=0.1.0", 
                    "cognitron-indexing>=0.1.0",
                    "cognitron-cli>=0.1.0",
                    "cognitron-connectors>=0.1.0"
                ],
                "optional-dependencies": {
                    "dev": self.common_dev_deps + [
                        "build>=0.10.0",
                        "twine>=4.0.0"
                    ],
                    "all": [
                        "cognitron-core[llm]>=0.1.0",
                        "cognitron-connectors[ide,advanced]>=0.1.0"
                    ]
                },
                "scripts": {
                    "cognitron": "cognitron_cli.cli:main"
                }
            },
            **self.common_tool_config
        }
        
        root_pyproject_path = self.root_dir / "pyproject.toml"
        with open(root_pyproject_path, "w") as f:
            toml.dump(root_config, f)
        
        print("✓ Created root pyproject.toml")
        
        print()
        print("✅ All package configurations generated!")
        print("\nGenerated files:")
        for package_name in package_configs.keys():
            print(f"  - packages/{package_name}/pyproject.toml")
            print(f"  - packages/{package_name}/README.md")
        print("  - workspace.json")
        print("  - pyproject.toml (root)")


def main():
    """Main configuration generator entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate package configurations")
    parser.add_argument("--root", type=Path, default=Path.cwd(),
                       help="Root directory (default: current directory)")
    
    args = parser.parse_args()
    
    generator = PackageConfigGenerator(args.root)
    generator.generate_all_configs()


if __name__ == "__main__":
    main()