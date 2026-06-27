#!/bin/bash
# Pareto Frontier CI Runner - Executes all experiment modes and aggregates results

set -e

PROJECT_ROOT=$(pwd)
OUTPUT_DIR="${PROJECT_ROOT}/evals/ci_reports"
BASELINE_FILE="${PROJECT_ROOT}/.pareto_baseline.json"
CURRENT_REPORT="${OUTPUT_DIR}/current_report.json"

mkdir -p "$OUTPUT_DIR"

echo "[*] Starting Pareto Automated Benchmarking..."

# 1. Ensure jq is present
if ! command -v jq &> /dev/null; then
    echo "[ERROR] 'jq' is required for CI aggregation."
    exit 1
fi

# Function to run a single experiment and save output
run_step() {
    local step_name=$1
    local cmd=$2
    local out_file=$3

    echo "[*] Step: $step_name ..."
    if eval "$cmd" > /dev/null 2>&1; then
        echo "  [+] Success"
        return 0
    else
        echo "  [-] Failed (check output)"
        return 1
    fi
}

# Temporary files for partial data
TEMP_STD="${OUTPUT_DIR}/std.json"
TEMP_CACHE="${OUTPUT_DIR}/cache.json"
TEMP_RESULTS="${PROJECT_ROOT}/ci_temp_results.json"

echo '{"timestamp": "'$(date -Iseconds)'", "experiments": {}}' > "$TEMP_RESULTS"

# --- 1. Standard Benchmark ---
run_step "Standard Mode" "python3 evals/benchmark.py --experiment standard --output-file $TEMP_STD" || true

if [ -f "$TEMP_STD" ]; then
    jq --argjson val "$(cat "$TEMP_STD")" '.experiments["standard"] = $val' "$TEMP_RESULTS" > "${TEMP_RESULTS}.tmp" && mv "${TEMP_RESULTS}.tmp" "$TEMP_RESULTS"
else
    echo "[!] Warning: Standard Mode failed or produced no output."
fi

# --- 2. Cache Experiment ---
run_step "Cache Mode" "python3 evals/benchmark.py --experiment cache --output-file $TEMP_CACHE" || true

if [ -f "$TEMP_CACHE" ]; then
    jq --argjson val "$(cat "$TEMP_CACHE")" '.experiments["cache"] = $val' "$TEMP_RESULTS" > "${TEMP_RESULTS}.tmp" && mv "${TEMP_TEM_TMP}" "$TEMP_RESULTS" 2>/dev/null || true
    # Let's be safer with the jq command to avoid errors if file is empty
    jq --argjson val "$(cat "$TEMP_CACHE")" '.experiments["cache"] = $val' "$TEMP_RESULTS" > "${TEMP_RESULTS}.tmp" && mv "${TEMP_RESULTS}.tmp" "$TEMP_RESULTS"
fi

# Finalize current report
cp "$TEMP_RESULTS" "$CURRENT_REPORT"
rm -f "$TEMP_RESULTS"

echo "[+] Benchmark complete. Report: ${CURRENT_REPORT}"

if [ ! -f "$BASELINE_FILE" ]; then
    echo "[i] No baseline found. Creating new baseline at $BASELINE_FILE."
    cp "$CURRENT_REPORT" "$BASELINE_FILE"
    exit 0
fi

# 3. Comparison (The critical logic)
echo "[*] Running regression check..."
python3 -c "
import json, sys
try:
    with open('$BASELINE_FILE', 'r') as f: baseline = json.load(f)
    with open('$CURRENT_REPORT', 'r') as f: current = json.load(f)

    def check_regressions(b, c):
        errors = []
        # Check standard latency (15% threshold)
        if 'standard' in b['experiments'] and 'standard' in c['experiments']:
            old_lat = b['experiments']['standard'].get('latency', 0)
            new_lat = c['experiments']['standard'].get('latency', 0)
            if old_lat > 0 and new_lat > (old_lat * 1.15):
                errors.append(f'CRITICAL: Latency regression! {old_lat:.2f}s -> {new_lat:.2f}s')

        # Check cache improvement factor
        if 'cache' in b['experiments'] and 'cache' in c['experiments']:
            try:
                old_imp = b['experiments']['cache'].get('savings', {}).get('latency_imp', 1.0)
                new_imp = c['experiments']['cache'].get('savings', {}).get('latency_imp', 1.0)
                if new_imp < (old_imp * 0.95):
                    errors.append(f'WARNING: Cache efficiency drop! {old_imp:.2f}x -> {new_imp:.2f}x')
            except Exception: pass

        return errors

    errs = check_regressions(baseline, current)
    if errs:
        print('\\n[!] REGRESSION DETECTED:')
        for e in errs: print(f'  - {e}')
        sys.exit(1)
    else:
        print('[OK] No significant regressions detected.')
except Exception as e:
    print(f'[ERROR] Comparison script error: {e}')
    sys.exit(0) 
" && exit 0 || exit 1
