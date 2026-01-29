#!/bin/bash
# Real-time benchmark monitoring script
# Shows: completed datasets, current progress, last errors

RESULTS_DIR="/Volumes/WS4TB/newragcity/UltraRAG-main/ersatz_rag/regulus/backend/benchmarks/results/all_beir_datasets"
CHECKPOINT_FILE="$RESULTS_DIR/checkpoint.json"

echo "======================================================================="
echo "BEIR BENCHMARK MONITORING - $(date)"
echo "======================================================================="
echo ""

# Check if benchmark is running
if ps aux | grep -v grep | grep "beir_all_datasets.py" > /dev/null; then
    echo "✅ Benchmark is RUNNING"
    ps aux | grep -v grep | grep "beir_all_datasets.py" | awk '{print "   PID:", $2, "  Elapsed:", $10}'
else
    echo "❌ Benchmark is NOT RUNNING"
fi
echo ""

# Check checkpoint
if [ -f "$CHECKPOINT_FILE" ]; then
    echo "📊 CHECKPOINT STATUS:"
    echo "-------------------------------------------------------------------"

    COMPLETED=$(python3 -c "import json; print(len(json.load(open('$CHECKPOINT_FILE'))['completed_datasets']))" 2>/dev/null || echo "0")
    FAILED=$(python3 -c "import json; print(len(json.load(open('$CHECKPOINT_FILE'))['failed_datasets']))" 2>/dev/null || echo "0")

    echo "   Completed datasets: $COMPLETED"
    echo "   Failed datasets: $FAILED"

    if [ "$COMPLETED" -gt "0" ]; then
        echo ""
        echo "   ✅ Completed:"
        python3 -c "import json; d=json.load(open('$CHECKPOINT_FILE')); [print(f'      - {ds}') for ds in d['completed_datasets']]" 2>/dev/null
    fi

    if [ "$FAILED" -gt "0" ]; then
        echo ""
        echo "   ❌ Failed:"
        python3 -c "import json; d=json.load(open('$CHECKPOINT_FILE')); [print(f'      - {fail[\"name\"]}: {fail[\"reason\"]}') for fail in d['failed_datasets']]" 2>/dev/null
    fi
else
    echo "⚠️  No checkpoint file found"
fi
echo ""

# Check result files
echo "📁 RESULT FILES:"
echo "-------------------------------------------------------------------"
if [ -d "$RESULTS_DIR" ]; then
    ls -lh "$RESULTS_DIR"/*_results.json 2>/dev/null | wc -l | xargs echo "   Total result files:"

    echo ""
    echo "   Recent results:"
    for file in $(ls -t "$RESULTS_DIR"/*_results.json 2>/dev/null | head -5); do
        DATASET=$(basename "$file" _results.json)
        NDCG=$(python3 -c "import json; d=json.load(open('$file')); print(f'{d[\"metrics\"][\"nDCG@10\"]:.4f}')" 2>/dev/null || echo "N/A")
        BEATS=$(python3 -c "import json; d=json.load(open('$file')); print('✅' if d.get('beats_sota', False) else '❌')" 2>/dev/null || echo "?")
        echo "      $BEATS $DATASET: nDCG@10 = $NDCG"
    done
else
    echo "   ⚠️  Results directory not found"
fi
echo ""

# Show recent log activity
if [ -f "/tmp/all_13_beir_benchmark.log" ]; then
    echo "📝 RECENT LOG ACTIVITY (last 10 lines):"
    echo "-------------------------------------------------------------------"
    tail -10 /tmp/all_13_beir_benchmark.log
else
    echo "⚠️  No log file found at /tmp/all_13_beir_benchmark.log"
fi
echo ""

echo "======================================================================="
echo "To monitor in real-time: tail -f /tmp/all_13_beir_benchmark.log"
echo "To check detailed checkpoint: cat $CHECKPOINT_FILE"
echo "======================================================================="
