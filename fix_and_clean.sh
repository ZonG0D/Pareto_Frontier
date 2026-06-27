#!/bin/bash
set -e

echo "[INFO] Starting Cleanup..."

# 1. Remove redundant sub-package and logs
rm -rf Pareto_Frontier/core/
rm -f prompt_a.log prompt_b.log bench_results.txt
rm -rf .cache

# 2. Fix permissions for bin files
chmod +x bin/*

echo "[INFO] Cleanup complete."

echo "[INFO] Starting Bug Hunt (Static Analysis)..."

# Check for common Python/Bash issues using basic grep patterns
echo "[TRACE] Checking for hardcoded secrets or unquoted variables in shell scripts..."
grep -r "export .*=" . | grep -vE "(PATH|HOME|USER)" || echo "[OK] No suspicious env vars found."

echo "[TRACE] Checking for potential security/config issues..."
# Check if any files contain 'PASSWORD=' or similar (crude check)
grep -rn "PASSWORD" . --exclude-dir=.git --exclude-dir=.venv || echo "[OK] No obvious password strings in code."

echo "[INFO] Running Verification Tests..."
source .venv/bin/activate
python3 verification_test.py || { echo "[ERROR] Verification tests failed!"; exit 1; }

echo "[INFO] All checks passed!"
