#!/usr/bin/env python3
"""
Cognitron Monorepo Migration Script

This script reorganizes the current codebase into a proper monorepo structure
while preserving all functionality and maintaining the medical-grade quality requirements.

Target Structure:
cognitron/
├── packages/
│   ├── cognitron-core/           # Core functionality
│   ├── cognitron-temporal/       # Temporal intelligence
│   ├── cognitron-indexing/       # Knowledge indexing
│   ├── cognitron-cli/            # Command line interface
│   └── cognitron-connectors/     # Workspace connectors
├── apps/
│   └── cognitron-desktop/        # Desktop application
├── tools/
│   ├── build/                    # Build utilities
│   ├── test/                     # Test utilities
│   └── quality/                  # Quality assurance tools
├── scripts/                      # Migration and automation scripts
└── config/                       # Shared configurations
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
import json


class MonorepoMigrator:
    """Handles migration from single package to monorepo structure."""
    
    def __init__(self, source_dir: Path, dry_run: bool = False):
        self.source_dir = Path(source_dir)
        self.dry_run = dry_run
        self.backup_dir = self.source_dir.parent / f"{self.source_dir.name}_backup"
        
        # Define target monorepo structure
        self.monorepo_structure = {
            "packages": {
                "cognitron-core": ["core", "models.py"],
                "cognitron-temporal": ["temporal"],
                "cognitron-indexing": ["indexing"],
                "cognitron-cli": ["cli.py"],
                "cognitron-connectors": []  # New package for workspace connectors
            },
            "apps": {
                "cognitron-desktop": []  # Future desktop app
            },
            "tools": {
                "build": [],
                "test": [],
                "quality": []
            },
            "scripts": [],
            "config": []
        }
        
    def create_backup(self) -> None:
        """Create backup of current structure."""
        print(f"Creating backup at {self.backup_dir}...")
        if not self.dry_run:
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
            shutil.copytree(self.source_dir, self.backup_dir)
        print("✓ Backup created")
    
    def create_monorepo_structure(self) -> None:
        """Create the new monorepo directory structure."""
        print("Creating monorepo directory structure...")
        
        for category, packages in self.monorepo_structure.items():
            category_path = self.source_dir / category
            if not self.dry_run:
                category_path.mkdir(exist_ok=True)
            
            if isinstance(packages, dict):
                for package_name in packages:
                    package_path = category_path / package_name
                    if not self.dry_run:
                        package_path.mkdir(exist_ok=True)
                        # Create basic package structure
                        (package_path / "src").mkdir(exist_ok=True)
                        (package_path / "tests").mkdir(exist_ok=True)
                        (package_path / "__init__.py").touch()
            
            print(f"✓ Created {category}/ structure")
    
    def migrate_core_package(self) -> None:
        """Migrate core cognitron functionality."""
        print("Migrating cognitron core package...")
        
        core_package_path = self.source_dir / "packages" / "cognitron-core"
        src_path = core_package_path / "src" / "cognitron_core"
        
        if not self.dry_run:
            src_path.mkdir(parents=True, exist_ok=True)
            
            # Move core modules
            core_src = self.source_dir / "cognitron" / "core"
            if core_src.exists():
                shutil.move(str(core_src), str(src_path / "core"))
            
            # Move models
            models_src = self.source_dir / "cognitron" / "models.py"
            if models_src.exists():
                shutil.move(str(models_src), str(src_path / "models.py"))
            
            # Create package __init__.py
            init_content = '''"""
Cognitron Core Package

Core functionality for the Cognitron knowledge management system.
Includes agent, memory, confidence, and routing capabilities.
"""

__version__ = "0.1.0"

from .core.agent import CognitronAgent
from .core.memory import CaseMemory
from .core.confidence import calculate_confidence_profile
from .core.router import QueryRouter
from .models import QueryResult, WorkflowTrace, CaseMemoryEntry

__all__ = [
    "CognitronAgent",
    "CaseMemory", 
    "calculate_confidence_profile",
    "QueryRouter",
    "QueryResult",
    "WorkflowTrace",
    "CaseMemoryEntry"
]
'''
            (src_path / "__init__.py").write_text(init_content)
        
        print("✓ Core package migrated")
    
    def migrate_temporal_package(self) -> None:
        """Migrate temporal intelligence functionality."""
        print("Migrating temporal intelligence package...")
        
        temporal_package_path = self.source_dir / "packages" / "cognitron-temporal"
        src_path = temporal_package_path / "src" / "cognitron_temporal"
        
        if not self.dry_run:
            src_path.mkdir(parents=True, exist_ok=True)
            
            # Move temporal modules
            temporal_src = self.source_dir / "cognitron" / "temporal"
            if temporal_src.exists():
                shutil.move(str(temporal_src), str(src_path / "temporal"))
            
            # Create package __init__.py
            init_content = '''"""
Cognitron Temporal Intelligence Package

