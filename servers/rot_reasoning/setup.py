#!/usr/bin/env python3
"""
RoT Reasoning Server - Interactive Setup Script

This script provides a smooth onboarding experience:
1. System detection
2. LLM framework selection (auto-detect best option)
3. Model scanning and selection
4. Full installation with training dependencies
5. Validation and testing
6. Usage instructions
"""

import os
import sys
import platform
import subprocess
import json
from pathlib import Path
from typing import Optional, List, Dict, Tuple

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{text}{Colors.RESET}")
    print("=" * len(text))

def print_step(step_num: int, text: str):
    print(f"\n{Colors.CYAN}{Colors.BOLD}[Step {step_num}] {text}{Colors.RESET}")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def run_command(cmd: List[str], capture=True, check=True) -> Tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        if capture:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check
            )
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, check=check)
            return result.returncode, "", ""
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout if hasattr(e, 'stdout') else "", e.stderr if hasattr(e, 'stderr') else ""
    except FileNotFoundError:
        return -1, "", f"Command not found: {cmd[0]}"

def detect_system() -> Dict[str, any]:
    """Detect system information."""
    system_info = {
        'os': platform.system(),
        'arch': platform.machine(),
        'python_version': sys.version_info,
        'is_macos': platform.system() == 'Darwin',
        'is_arm': platform.machine() in ['arm64', 'aarch64'],
        'has_cuda': False,
        'has_mps': False,
    }

    # Check for CUDA
    returncode, stdout, _ = run_command(['nvidia-smi'], check=False)
    system_info['has_cuda'] = returncode == 0

    # Check for Apple Metal (MPS)
    if system_info['is_macos'] and system_info['is_arm']:
        system_info['has_mps'] = True

    return system_info

def check_disk_space() -> int:
    """Return available disk space in GB."""
    stat = os.statvfs('.')
    available_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
    return int(available_gb)

def detect_ollama_models() -> List[Dict[str, str]]:
    """Scan for Ollama models (multimodal only)."""
    returncode, stdout, _ = run_command(['ollama', 'list'], check=False)
    if returncode != 0:
        return []

    models = []
    multimodal_keywords = ['vision', 'vl', 'llava', 'qwen2-vl', 'phi3-vision', 'minicpm-v']

    for line in stdout.split('\n')[1:]:  # Skip header
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 1:
            model_name = parts[0]
            # Filter for multimodal models only
            if any(keyword in model_name.lower() for keyword in multimodal_keywords):
                models.append({
                    'framework': 'ollama',
                    'name': model_name,
                    'path': f'ollama:{model_name}'
                })

    return models

def detect_huggingface_models() -> List[Dict[str, str]]:
    """Scan HuggingFace cache for multimodal models."""
    hf_cache = Path.home() / '.cache' / 'huggingface' / 'hub'
    if not hf_cache.exists():
        return []

    models = []
    multimodal_patterns = ['qwen2-vl', 'qwen2.5-vl', 'llava', 'phi-3-vision', 'minicpm-v', 'deepseek-vl']

    for model_dir in hf_cache.iterdir():
        if model_dir.is_dir() and model_dir.name.startswith('models--'):
            model_name = model_dir.name.replace('models--', '').replace('--', '/')
            # Filter for multimodal models only
            if any(pattern in model_name.lower() for pattern in multimodal_patterns):
                models.append({
                    'framework': 'huggingface',
                    'name': model_name,
                    'path': model_name
                })

    return models

def detect_mlx_models() -> List[Dict[str, str]]:
    """Scan for MLX models (macOS only)."""
    mlx_cache = Path.home() / '.cache' / 'huggingface' / 'hub'
    if not mlx_cache.exists():
        return []

    models = []
    mlx_patterns = ['mlx', 'qwen2-vl', 'qwen2.5-vl', 'llava']

    for model_dir in mlx_cache.iterdir():
        if model_dir.is_dir() and model_dir.name.startswith('models--'):
            model_name = model_dir.name.replace('models--', '').replace('--', '/')
            # Filter for MLX-compatible multimodal models
            if any(pattern in model_name.lower() for pattern in mlx_patterns):
                models.append({
                    'framework': 'mlx',
                    'name': model_name,
                    'path': model_name
                })

    return models

def get_recommended_framework(system_info: Dict) -> str:
    """Determine recommended framework based on system."""
    if system_info['is_macos'] and system_info['is_arm']:
        return 'mlx'
    return 'ollama'

