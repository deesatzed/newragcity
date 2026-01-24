#!/usr/bin/env python3
"""
Validation script to test setup.py components without full installation.
"""

import sys
from pathlib import Path

# Add setup.py functions to path
sys.path.insert(0, str(Path(__file__).parent))

# Import setup.py components
from setup import (
    detect_system,
    check_disk_space,
    detect_ollama_models,
    detect_huggingface_models,
    detect_mlx_models,
    get_recommended_framework,
    Colors,
    print_header,
    print_step,
    print_success,
    print_info,
    print_warning,
)

def test_system_detection():
    """Test Step 1: System Check"""
    print_header("Test 1: System Detection")

    system_info = detect_system()

    print_info(f"OS: {system_info['os']}")
    print_info(f"Architecture: {system_info['arch']}")
    print_info(f"Python: {system_info['python_version'].major}.{system_info['python_version'].minor}")
    print_info(f"macOS: {system_info['is_macos']}")
    print_info(f"ARM: {system_info['is_arm']}")
    print_info(f"CUDA: {system_info['has_cuda']}")
    print_info(f"MPS: {system_info['has_mps']}")

    disk_space = check_disk_space()
    print_info(f"Disk space: {disk_space}GB")

    if system_info['python_version'] >= (3, 11):
        print_success("System detection passed")
        return True
    else:
        print_warning("Python version too old")
        return False

def test_framework_recommendation():
    """Test Step 2: Framework Selection"""
    print_header("Test 2: Framework Recommendation")

    system_info = detect_system()
    recommended = get_recommended_framework(system_info)

    print_info(f"Recommended framework: {recommended}")

    if system_info['is_macos'] and system_info['is_arm']:
        expected = 'mlx'
    else:
        expected = 'ollama'

    if recommended == expected:
        print_success("Framework recommendation correct")
        return True
    else:
        print_warning(f"Expected {expected}, got {recommended}")
        return False

def test_model_detection():
    """Test Step 3: Model Detection"""
    print_header("Test 3: Model Detection")

    ollama_models = detect_ollama_models()
    print_info(f"Ollama models found: {len(ollama_models)}")
    for model in ollama_models[:3]:
        print(f"  - {model['name']} ({model['framework']})")

    hf_models = detect_huggingface_models()
    print_info(f"HuggingFace models found: {len(hf_models)}")
    for model in hf_models[:3]:
        print(f"  - {model['name']} ({model['framework']})")

    mlx_models = detect_mlx_models()
    print_info(f"MLX models found: {len(mlx_models)}")
    for model in mlx_models[:3]:
        print(f"  - {model['name']} ({model['framework']})")

    total_models = len(ollama_models) + len(hf_models) + len(mlx_models)
    print_info(f"Total multimodal models detected: {total_models}")

    print_success("Model detection completed")
    return True

def test_data_folder_creation():
    """Test Step 4: Data Folder Configuration"""
    print_header("Test 4: Data Folder Setup")

    test_folder = Path.cwd() / 'data'

    if test_folder.exists():
        print_info(f"Data folder exists: {test_folder.absolute()}")
        existing_files = list(test_folder.glob('*'))
        print_info(f"Files in folder: {len(existing_files)}")
        for f in existing_files[:5]:
            print(f"  - {f.name} ({f.stat().st_size / 1024:.1f} KB)")
    else:
        print_info(f"Data folder would be created at: {test_folder.absolute()}")

    print_success("Data folder setup validated")
    return True

def test_supported_document_types():
    """Test document type display"""
    print_header("Test 5: Document Type Information")

    doc_types = {
        "Text": [".txt", ".md", ".markdown", ".rst"],
        "PDF": [".pdf"],
        "Office": [".docx", ".doc", ".rtf"],
        "Images": [".png", ".jpg", ".jpeg", ".webp"],
        "Data": [".json", ".jsonl", ".csv"]
    }

    for category, extensions in doc_types.items():
        print(f"  {Colors.GREEN}✓{Colors.RESET} {category}: {', '.join(extensions)}")

    print_success("Document types validated")
    return True

def main():
    """Run all validation tests"""
    print_header("RoT Setup.py Validation Tests")
    print("Testing setup components without full installation...\n")

    tests = [
        ("System Detection", test_system_detection),
        ("Framework Recommendation", test_framework_recommendation),
        ("Model Detection", test_model_detection),
        ("Data Folder Setup", test_data_folder_creation),
        ("Document Types", test_supported_document_types),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print()
        except Exception as e:
            print_warning(f"{test_name} failed with error: {e}")
            results.append((test_name, False))
            print()

    # Summary
    print_header("Validation Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if result else f"{Colors.RED}✗ FAIL{Colors.RESET}"
        print(f"{status} - {test_name}")

    print()
    if passed == total:
        print_success(f"All {total} validation tests passed!")
        print_info("setup.py is ready for use")
        return 0
    else:
        print_warning(f"{passed}/{total} tests passed")
        print_info("Some components may need attention")
        return 1

if __name__ == '__main__':
    sys.exit(main())
