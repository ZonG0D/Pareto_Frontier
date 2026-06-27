import sys
import os
import json
import argparse
from pathlib import Path
from statistics import mean

class ParetoObserver:
    \"\"\"
    The Linux Guru's Observability Layer:
    No database. No microservices. Just high-speed parsing of the audit trails.
    \"\"\"
    def __init__(self, log_path: str):
        self.log_path = Path(log_path)
        if not self.log_path.exists():
            raise FileNotFoundError(f"Audit log not found at: {self.log_path}")

    def _read_logs(self):
        with open(self.log_path, 'r') as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)

    def get_summary(self):
        total_cost = 0.0
        total_latency = 0.0
        count = 0
        scores = []
        accuracies = []

        for entry in self._read_logs():
            # Support both the orchestrator output and various log formats
            cost = entry.get('total_cost', entry.get('compute_cost', 0.0))
            latency = entry.get('total_latency_ms', 0) / 1000.0 if isinstance(entry.get('total_latency_ms'), (int, float)) else 0
            accuracy = entry.get('_accuracy', entry.get('semantic_accuracy', 0.0))
            pareto = entry.get('pareto_score', 0.0)

            if isinstance(cost, (int, float)): total_cost += cost
            if latency > 0: total_latency += latency
            accuracies.append(float(accuracy))
            if pareto > 0: scores.append(float(pareto))
            count += 1

        return {
            "runs": count,
            "total_cost": round(total_cost, 4),
            "avg_latency_s": round(mean(total_latency), 2) if total_latency > 0 else 0,
            "avg_accuracy": round(mean(accuracies), 3) if accuracies else 0,
            "avg_pareto": round(mean(scores), 2) if scores else 0
        }

    def plot_trend(self, limit=15):
        \"\"\"Renders a minimalist ASCII trend of Accuracy vs Cost in the terminal.\"\"\"
        entries = list(self._read_logs())[-limit:]
        if not entries:
            print("[WARN] No data points found to plot.")
            return

        print(f"\\n--- Pareto Trend (Last {len(entries)} runs) ---")
        print(f"{'Run':<5} | {'Cost ($)':<8} | {'Acc %':<7} | {'Efficiency (ASCII)'}")
        print("---------------------------------------------------------")

        for i, e in enumerate(entries):
            cost = f"${e.get('total_cost', e.get('compute_cost', 0.0)):.4f}"
            acc = int((e.get('_accuracy', e.get('semantic_accuracy', 0.0)) * 100))
            # ASCII bar for accuracy: max 20 chars
            bar = '#' * (acc // 5)
            print(f"{i+1:<5} | {cost:<8} | {acc:>4}% | {bar}")
        print("---------------------------------------------------------\\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, required=True, help="Path to the audit log (.jsonl)")
    parser.add_argument("--summary", action="store_true", help="Show high-level summary")
    parser.add_argument("--trend", action="store_true", help="Show ASCII accuracy trend")
    args = parser.parse_args()

    try:
        obs = ParetoObserver(args.path)
        if args.summary or not args.trend:
            stats = obs.get_summary()
            print("\\n[TRACE] Aggregate Metrics:")
            for k, v in stats.items():
                print(f"  {k.replace('_', ' ').title()}: {v}")
        if args.trend or not args.summary:
            obs.plot_trend()
    except Exception as e:
        print(f"[ERROR] Observer failed: {e}")
        sys.exit(1)
