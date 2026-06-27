import sys
import json
import argparse
from pathlib import Path
from statistics import mean


class ParetoObserver:
    def __init__(self, log_path):
        self.log_path = Path(log_path)
        if not self.log_path.exists():
            raise FileNotFoundError(f"Audit log not found at: {self.log_path}")

    def _read_logs(self):
        with open(self.log_path, "r") as f:
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
            cost = entry.get("total_cost", entry.get("compute_cost", 0.0))
            lat = (
                entry.get("total_latency_ms", 0) / 1000.0
                if isinstance(entry.get("total_latency_ms"), (int, float))
                else 0
            )
            acc = entry.get("_accuracy", entry.get("semantic_accuracy", 0.0))
            score = entry.get("pareto_score", 0.0)
            if isinstance(cost, (int, float)):
                total_cost += cost
            total_latency += lat
            accuracies.append(float(acc))
            if score > 0:
                scores.append(float(score))
            count += 1
        return {
            "runs": count,
            "total_cost": round(total_cost, 4),
            "avg_latency_s": round(total_latency / count if count > 0 else 0, 2),
            "avg_accuracy": round(mean(accuracies) if accuracies else 0, 3),
            "avg_pareto": round(mean(scores) if scores else 0, 2),
        }

    def plot_trend(self, limit=15):
        entries = list(self._read_logs())[-limit:]
        if not entries:
            return
        print("\n--- Pareto Trend (Last {} runs) ---".format(len(entries)))
        print(
            "{:<5} | {:<8} | {:<7} | {}".format(
                "Run", "Cost ($)", "Acc %", "Efficiency"
            )
        )
        for i, e in enumerate(entries):
            c = f"${e.get('total_cost', e.get('compute_cost', 0.0)):.4f}"
            a = int((e.get("_accuracy", e.get("semantic_accuracy", 0.0)) * 100))
            print(f"{i+1:<5} | {c:<8} | {a:>4}% | {'#' * (a//5)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, required=True)
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--trend", action="store_true")
    args = parser.parse_args()
    try:
        obs = ParetoObserver(args.path)
        if args.summary or not args.trend:
            s = obs.get_summary()
            print("\n[TRACE] Metrics:", s)
        if args.trend or not args.summary:
            obs.plot_trend()
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
