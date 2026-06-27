 `#!/bin/bash
# Pareto Frontier - Baseline Initializer

set -e

PROJECT_ROOT=$(pwd)
CURRENT_REPORT="${PROJECT_ROOT}/evals/ci_reports/current_report.json"
BASELINE_FILE="${PROJECT_ROOT}/.pareto_baseline.json"

if [ ! -f "$CURRENT_REPORT" ]; then
    echo "[ERROR] No current report found at $CURRENT_REPORT."
    echo "Please run './evals/run_benchmarks.sh' first to generate a result set."
    exit 1
fi

echo "[*] Current performance detected."
cat "$CURRENT_REPORT" | jq .

read -p "Is this the new 'Golden Baseline'? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]
then
    cp "$CURRENT_REPORT" "$BASELINE_FILE"
    echo "[SUCCESS] New baseline established at $BASELINE_FILE."
else
    echo "[INFO] Baseline not updated."
fi`