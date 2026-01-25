#!/usr/bin/env python3
"""
Install All Packages Script

Installs all packages in the monorepo in the correct dependency order,
with support for development mode and editable installs.
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional


class MonorepoInstaller:
    """Handles installation of all packages in correct dependency order."""
    
    def __init__(self, root_dir: Path, dev_mode: bool = False, editable: bool = True):
        self.root_dir = Path(root_dir)
        self.packages_dir = self.root_dir / "packages"
        self.dev_mode = dev_mode
        self.editable = editable
        
        # Install order based on dependencies
        self.install_order = [
            "cognitron-core",        # Base package
            "cognitron-temporal",    # Depends on core
            "cognitron-indexing",    # Depends on core  
            "cognitron-connectors",  # Depends on core
            "cognitron-cli"          # Depends on all above
        ]
        
        self.install_results = {}
    
    def run_command(self, command: List[str], cwd: Path = None) -> Dict[str, Any]:
        """Run a command and capture the result."""
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
    
    def install_package(self, package_name: str) -> bool:
        """Install a single package."""
        package_dir = self.packages_dir / package_name
        
        if not package_dir.exists():
            print(f"❌ Package directory not found: {package_name}")
            return False
        
        print(f"📦 Installing {package_name}...")
        
        # Build pip install command
        if self.editable:
            # Install in editable mode
            install_cmd = ["pip", "install", "-e", str(package_dir)]
        else:
            # Install normally
            install_cmd = ["pip", "install", str(package_dir)]
        
        # Add dev dependencies if in dev mode
        if self.dev_mode:
            install_cmd.extend(["[dev]"])
        
        # Run installation
        result = self.run_command(install_cmd)
        
        if result["success"]:
            print(f"✅ Successfully installed {package_name} in {result['execution_time']:.2f}s")
            self.install_results[package_name] = {
                "success": True,
                "execution_time": result["execution_time"]
            }
            return True
        else:
            print(f"❌ Failed to install {package_name}")
            print(f"Error: {result['stderr']}")
            self.install_results[package_name] = {
                "success": False,
                "error": result["stderr"],
                "execution_time": result["execution_time"]
            }
            return False
    
    def check_dependencies(self) -> bool:
        """Check that required system dependencies are available."""
        print("🔍 Checking system dependencies...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 11):
            print(f"❌ Python 3.11+ required, found {python_version.major}.{python_version.minor}")
            return False
        
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check pip
        pip_result = self.run_command(["pip", "--version"])
        if not pip_result["success"]:
            print("❌ pip not found")
            return False
        
        print("✅ pip available")
        
        # Check build tools
        build_result = self.run_command(["pip", "show", "build"])
        if not build_result["success"]:
            print("⚠️ build package not found, installing...")
            install_result = self.run_command(["pip", "install", "build"])
            if not install_result["success"]:
                print("❌ Failed to install build package")
                return False
        
        print("✅ Build tools available")
        return True
    
    def create_virtual_environment(self, venv_path: Path) -> bool:
        """Create a virtual environment if requested."""
        print(f"🔧 Creating virtual environment at {venv_path}...")
        
        result = self.run_command(["python", "-m", "venv", str(venv_path)])
        
        if result["success"]:
            print(f"✅ Virtual environment created")
            return True
        else:
            print(f"❌ Failed to create virtual environment: {result['stderr']}")
            return False
    
    def install_all(self) -> bool:
        """Install all packages in dependency order."""
        print("🚀 Starting Cognitron monorepo installation...")
        print(f"Mode: {'Development' if self.dev_mode else 'Production'}")
        print(f"Editable: {self.editable}")
        print(f"Install order: {' → '.join(self.install_order)}")
        print()
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        # Install each package
        all_success = True
        for package_name in self.install_order:
            success = self.install_package(package_name)
            if not success:
                all_success = False
                break
        
        # Install root package if it exists
        root_pyproject = self.root_dir / "pyproject.toml"
        if root_pyproject.exists():
            print("📦 Installing root package...")
            if self.editable:
                install_cmd = ["pip", "install", "-e", str(self.root_dir)]
            else:
                install_cmd = ["pip", "install", str(self.root_dir)]
            
            if self.dev_mode:
                install_cmd.extend(["[dev]"])
            
            result = self.run_command(install_cmd)
            if result["success"]:
                print("✅ Root package installed")
            else:
                print(f"❌ Failed to install root package: {result['stderr']}")
                all_success = False
        
        # Generate installation report
        self.generate_install_report(all_success)
        
        if all_success:
            print("\n🎉 All packages installed successfully!")
            print("\nYou can now use:")
            print("  cognitron --help")
        else:
            print("\n💥 Installation failed - check errors above")
        
        return all_success
    
    def generate_install_report(self, overall_success: bool) -> None:
        """Generate installation report."""
        total_time = sum(r.get("execution_time", 0) for r in self.install_results.values())
        
        print("\n" + "="*60)
        print("📊 INSTALLATION SUMMARY")
        print("="*60)
        print(f"Overall success: {'✅' if overall_success else '❌'}")
        print(f"Total installation time: {total_time:.2f}s")
        print(f"Packages installed: {len([r for r in self.install_results.values() if r['success']])}/{len(self.install_results)}")
        
        if not overall_success:
            failed_packages = [pkg for pkg, result in self.install_results.items() if not result["success"]]
            print(f"\n❌ FAILED PACKAGES:")
            for pkg in failed_packages:
                error = self.install_results[pkg].get("error", "Unknown error")
                print(f"  - {pkg}: {error}")


def main():
    """Main installer entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Install all Cognitron packages")
    parser.add_argument("--root", type=Path, default=Path.cwd(),
                       help="Root directory (default: current directory)")
    parser.add_argument("--dev", action="store_true",
                       help="Install development dependencies")
    parser.add_argument("--no-editable", action="store_true",
                       help="Install in non-editable mode")
    parser.add_argument("--venv", type=Path,
                       help="Create virtual environment at specified path")
    parser.add_argument("--upgrade", action="store_true",
                       help="Upgrade packages if already installed")
    
    args = parser.parse_args()
    
    # Create virtual environment if requested
    if args.venv:
        installer = MonorepoInstaller(args.root, dev_mode=args.dev)
        if not installer.create_virtual_environment(args.venv):
            sys.exit(1)
        
        print(f"\n🔧 To activate virtual environment:")
        print(f"source {args.venv}/bin/activate  # On Unix/macOS")
        print(f"{args.venv}\\Scripts\\activate.bat  # On Windows")
        print("\nThen run this script again to install packages.")
        sys.exit(0)
    
    # Install packages
    installer = MonorepoInstaller(
        root_dir=args.root,
        dev_mode=args.dev,
        editable=not args.no_editable
    )
    
    success = installer.install_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()