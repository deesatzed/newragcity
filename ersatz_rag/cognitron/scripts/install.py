#!/usr/bin/env python3
"""
Cognitron Cross-Platform Installation Script
Medical-Grade Personal Knowledge Assistant
Version: 1.0.0
"""

import os
import sys
import subprocess
import platform
import shutil
import json
import tempfile
import zipfile
import tarfile
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError
import argparse
import logging
from typing import List, Optional, Dict, Any
import venv
import site

# =============================================================================
# Configuration and Constants
# =============================================================================

SCRIPT_VERSION = "1.0.0"
COGNITRON_VERSION = os.environ.get("COGNITRON_VERSION", "1.0.0")
PYTHON_MIN_VERSION = (3, 11)
PYPI_PACKAGE = "cognitron"
GITHUB_REPO = "https://github.com/cognitron-ai/cognitron"

# Platform detection
PLATFORM = platform.system().lower()
ARCHITECTURE = platform.machine().lower()
IS_WINDOWS = PLATFORM == "windows"
IS_MACOS = PLATFORM == "darwin"
IS_LINUX = PLATFORM == "linux"

# Default installation paths
if IS_WINDOWS:
    DEFAULT_INSTALL_DIR = Path.home() / "AppData" / "Local" / "Cognitron"
else:
    DEFAULT_INSTALL_DIR = Path.home() / ".cognitron"

# =============================================================================
# Color Output and Logging
# =============================================================================

class Colors:
    """ANSI color codes for terminal output."""
    
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    GRAY = '\033[0;37m'
    NC = '\033[0m'  # No Color
    
    @classmethod
    def disable(cls):
        """Disable colors for non-terminal output."""
        for attr in dir(cls):
            if not attr.startswith('_') and attr != 'disable':
                setattr(cls, attr, '')

# Disable colors if not outputting to a terminal
if not sys.stdout.isatty():
    Colors.disable()

def setup_logging(log_file: Path, verbose: bool = False) -> logging.Logger:
    """Setup logging configuration."""
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout) if verbose else logging.NullHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def print_header():
    """Print installation header."""
    if not sys.stdout.isatty():
        return
    
    os.system('clear' if not IS_WINDOWS else 'cls')
    print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗")
    print(f"║                                                                              ║")
    print(f"║   🧠 COGNITRON INSTALLER                                                     ║")
    print(f"║   Medical-Grade Personal Knowledge Assistant                                 ║")
    print(f"║                                                                              ║")
    print(f"║   Version: {COGNITRON_VERSION:<10}                                                       ║")
    print(f"║   Platform: {PLATFORM.title()} {ARCHITECTURE:<20}                                        ║")
    print(f"║                                                                              ║")
    print(f"╚══════════════════════════════════════════════════════════════════════════════╝{Colors.NC}\n")

def print_step(message: str):
    """Print step message."""
    print(f"{Colors.BLUE}[STEP]{Colors.NC} {message}")

def print_success(message: str):
    """Print success message."""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def print_warning(message: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def print_error(message: str):
    """Print error message."""
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}", file=sys.stderr)

def print_info(message: str):
    """Print info message."""
    print(f"{Colors.WHITE}[INFO]{Colors.NC} {message}")

def ask_yes_no(prompt: str, default: str = "y") -> bool:
    """Ask yes/no question with default."""
    suffix = " [Y/n]: " if default.lower() == "y" else " [y/N]: "
    
    while True:
        try:
            response = input(f"{Colors.YELLOW}{prompt}{suffix}{Colors.NC}").strip()
            if not response:
                response = default
            
            if response.lower() in ['y', 'yes']:
                return True
            elif response.lower() in ['n', 'no']:
                return False
            else:
                print(f"{Colors.RED}Please answer yes or no.{Colors.NC}")
        except KeyboardInterrupt:
            print("\nInstallation cancelled by user.")
            sys.exit(130)
        except EOFError:
            return default.lower() == "y"