Provides temporal pattern recognition, context resurrection,
memory decay algorithms, and pattern crystallization.
"""

__version__ = "0.1.0"

from .temporal.project_discovery import ProjectDiscovery
from .temporal.pattern_engine import TemporalPatternEngine
from .temporal.context_resurrection import ContextResurrection
from .temporal.memory_decay import MemoryDecay, MemoryType
from .temporal.pattern_crystallization import PatternCrystallization

__all__ = [
    "ProjectDiscovery",
    "TemporalPatternEngine",
    "ContextResurrection", 
    "MemoryDecay",
    "MemoryType",
    "PatternCrystallization"
]
'''
            (src_path / "__init__.py").write_text(init_content)
        
        print("✓ Temporal package migrated")
    
    def migrate_indexing_package(self) -> None:
        """Migrate indexing functionality."""
        print("Migrating indexing package...")
        
        indexing_package_path = self.source_dir / "packages" / "cognitron-indexing"
        src_path = indexing_package_path / "src" / "cognitron_indexing"
        
        if not self.dry_run:
            src_path.mkdir(parents=True, exist_ok=True)
            
            # Move indexing modules
            indexing_src = self.source_dir / "cognitron" / "indexing"
            if indexing_src.exists():
                shutil.move(str(indexing_src), str(src_path / "indexing"))
                
            # Move topics service
            topics_src = self.source_dir / "cognitron" / "topics"
            if topics_src.exists():
                shutil.move(str(topics_src), str(src_path / "topics"))
            
            # Create package __init__.py
            init_content = '''"""
Cognitron Indexing Package

Provides knowledge indexing, search, and topic discovery capabilities.
"""

__version__ = "0.1.0"

from .indexing.service import IndexingService
from .topics.service import TopicService

__all__ = [
    "IndexingService",
    "TopicService"
]
'''
            (src_path / "__init__.py").write_text(init_content)
        
        print("✓ Indexing package migrated")
    
    def migrate_cli_package(self) -> None:
        """Migrate CLI functionality."""
        print("Migrating CLI package...")
        
        cli_package_path = self.source_dir / "packages" / "cognitron-cli"
        src_path = cli_package_path / "src" / "cognitron_cli"
        
        if not self.dry_run:
            src_path.mkdir(parents=True, exist_ok=True)
            
            # Move CLI module
            cli_src = self.source_dir / "cognitron" / "cli.py"
            if cli_src.exists():
                shutil.move(str(cli_src), str(src_path / "cli.py"))
            
            # Create package __init__.py
            init_content = '''"""
Cognitron CLI Package

Command-line interface for the Cognitron knowledge management system.
"""

__version__ = "0.1.0"

from .cli import main

__all__ = ["main"]
'''
            (src_path / "__init__.py").write_text(init_content)
        
        print("✓ CLI package migrated")
    
    def create_workspace_connectors_package(self) -> None:
        """Create new workspace connectors package."""
        print("Creating workspace connectors package...")
        
        connectors_package_path = self.source_dir / "packages" / "cognitron-connectors"
        src_path = connectors_package_path / "src" / "cognitron_connectors"
        
        if not self.dry_run:
            src_path.mkdir(parents=True, exist_ok=True)
            
            # Create connector modules based on transformation checklist
            connectors = ["git", "markdown", "ide", "filesystem"]
            
            for connector in connectors:
                connector_path = src_path / f"{connector}_connector.py"
                
                connector_template = f'''"""
{connector.title()} Workspace Connector

Connects Cognitron to {connector} workspace data.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path


class {connector.title()}Connector(ABC):
    """Base connector for {connector} integration."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """Validate connector configuration."""
        pass
    
    @abstractmethod
    async def index_content(self) -> List[Dict[str, Any]]:
        """Index content from {connector} source."""
        pass
    
    @abstractmethod
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Search indexed content."""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get connector status."""
        pass


class {connector.title()}ConnectorImpl({connector.title()}Connector):
    """Implementation of {connector} connector."""
    
    def _validate_config(self) -> None:
        """Validate {connector} specific configuration."""
        # TODO: Implement validation logic
        pass
    
    async def index_content(self) -> List[Dict[str, Any]]:
        """Index content from {connector}."""
        # TODO: Implement indexing logic
        return []
    
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Search {connector} content.""" 
        # TODO: Implement search logic
        return []
    
    def get_status(self) -> Dict[str, Any]:
        """Get {connector} connector status."""
        return {{
            "connector": "{connector}",
            "status": "not_implemented",
            "indexed_items": 0
        }}
'''
                connector_path.write_text(connector_template)
            
            # Create package __init__.py
            init_content = '''"""
Cognitron Workspace Connectors Package

Provides connectors to various workspace data sources including:
- Git repositories (with history and branch analysis)
- Markdown/note files (with Obsidian-style links)
- IDE integration (VSCode, current files)
- Filesystem watching and indexing
"""

__version__ = "0.1.0"

