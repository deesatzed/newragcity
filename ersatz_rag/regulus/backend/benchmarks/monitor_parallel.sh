#!/bin/bash
# Parallel Benchmark Monitoring Dashboard
# Shows: global progress, active workers, recent completions, live logs

RESULTS_DIR="/Volumes/WS4TB/newragcity/UltraRAG-main/ersatz_rag/regulus/backend/benchmarks/results/all_beir_datasets"
CHECKPOINT_FILE="$RESULTS_DIR/checkpoint.json"
LOG_DIR="/tmp/beir_parallel_logs"

echo "======================================================================="
echo "PARALLEL BEIR BENCHMARK MONITORING - $(date)"
echo "======================================================================="
echo ""

# Check if master process is running
if ps aux | grep -v grep | grep "beir_parallel_runner.py" > /dev/null; then
    echo "✅ Master process is RUNNING"
    ps aux | grep -v grep | grep "beir_parallel_runner.py" | awk '{print "   PID:", $2, "  Elapsed:", $10}'
else
    echo "❌ Master process is NOT RUNNING"
fi
echo ""

# Check for active worker processes
echo "🔧 ACTIVE WORKERS:"
echo "-------------------------------------------------------------------"
WORKER_COUNT=$(ps aux | grep -v grep | grep "beir_single_dataset.py" | wc -l | xargs)
if [ "$WORKER_COUNT" -gt "0" ]; then
    echo "   $WORKER_COUNT workers currently running:"
    ps aux | grep -v grep | grep "beir_single_dataset.py" | while read line; do
        PID=$(echo "$line" | awk '{print $2}')
        ELAPSED=$(echo "$line" | awk '{print $10}')
        DATASET=$(echo "$line" | grep -o '\-\-dataset [^ ]*' | awk '{print $2}')
        echo "      [$DATASET] PID: $PID, Elapsed: $ELAPSED"
    done
else
    echo "   No active workers (between batches or completed)"
fi
echo ""

# Check checkpoint
if [ -f "$CHECKPOINT_FILE" ]; then
    echo "📊 GLOBAL PROGRESS:"
    echo "-------------------------------------------------------------------"

    COMPLETED=$(python3 -c "import json; print(len(json.load(open('$CHECKPOINT_FILE'))['completed_datasets']))" 2>/dev/null || echo "0")
    FAILED=$(python3 -c "import json; print(len(json.load(open('$CHECKPOINT_FILE'))['failed_datasets']))" 2>/dev/null || echo "0")
    TOTAL=13  # Total available BEIR datasets

    PROGRESS=$((($COMPLETED * 100) / $TOTAL))

    echo "   Progress: $COMPLETED / $TOTAL datasets ($PROGRESS%)"
    echo "   Failed: $FAILED datasets"
    echo ""

    # Progress bar
    FILLED=$((PROGRESS / 5))
    EMPTY=$((20 - FILLED))
    BAR=$(printf '█%.0s' $(seq 1 $FILLED))$(printf '░%.0s' $(seq 1 $EMPTY))
    echo "   [$BAR] $PROGRESS%"
    echo ""

    if [ "$COMPLETED" -gt "0" ]; then
        echo "   ✅ Completed datasets:"
        python3 -c "import json; d=json.load(open('$CHECKPOINT_FILE')); [print(f'      - {ds}') for ds in d['completed_datasets']]" 2>/dev/null
    fi

    if [ "$FAILED" -gt "0" ]; then
        echo ""
        echo "   ❌ Failed datasets:"
        python3 -c "import json; d=json.load(open('$CHECKPOINT_FILE')); [print(f'      - {fail[\"name\"]}: {fail[\"reason\"]}') for fail in d['failed_datasets']]" 2>/dev/null
    fi
else
    echo "⚠️  No checkpoint file found"
fi
echo ""

# Check result files
echo "📁 COMPLETED RESULTS:"
echo "-------------------------------------------------------------------"
if [ -d "$RESULTS_DIR" ]; then
    RESULT_COUNT=$(ls "$RESULTS_DIR"/*_results.json 2>/dev/null | wc -l | xargs)
    echo "   Total result files: $RESULT_COUNT"

    if [ "$RESULT_COUNT" -gt "0" ]; then
        echo ""
        echo "   Recent completions (last 5):"
        for file in $(ls -t "$RESULTS_DIR"/*_results.json 2>/dev/null | head -5); do
            DATASET=$(basename "$file" _results.json)
            NDCG=$(python3 -c "import json; d=json.load(open('$file')); print(f'{d[\"metrics\"][\"nDCG@10\"]:.4f}')" 2>/dev/null || echo "N/A")
            BEATS=$(python3 -c "import json; d=json.load(open('$file')); print('✅' if d.get('beats_sota', False) else '❌')" 2>/dev/null || echo "?")
            ELAPSED=$(python3 -c "import json; d=json.load(open('$file')); print(f'{d.get(\"elapsed_time_hours\", 0):.1f}h')" 2>/dev/null || echo "N/A")
            echo "      $BEATS $DATASET: nDCG@10 = $NDCG, Time = $ELAPSED"
        done
    fi
else
    echo "   ⚠️  Results directory not found"
fi
echo ""

# Show recent log activity from active workers
if [ -d "$LOG_DIR" ]; then
    echo "📝 ACTIVE WORKER LOGS (last 3 lines each):"
    echo "-------------------------------------------------------------------"

    # Find logs modified in last 5 minutes (actively running)
    ACTIVE_LOGS=$(find "$LOG_DIR" -name "*.log" -mmin -5 2>/dev/null)

    if [ -n "$ACTIVE_LOGS" ]; then
        for log in $ACTIVE_LOGS; do
            DATASET=$(basename "$log" .log)
            echo "   [$DATASET]:"
            tail -3 "$log" 2>/dev/null | sed 's/^/      /'
            echo ""
        done
    else
        echo "   No active logs (workers may be between tasks)"
    fi
else
    echo "⚠️  Log directory not found at $LOG_DIR"
fi
echo ""

# Show aggregate if available
AGGREGATE_FILE="$RESULTS_DIR/beir_aggregate_summary.json"
if [ -f "$AGGREGATE_FILE" ]; then
    echo "🏆 BEIR AGGREGATE (partial or final):"
    echo "-------------------------------------------------------------------"
    BEIR_AVG=$(python3 -c "import json; d=json.load(open('$AGGREGATE_FILE')); print(f'{d[\"beir_aggregate_ndcg10\"]:.4f}')" 2>/dev/null || echo "N/A")
    VS_SOTA=$(python3 -c "import json; d=json.load(open('$AGGREGATE_FILE')); print(f'{d[\"vs_sota_improvement\"]:+.1f}%')" 2>/dev/null || echo "N/A")
    BEATS=$(python3 -c "import json; d=json.load(open('$AGGREGATE_FILE')); print('✅ YES' if d.get('beats_sota', False) else '❌ NO')" 2>/dev/null || echo "?")

    echo "   BEIR Average nDCG@10: $BEIR_AVG"
    echo "   vs SOTA (NV-Embed):   $VS_SOTA"
    echo "   Beats SOTA:           $BEATS"
    echo ""
fi

echo "======================================================================="
echo "Commands:"
echo "  Monitor continuously:  watch -n 60 './monitor_parallel.sh'"
echo "  View specific log:     tail -f $LOG_DIR/<dataset>.log"
echo "  Check checkpoint:      cat $CHECKPOINT_FILE"
echo "  View aggregate:        cat $AGGREGATE_FILE"
echo "======================================================================="
echo ""