# =============================================================================
# System Detection and Requirements
# =============================================================================

class SystemInfo:
    """System information and capabilities."""
    
    def __init__(self):
        self.platform = PLATFORM
        self.architecture = ARCHITECTURE
        self.python_version = sys.version_info
        self.python_executable = sys.executable
        self.is_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        # Detect OS distribution
        self.os_name = self._detect_os_name()
        self.os_version = self._detect_os_version()
        
    def _detect_os_name(self) -> str:
        """Detect OS distribution name."""
        if IS_WINDOWS:
            return "Windows"
        elif IS_MACOS:
            return "macOS"
        elif IS_LINUX:
            try:
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("ID="):
                            return line.split("=")[1].strip().strip('"')
            except FileNotFoundError:
                pass
            return "Linux"
        else:
            return platform.system()
    
    def _detect_os_version(self) -> str:
        """Detect OS version."""
        if IS_WINDOWS:
            return platform.version()
        elif IS_MACOS:
            return platform.mac_ver()[0]
        elif IS_LINUX:
            try:
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("VERSION_ID="):
                            return line.split("=")[1].strip().strip('"')
            except FileNotFoundError:
                pass
            return platform.release()
        else:
            return platform.release()

def check_python_version() -> bool:
    """Check if Python version meets requirements."""
    print_step("Checking Python version")
    
    current_version = sys.version_info[:2]
    if current_version < PYTHON_MIN_VERSION:
        print_error(f"Python {PYTHON_MIN_VERSION[0]}.{PYTHON_MIN_VERSION[1]}+ required. Current: {current_version[0]}.{current_version[1]}")
        return False
    
    print_success(f"Python {current_version[0]}.{current_version[1]} meets requirements")
    return True

def check_system_dependencies() -> bool:
    """Check system dependencies."""
    print_step("Checking system dependencies")
    
    missing_deps = []
    
    # Check for required commands
    required_commands = ["git"]
    if not IS_WINDOWS:
        required_commands.extend(["gcc", "make"])
    
    for cmd in required_commands:
        if not shutil.which(cmd):
            missing_deps.append(cmd)
    
    if missing_deps:
        print_warning(f"Missing dependencies: {', '.join(missing_deps)}")
        
        if ask_yes_no("Install missing dependencies?"):
            return install_system_dependencies(missing_deps)
        else:
            print_error("Dependencies are required for installation")
            return False
    
    print_success("All system dependencies are available")
    return True

def install_system_dependencies(deps: List[str]) -> bool:
    """Install system dependencies."""
    print_step(f"Installing system dependencies: {', '.join(deps)}")
    
    system_info = SystemInfo()
    
    try:
        if IS_MACOS:
            # Try Homebrew first
            if shutil.which("brew"):
                subprocess.run(["brew", "install"] + deps, check=True)
            else:
                print_error("Homebrew is required to install dependencies on macOS")
                print_info("Install Homebrew from: https://brew.sh/")
                return False
                
        elif IS_LINUX:
            if system_info.os_name in ["ubuntu", "debian"]:
                # Map dependencies to Ubuntu/Debian packages
                pkg_map = {"gcc": "build-essential", "make": "build-essential"}
                packages = [pkg_map.get(dep, dep) for dep in deps]
                packages = list(set(packages))  # Remove duplicates
                
                subprocess.run(["sudo", "apt", "update"], check=True)
                subprocess.run(["sudo", "apt", "install", "-y"] + packages, check=True)
                
            elif system_info.os_name in ["centos", "rhel", "fedora"]:
                pkg_manager = "dnf" if shutil.which("dnf") else "yum"
                pkg_map = {"gcc": "gcc", "make": "make", "git": "git"}
                packages = [pkg_map.get(dep, dep) for dep in deps]
                
                subprocess.run(["sudo", pkg_manager, "install", "-y"] + packages, check=True)
            else:
                print_error(f"Cannot automatically install dependencies for {system_info.os_name}")
                print_info(f"Please install manually: {', '.join(deps)}")
                return False
                
        elif IS_WINDOWS:
            print_error("Automatic dependency installation not supported on Windows")
            print_info("Please install dependencies manually:")
            for dep in deps:
                if dep == "git":
                    print_info("  Git: https://git-scm.com/download/win")
            return False
        
        print_success("System dependencies installed")
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        return False

