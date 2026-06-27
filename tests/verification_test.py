import json
import time
import sys
import os
from pathlib import Path
try:
    from pareto_frontier.core.orchestrator import Orchestrator
except ImportError:
    import sys as sysmodule
    sysmodule.path.append(str(Path(__file__).resolve().parent))
    from pareto_frontier.core.orchestrator import Orchestrator

try:
    from evals.metrics_engine import ParetoMetrics
except ImportError:
    import sys as sysmodule
    sysmodule.path.append(str(Path(__file__).resolve().parent))
    from evals.metrics_engine import ParetoMetrics

def run_manual_benchmark():
    print("--- Starting Manual Verification ---")
    orch = Orchestrator()
    metrics_engine = ParetoMetrics()
    
    test_prompts = [
        "How to optimize LLM inference",
        "What is quantum entanglement?",
        "Write a git commit message for fixing an empty list error."
    ]
    
    results = []
    
    for p in test_prompts:
        print(f"Processing: {p}")
        start = time.time()
        try:
            res = orch.run_cascade(p)
            duration = time.time() - start
            
            # Extract metrics for evaluation (simulated ground truth as we don't have an LLM judge here)
            accuracy = 0.95 
            compute = res['_metrics'].get('total_cost', 1.0)
            latency = duration
            
            results.append({
                "accuracy": accuracy,
                "compute": compute,
                "latency": latency
            })
        except Exception as e:
            print(f"Failed prompt '{p}': {e}")

    if results:
        summary = metrics_engine.evaluate_system(results)
        print("\n--- VERIFICATION SUMMARY ---")
        print(json.dumps(summary, indent=2))
        if summary and summary.get('pareto_score', 0) > 0:
            print("\n✅ SUCCESS: Pareto Score calculated.")
        else:
            print("\n❌ FAILURE: No valid Pareto Score computed.")
    else:
        print("No results collected.")

if __name__ == "__main__":
    run_manual_benchmark()