from .git_connector import GitConnectorImpl
from .markdown_connector import MarkdownConnectorImpl  
from .ide_connector import IdeConnectorImpl
from .filesystem_connector import FilesystemConnectorImpl

__all__ = [
    "GitConnectorImpl",
    "MarkdownConnectorImpl",
    "IdeConnectorImpl", 
    "FilesystemConnectorImpl"
]
'''
            (src_path / "__init__.py").write_text(init_content)
        
        print("✓ Workspace connectors package created")
    
    def migrate_test_files(self) -> None:
        """Migrate test files to appropriate packages."""
        print("Migrating test files...")
        
        if not self.dry_run:
            # Move test files to tools/test for now
            test_tools_path = self.source_dir / "tools" / "test"
            test_tools_path.mkdir(parents=True, exist_ok=True)
            
            # Move all test files
            for test_file in self.source_dir.glob("test_*.py"):
                shutil.move(str(test_file), str(test_tools_path / test_file.name))
            
            # Move test knowledge
            test_knowledge_src = self.source_dir / "test_knowledge"
            if test_knowledge_src.exists():
                shutil.move(str(test_knowledge_src), str(test_tools_path / "test_knowledge"))
        
        print("✓ Test files migrated")
    
    def migrate_scripts(self) -> None:
        """Migrate utility scripts."""
        print("Migrating utility scripts...")
        
        if not self.dry_run:
            scripts_path = self.source_dir / "scripts"
            scripts_path.mkdir(exist_ok=True)
            
            # Move utility scripts
            utility_scripts = ["approve.py", "transform_to_developer.py"]
            for script in utility_scripts:
                script_path = self.source_dir / script
                if script_path.exists():
                    shutil.move(str(script_path), str(scripts_path / script))
        
        print("✓ Utility scripts migrated")
    
    def create_root_package_json(self) -> None:
        """Create root package.json for monorepo management."""
        print("Creating root package.json...")
        
        package_json = {
            "name": "cognitron-monorepo",
            "version": "0.1.0", 
            "description": "Cognitron Knowledge Management System - Monorepo",
            "private": True,
            "workspaces": [
                "packages/*",
                "apps/*"
            ],
            "scripts": {
                "build": "python scripts/build_all.py",
                "test": "python scripts/test_all.py", 
                "lint": "python scripts/lint_all.py",
                "format": "python scripts/format_all.py",
                "install": "python scripts/install_all.py",
                "clean": "python scripts/clean_all.py",
                "migrate": "python scripts/migrate_to_monorepo.py"
            },
            "devDependencies": {},
            "engines": {
                "python": ">=3.11"
            }
        }
        
        if not self.dry_run:
            with open(self.source_dir / "package.json", "w") as f:
                json.dump(package_json, f, indent=2)
        
        print("✓ Root package.json created")
    
    def run_migration(self) -> None:
        """Execute the complete migration."""
        print("🚀 Starting Cognitron Monorepo Migration...")
        print(f"Source: {self.source_dir}")
        print(f"Dry run: {self.dry_run}")
        print()
        
        try:
            # Phase 1: Backup and prepare
            self.create_backup()
            
            # Phase 2: Create structure
            self.create_monorepo_structure()
            
            # Phase 3: Migrate packages
            self.migrate_core_package()
            self.migrate_temporal_package()
            self.migrate_indexing_package() 
            self.migrate_cli_package()
            self.create_workspace_connectors_package()
            
            # Phase 4: Migrate supporting files
            self.migrate_test_files()
            self.migrate_scripts()
            
            # Phase 5: Create management files
            self.create_root_package_json()
            
            print()
            print("✅ Migration completed successfully!")
            print(f"Backup available at: {self.backup_dir}")
            
            if not self.dry_run:
                print("\nNext steps:")
                print("1. Run 'python scripts/create_package_configs.py' to generate pyproject.toml files")
                print("2. Run 'python scripts/setup_ci_cd.py' to create CI/CD configurations")
                print("3. Run 'python scripts/install_all.py' to install all packages")
                print("4. Run 'python scripts/test_all.py' to validate migration")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            if not self.dry_run and self.backup_dir.exists():
                print(f"Restore from backup at: {self.backup_dir}")
            raise


def main():
    """Main migration entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate Cognitron to monorepo structure")
    parser.add_argument("--source", type=Path, default=Path.cwd(),
                       help="Source directory (default: current directory)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done without making changes")
    parser.add_argument("--force", action="store_true",
                       help="Force migration even if target structure exists")
    
    args = parser.parse_args()
    
    if not args.force:
        # Check if already looks like a monorepo
        if (args.source / "packages").exists():
            print("❌ Target already appears to be a monorepo structure")
            print("Use --force to override")
            sys.exit(1)
    
    migrator = MonorepoMigrator(args.source, dry_run=args.dry_run)
    migrator.run_migration()


if __name__ == "__main__":
    main()