def prompt_choice(prompt: str, options: List[str], default: int = 1) -> int:
    """Prompt user to select from options."""
    print(f"\n{prompt}")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")

    while True:
        choice = input(f"\nYour choice [1-{len(options)}] (default: {default}): ").strip()
        if not choice:
            return default
        try:
            choice_int = int(choice)
            if 1 <= choice_int <= len(options):
                return choice_int
            print_error(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            print_error("Please enter a valid number")

def prompt_yes_no(prompt: str, default: bool = True) -> bool:
    """Prompt user for yes/no."""
    default_str = "Y/n" if default else "y/N"
    response = input(f"{prompt} [{default_str}]: ").strip().lower()
    if not response:
        return default
    return response in ['y', 'yes']

def prompt_path(prompt: str, default: str) -> str:
    """Prompt user for a path."""
    response = input(f"{prompt} (default: {default}): ").strip()
    if not response:
        return default
    return os.path.expanduser(response)

def install_preliminary_dependencies(debug: bool = False) -> bool:
    """Install minimal dependencies needed for setup script to run."""
    print_info("Installing preliminary dependencies...")
    print_info("This will install basic tools: fastmcp, PyYAML, requests")

    prelim_packages = ['fastmcp>=2.14.4', 'pyyaml', 'requests']

    if debug:
        print(f"  Debug: Installing packages: {', '.join(prelim_packages)}")

    returncode, stdout, stderr = run_command([
        sys.executable, '-m', 'pip', 'install', '--quiet'
    ] + prelim_packages, check=False)

    if returncode != 0:
        print_error(f"Failed to install preliminary dependencies: {stderr}")
        return False

    print_success("Preliminary dependencies installed")
    return True

def install_dependencies(framework: str, debug: bool = False):
    """Install all dependencies (full setup)."""
    print_info("Installing full setup (includes training dependencies)...")
    print_info("This may take 10-30 minutes depending on your connection.")

    install_steps = [
        "Installing core dependencies (PyTorch, Transformers, etc.)",
        "Installing training tools (DeepSpeed, accelerate)",
        f"Installing {framework}-specific packages"
    ]

    if debug:
        print("\n  Debug: Installation checklist:")
        for i, step in enumerate(install_steps, 1):
            print(f"  [{i}/{len(install_steps)}] {step}")
        print()

    # Check for uv
    returncode, _, _ = run_command(['uv', '--version'], check=False)
    has_uv = returncode == 0

    if has_uv:
        print_info("Using uv for fast installation...")
        if debug:
            print("  Debug: Running 'uv sync --all-extras'")
        returncode, stdout, stderr = run_command(['uv', 'sync', '--all-extras'], check=False)
        if returncode != 0:
            print_warning("uv sync failed, falling back to pip...")
            has_uv = False

    if not has_uv:
        if debug:
            print("  Debug: Using pip for installation")
            print(f"  Debug: Running 'pip install -r requirements.txt'")
        print_info("Using pip for installation...")
        returncode, stdout, stderr = run_command([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], check=False)
        if returncode != 0:
            print_error(f"Failed to install dependencies: {stderr}")
            return False

    # Install framework-specific packages
    framework_deps = {
        'mlx': ['mlx', 'mlx-lm'],
        'ollama': [],  # Ollama is standalone
        'vllm': ['vllm'],
        'huggingface': []  # Already in requirements.txt
    }

    if framework in framework_deps and framework_deps[framework]:
        print_info(f"Installing {framework}-specific packages...")
        if debug:
            print(f"  Debug: Installing {', '.join(framework_deps[framework])}")
        returncode, stdout, stderr = run_command([
            sys.executable, '-m', 'pip', 'install'
        ] + framework_deps[framework], check=False)
        if returncode != 0:
            print_warning(f"Some {framework} packages failed to install. Continuing anyway...")

    print_success("Dependencies installed")
    return True

def download_default_model(framework: str) -> str:
    """Download the default Qwen2.5-VL model."""
    print_info("Downloading default model: Qwen2.5-VL-7B-Instruct")
    print_info("This is a ~15GB download and may take 15-60 minutes...")

    if framework == 'ollama':
        print_info("Downloading via Ollama...")
        returncode, stdout, stderr = run_command([
            'ollama', 'pull', 'qwen2.5-vl:7b'
        ], capture=False, check=False)
        if returncode == 0:
            print_success("Model downloaded successfully")
            return 'ollama:qwen2.5-vl:7b'
        else:
            print_error("Failed to download via Ollama")
            return None

    elif framework == 'mlx':
        print_info("Downloading via HuggingFace (MLX format)...")
        returncode, stdout, stderr = run_command([
            sys.executable, '-c',
            "from huggingface_hub import snapshot_download; "
            "snapshot_download('Qwen/Qwen2.5-VL-7B-Instruct')"
        ], capture=False, check=False)
        if returncode == 0:
            print_success("Model downloaded successfully")
            return 'Qwen/Qwen2.5-VL-7B-Instruct'
        else:
            print_error("Failed to download model")
            return None

    else:  # huggingface or vllm
        print_info("Downloading via HuggingFace...")
        returncode, stdout, stderr = run_command([
            sys.executable, '-c',
            "from huggingface_hub import snapshot_download; "
            "snapshot_download('Qwen/Qwen2.5-VL-7B-Instruct')"
        ], capture=False, check=False)
        if returncode == 0:
            print_success("Model downloaded successfully")
            return 'Qwen/Qwen2.5-VL-7B-Instruct'
        else:
            print_error("Failed to download model")
            return None

def create_config(framework: str, model_path: str, data_folder: str):
    """Create configuration file."""
    config = {
        'framework': framework,
        'model_path': model_path,
        'data_folder': data_folder,
        'version': '0.2.0'
    }

    config_path = Path('config.yaml')
    with open(config_path, 'w') as f:
        for key, value in config.items():
            f.write(f"{key}: {value}\n")

    print_success(f"Configuration saved to {config_path}")

def run_tests():
    """Run validation tests."""
    print_info("Running validation tests...")

    # Test 1: MCP server import
    returncode, stdout, stderr = run_command([
        sys.executable, '-c', 'import sys; sys.path.insert(0, "src"); from rot_reasoning import server'
    ], check=False)
    if returncode == 0:
        print_success("MCP server imports successfully")
    else:
        print_error(f"MCP server import failed: {stderr}")
        return False

    # Test 2: Run basic test
    returncode, stdout, stderr = run_command([
        sys.executable, 'src/rot_reasoning.py', '--test'
    ], check=False)
    if returncode == 0 and 'Core tests passed' in stdout:
        print_success("Basic functionality tests passed")
    else:
        print_warning("Some tests failed, but server may still work")

    return True

def show_usage_instructions(framework: str, model_path: str, data_folder: str):
    """Show usage instructions."""
    print_header("Setup Complete!")

    print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 RoT Reasoning Server is ready to use!{Colors.RESET}\n")

    print_step(1, "Using with Claude Desktop (MCP)")
    print(f"""
Add this to your Claude Desktop config:
{Colors.YELLOW}
# macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
# Windows: %APPDATA%/Claude/claude_desktop_config.json

{{
  "mcpServers": {{
    "rot-reasoning": {{
      "command": "python",
      "args": ["{Path.cwd() / 'src' / 'rot_reasoning.py'}"],
      "env": {{
        "DATA_FOLDER": "{data_folder}",
        "MODEL_PATH": "{model_path}",
        "FRAMEWORK": "{framework}"
      }}
    }}
  }}
}}
{Colors.RESET}
After adding, restart Claude Desktop. You'll see RoT tools available in the chat.
""")

    print_step(2, "Using with Your Data")
    print(f"""
Your data folder: {Colors.CYAN}{data_folder}{Colors.RESET}

Supported document types:
  {Colors.GREEN}✓ Text Documents{Colors.RESET}: .txt, .md, .markdown, .rst
  {Colors.GREEN}✓ PDF Documents{Colors.RESET}: .pdf (with text extraction)
  {Colors.GREEN}✓ Office Documents{Colors.RESET}: .docx, .doc, .rtf
  {Colors.GREEN}✓ Images{Colors.RESET}: .png, .jpg, .jpeg, .webp (multimodal analysis)
  {Colors.GREEN}✓ Structured Data{Colors.RESET}: .json, .jsonl, .csv

Data folder location:
  Absolute path: {Colors.CYAN}{Path(data_folder).absolute()}{Colors.RESET}

To use your data:
  1. Copy documents to the data folder
  2. RoT will automatically index and compress them
  3. Query via Claude Desktop or Python API
  4. Documents are processed with 3-4× compression for efficiency
""")

    print_step(3, "Using with Chatbots (REST API)")
    print(f"""
RoT is an MCP server, but can be wrapped as a REST API for chatbot integration.

{Colors.YELLOW}Quick REST API wrapper example:{Colors.RESET}

Create {Colors.CYAN}rest_api_wrapper.py{Colors.RESET}:

{Colors.BLUE}
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
sys.path.insert(0, "src")
from rot_reasoning import _assess_complexity_impl, get_rot_compressor

app = FastAPI(title="RoT Reasoning API")

class QueryRequest(BaseModel):
    query: str
    context: list[str]
    max_tokens: int = 256

@app.post("/compress_and_generate")
async def compress_and_generate(req: QueryRequest):
    try:
        compressor = get_rot_compressor()
        result = await compressor.compress_and_generate(
            prompt=req.query,
            compressed_state=None,
            max_tokens=req.max_tokens
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/assess_complexity")
def assess_complexity(req: QueryRequest):
    return _assess_complexity_impl(req.query, req.context)

# Run: uvicorn rest_api_wrapper:app --reload --port 8000
{Colors.RESET}

Then integrate with your chatbot:
  {Colors.CYAN}POST http://localhost:8000/compress_and_generate{Colors.RESET}
  {Colors.CYAN}POST http://localhost:8000/assess_complexity{Colors.RESET}

For direct MCP integration:
  - Claude Desktop (native MCP support)
  - Any MCP-compatible client
  - Python API (see examples/example_usage.py)
""")

    print_step(4, "Testing and Examples")
    print(f"""
Run example usage:
  {Colors.CYAN}python examples/example_usage.py{Colors.RESET}

Run benchmarks:
  {Colors.CYAN}python benchmarks/run_benchmarks.py --quick-test{Colors.RESET}

Test with your own query:
  {Colors.CYAN}python src/rot_reasoning.py --query "Your question here"{Colors.RESET}
""")

    print_step(5, "Next Steps")
    print("""
To train a custom model:
  - See MODEL_TRAINING.md for detailed guide
  - Requires ~8-16 hours on GPU
  - Checkpoints will be saved to checkpoints/

Documentation:
  - QUICK_START.md - Tutorials and examples
  - BENCHMARK_PLAN.md - Evaluation and SOTA comparison
  - MODEL_SETUP.md - Advanced model configuration
  - TROUBLESHOOTING.md - Common issues and solutions
""")

    print(f"\n{Colors.BOLD}Happy reasoning! 🧠{Colors.RESET}\n")

def main(debug: bool = False):
    """Main setup workflow."""
    print_header("Welcome to RoT Reasoning Server Setup!")
    print("This interactive setup will guide you through installation.\n")

    # Step 0: Preliminary Installation (before questions)
    print_step(0, "Preliminary Setup")
    if not install_preliminary_dependencies(debug):
        print_error("Preliminary installation failed")
        sys.exit(1)

    # Step 1: System Check
    print_step(1, "System Check")
    system_info = detect_system()

    python_version = f"{system_info['python_version'].major}.{system_info['python_version'].minor}"
    print_success(f"Python {python_version} detected")

    if system_info['python_version'] < (3, 11):
        print_error("Python 3.11+ required. Please upgrade Python.")
        sys.exit(1)

    print_info(f"OS: {system_info['os']} ({system_info['arch']})")

    if system_info['has_cuda']:
        print_success("NVIDIA GPU detected (CUDA available)")
    elif system_info['has_mps']:
        print_success("Apple Silicon detected (Metal Performance Shaders available)")
    else:
        print_warning("No GPU detected. CPU-only mode (slower performance)")

    disk_space = check_disk_space()
    if disk_space < 50:
        print_error(f"Insufficient disk space: {disk_space}GB available, 50GB required")
        if not prompt_yes_no("Continue anyway?", default=False):
            sys.exit(1)
    else:
        print_success(f"Disk space: {disk_space}GB available")

    # Step 2: Framework Selection
    print_step(2, "LLM Framework Selection")
    recommended = get_recommended_framework(system_info)

    framework_options = []
    if system_info['is_macos'] and system_info['is_arm']:
        framework_options = [
            "MLX-LM (recommended for Apple Silicon - fastest on M1/M2/M3)",
            "Ollama (easy setup, good compatibility)",
            "HuggingFace Transformers (most flexible)",
        ]
        framework_map = ['mlx', 'ollama', 'huggingface']
    else:
        framework_options = [
            "Ollama (recommended - easiest setup, CPU/GPU)",
            "VLLM (production, GPU-only, fastest inference)",
            "HuggingFace Transformers (most flexible)",
        ]
        framework_map = ['ollama', 'vllm', 'huggingface']

    choice = prompt_choice("Which framework would you like to use?", framework_options, default=1)
    framework = framework_map[choice - 1]
    print_success(f"Selected framework: {framework}")

    # Step 3: Model Detection and Selection
    print_step(3, "Model Detection")
    print_info("Scanning for existing multimodal models...")

    existing_models = []
    if framework == 'ollama':
        existing_models.extend(detect_ollama_models())
    elif framework == 'mlx':
        existing_models.extend(detect_mlx_models())
    else:
        existing_models.extend(detect_huggingface_models())

    model_path = None
    if existing_models:
        print_success(f"Found {len(existing_models)} multimodal model(s)")
        model_options = [
            f"Use {m['name']} ({m['framework']})" for m in existing_models
        ]
        model_options.append("Download default: Qwen2.5-VL-7B-Instruct (recommended)")
        model_options.append("Skip model setup (configure later)")

        choice = prompt_choice("Select a model:", model_options, default=len(model_options) - 1)

        if choice <= len(existing_models):
            model_path = existing_models[choice - 1]['path']
            print_success(f"Using existing model: {model_path}")
        elif choice == len(model_options) - 1:
            print_info("Skipping model setup. You can configure it later in config.yaml")
            model_path = "NOT_CONFIGURED"
        else:
            model_path = download_default_model(framework)
            if not model_path:
                print_error("Model download failed")
                sys.exit(1)
    else:
        print_warning("No existing multimodal models found")
        if prompt_yes_no("Download default Qwen2.5-VL-7B-Instruct model?", default=True):
            model_path = download_default_model(framework)
            if not model_path:
                print_error("Model download failed")
                sys.exit(1)
        else:
            print_info("Skipping model setup")
            model_path = "NOT_CONFIGURED"

    # Step 4: Data Folder Setup
    print_step(4, "Data Folder Configuration")
    default_data_folder = str(Path.cwd() / 'data')
    print_info(f"Default data folder: {default_data_folder}")
    print_info("This folder will store your documents for RoT processing")

    print("\nSupported document types:")
    print(f"  {Colors.GREEN}✓{Colors.RESET} Text: .txt, .md, .markdown, .rst")
    print(f"  {Colors.GREEN}✓{Colors.RESET} PDF: .pdf (with text extraction)")
    print(f"  {Colors.GREEN}✓{Colors.RESET} Office: .docx, .doc, .rtf")
    print(f"  {Colors.GREEN}✓{Colors.RESET} Images: .png, .jpg, .jpeg, .webp (multimodal)")
    print(f"  {Colors.GREEN}✓{Colors.RESET} Data: .json, .jsonl, .csv")

    if prompt_yes_no("\nIs this location okay for your documents?", default=True):
        data_folder = default_data_folder
    else:
        data_folder = prompt_path("Enter your data folder path", default_data_folder)

    # Create data folder if it doesn't exist
    data_path = Path(data_folder)
    data_path.mkdir(parents=True, exist_ok=True)
    print_success(f"Data folder created: {data_path.absolute()}")

    # Check if folder has any files
    existing_files = list(data_path.glob('*'))
    if existing_files:
        print_info(f"Found {len(existing_files)} existing file(s) in data folder")
    else:
        print_info("Data folder is empty. Add documents to get started!")

    # Step 5: Full Installation
    print_step(5, "Installation (Full Setup)")
    if not install_dependencies(framework, debug):
        print_error("Installation failed")
        sys.exit(1)

    # Step 6: Configuration
    print_step(6, "Configuration")
    create_config(framework, model_path, data_folder)

    # Step 7: Validation
    print_step(7, "Validation")
    if not run_tests():
        print_warning("Some validation tests failed, but setup may still work")
        if not prompt_yes_no("Continue with setup?", default=True):
            sys.exit(1)

    # Step 8: Usage Instructions
    show_usage_instructions(framework, model_path, data_folder)

    print_success("Setup complete!")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='RoT Reasoning Server Setup')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode with detailed logs')
    args = parser.parse_args()

    try:
        main(debug=args.debug)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Setup cancelled by user{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Setup failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
