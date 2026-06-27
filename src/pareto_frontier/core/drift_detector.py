import sys
import json
import argparse
from pathlib import Path
from statistics import mean


class ParetoDriftDetector:
    def __init__(self, log_path):
        self.log_path = Path(log_path)
        if not self.log_path.exists():
            raise FileNotFoundError(f"Audit log not found at: {self.log_path}")

    def _read_logs(self):
        with open(self.log_path, "r") as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)

    def check_drift(self, window_recent=5, window_historical=20, threshold=0.8):
        import math

        recent_effs = []
        hist_effs = []
        logs = list(self._read_logs())
        if len(logs) < (window_recent + window_historical):
            return "INSUFFICIENT_DATA", 0.0, 0.0

        for i, entry in enumerate(reversed(logs)):
            acc = float(entry.get("_accuracy", entry.get("semantic_accuracy", 0.0)))
            cost = float(entry.get("total_cost", entry.get("compute_cost", 0.1)))
            if cost <= 0:
                cost = 0.0001
            eff = acc / math.log(cost + 1.01)

            if i < window_recent:
                recent_effs.append(eff)
            else:
                hist_effs.append(eff)
            if (
                len(recent_effs) == window_recent
                and len(hist_effs) == window_historical
            ):
                break

        avg_r = mean(recent_effs)
        avg_h = mean(hist_effs)
        ratio = avg_r / avg_h if avg_h > 0 else 1.0
        status = "DRIFT_DETECTED" if ratio < threshold else "STABLE"
        return status, round(ratio, 3), round(avg_r, 4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, required=True)
    args = parser.parse_args()
    try:
        det = ParetoDriftDetector(args.path)
        s, r, e = det.check_drift()
        print(f"STATUS:{s}|RATIO:{r}|EFFICIENCY:{e}")
    except Exception as err:
        print(f"ERROR:{err}")
        sys.exit(1)
