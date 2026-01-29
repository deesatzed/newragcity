#!/bin/bash
#
# Automated SOTA Testing Execution Script
#
# This script provides a complete automated workflow for:
# - Running BEIR benchmarks with Qwen3 embeddings
# - Monitoring progress in real-time
# - Generating SOTA comparison reports
# - Handling errors and resuming from checkpoints
#

set -e  # Exit on error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATASETS_DIR="/Volumes/WS4TB/newragcity/UltraRAG-main/datasets"
RESULTS_DIR="$SCRIPT_DIR/results/automated_sota"
LOG_FILE="$RESULTS_DIR/execution.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1" | tee -a "$LOG_FILE"
}

# Create results directory
mkdir -p "$RESULTS_DIR"

# Banner
echo ""
echo "=========================================================================="
echo "  AUTOMATED SOTA TESTING - newragcity with Qwen3-Embedding-0.6B"
echo "=========================================================================="
echo ""

# Parse arguments
MODE="${1:-full}"

case "$MODE" in
    quick)
        log "Mode: QUICK VALIDATION (3 datasets)"
        PYTHON_MODE="quick"
        EXPECTED_TIME="2-3 hours"
        ;;
    full)
        log "Mode: FULL BEIR BENCHMARK (15 datasets)"
        PYTHON_MODE="full"
        EXPECTED_TIME="60-80 hours"
        ;;
    resume)
        log "Mode: RESUME FROM CHECKPOINT"
        PYTHON_MODE="resume"
        EXPECTED_TIME="Varies"
        ;;
    *)
        error "Invalid mode: $MODE"
        echo "Usage: $0 [quick|full|resume]"
        exit 1
        ;;
esac

info "Expected completion time: $EXPECTED_TIME"
info "Results directory: $RESULTS_DIR"
info "Log file: $LOG_FILE"
echo ""

# Check Python environment
log "Checking Python environment..."

if ! command -v python3 &> /dev/null; then
    error "Python 3 not found. Please install Python 3.11+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
info "Python version: $PYTHON_VERSION"

# Check required Python packages
log "Checking required packages..."

python3 -c "import sys; sys.path.insert(0, '$SCRIPT_DIR/../..'); from app.three_approach_integration import ThreeApproachRAG" 2>/dev/null || {
    error "ThreeApproachRAG not found. Please install dependencies."
    exit 1
}

python3 -c "import scipy" 2>/dev/null || {
    warn "scipy not found. Installing..."
    pip3 install scipy
}

python3 -c "import numpy" 2>/dev/null || {
    warn "numpy not found. Installing..."
    pip3 install numpy
}

log "All dependencies satisfied ✓"
echo ""

# Check datasets
log "Checking datasets directory: $DATASETS_DIR"

if [ ! -d "$DATASETS_DIR" ]; then
    error "Datasets directory not found: $DATASETS_DIR"
    exit 1
fi

DATASET_COUNT=$(find "$DATASETS_DIR" -maxdepth 1 -type d | wc -l)
info "Found $((DATASET_COUNT - 1)) dataset directories"
echo ""

# Start monitoring process in background
log "Starting progress monitor..."

monitor_progress() {
    while true; do
        sleep 300  # Check every 5 minutes

        if [ -f "$RESULTS_DIR/checkpoint.json" ]; then
            COMPLETED=$(python3 -c "import json; data=json.load(open('$RESULTS_DIR/checkpoint.json')); print(len(data.get('completed_datasets', [])))")
            FAILED=$(python3 -c "import json; data=json.load(open('$RESULTS_DIR/checkpoint.json')); print(len(data.get('failed_datasets', [])))")

            info "Progress: $COMPLETED completed, $FAILED failed"
        fi
    done
}

monitor_progress &
MONITOR_PID=$!

# Cleanup function
cleanup() {
    log "Cleaning up..."
    kill $MONITOR_PID 2>/dev/null || true
}

trap cleanup EXIT

# Run automated SOTA testing
log "Starting automated SOTA testing..."
echo ""

START_TIME=$(date +%s)

python3 "$SCRIPT_DIR/automated_sota_testing.py" \
    --mode "$PYTHON_MODE" \
    --datasets-dir "$DATASETS_DIR" \
    --results-dir "$RESULTS_DIR" \
    2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=$?
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
ELAPSED_HOURS=$((ELAPSED / 3600))
ELAPSED_MINS=$(((ELAPSED % 3600) / 60))

echo ""

if [ $EXIT_CODE -eq 0 ]; then
    log "Automated SOTA testing completed successfully ✓"
    log "Total time: ${ELAPSED_HOURS}h ${ELAPSED_MINS}m"
    echo ""

    # Check if we beat SOTA
    if [ -f "$RESULTS_DIR/automated_sota_results.json" ]; then
        BEATS_SOTA=$(python3 -c "import json; data=json.load(open('$RESULTS_DIR/automated_sota_results.json')); print(data.get('beats_aggregate_sota', False))")

        if [ "$BEATS_SOTA" = "True" ]; then
            echo "=========================================================================="
            echo "  🎉 NEW BEIR SOTA ACHIEVED! 🎉"
            echo "=========================================================================="
        else
            info "Results below SOTA, but still competitive."
            info "See report for improvement recommendations."
        fi
    fi

    echo ""
    info "Report location: $RESULTS_DIR/AUTOMATED_SOTA_REPORT_${MODE^^}.md"
    info "Results JSON: $RESULTS_DIR/automated_sota_results.json"

else
    error "Automated SOTA testing failed with exit code $EXIT_CODE"
    warn "Check log file for details: $LOG_FILE"
    exit $EXIT_CODE
fi

echo ""
log "Done!"
echo ""