# =============================================================================
# Installation Functions
# =============================================================================

class CognitronInstaller:
    """Main installer class."""
    
    def __init__(self, install_dir: Path, force: bool = False, quiet: bool = False):
        self.install_dir = Path(install_dir)
        self.force = force
        self.quiet = quiet
        
        # Derived paths
        self.venv_dir = self.install_dir / "venv"
        self.data_dir = self.install_dir / "data"
        self.logs_dir = self.install_dir / "logs"
        self.config_dir = self.install_dir / "config"
        self.cache_dir = self.install_dir / "cache"
        
        # Virtual environment executables
        if IS_WINDOWS:
            self.venv_python = self.venv_dir / "Scripts" / "python.exe"
            self.venv_pip = self.venv_dir / "Scripts" / "pip.exe"
            self.cognitron_exe = self.venv_dir / "Scripts" / "cognitron.exe"
        else:
            self.venv_python = self.venv_dir / "bin" / "python"
            self.venv_pip = self.venv_dir / "bin" / "pip"
            self.cognitron_exe = self.venv_dir / "bin" / "cognitron"
        
        # Setup logging
        self.log_file = self.logs_dir / "install.log"
        self.logger = setup_logging(self.log_file)
    
    def create_directories(self):
        """Create installation directories."""
        print_step("Setting up installation directories")
        
        directories = [
            self.install_dir,
            self.data_dir,
            self.logs_dir,
            self.config_dir,
            self.cache_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created directory: {directory}")
        
        # Set secure permissions on Unix-like systems
        if not IS_WINDOWS:
            os.chmod(self.install_dir, 0o755)
            os.chmod(self.data_dir, 0o750)
            os.chmod(self.logs_dir, 0o750)
            os.chmod(self.config_dir, 0o750)
            os.chmod(self.cache_dir, 0o755)
        
        print_success(f"Installation directories created: {self.install_dir}")
    
    def create_virtual_environment(self):
        """Create Python virtual environment."""
        print_step("Creating Python virtual environment")
        
        if self.venv_dir.exists():
            if self.force or ask_yes_no("Virtual environment exists. Remove and recreate?"):
                shutil.rmtree(self.venv_dir)
            else:
                print_info("Using existing virtual environment")
                return
        
        # Create virtual environment
        venv.create(self.venv_dir, with_pip=True, upgrade_deps=True)
        
        # Verify creation
        if not self.venv_python.exists():
            raise RuntimeError("Failed to create virtual environment")
        
        print_success("Virtual environment created")
    
    def install_cognitron(self):
        """Install Cognitron package."""
        print_step(f"Installing Cognitron {COGNITRON_VERSION}")
        
        # Upgrade pip first
        subprocess.run([
            str(self.venv_python), "-m", "pip", "install", 
            "--upgrade", "pip", "setuptools", "wheel"
        ], check=True)
        
        # Install Cognitron
        dev_path = os.environ.get("COGNITRON_DEV")
        if dev_path:
            print_info("Installing development version from source")
            subprocess.run([
                str(self.venv_pip), "install", "-e", f"{dev_path}[dev]"
            ], check=True)
        else:
            print_info("Installing from PyPI")
            subprocess.run([
                str(self.venv_pip), "install", f"{PYPI_PACKAGE}=={COGNITRON_VERSION}"
            ], check=True)
        
        print_success("Cognitron installed successfully")
    
    def create_configuration(self):
        """Create default configuration files."""
        print_step("Creating default configuration")
        
        config_file = self.config_dir / "config.yaml"
        
        if config_file.exists() and not self.force:
            if not ask_yes_no("Configuration exists. Overwrite?"):
                return
        
        config_content = """# Cognitron Medical-Grade Configuration
# Version: 1.0.0

# Medical-Grade Quality Thresholds
confidence:
  critical_threshold: 0.95      # Critical decisions (medical-grade)
  production_threshold: 0.85    # Production use
  display_threshold: 0.70       # Display minimum
  storage_threshold: 0.85       # Case memory storage

# Processing Configuration
processing:
  max_context_length: 4000      # Maximum context per query
  chunk_overlap: 200            # Text chunking overlap
  parallel_processing: true     # Enable parallel processing
  cache_enabled: true           # Enable response caching
  local_processing_only: true   # Force local processing

# Privacy and Security
privacy:
  encrypt_storage: true         # Encrypt stored data
  audit_logging: true           # Enable audit trails
  anonymize_logs: true          # Anonymize log entries
  data_retention_days: 90       # Data retention period

# Performance Tuning
performance:
  max_memory_usage: "2GB"       # Memory limit
  index_compression: true       # Compress search indices
  background_indexing: true     # Index in background
  cache_size: "500MB"          # Response cache size

# Monitoring and Health
monitoring:
  enable_metrics: true          # Prometheus metrics
  health_checks: true          # Health check endpoints
  log_level: "INFO"            # Logging level
  log_format: "structured"     # Log format

# LLM Provider Configuration (optional)
llm:
  primary_provider: "openai"    # Primary LLM provider
  fallback_providers: []       # Fallback providers
  
  providers:
    openai:
      model: "gpt-4"
      confidence_tracking: true
    
    google:
      model: "gemini-pro" 
      confidence_tracking: true
"""
        
        config_file.write_text(config_content)
        print_success(f"Configuration created: {config_file}")
    
    def setup_shell_integration(self):
        """Setup shell integration."""
        if IS_WINDOWS:
            self._setup_windows_integration()
        else:
            self._setup_unix_shell_integration()
    
    def _setup_windows_integration(self):
        """Setup Windows integration."""
        print_step("Setting up Windows integration")
        
        # Add to PATH via registry (requires admin) or user environment
        scripts_dir = self.venv_dir / "Scripts"
        
        try:
            # Try to add to user PATH
            import winreg
            
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS) as key:
                try:
                    current_path, _ = winreg.QueryValueEx(key, "PATH")
                except FileNotFoundError:
                    current_path = ""
                
                if str(scripts_dir) not in current_path:
                    new_path = f"{scripts_dir};{current_path}".rstrip(';')
                    winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                    print_success("Added Cognitron to user PATH")
                else:
                    print_info("Cognitron already in PATH")
            
        except ImportError:
            print_warning("Cannot automatically add to PATH on this system")
            print_info(f"Please add {scripts_dir} to your PATH manually")
    
    def _setup_unix_shell_integration(self):
        """Setup Unix shell integration."""
        print_step("Setting up shell integration")
        
        shell = os.environ.get("SHELL", "/bin/bash")
        shell_name = Path(shell).name
        
        # Determine profile file
        profile_file = None
        if shell_name == "bash":
            profile_file = Path.home() / ".bash_profile"
            if not profile_file.exists():
                profile_file = Path.home() / ".bashrc"
        elif shell_name == "zsh":
            profile_file = Path.home() / ".zshrc"
        elif shell_name == "fish":
            profile_file = Path.home() / ".config" / "fish" / "config.fish"
        
        if profile_file:
            integration_code = f"""
# Cognitron Medical-Grade Personal Knowledge Assistant
export COGNITRON_HOME="{self.install_dir}"
export PATH="{self.venv_dir}/bin:$PATH"

# Cognitron aliases
alias cognitron="{self.cognitron_exe}"
alias cgn="{self.cognitron_exe}"
"""
            
            # Check if already configured
            if profile_file.exists() and "COGNITRON_HOME" in profile_file.read_text():
                print_info("Shell integration already configured")
                return
            
            # Add integration
            profile_file.parent.mkdir(parents=True, exist_ok=True)
            with profile_file.open("a") as f:
                f.write(integration_code)
            
            print_success(f"Shell integration added to {profile_file}")
    
    def create_desktop_integration(self):
        """Create desktop integration (Linux only)."""
        if not IS_LINUX:
            return
        
        print_step("Creating desktop integration")
        
        desktop_file = Path.home() / ".local" / "share" / "applications" / "cognitron.desktop"
        desktop_file.parent.mkdir(parents=True, exist_ok=True)
        
        desktop_content = f"""[Desktop Entry]
Version=1.0
Name=Cognitron
Comment=Medical-Grade Personal Knowledge Assistant
Exec={self.cognitron_exe} gui
Icon={self.install_dir}/icon.png
Terminal=false
Type=Application
Categories=Office;Education;Science;
StartupNotify=true
MimeType=text/plain;text/markdown;application/pdf;
Keywords=ai;knowledge;assistant;medical;confidence;
"""
        
        desktop_file.write_text(desktop_content)
        desktop_file.chmod(0o755)
        
        print_success(f"Desktop entry created: {desktop_file}")
    
    def run_post_install_setup(self):
        """Run post-installation setup."""
        print_step("Running post-installation setup")
        
        try:
            # Initialize Cognitron
            subprocess.run([
                str(self.cognitron_exe), "setup",
                "--data-dir", str(self.data_dir),
                "--config-dir", str(self.config_dir)
            ], check=True, capture_output=True, text=True)
            
            # Run health check
            result = subprocess.run([
                str(self.cognitron_exe), "health-check", "--quiet"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print_success("Cognitron health check passed")
            else:
                print_warning("Cognitron health check failed - check configuration")
                
        except subprocess.CalledProcessError as e:
            print_warning(f"Post-installation setup warning: {e}")
        
        print_success("Post-installation setup completed")
    
    def configure_api_keys(self):
        """Configure API keys interactively."""
        if self.quiet:
            return
        
        print_step("Configuring API keys (optional)")
        
        if not ask_yes_no("Configure API keys for enhanced confidence tracking?"):
            return
        
        env_file = self.install_dir / ".env"
        env_content = ["# Cognitron API Keys", f"# Generated: {__import__('datetime').datetime.now()}", ""]
        
        # OpenAI API Key
        if ask_yes_no("Configure OpenAI API key?"):
            import getpass
            openai_key = getpass.getpass("Enter OpenAI API key: ")
            if openai_key:
                env_content.append(f"OPENAI_API_KEY={openai_key}")
                print_success("OpenAI API key configured")
        
        # Google API Key
        if ask_yes_no("Configure Google Gemini API key?"):
            import getpass
            google_key = getpass.getpass("Enter Google API key: ")
            if google_key:
                env_content.append(f"GOOGLE_API_KEY={google_key}")
                print_success("Google API key configured")
        
        # Write environment file
        env_file.write_text("\n".join(env_content))
        
        # Set secure permissions
        if not IS_WINDOWS:
            env_file.chmod(0o600)
    
    def configure_knowledge_indexing(self):
        """Configure initial knowledge indexing."""
        if self.quiet:
            return
        
        print_step("Configuring knowledge indexing")
        
        if not ask_yes_no("Index your knowledge base now?"):
            return
        
        # Default paths to check
        default_paths = [
            Path.home() / "Documents",
            Path.home() / "code",
            Path.home() / "projects",
            Path.home() / "notes"
        ]
        
        index_paths = []
        
        print_info("Select directories to index:")
        for path in default_paths:
            if path.exists() and ask_yes_no(f"Index {path}?"):
                index_paths.append(str(path))
        
        # Custom paths
        while ask_yes_no("Add custom directory?"):
            custom_path = input("Enter directory path: ").strip()
            if custom_path and Path(custom_path).exists():
                index_paths.append(custom_path)
            else:
                print_warning(f"Directory does not exist: {custom_path}")
        
        if index_paths:
            print_info(f"Indexing directories: {', '.join(index_paths)}")
            try:
                subprocess.run([
                    str(self.cognitron_exe), "index"
                ] + index_paths + ["--verbose"], check=True)
                print_success("Knowledge indexing completed")
            except subprocess.CalledProcessError:
                print_warning("Knowledge indexing failed")
    
    def install(self):
        """Run complete installation."""
        try:
            self.create_directories()
            self.create_virtual_environment()
            self.install_cognitron()
            self.create_configuration()
            self.setup_shell_integration()
            self.create_desktop_integration()
            self.run_post_install_setup()
            
            # Interactive configuration
            self.configure_api_keys()
            self.configure_knowledge_indexing()
            
            self._print_success_message()
            
        except Exception as e:
            print_error(f"Installation failed: {e}")
            self.logger.exception("Installation failed")
            sys.exit(1)
    
    def _print_success_message(self):
        """Print installation success message."""
        print(f"\n{Colors.GREEN}╔══════════════════════════════════════════════════════════════════════════════╗")
        print(f"║  🎉 COGNITRON INSTALLATION COMPLETED SUCCESSFULLY!                          ║")
        print(f"╚══════════════════════════════════════════════════════════════════════════════╝{Colors.NC}\n")
        
        print(f"{Colors.WHITE}Installation Details:{Colors.NC}")
        print(f"  📁 Install Directory: {self.install_dir}")
        print(f"  🐍 Python Version: {sys.version_info.major}.{sys.version_info.minor}")
        print(f"  🧠 Cognitron Version: {COGNITRON_VERSION}")
        print(f"  📋 Log File: {self.log_file}")
        
        print(f"\n{Colors.WHITE}Next Steps:{Colors.NC}")
        if IS_WINDOWS:
            print(f"  1. Restart Command Prompt/PowerShell")
        else:
            print(f"  1. Restart terminal or run: {Colors.CYAN}source ~/.bashrc{Colors.NC}")
        print(f"  2. Verify installation: {Colors.CYAN}cognitron --version{Colors.NC}")
        print(f"  3. Check system status: {Colors.CYAN}cognitron status{Colors.NC}")
        print(f"  4. Start using Cognitron: {Colors.CYAN}cognitron ask \"How does this work?\"{Colors.NC}")
        
        print(f"\n{Colors.WHITE}Documentation:{Colors.NC}")
        print(f"  📖 User Guide: https://docs.cognitron.ai")
        print(f"  💬 Community: https://discord.gg/cognitron")
        print(f"  🐛 Issues: https://github.com/cognitron-ai/cognitron/issues")
        
        print(f"\n{Colors.CYAN}Experience medical-grade AI reliability with Cognitron!{Colors.NC}\n")

# =============================================================================
# Uninstall and Update Functions
# =============================================================================

def uninstall_cognitron(install_dir: Path):
    """Uninstall Cognitron."""
    print_step("Uninstalling Cognitron")
    
    if not install_dir.exists():
        print_error(f"Cognitron installation not found at {install_dir}")
        sys.exit(1)
    
    print(f"{Colors.RED}WARNING: This will remove all Cognitron data and configuration{Colors.NC}")
    if not ask_yes_no("Are you sure you want to uninstall Cognitron?", "n"):
        print_info("Uninstall cancelled")
        sys.exit(0)
    
    # Remove installation directory
    shutil.rmtree(install_dir)
    
    # Clean up shell integration (basic cleanup)
    if not IS_WINDOWS:
        shell = os.environ.get("SHELL", "/bin/bash")
        shell_name = Path(shell).name
        
        profile_files = []
        if shell_name == "bash":
            profile_files = [Path.home() / ".bash_profile", Path.home() / ".bashrc"]
        elif shell_name == "zsh":
            profile_files = [Path.home() / ".zshrc"]
        
        for profile_file in profile_files:
            if profile_file.exists():
                content = profile_file.read_text()
                if "COGNITRON_HOME" in content:
                    print_info(f"Please manually remove Cognitron entries from {profile_file}")
    
    # Remove desktop entry
    if IS_LINUX:
        desktop_file = Path.home() / ".local" / "share" / "applications" / "cognitron.desktop"
        if desktop_file.exists():
            desktop_file.unlink()
    
    print_success("Cognitron uninstalled successfully")
    print_info("Please restart your terminal to complete the uninstall process")

def update_cognitron(install_dir: Path):
    """Update Cognitron installation."""
    print_step("Updating Cognitron")
    
    venv_dir = install_dir / "venv"
    if not venv_dir.exists():
        print_error("Cognitron installation not found. Please run installation first.")
        sys.exit(1)
    
    # Determine executable paths
    if IS_WINDOWS:
        venv_pip = venv_dir / "Scripts" / "pip.exe"
        cognitron_exe = venv_dir / "Scripts" / "cognitron.exe"
    else:
        venv_pip = venv_dir / "bin" / "pip"
        cognitron_exe = venv_dir / "bin" / "cognitron"
    
    # Check current version
    try:
        result = subprocess.run([str(cognitron_exe), "--version"], 
                              capture_output=True, text=True, check=True)
        current_version = result.stdout.strip().split()[-1]
        print_info(f"Current version: {current_version}")
    except subprocess.CalledProcessError:
        print_info("Current version: unknown")
    
    # Update package
    try:
        subprocess.run([str(venv_pip), "install", "--upgrade", PYPI_PACKAGE], check=True)
        
        # Check new version
        result = subprocess.run([str(cognitron_exe), "--version"], 
                              capture_output=True, text=True, check=True)
        new_version = result.stdout.strip().split()[-1]
        print_success(f"Updated to version: {new_version}")
        
        # Run migration if needed
        try:
            subprocess.run([str(cognitron_exe), "migrate", "--check-needed"], 
                         check=True, capture_output=True)
            print_step("Running migration")
            subprocess.run([str(cognitron_exe), "migrate", "--backup"], check=True)
            print_success("Migration completed")
        except subprocess.CalledProcessError:
            # Migration not needed or not available
            pass
            
    except subprocess.CalledProcessError as e:
        print_error(f"Update failed: {e}")
        sys.exit(1)

# =============================================================================
# Main Function and CLI
# =============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Cognitron Medical-Grade Personal Knowledge Assistant Installer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python install.py                              # Install Cognitron
  python install.py install --force              # Force installation
  python install.py update                       # Update existing installation
  python install.py uninstall                    # Remove Cognitron
  python install.py --install-dir /opt/cognitron # Custom install directory
        """
    )
    
    parser.add_argument(
        "action",
        choices=["install", "uninstall", "update", "help"],
        nargs="?",
        default="install",
        help="Action to perform (default: install)"
    )
    
    parser.add_argument(
        "--install-dir",
        type=Path,
        default=DEFAULT_INSTALL_DIR,
        help=f"Installation directory (default: {DEFAULT_INSTALL_DIR})"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force installation without prompts"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true", 
        help="Suppress interactive prompts"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"Cognitron Installer {SCRIPT_VERSION}"
    )
    
    args = parser.parse_args()
    
    if args.action == "help":
        parser.print_help()
        return
    
    # Check Python version first
    if not check_python_version():
        sys.exit(1)
    
    # Handle actions
    if args.action == "install":
        print_header()
        
        if not args.quiet and not check_system_dependencies():
            sys.exit(1)
        
        installer = CognitronInstaller(
            install_dir=args.install_dir,
            force=args.force,
            quiet=args.quiet
        )
        installer.install()
        
    elif args.action == "uninstall":
        uninstall_cognitron(args.install_dir)
        
    elif args.action == "update":
        update_cognitron(args.install_dir)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInstallation cancelled by user.")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)