#!/bin/bash
# RoT Reasoning Server - Virtual Environment Setup Script
# Version: v0.2.0

set -e  # Exit on error

echo "=================================================="
echo "RoT Reasoning Server - venv Setup"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
PYTHON_CMD=""
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 11 ]; then
        PYTHON_CMD="python3"
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}❌ Error: Python 3.11+ not found${NC}"
    echo "Please install Python 3.11 or 3.12"
    exit 1
fi

echo -e "${GREEN}✓ Found: $($PYTHON_CMD --version)${NC}"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠ venv directory already exists${NC}"
    read -p "Remove and recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        $PYTHON_CMD -m venv venv
        echo -e "${GREEN}✓ venv recreated${NC}"
    else
        echo "Using existing venv"
    fi
else
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}✓ venv created${NC}"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ venv activated${NC}"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✓ pip upgraded${NC}"
echo ""

# Install dependencies
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed from requirements.txt${NC}"
elif [ -f "pyproject.toml" ]; then
    pip install -e .
    echo -e "${GREEN}✓ Dependencies installed from pyproject.toml${NC}"
else
    echo -e "${RED}❌ Error: No requirements.txt or pyproject.toml found${NC}"
    exit 1
fi
echo ""

# Verify installations
echo "Verifying installations..."
echo -n "  - fastmcp: "
python -c "import fastmcp; print('✓ ' + fastmcp.__version__)" 2>/dev/null || echo -e "${RED}✗ Not installed${NC}"

echo -n "  - torch: "
python -c "import torch; print('✓ ' + torch.__version__)" 2>/dev/null || echo -e "${RED}✗ Not installed${NC}"

echo -n "  - transformers: "
python -c "import transformers; print('✓ ' + transformers.__version__)" 2>/dev/null || echo -e "${RED}✗ Not installed${NC}"

echo -n "  - PIL: "
python -c "import PIL; print('✓ ' + PIL.__version__)" 2>/dev/null || echo -e "${RED}✗ Not installed${NC}"

echo ""

# Check CUDA availability
echo "Checking GPU/CUDA..."
python -c "
import torch
if torch.cuda.is_available():
    print(f'✓ CUDA available: {torch.cuda.get_device_name(0)}')
    print(f'  VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB')
else:
    print('⚠ CUDA not available (CPU-only mode)')
"
echo ""

# Run tests
echo "Running tests..."
cd src
python rot_reasoning.py --test
TEST_RESULT=$?
cd ..

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    echo -e "${RED}✗ Tests failed${NC}"
    exit 1
fi
echo ""

# Summary
echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "To deactivate:"
echo "  deactivate"
echo ""
echo "To run the server:"
echo "  source venv/bin/activate"
echo "  cd src"
echo "  python rot_reasoning.py --test"
echo ""
echo "Next steps:"
echo "  1. Configure models in parameter.yaml"
echo "  2. See MODEL_SETUP.md for model download"
echo "  3. Run: python src/rot_reasoning.py --test"
echo ""
